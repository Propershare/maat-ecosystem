#!/usr/bin/env python3
"""Reference adapter: envelope → POST /decision → enforce → JSONL (correlation_id).

Ma’at audit §6 embodiment: narrow repeatable proof without OpenClaw wiring.
See: docs/MAAT-AUDIT-ACTION-PLAN.md §6,
docs/TEHUTI-SENTINEL-GUARD-ADAPTER-CONTRACT.md §9.

Environment:
  GUARD_URL          Base URL (default: http://127.0.0.1:8013)
  GUARD_ADAPTER_LOG  JSONL append path (default: logs/guard_adapter_e2e.jsonl)

Usage (lab root, Guard on 8013):
  python3 scripts/guard_adapter_e2e_demo.py
  python3 scripts/guard_adapter_e2e_demo.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def _utc_now_iso() -> str:
    dt = datetime.now(timezone.utc).replace(microsecond=0)
    return dt.isoformat().replace("+00:00", "Z")


def _default_envelope(correlation_id: str) -> dict:
    actor_id = os.environ.get("GUARD_DEMO_ACTOR_ID", "guard_adapter_e2e_demo")
    return {
        "correlation_id": correlation_id,
        "machine_id": os.environ.get("GUARD_DEMO_MACHINE_ID", "staydangerous"),
        "actor": {"id": actor_id, "role": "agent"},
        "action": {
            "kind": "read",
            "resource": "/tmp/.guard-adapter-e2e-demo",
            "risk": "low",
        },
    }


def _enforce(decision: str | None) -> tuple[bool, str | None]:
    """Return (simulated_action_would_run, blocked_reason)."""
    if decision == "allow":
        return True, None
    if decision is None:
        return False, "no_decision"
    return False, f"policy_decision:{decision}"


def _append_jsonl(log_path: Path, record: dict) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(record, ensure_ascii=False, separators=(",", ":"))
    with log_path.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def main() -> int:
    desc = "Guard adapter E2E demo (audit §6 reference)."
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Build envelope and print JSON; do not call Guard or write log.",
    )
    parser.add_argument(
        "--correlation-id",
        default="",
        help="Fixed correlation_id (default: generate UUID).",
    )
    args = parser.parse_args()

    base = os.environ.get("GUARD_URL", "http://127.0.0.1:8013").rstrip("/")
    default_log = "logs/guard_adapter_e2e.jsonl"
    log_path = Path(os.environ.get("GUARD_ADAPTER_LOG", default_log))

    correlation_id = args.correlation_id.strip() or str(uuid.uuid4())
    envelope = _default_envelope(correlation_id)
    body = json.dumps(envelope).encode("utf-8")

    record: dict = {
        "schema": "guard_adapter_e2e_v1",
        "ts": _utc_now_iso(),
        "correlation_id": correlation_id,
        "envelope": envelope,
        "guard": None,
        "enforce": None,
        "error": None,
    }

    if args.dry_run:
        record["enforce"] = {
            "simulated_action_executed": False,
            "blocked_reason": "dry_run",
        }
        print(json.dumps(record, indent=2, ensure_ascii=False))
        return 0

    url = f"{base}/decision"
    req = Request(
        url,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "X-Correlation-ID": correlation_id,
        },
    )

    try:
        with urlopen(req, timeout=15) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            guard_json = json.loads(raw)
    except HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        record["error"] = {
            "type": "HTTPError",
            "code": e.code,
            "body": err_body[:2000],
        }
        record["enforce"] = {
            "simulated_action_executed": False,
            "blocked_reason": "http_error",
        }
        _append_jsonl(log_path, record)
        print(f"HTTP {e.code} from {url}\n{err_body[:500]}", file=sys.stderr)
        print(f"Wrote audit line to {log_path}", file=sys.stderr)
        return 1
    except (URLError, TimeoutError, json.JSONDecodeError) as e:
        record["error"] = {"type": type(e).__name__, "message": str(e)}
        record["enforce"] = {
            "simulated_action_executed": False,
            "blocked_reason": "request_or_parse_failed",
        }
        _append_jsonl(log_path, record)
        print(str(e), file=sys.stderr)
        print(f"Wrote audit line to {log_path}", file=sys.stderr)
        return 1

    record["guard"] = guard_json
    cid_echo = guard_json.get("correlation_id")
    if cid_echo != correlation_id:
        record["error"] = {
            "type": "correlation_mismatch",
            "expected": correlation_id,
            "got": cid_echo,
        }

    gdict = guard_json if isinstance(guard_json, dict) else {}
    decision = gdict.get("decision")
    dec = decision if isinstance(decision, str) else None
    executed, reason = _enforce(dec)
    record["enforce"] = {
        "simulated_action_executed": executed,
        "blocked_reason": reason,
    }

    _append_jsonl(log_path, record)

    print(json.dumps(record, indent=2, ensure_ascii=False))
    resolved = log_path.resolve()
    print(f"\nAppended joinable record to {resolved}", file=sys.stderr)
    if record.get("error"):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
