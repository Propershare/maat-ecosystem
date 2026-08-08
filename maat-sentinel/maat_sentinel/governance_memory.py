"""Optional compact rows to maat-memory when MAAT_SENTINEL_MEMORY=1.

Logs:
- sentinel_posture_summary — when unified_view fingerprint changes after ingest
- sentinel_immune_alert — constitutional-severity immune events (per ingest)
"""

from __future__ import annotations

import logging
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

_LAST_FP: dict[str, tuple[Any, ...]] = {}


def _enabled() -> bool:
    v = os.environ.get("MAAT_SENTINEL_MEMORY", "").strip().lower()
    return v in ("1", "true", "yes")


def _ensure_maat_path() -> None:
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


def _fingerprint(uv: dict[str, Any]) -> tuple[Any, ...]:
    im = uv.get("immune_summary") or {}
    doc = uv.get("doctor") or {}
    posture = str(doc.get("machine_trust_posture") or "").lower()
    return (
        str(uv.get("machine_status") or ""),
        int(im.get("recent_constitutional_count") or 0),
        int(im.get("recent_blocked_count") or 0),
        posture,
        bool(uv.get("requires_human_review")),
    )


def _log_row(payload: dict[str, Any]) -> None:
    if not _enabled():
        return
    try:
        _ensure_maat_path()
        from maat_memory.memory_postgres import (  # type: ignore
            MaatMemoryPostgres,
        )

        mem = MaatMemoryPostgres()
        cid = str(uuid.uuid4())
        p = {
            **payload,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "correlation_id": payload.get("correlation_id") or cid,
            "source_service": "maat-sentinel",
        }
        mem.log_governance_event(
            p,
            agent="maat-sentinel",
            machine_id=str(payload.get("machine_id") or "") or None,
            correlation_id=p.get("correlation_id"),
            source_service="maat-sentinel",
        )
    except Exception as e:
        log.debug("MAAT_SENTINEL_MEMORY: skip or failed: %s", e)


def after_ingest(machine_id: str) -> None:
    """After doctor / immune / presence ingest when machine_id is known."""
    if not machine_id or not _enabled():
        return
    try:
        from maat_sentinel.surface import unified_view

        uv = unified_view(machine_id)
        fp = _fingerprint(uv)
        prev = _LAST_FP.get(machine_id)
        if prev == fp:
            return
        _LAST_FP[machine_id] = fp
        im = uv.get("immune_summary") or {}
        doc = uv.get("doctor") or {}
        payload: dict[str, Any] = {
            "record_type": "sentinel_posture_summary",
            "machine_id": machine_id,
            "machine_status": uv.get("machine_status"),
            "risk_summary": uv.get("risk_summary"),
            "requires_human_review": uv.get("requires_human_review"),
            "machine_trust_posture": doc.get("machine_trust_posture"),
            "constitutional_count_doctor": doc.get("constitutional_count"),
            "blocking_actions_count": len(doc.get("blocking_actions") or []),
            "recent_constitutional_count": im.get(
                "recent_constitutional_count"
            ),
            "recent_blocked_count": im.get("recent_blocked_count"),
            "recent_critical_count": im.get("recent_critical_count"),
            "fingerprint_changed": prev is not None,
        }
        _log_row(payload)
    except Exception as e:
        log.debug("after_ingest governance: %s", e)


def after_immune_constitutional(ev: Any) -> None:
    """Log compact constitutional alert (does not replace posture_summary)."""
    if not _enabled():
        return
    sev = str(getattr(ev, "severity", "") or "").lower()
    if sev != "constitutional":
        return
    payload = {
        "record_type": "sentinel_immune_alert",
        "machine_id": getattr(ev, "machine_id", "") or "",
        "severity": "constitutional",
        "event_type": getattr(ev, "event_type", ""),
        "blocked": getattr(ev, "blocked", False),
        "session_id": getattr(ev, "session_id", "") or None,
        "task_id": getattr(ev, "task_id", None),
    }
    _log_row(payload)
