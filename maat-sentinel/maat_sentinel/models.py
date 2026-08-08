"""Typed inputs for Sentinel v1 (aligned with maat doctor + maat-immune envelopes)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DoctorSnapshot:
    """A. Doctor snapshot (from `maat doctor --json` subset)."""

    machine_id: str
    install_mode: str
    machine_trust_posture: str
    blocking_actions: list[str]
    constitutional_count: int
    timestamp: str  # ISO-8601

    @classmethod
    def from_doctor_json(cls, doc: dict[str, Any]) -> DoctorSnapshot:
        return cls(
            machine_id=str(doc.get("machine_id") or ""),
            install_mode=str(doc.get("install_mode") or "unknown"),
            machine_trust_posture=str(doc.get("machine_trust_posture") or "unknown"),
            blocking_actions=list(doc.get("blocking_actions") or []),
            constitutional_count=int(doc.get("constitutional_count") or 0),
            timestamp=str(doc.get("timestamp") or ""),
        )


@dataclass
class ImmuneEventInput:
    """B. One line from maat-immune JSONL (or equivalent dict)."""

    severity: str
    event_type: str
    tags: list[str]
    blocked: bool
    session_id: str
    task_id: str | None
    machine_id: str
    timestamp: str

    @classmethod
    def from_envelope_dict(cls, row: dict[str, Any]) -> ImmuneEventInput:
        return cls(
            severity=str(row.get("severity") or ""),
            event_type=str(row.get("event_type") or ""),
            tags=list(row.get("tags") or []),
            blocked=bool(row.get("blocked")),
            session_id=str(row.get("session_id") or ""),
            task_id=row.get("task_id") if row.get("task_id") is not None else None,
            machine_id=str(row.get("machine_id") or ""),
            timestamp=str(row.get("timestamp") or ""),
        )


@dataclass
class PresenceRecord:
    """C. Canonical presence heartbeat (session-aware; stable fields for evolution)."""

    machine_id: str
    runtime: str
    session_id: str | None
    status: str
    last_seen_at: str
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PresenceRecord:
        return cls(
            machine_id=str(data.get("machine_id") or ""),
            runtime=str(data.get("runtime") or "unknown"),
            session_id=data.get("session_id"),
            status=str(data.get("status") or "unknown"),
            last_seen_at=str(data.get("last_seen_at") or ""),
            extra=dict(data.get("extra") or {}),
        )
