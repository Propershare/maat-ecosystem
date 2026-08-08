"""Tehuti Guard gate for Memory Plane enroll / invite consume (should)."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def _load_decide():
    candidates = [
        Path("/mnt/data_drive/hermes/workflowware-backend/guard/decide.py"),
        Path.home() / ".n8n/hermes/workflowware-backend/guard/decide.py",
    ]
    for p in candidates:
        if p.is_file():
            root = str(p.parent)
            if root not in sys.path:
                sys.path.insert(0, root)
            import decide as decide_mod  # type: ignore

            return decide_mod
    return None


def should_enroll(
    *,
    principal_id: str,
    agent_id: str,
    intended_ring: str = "outer",
    machine_id: str | None = None,
    human_approval: bool = False,
    lab_interim: bool = False,
) -> dict[str, Any]:
    """Guard should() for signup/enroll.

    Returns {ok, decision, reason, correlation_id?, guard?}.
    ok True only for allow / passive_only (enroll still at intended_ring capped).
    """
    ring = (intended_ring or "outer").lower()
    if ring not in ("outer", "middle", "inner"):
        ring = "outer"

    # Hard Isfet gates before package decide
    if ring == "inner" and not human_approval:
        return {
            "ok": False,
            "decision": "deny",
            "reason": "Inner-ring enroll requires explicit human approval",
            "intended_ring": ring,
        }
    if not principal_id:
        return {
            "ok": False,
            "decision": "deny",
            "reason": "principal_id required for enroll",
        }

    req = {
        "requested_action": (
            f"enroll agent {agent_id} for principal {principal_id} "
            f"at ring {ring} on machine {machine_id or 'unknown'}"
        ),
        "environment": "owned_home_lab",
        "target_owned_or_authorized": "yes",
        "scope_present": True,
        "case_id": f"enroll:{principal_id}:{agent_id}",
        "human_approval_present": human_approval or ring == "outer",
        "risk_hint": "passive" if ring == "outer" else "light_active",
        "operator_id": principal_id,
        "evidence_path": "maat_invites",
    }

    mod = _load_decide()
    if mod is None:
        if lab_interim:
            return {
                "ok": True,
                "decision": "allow",
                "reason": "Guard decide.py missing — lab_interim override (logged)",
                "intended_ring": ring,
                "lab_interim": True,
            }
        return {
            "ok": False,
            "decision": "escalate",
            "reason": "Guard decide.py not found; refuse silent enroll",
            "intended_ring": ring,
        }

    try:
        out = mod.decide(req)
    except Exception as e:  # noqa: BLE001
        return {
            "ok": False,
            "decision": "escalate",
            "reason": f"Guard decide failed: {e}",
            "intended_ring": ring,
        }

    decision = out.get("decision") or "deny"
    ok = decision in ("allow", "passive_only")
    # Cap: even if Guard allows, without human_approval never grant above outer via automation
    effective_ring = ring
    if ok and ring != "outer" and not human_approval:
        effective_ring = "outer"
        out = {
            **out,
            "reason": (out.get("reason") or "")
            + " | ring capped to outer without human_approval",
        }
    return {
        "ok": ok,
        "decision": decision,
        "reason": out.get("reason"),
        "correlation_id": out.get("correlation_id"),
        "intended_ring": effective_ring,
        "guard": out,
    }


def should_write_artifact(
    *,
    agent_ring: str,
    artifact_ring: str,
    title: str = "",
) -> dict[str, Any]:
    """Outer agent cannot write inner artifacts."""
    ranks = {"outer": 0, "middle": 1, "inner": 2}
    ar = ranks.get(agent_ring, 0)
    tr = ranks.get(artifact_ring, 0)
    if tr > ar:
        return {
            "ok": False,
            "decision": "deny",
            "reason": f"Agent ring {agent_ring} cannot write artifact ring {artifact_ring}",
        }
    if artifact_ring == "inner" and "secret" in (title or "").lower():
        return {
            "ok": False,
            "decision": "deny",
            "reason": "Refused secret-like inner title without review",
        }
    return {"ok": True, "decision": "allow", "reason": "write within ring"}
