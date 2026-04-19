"""Guard v1 rules — Sentinel unified_view + action envelope."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from tehuti_guard import POLICY_VERSION
from tehuti_guard.models import ActionSpec, DecisionRequest, DecisionResult


def _blocking_from_view(view: dict[str, Any]) -> list[str]:
    return list(view.get("blocking_actions") or [])


def _high_impact(action: ActionSpec) -> bool:
    r = (action.risk or "medium").lower()
    k = (action.kind or "").lower()
    if r in ("high", "protected"):
        return True
    if k in ("deploy", "delete", "execute", "write", "promote"):
        return True
    return False


def compute_explanation_id(
    req: DecisionRequest, matched_rules: list[str]
) -> str:
    """Deterministic id for correlating Studio, memory, and repeated explains.

    Hashes canonical envelope fields + policy_version + matched_rules (outcome).
    """
    payload = {
        "machine_id": req.machine_id,
        "actor": {"id": req.actor.id, "role": req.actor.role},
        "action": {
            "kind": req.action.kind,
            "resource": req.action.resource,
            "risk": req.action.risk,
        },
        "policy_version": POLICY_VERSION,
        "matched_rules": matched_rules,
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )
    digest = hashlib.sha256(raw).hexdigest()
    return f"sha256:{digest}"


def _protected_action(action: ActionSpec) -> bool:
    r = (action.risk or "").lower()
    if r == "protected":
        return True
    res = (action.resource or "").lower()
    return (
        "sacred" in res
        or "skeleton/schemas" in res
        or "maat-ecosystem/soul" in res
    )


def _evaluate_core(
    req: DecisionRequest, view: dict[str, Any] | None
) -> tuple[DecisionResult, list[str]]:
    """Return decision plus stable matched_rules ids for /explain and operators."""
    if not req.machine_id.strip():
        return (
            DecisionResult(
                "review",
                "warning",
                "machine_id is required",
                ["invalid_request"],
                [],
            ),
            ["invalid_machine_id"],
        )

    if view is None:
        return (
            DecisionResult(
                "review",
                "warning",
                "Sentinel unified view unavailable — cannot align posture",
                ["sentinel_unreachable"],
                [
                    "Check TEHUTI_GUARD_SENTINEL_URL and that "
                    "maat-sentinel serve is running"
                ],
            ),
            ["sentinel_unreachable_review"],
        )

    status = str(view.get("machine_status") or "unknown").lower()
    immune = view.get("immune_summary") or {}
    const_n = int(immune.get("recent_constitutional_count") or 0)
    blocking = _blocking_from_view(view)

    risk = (req.action.risk or "medium").lower()
    hi = _high_impact(req.action)
    prot = _protected_action(req.action)

    # 1) Constitutional breach posture
    if status == "constitutional_breach":
        if prot or risk == "high":
            return (
                DecisionResult(
                    "deny",
                    "constitutional",
                    (
                        "Machine posture is constitutional_breach; "
                        "protected/high action blocked"
                    ),
                    ["posture_constitutional_breach"],
                    blocking,
                ),
                ["posture_constitutional_breach_deny"],
            )
        return (
            DecisionResult(
                "quarantine",
                "high",
                (
                    "Machine posture is constitutional_breach; "
                    "action quarantined for review"
                ),
                ["posture_constitutional_breach"],
                blocking,
            ),
            ["posture_constitutional_breach_quarantine"],
        )

    # 2) Unsafe posture
    if status == "unsafe":
        if hi:
            return (
                DecisionResult(
                    "deny",
                    "high",
                    "Machine posture is unsafe; high-impact action denied",
                    ["posture_unsafe"],
                    blocking,
                ),
                ["posture_unsafe_deny"],
            )
        return (
            DecisionResult(
                "review",
                "warning",
                "Machine posture is unsafe; review required before proceeding",
                ["posture_unsafe"],
                blocking,
            ),
            ["posture_unsafe_review"],
        )

    # 3) Recent constitutional immune signals (Sentinel window)
    if const_n > 0:
        if hi:
            return (
                DecisionResult(
                    "escalate",
                    "critical",
                    (
                        f"Recent constitutional immune events ({const_n}) "
                        "with high-impact action"
                    ),
                    ["immune_constitutional_recent"],
                    blocking,
                ),
                ["immune_constitutional_recent_escalate"],
            )
        return (
            DecisionResult(
                "quarantine",
                "high",
                "Recent constitutional immune activity; hold for review",
                ["immune_constitutional_recent"],
                blocking,
            ),
            ["immune_constitutional_recent_quarantine"],
        )

    # 4) Degraded + risky
    if status == "degraded" and hi:
        return (
            DecisionResult(
                "review",
                "warning",
                "Degraded machine posture; high-impact action needs review",
                ["posture_degraded", "high_impact"],
                blocking,
            ),
            ["posture_degraded_high_impact_review"],
        )

    # 5) Trusted path — low risk
    if status == "operational" and risk == "low":
        return (
            DecisionResult(
                "allow",
                "info",
                "Operational posture; low-risk action allowed",
                ["allow"],
                [],
            ),
            ["operational_low_risk_allow"],
        )

    # Default: medium-risk or unknown posture
    if hi:
        return (
            DecisionResult(
                "review",
                "warning",
                "Default path: high-impact action requires review",
                ["default_review"],
                blocking,
            ),
            ["default_high_impact_review"],
        )

    return (
        DecisionResult(
            "allow",
            "info",
            "Default allow for non-high-impact action",
            ["default_allow"],
            [],
        ),
        ["default_allow"],
    )


def evaluate(
    req: DecisionRequest, view: dict[str, Any] | None
) -> DecisionResult:
    result, _ = _evaluate_core(req, view)
    return result


def evaluate_with_rules(
    req: DecisionRequest, view: dict[str, Any] | None
) -> tuple[DecisionResult, list[str]]:
    """Same as evaluate plus matched_rules — used by /decision and memory rows."""
    return _evaluate_core(req, view)


def explain_envelope(
    req: DecisionRequest, view: dict[str, Any] | None
) -> dict[str, Any]:
    """Human-oriented explanation — same inputs as evaluate; for POST /explain."""
    result, matched_rules = _evaluate_core(req, view)
    tags = list(result.tags)
    if result.decision != "allow" and "policy_rejection" not in tags:
        tags.append("policy_rejection")
    explanation_id = compute_explanation_id(req, matched_rules)
    return {
        "explanation_id": explanation_id,
        "decision": result.decision,
        "reason": result.reason,
        "matched_rules": matched_rules,
        "severity": result.severity,
        "tags": tags,
    }


def policy_rules_document() -> dict[str, Any]:
    """Static catalog for GET /rules — must stay aligned with evaluate()."""
    return {
        "policy_version": POLICY_VERSION,
        "service": "tehuti-guard-api",
        "rules": [
            {
                "id": "invalid_machine_id",
                "order": 0,
                "when": "empty machine_id",
                "decision": "review",
                "tags": ["invalid_request"],
            },
            {
                "id": "sentinel_unreachable",
                "order": 1,
                "when": "Sentinel unified view is None (fetch failed)",
                "decision": "review",
                "tags": ["sentinel_unreachable"],
            },
            {
                "id": "posture_constitutional_breach",
                "order": 2,
                "when": "machine_status == constitutional_breach",
                "decision": "deny or quarantine",
                "detail": (
                    "deny if protected action or high risk; else quarantine"
                ),
                "tags": ["posture_constitutional_breach"],
            },
            {
                "id": "posture_unsafe",
                "order": 3,
                "when": "machine_status == unsafe",
                "decision": "deny or review",
                "detail": "deny if high-impact; else review",
                "tags": ["posture_unsafe"],
            },
            {
                "id": "immune_constitutional_recent",
                "order": 4,
                "when": "immune_summary.recent_constitutional_count > 0",
                "decision": "escalate or quarantine",
                "detail": "escalate if high-impact; else quarantine",
                "tags": ["immune_constitutional_recent"],
            },
            {
                "id": "posture_degraded_high_impact",
                "order": 5,
                "when": "machine_status == degraded and high-impact action",
                "decision": "review",
                "tags": ["posture_degraded", "high_impact"],
            },
            {
                "id": "operational_low_risk",
                "order": 6,
                "when": "machine_status == operational and action.risk == low",
                "decision": "allow",
                "tags": ["allow"],
            },
            {
                "id": "default_high_impact",
                "order": 7,
                "when": "fallback: high-impact action",
                "decision": "review",
                "tags": ["default_review"],
            },
            {
                "id": "default_allow",
                "order": 8,
                "when": "fallback: non-high-impact action",
                "decision": "allow",
                "tags": ["default_allow"],
            },
        ],
    }
