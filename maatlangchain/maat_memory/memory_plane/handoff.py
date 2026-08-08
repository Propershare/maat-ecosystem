"""Maat Handoff Protocol v0 — offer → receive → acknowledge → verify.

Law:
  - Chat claims are not membership.
  - Visibility uses ring column ranks (outer < middle < inner).
  - Verified means challenge evidence passed (usually fetch sha match).
"""

from __future__ import annotations

import hashlib
import json
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from uuid import uuid4

from . import db
from .artifact_bank import ArtifactBank

PROTOCOL = "maat.handoff.v0"
RING_RANK = {"outer": 0, "middle": 1, "inner": 2}
VALID_RINGS = set(RING_RANK)
OPEN_STATUSES = ("offered", "received", "acknowledged")


def normalize_ring(ring: str | None, default: str = "outer") -> str:
    r = (ring or default).strip().lower()
    return r if r in VALID_RINGS else default


def ring_allows(agent_ring: str, artifact_ring: str) -> bool:
    """Agent may see artifact if agent clearance >= artifact sensitivity."""
    return RING_RANK.get(normalize_ring(agent_ring), 0) >= RING_RANK.get(
        normalize_ring(artifact_ring), 0
    )


def audience_to_ring(audience: str | None, explicit: str | None = None) -> str:
    if explicit and explicit in VALID_RINGS:
        return explicit
    a = (audience or "").strip().lower()
    if a in ("inner", "principal_private", "canon", "lab_inner"):
        return "inner"
    if a in ("scholarship", "middle", "scholar", "fleet_ops"):
        return "middle"
    return "outer"


class HandoffProtocol:
    """Ledgered handoffs with ack/verify. Does not replace Guard — records the flow."""

    def offer(
        self,
        *,
        from_agent: str,
        summary: str,
        kind: str = "work",
        to_agent: str | None = None,
        principal_id: str | None = None,
        machine_id: str | None = None,
        ring: str = "outer",
        payload: dict[str, Any] | None = None,
        ttl_seconds: int = 3600,
        challenge: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if kind not in ("work", "signup", "artifact", "revoke"):
            return {"ok": False, "error": "invalid_kind", "kind": kind}
        ring_n = normalize_ring(ring)
        payload = dict(payload or {})
        chal = dict(challenge or {})
        # Default challenge: fetch portable sha if present
        sha = payload.get("sha256") or payload.get("content_sha256")
        if sha and not chal:
            chal = {"type": "fetch_sha", "expected_sha": sha}
        hid = str(uuid4())
        expires = datetime.now(timezone.utc) + timedelta(seconds=max(60, int(ttl_seconds)))
        db.execute(
            """
            INSERT INTO maat_handoffs (
                handoff_id, protocol, kind, status, from_agent, to_agent,
                principal_id, machine_id, ring, summary, payload, challenge,
                expires_at, metadata
            ) VALUES (
                %s::uuid, %s, %s, 'offered', %s, %s,
                %s, %s, %s, %s, %s::jsonb, %s::jsonb,
                %s, %s::jsonb
            )
            """,
            (
                hid,
                PROTOCOL,
                kind,
                from_agent,
                to_agent,
                principal_id,
                machine_id,
                ring_n,
                summary,
                json.dumps(payload),
                json.dumps(chal),
                expires,
                json.dumps(metadata or {}),
            ),
        )
        return {"ok": True, **(self.get(hid) or {"handoff_id": hid, "status": "offered"})}

    def receive(self, handoff_id: str, *, by_agent: str) -> dict[str, Any]:
        row = self.get(handoff_id)
        if not row:
            return {"ok": False, "error": "not_found"}
        gate = self._gate_open(row, by_agent)
        if not gate["ok"]:
            return gate
        if row["status"] not in ("offered", "received"):
            return {"ok": False, "error": "bad_status", "status": row["status"]}
        db.execute(
            """
            UPDATE maat_handoffs SET
                status = 'received',
                received_by = %s,
                received_at = COALESCE(received_at, NOW()),
                to_agent = COALESCE(to_agent, %s),
                updated_at = NOW()
            WHERE handoff_id = %s::uuid
            """,
            (by_agent, by_agent, handoff_id),
        )
        return {"ok": True, **(self.get(handoff_id) or {})}

    def acknowledge(
        self,
        handoff_id: str,
        *,
        by_agent: str,
        note: str = "",
    ) -> dict[str, Any]:
        row = self.get(handoff_id)
        if not row:
            return {"ok": False, "error": "not_found"}
        gate = self._gate_open(row, by_agent)
        if not gate["ok"]:
            return gate
        if row["status"] not in ("offered", "received", "acknowledged"):
            return {"ok": False, "error": "bad_status", "status": row["status"]}
        # Auto-receive if skipped
        if row["status"] == "offered":
            self.receive(handoff_id, by_agent=by_agent)
        evidence = dict(row.get("evidence") or {})
        evidence["ack_note"] = note
        db.execute(
            """
            UPDATE maat_handoffs SET
                status = 'acknowledged',
                acknowledged_by = %s,
                acknowledged_at = NOW(),
                evidence = %s::jsonb,
                updated_at = NOW()
            WHERE handoff_id = %s::uuid
            """,
            (by_agent, json.dumps(evidence), handoff_id),
        )
        return {"ok": True, **(self.get(handoff_id) or {})}

    def verify(
        self,
        handoff_id: str,
        *,
        by_agent: str,
        skip_challenge: bool = False,
    ) -> dict[str, Any]:
        row = self.get(handoff_id)
        if not row:
            return {"ok": False, "error": "not_found"}
        if row["status"] in ("rejected", "expired", "superseded"):
            return {"ok": False, "error": "closed", "status": row["status"]}
        if self._expired(row):
            self._mark_expired(handoff_id)
            return {"ok": False, "error": "expired"}
        # Must be acknowledged (or allow verify after receive for artifact-only)
        if row["status"] == "offered":
            return {"ok": False, "error": "not_received", "hint": "receive then acknowledge first"}
        if row["status"] == "received":
            return {"ok": False, "error": "not_acknowledged", "hint": "acknowledge before verify"}

        chal = dict(row.get("challenge") or {})
        evidence = dict(row.get("evidence") or {})
        if not skip_challenge and chal.get("type") == "fetch_sha":
            expected = (chal.get("expected_sha") or "").lower()
            uri = (
                (row.get("payload") or {}).get("portable_uri")
                or (row.get("payload") or {}).get("uri")
                or f"maat://object/{expected}"
            )
            fetched = ArtifactBank().fetch(uri)
            got = (fetched.get("sha256") or "").lower()
            evidence["verify"] = {
                "type": "fetch_sha",
                "expected": expected,
                "got": got,
                "fetch_ok": bool(fetched.get("ok")),
                "by": by_agent,
            }
            if not fetched.get("ok") or got != expected:
                db.execute(
                    """
                    UPDATE maat_handoffs SET evidence = %s::jsonb, updated_at = NOW()
                    WHERE handoff_id = %s::uuid
                    """,
                    (json.dumps(evidence), handoff_id),
                )
                return {
                    "ok": False,
                    "error": "challenge_failed",
                    "evidence": evidence["verify"],
                }
        elif not skip_challenge and chal:
            return {"ok": False, "error": "unsupported_challenge", "challenge": chal}

        db.execute(
            """
            UPDATE maat_handoffs SET
                status = 'verified',
                verified_by = %s,
                verified_at = NOW(),
                closed_at = NOW(),
                evidence = %s::jsonb,
                updated_at = NOW()
            WHERE handoff_id = %s::uuid
            """,
            (by_agent, json.dumps(evidence), handoff_id),
        )
        return {"ok": True, **(self.get(handoff_id) or {})}

    def reject(
        self,
        handoff_id: str,
        *,
        by_agent: str,
        reason: str = "",
    ) -> dict[str, Any]:
        row = self.get(handoff_id)
        if not row:
            return {"ok": False, "error": "not_found"}
        if row["status"] in ("verified", "rejected", "expired", "superseded"):
            return {"ok": False, "error": "closed", "status": row["status"]}
        db.execute(
            """
            UPDATE maat_handoffs SET
                status = 'rejected',
                reject_reason = %s,
                closed_at = NOW(),
                metadata = COALESCE(metadata, '{}'::jsonb) || %s::jsonb,
                updated_at = NOW()
            WHERE handoff_id = %s::uuid
            """,
            (
                reason,
                json.dumps({"rejected_by": by_agent}),
                handoff_id,
            ),
        )
        return {"ok": True, **(self.get(handoff_id) or {})}

    def get(self, handoff_id: str) -> Optional[dict[str, Any]]:
        row = db.fetchone(
            "SELECT * FROM maat_handoffs WHERE handoff_id = %s::uuid",
            (handoff_id,),
        )
        return dict(row) if row else None

    def list(
        self,
        *,
        agent_id: str | None = None,
        status: str | None = None,
        kind: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        conds = ["1=1"]
        params: list[Any] = []
        if agent_id:
            conds.append("(from_agent = %s OR to_agent = %s OR to_agent IS NULL)")
            params.extend([agent_id, agent_id])
        if status:
            conds.append("status = %s")
            params.append(status)
        if kind:
            conds.append("kind = %s")
            params.append(kind)
        params.append(limit)
        rows = db.fetchall(
            f"""
            SELECT * FROM maat_handoffs
            WHERE {' AND '.join(conds)}
            ORDER BY offered_at DESC
            LIMIT %s
            """,
            tuple(params),
        )
        return [dict(r) for r in rows or []]

    def issue_invite(
        self,
        *,
        principal_id: str,
        created_by: str,
        intended_ring: str = "outer",
        intended_tool: str | None = None,
        intended_machine: str | None = None,
        ttl_seconds: int = 600,
        plaintext_token: str | None = None,
    ) -> dict[str, Any]:
        """Mint one-time invite. Returns plaintext token once; store only hash."""
        ring_n = normalize_ring(intended_ring)
        if ring_n == "inner":
            # Isfet: never default-issue inner invites from automation without explicit
            pass
        token = plaintext_token or secrets.token_urlsafe(24)
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        expires = datetime.now(timezone.utc) + timedelta(seconds=max(60, int(ttl_seconds)))
        # Pair with signup handoff (open claim)
        offered = self.offer(
            from_agent=created_by,
            to_agent=None,
            kind="signup",
            principal_id=principal_id,
            ring=ring_n,
            summary=f"Signup invite for principal {principal_id} at ring {ring_n}",
            payload={"invite_token_hash": token_hash, "intended_tool": intended_tool},
            ttl_seconds=ttl_seconds,
            challenge={"type": "invite_consume", "token_hash": token_hash},
            metadata={"invite": True},
        )
        if not offered.get("ok"):
            return offered
        hid = offered.get("handoff_id")
        row = db.execute_returning(
            """
            INSERT INTO maat_invites (
                token_hash, principal_id, intended_ring, intended_tool,
                intended_machine, status, handoff_id, created_by, expires_at
            ) VALUES (%s, %s, %s, %s, %s, 'issued', %s::uuid, %s, %s)
            RETURNING invite_id::text AS invite_id, status, expires_at, intended_ring
            """,
            (
                token_hash,
                principal_id,
                ring_n,
                intended_tool,
                intended_machine,
                hid,
                created_by,
                expires,
            ),
        )
        if not row:
            return {"ok": False, "error": "invite_insert_failed", "handoff_id": hid}
        return {
            "ok": True,
            "invite_id": row["invite_id"],
            "token": token,
            "token_hash": token_hash,
            "handoff_id": hid,
            "intended_ring": ring_n,
            "expires_at": row["expires_at"],
            "hint": "Show token once to the new machine; never log plaintext into artifacts.",
        }

    def claim_invite(
        self,
        token: str,
        *,
        by_agent: str,
        machine_id: str | None = None,
        tool_type: str = "cursor",
        human_approval: bool = False,
        lab_interim: bool = False,
        auto_enroll: bool = True,
        working_on: str | None = None,
        role: str = "general",
    ) -> dict[str, Any]:
        """Claim invite → Guard should → enroll + birth → consume/verify."""
        from .enrollment import EnrollmentBirth
        from .guard_gate import should_enroll
        from .registry import FleetRegistry
        from .tepi import TepiIdentity

        work = (working_on or "").strip()
        if not work:
            return {
                "ok": False,
                "error": "working_on_required",
                "hint": "Pass --working-on with the specific chore/test this agent owns.",
            }

        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        inv = db.fetchone(
            "SELECT * FROM maat_invites WHERE token_hash = %s",
            (token_hash,),
        )
        if not inv:
            return {"ok": False, "error": "invite_not_found"}
        if inv["status"] != "issued":
            return {"ok": False, "error": "invite_not_open", "status": inv["status"]}
        if inv["expires_at"] and inv["expires_at"] < datetime.now(timezone.utc):
            db.execute(
                "UPDATE maat_invites SET status='expired', updated_at=NOW() WHERE invite_id=%s",
                (inv["invite_id"],),
            )
            return {"ok": False, "error": "expired"}
        if inv.get("intended_machine") and machine_id and inv["intended_machine"] != machine_id:
            return {"ok": False, "error": "machine_mismatch"}

        db.execute(
            """
            UPDATE maat_invites SET
                status = 'claimed',
                claimed_by = %s,
                claimed_at = NOW(),
                updated_at = NOW()
            WHERE invite_id = %s
            """,
            (by_agent, inv["invite_id"]),
        )
        hid = str(inv["handoff_id"]) if inv.get("handoff_id") else None
        if hid:
            self.receive(hid, by_agent=by_agent)
            self.acknowledge(
                hid,
                by_agent=by_agent,
                note=f"claimed invite {inv['invite_id']}",
            )

        gate = should_enroll(
            principal_id=inv["principal_id"],
            agent_id=by_agent,
            intended_ring=inv["intended_ring"],
            machine_id=machine_id,
            human_approval=human_approval,
            lab_interim=lab_interim,
        )
        if not gate.get("ok"):
            return {
                "ok": False,
                "error": "guard_denied",
                "invite_id": str(inv["invite_id"]),
                "guard": gate,
                "handoff_id": hid,
            }

        ring = gate.get("intended_ring") or inv["intended_ring"] or "outer"
        enrolled = None
        birth = None
        if auto_enroll:
            reg = FleetRegistry()
            enrolled = reg.enroll_agent(
                agent_id=by_agent,
                tool_type=tool_type or inv.get("intended_tool") or "cursor",
                machine_id=machine_id,
                ring=ring,
                role=role,
                principal_id=inv["principal_id"],
                metadata={
                    "principal_id": inv["principal_id"],
                    "invite_id": str(inv["invite_id"]),
                    "guard_decision": gate.get("decision"),
                    "guard_correlation_id": gate.get("correlation_id"),
                    "working_on": work,
                },
            )
            db.execute(
                "UPDATE maat_agents SET principal_id=%s, ring=%s, updated_at=NOW() WHERE agent_id=%s",
                (inv["principal_id"], ring, by_agent),
            )
            TepiIdentity().bind(
                principal_id=inv["principal_id"],
                agent_id=by_agent,
                ring=ring,
                machine_id=machine_id,
                episode_id=str(inv["invite_id"]),
                summary="signup enroll after Guard allow",
                payload={"invite_id": str(inv["invite_id"]), "guard": gate.get("decision")},
            )
            birth = EnrollmentBirth().birth(
                working_on=work,
                principal_id=inv["principal_id"],
                tool_type=tool_type or inv.get("intended_tool") or "cursor",
                agent_id=by_agent,
                machine_id=machine_id,
                ring=ring,
                role=role,
                invite_id=str(inv["invite_id"]),
                episode_id=str(inv["invite_id"]),
                metadata={
                    "guard_decision": gate.get("decision"),
                    "guard_correlation_id": gate.get("correlation_id"),
                    "join": True,
                },
                enroll=False,  # already enrolled above
            )
            if not birth.get("ok"):
                return {
                    "ok": False,
                    "error": "birth_failed",
                    "invite_id": str(inv["invite_id"]),
                    "birth": birth,
                    "enrolled": enrolled,
                }

        consumed = self.consume_invite_after_enroll(
            str(inv["invite_id"]),
            by_agent=by_agent,
            verifier=f"guard:{gate.get('decision')}",
        )
        return {
            "ok": True,
            "invite_id": str(inv["invite_id"]),
            "principal_id": inv["principal_id"],
            "intended_ring": ring,
            "working_on": work,
            "role": role,
            "handoff_id": hid,
            "guard": gate,
            "enrolled": enrolled,
            "birth": birth,
            "consumed": consumed,
        }

    def consume_invite_after_enroll(
        self,
        invite_id: str,
        *,
        by_agent: str,
        verifier: str,
    ) -> dict[str, Any]:
        inv = db.fetchone("SELECT * FROM maat_invites WHERE invite_id = %s::uuid", (invite_id,))
        if not inv:
            return {"ok": False, "error": "invite_not_found"}
        if inv["status"] not in ("claimed", "issued"):
            return {"ok": False, "error": "bad_status", "status": inv["status"]}
        db.execute(
            """
            UPDATE maat_invites SET
                status = 'consumed',
                consumed_by = %s,
                consumed_at = NOW(),
                updated_at = NOW()
            WHERE invite_id = %s::uuid
            """,
            (by_agent, invite_id),
        )
        hid = str(inv["handoff_id"]) if inv.get("handoff_id") else None
        verified = None
        if hid:
            # Signup verify: skip fetch_sha; evidence is enroll binding
            row = self.get(hid)
            if row and row["status"] == "offered":
                self.receive(hid, by_agent=by_agent)
            if row and row["status"] in ("offered", "received"):
                self.acknowledge(hid, by_agent=by_agent, note="enrolled")
            evidence = {"enroll_agent": by_agent, "invite_id": invite_id}
            db.execute(
                """
                UPDATE maat_handoffs SET
                    status = 'verified',
                    verified_by = %s,
                    verified_at = NOW(),
                    closed_at = NOW(),
                    evidence = COALESCE(evidence, '{}'::jsonb) || %s::jsonb,
                    challenge = jsonb_build_object('type','invite_consume','ok',true),
                    updated_at = NOW()
                WHERE handoff_id = %s::uuid
                """,
                (verifier, json.dumps(evidence), hid),
            )
            verified = self.get(hid)
        return {"ok": True, "invite_id": invite_id, "handoff": verified}

    def _gate_open(self, row: dict[str, Any], by_agent: str) -> dict[str, Any]:
        if self._expired(row):
            self._mark_expired(str(row["handoff_id"]))
            return {"ok": False, "error": "expired"}
        to_agent = row.get("to_agent")
        if to_agent and to_agent != by_agent:
            return {"ok": False, "error": "not_addressee", "to_agent": to_agent}
        return {"ok": True}

    @staticmethod
    def _expired(row: dict[str, Any]) -> bool:
        exp = row.get("expires_at")
        if not exp:
            return False
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        return exp < datetime.now(timezone.utc)

    def _mark_expired(self, handoff_id: str) -> None:
        db.execute(
            """
            UPDATE maat_handoffs SET
                status = 'expired', closed_at = NOW(), updated_at = NOW()
            WHERE handoff_id = %s::uuid
              AND status IN ('offered', 'received', 'acknowledged')
            """,
            (handoff_id,),
        )
