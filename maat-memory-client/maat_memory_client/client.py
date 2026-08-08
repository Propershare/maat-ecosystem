"""Maat Memory client — zero-config, mcpo wire contract."""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

from .agent_id import resolve_agent_id
from .discovery import discover_memory_url, resolve_api_key
from .transport import call_tool_safe, unwrap_search_results

log = logging.getLogger(__name__)


class MaatMemoryClient:
    """Self-configuring client for Maat Memory (:8022 mcpo tools)."""

    def __init__(
        self,
        *,
        base_url: Optional[str] = None,
        agent_id: Optional[str] = None,
        api_key: Optional[str] = None,
        strict: bool = False,
        timeout: float = 30.0,
        agent_prefix: str = "cursor",
    ) -> None:
        self.base_url = (base_url or discover_memory_url()).rstrip("/")
        self.agent_id = agent_id or resolve_agent_id(agent_prefix)
        self.api_key = api_key if api_key is not None else resolve_api_key()
        self.strict = strict
        self.timeout = timeout

    def _call(self, tool: str, args: Dict[str, Any]) -> Any:
        return call_tool_safe(
            self.base_url,
            tool,
            args,
            api_key=self.api_key,
            timeout=self.timeout,
            strict=self.strict,
        )

    def doctor(self) -> Dict[str, Any]:
        """Self-check: resolved config + connectivity."""
        health = self.health()
        ok = health is not None and not (
            isinstance(health, str) and health.strip().startswith("❌")
        )
        return {
            "base_url": self.base_url,
            "agent_id": self.agent_id,
            "api_key_set": bool(self.api_key),
            "reachable": ok,
            "health": health,
        }

    def health(self) -> Any:
        return self._call("memory_health", {})

    def remember(
        self,
        text: str,
        *,
        tags: Optional[List[str]] = None,
        topic: str = "note",
        source: str = "maat-memory-client",
    ) -> bool:
        """Store a durable learning/note (maps to memory_log_learning)."""
        tag_str = ", ".join(tags) if tags else ""
        insight = text if not tag_str else f"{text} [tags: {tag_str}]"
        raw = self._call(
            "memory_log_learning",
            {
                "agent": self.agent_id,
                "topic": topic,
                "insight": insight,
                "source": source,
                "confidence": 0.85,
            },
        )
        return _ok(raw)

    def recall(self, query: str, *, limit: int = 10) -> List[Dict[str, Any]]:
        """Semantic/text search (memory_search)."""
        raw = self._call(
            "memory_search",
            {"query": query, "agent": self.agent_id, "limit": limit},
        )
        return unwrap_search_results(raw)[:limit]

    def search(self, query: str, *, limit: int = 10, agent: Optional[str] = None) -> List[Dict[str, Any]]:
        raw = self._call(
            "memory_search",
            {"query": query, "agent": agent or self.agent_id, "limit": limit},
        )
        return unwrap_search_results(raw)[:limit]

    def log_task(
        self,
        title: str,
        description: str,
        *,
        status: str = "pending",
        priority: str = "medium",
    ) -> bool:
        raw = self._call(
            "memory_log_task",
            {
                "agent": self.agent_id,
                "title": title,
                "description": description,
                "status": status,
                "priority": priority,
            },
        )
        return _ok(raw)

    def log_decision(self, context: str, decision_made: str, rationale: str) -> bool:
        raw = self._call(
            "memory_log_decision",
            {
                "agent": self.agent_id,
                "context": context,
                "decision_made": decision_made,
                "rationale": rationale,
            },
        )
        return _ok(raw)

    def log_change(
        self,
        file_path: str,
        change_type: str,
        summary: str,
        reason: str,
    ) -> bool:
        raw = self._call(
            "memory_log_change",
            {
                "agent": self.agent_id,
                "file_path": file_path,
                "change_type": change_type,
                "summary": summary,
                "reason": reason,
            },
        )
        return _ok(raw)

    def log_learning(self, topic: str, insight: str, source: str, *, confidence: float = 0.7) -> bool:
        raw = self._call(
            "memory_log_learning",
            {
                "agent": self.agent_id,
                "topic": topic,
                "insight": insight,
                "source": source,
                "confidence": confidence,
            },
        )
        return _ok(raw)

    def get_tasks(self, *, status: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        raw = self._call("memory_get_tasks", {"status": status, "limit": limit})
        return _as_list(raw)

    def get_learnings(self, *, limit: int = 10) -> List[Dict[str, Any]]:
        raw = self._call("memory_get_learnings", {"limit": limit})
        return _as_list(raw)


def _ok(raw: Any) -> bool:
    if raw is None:
        return False
    if isinstance(raw, str) and raw.strip().startswith("❌"):
        return False
    if isinstance(raw, dict) and raw.get("ok") is True:
        return True
    return raw is not None


def _as_list(raw: Any) -> List[Dict[str, Any]]:
    if raw is None:
        return []
    if isinstance(raw, list):
        return [x for x in raw if isinstance(x, dict)]
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                return [x for x in parsed if isinstance(x, dict)]
        except json.JSONDecodeError:
            pass
    return []
