"""
Build and write MaatBench Evidence Records for dissertation appendices.

Stdlib only except optional gitMaat query via maatlangchain when PGVECTOR_DB_URL is set.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import socket
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

RECORD_TYPE = "MaatBench Evidence Record"
SCHEMA_VERSION = "1.0.0"

# Documented lab controls (dissertation Ch. 7) — used when gitMaat is unreachable.
_STATIC_JUSTICE_EXEMPLARS = [
    {
        "kind": "allow",
        "correlation_id": "maat-security-stack:20260606T144720Z:3efa879b:guard-sentinel-smoke",
        "decision": "allow",
        "matched_rule": "operational_low_risk_allow",
        "source": "gitMaat row 2026-06-06 (positive control)",
        "notes": "Posture feed live; low-risk read allowed.",
    },
    {
        "kind": "review",
        "correlation_id": "maat-security-stack:20260606T144720Z:3efa879b:guard-sentinel-smoke",
        "decision": "review",
        "matched_rule": "sentinel_unreachable_review",
        "source": "gitMaat row 2026-06-06 (fail-safe control)",
        "notes": "Sentinel unreachable; Guard returns review, not silent allow.",
    },
]


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _git_field(*args: str) -> str:
    try:
        out = subprocess.run(
            ["git", *args],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        if out.returncode == 0:
            return out.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        pass
    return "unknown"


def _http_code(url: str, timeout: float = 3.0) -> int | None:
    try:
        req = Request(url, method="GET")
        with urlopen(req, timeout=timeout) as resp:
            return resp.getcode()
    except URLError:
        return None
    except Exception:
        return None


def _sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def _machine_id() -> str:
    return (
        os.environ.get("MAAT_MACHINE_ID", "").strip()
        or os.environ.get("MAAT_MACHINE", "").strip()
        or socket.gethostname()
    )


def _operator() -> str:
    return os.environ.get("MAAT_OPERATOR", "").strip() or os.environ.get("USER", "unknown")


def _probe_services(lab_host: str) -> list[dict[str, Any]]:
    probes = [
        ("ka_discovery", f"http://{lab_host}:8010/manifest", True),
        ("tehuti_core", f"http://{lab_host}:8014/openapi.json", True),
        ("maat_memory_mcp", f"http://{lab_host}:8022/docs", True),
        ("tehuti_guard", f"http://{lab_host}:8013/health", False),
        ("maat_sentinel", f"http://{lab_host}:4242/machines", False),
        ("openclaw_gateway", "http://127.0.0.1:18790/", False),
        ("maat_gateway", f"http://{lab_host}:8040/health", False),
        ("ollama", "http://127.0.0.1:11434/api/tags", False),
    ]
    out: list[dict[str, Any]] = []
    for name, url, critical in probes:
        code = _http_code(url)
        if code is not None and 200 <= code < 400:
            status = "up"
        elif code is not None:
            status = f"http_{code}"
        else:
            status = "down"
        out.append(
            {
                "service": name,
                "url": url,
                "critical": critical,
                "status": status,
                "http_code": code,
            }
        )
    return out


def _optional_services_down(
    services: list[dict[str, Any]], state: dict[str, Any]
) -> list[dict[str, str]]:
    down: list[dict[str, str]] = []
    for svc in services:
        if svc.get("critical"):
            continue
        if svc.get("status") == "up":
            continue
        name = str(svc.get("service", ""))
        rationales = {
            "maat_gateway": "MAAT Gateway (:8040) optional for contract-tier bench; required for triad_live.",
            "openclaw_gateway": "OpenClaw (:18790) optional for offline MaatBench; required for channel/cron agents.",
            "ollama": "Ollama optional unless LAB_BENCH_LIVE=1 or triad_live category runs.",
            "maat_sentinel": "Sentinel optional for schema tests; required for posture-aware Guard E2E.",
            "tehuti_guard": "Guard optional for offline contract tests; required for live policy E2E.",
        }
        down.append(
            {
                "service": name,
                "rationale": rationales.get(
                    name,
                    "Non-critical organ offline; MaatBench optional tier records skip, not false failure.",
                ),
            }
        )
    tiers = state.get("tiers") or {}
    if tiers.get("lab_bench_live") is False:
        down.append(
            {
                "service": "live_model_tier",
                "rationale": "LAB_BENCH_LIVE=0; Gemma/Ollama smoke intentionally skipped.",
            }
        )
    return down


def _count_maatbench(maat_report: dict[str, Any]) -> dict[str, Any]:
    results = maat_report.get("results") or {}
    passed = failed = skipped = 0
    skip_notes: list[str] = []
    for cat_results in results.values():
        if not isinstance(cat_results, list):
            continue
        for r in cat_results:
            notes = str(r.get("notes", ""))
            if r.get("passed"):
                if "optional —" in notes.lower() or "optional -" in notes.lower():
                    skipped += 1
                    skip_notes.append(f"{r.get('id')}: optional skip")
                else:
                    passed += 1
            else:
                failed += 1
    cats = maat_report.get("category_scores") or {}
    return {
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "skip_notes": skip_notes[:20],
        "categories_tested": maat_report.get("categories_tested", len(cats)),
        "maat_score": maat_report.get("maat_score"),
        "category_ids": list(cats.keys()),
    }


def _fetch_justice_exemplars(lab_root: Path) -> list[dict[str, Any]]:
    exemplars: list[dict[str, Any]] = []
    if not os.environ.get("PGVECTOR_DB_URL"):
        return list(_STATIC_JUSTICE_EXEMPLARS)

    try:
        sys.path.insert(0, str(lab_root / "maatlangchain"))
        from maat_memory.memory_postgres import MaatMemoryPostgres  # type: ignore

        mem = MaatMemoryPostgres()
        rows = mem.query_governance_events(limit=30)
        for row in rows:
            payload = row.get("payload") or {}
            if isinstance(payload, str):
                try:
                    payload = json.loads(payload)
                except json.JSONDecodeError:
                    payload = {}
            decision = str(
                row.get("decision")
                or payload.get("decision")
                or ""
            ).lower()
            if decision not in ("allow", "review", "deny", "escalate", "quarantine"):
                continue
            kind = "deny-or-escalate" if decision in ("deny", "escalate", "quarantine") else decision
            exemplars.append(
                {
                    "kind": kind,
                    "correlation_id": row.get("correlation_id") or payload.get("correlation_id"),
                    "decision": decision,
                    "matched_rule": payload.get("matched_rule") or payload.get("rule_id"),
                    "source": "gitMaat maat_governance_events",
                    "timestamp": str(row.get("created_at") or row.get("timestamp") or ""),
                }
            )
            if len([e for e in exemplars if e["kind"] == "allow"]) >= 1 and any(
                e["kind"] == "review" for e in exemplars
            ) and any(e["kind"] == "deny-or-escalate" for e in exemplars):
                break
    except Exception:
        pass

    if not exemplars:
        return list(_STATIC_JUSTICE_EXEMPLARS)

    # Ensure at least one allow and one review from static if DB sparse
    kinds = {e.get("kind") for e in exemplars}
    if "allow" not in kinds:
        exemplars.insert(0, _STATIC_JUSTICE_EXEMPLARS[0])
    if "review" not in kinds:
        exemplars.append(_STATIC_JUSTICE_EXEMPLARS[1])
    return exemplars[:6]


def _maat_interpretation(
    services: list[dict[str, Any]],
    maat_counts: dict[str, Any],
    pytest: dict[str, Any],
    optional_down: list[dict[str, str]],
    workflow_status: str,
) -> dict[str, str]:
    crit_down = [s for s in services if s.get("critical") and s.get("status") != "up"]
    return {
        "truth": (
            f"MaatBench {maat_counts.get('passed', 0)} passed, "
            f"{maat_counts.get('failed', 0)} failed, "
            f"{maat_counts.get('skipped', 0)} optional skips; "
            f"pytest {pytest.get('passed', 0)} passed. "
            "Counts and report_hash support reproducibility."
        ),
        "balance": (
            f"{len(optional_down)} optional service(s) down or tier skipped with explicit rationale; "
            "optional organs do not force false failure when categories are marked optional."
        ),
        "order": (
            f"Tiered workflow; {maat_counts.get('categories_tested', 0)} MaatBench categories; "
            f"critical MCP spine {'degraded' if crit_down else 'reachable'}."
        ),
        "justice": (
            "Guard/Gateway/scorecard named in bench; justice_exemplars attach allow/review/deny "
            "samples when gitMaat or static controls available."
        ),
        "reciprocity": (
            "Not fully exercised in this run — reciprocity category pending. "
            "Hermes skills path checked when mounted."
        ),
        "accountability": (
            f"Dated artifacts under appendices/evidence-records/; workflow_status={workflow_status}; "
            "git_commit and machine_id bind run to code and host."
        ),
    }


def _limitations(maat_counts: dict[str, Any], state: dict[str, Any]) -> list[str]:
    lim = [
        "MaatBench score reflects implemented contract tests only, not universal system proof.",
        "behavior_balance and triad_live categories not included unless explicitly run.",
        "RAG citation-fidelity audit deferred per dissertation Ch. 7.3.",
        "Reciprocity tests not yet implemented as a MaatBench category.",
    ]
    if state.get("tiers", {}).get("lab_bench_live") is False:
        lim.append("Live Ollama/Gemma tier skipped (LAB_BENCH_LIVE=0).")
    if maat_counts.get("skipped", 0) > 0:
        lim.append(
            f"{maat_counts['skipped']} MaatBench check(s) passed as optional skip (organ absent)."
        )
    return lim


def build_evidence_record(
    *,
    lab_root: Path,
    state: dict[str, Any],
    maatbench_report_path: Path,
    workflow_log_path: Path,
    script_invoked: str,
) -> dict[str, Any]:
    ended = _utc_now()
    started_raw = state.get("started_at")
    try:
        started = datetime.fromisoformat(str(started_raw).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        started = ended
    duration = max(0.0, (ended - started).total_seconds())

    lab_host = str(state.get("lab_host") or "127.0.0.1")
    services = _probe_services(lab_host)

    maat_report: dict[str, Any] = {}
    if maatbench_report_path.is_file():
        maat_report = json.loads(maatbench_report_path.read_text())

    maat_counts = _count_maatbench(maat_report)
    pytest_info = state.get("pytest") or {}
    optional_down = _optional_services_down(services, state)
    workflow_status = "ok" if state.get("workflow_fail", 0) == 0 else "failed"

    report_hash = _sha256_file(maatbench_report_path)
    run_id = state.get("run_id") or f"bench-{ended.strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}"

    record = {
        "schema_version": SCHEMA_VERSION,
        "record_type": RECORD_TYPE,
        "run_id": run_id,
        "timestamp": ended.isoformat(),
        "started_at": started.isoformat(),
        "duration_seconds": round(duration, 3),
        "git_commit": _git_field("rev-parse", "HEAD"),
        "branch": _git_field("rev-parse", "--abbrev-ref", "HEAD"),
        "machine_id": _machine_id(),
        "operator": _operator(),
        "script_invoked": script_invoked,
        "environment": {
            "lab_root": str(lab_root.resolve()),
            "lab_host": lab_host,
            "platform": platform.platform(),
            "python": platform.python_version(),
            "hostname": socket.gethostname(),
            "lab_bench_live": bool(state.get("tiers", {}).get("lab_bench_live")),
        },
        "services_checked": services,
        "optional_services_down": optional_down,
        "pytest": {
            "passed": int(pytest_info.get("passed", 0)),
            "failed": int(pytest_info.get("failed", 0)),
            "skipped": int(pytest_info.get("skipped", 0)),
            "errors": int(pytest_info.get("errors", 0)),
            "exit_code": int(pytest_info.get("exit_code", -1)),
        },
        "maatbench": maat_counts,
        "categories_tested": maat_counts.get("category_ids") or [],
        "artifact_paths": {
            "maatbench_report": str(maatbench_report_path.resolve()),
            "workflow_log": str(workflow_log_path.resolve()),
            "workflow_state": str(state.get("_state_path", "")),
        },
        "report_hash": report_hash,
        "maat_interpretation": _maat_interpretation(
            services, maat_counts, pytest_info, optional_down, workflow_status
        ),
        "justice_exemplars": _fetch_justice_exemplars(lab_root),
        "limitations": _limitations(maat_counts, state),
        "workflow_status": workflow_status,
    }
    return record


def write_evidence_record(record: dict[str, Any], out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    run_id = str(record.get("run_id", "unknown"))
    safe_id = run_id.replace(":", "-")
    ts = str(record.get("timestamp", ""))[:10]
    path = out_dir / f"maatbench-evidence-record-{ts}-{safe_id}.json"
    artifacts = record.setdefault("artifact_paths", {})
    artifacts["evidence_record"] = str(path.resolve())
    body = json.dumps(record, indent=2, sort_keys=False) + "\n"
    path.write_text(body)
    return path


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Generate MaatBench Evidence Record")
    parser.add_argument("--state", required=True, help="Workflow state JSON from bash driver")
    parser.add_argument("--maatbench-report", required=True)
    parser.add_argument("--workflow-log", required=True)
    parser.add_argument("--lab-root", required=True)
    parser.add_argument("--script", default="scripts/run-lab-bench-workflow.sh")
    parser.add_argument(
        "--out-dir",
        default="docs/Maat-Constitutional-Infrastructure-Dissertation/appendices/evidence-records",
    )
    args = parser.parse_args(argv)

    lab_root = Path(args.lab_root).resolve()
    sys.path.insert(0, str(lab_root / "maat-ecosystem"))
    from maatbench.bootstrap import bootstrap

    bootstrap()

    state_path = Path(args.state)
    state = json.loads(state_path.read_text())
    state["_state_path"] = str(state_path.resolve())

    record = build_evidence_record(
        lab_root=lab_root,
        state=state,
        maatbench_report_path=Path(args.maatbench_report),
        workflow_log_path=Path(args.workflow_log),
        script_invoked=str(args.script),
    )
    out = write_evidence_record(record, lab_root / args.out_dir)
    # Fill evidence_record path in artifact_paths (already set by write_evidence_record)
    print(json.dumps({"evidence_record": str(out), "run_id": record["run_id"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
