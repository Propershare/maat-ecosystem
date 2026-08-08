"""Propose → (Guard/review) → apply → rollback learning loop."""

from __future__ import annotations

import json
import uuid
from typing import Any

from . import db
from .registry import FleetRegistry

LEARNING_TYPES = frozenset(
    {
        "memory_consolidation",
        "prompt_refinement",
        "tool_usage_refinement",
        "fine_tune_metadata",
        "policy_update",
        "rollback",
    }
)

# Types that must not auto-apply without elevated approval
BLOCKED_AUTO_TYPES = frozenset({"policy_update"})


class LearningLoop:
    def __init__(self, registry: FleetRegistry | None = None):
        self.registry = registry or FleetRegistry()

    def propose(
        self,
        *,
        agent_id: str,
        topic: str,
        insight: str,
        source: str,
        learning_type: str = "memory_consolidation",
        confidence: float = 0.5,
        before_snapshot: dict[str, Any] | None = None,
        machine_id: str | None = None,
        application_context: str | None = None,
    ) -> dict[str, Any]:
        if learning_type not in LEARNING_TYPES:
            raise ValueError(f"invalid learning_type: {learning_type}")
        ok, reason = self.registry.assert_can_write_durable(agent_id)
        if not ok:
            return {
                "ok": False,
                "error": "not_enrolled",
                "reason": reason,
            }
        if learning_type in BLOCKED_AUTO_TYPES:
            guard_decision = "deny"
            note = "policy_update requires amendment path, not learning apply"
        else:
            guard_decision = "review"
            note = "proposed; applied=false until apply()"

        # Poison heuristic (Isfet-aligned minimal)
        lowered = (insight + " " + topic).lower()
        if any(
            x in lowered
            for x in ("never trust", "is an enemy", "delete the audit", "ignore governance")
        ):
            guard_decision = "deny"
            note = "Isfet: hostile/poison pattern in proposed learning"

        learning_id = str(uuid.uuid4())
        snap = before_snapshot or {"state": "unspecified"}
        row = db.execute_returning(
            """
            INSERT INTO maat_learnings (
                id, agent, topic, insight, source, confidence, applied,
                application_context, learning_type, before_snapshot,
                reversible, rolled_back, storage_class, machine_id, guard_decision
            ) VALUES (
                %s, %s, %s, %s, %s, %s, FALSE,
                %s, %s, %s::jsonb,
                TRUE, FALSE, 'learning', %s, %s
            )
            RETURNING *
            """,
            (
                learning_id,
                agent_id,
                topic[:255],
                insight,
                source[:255],
                confidence,
                application_context or note,
                learning_type,
                json.dumps(snap),
                machine_id,
                guard_decision,
            ),
        )
        return {
            "ok": True,
            "learning_id": learning_id,
            "guard_decision": guard_decision,
            "applied": False,
            "note": note,
            "row": row,
        }

    def apply(
        self,
        learning_id: str,
        *,
        approved_by: str,
        after_snapshot: dict[str, Any] | None = None,
        force: bool = False,
    ) -> dict[str, Any]:
        rows = db.fetchall("SELECT * FROM maat_learnings WHERE id = %s", (learning_id,))
        if not rows:
            return {"ok": False, "error": "not_found"}
        row = rows[0]
        if row.get("guard_decision") == "deny" and not force:
            return {
                "ok": False,
                "error": "guard_deny",
                "reason": row.get("application_context") or "denied",
            }
        if row.get("learning_type") in BLOCKED_AUTO_TYPES and not force:
            return {"ok": False, "error": "constitutional_or_policy_blocked"}
        agent_id = str(row.get("agent") or "")
        ok, reason = self.registry.assert_can_write_durable(agent_id)
        if not ok:
            return {"ok": False, "error": "not_enrolled", "reason": reason}

        after = after_snapshot or {"state": "applied", "approved_by": approved_by}
        updated = db.execute_returning(
            """
            UPDATE maat_learnings SET
                applied = TRUE,
                approved_by = %s,
                after_snapshot = %s::jsonb,
                guard_decision = 'allow',
                application_context = COALESCE(application_context, '') || ' | applied'
            WHERE id = %s
            RETURNING *
            """,
            (approved_by, json.dumps(after), learning_id),
        )
        return {"ok": True, "learning_id": learning_id, "applied": True, "row": updated}

    def rollback(self, learning_id: str, *, by_agent: str) -> dict[str, Any]:
        rows = db.fetchall("SELECT * FROM maat_learnings WHERE id = %s", (learning_id,))
        if not rows:
            return {"ok": False, "error": "not_found"}
        row = rows[0]
        if not row.get("reversible", True):
            return {"ok": False, "error": "not_reversible"}
        updated = db.execute_returning(
            """
            UPDATE maat_learnings SET
                applied = FALSE,
                rolled_back = TRUE,
                guard_decision = 'rollback',
                application_context = COALESCE(application_context, '') || %s
            WHERE id = %s
            RETURNING *
            """,
            (f" | rolled_back_by={by_agent}", learning_id),
        )
        return {
            "ok": True,
            "learning_id": learning_id,
            "rolled_back": True,
            "before_snapshot": row.get("before_snapshot"),
            "row": updated,
        }

    def list_proposed(self, limit: int = 20) -> list[dict[str, Any]]:
        return db.fetchall(
            """
            SELECT id, agent, topic, learning_type, guard_decision, confidence, timestamp
            FROM maat_learnings
            WHERE applied = FALSE AND COALESCE(rolled_back, FALSE) = FALSE
            ORDER BY timestamp DESC
            LIMIT %s
            """,
            (limit,),
        )

    def list_applied(self, topic_ilike: str | None = None, limit: int = 20) -> list[dict[str, Any]]:
        if topic_ilike:
            return db.fetchall(
                """
                SELECT id, agent, topic, insight, learning_type, confidence, timestamp
                FROM maat_learnings
                WHERE applied = TRUE AND topic ILIKE %s
                ORDER BY timestamp DESC
                LIMIT %s
                """,
                (f"%{topic_ilike}%", limit),
            )
        return db.fetchall(
            """
            SELECT id, agent, topic, insight, learning_type, confidence, timestamp
            FROM maat_learnings
            WHERE applied = TRUE
            ORDER BY timestamp DESC
            LIMIT %s
            """,
            (limit,),
        )
