"""Enrollment birth certificates + chronology + full identity cards.

Law: every enrollment has a birth and an append-only chronology.
Agents never become principals — principal_id is the human user/sovereign.
"""

from __future__ import annotations

import json
import os
from typing import Any, Optional

from ..machine_info import get_machine_info, get_unique_agent_id
from . import db
from .handoff import normalize_ring
from .registry import FleetRegistry
from .tepi import TepiIdentity


def build_full_identity(
    *,
    agent_id: str,
    machine_id: str,
    principal_id: str,
    working_on: str,
    tool_type: str = "cursor",
    ring: str = "outer",
    role: str = "general",
    invite_id: str | None = None,
    episode_id: str | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Concrete identity card — who, for whom, where, what work."""
    info = get_machine_info()
    principal = TepiIdentity().ensure_principal(principal_id)
    os_user = info.get("user") or os.getenv("USER") or os.getenv("USERNAME") or "unknown"
    card = {
        "schema": "maat.enrollment.identity.v0",
        "agent_id": agent_id,
        "display_name": f"{tool_type}:{agent_id}",
        "tool_type": tool_type,
        "role": role,
        "ring": normalize_ring(ring),
        "principal": {
            "principal_id": principal_id,
            "display_name": principal.get("display_name") or principal_id,
            "meaning": "human user / sovereign — agent acts under this user",
        },
        "os_user": os_user,
        "machine": {
            "machine_id": machine_id,
            "hostname": info.get("hostname"),
            "platform": info.get("platform"),
        },
        "workspace": {
            "workspace_root": info.get("workspace_root"),
            "workspace_slug": info.get("workspace_slug"),
            "working_directory": info.get("working_directory"),
            "project_path": info.get("project_path"),
        },
        "working_on": working_on,
        "invite_id": invite_id,
        "episode_id": episode_id,
        "env_hints": {
            "MAAT_AGENT_ID": (info.get("env") or {}).get("MAAT_AGENT_ID") or "",
            "MAAT_PRINCIPAL_ID": os.environ.get("MAAT_PRINCIPAL_ID", ""),
        },
    }
    if extra:
        card["extra"] = extra
    return card


class EnrollmentBirth:
    """Birth + chronology for fleet enrollments."""

    def birth(
        self,
        *,
        working_on: str,
        principal_id: str = "imhotep",
        tool_type: str = "cursor",
        agent_id: str | None = None,
        machine_id: str | None = None,
        ring: str = "outer",
        role: str = "general",
        invite_id: str | None = None,
        episode_id: str | None = None,
        metadata: dict[str, Any] | None = None,
        enroll: bool = True,
    ) -> dict[str, Any]:
        work = (working_on or "").strip()
        if not work:
            return {
                "ok": False,
                "error": "working_on_required",
                "hint": "Say specifically what this agent is testing/building (not 'general').",
            }
        pid = (principal_id or "").strip()
        if not pid:
            return {"ok": False, "error": "principal_id_required", "hint": "Who is the human user?"}

        TepiIdentity().ensure_principal(pid)
        reg = FleetRegistry()
        info = get_machine_info()
        mid = machine_id or info["machine_id"]
        aid = agent_id or get_unique_agent_id(tool_type)
        ring_n = normalize_ring(ring)
        os_user = info.get("user") or os.getenv("USER") or "unknown"

        if enroll:
            reg.enroll_machine(machine_id=mid, hostname=info.get("hostname"))
            reg.enroll_agent(
                agent_id=aid,
                tool_type=tool_type,
                machine_id=mid,
                ring=ring_n,
                role=role,
                principal_id=pid,
                metadata={
                    "working_on": work,
                    "os_user": os_user,
                    "invite_id": invite_id,
                    **(metadata or {}),
                },
            )

        identity = build_full_identity(
            agent_id=aid,
            machine_id=mid,
            principal_id=pid,
            working_on=work,
            tool_type=tool_type,
            ring=ring_n,
            role=role,
            invite_id=invite_id,
            episode_id=episode_id,
            extra=metadata,
        )

        # Supersede prior alive birth for this agent (re-enroll = new birth)
        db.execute(
            """
            UPDATE maat_enrollment_births
            SET status = 'superseded', updated_at = NOW()
            WHERE agent_id = %s AND status = 'alive'
            """,
            (aid,),
        )

        row = db.execute_returning(
            """
            INSERT INTO maat_enrollment_births (
                agent_id, machine_id, principal_id, os_user, tool_type, ring, role,
                working_on, full_identity, invite_id, episode_id, status, metadata
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s::uuid, %s, 'alive', %s::jsonb
            )
            RETURNING *
            """,
            (
                aid,
                mid,
                pid,
                os_user,
                tool_type,
                ring_n,
                role,
                work,
                json.dumps(identity),
                invite_id,
                episode_id,
                json.dumps(metadata or {}),
            ),
        )
        if not row:
            return {"ok": False, "error": "birth_insert_failed"}

        birth_id = str(row["birth_id"])
        # Mirror onto agent row
        try:
            db.execute(
                """
                UPDATE maat_agents SET
                    principal_id = %s,
                    ring = %s,
                    role = %s,
                    working_on = %s,
                    os_user = %s,
                    display_name = %s,
                    birth_id = %s::uuid,
                    metadata = COALESCE(metadata, '{}'::jsonb) || %s::jsonb,
                    updated_at = NOW()
                WHERE agent_id = %s
                """,
                (
                    pid,
                    ring_n,
                    role,
                    work,
                    os_user,
                    identity["display_name"],
                    birth_id,
                    json.dumps(
                        {
                            "working_on": work,
                            "os_user": os_user,
                            "birth_id": birth_id,
                            "principal_id": pid,
                        }
                    ),
                    aid,
                ),
            )
        except Exception:
            # Columns may be missing until migrate — metadata still carries identity
            db.execute(
                """
                UPDATE maat_agents SET
                    principal_id = %s,
                    ring = %s,
                    role = %s,
                    metadata = COALESCE(metadata, '{}'::jsonb) || %s::jsonb,
                    updated_at = NOW()
                WHERE agent_id = %s
                """,
                (
                    pid,
                    ring_n,
                    role,
                    json.dumps(
                        {
                            "working_on": work,
                            "os_user": os_user,
                            "birth_id": birth_id,
                            "principal_id": pid,
                        }
                    ),
                    aid,
                ),
            )

        chron = self.append_event(
            birth_id=birth_id,
            agent_id=aid,
            machine_id=mid,
            principal_id=pid,
            event_type="birth",
            summary=f"Enrollment birth under principal {pid}: {work}",
            working_on=work,
            payload={"full_identity": identity, "invite_id": invite_id},
        )

        TepiIdentity().log(
            principal_id=pid,
            agent_id=aid,
            machine_id=mid,
            ring=ring_n,
            episode_id=episode_id or birth_id,
            event_type="enrollment_birth",
            summary=f"birth {aid} working_on={work}",
            payload={"birth_id": birth_id, "identity": identity},
        )

        return {
            "ok": True,
            "birth_id": birth_id,
            "born_at": row.get("born_at"),
            "agent_id": aid,
            "machine_id": mid,
            "principal_id": pid,
            "os_user": os_user,
            "working_on": work,
            "role": role,
            "ring": ring_n,
            "full_identity": identity,
            "chronology_event_id": chron.get("event_id"),
        }

    def append_event(
        self,
        *,
        birth_id: str,
        agent_id: str,
        event_type: str,
        summary: str = "",
        working_on: str | None = None,
        machine_id: str | None = None,
        principal_id: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        row = db.execute_returning(
            """
            INSERT INTO maat_enrollment_chronology (
                birth_id, agent_id, machine_id, principal_id,
                event_type, summary, working_on, payload
            ) VALUES (
                %s::uuid, %s, %s, %s, %s, %s, %s, %s::jsonb
            )
            RETURNING event_id::text AS event_id, occurred_at, event_type
            """,
            (
                birth_id,
                agent_id,
                machine_id,
                principal_id,
                event_type,
                summary,
                working_on,
                json.dumps(payload or {}),
            ),
        )
        if working_on:
            try:
                db.execute(
                    """
                    UPDATE maat_enrollment_births
                    SET working_on = %s,
                        full_identity = full_identity || jsonb_build_object('working_on', %s::text),
                        updated_at = NOW()
                    WHERE birth_id = %s::uuid
                    """,
                    (working_on, working_on, birth_id),
                )
                db.execute(
                    "UPDATE maat_agents SET working_on = %s, updated_at = NOW() WHERE agent_id = %s",
                    (working_on, agent_id),
                )
            except Exception:
                db.execute(
                    """
                    UPDATE maat_agents SET
                        metadata = COALESCE(metadata, '{}'::jsonb) || %s::jsonb,
                        updated_at = NOW()
                    WHERE agent_id = %s
                    """,
                    (json.dumps({"working_on": working_on}), agent_id),
                )
        return dict(row) if row else {"ok": False}

    def update_work(
        self,
        agent_id: str,
        working_on: str,
        *,
        summary: str | None = None,
    ) -> dict[str, Any]:
        work = (working_on or "").strip()
        if not work:
            return {"ok": False, "error": "working_on_required"}
        birth = self.get_alive_birth(agent_id)
        if not birth:
            return {"ok": False, "error": "no_alive_birth", "hint": "Run join/enroll-birth first"}
        ev = self.append_event(
            birth_id=str(birth["birth_id"]),
            agent_id=agent_id,
            machine_id=birth.get("machine_id"),
            principal_id=birth.get("principal_id"),
            event_type="work_update",
            summary=summary or f"Now working on: {work}",
            working_on=work,
            payload={"previous": birth.get("working_on"), "next": work},
        )
        return {
            "ok": True,
            "agent_id": agent_id,
            "birth_id": str(birth["birth_id"]),
            "working_on": work,
            "event": ev,
        }

    def get_alive_birth(self, agent_id: str) -> Optional[dict[str, Any]]:
        row = db.fetchone(
            """
            SELECT * FROM maat_enrollment_births
            WHERE agent_id = %s AND status = 'alive'
            ORDER BY born_at DESC LIMIT 1
            """,
            (agent_id,),
        )
        return dict(row) if row else None

    def chronology(
        self,
        agent_id: str | None = None,
        *,
        birth_id: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        if birth_id:
            rows = db.fetchall(
                """
                SELECT * FROM maat_enrollment_chronology
                WHERE birth_id = %s::uuid
                ORDER BY occurred_at ASC
                LIMIT %s
                """,
                (birth_id, limit),
            )
        elif agent_id:
            rows = db.fetchall(
                """
                SELECT * FROM maat_enrollment_chronology
                WHERE agent_id = %s
                ORDER BY occurred_at ASC
                LIMIT %s
                """,
                (agent_id, limit),
            )
        else:
            rows = db.fetchall(
                """
                SELECT * FROM maat_enrollment_chronology
                ORDER BY occurred_at DESC
                LIMIT %s
                """,
                (limit,),
            )
        return [dict(r) for r in rows or []]

    def identity_card(self, agent_id: str | None = None, tool_type: str = "cursor") -> dict[str, Any]:
        aid = agent_id or get_unique_agent_id(tool_type)
        birth = self.get_alive_birth(aid)
        agent = FleetRegistry().get_agent(aid) or {}
        chron = self.chronology(aid, limit=20) if birth else []
        if birth:
            return {
                "ok": True,
                "agent_id": aid,
                "birth_id": str(birth["birth_id"]),
                "born_at": birth.get("born_at"),
                "principal_id": birth.get("principal_id"),
                "os_user": birth.get("os_user"),
                "working_on": birth.get("working_on"),
                "role": birth.get("role"),
                "ring": birth.get("ring"),
                "machine_id": birth.get("machine_id"),
                "full_identity": birth.get("full_identity"),
                "agent_row": {
                    "status": agent.get("status"),
                    "principal_id": agent.get("principal_id"),
                    "working_on": agent.get("working_on")
                    or (agent.get("metadata") or {}).get("working_on"),
                },
                "chronology": chron,
                "chronology_n": len(chron),
            }
        return {
            "ok": False,
            "error": "no_alive_birth",
            "agent_id": aid,
            "agent_row": agent or None,
            "hint": "Run: maat_memory_plane.py join --token … --working-on '…' "
            "or enroll-birth --working-on '…' --principal imhotep",
        }

    def list_alive(self, limit: int = 50) -> list[dict[str, Any]]:
        rows = db.fetchall(
            """
            SELECT birth_id, agent_id, machine_id, principal_id, os_user,
                   role, ring, working_on, born_at, invite_id
            FROM maat_enrollment_births
            WHERE status = 'alive'
            ORDER BY born_at DESC
            LIMIT %s
            """,
            (limit,),
        )
        return [dict(r) for r in rows or []]
