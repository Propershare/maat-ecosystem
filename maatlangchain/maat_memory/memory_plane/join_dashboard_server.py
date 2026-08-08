#!/usr/bin/env python3
"""Join Dashboard HTTP API — localhost only.

Binds CLI join ritual to Hermes HTML dashboards.
Operator token stays on the server (from env / .env.broker) — never sent to the browser.

Usage:
  python3 -m maat_memory.memory_plane.join_dashboard_server [--port 8040]
  # or: maat_memory_plane.py join-dashboard-serve
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib import error as urllib_error
from urllib import request as urllib_request
from urllib.parse import parse_qs, urlparse

# maatlangchain on path
_ML = Path("/mnt/data_drive/maatlangchain")
if _ML.is_dir() and str(_ML) not in sys.path:
    sys.path.insert(0, str(_ML))

DASH_DIR = Path(
    "/mnt/data_drive/hermes/workflowware-backend/guard/dashboards"
).resolve()
MCP_REGISTRY_PATH = Path(
    "/mnt/data_drive/hermes/workflowware-backend/guard/config/mcp-registry.json"
)

OPERATOR_DECIDER = "operator_imhotep_dashboard"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8040
GUARD_BASE = "http://127.0.0.1:8013"
GUARD_TIMEOUT_SECONDS = 3
GUARD_MAX_RESPONSE_BYTES = 512 * 1024

ENTITIES_SCHEMA_PATH = Path(
    "/mnt/data_drive/hermes/research-artifacts/workflowware-template-operator-surface"
    "/schemas/entities.schema.json"
)

# Forbidden zones surfaced on every agent card / join review.
FORBIDDEN_PATHS = [
    ".env.broker",
    "broker/",
    "secrets/",
    "auth.json",
    "*.pem",
    "*.key",
    "~/.n8n/.env.broker",
    "MAAT_OPERATOR_TOKEN",
]

# Runtime prefix → human runtime label.
RUNTIME_LABELS = {
    "cursor": "Cursor Agent",
    "hermes": "Hermes Gateway",
    "opencode": "OpenCode Agent",
    "codex": "OpenAI Codex CLI",
    "claude": "Claude Code",
    "operator": "Operator Console",
    "isfet": "Isfet Counter-eye (test)",
}

# Display authority label → schema authority_tier enum
AUTHORITY_TIER_MAP = {
    "OPERATOR": "operator_approved",
    "TESTER": "tester",
    "MEMBER (INNER)": "member",
    "MEMBER (MIDDLE)": "member",
    "MEMBER (OUTER)": "member",
    "MEMBER IDENTITY ONLY": "member",
    "SCOPED WORKER": "scoped_worker",
    "SUBAGENT PARENT": "subagent_parent",
    "REVOKED": "revoked",
    "NO_GO": "no_go",
    "REQUESTER": "requester",
}


def _authority_tier_enum(label: str) -> str:
    return AUTHORITY_TIER_MAP.get((label or "").upper().strip(), "member")


def _short_agent_display(agent_id: str) -> str:
    if not agent_id:
        return "unknown"
    s = str(agent_id)
    for prefix in RUNTIME_LABELS:
        if s.lower().startswith(prefix + "_"):
            return prefix + " · " + s[len(prefix) + 1 :].replace("_", " ")
    return s


def _load_entities_schema() -> dict:
    try:
        return json.loads(ENTITIES_SCHEMA_PATH.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        return {"error": type(e).__name__, "detail": str(e), "path": str(ENTITIES_SCHEMA_PATH)}


def _validate_entity(entity: str, instance: dict) -> dict:
    """Validate instance against $defs[entity]. Returns {ok, errors[]}."""
    schema = _load_entities_schema()
    if schema.get("error"):
        return {"ok": False, "errors": [f"schema_load:{schema.get('error')}"]}
    defs = schema.get("$defs") or {}
    if entity not in defs:
        return {"ok": False, "errors": [f"unknown_entity:{entity}"]}
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        return {"ok": False, "errors": ["jsonschema_not_installed"]}
    wrapper = {"$defs": defs, **defs[entity]}
    errs = [
        {"path": "/".join(str(p) for p in e.absolute_path), "message": e.message}
        for e in Draft202012Validator(wrapper).iter_errors(instance)
    ]
    return {"ok": not errs, "errors": errs[:12], "entity": entity}


def _agent_schema_card(raw: dict) -> dict:
    """
    Build template-operator-surface $defs.agent card from fleet raw.
    Missing required WHERE fields → schema_status=unproven with named gaps (I1/I3).
    Never invent a fake cwd/workspace just to pass schema.
    """
    gaps: list[str] = []
    ws = raw.get("workspace_root_declared") or raw.get("workspace_root")
    cwd = raw.get("current_working_dir") or raw.get("cwd")
    if not ws:
        gaps.append("workspace_root")
    if not cwd:
        gaps.append("cwd")
    if not raw.get("last_seen"):
        gaps.append("last_seen")

    label = raw.get("authority_state") or "MEMBER IDENTITY ONLY"
    tier = _authority_tier_enum(label)
    reach = "reachable"
    if not raw.get("last_seen"):
        reach = "unproven"
    # stale window: 90s teaching case from template — use 5m for lab reality
    try:
        from datetime import datetime, timezone

        ts = str(raw.get("last_seen") or "")
        # tolerate "2026-07-28 21:18:33.009889+00:00"
        dt = datetime.fromisoformat(ts.replace(" ", "T"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        age = (datetime.now(timezone.utc) - dt).total_seconds()
        if age > 300:
            reach = "unreachable"
    except Exception:
        if raw.get("last_seen"):
            reach = "unproven"

    registered = list(raw.get("available_mcps") or raw.get("registered_mcps") or [])
    allowed = list(raw.get("requested_scopes") or raw.get("allowed_scopes") or ["manifest:read", "report:write"])
    denied = list(raw.get("denied_scopes") or ["broker:read", "organ:admin", "key:mint"])
    no_go = list(raw.get("no_go") or [])
    if raw.get("organ_bearer") is None:
        no_go = list(dict.fromkeys(no_go + ["scoped organ bearer"]))
    no_go = list(dict.fromkeys(no_go + ["subagent birth ritual"]))

    card = {
        "agent_id": raw.get("agent_id") or "unknown",
        "display_name": _short_agent_display(raw.get("agent_id") or ""),
        "crew_role": raw.get("role") or raw.get("crew_role") or "fleet_tester",
        "machine_id": raw.get("machine_id") or raw.get("hostname") or "unknown",
        "runtime": raw.get("runtime") or "unknown",
        "model_harness": raw.get("model_harness"),
        "workspace_root": ws or "",
        "cwd": cwd or "",
        "assigned_workflow": raw.get("assigned_workflow"),
        "current_chore": raw.get("working_on") or raw.get("current_chore"),
        "registered_mcps": registered,
        "authority_tier": tier,
        "allowed_scopes": allowed,
        "denied_scopes": denied,
        "subagent_authority": bool((raw.get("capabilities") or {}).get("can_spawn_subagents")),
        "subagent_count": int(raw.get("subagent_count") or 0),
        "artifacts_created": list(raw.get("artifacts_created") or []),
        "no_go": no_go,
        "last_seen": str(raw.get("last_seen") or ""),
        "reachability": reach,
        "birth_id": str(raw.get("birth_id")) if raw.get("birth_id") else None,
        "join_id": (raw.get("pending_join_ids") or [None])[0],
        "principal": raw.get("principal_id") or raw.get("principal"),
        "operator": raw.get("operator"),
        "git_branch": raw.get("git_branch"),
        "git_commit": raw.get("git_commit"),
        "forbidden_paths": list(raw.get("forbidden_paths") or FORBIDDEN_PATHS),
    }

    if gaps:
        return {
            "schema_status": "unproven",
            "schema_gaps": gaps,
            "schema_note": "Missing required WHERE/identity fields — card must not look fine (I3). Allow disabled until self-report.",
            "schema_card": None,
            "partial": card,
        }

    v = _validate_entity("agent", card)
    return {
        "schema_status": "proven" if v["ok"] else "failed",
        "schema_gaps": [e["message"] for e in (v.get("errors") or [])],
        "schema_card": card if v["ok"] else None,
        "partial": None if v["ok"] else card,
        "validation": v,
    }


def _join_schema_card(preview: dict, row: dict) -> dict:
    """Build $defs.join_request from join preview + row. Gaps named, never invented."""
    who = preview.get("who") or {}
    wants = preview.get("wants") or {}
    facts = preview.get("proven_facts") or {}
    gaps = []

    def fact_val(key):
        f = facts.get(key) or {}
        return f.get("value")

    # A path guessed from an agent id is display context, never proven WHERE.
    ws = fact_val("workspace_root_declared")
    cwd = fact_val("cwd")
    if not ws:
        gaps.append("workspace_root")
    if not cwd:
        gaps.append("cwd")

    if_allowed = list(preview.get("if_allowed_receives") or [])
    will_not = list(preview.get("if_allowed_does_NOT_receive") or [])
    if not if_allowed:
        gaps.append("if_allowed")
    if not will_not:
        gaps.append("will_not_be_granted")

    rid = str(preview.get("request_id") or row.get("request_id") or "")
    card = {
        "request_id": rid or "unknown",
        "agent_id": who.get("agent_id") or row.get("requesting_agent_id") or "unknown",
        "principal": who.get("principal_claimed") or row.get("principal_id") or "imhotep",
        "operator": who.get("operator"),
        "runtime": who.get("runtime") or "unknown",
        "model_harness": None,
        "machine_id": who.get("machine_id") or row.get("machine_id") or "unknown",
        "workspace_root": ws or "",
        "cwd": cwd or "",
        "git_branch": fact_val("git_branch"),
        "git_commit": fact_val("git_commit"),
        "requested_chore": wants.get("chore") or row.get("working_on") or "unspecified",
        "requested_scopes": list(wants.get("requested_scopes") or []),
        "requested_mcps": list(wants.get("requested_mcps") or []),
        "forbidden_paths_acknowledged": list(fact_val("forbidden_paths_acknowledged") or []),
        "if_allowed": if_allowed or ["membership identity"],
        "will_not_be_granted": will_not or ["master KA"],
        "risk_level": row.get("risk_level") or "unproven",
        "where_complete": not gaps,
        "registry_delta": preview.get("registry_delta"),
    }
    # Bind the decision to every field displayed in the canonical preview,
    # including grants, refusals, and registry deltas. The digest itself is
    # excluded from its input.
    decision_material = {
        "card": card,
        "requested_organs": list(wants.get("requested_organs") or []),
        "message": wants.get("message"),
        "expires_at": preview.get("expires_at"),
        "correlation_id": preview.get("correlation_id"),
    }
    digest_src = json.dumps(
        decision_material,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )
    card["request_digest"] = hashlib.sha256(digest_src.encode("utf-8")).hexdigest()

    if gaps:
        return {
            "schema_status": "unproven",
            "schema_gaps": gaps,
            "allow_disabled": True,
            "allow_disabled_reason": "WHERE incomplete or preview incomplete — " + ", ".join(gaps),
            "schema_card": None,
            "partial": card,
        }

    v = _validate_entity("join_request", card)
    return {
        "schema_status": "proven" if v["ok"] else "failed",
        "schema_gaps": [e["message"] for e in (v.get("errors") or [])],
        "allow_disabled": not v["ok"],
        "allow_disabled_reason": None if v["ok"] else "schema validation failed",
        "schema_card": card if v["ok"] else None,
        "partial": None if v["ok"] else card,
        "validation": v,
    }


def _decision_preflight(
    preview: dict, supplied_digest: object, *, allow: bool
) -> tuple[int, dict]:
    """Bind one decision to one rendered preview; fail closed on drift."""
    schema = preview.get("schema") or {}
    card = schema.get("schema_card") or schema.get("partial") or {}
    current_digest = card.get("request_digest")
    supplied = supplied_digest.strip() if isinstance(supplied_digest, str) else ""

    if not supplied:
        return 400, {
            "ok": False,
            "error": "request_digest_required",
            "hint": "Refresh the preview and submit the digest that was displayed.",
        }
    if not current_digest:
        return 409, {
            "ok": False,
            "error": "preview_digest_unavailable",
            "hint": "Decision disabled because the current item cannot be bound.",
        }
    if not hmac.compare_digest(supplied, str(current_digest)):
        return 409, {
            "ok": False,
            "error": "item_changed",
            "hint": "The request or decision context changed. Refresh and review again.",
            "current_request_digest": current_digest,
        }
    if allow and (
        schema.get("schema_status") != "proven" or schema.get("allow_disabled")
    ):
        return 409, {
            "ok": False,
            "error": "allow_disabled",
            "reason": schema.get("allow_disabled_reason")
            or "Join preview is not proven.",
            "schema_gaps": list(schema.get("schema_gaps") or []),
            "request_digest": current_digest,
        }
    return 200, {
        "ok": True,
        "request_digest": current_digest,
        "schema_status": schema.get("schema_status") or "unproven",
    }


def _mcp_schema_rows() -> list[dict]:
    """Flatten MCP registry into $defs.mcp rows."""
    reg = _load_mcp_registry()
    rows = []
    for host, m in (reg.get("machines") or {}).items():
        for t in m.get("mcp") or []:
            card = {
                "mcp_name": t.get("name") or "unknown",
                "machine_id": host,
                "scope_path": t.get("scope"),
                "risk_level": t.get("risk") or "unproven",
                "registration": t.get("status") or "unregistered",
                "owner": t.get("registered_by"),
                "registered_by": t.get("registered_by"),
                "allowed_agents": list(t.get("allowed_agents") or []),
                "forbidden_paths": list(m.get("forbidden_paths") or FORBIDDEN_PATHS),
                "last_used": t.get("last_used"),
                "note": t.get("note"),
            }
            v = _validate_entity("mcp", card)
            rows.append({
                "schema_status": "proven" if v["ok"] else "failed",
                "schema_card": card if v["ok"] else None,
                "partial": None if v["ok"] else card,
                "validation": v,
            })
    return rows


def _runtime_from_agent_id(agent_id: str) -> str:
    aid = (agent_id or "").lower()
    for prefix, label in RUNTIME_LABELS.items():
        if aid.startswith(prefix + "_") or aid == prefix:
            return label
    return "unknown runtime"


def _workspace_from_agent_id(agent_id: str) -> str:
    """Convention: cursor_<host>_<workspace-slug>. Best-effort guess only."""
    if not agent_id:
        return ""
    parts = agent_id.split("_")
    if len(parts) < 3:
        return ""
    # skip runtime + host, remainder is workspace slug
    slug = "_".join(parts[2:])
    if slug in {"data_drive", "datadrive"}:
        return "/mnt/data_drive"
    return f"/mnt/data_drive/{slug.replace('_', '-')}"


def _authority_state(birth: dict) -> tuple[str, str]:
    """Return (label, one-line explanation) for an alive agent."""
    role = (birth.get("role") or "").lower()
    ring = (birth.get("ring") or "").lower()
    # Every birth today has organ_bearer=null — scoped organs still NO_GO.
    if role in {"operator", "head_operator"}:
        return ("OPERATOR", "operator-approved · can decide join requests")
    if role in {"fleet_tester", "tester"}:
        return ("TESTER", "identity + report only · no organ authority")
    if ring == "inner":
        return ("MEMBER (inner)", "member identity · read-only canon ring")
    if ring == "middle":
        return ("MEMBER (middle)", "member identity · scholarship ring")
    if ring == "outer":
        return ("MEMBER (outer)", "member identity · outer ring · no organ bearer")
    return ("MEMBER IDENTITY ONLY", "membership recorded · no organ bearer")


def _load_mcp_registry() -> dict:
    try:
        return json.loads(MCP_REGISTRY_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {"schema": "tehuti.mcp_registry.v0", "machines": {}, "error": "file_missing", "path": str(MCP_REGISTRY_PATH)}
    except Exception as e:  # noqa: BLE001
        return {"schema": "tehuti.mcp_registry.v0", "machines": {}, "error": type(e).__name__, "detail": str(e)}


def _load_operator_token_from_broker() -> bool:
    """Load MAAT_OPERATOR_TOKEN into environ from broker files if unset."""
    if os.environ.get("MAAT_OPERATOR_TOKEN", "").strip():
        return True
    candidates = [
        Path.home() / ".n8n" / ".env.broker",
        Path("/mnt/data_drive/hermes") / ".env.broker",
        Path.home() / ".hermes" / ".env.broker",
        Path("/mnt/data_drive/hermes/docs/operator-only/MAAT_OPERATOR_TOKEN.env"),
    ]
    for p in candidates:
        if not p.is_file():
            continue
        try:
            for line in p.read_text(encoding="utf-8").splitlines():
                if line.startswith("MAAT_OPERATOR_TOKEN="):
                    val = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if val:
                        os.environ["MAAT_OPERATOR_TOKEN"] = val
                        return True
        except OSError:
            continue
    return False


def _guard_call(path: str, body: dict | None = None) -> tuple[int, dict]:
    """Authenticated server-side Guard call; token never reaches the browser."""
    token = (
        os.environ.get("TEHUTI_GUARD_TOKEN")
        or os.environ.get("MAAT_GUARD_TOKEN")
        or ""
    ).strip()
    if not token:
        return 0, {"ok": False, "error": "guard_token_not_loaded"}

    data = None if body is None else json.dumps(body).encode("utf-8")
    headers = {"Authorization": f"Bearer {token}"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib_request.Request(
        f"{GUARD_BASE}{path}",
        data=data,
        headers=headers,
        method="POST" if data is not None else "GET",
    )
    try:
        with urllib_request.urlopen(req, timeout=GUARD_TIMEOUT_SECONDS) as response:
            raw = response.read(GUARD_MAX_RESPONSE_BYTES + 1)
            if len(raw) > GUARD_MAX_RESPONSE_BYTES:
                return 0, {"ok": False, "error": "guard_response_too_large"}
            parsed = json.loads(raw.decode("utf-8"))
            if not isinstance(parsed, dict):
                return 0, {"ok": False, "error": "guard_invalid_response"}
            return int(response.status), parsed
    except urllib_error.HTTPError as exc:
        return int(exc.code), {"ok": False, "error": "guard_http_error"}
    except (urllib_error.URLError, TimeoutError, json.JSONDecodeError):
        return 0, {"ok": False, "error": "guard_unreachable"}


def _guard_health() -> dict:
    status, health = _guard_call("/health")
    if status != 200 or not health.get("ok"):
        return {
            "ok": False,
            "schema_status": "unproven",
            "organ": "tehuti-guard",
            "reason": health.get("error") or f"guard_http_{status}",
            "approve_disabled": True,
        }
    policy_status, policy = _guard_call("/policy-version")
    if policy_status != 200 or not policy.get("policy_version"):
        return {
            "ok": False,
            "schema_status": "unproven",
            "organ": "tehuti-guard",
            "reason": policy.get("error") or "guard_policy_unavailable",
            "approve_disabled": True,
        }
    return {
        "ok": True,
        "schema_status": "proven",
        "organ": "tehuti-guard",
        "service": health.get("service"),
        "version": health.get("version"),
        "policy_version": policy.get("policy_version"),
        "approve_disabled": False,
    }


def _guard_join_allow(preview: dict, reason: str, actor: str) -> dict:
    schema = preview.get("schema") or {}
    card = schema.get("schema_card") or {}
    digest = card.get("request_digest")
    who = preview.get("who") or {}
    status, decision = _guard_call(
        "/decision",
        {
            "machine_id": who.get("machine_id"),
            "actor": {"id": actor, "role": "head_operator"},
            "action": {
                "kind": "join_allow",
                "resource": f"maat_join_request:{preview.get('request_id')}",
                "risk": card.get("risk_level") or "medium",
                "metadata": {
                    "request_digest": digest,
                    "reason": reason,
                    "requested": preview.get("wants") or {},
                    "if_allowed": preview.get("if_allowed_receives") or [],
                    "will_not_be_granted": (
                        preview.get("if_allowed_does_NOT_receive") or []
                    ),
                },
            },
            "correlation_id": preview.get("correlation_id"),
        },
    )
    allowed = status == 200 and decision.get("decision") == "allow"
    return {
        "ok": allowed,
        "schema_status": "proven" if status == 200 else "unproven",
        "organ": "tehuti-guard",
        "decision": decision.get("decision"),
        "reason": decision.get("reason") or decision.get("error"),
        "policy_version": decision.get("policy_version"),
        "explanation_id": decision.get("explanation_id"),
        "approve_disabled": not allowed,
    }


def _ritual():
    from maat_memory.memory_plane import JoinRequestRitual

    return JoinRequestRitual()


def _json_default(obj):
    return str(obj)


class JoinDashboardHandler(BaseHTTPRequestHandler):
    server_version = "MaatJoinDashboard/0.1.1"

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _send(self, status: int, body: dict | list | str, content_type: str = "application/json") -> None:
        if isinstance(body, (dict, list)):
            data = json.dumps(body, indent=2, default=_json_default).encode("utf-8")
            content_type = "application/json"
        elif isinstance(body, str):
            data = body.encode("utf-8")
        else:
            data = body
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        # Local dashboards only
        self.send_header("Access-Control-Allow-Origin", f"http://{DEFAULT_HOST}:{self.server.server_port}")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", f"http://{DEFAULT_HOST}:{self.server.server_port}")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        qs = parse_qs(parsed.query)

        try:
            if path == "/health":
                has_tok = bool(os.environ.get("MAAT_OPERATOR_TOKEN", "").strip())
                return self._send(
                    200,
                    {
                        "ok": True,
                        "service": "maat-join-dashboard",
                        "policy_version": "maat-join@0.1.1",
                        "operator_token_loaded": has_tok,
                        "bind": "127.0.0.1-only",
                        "dashboards": {"mobile": "/mobile", "lab": "/lab"},
                    },
                )

            if path == "/api/guard/health":
                guard = _guard_health()
                return self._send(200 if guard.get("ok") else 503, guard)

            if path in ("/", "/index"):
                return self._send(
                    200,
                    "<!doctype html><html><body style='background:#0a0a0f;color:#d4d4d8;"
                    "font-family:system-ui;padding:40px'>"
                    "<h1 style='color:#c9a84c'>Maat Join Dashboard</h1>"
                    "<p>Localhost only. Phone client app comes later.</p>"
                    "<ul>"
                    "<li><a style='color:#c9a84c' href='/mobile'>Mobile Gateway</a></li>"
                    "<li><a style='color:#c9a84c' href='/lab'>Lab Command</a></li>"
                    "<li><a style='color:#c9a84c' href='/mark'>DESIGN-MARK (your picture)</a></li>"
                    "<li><a style='color:#c9a84c' href='/health'>/health</a></li>"
                    "</ul></body></html>",
                    "text/html; charset=utf-8",
                )

            if path == "/mobile":
                return self._serve_file(DASH_DIR / "mobile-gateway.html")
            if path == "/lab":
                return self._serve_file(DASH_DIR / "lab-command-dashboard.html")
            if path in ("/mark", "/design-mark"):
                return self._serve_file(DASH_DIR / "refs" / "DESIGN-MARK.jpg")
            if path.startswith("/static/"):
                name = path[len("/static/") :]
                if ".." in name or name.startswith("/"):
                    return self._send(400, {"error": "bad_path"})
                return self._serve_file(DASH_DIR / name)

            if path == "/api/whoami":
                return self._send(200, _ritual().whoami())

            if path == "/api/help":
                from maat_memory.memory_plane import constitutional_help

                topic = (qs.get("topic") or [None])[0]
                return self._send(200, constitutional_help(topic))

            if path == "/api/join/inbox":
                status = (qs.get("status") or ["pending"])[0]
                rows = _ritual().inbox(principal_id="imhotep", status=status, limit=50)
                return self._send(200, {"ok": True, "count": len(rows), "inbox": rows})

            if path == "/api/join/sentinel":
                rid = (qs.get("id") or [None])[0]
                limit = int((qs.get("limit") or ["30"])[0])
                rows = _ritual().sentinel_log(rid, limit=limit)
                return self._send(200, {"ok": True, "events": rows})

            if path == "/api/join/status":
                rid = (qs.get("id") or [None])[0]
                if not rid:
                    return self._send(400, {"ok": False, "error": "id_required"})
                return self._send(200, _ritual().status(rid))

            if path == "/api/join/births":
                from maat_memory.memory_plane import EnrollmentBirth

                rows = EnrollmentBirth().list_alive(limit=50)
                return self._send(200, {"ok": True, "count": len(rows), "births": rows})

            if path == "/api/join/stats":
                return self._send(200, self._stats())

            if path == "/api/fleet/agents":
                return self._send(200, self._fleet_agents())

            if path == "/api/fleet/machines":
                return self._send(200, self._fleet_machines())

            if path == "/api/fleet/mcp_registry":
                base = _load_mcp_registry()
                return self._send(200, {
                    "ok": True,
                    **base,
                    "schema_version": "template-operator-surface@0.1",
                    "schema_rows": _mcp_schema_rows(),
                })

            if path == "/api/fleet/join_preview":
                rid = (qs.get("id") or [None])[0]
                if not rid:
                    return self._send(400, {"ok": False, "error": "id_required"})
                return self._send(200, self._join_preview(rid))

            if path == "/api/fleet/schema_validate":
                agents = self._fleet_agents()
                mcp_rows = _mcp_schema_rows()
                agent_stats = {"proven": 0, "unproven": 0, "failed": 0}
                for a in agents.get("agents") or []:
                    st = ((a.get("schema") or {}).get("schema_status") or "unproven")
                    agent_stats[st] = agent_stats.get(st, 0) + 1
                mcp_stats = {"proven": 0, "unproven": 0, "failed": 0}
                for r in mcp_rows:
                    st = r.get("schema_status") or "unproven"
                    mcp_stats[st] = mcp_stats.get(st, 0) + 1
                # pending joins
                pending = (_ritual().inbox(status="pending", limit=20) or [])
                join_stats = {"proven": 0, "unproven": 0, "failed": 0}
                for p in pending:
                    prev = self._join_preview(str(p.get("request_id")))
                    st = ((prev.get("schema") or {}).get("schema_status") or "unproven")
                    join_stats[st] = join_stats.get(st, 0) + 1
                return self._send(200, {
                    "ok": True,
                    "schema_version": "template-operator-surface@0.1",
                    "schema_path": str(ENTITIES_SCHEMA_PATH),
                    "doctrine": agents.get("doctrine"),
                    "tally": {
                        "agents": agent_stats,
                        "mcp": mcp_stats,
                        "join_requests": join_stats,
                    },
                    "note": "I2: unproven is named via schema_gaps on each card — never a naked percentage.",
                    "implemented": False,
                    "evals_run": False,
                })

            return self._send(404, {"error": "not_found", "path": path})
        except Exception as e:  # noqa: BLE001
            return self._send(500, {"ok": False, "error": type(e).__name__, "detail": str(e)})

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length) if length else b"{}"
            body = json.loads(raw.decode("utf-8") or "{}")
        except Exception as e:  # noqa: BLE001
            return self._send(400, {"ok": False, "error": "invalid_json", "detail": str(e)})

        try:
            if path == "/api/join/ask":
                work = (body.get("working_on") or "").strip()
                # ask-join self-report v0.2 pass-through
                self_report_kwargs = {
                    "runtime": body.get("runtime"),
                    "workspace_root": body.get("workspace_root"),
                    "cwd": body.get("cwd"),
                    "git_branch": body.get("git_branch"),
                    "git_commit": body.get("git_commit"),
                    "requested_scopes": body.get("requested_scopes"),
                    "requested_mcps": body.get("requested_mcps"),
                    "available_mcps": body.get("available_mcps"),
                    "forbidden_paths_acknowledged": body.get("forbidden_paths_acknowledged"),
                }
                if not work:
                    return self._send(400, {"ok": False, "error": "working_on_required"})
                out = _ritual().ask(
                    working_on=work,
                    principal_id=body.get("principal_id") or "imhotep",
                    role=body.get("role") or "fleet_tester",
                    ring=body.get("ring") or "outer",
                    organs=body.get("organs"),
                    message=body.get("message"),
                    agent_id=body.get("agent_id"),
                    tool_type=body.get("tool_type") or "cursor",
                    machine_id=body.get("machine_id"),
                    hostname=body.get("hostname"),
                    **{k: v for k, v in self_report_kwargs.items() if v is not None},
                )
                return self._send(200 if out.get("ok") else 400, out)

            if path == "/api/join/decide":
                if not os.environ.get("MAAT_OPERATOR_TOKEN", "").strip():
                    return self._send(
                        403,
                        {
                            "ok": False,
                            "error": "operator_token_not_loaded",
                            "hint": "Set MAAT_OPERATOR_TOKEN or put it in .env.broker; restart serve",
                        },
                    )
                rid = body.get("request_id") or body.get("id")
                if not rid:
                    return self._send(400, {"ok": False, "error": "request_id_required"})
                allow = bool(body.get("allow"))
                deny = bool(body.get("deny"))
                if allow == deny:
                    # default: allow flag explicit
                    if "allow" not in body and "deny" not in body:
                        return self._send(400, {"ok": False, "error": "pass allow or deny"})
                    if deny:
                        allow = False
                reason = (body.get("reason") or "").strip()
                if not reason:
                    return self._send(400, {"ok": False, "error": "reason_required"})
                preview = self._join_preview(str(rid))
                if not preview.get("ok"):
                    return self._send(
                        404 if preview.get("error") == "not_found" else 409,
                        preview,
                    )
                preflight_status, preflight = _decision_preflight(
                    preview,
                    body.get("request_digest"),
                    allow=allow,
                )
                if not preflight.get("ok"):
                    return self._send(preflight_status, preflight)
                guard_receipt = None
                if allow:
                    guard_receipt = _guard_join_allow(
                        preview,
                        reason,
                        body.get("decided_by_agent") or OPERATOR_DECIDER,
                    )
                    if not guard_receipt.get("ok"):
                        return self._send(
                            503
                            if guard_receipt.get("schema_status") == "unproven"
                            else 409,
                            {
                                "ok": False,
                                "error": "guard_refused",
                                "hint": (
                                    "Tehuti Guard did not allow this exact join. "
                                    "No authority changed."
                                ),
                                "guard": guard_receipt,
                            },
                        )
                out = _ritual().decide(
                    rid,
                    allow=allow,
                    reason=reason,
                    decided_by_agent=body.get("decided_by_agent") or OPERATOR_DECIDER,
                    operator_token=os.environ.get("MAAT_OPERATOR_TOKEN"),
                    operator_principal_id=body.get("operator_principal_id") or "imhotep",
                    request_digest=preflight["request_digest"],
                )
                if isinstance(out, dict) and guard_receipt:
                    out["guard"] = guard_receipt
                # provision_code returned only to localhost operator UI — never log full code here
                return self._send(200 if out.get("ok") else 400, out)

            return self._send(404, {"error": "not_found", "path": path})
        except Exception as e:  # noqa: BLE001
            return self._send(500, {"ok": False, "error": type(e).__name__, "detail": str(e)})

    def _serve_file(self, path: Path) -> None:
        if not path.is_file():
            return self._send(404, {"error": "file_not_found", "path": str(path)})
        data = path.read_bytes()
        ctype = "text/html; charset=utf-8"
        if path.suffix == ".js":
            ctype = "application/javascript; charset=utf-8"
        elif path.suffix == ".css":
            ctype = "text/css; charset=utf-8"
        elif path.suffix == ".png":
            ctype = "image/png"
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _fleet_agents(self) -> dict:
        """Enriched per-agent cards from EnrollmentBirth + inbox/sentinel context +
        v0.2 self-report facts pulled from the latest join request for each agent."""
        from maat_memory.memory_plane import EnrollmentBirth
        from maat_memory.memory_plane import db as _db

        births = EnrollmentBirth().list_alive(limit=100)
        r = _ritual()
        pending = r.inbox(status="pending", limit=100) or []
        events = r.sentinel_log(limit=200) or []

        # v0.2: for every alive agent, pull the most recent join request row so the
        # UI can show the *proven* cwd/git/workspace instead of guessing.
        aids = [b.get("agent_id") for b in (births or []) if b.get("agent_id")]
        self_report_by_agent: dict[str, dict] = {}
        if aids:
            try:
                rows = _db.fetchall(
                    """
                    SELECT DISTINCT ON (requesting_agent_id)
                           requesting_agent_id, workspace_root, runtime, cwd,
                           git_branch, git_commit, requested_scopes, requested_mcps,
                           available_mcps, forbidden_paths_acknowledged,
                           identity_snapshot, created_at
                    FROM maat_join_requests
                    WHERE requesting_agent_id = ANY(%s)
                    ORDER BY requesting_agent_id, created_at DESC
                    """,
                    (aids,),
                )
                for row in rows or []:
                    d = dict(row)
                    snap = d.get("identity_snapshot") or {}
                    sr = (snap or {}).get("self_report") if isinstance(snap, dict) else None
                    if isinstance(sr, dict):
                        for k in ("runtime", "cwd", "git_branch", "git_commit",
                                  "requested_scopes", "requested_mcps",
                                  "available_mcps", "forbidden_paths_acknowledged"):
                            if d.get(k) is None:
                                d[k] = sr.get(k)
                        d["workspace_mismatch"] = bool(sr.get("workspace_mismatch"))
                    self_report_by_agent[d["requesting_agent_id"]] = d
            except Exception:
                # older schema — just leave self_report_by_agent empty
                pass

        # last-seen per agent from Sentinel actor events
        last_seen: dict[str, str] = {}
        for e in events:
            actor = e.get("actor") or ""
            ts = e.get("occurred_at")
            if actor and ts and actor not in last_seen:
                last_seen[actor] = str(ts)

        # index pending requests by agent
        pending_by_agent: dict[str, list[dict]] = {}
        for p in pending:
            aid = p.get("requesting_agent_id") or ""
            pending_by_agent.setdefault(aid, []).append(p)

        agents = []
        for b in births:
            aid = b.get("agent_id") or ""
            label, why = _authority_state(b)
            hostname = (b.get("machine_id") or "").split("-", 1)[0] or "unknown"
            sr = self_report_by_agent.get(aid) or {}
            proven_runtime = sr.get("runtime")
            proven_ws = sr.get("workspace_root")
            proven_cwd = sr.get("cwd")
            proven_gb = sr.get("git_branch")
            proven_gc = sr.get("git_commit")
            # only truly "present" if agent actually self-reported at least one v0.2 field
            has_self_report = any([
                proven_cwd, proven_gb, proven_gc,
                sr.get("requested_scopes"), sr.get("requested_mcps"),
                sr.get("available_mcps"), sr.get("forbidden_paths_acknowledged"),
            ])
            agents.append({
                "agent_id": aid,
                "runtime": proven_runtime or _runtime_from_agent_id(aid),
                "runtime_proven": bool(proven_runtime and has_self_report),
                "machine_id": b.get("machine_id"),
                "hostname": hostname,
                "principal_id": b.get("principal_id") or "imhotep",
                "os_user": b.get("os_user"),
                "birth_id": b.get("birth_id"),
                "invite_id": b.get("invite_id"),
                "role": b.get("role"),
                "ring": b.get("ring"),
                "working_on": b.get("working_on"),
                "born_at": str(b.get("born_at") or ""),
                "authority_state": label,
                "authority_note": why,
                "authority_tier": _authority_tier_enum(label),
                "organ_bearer": None,  # NO_GO across fleet today
                # v0.2 proven-vs-inferred workspace fields
                "workspace_root_declared": proven_ws,
                "workspace_root_observed": (sr.get("identity_snapshot") or {}).get("self_report", {}).get("workspace_root_observed") if isinstance(sr.get("identity_snapshot"), dict) else None,
                "workspace_mismatch": bool(sr.get("workspace_mismatch")),
                "workspace_root_guess": _workspace_from_agent_id(aid),
                "current_working_dir": proven_cwd,
                "git_branch": proven_gb,
                "git_commit": proven_gc,
                "requested_scopes": sr.get("requested_scopes"),
                "requested_mcps": sr.get("requested_mcps"),
                "available_mcps": sr.get("available_mcps"),
                "forbidden_paths_acknowledged": sr.get("forbidden_paths_acknowledged"),
                "self_report_present": has_self_report,
                "subagent_count": 0,            # v0.2 — subagent birth ritual NO_GO
                "last_seen": last_seen.get(aid),
                "pending_join_ids": [p.get("request_id") for p in pending_by_agent.get(aid, [])],
                "forbidden_paths": FORBIDDEN_PATHS,
                "capabilities": {
                    "can_act_on_organs": False,
                    "can_report": True,
                    "can_spawn_subagents": False,
                },
            })
            # template-operator-surface@0.1 schema projection (Slice A)
            agents[-1]["schema"] = _agent_schema_card(agents[-1])
        return {
            "ok": True,
            "count": len(agents),
            "agents": agents,
            "schema_version": "template-operator-surface@0.1",
            "doctrine": (
                "An agent is not just alive — it is alive somewhere, under someone, "
                "inside a workspace, with specific tools, scopes, limits, and evidence."
            ),
        }

    def _fleet_machines(self) -> dict:
        from maat_memory.memory_plane import EnrollmentBirth

        births = EnrollmentBirth().list_alive(limit=200) or []
        r = _ritual()
        pending = r.inbox(status="pending", limit=200) or []
        reg = _load_mcp_registry().get("machines") or {}

        by_host: dict[str, dict] = {}
        for b in births:
            host = (b.get("machine_id") or "").split("-", 1)[0] or "unknown"
            m = by_host.setdefault(host, {
                "hostname": host,
                "machine_id_examples": set(),
                "agents_alive": 0,
                "agents": [],
                "pending_joins": 0,
                "workspace_roots": set(),
            })
            m["agents_alive"] += 1
            m["machine_id_examples"].add(b.get("machine_id"))
            m["agents"].append(b.get("agent_id"))
            ws = _workspace_from_agent_id(b.get("agent_id") or "")
            if ws:
                m["workspace_roots"].add(ws)

        for p in pending:
            host = (p.get("hostname") or (p.get("machine_id") or "").split("-", 1)[0] or "unknown")
            m = by_host.setdefault(host, {
                "hostname": host, "machine_id_examples": set(),
                "agents_alive": 0, "agents": [],
                "pending_joins": 0, "workspace_roots": set(),
            })
            m["pending_joins"] += 1

        result = []
        for host, m in by_host.items():
            reg_row = reg.get(host) or {}
            mcp = reg_row.get("mcp") or []
            result.append({
                "hostname": host,
                "role": reg_row.get("role") or ("organ_host" if host == "staydangerous" else "unknown"),
                "operator": reg_row.get("operator") or "imhotep",
                "status": "online",
                "agents_alive": m["agents_alive"],
                "agents": m["agents"],
                "pending_joins": m["pending_joins"],
                "subagent_count": 0,
                "machine_id_examples": sorted(x for x in m["machine_id_examples"] if x),
                "workspace_roots": sorted(m["workspace_roots"]) or reg_row.get("workspace_roots") or [],
                "forbidden_paths": reg_row.get("forbidden_paths") or FORBIDDEN_PATHS,
                "mcp_registered": [x["name"] for x in mcp if x.get("status") == "registered"],
                "mcp_blocked":    [x["name"] for x in mcp if x.get("status") == "blocked"],
                "mcp_denied":     [x["name"] for x in mcp if x.get("status") == "denied"],
                "organ_authority": {
                    "master_token_server_side": bool(os.environ.get("MAAT_OPERATOR_TOKEN", "").strip()),
                    "scoped_organ_bearers_issued": 0,
                    "state": "NO_GO_scoped",
                },
                "nogo": [
                    "unsupervised fleet",
                    "subagent birth ritual",
                    "payload hash oracle",
                    "gateway auto-notify (Discord)",
                    "same-user broker debt",
                ],
            })
        return {"ok": True, "count": len(result), "machines": result}

    def _join_preview(self, request_id: str) -> dict:
        """Answer: 'If I click Allow, what does the agent receive?'"""
        r = _ritual()
        s = r.status(request_id)
        row = s.get("request") if isinstance(s, dict) else None
        if not row:
            # inbox fallback (also carries self-report v0.2 fields)
            for p in r.inbox(status="pending", limit=100) or []:
                if str(p.get("request_id")) == str(request_id):
                    row = p
                    break
        if not row:
            return {"ok": False, "error": "not_found", "request_id": request_id}

        def _jl(v):
            if v is None:
                return []
            if isinstance(v, str):
                try:
                    return json.loads(v)
                except Exception:
                    return [v]
            return list(v)

        organs = _jl(row.get("requested_organs") or row.get("organs"))
        req_scopes = _jl(row.get("requested_scopes"))
        req_mcps = _jl(row.get("requested_mcps"))
        avail_mcps = _jl(row.get("available_mcps"))
        forbidden_ack = _jl(row.get("forbidden_paths_acknowledged"))

        agent_id = row.get("requesting_agent_id") or ""
        host = row.get("hostname") or (row.get("machine_id") or "").split("-", 1)[0]
        ws_declared = row.get("workspace_root_declared") or row.get("workspace_root")
        ws_observed = row.get("workspace_root_observed")
        cwd = row.get("cwd")
        # Prefer explicit cwd; else use identity_snapshot workspace paths already
        # reported by the agent (evidence, not invented guesses from agent_id).
        if not cwd:
            snap = row.get("identity_snapshot") or {}
            if isinstance(snap, str):
                try:
                    snap = json.loads(snap)
                except Exception:
                    snap = {}
            if isinstance(snap, dict):
                ws_snap = snap.get("workspace") if isinstance(snap.get("workspace"), dict) else {}
                sr = snap.get("self_report") if isinstance(snap.get("self_report"), dict) else {}
                cwd = (
                    ws_snap.get("working_directory")
                    or ws_snap.get("project_path")
                    or ws_snap.get("root")
                    or sr.get("cwd")
                    or None
                )
        git_branch = row.get("git_branch")
        git_commit = row.get("git_commit")
        runtime_val = row.get("runtime") or _runtime_from_agent_id(agent_id)
        workspace_mismatch = bool(row.get("workspace_mismatch"))

        # tri-state proven / unreported / mismatch on each self-report field
        def _prov(val, mismatch=False):
            if mismatch:
                return {"value": val, "state": "mismatch"}
            if val is None or val == "":
                return {"value": None, "state": "unreported"}
            return {"value": val, "state": "proven"}

        proven_facts = {
            "runtime": _prov(runtime_val if row.get("runtime") else None),
            "workspace_root_declared": _prov(ws_declared, mismatch=workspace_mismatch),
            "workspace_root_observed": _prov(ws_observed),
            "cwd": _prov(cwd),
            "git_branch": _prov(git_branch),
            "git_commit": _prov(git_commit),
            "forbidden_paths_acknowledged": _prov(forbidden_ack if forbidden_ack else None),
        }

        # registry delta: what did the agent request vs what does the registry say?
        reg = _load_mcp_registry().get("machines") or {}
        host_reg = reg.get(host) or {}
        mcp_index = {m.get("name"): m for m in (host_reg.get("mcp") or [])}

        def _mcp_state(name: str):
            entry = mcp_index.get(name)
            if entry is None:
                return {"name": name, "state": "unregistered", "risk": "unknown",
                        "note": "not in machine MCP registry"}
            s = (entry.get("status") or "unknown").lower()
            return {"name": name, "state": s, "risk": entry.get("risk"),
                    "scope": entry.get("scope"), "note": entry.get("note")}

        req_mcp_delta = [_mcp_state(n) for n in req_mcps]

        allowed_scope_defaults = {
            "manifest:read", "auth:test", "report:write", "join:ring",
        }
        req_scope_delta = []
        for scope in req_scopes:
            if scope in allowed_scope_defaults:
                req_scope_delta.append({"name": scope, "state": "allowed_default"})
            else:
                req_scope_delta.append({"name": scope, "state": "unknown_needs_review"})

        acked = set(forbidden_ack or [])
        forbidden_ack_delta = []
        for path in FORBIDDEN_PATHS:
            forbidden_ack_delta.append({
                "path": path,
                "acknowledged": path in acked,
            })

        out = {
            "ok": True,
            "request_id": row.get("request_id"),
            "doctrine": (
                "An agent is not just alive — it is alive somewhere, under someone, "
                "inside a workspace, with specific tools, scopes, limits, and evidence."
            ),
            "who": {
                "agent_id": agent_id,
                "runtime": runtime_val,
                "machine_id": row.get("machine_id"),
                "hostname": host,
                "os_user": row.get("os_user"),
                "principal_claimed": row.get("principal_id"),
                # backward-compat guess (used when unreported)
                "workspace_root_guess": _workspace_from_agent_id(agent_id),
            },
            "proven_facts": proven_facts,
            "wants": {
                "chore": row.get("working_on"),
                "ring": row.get("requested_ring"),
                "role": row.get("requested_role"),
                "requested_organs": organs,
                "requested_scopes": req_scopes,
                "requested_mcps": req_mcps,
                "available_mcps": avail_mcps,
                "message": row.get("message"),
            },
            "registry_delta": {
                "mcps": req_mcp_delta,
                "scopes": req_scope_delta,
                "forbidden_ack": forbidden_ack_delta,
            },
            "if_allowed_receives": [
                "membership identity (join.produced)",
                "local ~/.maat/credentials.json (birth_id + grant_id + agent_id + principal)",
                "manifest read + auth test rights (join ring)",
                f"role={row.get('requested_role') or '—'} / ring={row.get('requested_ring') or '—'}",
                "one-time provision code shown to operator (agent runs join-produce --code …)",
            ],
            "if_allowed_does_NOT_receive": [
                "organ bearer token (scoped organs are NO_GO across fleet today)",
                "broker env access (.env.broker forbidden by design)",
                "master KA / MAAT_OPERATOR_TOKEN",
                "subagent authority (subagent birth ritual not implemented)",
                "direct Postgres DSN or filesystem write outside workspace",
                "any MCP marked 'blocked' or 'denied' in the machine registry",
            ],
            "expires_at": str(row.get("expires_at") or ""),
            "correlation_id": row.get("correlation_id"),
            "forbidden_paths": FORBIDDEN_PATHS,
            "schema_version": "template-operator-surface@0.1",
        }
        out["schema"] = _join_schema_card(out, row)
        return out

    def _stats(self) -> dict:
        r = _ritual()
        pending = r.inbox(status="pending", limit=100)
        denied = r.inbox(status="denied", limit=100)
        allowed = r.inbox(status="allowed", limit=100)
        produced = r.inbox(status="produced", limit=100)
        events = r.sentinel_log(limit=40)
        from maat_memory.memory_plane import EnrollmentBirth

        births = EnrollmentBirth().list_alive(limit=100)
        return {
            "ok": True,
            "pending": len(pending),
            "denied": len(denied),
            "allowed": len(allowed),
            "produced": len(produced),
            "births_alive": len(births),
            "inbox_preview": pending[:10],
            "recent_events": events[:15],
            "operator_token_loaded": bool(os.environ.get("MAAT_OPERATOR_TOKEN", "").strip()),
            "policy_version": "maat-join@0.1.1",
        }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Maat Join Dashboard (localhost)")
    ap.add_argument("--host", default=DEFAULT_HOST)
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = ap.parse_args(argv)

    if args.host not in ("127.0.0.1", "localhost"):
        print(
            json.dumps(
                {
                    "ok": False,
                    "error": "host_must_be_localhost",
                    "hint": "Dashboards stay on 127.0.0.1 until phone client is built",
                }
            ),
            file=sys.stderr,
        )
        return 2

    loaded = _load_operator_token_from_broker()
    try:
        httpd = ThreadingHTTPServer((args.host, args.port), JoinDashboardHandler)
    except OSError as e:
        print(
            json.dumps(
                {
                    "ok": False,
                    "error": "address_already_in_use",
                    "detail": str(e),
                    "hint": (
                        f"Dashboard likely already running at http://{args.host}:{args.port}/ "
                        f"(mobile / lab). Open that URL, or: fuser -k {args.port}/tcp && "
                        "retry, or --port 8041"
                    ),
                    "mobile": f"http://{args.host}:{args.port}/mobile",
                    "lab": f"http://{args.host}:{args.port}/lab",
                    "health": f"http://{args.host}:{args.port}/health",
                },
                indent=2,
            ),
            file=sys.stderr,
        )
        return 98
    print(
        json.dumps(
            {
                "ok": True,
                "serving": f"http://{args.host}:{args.port}/",
                "mobile": f"http://{args.host}:{args.port}/mobile",
                "lab": f"http://{args.host}:{args.port}/lab",
                "operator_token_loaded": loaded,
                "law": "Operator token never sent to browser; decide uses server env",
            },
            indent=2,
        )
    )
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
