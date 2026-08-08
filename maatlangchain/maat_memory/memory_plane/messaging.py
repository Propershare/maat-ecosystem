"""Agent Messaging — cross-agent communication via Postgres NOTIFY/LISTEN.

Part of the Memory Plane. Agents send messages to each other through
the shared Postgres organ. NOTIFY triggers push delivery in real time.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from .db import fetchall, fetchone, execute, execute_returning


class AgentMessaging:
    """Send, receive, and query agent-to-agent messages."""

    def send(
        self,
        *,
        from_agent: str,
        to_agent: str | None = None,
        message_type: str = "notify",
        subject: str = "",
        body: str = "",
        priority: str = "normal",
        correlation_id: str | None = None,
        in_reply_to: str | None = None,
        ttl_seconds: int = 86400,
        machine_id: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Send a message. to_agent=None means broadcast."""
        msg_id = str(uuid.uuid4())
        corr_id = correlation_id or str(uuid.uuid4())
        expires_at = datetime.now(timezone.utc).timestamp() + ttl_seconds
        actual_type = "broadcast" if to_agent is None else message_type

        payload = {
            "body": body,
            "sender_machine": machine_id,
        }
        if metadata:
            payload.update(metadata)

        row = execute_returning(
            """INSERT INTO maat_agent_messages
               (id, from_agent, to_agent, message_type, subject, payload,
                correlation_id, in_reply_to, priority, ttl_seconds, expires_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, to_timestamp(%s))
               RETURNING id, from_agent, to_agent, message_type, subject,
                         priority, status, correlation_id, in_reply_to, created_at""",
            (
                msg_id,
                from_agent,
                to_agent,
                actual_type,
                subject,
                json.dumps(payload),
                corr_id,
                in_reply_to,
                priority,
                ttl_seconds,
                expires_at,
            ),
        )

        if row:
            row["created_at"] = row["created_at"].isoformat() if row.get("created_at") else None
            return {"ok": True, "message": row}
        return {"ok": False, "error": "insert returned no row"}

    def inbox(
        self,
        agent_id: str,
        status: str = "pending",
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Get pending messages for an agent (including broadcasts)."""
        rows = fetchall(
            """SELECT id, from_agent, to_agent, message_type, subject, payload,
                      priority, status, correlation_id, in_reply_to,
                      created_at, expires_at
               FROM maat_agent_messages
               WHERE (to_agent = %s OR (to_agent IS NULL AND message_type = 'broadcast'))
                 AND status = %s
                 AND (expires_at IS NULL OR expires_at > NOW())
               ORDER BY
                 CASE priority
                   WHEN 'urgent' THEN 0
                   WHEN 'high' THEN 1
                   WHEN 'normal' THEN 2
                   WHEN 'low' THEN 3
                 END,
                 created_at DESC
               LIMIT %s""",
            (agent_id, status, limit),
        )

        for r in rows:
            r["created_at"] = r["created_at"].isoformat() if r.get("created_at") else None
            r["expires_at"] = r["expires_at"].isoformat() if r.get("expires_at") else None
            if isinstance(r.get("payload"), str):
                try:
                    r["payload"] = json.loads(r["payload"])
                except (json.JSONDecodeError, TypeError):
                    pass

        return rows

    def mark_read(self, message_id: str) -> dict[str, Any]:
        """Mark a message as read."""
        row = execute_returning(
            """UPDATE maat_agent_messages
               SET status = 'read', read_at = NOW()
               WHERE id = %s
               RETURNING id, status, read_at""",
            (message_id,),
        )
        if row:
            row["read_at"] = row["read_at"].isoformat() if row.get("read_at") else None
            return {"ok": True, "message": row}
        return {"ok": False, "error": f"message {message_id} not found"}

    def reply(
        self,
        *,
        to_message_id: str,
        from_agent: str,
        body: str,
        machine_id: str = "",
    ) -> dict[str, Any]:
        """Reply to a message, auto-threading via correlation_id."""
        original = fetchone(
            "SELECT id, from_agent, correlation_id, subject FROM maat_agent_messages WHERE id = %s",
            (to_message_id,),
        )
        if not original:
            return {"ok": False, "error": f"message {to_message_id} not found"}

        reply_to = original["from_agent"]
        corr_id = original["correlation_id"]
        subject = f"Re: {original.get('subject', '')}" if original.get("subject") else "Reply"

        result = self.send(
            from_agent=from_agent,
            to_agent=reply_to,
            message_type="reply",
            subject=subject,
            body=body,
            correlation_id=corr_id,
            in_reply_to=to_message_id,
            machine_id=machine_id,
        )

        if result.get("ok"):
            execute(
                "UPDATE maat_agent_messages SET status = 'replied', replied_at = NOW() WHERE id = %s",
                (to_message_id,),
            )

        return result

    def conversation(self, correlation_id: str) -> list[dict[str, Any]]:
        """Get full thread by correlation_id."""
        rows = fetchall(
            """SELECT id, from_agent, to_agent, message_type, subject, payload,
                      priority, status, correlation_id, in_reply_to,
                      created_at, read_at, replied_at
               FROM maat_agent_messages
               WHERE correlation_id = %s
               ORDER BY created_at ASC""",
            (correlation_id,),
        )

        for r in rows:
            r["created_at"] = r["created_at"].isoformat() if r.get("created_at") else None
            r["read_at"] = r["read_at"].isoformat() if r.get("read_at") else None
            r["replied_at"] = r["replied_at"].isoformat() if r.get("replied_at") else None
            if isinstance(r.get("payload"), str):
                try:
                    r["payload"] = json.loads(r["payload"])
                except (json.JSONDecodeError, TypeError):
                    pass

        return rows

    def status(self, message_id: str) -> dict[str, Any] | None:
        """Get delivery status of a message."""
        row = fetchone(
            """SELECT m.id, m.from_agent, m.to_agent, m.message_type, m.subject,
                      m.status, m.priority, m.correlation_id, m.in_reply_to,
                      m.created_at, m.delivered_at, m.read_at, m.replied_at,
                      m.expires_at,
                      COALESCE(
                        (SELECT json_agg(json_build_object(
                          'agent', d.agent_id, 'event', d.event, 'at', d.occurred_at
                        )) FROM maat_agent_message_delivery d WHERE d.message_id = m.id),
                        '[]'::json
                      ) AS delivery_log
               FROM maat_agent_messages m
               WHERE m.id = %s""",
            (message_id,),
        )

        if row:
            for ts_field in ("created_at", "delivered_at", "read_at", "replied_at", "expires_at"):
                row[ts_field] = row[ts_field].isoformat() if row.get(ts_field) else None

        return row

    def cleanup_expired(self) -> None:
        """Mark expired messages as expired."""
        execute("SELECT maat_agent_message_expire()")
