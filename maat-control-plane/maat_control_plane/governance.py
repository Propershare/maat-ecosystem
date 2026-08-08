"""Read maat_governance_events — CLI backing for `maat governance`."""

from __future__ import annotations

import json
import os
import sys
from collections import Counter
from pathlib import Path
from typing import Any


def _ensure_maatlangchain_path() -> None:
    root = os.environ.get("MAAT_WORKSPACE_ROOT", "").strip()
    candidates: list[Path] = []
    if root:
        candidates.append(Path(root))
    here = Path(__file__).resolve()
    for i in range(0, min(12, len(here.parents))):
        candidates.append(here.parents[i])
    for base in candidates:
        ml = base / "maatlangchain"
        if (ml / "maat_memory").is_dir():
            mp = str(ml)
            if mp not in sys.path:
                sys.path.insert(0, mp)
            return


def _get_memory() -> Any:
    _ensure_maatlangchain_path()
    from maat_memory.memory_postgres import MaatMemoryPostgres  # type: ignore

    return MaatMemoryPostgres()


def _severity_from_row(row: dict[str, Any]) -> str:
    p = row.get("payload") or {}
    if isinstance(p, dict):
        s = p.get("severity")
        if s:
            return str(s)
    return ""


def _format_table(rows: list[dict[str, Any]], json_mode: bool) -> None:
    if json_mode:
        # JSON-serializable: datetime etc.
        out = []
        for r in rows:
            item = dict(r)
            if item.get("timestamp") is not None:
                item["timestamp"] = str(item["timestamp"])
            if item.get("created_at") is not None:
                item["created_at"] = str(item["created_at"])
            out.append(item)
        print(json.dumps(out, indent=2, default=str))
        return

    if not rows:
        print("(no rows)")
        return

    for r in rows:
        ts = str(r.get("timestamp") or "")[:19]
        rt = str(r.get("record_type") or "")
        src = str(r.get("source_service") or "")
        mid = str(r.get("machine_id") or "")
        cid = str(r.get("correlation_id") or "")[:16]
        sev = _severity_from_row(r)
        sev_s = f" sev={sev}" if sev else ""
        print(f"{ts}  {rt:28}  {src:18}  {mid:20}  {cid}{sev_s}")

    print()
    by_src = Counter(str(r.get("source_service") or "?") for r in rows)
    by_rt = Counter(str(r.get("record_type") or "?") for r in rows)
    print("In this result set — by source_service:", dict(by_src))
    print("In this result set — by record_type:", dict(by_rt))


def cmd_recent(args: Any) -> int:
    try:
        mem = _get_memory()
    except Exception as e:
        print(
            "Could not open maat-memory (PostgreSQL). "
            "Set PGVECTOR_DB_URL and MAAT_WORKSPACE_ROOT (lab root).",
            file=sys.stderr,
        )
        print(str(e), file=sys.stderr)
        return 2
    limit = max(1, min(500, int(getattr(args, "limit", 30))))
    rows = mem.query_governance_events(limit=limit)
    _format_table(rows, getattr(args, "json", False))
    return 0


def cmd_machine(args: Any) -> int:
    mid = (getattr(args, "machine_id", None) or "").strip()
    if not mid:
        print("machine_id required", file=sys.stderr)
        return 2
    try:
        mem = _get_memory()
    except Exception as e:
        print(str(e), file=sys.stderr)
        return 2
    limit = max(1, min(500, int(getattr(args, "limit", 50))))
    rows = mem.query_governance_events(machine_id=mid, limit=limit)
    _format_table(rows, getattr(args, "json", False))
    return 0


def cmd_correlation(args: Any) -> int:
    cid = (getattr(args, "correlation_id", None) or "").strip()
    if not cid:
        print("correlation_id required", file=sys.stderr)
        return 2
    try:
        mem = _get_memory()
    except Exception as e:
        print(str(e), file=sys.stderr)
        return 2
    limit = max(1, min(500, int(getattr(args, "limit", 100))))
    rows = mem.query_governance_events(correlation_id=cid, limit=limit)
    if not getattr(args, "json", False):
        print(
            f"Lifecycle for correlation_id={cid} "
            f"(oldest first, limit={limit})"
        )
        print()
    _format_table(rows, getattr(args, "json", False))
    return 0
