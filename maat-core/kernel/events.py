"""
MAAT Event Bus — First-Class Event System

Events are the nervous system of the ecology.
Not logs. Not print statements. Structured, typed, permanent.

Rules:
1. Every domain gets a namespace (agent.*, memory.*, task.*, etc.)
2. Payload is always a dict
3. Severity is meaningful (debug/info/warning/error/critical)
4. Events are append-only — never delete
5. Events enable everything downstream (Studio, replay, audit, learning)
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

# Canonical event types — see EVENTS.md for full taxonomy
CANONICAL_EVENTS = {
    # Agent lifecycle
    "agent.registered", "agent.started", "agent.stopped", "agent.identity_updated",
    # Memory
    "memory.written", "memory.retrieved", "memory.deleted",
    "memory.consolidated", "memory.constitutional_amended",
    # Task
    "task.created", "task.in_progress", "task.completed",
    "task.failed", "task.blocked", "task.escalated",
    # Tool
    "tool.called", "tool.denied", "tool.failed",
    # Policy
    "policy.evaluated", "policy.violated",
    "policy.escalation_requested", "policy.loaded",
    # Learning
    "learning.proposed", "learning.approved", "learning.applied",
    "learning.rolled_back", "learning.cycle_complete",
    # Adapter
    "adapter.loaded", "adapter.swapped", "adapter.failed",
    # Constitution
    "constitution.amended", "constitution.violation_detected",
    # Migration
    "migration.started", "migration.completed", "migration.failed",
    # Human
    "human.approval_requested", "human.approved",
    "human.rejected", "human.override",
    # Kernel
    "kernel.started", "kernel.stopped",
}


class EventBus:
    """
    First-class event system for the MAAT ecosystem.

    Subscribers are callables: fn(event: dict) -> None.
    Events persist to JSONL. Events are append-only.
    """

    def __init__(self, config: dict = None):
        config = config or {}
        self._subscribers: dict[str, list[Callable]] = {}
        self._wildcard: list[Callable] = []
        self._strict = config.get("strict", False)  # Warn on non-canonical events

        log_path = config.get("log_path")
        self._log_file = None
        if log_path:
            log_path = Path(log_path).expanduser()
            log_path.parent.mkdir(parents=True, exist_ok=True)
            self._log_file = open(log_path, "a")

    def subscribe(self, event_type: str, handler: Callable) -> None:
        """
        Subscribe to events.
        Use exact type for specific events.
        Use 'domain.*' for all events in a domain.
        Use '*' for all events.
        """
        if event_type == "*":
            self._wildcard.append(handler)
        else:
            self._subscribers.setdefault(event_type, []).append(handler)

    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        if event_type == "*":
            self._wildcard = [h for h in self._wildcard if h != handler]
        elif event_type in self._subscribers:
            self._subscribers[event_type] = [
                h for h in self._subscribers[event_type] if h != handler
            ]

    def emit(self, event: dict) -> None:
        """
        Emit an event. Persists to log and dispatches to subscribers.

        Events are NEVER deleted from the log. Append-only.
        """
        event_type = event.get("type", "unknown")

        # Strict mode: warn on non-canonical events
        if self._strict and event_type not in CANONICAL_EVENTS:
            domain = event_type.split(".")[0]
            if f"{domain}.*" not in CANONICAL_EVENTS:
                print(f"[events] WARNING: Non-canonical event type: {event_type}")

        # Persist (append-only)
        if self._log_file:
            self._log_file.write(json.dumps(event) + "\n")
            self._log_file.flush()

        # Dispatch to exact subscribers
        for handler in self._wildcard:
            self._safe_call(handler, event)
        for handler in self._subscribers.get(event_type, []):
            self._safe_call(handler, event)

        # Domain-level subscribers (e.g. "memory.*" gets all memory.* events)
        domain = event_type.split(".")[0]
        for handler in self._subscribers.get(f"{domain}.*", []):
            self._safe_call(handler, event)

    @staticmethod
    def _safe_call(handler: Callable, event: dict) -> None:
        try:
            handler(event)
        except Exception as e:
            print(f"[events] Handler {getattr(handler, '__name__', '?')} failed: {e}")

    def __del__(self):
        if self._log_file:
            try:
                self._log_file.close()
            except Exception:
                pass
