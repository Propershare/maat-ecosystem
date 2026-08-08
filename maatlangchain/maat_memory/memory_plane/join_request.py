"""Join Request ritual — agent knocks, Head Operator decides, local agent produces.

Innovation (vs traditional key handoff):
  1) Agent: ask-join  → pending request + sentinel record
  2) Imhotep: join-inbox / join-decide allow|deny → sentinel record
  3) On allow: one-time provision code
  4) Agent: join-produce → birth + local credential bundle (never reads .env.broker)

Organ Bearer: NOT auto-copied from broker. Optional operator attach on allow
(--with-discovery-only is default). Full organ key remains a separate Head Operator
choice until scoped organ tokens exist.
"""

from __future__ import annotations

import hashlib
import json
import os
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

from ..machine_info import get_machine_info, get_unique_agent_id
from . import db
from .enrollment import EnrollmentBirth, build_full_identity
from .handoff import normalize_ring
from .operator_authority import OperatorAuthority
from .tepi import TepiIdentity


DEFAULT_DISCOVERY = os.environ.get(
    "MAAT_DISCOVERY_URL", "http://192.168.4.21:8010/manifest"
)
POLICY_VERSION = "maat-join@0.1.1"


def _utcnow():
    return datetime.now(timezone.utc)


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _event_hash(payload: dict[str, Any]) -> str:
    blob = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _sentinel(
    *,
    request_id: str | None,
    event_type: str,
    actor: str,
    summary: str,
    decision: str | None = None,
    grant_id: str | None = None,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    prev = None
    if request_id:
        prev_row = db.fetchone(
            """
            SELECT event_hash FROM maat_join_sentinel_events
            WHERE request_id = %s::uuid AND event_hash IS NOT NULL
            ORDER BY occurred_at DESC LIMIT 1
            """,
            (request_id,),
        )
        if prev_row:
            prev = prev_row.get("event_hash")
    body = {
        "event_type": event_type,
        "actor": actor,
        "decision": decision,
        "summary": summary,
        "request_id": request_id,
        "grant_id": grant_id,
        "payload": payload or {},
        "previous_event_hash": prev,
        "policy_version": POLICY_VERSION,
    }
    eh = _event_hash(body)
    # Columns event_hash may be missing pre-migrate — try full insert then fallback
    try:
        row = db.execute_returning(
            """
            INSERT INTO maat_join_sentinel_events (
                request_id, grant_id, event_type, actor, decision, summary, payload,
                event_hash, previous_event_hash
            ) VALUES (
                %s::uuid, %s::uuid, %s, %s, %s, %s, %s::jsonb, %s, %s
            )
            RETURNING event_id::text AS event_id, occurred_at, event_type, event_hash
            """,
            (
                request_id,
                grant_id,
                event_type,
                actor,
                decision,
                summary,
                json.dumps(payload or {}),
                eh,
                prev,
            ),
        )
    except Exception:
        row = db.execute_returning(
            """
            INSERT INTO maat_join_sentinel_events (
                request_id, grant_id, event_type, actor, decision, summary, payload
            ) VALUES (
                %s::uuid, %s::uuid, %s, %s, %s, %s, %s::jsonb
            )
            RETURNING event_id::text AS event_id, occurred_at, event_type
            """,
            (
                request_id,
                grant_id,
                event_type,
                actor,
                decision,
                summary,
                json.dumps(payload or {}),
            ),
        )
    pid = (payload or {}).get("principal_id")
    aid = (payload or {}).get("agent_id")
    if pid and aid:
        try:
            TepiIdentity().log(
                principal_id=pid,
                agent_id=aid,
                ring=(payload or {}).get("ring") or "outer",
                machine_id=(payload or {}).get("machine_id"),
                episode_id=request_id,
                event_type=f"join_sentinel:{event_type}",
                summary=summary,
                payload={"sentinel_event": row, **(payload or {})},
            )
        except Exception:
            pass
    return dict(row) if row else {"ok": False}


def constitutional_help(topic: str | None = None) -> dict[str, Any]:
    """Governed help — rules and commands, never secrets."""
    base = {
        "schema": "maat.join.help.v0",
        "policy_version": POLICY_VERSION,
        "available": [
            "ask-join — request membership (pending)",
            "join-status — check pending/allowed/denied/produced",
            "join-produce — after allow, claim on same machine (--request-id; --code offline backup only)",
            "whoami — show local identity without secrets",
            "join-help — this guide",
            "join-inbox / join-decide — Head Operator only (operator token required)",
        ],
        "forbidden": [
            "Do not read .env.broker or .ka-auth",
            "Do not copy operator secrets or another machine's credentials",
            "Do not self-approve join-decide",
            "Do not expect organ_bearer / master KA key from join-produce",
            "Do not birth silent subagents with inherited authority",
        ],
        "identity_layers": [
            "operator_principal — human Head Operator (e.g. imhotep)",
            "principal — sovereign the agent acts under",
            "agent_id — tool instance",
            "machine_id — host",
            "birth_id — enrollment birth certificate",
            "working_on — specific chore",
        ],
    }
    topics = {
        "join": {
            "steps": [
                "1) ask-join --working-on 'specific chore' --principal imhotep",
                "2) wait; Head Operator join-inbox + join-decide --allow|--deny",
                "3) join-produce --request-id <id>  (same machine; --code only as offline backup)",
                "4) whoami; run approved chore; report birth_id + findings",
            ]
        },
        "scopes": {
            "level_1_member": [
                "discovery:read",
                "identity:birth",
                "whoami:read",
                "join:status",
                "openapi:probe",
            ],
            "not_default": [
                "memory:write",
                "tool:execute",
                "organ:admin",
                "broker:read",
                "key:mint",
            ],
        },
        "denied": {
            "meaning": "Deny is a recorded Sentinel outcome with reason — not silence.",
            "next": "Fix chore/scope and ask-join again; do not reuse old provision codes.",
        },
    }
    t = (topic or "").strip().lower()
    if t and t in topics:
        return {**base, "topic": t, **topics[t]}
    if t:
        return {**base, "error": "unknown_topic", "topics": list(topics)}
    return {**base, "topics": list(topics), "hint": "join-help --topic join|scopes|denied"}


class JoinRequestRitual:
    """Head-Operator-gated join: ask → decide → produce."""

    _self_report_migrated = False

    @classmethod
    def _ensure_self_report_columns(cls) -> None:
        """One-shot migration: add ask-join self-report v0.2 columns if missing."""
        if cls._self_report_migrated:
            return
        try:
            db.execute(
                """
                ALTER TABLE maat_join_requests
                  ADD COLUMN IF NOT EXISTS runtime TEXT,
                  ADD COLUMN IF NOT EXISTS cwd TEXT,
                  ADD COLUMN IF NOT EXISTS git_branch TEXT,
                  ADD COLUMN IF NOT EXISTS git_commit TEXT,
                  ADD COLUMN IF NOT EXISTS requested_scopes JSONB,
                  ADD COLUMN IF NOT EXISTS requested_mcps JSONB,
                  ADD COLUMN IF NOT EXISTS available_mcps JSONB,
                  ADD COLUMN IF NOT EXISTS forbidden_paths_acknowledged JSONB
                """
            )
            cls._self_report_migrated = True
        except Exception:
            # Older Postgres or missing table — fall back to identity_snapshot JSONB.
            cls._self_report_migrated = True

    def ask(
        self,
        *,
        working_on: str,
        principal_id: str = "imhotep",
        tool_type: str = "cursor",
        role: str = "fleet_tester",
        ring: str = "outer",
        organs: list[str] | None = None,
        message: str | None = None,
        agent_id: str | None = None,
        ttl_hours: int = 48,
        # --- ask-join self-report v0.2 ---
        runtime: str | None = None,
        workspace_root: str | None = None,
        cwd: str | None = None,
        git_branch: str | None = None,
        git_commit: str | None = None,
        requested_scopes: list[str] | None = None,
        requested_mcps: list[str] | None = None,
        available_mcps: list[str] | None = None,
        forbidden_paths_acknowledged: list[str] | None = None,
        # Remote Desktop / edge ask via hub proxy — declare the *edge* machine
        machine_id: str | None = None,
        hostname: str | None = None,
    ) -> dict[str, Any]:
        work = (working_on or "").strip()
        if not work:
            return {
                "ok": False,
                "error": "working_on_required",
                "hint": "Say the specific chore you want authorization for.",
            }
        pid = (principal_id or "").strip() or "imhotep"
        TepiIdentity().ensure_principal(pid)
        info = get_machine_info()
        aid = agent_id or get_unique_agent_id(tool_type)
        declared_mid = (machine_id or "").strip() or None
        declared_host = (hostname or "").strip() or None
        mid = declared_mid or info["machine_id"]
        ring_n = normalize_ring(ring)
        organs_n = organs or ["discovery", "brain", "memory"]

        # self-report: agent-declared wins over machine-detected, but keep both
        ws_declared = (workspace_root or "").strip() or None
        ws_effective = ws_declared or info.get("workspace_root")
        runtime_effective = (runtime or tool_type or "").strip() or "unknown"
        self_report = {
            "runtime": runtime_effective,
            "workspace_root_declared": ws_declared,
            "workspace_root_observed": info.get("workspace_root"),
            "cwd": (cwd or "").strip() or None,
            "git_branch": (git_branch or "").strip() or None,
            "git_commit": (git_commit or "").strip() or None,
            "requested_scopes": requested_scopes or None,
            "requested_mcps": requested_mcps or None,
            "available_mcps": available_mcps or None,
            "forbidden_paths_acknowledged": forbidden_paths_acknowledged or None,
            "os_user_observed": info.get("user"),
            "hostname_observed": info.get("hostname"),
            "hostname_declared": declared_host,
            "machine_id_declared": declared_mid,
            "machine_id_observed": info.get("machine_id"),
            "proxied_ask": bool(declared_mid and declared_mid != info.get("machine_id")),
        }
        # detect mismatch between declared workspace_root and observed
        self_report["workspace_mismatch"] = bool(
            ws_declared and info.get("workspace_root")
            and ws_declared != info.get("workspace_root")
        )

        identity = build_full_identity(
            agent_id=aid,
            machine_id=mid,
            principal_id=pid,
            working_on=work,
            tool_type=tool_type,
            ring=ring_n,
            role=role,
        )
        # Merge self-report into identity_snapshot so it is queryable via JSONB even
        # if the ALTER TABLE migration failed on an older server.
        identity["self_report"] = self_report

        self._ensure_self_report_columns()

        corr = f"joinreq:{secrets.token_hex(8)}"
        expires = _utcnow() + timedelta(hours=max(1, ttl_hours))
        # Preferred write path: with self-report columns.
        row = None
        try:
            row = db.execute_returning(
                """
                INSERT INTO maat_join_requests (
                    status, requesting_agent_id, machine_id, hostname, os_user, tool_type,
                    workspace_root, workspace_slug, principal_id, operator_principal_id,
                    requested_ring, requested_role, working_on, requested_organs,
                    identity_snapshot, message, correlation_id, expires_at,
                    runtime, cwd, git_branch, git_commit,
                    requested_scopes, requested_mcps, available_mcps,
                    forbidden_paths_acknowledged
                ) VALUES (
                    'pending', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s::jsonb, %s::jsonb, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s::jsonb, %s::jsonb, %s::jsonb, %s::jsonb
                )
                RETURNING *
                """,
                (
                    aid,
                    mid,
                    declared_host or info.get("hostname"),
                    info.get("user"),
                    tool_type,
                    ws_effective,
                    info.get("workspace_slug"),
                    pid,
                    pid,
                    ring_n,
                    role,
                    work,
                    json.dumps(organs_n),
                    json.dumps(identity),
                    message or "",
                    corr,
                    expires,
                    runtime_effective,
                    self_report["cwd"],
                    self_report["git_branch"],
                    self_report["git_commit"],
                    json.dumps(self_report["requested_scopes"]) if self_report["requested_scopes"] is not None else None,
                    json.dumps(self_report["requested_mcps"]) if self_report["requested_mcps"] is not None else None,
                    json.dumps(self_report["available_mcps"]) if self_report["available_mcps"] is not None else None,
                    json.dumps(self_report["forbidden_paths_acknowledged"]) if self_report["forbidden_paths_acknowledged"] is not None else None,
                ),
            )
        except Exception:
            row = None
        if not row:
            row = db.execute_returning(
                """
                INSERT INTO maat_join_requests (
                    status, requesting_agent_id, machine_id, hostname, os_user, tool_type,
                    workspace_root, workspace_slug, principal_id, operator_principal_id,
                    requested_ring, requested_role, working_on, requested_organs,
                    identity_snapshot, message, correlation_id, expires_at
                ) VALUES (
                    'pending', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s::jsonb, %s::jsonb, %s, %s, %s
                )
                RETURNING *
                """,
                (
                    aid,
                    mid,
                    declared_host or info.get("hostname"),
                    info.get("user"),
                    tool_type,
                    ws_effective,
                    info.get("workspace_slug"),
                    pid,
                    pid,
                    ring_n,
                    role,
                    work,
                    json.dumps(organs_n),
                    json.dumps(identity),
                    message or "",
                    corr,
                    expires,
                ),
            )
        if not row:
            # fallback without new columns
            row = db.execute_returning(
                """
                INSERT INTO maat_join_requests (
                    status, requesting_agent_id, machine_id, hostname, os_user, tool_type,
                    workspace_root, workspace_slug, principal_id, requested_ring,
                    requested_role, working_on, requested_organs, identity_snapshot,
                    message, correlation_id, expires_at
                ) VALUES (
                    'pending', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s::jsonb, %s::jsonb, %s, %s, %s
                )
                RETURNING *
                """,
                (
                    aid,
                    mid,
                    declared_host or info.get("hostname"),
                    info.get("user"),
                    tool_type,
                    info.get("workspace_root"),
                    info.get("workspace_slug"),
                    pid,
                    ring_n,
                    role,
                    work,
                    json.dumps(organs_n),
                    json.dumps(identity),
                    message or "",
                    corr,
                    expires,
                ),
            )
        if not row:
            return {"ok": False, "error": "request_insert_failed"}
        rid = str(row["request_id"])
        sev = _sentinel(
            request_id=rid,
            event_type="join_requested",
            actor=aid,
            decision="pending",
            summary=f"Agent {aid} requests join under {pid}: {work}",
            payload={
                "principal_id": pid,
                "operator_principal_id": pid,
                "agent_id": aid,
                "machine_id": mid,
                "ring": ring_n,
                "working_on": work,
                "organs": organs_n,
                "correlation_id": corr,
                "policy_version": POLICY_VERSION,
                "self_report": self_report,
            },
        )
        return {
            "ok": True,
            "status": "pending",
            "request_id": rid,
            "correlation_id": corr,
            "principal_id": pid,
            "operator_principal_id": pid,
            "agent_id": aid,
            "machine_id": mid,
            "working_on": work,
            "requested_organs": organs_n,
            "expires_at": row.get("expires_at"),
            "sentinel_event_id": sev.get("event_id"),
            "policy_version": POLICY_VERSION,
            "next": (
                "Head Operator: join-inbox && "
                f"join-decide --id {rid} --allow|--deny --reason '...' --operator-token <TOKEN>"
            ),
            "agent_wait": (
                f"join-status --id {rid} then "
                f"join-produce --request-id {rid}  # same machine; no code walk"
            ),
        }

    def inbox(
        self,
        *,
        principal_id: str | None = "imhotep",
        status: str = "pending",
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        # Try the richer projection (v0.2 self-report columns). If those columns
        # don't exist yet on this DB, fall back to the legacy projection and
        # backfill the missing keys from identity_snapshot.self_report.
        try:
            if principal_id:
                rows = db.fetchall(
                    """
                    SELECT request_id, status, requesting_agent_id, machine_id, hostname,
                           os_user, principal_id, requested_ring, requested_role,
                           working_on, requested_organs, message, created_at, expires_at,
                           correlation_id, workspace_root, runtime, cwd, git_branch,
                           git_commit, requested_scopes, requested_mcps, available_mcps,
                           forbidden_paths_acknowledged, identity_snapshot
                    FROM maat_join_requests
                    WHERE principal_id = %s AND status = %s
                    ORDER BY created_at ASC
                    LIMIT %s
                    """,
                    (principal_id, status, limit),
                )
            else:
                rows = db.fetchall(
                    """
                    SELECT request_id, status, requesting_agent_id, machine_id, hostname,
                           os_user, principal_id, requested_ring, requested_role,
                           working_on, requested_organs, message, created_at, expires_at,
                           correlation_id, workspace_root, runtime, cwd, git_branch,
                           git_commit, requested_scopes, requested_mcps, available_mcps,
                           forbidden_paths_acknowledged, identity_snapshot
                    FROM maat_join_requests
                    WHERE status = %s
                    ORDER BY created_at ASC
                    LIMIT %s
                    """,
                    (status, limit),
                )
        except Exception:
            if principal_id:
                rows = db.fetchall(
                    """
                    SELECT request_id, status, requesting_agent_id, machine_id, hostname,
                           os_user, principal_id, requested_ring, requested_role,
                           working_on, requested_organs, message, created_at, expires_at,
                           correlation_id, workspace_root, identity_snapshot
                    FROM maat_join_requests
                    WHERE principal_id = %s AND status = %s
                    ORDER BY created_at ASC
                    LIMIT %s
                    """,
                    (principal_id, status, limit),
                )
            else:
                rows = db.fetchall(
                    """
                    SELECT request_id, status, requesting_agent_id, machine_id, hostname,
                           os_user, principal_id, requested_ring, requested_role,
                           working_on, requested_organs, message, created_at, expires_at,
                           correlation_id, workspace_root, identity_snapshot
                    FROM maat_join_requests
                    WHERE status = %s
                    ORDER BY created_at ASC
                    LIMIT %s
                    """,
                    (status, limit),
                )
        out = []
        for r in rows or []:
            d = dict(r)
            snap = d.get("identity_snapshot") or {}
            sr = (snap or {}).get("self_report") if isinstance(snap, dict) else None
            if isinstance(sr, dict):
                for k in ("runtime", "cwd", "git_branch", "git_commit",
                          "requested_scopes", "requested_mcps", "available_mcps",
                          "forbidden_paths_acknowledged"):
                    d.setdefault(k, sr.get(k))
                d["workspace_mismatch"] = bool(sr.get("workspace_mismatch"))
                d["workspace_root_declared"] = sr.get("workspace_root_declared")
                d["workspace_root_observed"] = sr.get("workspace_root_observed")
            out.append(d)
        return out

    def status(self, request_id: str) -> dict[str, Any]:
        row = db.fetchone(
            "SELECT * FROM maat_join_requests WHERE request_id = %s::uuid",
            (request_id,),
        )
        if not row:
            return {"ok": False, "error": "not_found"}
        d = dict(row)
        # Never leak provision hash; say if produce is ready
        out = {
            "ok": True,
            "request_id": str(d["request_id"]),
            "status": d["status"],
            "decision": d.get("decision"),
            "decision_reason": d.get("decision_reason"),
            "principal_id": d.get("principal_id"),
            "agent_id": d.get("requesting_agent_id"),
            "working_on": d.get("working_on"),
            "decided_by": d.get("decided_by"),
            "decided_at": d.get("decided_at"),
            "produce_ready": d["status"] == "allowed",
            "produced_at": d.get("produced_at"),
            "birth_id": str(d["birth_id"]) if d.get("birth_id") else None,
        }
        if d["status"] == "allowed":
            # Agent on the bound machine claims without you walking a code.
            out["next"] = (
                f"python3 /mnt/data_drive/hermes/scripts/maat_memory_plane.py "
                f"join-produce --request-id {d['request_id']}"
            )
            out["hint"] = (
                "produce_ready: run join-produce --request-id on the SAME machine/agent "
                "that asked. No courier code. --code is offline backup only."
            )
        return out

    def decide(
        self,
        request_id: str,
        *,
        allow: bool,
        reason: str,
        decided_by_agent: str,
        operator_token: str | None = None,
        operator_principal_id: str = "imhotep",
        discovery_url: str | None = None,
        scopes: list[str] | None = None,
        denied_scopes: list[str] | None = None,
        ttl_hours: int = 24,
        request_digest: str | None = None,
    ) -> dict[str, Any]:
        reason_s = (reason or "").strip()
        if not reason_s:
            return {
                "ok": False,
                "error": "reason_required",
                "hint": "Head Operator must say why allow or deny (accountability).",
            }

        auth = OperatorAuthority().verify(
            operator_token, principal_id=operator_principal_id
        )
        if not auth.get("ok"):
            _sentinel(
                request_id=request_id if request_id else None,
                event_type="join_decide_auth_denied",
                actor=decided_by_agent or "unknown",
                decision="deny",
                summary=f"decide blocked: {auth.get('error')}",
                payload={
                    "error": auth.get("error"),
                    "agent_id": decided_by_agent,
                    "operator_principal_id": operator_principal_id,
                    "policy_version": POLICY_VERSION,
                },
            )
            return {**auth, "recorded": True}

        row = db.fetchone(
            "SELECT * FROM maat_join_requests WHERE request_id = %s::uuid",
            (request_id,),
        )
        if not row:
            return {"ok": False, "error": "not_found"}

        # Isfet I1: agent cannot self-approve
        if decided_by_agent and decided_by_agent == row["requesting_agent_id"]:
            _sentinel(
                request_id=str(row["request_id"]),
                event_type="join_self_approve_denied",
                actor=decided_by_agent,
                decision="deny",
                summary="Self-approve blocked — requesting agent cannot decide own join",
                payload={
                    "principal_id": row["principal_id"],
                    "agent_id": row["requesting_agent_id"],
                    "machine_id": row.get("machine_id"),
                    "policy_version": POLICY_VERSION,
                },
            )
            return {
                "ok": False,
                "error": "self_approve_denied",
                "hint": (
                    "Head Operator must decide from a different agent_id "
                    "(e.g. MAAT_AGENT_ID=operator_imhotep) with operator token."
                ),
                "recorded": True,
            }

        if row["status"] != "pending":
            return {
                "ok": False,
                "error": "not_pending",
                "status": row["status"],
            }
        if row.get("expires_at") and row["expires_at"] < _utcnow():
            db.execute(
                "UPDATE maat_join_requests SET status='expired', updated_at=NOW() WHERE request_id=%s",
                (row["request_id"],),
            )
            _sentinel(
                request_id=str(row["request_id"]),
                event_type="join_expired",
                actor=decided_by_agent,
                decision="deny",
                summary="Request expired before decision",
                payload={
                    "principal_id": row["principal_id"],
                    "agent_id": row["requesting_agent_id"],
                    "operator_principal_id": operator_principal_id,
                },
            )
            return {"ok": False, "error": "expired"}

        decision = "allow" if allow else "deny"
        approved = scopes or [
            "discovery:read",
            "identity:birth",
            "preflight",
            "openapi:probe",
            "whoami:read",
            "join:status",
        ]
        denied = denied_scopes or [
            "memory:write",
            "tool:execute",
            "organ:admin",
            "broker:read",
            "key:mint",
        ]

        if not allow:
            try:
                db.execute(
                    """
                    UPDATE maat_join_requests SET
                        status = 'denied',
                        decision = 'deny',
                        decision_reason = %s,
                        decided_by = %s,
                        decided_by_agent = %s,
                        decided_by_principal = %s,
                        operator_principal_id = %s,
                        decided_at = NOW(),
                        updated_at = NOW()
                    WHERE request_id = %s
                    """,
                    (
                        reason_s,
                        decided_by_agent,
                        decided_by_agent,
                        operator_principal_id,
                        operator_principal_id,
                        row["request_id"],
                    ),
                )
            except Exception:
                db.execute(
                    """
                    UPDATE maat_join_requests SET
                        status = 'denied',
                        decision = 'deny',
                        decision_reason = %s,
                        decided_by = %s,
                        decided_at = NOW(),
                        updated_at = NOW()
                    WHERE request_id = %s
                    """,
                    (reason_s, decided_by_agent, row["request_id"]),
                )
            sev = _sentinel(
                request_id=str(row["request_id"]),
                event_type="join_denied",
                actor=decided_by_agent,
                decision="deny",
                summary=f"Head Operator DENY: {reason_s}",
                payload={
                    "principal_id": row["principal_id"],
                    "operator_principal_id": operator_principal_id,
                    "decided_by_agent": decided_by_agent,
                    "decided_by_principal": operator_principal_id,
                    "agent_id": row["requesting_agent_id"],
                    "machine_id": row.get("machine_id"),
                    "working_on": row.get("working_on"),
                    "reason": reason_s,
                    "request_digest": request_digest,
                    "policy_version": POLICY_VERSION,
                },
            )
            return {
                "ok": True,
                "decision": "deny",
                "request_id": str(row["request_id"]),
                "status": "denied",
                "operator_principal_id": operator_principal_id,
                "decided_by_agent": decided_by_agent,
                "request_digest": request_digest,
                "sentinel_event_id": sev.get("event_id"),
                "recorded": True,
            }

        # ALLOW → mint one-time provision code + grant (machine-bound)
        provision = secrets.token_urlsafe(24)
        provision_hash = _hash(provision)
        session = secrets.token_urlsafe(32)
        session_hash = _hash(session)
        grant_expires = _utcnow() + timedelta(hours=max(1, ttl_hours))
        discovery = discovery_url or DEFAULT_DISCOVERY
        organs = row.get("requested_organs") or ["discovery"]
        if isinstance(organs, str):
            organs = json.loads(organs)

        grant = db.execute_returning(
            """
            INSERT INTO maat_join_grants (
                request_id, agent_id, principal_id, machine_id, ring, role,
                working_on, scopes, allowed_organs, discovery_url,
                session_token_hash, status, issued_by, expires_at, local_bundle
            ) VALUES (
                %s::uuid, %s, %s, %s, %s, %s, %s, %s::jsonb, %s::jsonb, %s,
                %s, 'issued', %s, %s, %s::jsonb
            )
            RETURNING grant_id::text AS grant_id, expires_at
            """,
            (
                row["request_id"],
                row["requesting_agent_id"],
                row["principal_id"],
                row.get("machine_id"),
                row.get("requested_ring") or "outer",
                row.get("requested_role") or "fleet_tester",
                row["working_on"],
                json.dumps(approved),
                json.dumps(organs),
                discovery,
                session_hash,
                decided_by_agent,
                grant_expires,
                json.dumps(
                    {
                        "schema": "maat.local_bundle.v0",
                        "discovery_url": discovery,
                        "scopes": approved,
                        "denied_scopes": denied,
                        "bound_machine_id": row.get("machine_id"),
                        "bound_agent_id": row["requesting_agent_id"],
                        "operator_principal_id": operator_principal_id,
                        "decided_by_agent": decided_by_agent,
                        "request_digest": request_digest,
                        "policy_version": POLICY_VERSION,
                        "note": (
                            "Organ Bearer NOT included. Machine-bound provision. "
                            "Never read .env.broker."
                        ),
                    }
                ),
            ),
        )
        if not grant:
            return {"ok": False, "error": "grant_insert_failed"}

        try:
            db.execute(
                """
                UPDATE maat_join_requests SET
                    status = 'allowed',
                    decision = 'allow',
                    decision_reason = %s,
                    decided_by = %s,
                    decided_by_agent = %s,
                    decided_by_principal = %s,
                    operator_principal_id = %s,
                    approved_scopes = %s::jsonb,
                    denied_scopes = %s::jsonb,
                    decided_at = NOW(),
                    grant_id = %s::uuid,
                    provision_token_hash = %s,
                    provision_expires_at = %s,
                    updated_at = NOW()
                WHERE request_id = %s
                """,
                (
                    reason_s,
                    decided_by_agent,
                    decided_by_agent,
                    operator_principal_id,
                    operator_principal_id,
                    json.dumps(approved),
                    json.dumps(denied),
                    grant["grant_id"],
                    provision_hash,
                    grant_expires,
                    row["request_id"],
                ),
            )
        except Exception:
            db.execute(
                """
                UPDATE maat_join_requests SET
                    status = 'allowed',
                    decision = 'allow',
                    decision_reason = %s,
                    decided_by = %s,
                    decided_at = NOW(),
                    grant_id = %s::uuid,
                    provision_token_hash = %s,
                    provision_expires_at = %s,
                    updated_at = NOW()
                WHERE request_id = %s
                """,
                (
                    reason_s,
                    decided_by_agent,
                    grant["grant_id"],
                    provision_hash,
                    grant_expires,
                    row["request_id"],
                ),
            )
        sev = _sentinel(
            request_id=str(row["request_id"]),
            grant_id=grant["grant_id"],
            event_type="join_allowed",
            actor=decided_by_agent,
            decision="allow",
            summary=f"Head Operator ALLOW: {reason_s}",
            payload={
                "principal_id": row["principal_id"],
                "operator_principal_id": operator_principal_id,
                "decided_by_agent": decided_by_agent,
                "decided_by_principal": operator_principal_id,
                "agent_id": row["requesting_agent_id"],
                "machine_id": row.get("machine_id"),
                "working_on": row.get("working_on"),
                "reason": reason_s,
                "grant_id": grant["grant_id"],
                "approved_scopes": approved,
                "denied_scopes": denied,
                "request_digest": request_digest,
                "policy_version": POLICY_VERSION,
            },
        )
        return {
            "ok": True,
            "decision": "allow",
            "request_id": str(row["request_id"]),
            "status": "allowed",
            "grant_id": grant["grant_id"],
            "provision_code": provision,
            "expires_at": grant.get("expires_at"),
            "discovery_url": discovery,
            "approved_scopes": approved,
            "denied_scopes": denied,
            "bound_machine_id": row.get("machine_id"),
            "bound_agent_id": row["requesting_agent_id"],
            "operator_principal_id": operator_principal_id,
            "decided_by_agent": decided_by_agent,
            "request_digest": request_digest,
            "sentinel_event_id": sev.get("event_id"),
            "policy_version": POLICY_VERSION,
            "hint": (
                "Agent claims on the bound machine: join-produce --request-id <id>. "
                "provision_code is OPTIONAL offline backup — do not courier it. "
                "Machine-bound + one-time. No master KA key."
            ),
            "agent_claim": (
                f"python3 /mnt/data_drive/hermes/scripts/maat_memory_plane.py "
                f"join-produce --request-id {row['request_id']}"
            ),
            "recorded": True,
        }

    def produce(
        self,
        provision_code: str | None = None,
        *,
        request_id: str | None = None,
        tool_type: str = "cursor",
        credential_dir: str | None = None,
        skip_machine_bind: bool = False,
        agent_id: str | None = None,
    ) -> dict[str, Any]:
        """Local agent produces birth + credentials.

        Preferred: ``request_id`` on the same machine/agent that asked (no code walk).
        Backup: one-time ``provision_code`` for offline/remote handoff.
        Hub Desktop proxy may pass ``agent_id`` + ``skip_machine_bind`` with a temp credential_dir.
        """
        code = (provision_code or "").strip()
        rid_in = (request_id or "").strip()
        if not code and not rid_in:
            return {
                "ok": False,
                "error": "request_id_or_provision_code_required",
                "hint": "Prefer: join-produce --request-id <uuid> on the asking machine.",
            }

        info = get_machine_info()
        local_mid = info["machine_id"]
        local_aid = (agent_id or "").strip() or get_unique_agent_id(tool_type)

        req = None
        claim_via = None
        if rid_in:
            req = db.fetchone(
                "SELECT * FROM maat_join_requests WHERE request_id = %s::uuid",
                (rid_in,),
            )
            claim_via = "request_id"
            if not req:
                _sentinel(
                    request_id=rid_in,
                    event_type="join_produce_denied",
                    actor=local_aid,
                    decision="deny",
                    summary="request_not_found",
                    payload={
                        "error": "not_found",
                        "agent_id": local_aid,
                        "machine_id": local_mid,
                        "policy_version": POLICY_VERSION,
                    },
                )
                return {"ok": False, "error": "not_found", "recorded": True}
        else:
            th = _hash(code)
            req = db.fetchone(
                """
                SELECT * FROM maat_join_requests
                WHERE provision_token_hash = %s
                """,
                (th,),
            )
            claim_via = "provision_code"
        if not req:
            _sentinel(
                request_id=None,
                event_type="join_produce_denied",
                actor=local_aid,
                decision="deny",
                summary="invalid_or_used_code",
                payload={
                    "error": "invalid_or_used_code",
                    "agent_id": local_aid,
                    "machine_id": local_mid,
                    "policy_version": POLICY_VERSION,
                    "claim_via": claim_via,
                },
            )
            return {
                "ok": False,
                "error": "invalid_or_used_code",
                "hint": "Ask Head Operator to allow again, or join-produce --request-id <id>.",
                "recorded": True,
            }

        rid = str(req["request_id"])
        if req.get("status") == "denied":
            _sentinel(
                request_id=rid,
                event_type="join_produce_denied",
                actor=local_aid,
                decision="deny",
                summary="denied_request_cannot_produce",
                payload={
                    "error": "denied_request_cannot_produce",
                    "agent_id": local_aid,
                    "machine_id": local_mid,
                    "policy_version": POLICY_VERSION,
                },
            )
            return {
                "ok": False,
                "error": "denied_request_cannot_produce",
                "recorded": True,
            }

        if req.get("status") != "allowed":
            _sentinel(
                request_id=rid,
                event_type="join_produce_denied",
                actor=local_aid,
                decision="deny",
                summary=f"status_{req.get('status')}_cannot_produce",
                payload={
                    "error": "not_allowed_status",
                    "status": req.get("status"),
                    "agent_id": local_aid,
                    "policy_version": POLICY_VERSION,
                },
            )
            return {
                "ok": False,
                "error": "not_allowed_status",
                "status": req.get("status"),
                "recorded": True,
            }

        if req.get("provision_expires_at") and req["provision_expires_at"] < _utcnow():
            db.execute(
                "UPDATE maat_join_requests SET status='expired', updated_at=NOW() WHERE request_id=%s",
                (req["request_id"],),
            )
            _sentinel(
                request_id=rid,
                event_type="join_produce_denied",
                actor=local_aid,
                decision="deny",
                summary="provision_expired",
                payload={
                    "error": "provision_expired",
                    "agent_id": local_aid,
                    "machine_id": local_mid,
                    "policy_version": POLICY_VERSION,
                },
            )
            return {"ok": False, "error": "provision_expired", "recorded": True}

        # Machine bind (Isfet I3)
        bound_mid = req.get("machine_id")
        if (
            not skip_machine_bind
            and bound_mid
            and local_mid
            and bound_mid != local_mid
        ):
            _sentinel(
                request_id=rid,
                event_type="join_produce_denied",
                actor=local_aid,
                decision="deny",
                summary="wrong_machine_cannot_use_code",
                payload={
                    "error": "machine_mismatch",
                    "bound_machine_id": bound_mid,
                    "local_machine_id": local_mid,
                    "agent_id": local_aid,
                    "policy_version": POLICY_VERSION,
                },
            )
            return {
                "ok": False,
                "error": "machine_mismatch",
                "bound_machine_id": bound_mid,
                "local_machine_id": local_mid,
                "recorded": True,
            }

        # Agent bind — produce must be the requesting agent
        bound_aid = req["requesting_agent_id"]
        if local_aid != bound_aid:
            _sentinel(
                request_id=rid,
                event_type="join_produce_denied",
                actor=local_aid,
                decision="deny",
                summary="wrong_agent_cannot_use_code",
                payload={
                    "error": "agent_mismatch",
                    "bound_agent_id": bound_aid,
                    "local_agent_id": local_aid,
                    "policy_version": POLICY_VERSION,
                },
            )
            return {
                "ok": False,
                "error": "agent_mismatch",
                "bound_agent_id": bound_aid,
                "local_agent_id": local_aid,
                "recorded": True,
            }

        grant = db.fetchone(
            "SELECT * FROM maat_join_grants WHERE grant_id = %s::uuid",
            (req.get("grant_id"),),
        )
        if not grant or grant.get("status") != "issued":
            return {"ok": False, "error": "grant_not_issuable", "grant": grant}

        produce_aid = bound_aid
        birth = EnrollmentBirth().birth(
            working_on=req["working_on"],
            principal_id=req["principal_id"],
            tool_type=req.get("tool_type") or tool_type,
            agent_id=produce_aid,
            machine_id=req.get("machine_id"),
            ring=req.get("requested_ring") or "outer",
            role=req.get("requested_role") or "fleet_tester",
            episode_id=str(req["request_id"]),
            metadata={
                "join_request_id": rid,
                "grant_id": str(grant["grant_id"]),
                "produced_via": "join_request_ritual_v0_1",
                "operator_principal_id": req.get("operator_principal_id")
                or req.get("principal_id"),
                "decided_by_agent": req.get("decided_by_agent") or req.get("decided_by"),
                "policy_version": POLICY_VERSION,
            },
        )
        if not birth.get("ok"):
            return {"ok": False, "error": "birth_failed", "birth": birth}

        cred_root = Path(
            credential_dir
            or os.environ.get("MAAT_CREDENTIAL_DIR")
            or (Path.home() / ".maat")
        ).expanduser()
        cred_root.mkdir(mode=0o700, parents=True, exist_ok=True)
        cred_path = cred_root / "credentials.json"
        bundle = grant.get("local_bundle") or {}
        if isinstance(bundle, str):
            bundle = json.loads(bundle)
        local_doc = {
            "schema": "maat.agent_credentials.v0",
            "policy_version": POLICY_VERSION,
            "produced_at": _utcnow().isoformat(),
            "request_id": rid,
            "grant_id": str(grant["grant_id"]),
            "birth_id": birth["birth_id"],
            "agent_id": produce_aid,
            "principal_id": req["principal_id"],
            "operator_principal_id": req.get("operator_principal_id")
            or req.get("principal_id"),
            "decided_by_agent": req.get("decided_by_agent") or req.get("decided_by"),
            "decided_by_principal": req.get("decided_by_principal")
            or req.get("operator_principal_id"),
            "os_user": birth.get("os_user"),
            "machine_id": birth.get("machine_id"),
            "working_on": req["working_on"],
            "ring": req.get("requested_ring"),
            "role": req.get("requested_role"),
            "discovery_url": grant.get("discovery_url") or DEFAULT_DISCOVERY,
            "scopes": grant.get("scopes"),
            "denied_scopes": bundle.get("denied_scopes"),
            "allowed_organs": grant.get("allowed_organs"),
            "full_identity": birth.get("full_identity"),
            "organ_bearer": None,
            "organ_bearer_note": (
                "NOT included by design. Head Operator may issue separately. "
                "Never copy .env.broker."
            ),
            "bundle_note": bundle.get("note"),
        }
        # Refuse to write if someone stuffed a master key into the doc
        for bad in ("KA_API_KEY", "MCPO_API_KEY", "PGVECTOR_DB_URL"):
            if local_doc.get(bad) or (local_doc.get("organ_bearer") and bad in str(local_doc.get("organ_bearer"))):
                return {"ok": False, "error": "refused_master_secret_in_credentials"}

        tmp = cred_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(local_doc, indent=2, default=str) + "\n", encoding="utf-8")
        tmp.chmod(0o600)
        tmp.replace(cred_path)
        cred_path.chmod(0o600)

        db.execute(
            """
            UPDATE maat_join_grants SET
                status = 'redeemed',
                redeemed_at = NOW(),
                updated_at = NOW(),
                local_bundle = COALESCE(local_bundle, '{}'::jsonb) || %s::jsonb
            WHERE grant_id = %s
            """,
            (
                json.dumps({"credential_path": str(cred_path), "birth_id": birth["birth_id"]}),
                grant["grant_id"],
            ),
        )
        db.execute(
            """
            UPDATE maat_join_requests SET
                status = 'produced',
                produced_at = NOW(),
                birth_id = %s::uuid,
                provision_token_hash = NULL,
                updated_at = NOW()
            WHERE request_id = %s
            """,
            (birth["birth_id"], req["request_id"]),
        )
        EnrollmentBirth().append_event(
            birth_id=birth["birth_id"],
            agent_id=produce_aid,
            machine_id=birth.get("machine_id"),
            principal_id=req["principal_id"],
            event_type="join_produced",
            summary="Local agent produced credentials after Head Operator allow",
            working_on=req["working_on"],
            payload={
                "request_id": rid,
                "grant_id": str(grant["grant_id"]),
                "credential_path": str(cred_path),
                "operator_principal_id": local_doc.get("operator_principal_id"),
                "decided_by_agent": local_doc.get("decided_by_agent"),
            },
        )
        sev = _sentinel(
            request_id=rid,
            grant_id=str(grant["grant_id"]),
            event_type="join_produced",
            actor=produce_aid,
            decision="allow",
            summary=f"Local produce complete; birth {birth['birth_id']}",
            payload={
                "principal_id": req["principal_id"],
                "operator_principal_id": local_doc.get("operator_principal_id"),
                "decided_by_agent": local_doc.get("decided_by_agent"),
                "agent_id": produce_aid,
                "machine_id": birth.get("machine_id"),
                "birth_id": birth["birth_id"],
                "credential_path": str(cred_path),
                "policy_version": POLICY_VERSION,
            },
        )
        return {
            "ok": True,
            "status": "produced",
            "request_id": rid,
            "grant_id": str(grant["grant_id"]),
            "birth_id": birth["birth_id"],
            "agent_id": produce_aid,
            "principal_id": req["principal_id"],
            "operator_principal_id": local_doc.get("operator_principal_id"),
            "decided_by_agent": local_doc.get("decided_by_agent"),
            "working_on": req["working_on"],
            "credential_path": str(cred_path),
            "discovery_url": local_doc["discovery_url"],
            "organ_bearer_installed": False,
            "full_identity": birth.get("full_identity"),
            "sentinel_event_id": sev.get("event_id"),
            "policy_version": POLICY_VERSION,
            "claim_via": claim_via,
            "next_chores": [
                "whoami / join-help",
                "Prove organs no-auth → 401",
                "If need auth 200: Head Operator issues scoped Bearer separately",
            ],
        }

    def whoami(self, tool_type: str = "cursor", credential_dir: str | None = None) -> dict[str, Any]:
        """Local identity without secrets."""
        aid = get_unique_agent_id(tool_type)
        info = get_machine_info()
        cred_path = Path(
            credential_dir
            or os.environ.get("MAAT_CREDENTIAL_DIR")
            or (Path.home() / ".maat")
        ).expanduser() / "credentials.json"
        cred = None
        if cred_path.is_file():
            try:
                cred = json.loads(cred_path.read_text(encoding="utf-8"))
            except Exception as e:  # noqa: BLE001
                cred = {"error": str(e)}
        birth = EnrollmentBirth().identity_card(agent_id=aid, tool_type=tool_type)
        safe_cred = None
        if isinstance(cred, dict) and not cred.get("error"):
            safe_cred = {
                k: cred.get(k)
                for k in (
                    "schema",
                    "policy_version",
                    "request_id",
                    "grant_id",
                    "birth_id",
                    "agent_id",
                    "principal_id",
                    "operator_principal_id",
                    "decided_by_agent",
                    "decided_by_principal",
                    "machine_id",
                    "os_user",
                    "working_on",
                    "ring",
                    "role",
                    "discovery_url",
                    "scopes",
                    "denied_scopes",
                    "allowed_organs",
                    "produced_at",
                    "organ_bearer",
                )
            }
        return {
            "ok": True,
            "schema": "maat.whoami.v0",
            "agent_id": aid,
            "machine_id": info.get("machine_id"),
            "hostname": info.get("hostname"),
            "os_user": info.get("user"),
            "workspace": {
                "root": info.get("workspace_root"),
                "slug": info.get("workspace_slug"),
            },
            "credentials": safe_cred,
            "birth": {
                "ok": birth.get("ok"),
                "birth_id": birth.get("birth_id"),
                "principal_id": birth.get("principal_id"),
                "working_on": birth.get("working_on"),
                "chronology_n": birth.get("chronology_n"),
            }
            if birth
            else None,
            "forbidden_reminder": [
                "Do not read .env.broker",
                "organ_bearer should be null until scoped tokens exist",
            ],
        }

    def sentinel_log(
        self,
        request_id: str | None = None,
        *,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        if request_id:
            rows = db.fetchall(
                """
                SELECT * FROM maat_join_sentinel_events
                WHERE request_id = %s::uuid
                ORDER BY occurred_at ASC
                LIMIT %s
                """,
                (request_id, limit),
            )
        else:
            rows = db.fetchall(
                """
                SELECT * FROM maat_join_sentinel_events
                ORDER BY occurred_at DESC
                LIMIT %s
                """,
                (limit,),
            )
        return [dict(r) for r in rows or []]
