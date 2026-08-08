"""Fleet registry — machines and agents enroll / heartbeat / revoke."""

from __future__ import annotations

import json
from typing import Any

from ..machine_info import get_machine_info, get_unique_agent_id
from . import db


class FleetRegistry:
    def enroll_machine(
        self,
        *,
        machine_id: str | None = None,
        hostname: str | None = None,
        storage_roots: dict[str, str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        info = get_machine_info()
        mid = machine_id or info["machine_id"]
        host = hostname or info["hostname"]
        roots = storage_roots or {
            "workspace": str(info.get("project_path") or info.get("working_directory") or ""),
            "cwd": info.get("working_directory") or "",
        }
        db.execute(
            """
            INSERT INTO maat_machines (machine_id, hostname, storage_roots, status, metadata, last_seen_at)
            VALUES (%s, %s, %s::jsonb, 'enrolled', %s::jsonb, NOW())
            ON CONFLICT (machine_id) DO UPDATE SET
                hostname = EXCLUDED.hostname,
                storage_roots = EXCLUDED.storage_roots,
                status = 'enrolled',
                metadata = maat_machines.metadata || EXCLUDED.metadata,
                last_seen_at = NOW(),
                updated_at = NOW()
            """,
            (mid, host, json.dumps(roots), json.dumps(metadata or {})),
        )
        return self.get_machine(mid) or {"machine_id": mid, "status": "enrolled"}

    def enroll_agent(
        self,
        *,
        agent_id: str | None = None,
        tool_type: str = "cursor",
        machine_id: str | None = None,
        ring: str = "outer",
        role: str = "general",
        principal_id: str | None = None,
        capabilities: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        info = get_machine_info()
        mid = machine_id or info["machine_id"]
        # Ensure machine exists
        self.enroll_machine(machine_id=mid, hostname=info["hostname"])
        aid = agent_id or get_unique_agent_id(tool_type)
        if ring not in ("inner", "middle", "outer"):
            ring = "outer"
        meta = {
            "workspace_root": info.get("workspace_root"),
            "workspace_slug": info.get("workspace_slug"),
            "working_directory": info.get("working_directory"),
            **(metadata or {}),
        }
        if principal_id:
            meta["principal_id"] = principal_id
        # principal_id column may exist after TEPI migrate
        try:
            db.execute(
                """
                INSERT INTO maat_agents (
                    agent_id, machine_id, tool_type, ring, role, capabilities, status,
                    metadata, principal_id, last_seen_at
                ) VALUES (%s, %s, %s, %s, %s, %s::jsonb, 'enrolled', %s::jsonb, %s, NOW())
                ON CONFLICT (agent_id) DO UPDATE SET
                    machine_id = EXCLUDED.machine_id,
                    tool_type = EXCLUDED.tool_type,
                    ring = EXCLUDED.ring,
                    role = EXCLUDED.role,
                    capabilities = EXCLUDED.capabilities,
                    status = 'enrolled',
                    metadata = maat_agents.metadata || EXCLUDED.metadata,
                    principal_id = COALESCE(EXCLUDED.principal_id, maat_agents.principal_id),
                    last_seen_at = NOW(),
                    updated_at = NOW()
                """,
                (
                    aid,
                    mid,
                    tool_type,
                    ring,
                    role,
                    json.dumps(capabilities or []),
                    json.dumps(meta),
                    principal_id,
                ),
            )
        except Exception:
            db.execute(
                """
                INSERT INTO maat_agents (
                    agent_id, machine_id, tool_type, ring, role, capabilities, status, metadata, last_seen_at
                ) VALUES (%s, %s, %s, %s, %s, %s::jsonb, 'enrolled', %s::jsonb, NOW())
                ON CONFLICT (agent_id) DO UPDATE SET
                    machine_id = EXCLUDED.machine_id,
                    tool_type = EXCLUDED.tool_type,
                    ring = EXCLUDED.ring,
                    role = EXCLUDED.role,
                    capabilities = EXCLUDED.capabilities,
                    status = 'enrolled',
                    metadata = maat_agents.metadata || EXCLUDED.metadata,
                    last_seen_at = NOW(),
                    updated_at = NOW()
                """,
                (
                    aid,
                    mid,
                    tool_type,
                    ring,
                    role,
                    json.dumps(capabilities or []),
                    json.dumps(meta),
                ),
            )
        return self.get_agent(aid) or {"agent_id": aid, "status": "enrolled"}

    def heartbeat(self, agent_id: str, machine_id: str | None = None) -> None:
        db.execute(
            "UPDATE maat_agents SET last_seen_at = NOW(), updated_at = NOW() WHERE agent_id = %s",
            (agent_id,),
        )
        if machine_id:
            db.execute(
                "UPDATE maat_machines SET last_seen_at = NOW(), updated_at = NOW() WHERE machine_id = %s",
                (machine_id,),
            )

    def revoke_agent(self, agent_id: str) -> None:
        db.execute(
            "UPDATE maat_agents SET status = 'revoked', updated_at = NOW() WHERE agent_id = %s",
            (agent_id,),
        )

    def revoke_machine(self, machine_id: str) -> None:
        db.execute(
            "UPDATE maat_machines SET status = 'revoked', updated_at = NOW() WHERE machine_id = %s",
            (machine_id,),
        )

    def get_machine(self, machine_id: str) -> dict[str, Any] | None:
        rows = db.fetchall(
            "SELECT * FROM maat_machines WHERE machine_id = %s", (machine_id,)
        )
        return rows[0] if rows else None

    def get_agent(self, agent_id: str) -> dict[str, Any] | None:
        rows = db.fetchall("SELECT * FROM maat_agents WHERE agent_id = %s", (agent_id,))
        return rows[0] if rows else None

    def list_agents(self, status: str = "enrolled") -> list[dict[str, Any]]:
        return db.fetchall(
            "SELECT * FROM maat_agents WHERE status = %s ORDER BY last_seen_at DESC",
            (status,),
        )

    def list_machines(self, status: str = "enrolled") -> list[dict[str, Any]]:
        return db.fetchall(
            "SELECT * FROM maat_machines WHERE status = %s ORDER BY last_seen_at DESC",
            (status,),
        )

    def assert_can_write_durable(self, agent_id: str) -> tuple[bool, str]:
        if db.permissive():
            return True, "permissive bootstrap"
        agent = self.get_agent(agent_id)
        if not agent or agent.get("status") != "enrolled":
            return False, f"agent not enrolled: {agent_id}"
        mid = agent.get("machine_id")
        if mid:
            machine = self.get_machine(str(mid))
            if not machine or machine.get("status") != "enrolled":
                return False, f"machine not enrolled: {mid}"
        # Storage consciousness — capacity must be attested (absence ≠ compliance)
        try:
            from .storage import StorageAwareness

            cap = StorageAwareness(self).check_capacity(str(mid) if mid else None)
            if not cap.get("ok"):
                return False, f"storage_capacity:{cap.get('reason') or 'denied'}"
        except Exception as e:  # noqa: BLE001
            return False, f"storage_capacity:unmeasured:{type(e).__name__}"
        return True, "enrolled+capacity"

    def ensure_local(self, tool_type: str = "cursor") -> dict[str, Any]:
        """Enroll this host + agent; return ids."""
        info = get_machine_info()
        machine = self.enroll_machine()
        agent = self.enroll_agent(tool_type=tool_type)
        return {
            "machine_id": machine.get("machine_id") or info["machine_id"],
            "agent_id": agent.get("agent_id"),
            "hostname": info["hostname"],
        }
