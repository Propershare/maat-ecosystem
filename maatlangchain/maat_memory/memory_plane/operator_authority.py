"""Head Operator authority — token required for join-decide (closes self-approve Isfet).

Token plaintext is shown once on mint. Only the hash is stored.
Agents must not hold MAAT_OPERATOR_TOKEN (broker-class).
"""

from __future__ import annotations

import hashlib
import json
import os
import secrets
from typing import Any

from . import db
from .tepi import TepiIdentity


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class OperatorAuthority:
    def mint(
        self,
        principal_id: str = "imhotep",
        *,
        display_name: str | None = None,
        rotate: bool = True,
    ) -> dict[str, Any]:
        pid = (principal_id or "").strip()
        if not pid:
            return {"ok": False, "error": "principal_id_required"}
        TepiIdentity().ensure_principal(pid, display_name=display_name or pid)
        token = secrets.token_urlsafe(32)
        th = _hash(token)
        if rotate:
            db.execute(
                """
                INSERT INTO maat_operator_authority (
                    principal_id, token_hash, display_name, status, rotated_at
                ) VALUES (%s, %s, %s, 'active', NOW())
                ON CONFLICT (principal_id) DO UPDATE SET
                    token_hash = EXCLUDED.token_hash,
                    display_name = COALESCE(EXCLUDED.display_name, maat_operator_authority.display_name),
                    status = 'active',
                    rotated_at = NOW()
                """,
                (pid, th, display_name or pid),
            )
        else:
            existing = db.fetchone(
                "SELECT principal_id FROM maat_operator_authority WHERE principal_id=%s AND status='active'",
                (pid,),
            )
            if existing:
                return {
                    "ok": False,
                    "error": "already_minted",
                    "hint": "Pass rotate=True / --rotate to replace token",
                }
            db.execute(
                """
                INSERT INTO maat_operator_authority (principal_id, token_hash, display_name)
                VALUES (%s, %s, %s)
                """,
                (pid, th, display_name or pid),
            )
        return {
            "ok": True,
            "principal_id": pid,
            "operator_token": token,
            "hint": (
                "Store in operator-only channel or .env.broker as MAAT_OPERATOR_TOKEN. "
                "Do not put in .env.agent. Show once — hash only in DB."
            ),
            "broker_line": f"MAAT_OPERATOR_TOKEN={token}",
        }

    def verify(
        self,
        token: str | None,
        *,
        principal_id: str = "imhotep",
    ) -> dict[str, Any]:
        presented = (token or os.environ.get("MAAT_OPERATOR_TOKEN") or "").strip()
        if not presented:
            return {
                "ok": False,
                "error": "operator_token_required",
                "hint": (
                    "Head Operator must pass --operator-token or set MAAT_OPERATOR_TOKEN "
                    "(broker-only). Agents cannot decide joins."
                ),
            }
        row = db.fetchone(
            """
            SELECT principal_id, token_hash, status
            FROM maat_operator_authority
            WHERE principal_id = %s
            """,
            (principal_id,),
        )
        if not row:
            return {
                "ok": False,
                "error": "operator_authority_not_minted",
                "hint": "Run: maat_memory_plane.py operator-token-mint --principal imhotep",
            }
        if row.get("status") != "active":
            return {"ok": False, "error": "operator_authority_revoked"}
        if _hash(presented) != row["token_hash"]:
            return {"ok": False, "error": "operator_token_invalid"}
        return {
            "ok": True,
            "principal_id": principal_id,
            "operator_authenticated": True,
        }

    def revoke(self, principal_id: str = "imhotep") -> dict[str, Any]:
        db.execute(
            """
            UPDATE maat_operator_authority
            SET status = 'revoked', rotated_at = NOW()
            WHERE principal_id = %s
            """,
            (principal_id,),
        )
        return {"ok": True, "principal_id": principal_id, "status": "revoked"}
