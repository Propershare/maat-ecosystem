"""Write preflight — Host Body Awareness / Storage Consciousness Layer.

Before write:
  resolve path → detect mount → classify storage → estimate size →
  check authority → ALLOW | REVIEW | DENY_EVENT | NO_GO

Law: docs/MAAT_STORAGE_ROOTS_v0.1.yaml
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore

SCHEMA = "maat.storage.write_preflight.v0.1"

_DEFAULT_LAW_CANDIDATES = (
    Path("/home/suspect/.n8n/docs/MAAT_STORAGE_ROOTS_v0.1.yaml"),
    Path(__file__).resolve().parents[3] / "docs" / "MAAT_STORAGE_ROOTS_v0.1.yaml",
    Path("/mnt/data_drive/hermes/docs/MAAT_STORAGE_ROOTS_v0.1.yaml"),
)


class WriteDenied(PermissionError):
    """Durable/large write refused by storage consciousness."""


def _law_path() -> Path | None:
    env = os.environ.get("MAAT_STORAGE_ROOTS_YAML", "").strip()
    if env:
        p = Path(env)
        if p.is_file():
            return p
    for cand in _DEFAULT_LAW_CANDIDATES:
        if cand.is_file():
            return cand
    return None


def load_storage_law(path: str | Path | None = None) -> dict[str, Any]:
    """Load MAAT_STORAGE_ROOTS YAML. Fail closed if missing when enforcement on."""
    p = Path(path) if path else _law_path()
    if p is None or not p.is_file():
        return {
            "version": "0.1-embedded",
            "schema": "maat.storage_roots.v0.1",
            "machine": os.uname().nodename if hasattr(os, "uname") else "unknown",
            "storage_roots": _embedded_roots(),
            "deny_rules": _embedded_deny_rules(),
            "artifact_type_hints": {},
            "_source": "embedded_fallback",
        }
    if yaml is None:
        raise RuntimeError("PyYAML required to load MAAT_STORAGE_ROOTS — pip install pyyaml")
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    data["_source"] = str(p)
    return data


def _embedded_roots() -> dict[str, Any]:
    return {
        "cockpit": {
            "paths": ["/", "/home"],
            "max_write_mb_without_review": 50,
            "soft_full_pct": 90,
            "hard_full_pct": 95,
            "denied": ["model_weights", "training_outputs", "large_backups"],
        },
        "live_bulk": {
            "paths": ["/mnt/data_drive"],
            "max_write_mb_without_review": 8192,
            "soft_full_pct": 90,
            "hard_full_pct": 95,
        },
        "model_home": {
            "paths": ["/mnt/ai_models"],
            "max_write_mb_without_review": 65536,
            "soft_full_pct": 92,
            "hard_full_pct": 97,
        },
        "backup": {
            "paths": ["/mnt/ai_backup"],
            "max_write_mb_without_review": 65536,
            "soft_full_pct": 92,
            "hard_full_pct": 97,
        },
    }


def _embedded_deny_rules() -> list[dict[str, Any]]:
    return [
        {
            "name": "no_large_write_to_root",
            "if": {"mount_class": "cockpit", "estimated_size_mb_gt": 50},
            "then": "DENY_EVENT",
            "reason": "Large durable write refused on cockpit mount",
        },
        {
            "name": "no_model_weights_on_root",
            "if": {"mount_class": "cockpit", "artifact_type": "model_weight"},
            "then": "NO_GO",
            "reason": "Model weights must live under model_home",
        },
    ]


def resolve_mount(path: str | Path) -> dict[str, Any]:
    """Resolve realpath and find mount from /proc/mounts (longest prefix)."""
    target = Path(path).expanduser()
    try:
        resolved = target.resolve(strict=False)
    except Exception:
        resolved = target.absolute()

    mounts: list[tuple[str, str, str]] = []
    try:
        for line in Path("/proc/mounts").read_text(encoding="utf-8").splitlines():
            parts = line.split()
            if len(parts) < 3:
                continue
            device, mnt, fstype = parts[0], parts[1], parts[2]
            if mnt == "/" or mnt.startswith("/"):
                mounts.append((mnt, device, fstype))
    except OSError:
        mounts = [("/", "unknown", "unknown")]

    mounts.sort(key=lambda x: len(x[0]), reverse=True)
    s = str(resolved)
    for mnt, device, fstype in mounts:
        if mnt == "/":
            if s.startswith("/"):
                # only match / if no longer mount matched — keep as last resort
                continue
        if s == mnt or s.startswith(mnt.rstrip("/") + "/"):
            return {
                "path": s,
                "mountpoint": mnt,
                "device": device,
                "fstype": fstype,
            }
    # root fallback
    for mnt, device, fstype in mounts:
        if mnt == "/":
            return {
                "path": s,
                "mountpoint": "/",
                "device": device,
                "fstype": fstype,
            }
    return {
        "path": s,
        "mountpoint": "/",
        "device": "unknown",
        "fstype": "unknown",
    }


def classify_mount(mountpoint: str, law: dict[str, Any] | None = None) -> str:
    law = law or load_storage_law()
    roots = law.get("storage_roots") or {}
    # longest path match among declared roots
    best = ("unknown", -1)
    for class_name, spec in roots.items():
        if not isinstance(spec, dict):
            continue
        for p in spec.get("paths") or []:
            p = str(p)
            if mountpoint == p or mountpoint.startswith(p.rstrip("/") + "/"):
                if len(p) > best[1]:
                    best = (class_name, len(p))
            # also: if write path's mount is under a root path
            if p == "/" and mountpoint == "/":
                if len(p) >= best[1]:
                    best = (class_name, len(p))
    if best[0] != "unknown":
        return best[0]
    # path-based when mountpoint is / but target under /home
    return "cockpit" if mountpoint in ("/", "/home") or mountpoint.startswith("/home") else "unknown"


def classify_path(path: str | Path, law: dict[str, Any] | None = None) -> dict[str, Any]:
    law = law or load_storage_law()
    mount = resolve_mount(path)
    # Prefer classifying by resolved path against root path prefixes (not only mountpoint)
    resolved = mount["path"]
    roots = law.get("storage_roots") or {}
    mount_class = "unknown"
    best_len = -1
    for class_name, spec in roots.items():
        if not isinstance(spec, dict):
            continue
        for p in spec.get("paths") or []:
            p = str(p)
            if p == "/":
                # weakest match — only if nothing else
                if best_len < 0:
                    mount_class = class_name
                    best_len = 0
                continue
            if resolved == p or resolved.startswith(p.rstrip("/") + "/"):
                if len(p) > best_len:
                    mount_class = class_name
                    best_len = len(p)
    if mount_class == "unknown":
        mount_class = classify_mount(mount["mountpoint"], law)
    return {**mount, "mount_class": mount_class}


def infer_artifact_type(
    path: str | Path,
    *,
    artifact_type: str | None = None,
    law: dict[str, Any] | None = None,
) -> str | None:
    if artifact_type:
        return artifact_type
    law = law or load_storage_law()
    hints = law.get("artifact_type_hints") or {}
    s = str(path).lower()
    for atype, meta in hints.items():
        for sub in (meta or {}).get("path_substrings") or []:
            if str(sub).lower() in s:
                return atype
    return None


def disk_used_pct(path: str | Path) -> float | None:
    try:
        p = Path(path)
        probe = p if p.exists() else p.parent
        while not probe.exists() and probe != probe.parent:
            probe = probe.parent
        usage = shutil.disk_usage(probe)
        if not usage.total:
            return 100.0
        return round((usage.used / usage.total) * 100.0, 2)
    except OSError:
        return None


def check_write(
    path: str | Path,
    *,
    estimated_size_mb: float = 0.0,
    artifact_type: str | None = None,
    authorized: bool = False,
    law: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return allow/review/deny_event/no_go decision for a prospective write."""
    law = law or load_storage_law()
    classified = classify_path(path, law)
    mount_class = classified.get("mount_class") or "unknown"
    inferred = infer_artifact_type(path, artifact_type=artifact_type, law=law)
    used_pct = disk_used_pct(classified.get("path") or path)
    roots = law.get("storage_roots") or {}
    spec = roots.get(mount_class) if isinstance(roots.get(mount_class), dict) else {}
    max_mb = float((spec or {}).get("max_write_mb_without_review") or 50)
    soft = float((spec or {}).get("soft_full_pct") or 90)
    hard = float((spec or {}).get("hard_full_pct") or 95)

    decision = "ALLOW"
    matched_rule = None
    reason = "within policy"
    severity = {"ALLOW": 0, "REVIEW": 1, "DENY_EVENT": 2, "NO_GO": 3}

    # Explicit deny rules from law — keep highest severity match
    for rule in law.get("deny_rules") or []:
        cond = rule.get("if") or {}
        if cond.get("mount_class") and cond["mount_class"] != mount_class:
            continue
        if "artifact_type" in cond and cond["artifact_type"] != inferred:
            continue
        if "estimated_size_mb_gt" in cond and not (
            estimated_size_mb > float(cond["estimated_size_mb_gt"])
        ):
            continue
        if "used_pct_gte" in cond:
            if used_pct is None or used_pct < float(cond["used_pct_gte"]):
                continue
        candidate = str(rule.get("then") or "DENY_EVENT")
        if severity.get(candidate, 0) >= severity.get(decision, 0):
            decision = candidate
            matched_rule = rule.get("name")
            reason = str(rule.get("reason") or matched_rule)

    # Soft size gate if no harder rule fired
    if decision == "ALLOW" and estimated_size_mb > max_mb and not authorized:
        decision = "REVIEW" if mount_class != "cockpit" else "DENY_EVENT"
        matched_rule = "max_write_mb_without_review"
        reason = (
            f"estimated {estimated_size_mb}MB exceeds "
            f"{max_mb}MB without review on {mount_class}"
        )

    if decision == "ALLOW" and used_pct is not None and used_pct >= hard and not authorized:
        decision = "NO_GO"
        matched_rule = "hard_full"
        reason = f"{mount_class} at {used_pct}% >= hard {hard}%"

    if (
        decision == "ALLOW"
        and used_pct is not None
        and used_pct >= soft
        and estimated_size_mb > 10
        and mount_class == "cockpit"
        and not authorized
    ):
        decision = "DENY_EVENT"
        matched_rule = "cockpit_soft_full_large"
        reason = f"cockpit soft-full ({used_pct}%); refuse >10MB writes"

    if authorized and decision in ("DENY_EVENT", "REVIEW"):
        decision = "ALLOW"
        reason = f"operator authorized override of {matched_rule}"
        matched_rule = f"authorized:{matched_rule}"

    ok = decision == "ALLOW"
    return {
        "schema": SCHEMA,
        "ok": ok,
        "decision": decision,
        "path": classified.get("path"),
        "mountpoint": classified.get("mountpoint"),
        "mount_class": mount_class,
        "device": classified.get("device"),
        "artifact_type": inferred,
        "estimated_size_mb": estimated_size_mb,
        "used_pct": used_pct,
        "matched_rule": matched_rule,
        "reason": reason,
        "law_source": law.get("_source"),
        "hint": _hint(decision, mount_class),
    }


def assert_write(
    path: str | Path,
    *,
    estimated_size_mb: float = 0.0,
    artifact_type: str | None = None,
    authorized: bool = False,
) -> dict[str, Any]:
    result = check_write(
        path,
        estimated_size_mb=estimated_size_mb,
        artifact_type=artifact_type,
        authorized=authorized,
    )
    if result["decision"] in ("DENY_EVENT", "NO_GO"):
        raise WriteDenied(
            f"{result['decision']}:{result.get('matched_rule')}:{result.get('reason')}"
        )
    return result


def _hint(decision: str, mount_class: str) -> str:
    if decision == "ALLOW":
        return "proceed; log did/receipt after write"
    if mount_class == "cockpit":
        return (
            "route bulk to /mnt/data_drive (live_bulk), "
            "weights to /mnt/ai_models (model_home), "
            "archives to /mnt/ai_backup (backup)"
        )
    return "request REVIEW from Head Operator or shrink write"


def body_snapshot() -> dict[str, Any]:
    """Quick organ health for Head Operator report."""
    law = load_storage_law()
    organs = []
    for class_name, spec in (law.get("storage_roots") or {}).items():
        if not isinstance(spec, dict):
            continue
        paths = spec.get("paths") or []
        probe = next((p for p in paths if p != "/"), paths[0] if paths else None)
        if not probe:
            continue
        pct = disk_used_pct(probe)
        try:
            usage = shutil.disk_usage(probe if Path(probe).exists() else "/")
            free_g = round(usage.free / (1024**3), 1)
            total_g = round(usage.total / (1024**3), 1)
        except OSError:
            free_g = total_g = None
        organs.append(
            {
                "mount_class": class_name,
                "probe": probe,
                "used_pct": pct,
                "free_gb": free_g,
                "total_gb": total_g,
                "soft_full_pct": spec.get("soft_full_pct"),
                "hard_full_pct": spec.get("hard_full_pct"),
                "status": (
                    "NO_GO"
                    if pct is not None and pct >= float(spec.get("hard_full_pct") or 95)
                    else "WARN"
                    if pct is not None and pct >= float(spec.get("soft_full_pct") or 90)
                    else "OK"
                ),
            }
        )
    return {
        "schema": "maat.host_body.snapshot.v0.1",
        "machine": law.get("machine") or os.uname().nodename,
        "law_source": law.get("_source"),
        "organs": organs,
        "doctrine": "Root is the cockpit, not the warehouse.",
    }
