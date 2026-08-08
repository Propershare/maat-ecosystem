"""
Post-turn Guard validator.

Replaces "the model must self-check the scorecard" with "the runtime
computes the scorecard and asks Tehuti Guard for a decision". The scorecard
threshold (``pass_at=40``), RBL halt rule (``halt_flags>=3``), and
forbidden-actions list are sacred (see docs/MAAT-EVOLUTION-LANES.md) and
live in :mod:`gateway_contract`, not in prompt text.

Inputs
------
- An ArchivistRecord (or its dict form).
- Optional freshly produced content_text to run RBL + forbidden detectors
  against (useful when the record itself hasn't filled rbl_flags yet).

Outputs
-------
GuardDecision with:
    - decision: ``allow`` | ``deny`` | ``review``
    - reasons: list of short machine-readable reasons
    - scorecard: recomputed MaatScorecard dict (authoritative)
    - rbl_flags: detected flags (authoritative)
    - forbidden_hits: detected hits (authoritative)
    - next_action: ``proceed`` | ``reroute_deeper_model`` | ``halt``

The decision is first computed locally (always). If Guard HTTP is
reachable (``TEHUTI_GUARD_URL`` env, default ``http://127.0.0.1:8013``),
the validator POSTs to ``/decision`` as a confirmation. Guard's response
is respected for the final ``decision``, but the reasons list always
contains the validator's own reasons so the audit trail stays honest
when Guard is down.

Stdlib only. Network call is opt-in and tolerant.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any

from gateway_contract import (
    ArchivistRecord,
    HALT_AT_FLAGS,
    PASS_AT,
    SCHEMA_SCORECARD,
    SCORECARD_AXES,
    detect_forbidden_hits,
    detect_rbl_flags,
)

GUARD_URL_ENV = "TEHUTI_GUARD_URL"
DEFAULT_GUARD_URL = "http://127.0.0.1:8013"
GUARD_TIMEOUT_SEC = 1.5


@dataclass
class GuardDecision:
    decision: str  # "allow" | "deny" | "review"
    reasons: list[str] = field(default_factory=list)
    scorecard: dict[str, Any] | None = None
    rbl_flags: list[str] = field(default_factory=list)
    forbidden_hits: list[str] = field(default_factory=list)
    next_action: str = "proceed"
    guard_http_status: str = "unprobed"  # unprobed | ok | unreachable | bad_response | agreed | overrode
    guard_response: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        d = {
            "decision": self.decision,
            "reasons": list(self.reasons),
            "scorecard": self.scorecard,
            "rbl_flags": list(self.rbl_flags),
            "forbidden_hits": list(self.forbidden_hits),
            "next_action": self.next_action,
            "guard_http_status": self.guard_http_status,
        }
        if self.guard_response is not None:
            d["guard_response"] = self.guard_response
        return d


def _recompute_scorecard_from_record(
    record_dict: dict[str, Any], halt_flags: int
) -> dict[str, Any] | None:
    """Authoritative scorecard. If model supplied one, re-validate its math."""
    supplied = record_dict.get("maat_scorecard")
    if not supplied:
        if not record_dict.get("research_grade"):
            return None
        return {
            "schema": SCHEMA_SCORECARD,
            "scores": {axis: 0 for axis in SCORECARD_AXES},
            "total": 0,
            "pass_at": PASS_AT,
            "passed": False,
            "halt_flags": halt_flags,
            "correction_notes": "no scorecard supplied",
        }
    scores = dict(supplied.get("scores") or {})
    sanitized = {
        axis: max(0, min(10, int(scores.get(axis, 0)))) for axis in SCORECARD_AXES
    }
    total = sum(sanitized.values())
    passed = total >= PASS_AT and halt_flags < HALT_AT_FLAGS
    out = {
        "schema": SCHEMA_SCORECARD,
        "scores": sanitized,
        "total": total,
        "pass_at": PASS_AT,
        "passed": passed,
        "halt_flags": halt_flags,
    }
    correction = supplied.get("correction_notes")
    if not passed and not correction:
        correction = (
            f"auto: total={total}<{PASS_AT}" if total < PASS_AT else "auto: halt_flags>=3"
        )
    if correction:
        out["correction_notes"] = correction
    return out


def _call_guard_http(payload: dict[str, Any], url: str | None) -> tuple[str, dict[str, Any] | None]:
    """Fire-and-wait POST to Guard ``/decision``. Returns (status, body)."""
    target = (url or os.getenv(GUARD_URL_ENV) or DEFAULT_GUARD_URL).rstrip("/")
    try:
        req = urllib.request.Request(
            f"{target}/decision",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=GUARD_TIMEOUT_SEC) as resp:
            body = resp.read().decode("utf-8")
            try:
                return "ok", json.loads(body)
            except json.JSONDecodeError:
                return "bad_response", None
    except urllib.error.URLError:
        return "unreachable", None
    except TimeoutError:
        return "unreachable", None
    except Exception:  # noqa: BLE001
        return "unreachable", None


def validate_turn(
    record: ArchivistRecord | dict[str, Any],
    *,
    content_text: str | None = None,
    call_guard_http: bool = False,
    guard_url: str | None = None,
) -> GuardDecision:
    """Run the post-turn validator. ``content_text`` is the raw model output;
    if supplied it gives the best RBL / forbidden detector signal."""
    record_dict = record.to_dict() if isinstance(record, ArchivistRecord) else dict(record)

    ka2 = record_dict.get("ka2") or {}
    research_grade = bool(record_dict.get("research_grade"))

    rbl_from_text = detect_rbl_flags(content_text or "") if content_text else []
    forbidden_from_text = (
        detect_forbidden_hits(
            content_text or "", research_grade=research_grade, ka2=ka2 or None
        )
        if content_text
        else []
    )

    # Authoritative flag set = union(record-declared, detector-found)
    rbl_flags = sorted(set((record_dict.get("rbl_flags") or []) + rbl_from_text))
    forbidden_hits = sorted(
        set((record_dict.get("forbidden_hits") or []) + forbidden_from_text)
    )

    halt_flags = len(rbl_flags)
    scorecard = _recompute_scorecard_from_record(record_dict, halt_flags)

    reasons: list[str] = []
    decision = "allow"
    next_action = "proceed"

    if forbidden_hits:
        decision = "review"
        next_action = "reroute_deeper_model"
        reasons.append(f"forbidden_hits:{','.join(forbidden_hits)}")

    if halt_flags >= HALT_AT_FLAGS:
        decision = "deny"
        next_action = "halt"
        reasons.append(f"rbl_halt:{halt_flags}")

    if scorecard and not scorecard.get("passed", False):
        # Scorecard fail does not auto-halt — it downshifts to review so the
        # router can reroute once to a deeper model per Phase 1 of the plan.
        if decision != "deny":
            decision = "review"
            next_action = "reroute_deeper_model" if next_action == "proceed" else next_action
        reasons.append(
            f"scorecard_fail:total={scorecard.get('total')}<{PASS_AT}"
            if (scorecard.get("total") or 0) < PASS_AT
            else f"scorecard_fail:halt_flags={halt_flags}"
        )

    if research_grade and not ka2:
        decision = "review"
        next_action = "reroute_deeper_model" if next_action == "proceed" else next_action
        reasons.append("ka2_header_missing")

    guard_status = "unprobed"
    guard_body: dict[str, Any] | None = None
    if call_guard_http:
        guard_status, guard_body = _call_guard_http(
            {
                "schema": "maat.guard_decision_request.v1",
                "correlation_id": record_dict.get("correlation_id"),
                "gateway_id": record_dict.get("gateway_id"),
                "agent_id": record_dict.get("agent_id"),
                "local_decision": decision,
                "reasons": reasons,
                "scorecard": scorecard,
                "rbl_flags": rbl_flags,
                "forbidden_hits": forbidden_hits,
                "research_grade": research_grade,
            },
            url=guard_url,
        )
        if guard_status == "ok" and isinstance(guard_body, dict):
            guard_decision = guard_body.get("decision")
            if guard_decision in {"allow", "deny", "review"}:
                if guard_decision != decision:
                    guard_status = "overrode"
                    reasons.append(f"guard_override:{decision}->{guard_decision}")
                    decision = guard_decision
                    if decision == "deny":
                        next_action = "halt"
                    elif decision == "review":
                        next_action = "reroute_deeper_model"
                    else:
                        next_action = "proceed"
                else:
                    guard_status = "agreed"

    return GuardDecision(
        decision=decision,
        reasons=reasons,
        scorecard=scorecard,
        rbl_flags=rbl_flags,
        forbidden_hits=forbidden_hits,
        next_action=next_action,
        guard_http_status=guard_status,
        guard_response=guard_body,
    )


__all__ = [
    "GuardDecision",
    "validate_turn",
    "DEFAULT_GUARD_URL",
    "GUARD_URL_ENV",
]
