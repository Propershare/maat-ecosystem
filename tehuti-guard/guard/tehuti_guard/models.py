"""Action envelope and structured decision output."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

DecisionKind = Literal["allow", "deny", "review", "quarantine", "escalate"]
Severity = Literal["info", "warning", "high", "critical", "constitutional"]


@dataclass
class ActorSpec:
    id: str
    role: str = "unknown"


@dataclass
class ActionSpec:
    kind: str
    resource: str
    risk: str = "medium"  # low | medium | high | protected


@dataclass
class DecisionRequest:
    machine_id: str
    actor: ActorSpec
    action: ActionSpec

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DecisionRequest:
        a = data.get("actor") or {}
        ac = data.get("action") or {}
        return cls(
            machine_id=str(data.get("machine_id") or ""),
            actor=ActorSpec(
                id=str(a.get("id") or ""),
                role=str(a.get("role") or "unknown"),
            ),
            action=ActionSpec(
                kind=str(ac.get("kind") or "unknown"),
                resource=str(ac.get("resource") or ""),
                risk=str(ac.get("risk") or "medium").lower(),
            ),
        )


@dataclass
class DecisionResult:
    decision: DecisionKind
    severity: str
    reason: str
    tags: list[str] = field(default_factory=list)
    blocking_actions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision,
            "severity": self.severity,
            "reason": self.reason,
            "tags": self.tags,
            "blocking_actions": self.blocking_actions,
        }
