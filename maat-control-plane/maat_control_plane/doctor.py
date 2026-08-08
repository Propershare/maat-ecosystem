"""maat doctor — machine truth reader."""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
import shutil
import socket
import stat
import subprocess
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlparse

from maat_control_plane.discovery import (
    default_manifest_paths,
    default_profile_paths,
    discover_lab_root,
    find_first_existing,
)
from maat_control_plane.loaders import load_document

Status = Literal["pass", "warn", "fail"]
Severity = Literal["info", "low", "medium", "high", "critical"]
TrustPosture = Literal["trusted", "degraded", "unsafe", "constitutional_breach"]


@dataclass
class Check:
    name: str
    status: Status
    reason: str | None = None
    severity: Severity = "medium"
    constitutional: bool = False
    recommended_action: str | None = None
    detail: dict[str, Any] = field(default_factory=dict)


@dataclass
class DoctorReport:
    machine_id: str | None
    role: str | None
    install_mode: str
    lab_root: str | None
    manifest_path: str | None
    profile_path: str | None
    overall_status: Status
    checks: list[Check] = field(default_factory=list)
    recommended_actions: list[str] = field(default_factory=list)
    reconciliation: list[dict[str, Any]] = field(default_factory=list)


def _infer_severity(name: str, status: Status) -> Severity:
    if status == "pass":
        return "info"
    if name.startswith("dangerous_env_MAAT_IMMUNE_ALLOW_SACRED") or name.startswith(
        "dangerous_env_MAAT_ALLOW_UNSAFE",
    ):
        return "critical"
    if name.startswith("sacred_exists") and status == "fail":
        return "critical"
    if name.startswith("sacred_permissions") or name.startswith("sacred_stat"):
        return "high"
    if name.startswith("gateway_config_world_readable"):
        return "high"
    if name.startswith("sentinel_policy_server"):
        return "high"
    if status == "fail":
        return "high"
    return "medium"


def _infer_constitutional(name: str) -> bool:
    if name.startswith("sacred_"):
        return True
    if name.startswith("dangerous_env_"):
        return True
    if name in ("manifest_load_fail", "profile_load_fail"):
        return True
    if name.startswith("sentinel_policy_"):
        return True
    if name.startswith("gateway_workspace_lab_mismatch") or name.startswith("gateway_config_world_readable"):
        return True
    return False


def _recommended_action_for(name: str, status: Status) -> str | None:
    if status == "pass":
        return None
    if name.startswith("sacred_permissions") or name.startswith("sacred_stat"):
        return "Restrict sacred path permissions (owner-only or read-only mount) per immune doctrine."
    if name == "manifest_yaml_dependency":
        return "Install PyYAML (`pip install pyyaml`) to read YAML manifests."
    if name == "profile_yaml_dependency":
        return "Install PyYAML (`pip install pyyaml`) to read YAML profiles."
    if name == "manifest_missing":
        return "Create ~/.maat/config/machine.yaml (see MAAT-LAB-CONTROL-PLANE.md)."
    if name == "manifest_load_fail":
        return "Fix manifest syntax (valid JSON/YAML object) at the reported path."
    if name == "profile_load_fail":
        return "Fix profile syntax (valid JSON/YAML object) at the reported path."
    if name == "gateway_config_world_readable":
        return "chmod 600 ~/.openclaw/openclaw.json (or remove world/other read)."
    if name == "gateway_workspace_lab_mismatch":
        return "Set OpenClaw agents.defaults.workspace to your lab root (see AGENTS.md)."
    if name == "ollama_unreachable":
        return "Start Ollama or set MAAT_DOCTOR_SKIP_OLLAMA=1 to skip."
    if name == "postgres_unreachable":
        return "Verify PGVECTOR_DB_URL / Postgres is up, or fix network."
    if name.startswith("dangerous_env_"):
        return "Unset unsafe MAAT_* override variables in production contexts."
    if name.startswith("endpoint_"):
        return "Fix endpoint URL/host or start the service; or remove endpoint from manifest if remote-only."
    if name.startswith("sentinel_policy_server"):
        return "Install or enable Sentinel on server-class hosts (see MAAT-IMMUNE-SYSTEM.md)."
    return "Review check reason and manifest alignment."


def _add(
    checks: list[Check],
    name: str,
    status: Status,
    reason: str | None = None,
    *,
    severity: Severity | None = None,
    constitutional: bool | None = None,
    recommended_action: str | None = None,
    **detail: Any,
) -> None:
    sev = severity or _infer_severity(name, status)
    cons = _infer_constitutional(name) if constitutional is None else constitutional
    act = recommended_action if recommended_action is not None else _recommended_action_for(name, status)
    checks.append(
        Check(
            name=name,
            status=status,
            reason=reason,
            severity=sev,
            constitutional=cons,
            recommended_action=act,
            detail=dict(detail),
        ),
    )


def _path_stat_detail(path: Path) -> dict[str, Any]:
    out: dict[str, Any] = {"path": str(path)}
    try:
        st = path.stat()
        mode = st.st_mode
        out["mode_octal"] = oct(mode & 0o7777)
        out["uid"] = st.st_uid
        out["gid"] = st.st_gid
        out["writable_user"] = bool(mode & stat.S_IWUSR)
        out["writable_group"] = bool(mode & stat.S_IWGRP)
        out["writable_other"] = bool(mode & stat.S_IWOTH)
        out["readable_other"] = bool(mode & stat.S_IROTH)
    except OSError as e:
        out["stat_error"] = str(e)
    return out


def _overall(checks: list[Check]) -> Status:
    if any(c.status == "fail" for c in checks):
        return "fail"
    if any(c.status == "warn" for c in checks):
        return "warn"
    return "pass"


def _recommendations(checks: list[Check]) -> list[str]:
    out: list[str] = []
    for c in checks:
        if c.status == "pass":
            continue
        if c.recommended_action:
            out.append(c.recommended_action)
    return list(dict.fromkeys(out))


def _summary_counts(checks: list[Check]) -> dict[str, int]:
    return {
        "pass_count": sum(1 for c in checks if c.status == "pass"),
        "warn_count": sum(1 for c in checks if c.status == "warn"),
        "fail_count": sum(1 for c in checks if c.status == "fail"),
        "constitutional_count": sum(1 for c in checks if c.constitutional),
    }


def _machine_trust_posture(checks: list[Check], overall: Status) -> TrustPosture:
    breach = any(
        c.status == "fail"
        and (
            c.constitutional
            or c.name.startswith("sacred_exists")
            or c.name.startswith("dangerous_env_")
        )
        for c in checks
    )
    if breach:
        return "constitutional_breach"
    if overall == "fail":
        return "unsafe"
    if overall == "warn":
        return "degraded"
    return "trusted"


def _blocking_action_label(c: Check) -> str | None:
    eligible = c.status == "fail" or (
        c.status == "warn" and c.constitutional and c.severity in ("high", "critical")
    )
    if not eligible:
        return None
    n = c.name
    if n.startswith("dangerous_env_MAAT_IMMUNE_ALLOW_SACRED"):
        return "remove MAAT_IMMUNE_ALLOW_SACRED"
    if n.startswith("dangerous_env_MAAT_ALLOW_UNSAFE"):
        return "remove MAAT_ALLOW_UNSAFE"
    if n.startswith("dangerous_env_MAAT_IMMUNE_DISABLE"):
        return "unset MAAT_IMMUNE_DISABLE (restore immune hooks)"
    if n.startswith("dangerous_env_MAAT_SKIP_GUARD"):
        return "unset MAAT_SKIP_GUARD"
    if n.startswith("sacred_exists"):
        return "restore missing sacred path"
    if n.startswith("sacred_permissions") or n.startswith("sacred_world_or_group_writable"):
        return "fix sacred path permissions"
    if n.startswith("manifest_load_fail") or n.startswith("profile_load_fail"):
        return "fix invalid manifest or profile"
    if n.startswith("gateway_config_world_readable"):
        return "restrict gateway config file permissions (e.g. chmod 600)"
    if n.startswith("gateway_workspace_lab_mismatch"):
        return "align OpenClaw workspace with lab root"
    if n.startswith("sentinel_policy_server"):
        return "restore Sentinel on server-class host"
    if c.recommended_action:
        return c.recommended_action
    return None


def _blocking_actions(checks: list[Check]) -> list[str]:
    out: list[str] = []
    for c in checks:
        label = _blocking_action_label(c)
        if label:
            out.append(label)
    return list(dict.fromkeys(out))


def _derive_install_mode(manifest: dict[str, Any] | None, role: str | None) -> str:
    if manifest:
        for key in ("install_mode", "machine_kind", "node_kind"):
            v = manifest.get(key)
            if isinstance(v, str) and v.strip():
                return v.strip().lower().replace(" ", "_").replace("-", "_")
    if role:
        r = str(role).strip().lower()
        if r in ("server", "workstation", "forge", "memory", "runtime", "runtime_only", "mixed"):
            if r == "forge":
                return "forge_node"
            if r == "memory":
                return "memory_host"
            if r in ("runtime", "runtime_only"):
                return "runtime_only"
            return r
    return "unknown"


def _reconciliation_rows(
    manifest: dict[str, Any] | None,
    lab: Path | None,
    openclaw_exists: bool,
    gw_bin: str | None,
    tehuti_ok: bool,
    sentinel_ok: bool,
    rt_ok: bool,
    sentinel_path: str | None,
) -> list[dict[str, Any]]:
    if not manifest:
        return []
    rows: list[dict[str, Any]] = []
    prot = manifest.get("protected_services")
    if isinstance(prot, list):
        for raw in prot:
            svc = str(raw).lower().strip()
            if svc == "gateway":
                rows.append(
                    {
                        "service": "gateway",
                        "expected": "present",
                        "found": "openclaw_config" if openclaw_exists else "missing",
                        "status": "match" if openclaw_exists else "mismatch",
                    },
                )
                rows.append(
                    {
                        "service": "gateway_binary",
                        "expected": "in_path",
                        "found": gw_bin or "missing",
                        "status": "match" if gw_bin else "warn",
                    },
                )
            elif svc in ("guard", "tehuti"):
                gp = str((lab / "tehuti-guard") if lab else "—")
                rows.append(
                    {
                        "service": "guard",
                        "expected": "tehuti-guard under lab",
                        "found": gp,
                        "status": "match" if tehuti_ok else "mismatch",
                    },
                )
            elif svc == "sentinel":
                rows.append(
                    {
                        "service": "sentinel",
                        "expected": "sentinel code present",
                        "found": sentinel_path or ("present" if sentinel_ok else "missing"),
                        "status": "match" if sentinel_ok else "mismatch",
                    },
                )

    managed = manifest.get("managed_services")
    if isinstance(managed, list) and any(str(x).lower() == "maat-runtime" for x in managed):
        rp = str(lab / "maat-runtime") if lab else "—"
        rows.append(
            {
                "service": "maat-runtime",
                "expected": "directory",
                "found": rp,
                "status": "match" if rt_ok else "mismatch",
            },
        )

    remote = manifest.get("remote_services")
    if isinstance(remote, list):
        for raw in remote:
            rows.append(
                {
                    "service": str(raw),
                    "expected": "remote_endpoint",
                    "found": "see endpoint_* checks",
                    "status": "unknown",
                },
            )

    return rows


def _parse_pg_host_port(url: str) -> tuple[str, int] | None:
    try:
        p = urlparse(url.replace("postgresql+psycopg2://", "postgresql://", 1))
        if p.hostname:
            return (p.hostname, p.port or 5432)
    except OSError:
        pass
    return None


def _tcp_reachable(host: str, port: int, timeout: float = 2.0) -> bool:
    try:
        s = socket.create_connection((host, port), timeout=timeout)
        s.close()
        return True
    except OSError:
        return False


def _http_ok(url: str, timeout: float = 2.0) -> bool:
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return 200 <= getattr(r, "status", r.getcode()) < 400
    except (urllib.error.URLError, OSError):
        return False


def _openclaw_workspace(data: dict[str, Any]) -> str | None:
    agents = data.get("agents")
    if isinstance(agents, dict):
        defaults = agents.get("defaults")
        if isinstance(defaults, dict):
            ws = defaults.get("workspace")
            if isinstance(ws, str) and ws.strip():
                return ws.strip()
    return None


def _file_is_world_readable(path: Path) -> bool:
    try:
        mode = path.stat().st_mode
        return (mode & stat.S_IROTH) != 0
    except OSError:
        return False


def _parse_endpoint_value(value: Any, default_port: int | None) -> tuple[str, int] | None:
    """Return (host, port) for TCP reachability checks."""
    if value is None or value is False:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        if value <= 0 or value > 65535:
            return None
        return ("127.0.0.1", value)
    if isinstance(value, float):
        return _parse_endpoint_value(int(value), default_port)
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return None
        if s.isdigit():
            p = int(s)
            if 0 < p <= 65535:
                return ("127.0.0.1", p)
        if "://" in s:
            u = urlparse(s)
            if u.hostname and u.port:
                return (u.hostname, u.port)
            if u.hostname and u.scheme in ("http", "https"):
                return (u.hostname, u.port or (443 if u.scheme == "https" else 80))
        if ":" in s and not s.startswith("["):
            host, _, port_s = s.rpartition(":")
            host = host.strip()
            try:
                port = int(port_s.strip())
            except ValueError:
                return None
            if host and 0 < port <= 65535:
                return (host, port)
        return None
    return None


def _endpoint_from_manifest(manifest: dict[str, Any] | None, key: str) -> Any:
    if not manifest:
        return None
    ep = manifest.get("endpoints")
    if not isinstance(ep, dict):
        return None
    return ep.get(key)


def _coalesce_endpoint(
    manifest: dict[str, Any] | None,
    manifest_key: str,
    env_name: str,
) -> Any:
    ev = os.environ.get(env_name, "").strip()
    if ev:
        return ev
    return _endpoint_from_manifest(manifest, manifest_key)


def _check_single_endpoint(
    checks: list[Check],
    check_name: str,
    raw: Any,
    default_port: int | None,
) -> None:
    """Pass with 'absent by design' when not configured; warn if configured but unreachable."""
    host_port = _parse_endpoint_value(raw, default_port)
    if host_port is None:
        if raw in (None, "", False):
            _add(checks, check_name, "pass", reason="absent by design (not configured)", configured=False)
        else:
            _add(checks, check_name, "warn", "Could not parse endpoint value", configured=True, raw=str(raw))
        return
    host, port = host_port
    if _tcp_reachable(host, port):
        _add(checks, check_name, "pass", host=host, port=port, configured=True)
    else:
        _add(checks, check_name, "warn", f"Configured but unreachable: {host}:{port}", host=host, port=port)


def run_doctor() -> DoctorReport:
    checks: list[Check] = []
    openclaw_exists = False
    gw_bin: str | None = None
    tehuti_ok = False
    sentinel_ok = False
    rt_ok = False
    sentinel_path_str: str | None = None
    lab = discover_lab_root()
    lab_str = str(lab) if lab else None

    manifest_path = find_first_existing(default_manifest_paths())
    manifest: dict[str, Any] | None = None
    if manifest_path:
        manifest = load_document(manifest_path)
        suff = manifest_path.suffix.lower()
        if suff in (".yaml", ".yml"):
            try:
                import yaml  # noqa: F401
            except ImportError:
                if manifest is None:
                    _add(
                        checks,
                        "manifest_yaml_dependency",
                        "warn",
                        "PyYAML not installed; cannot parse YAML manifest",
                        path=str(manifest_path),
                    )
            else:
                if manifest is None:
                    _add(
                        checks,
                        "manifest_load_fail",
                        "fail",
                        "YAML manifest present but invalid or not a mapping",
                        path=str(manifest_path),
                    )
                else:
                    _add(checks, "manifest_load_ok", "pass", path=str(manifest_path))
        elif suff == ".json":
            if manifest is None:
                _add(
                    checks,
                    "manifest_load_fail",
                    "fail",
                    "JSON manifest present but invalid or not an object",
                    path=str(manifest_path),
                )
            else:
                _add(checks, "manifest_load_ok", "pass", path=str(manifest_path))
        elif manifest is None:
            _add(checks, "manifest_load_fail", "fail", "Manifest could not be loaded", path=str(manifest_path))
        else:
            _add(checks, "manifest_load_ok", "pass", path=str(manifest_path))
    else:
        _add(checks, "manifest_missing", "warn", "No machine manifest found in default locations")

    machine_id = None
    role = None
    if manifest:
        machine_id = manifest.get("machine_id") or manifest.get("machineId")
        role = manifest.get("role")
    if not machine_id and os.environ.get("MAAT_MACHINE_ID"):
        machine_id = os.environ["MAAT_MACHINE_ID"].strip()

    if machine_id:
        _add(checks, "machine_id_present", "pass", machine_id=machine_id)
    else:
        _add(checks, "machine_id_present", "warn", "machine_id not in manifest or MAAT_MACHINE_ID")

    if role:
        _add(checks, "role_present", "pass", role=role)
    else:
        _add(checks, "role_present", "warn", "role not set in manifest")

    profile_path = find_first_existing(default_profile_paths())
    profile: dict[str, Any] | None = None
    if profile_path:
        profile = load_document(profile_path)
        psuff = profile_path.suffix.lower()
        if psuff in (".yaml", ".yml"):
            try:
                import yaml  # noqa: F401
            except ImportError:
                if profile is None:
                    _add(
                        checks,
                        "profile_yaml_dependency",
                        "warn",
                        "PyYAML not installed; cannot parse YAML profile",
                        path=str(profile_path),
                    )
            else:
                if profile is None:
                    _add(
                        checks,
                        "profile_load_fail",
                        "fail",
                        "YAML profile present but invalid or not a mapping",
                        path=str(profile_path),
                    )
                else:
                    _add(checks, "profile_load_ok", "pass", path=str(profile_path))
        elif psuff == ".json":
            if profile is None:
                _add(
                    checks,
                    "profile_load_fail",
                    "fail",
                    "JSON profile present but invalid or not an object",
                    path=str(profile_path),
                )
            else:
                _add(checks, "profile_load_ok", "pass", path=str(profile_path))
        elif profile is None:
            _add(checks, "profile_load_fail", "fail", "Profile could not be loaded", path=str(profile_path))
        else:
            _add(checks, "profile_load_ok", "pass", path=str(profile_path))
    else:
        _add(checks, "profile_optional_absent", "pass", reason="no profile file (optional)")

    install_mode = _derive_install_mode(manifest, role)

    # Sacred paths
    sacred: list[str] = []
    if manifest and isinstance(manifest.get("sacred_paths"), list):
        sacred = [str(x) for x in manifest["sacred_paths"]]
    if lab and not sacred:
        sacred = [
            str(lab / "maat-ecosystem" / "skeleton" / "schemas"),
            str(lab / "maat-ecosystem" / "soul"),
        ]

    for i, sp in enumerate(sacred):
        p = Path(sp).expanduser().resolve()
        tag = f"_{i}"
        if not p.exists():
            _add(
                checks,
                f"sacred_exists{tag}",
                "fail",
                f"Missing sacred path: {p}",
                path=str(p),
                constitutional=True,
                severity="critical",
            )
        else:
            _add(checks, f"sacred_exists{tag}", "pass", path=str(p))
            stat_d = _path_stat_detail(p)
            _add(checks, f"sacred_stat{tag}", "pass", **stat_d)
            try:
                writable = os.access(p, os.W_OK)
                if p.is_file():
                    writable = os.access(p.parent, os.W_OK)
            except OSError:
                writable = False
            if writable:
                _add(
                    checks,
                    f"sacred_permissions{tag}",
                    "warn",
                    "Sacred path is writable by current user (expected read-only in hardened setups)",
                    constitutional=True,
                    severity="high",
                    **stat_d,
                )
            if stat_d.get("writable_other") or stat_d.get("writable_group"):
                _add(
                    checks,
                    f"sacred_world_or_group_writable{tag}",
                    "warn",
                    "Sacred path writable by group or other (constitutional risk)",
                    constitutional=True,
                    severity="high",
                    **stat_d,
                )

    # Managed / volatile / user path classes
    managed_defaults: list[Path] = [lab / "maat-runtime"] if lab else []
    volatile_defaults: list[Path] = [Path.home() / ".maat" / "cache"]
    user_defaults: list[Path] = [Path.home() / ".maat" / "config"]

    def paths_from_manifest(key: str, defaults: list[Path]) -> list[Path]:
        if manifest and isinstance(manifest.get(key), list):
            return [Path(str(x)).expanduser() for x in manifest[key]]
        return list(defaults)

    managed_list = paths_from_manifest("managed_paths", managed_defaults)
    volatile_list = paths_from_manifest("volatile_paths", volatile_defaults)
    user_list = paths_from_manifest("user_paths", user_defaults)

    for i, mp in enumerate(managed_list):
        rp = mp.expanduser().resolve()
        if rp.exists():
            _add(checks, f"managed_path_resolves_{i}", "pass", path=str(rp))
        else:
            _add(checks, f"managed_path_resolves_{i}", "warn", f"managed path missing: {rp}", path=str(rp))

    for i, vp in enumerate(volatile_list):
        rp = vp.expanduser().resolve()
        if rp.exists() or rp.parent.exists():
            _add(checks, f"volatile_path_resolves_{i}", "pass", path=str(rp))
        else:
            _add(checks, f"volatile_path_resolves_{i}", "warn", f"volatile path not yet created: {rp}", path=str(rp))

    for i, up in enumerate(user_list):
        rp = up.expanduser().resolve()
        if rp.exists():
            _add(checks, f"user_path_resolves_{i}", "pass", path=str(rp))
        else:
            _add(checks, f"user_path_resolves_{i}", "warn", f"user path not yet created: {rp}", path=str(rp))

    # Gateway: config exists, permissions, workspace alignment
    openclaw = Path.home() / ".openclaw" / "openclaw.json"
    openclaw_exists = openclaw.is_file()
    if openclaw_exists:
        _add(checks, "gateway_openclaw_config", "pass", path=str(openclaw))
        try:
            oc_data = json.loads(openclaw.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            _add(checks, "gateway_openclaw_parse", "warn", str(e), path=str(openclaw))
            oc_data = None
        if isinstance(oc_data, dict):
            if _file_is_world_readable(openclaw):
                _add(
                    checks,
                    "gateway_config_world_readable",
                    "warn",
                    "openclaw.json is readable by others (prefer chmod 600)",
                    path=str(openclaw),
                )
            else:
                _add(checks, "gateway_config_protected", "pass", path=str(openclaw))
            ws = _openclaw_workspace(oc_data)
            if lab and ws:
                try:
                    wsl = Path(ws).expanduser().resolve()
                    if wsl == lab.resolve():
                        _add(checks, "gateway_workspace_lab_aligned", "pass", workspace=str(wsl))
                    else:
                        _add(
                            checks,
                            "gateway_workspace_lab_mismatch",
                            "warn",
                            f"OpenClaw workspace {wsl} != discovered lab root {lab.resolve()}",
                            workspace=str(wsl),
                            lab_root=str(lab.resolve()),
                        )
                except OSError:
                    _add(checks, "gateway_workspace_lab_mismatch", "warn", "Could not resolve workspace path", workspace=ws)
            elif lab:
                _add(
                    checks,
                    "gateway_workspace_lab_mismatch",
                    "warn",
                    "agents.defaults.workspace not set in openclaw.json",
                    lab_root=str(lab.resolve()),
                )
    else:
        _add(checks, "gateway_openclaw_config", "warn", "No ~/.openclaw/openclaw.json (gateway optional)")

    gw_bin = shutil.which("openclaw") or shutil.which("openclaw-gateway")
    if gw_bin:
        _add(checks, "gateway_binary_in_path", "pass", path=gw_bin)
    else:
        _add(checks, "gateway_binary_in_path", "warn", "No openclaw binary in PATH (optional)")

    if lab:
        tg = lab / "tehuti-guard"
        tehuti_ok = tg.is_dir()
        if tehuti_ok:
            _add(checks, "tehuti_guard_repo", "pass", path=str(tg))
        else:
            _add(checks, "tehuti_guard_repo", "warn", "tehuti-guard not under lab root", path=str(tg))
        sent = lab / "maatlangchain" / "core" / "agents" / "sentinel.py"
        sentinel_path_str = str(sent)
        sentinel_ok = sent.is_file()
        if sentinel_ok:
            _add(checks, "sentinel_code_present", "pass", path=str(sent))
        else:
            _add(checks, "sentinel_code_present", "warn", "sentinel.py not found under lab")
        rt_pkg = lab / "maat-runtime" / "package.json"
        rt_dir = lab / "maat-runtime"
        rt_ok = rt_dir.is_dir()
        if rt_ok:
            _add(checks, "maat_runtime_path_exists", "pass", path=str(rt_dir))
        else:
            _add(checks, "maat_runtime_path_exists", "warn", "maat-runtime directory not found under lab root", path=str(rt_dir))
        if rt_pkg.is_file():
            try:
                pj = json.loads(rt_pkg.read_text(encoding="utf-8"))
                ver = pj.get("version", "?")
                _add(checks, "maat_runtime_version", "pass", version=str(ver))
            except (OSError, json.JSONDecodeError) as e:
                _add(checks, "maat_runtime_version", "warn", str(e))
        else:
            _add(checks, "maat_runtime_version", "warn", "maat-runtime/package.json not found")
    elif not lab:
        _add(checks, "lab_root_discovery", "warn", "MAAT_LAB_ROOT unset and no maat-ecosystem in cwd parents — many checks skipped")

    if install_mode in ("server", "memory_host") and lab and not sentinel_ok:
        _add(
            checks,
            "sentinel_policy_server",
            "warn",
            "Sentinel code not found under lab; expected for server-class install_mode",
            constitutional=True,
            severity="high",
        )

    # Runtime immune
    il = os.environ.get("MAAT_IMMUNE_LOG", "").strip()
    if il:
        ip = Path(il).expanduser()
        parent_ok = ip.parent.is_dir() or ip.parent == Path("/")
        _add(
            checks,
            "immune_log_configured",
            "pass" if parent_ok else "warn",
            None if parent_ok else "MAAT_IMMUNE_LOG parent dir missing",
            path=il,
        )
    else:
        _add(checks, "immune_log_configured", "warn", "MAAT_IMMUNE_LOG not set (immune JSONL optional)")

    if lab:
        ext = lab / "maat-runtime" / "packages" / "coding-agent" / "examples" / "extensions" / "maat-immune"
        if ext.is_dir():
            _add(checks, "maat_immune_extension_dir", "pass", path=str(ext))
        else:
            _add(checks, "maat_immune_extension_dir", "warn", "maat-immune extension dir not found")

    # Versions
    py = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    _add(checks, "python_version", "pass", version=py, detail={"major": sys.version_info.major})

    try:
        node = subprocess.run(
            ["node", "-v"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        if node.returncode == 0 and node.stdout.strip():
            _add(checks, "node_version", "pass", version=node.stdout.strip())
        else:
            _add(checks, "node_version", "warn", "node not found or error")
    except (OSError, subprocess.TimeoutExpired):
        _add(checks, "node_version", "warn", "node not runnable")

    skip_ollama = os.environ.get("MAAT_DOCTOR_SKIP_OLLAMA", "").lower() in ("1", "true", "yes")
    if not skip_ollama:
        if _http_ok("http://127.0.0.1:11434/api/tags"):
            _add(checks, "ollama_reachable", "pass", url="http://127.0.0.1:11434")
        else:
            _add(checks, "ollama_unreachable", "warn", "Ollama not reachable on :11434")

    pg_url = os.environ.get("PGVECTOR_DB_URL") or os.environ.get("DATABASE_URL") or ""
    if pg_url.strip():
        _add(checks, "postgres_url_configured", "pass", masked="set")
        parsed = _parse_pg_host_port(pg_url)
        if parsed:
            host, port = parsed
            if _tcp_reachable(host, port):
                _add(checks, "postgres_reachable", "pass", host=host, port=port)
            else:
                _add(checks, "postgres_unreachable", "warn", f"Cannot connect to {host}:{port}")
        else:
            _add(checks, "postgres_reachable", "warn", "Could not parse DB URL for TCP check")
    else:
        _add(checks, "postgres_url_configured", "warn", "PGVECTOR_DB_URL / DATABASE_URL not set")

    redis_url = os.environ.get("REDIS_URL", "").strip()
    if redis_url:
        p = urlparse(redis_url)
        if p.hostname and p.port:
            ok = _tcp_reachable(p.hostname, p.port)
            _add(
                checks,
                "redis_reachable",
                "pass" if ok else "warn",
                None if ok else "Redis TCP check failed",
                host=p.hostname,
                port=p.port,
            )

    # Endpoints: manifest.endpoints + MAAT_DOCTOR_* env overrides — absent by design when unset
    mem_raw = _coalesce_endpoint(manifest, "memory_mcp", "MAAT_DOCTOR_MEMORY_MCP")
    teh_raw = _coalesce_endpoint(manifest, "tehuti_core", "MAAT_DOCTOR_TEHUTI")
    sent_raw = _coalesce_endpoint(manifest, "sentinel", "MAAT_DOCTOR_SENTINEL")
    ka_raw = _coalesce_endpoint(manifest, "ka_discovery", "MAAT_DOCTOR_KA_DISCOVERY")

    _check_single_endpoint(checks, "endpoint_memory_mcp", mem_raw, 8022)
    _check_single_endpoint(checks, "endpoint_tehuti_core", teh_raw, 8014)
    _check_single_endpoint(checks, "endpoint_sentinel", sent_raw, None)
    _check_single_endpoint(checks, "endpoint_ka_discovery", ka_raw, 8010)

    # Dangerous overrides (explicit per-var for machine JSON)
    if os.environ.get("MAAT_IMMUNE_ALLOW_SACRED") == "1":
        _add(checks, "dangerous_env_MAAT_IMMUNE_ALLOW_SACRED", "fail", "MAAT_IMMUNE_ALLOW_SACRED=1 (unsafe for production)")
    else:
        _add(checks, "dangerous_env_MAAT_IMMUNE_ALLOW_SACRED", "pass")
    if os.environ.get("MAAT_ALLOW_UNSAFE") == "1":
        _add(checks, "dangerous_env_MAAT_ALLOW_UNSAFE", "fail", "MAAT_ALLOW_UNSAFE=1")
    else:
        _add(checks, "dangerous_env_MAAT_ALLOW_UNSAFE", "pass")
    if os.environ.get("MAAT_IMMUNE_DISABLE") == "1":
        _add(checks, "dangerous_env_MAAT_IMMUNE_DISABLE", "warn", "MAAT_IMMUNE_DISABLE=1 (immune hooks off)")
    else:
        _add(checks, "dangerous_env_MAAT_IMMUNE_DISABLE", "pass")
    if os.environ.get("MAAT_SKIP_GUARD") == "1":
        _add(checks, "dangerous_env_MAAT_SKIP_GUARD", "warn", "MAAT_SKIP_GUARD=1")
    else:
        _add(checks, "dangerous_env_MAAT_SKIP_GUARD", "pass")

    ov = _overall(checks)
    rec = _recommendations(checks)
    recon = _reconciliation_rows(
        manifest,
        lab,
        openclaw_exists,
        gw_bin,
        tehuti_ok,
        sentinel_ok,
        rt_ok,
        sentinel_path_str,
    )

    return DoctorReport(
        machine_id=str(machine_id) if machine_id else None,
        role=str(role) if role else None,
        install_mode=install_mode,
        lab_root=lab_str,
        manifest_path=str(manifest_path) if manifest_path else None,
        profile_path=str(profile_path) if profile_path else None,
        overall_status=ov,
        checks=checks,
        recommended_actions=rec,
        reconciliation=recon,
    )


def report_to_json(report: DoctorReport) -> dict[str, Any]:
    counts = _summary_counts(report.checks)
    posture = _machine_trust_posture(report.checks, report.overall_status)
    blocking = _blocking_actions(report.checks)
    return {
        "schema": "maat-control-plane/doctor-report/v2.1",
        "timestamp": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "machine_id": report.machine_id,
        "role": report.role,
        "install_mode": report.install_mode,
        "lab_root": report.lab_root,
        "manifest_path": report.manifest_path,
        "profile_path": report.profile_path,
        "overall_status": report.overall_status,
        "machine_trust_posture": posture,
        "pass_count": counts["pass_count"],
        "warn_count": counts["warn_count"],
        "fail_count": counts["fail_count"],
        "constitutional_count": counts["constitutional_count"],
        "blocking_actions": blocking,
        "checks": [
            {
                "name": c.name,
                "status": c.status,
                "severity": c.severity,
                "constitutional": c.constitutional,
                "reason": c.reason,
                "recommended_action": c.recommended_action,
                "detail": c.detail,
            }
            for c in report.checks
        ],
        "reconciliation": report.reconciliation,
        "recommended_actions": report.recommended_actions,
    }


def format_human(report: DoctorReport) -> str:
    lines: list[str] = []
    lines.append("MAAT Doctor")
    lines.append("===========")
    lines.append(f"Overall: {report.overall_status.upper()}")
    sc = _summary_counts(report.checks)
    lines.append(
        f"Counts: pass={sc['pass_count']} warn={sc['warn_count']} fail={sc['fail_count']} "
        f"constitutional_checks={sc['constitutional_count']}",
    )
    lines.append(f"Trust posture: {_machine_trust_posture(report.checks, report.overall_status)}")
    lines.append(f"Install mode: {report.install_mode}")
    lines.append(f"Lab root: {report.lab_root or '(not discovered — set MAAT_LAB_ROOT or run from workspace)'}")
    lines.append(f"Manifest: {report.manifest_path or '—'}")
    lines.append(f"Profile: {report.profile_path or '—'}")
    lines.append(f"Machine id: {report.machine_id or '—'} | Role: {report.role or '—'}")
    lines.append("")
    for c in report.checks:
        sym = {"pass": "[PASS]", "warn": "[WARN]", "fail": "[FAIL]"}[c.status]
        cons = " [constitutional]" if c.constitutional else ""
        lines.append(f"  {sym} {c.name} [{c.severity}]{cons}")
        if c.reason:
            lines.append(f"       {c.reason}")
        if c.recommended_action and c.status != "pass":
            lines.append(f"       → {c.recommended_action}")
    if report.reconciliation:
        lines.append("")
        lines.append("Reconciliation (manifest expected vs observed):")
        for row in report.reconciliation:
            lines.append(
                f"  {row.get('service', '?')}: expected={row.get('expected')} found={row.get('found')} ({row.get('status')})",
            )
    ba = _blocking_actions(report.checks)
    if ba:
        lines.append("")
        lines.append("Blocking actions (before safe proceed):")
        for a in ba:
            lines.append(f"  - {a}")
    if report.recommended_actions:
        lines.append("")
        lines.append("Suggested next actions:")
        for a in report.recommended_actions:
            lines.append(f"  - {a}")
    return "\n".join(lines)
