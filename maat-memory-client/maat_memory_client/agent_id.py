"""Resolve agent id without importing maatlangchain."""

from __future__ import annotations

import os
import socket


def resolve_agent_id(prefix: str = "cursor") -> str:
    explicit = os.environ.get("MAAT_AGENT_ID", "").strip()
    if explicit:
        return explicit
    hostname = socket.gethostname().lower().replace(".", "_")
    p = prefix.lower().strip() or "agent"
    if p == "cursor":
        return f"cursor_{hostname}"
    return f"{p}_{hostname}"
