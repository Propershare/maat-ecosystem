"""Agent-side client for mediated Maat Memory writes (no DSN)."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any, List, Optional


class MediatedMemoryClientError(RuntimeError):
    pass


class MediatedMemoryClient:
    """HTTP client — agents hold a token, never PGVECTOR_DB_URL."""

    def __init__(
        self,
        base_url: str | None = None,
        token: str | None = None,
    ):
        self.base_url = (
            base_url
            or os.environ.get("MAAT_MEMORY_WRITE_URL")
            or "http://127.0.0.1:8023"
        ).rstrip("/")
        self.token = token or os.environ.get("MAAT_MEMORY_AGENT_TOKEN") or ""
        if not self.token:
            raise MediatedMemoryClientError(
                "MAAT_MEMORY_AGENT_TOKEN required — agents do not use PGVECTOR_DB_URL"
            )

    def _post(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}{path}",
            data=data,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "X-Maat-Memory-Token": self.token,
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", errors="replace")
            raise MediatedMemoryClientError(f"HTTP {e.code}: {detail}") from e

    def log_task(
        self,
        agent: str,  # ignored — identity from token; kept for API compat
        title: str,
        description: str,
        status: str = "pending",
        priority: str = "medium",
        related_files: Optional[List[str]] = None,
        dependencies: Optional[List[str]] = None,
        *,
        origin: Optional[str] = None,
    ) -> str:
        if origin is not None:
            raise MediatedMemoryClientError(
                "origin must not be supplied — mediator stamps from identity"
            )
        # related_files/dependencies not yet on write service — drop for v1
        out = self._post(
            "/v1/tasks",
            {
                "title": title,
                "description": description,
                "status": status,
                "priority": priority,
            },
        )
        return out["task_id"]

    def log_decision(
        self,
        agent: str,
        context: str,
        decision_made: str,
        rationale: str,
        options_considered: Optional[List[str]] = None,
        maat_alignment: Optional[dict] = None,
        *,
        origin: Optional[str] = None,
    ) -> str:
        if origin is not None:
            raise MediatedMemoryClientError(
                "origin must not be supplied — mediator stamps from identity"
            )
        out = self._post(
            "/v1/decisions",
            {
                "context": context,
                "decision_made": decision_made,
                "rationale": rationale,
                "options_considered": options_considered,
            },
        )
        return out["decision_id"]
