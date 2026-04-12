"""
MAAT Identity Store

Agent identities. Must outlive any runtime or adapter.
Identity is the one thing that never changes.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


class IdentityStore:
    """
    Stores agent identities in a JSON file.
    Simple, inspectable, migrateable.
    """

    def __init__(self, config: dict = None):
        config = config or {}
        store_path = config.get("path", Path.home() / ".maat" / "identities.json")
        self._path = Path(store_path)
        self._store: dict[str, dict] = {}
        self._load()

    def _load(self) -> None:
        if self._path.exists():
            try:
                self._store = json.loads(self._path.read_text())
            except Exception:
                self._store = {}

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(self._store, indent=2))

    def register(self, identity: dict) -> str:
        """Register an agent. Returns agent_id."""
        agent_id = identity.get("id") or str(uuid.uuid4())
        identity["id"] = agent_id
        identity.setdefault("created_at", datetime.now(timezone.utc).isoformat())
        identity.setdefault("version", "1")
        self._store[agent_id] = identity
        self._save()
        return agent_id

    def get(self, agent_id: str) -> Optional[dict]:
        return self._store.get(agent_id)

    def get_by_name(self, name: str) -> Optional[dict]:
        for identity in self._store.values():
            if identity.get("name") == name:
                return identity
        return None

    def list_agents(self) -> list[dict]:
        return list(self._store.values())

    def update(self, agent_id: str, updates: dict) -> bool:
        if agent_id not in self._store:
            return False
        self._store[agent_id].update(updates)
        self._save()
        return True
