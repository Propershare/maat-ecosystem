"""Live session presence — who is active across the fleet (not transcripts)."""

from __future__ import annotations

import json
import uuid
from typing import Any

from . import db


class SessionPresence:
    def register(
        self,
        *,
        agent_id: str,
        machine_id: str | None = None,
        role: str = "general",
        ring: str = "outer",
        task_id: str | None = None,
        current_topic: str | None = None,
        current_tools: list[str] | None = None,
        session_id: str | None = None,
        status: str = "active",
    ) -> dict[str, Any]:
        sid = session_id or str(uuid.uuid4())
        ring_n = ring if ring in ("inner", "middle", "outer") else "outer"
        row = db.execute_returning(
            """
            INSERT INTO maat_session_presence (
                session_id, agent_id, machine_id, role, ring, task_id, status,
                current_topic, current_tools, last_seen_at
            ) VALUES (
                %s::uuid, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, NOW()
            )
            ON CONFLICT (session_id) DO UPDATE SET
                agent_id = EXCLUDED.agent_id,
                machine_id = EXCLUDED.machine_id,
                role = EXCLUDED.role,
                ring = EXCLUDED.ring,
                task_id = EXCLUDED.task_id,
                status = EXCLUDED.status,
                current_topic = EXCLUDED.current_topic,
                current_tools = EXCLUDED.current_tools,
                last_seen_at = NOW(),
                closed_at = NULL
            RETURNING *
            """,
            (
                sid,
                agent_id,
                machine_id,
                role,
                ring_n,
                task_id,
                status,
                current_topic,
                json.dumps(current_tools or []),
            ),
        )
        return row or {"session_id": sid, "agent_id": agent_id, "ring": ring_n}

    def heartbeat(self, session_id: str, *, current_topic: str | None = None) -> None:
        if current_topic is not None:
            db.execute(
                """
                UPDATE maat_session_presence
                SET last_seen_at = NOW(), current_topic = %s, status = 'active'
                WHERE session_id = %s::uuid
                """,
                (current_topic, session_id),
            )
        else:
            db.execute(
                """
                UPDATE maat_session_presence
                SET last_seen_at = NOW(), status = 'active'
                WHERE session_id = %s::uuid
                """,
                (session_id,),
            )

    def complete(self, session_id: str, status: str = "complete") -> None:
        if status not in ("complete", "failed", "idle"):
            status = "complete"
        db.execute(
            """
            UPDATE maat_session_presence
            SET status = %s, closed_at = NOW(), last_seen_at = NOW()
            WHERE session_id = %s::uuid
            """,
            (status, session_id),
        )

    def list_active(self, *, stale_minutes: int = 30, limit: int = 50) -> list[dict[str, Any]]:
        return db.fetchall(
            """
            SELECT session_id, agent_id, machine_id, role, task_id, status,
                   current_topic, last_seen_at, started_at
            FROM maat_session_presence
            WHERE status = 'active'
              AND last_seen_at > NOW() - (%s || ' minutes')::interval
            ORDER BY last_seen_at DESC
            LIMIT %s
            """,
            (str(stale_minutes), limit),
        )
