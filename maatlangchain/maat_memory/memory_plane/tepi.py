"""TEPI — Temporal · Episodic · Principal · Identity-path."""

from __future__ import annotations

import json
from typing import Any, Optional

from . import db
from .handoff import RING_RANK, normalize_ring, ring_allows


class TepiIdentity:
    def ensure_principal(
        self,
        principal_id: str,
        *,
        display_name: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        pid = (principal_id or "").strip()
        if not pid:
            raise ValueError("principal_id required")
        db.execute(
            """
            INSERT INTO maat_principals (principal_id, display_name, metadata)
            VALUES (%s, %s, %s::jsonb)
            ON CONFLICT (principal_id) DO UPDATE SET
                display_name = COALESCE(EXCLUDED.display_name, maat_principals.display_name),
                metadata = maat_principals.metadata || EXCLUDED.metadata,
                updated_at = NOW()
            """,
            (pid, display_name or pid, json.dumps(metadata or {})),
        )
        row = db.fetchone(
            "SELECT * FROM maat_principals WHERE principal_id = %s", (pid,)
        )
        return dict(row) if row else {"principal_id": pid}

    def bind(
        self,
        *,
        principal_id: str,
        agent_id: str,
        ring: str = "outer",
        episode_id: str | None = None,
        machine_id: str | None = None,
        summary: str = "bind",
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        self.ensure_principal(principal_id)
        ring_n = normalize_ring(ring)
        # Attach principal on agent roster when present
        db.execute(
            """
            UPDATE maat_agents SET
                principal_id = %s,
                ring = COALESCE(%s, ring),
                updated_at = NOW()
            WHERE agent_id = %s
            """,
            (principal_id, ring_n, agent_id),
        )
        return self.log(
            principal_id=principal_id,
            agent_id=agent_id,
            machine_id=machine_id,
            ring=ring_n,
            episode_id=episode_id,
            event_type="bind",
            summary=summary,
            payload=payload or {},
        )

    def log(
        self,
        *,
        principal_id: str,
        agent_id: str,
        ring: str,
        event_type: str,
        summary: str = "",
        machine_id: str | None = None,
        episode_id: str | None = None,
        memory_refs: list[Any] | None = None,
        payload: dict[str, Any] | None = None,
        valid_until=None,
    ) -> dict[str, Any]:
        self.ensure_principal(principal_id)
        ring_n = normalize_ring(ring)
        row = db.execute_returning(
            """
            INSERT INTO maat_tepi_log (
                principal_id, agent_id, machine_id, ring, episode_id,
                event_type, summary, memory_refs, payload, valid_until
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s::jsonb, %s
            )
            RETURNING *
            """,
            (
                principal_id,
                agent_id,
                machine_id,
                ring_n,
                episode_id,
                event_type,
                summary,
                json.dumps(memory_refs or []),
                json.dumps(payload or {}),
                valid_until,
            ),
        )
        return dict(row) if row else {"ok": True, "event_type": event_type}

    def recall(
        self,
        *,
        principal_id: str,
        viewer_ring: str,
        limit: int = 20,
        include_artifacts: bool = True,
        include_learnings: bool = True,
    ) -> dict[str, Any]:
        """Ring-filtered recall for a principal. Outer cannot see inner."""
        vring = normalize_ring(viewer_ring)
        rank = RING_RANK[vring]
        out: dict[str, Any] = {
            "principal_id": principal_id,
            "viewer_ring": vring,
            "artifacts": [],
            "learnings": [],
            "tepi": [],
        }

        tepi_rows = db.fetchall(
            """
            SELECT id, event_type, summary, ring, episode_id, seen_at, memory_refs
            FROM maat_tepi_log
            WHERE principal_id = %s
              AND CASE ring
                    WHEN 'outer' THEN 0 WHEN 'middle' THEN 1 WHEN 'inner' THEN 2 ELSE 0
                  END <= %s
            ORDER BY seen_at DESC
            LIMIT %s
            """,
            (principal_id, rank, limit),
        )
        out["tepi"] = [dict(r) for r in tepi_rows or []]

        if include_artifacts:
            arts = db.fetchall(
                """
                SELECT id, title, ring, portable_uri, content_sha256,
                       metadata->>'slug' AS slug,
                       metadata->>'public_uri' AS public_uri
                FROM maat_artifacts
                WHERE status LIKE 'active%%'
                  AND (
                    metadata->>'principal_id' = %s
                    OR metadata->>'audience' = 'every_lab_agent'
                    OR ring = 'outer'
                  )
                  AND CASE COALESCE(ring, 'outer')
                        WHEN 'outer' THEN 0 WHEN 'middle' THEN 1 WHEN 'inner' THEN 2 ELSE 0
                      END <= %s
                ORDER BY produced_at DESC NULLS LAST, created_at DESC
                LIMIT %s
                """,
                (principal_id, rank, limit),
            )
            out["artifacts"] = [dict(r) for r in arts or []]

        if include_learnings:
            # Learnings have no ring column yet — treat as outer-visible for viewer ≥ outer.
            if rank >= 0:
                learns = db.fetchall(
                    """
                    SELECT id, topic, insight, confidence, applied, created_at, agent
                    FROM maat_learnings
                    ORDER BY created_at DESC NULLS LAST
                    LIMIT %s
                    """,
                    (limit,),
                )
                out["learnings"] = [dict(L) for L in learns or []]

        out["ok"] = True
        return out

    def agent_may_read_artifact(self, agent_ring: str, artifact_ring: str) -> bool:
        return ring_allows(agent_ring, artifact_ring)

    def get_agent_binding(self, agent_id: str) -> Optional[dict[str, Any]]:
        row = db.fetchone(
            """
            SELECT agent_id, principal_id, ring, machine_id, status, role
            FROM maat_agents WHERE agent_id = %s
            """,
            (agent_id,),
        )
        return dict(row) if row else None
