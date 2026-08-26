"""Optional gateway route rows to gitMaat when MAAT_GATEWAY_MEMORY=1."""

from __future__ import annotations

import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _enabled() -> bool:
    v = os.environ.get("MAAT_GATEWAY_MEMORY", "").strip().lower()
    return v in ("1", "true", "yes")


def _ensure_maat_path() -> None:
    root = os.environ.get("MAAT_WORKSPACE_ROOT", "").strip()
    candidates: list[Path] = []
    if root:
        candidates.append(Path(root))
    here = Path(__file__).resolve()
    for base in [here.parents[i] for i in range(min(8, len(here.parents)))]:
        candidates.append(base)
    for base in candidates:
        ml = base / "maatlangchain"
        if (ml / "maat_memory").is_dir():
            mp = str(ml)
            if mp not in sys.path:
                sys.path.insert(0, mp)
            return


def log_gateway_route_row(
    *,
    expert_name: str,
    model: str,
    gateway_id: str | None,
    session_id: str,
    correlation_id: str,
    tags: list[str],
) -> None:
    if not _enabled():
        return
    try:
        _ensure_maat_path()
        from maat_memory.memory_postgres import MaatMemoryPostgres  # type: ignore

        mem = MaatMemoryPostgres()
        cid = correlation_id or str(uuid.uuid4())
        payload: dict[str, Any] = {
            "event_type": "gateway_route",
            "expert_name": expert_name,
            "model": model,
            "gateway_id": gateway_id,
            "session_id": session_id,
            "tags": tags,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "correlation_id": cid,
            "source_service": "maat-gateway-server",
        }
        mem.log_governance_event(
            payload,
            agent="maat-gateway-server",
            correlation_id=cid,
            source_service="maat-gateway-server",
        )
    except Exception:
        pass
