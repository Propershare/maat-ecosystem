#!/usr/bin/env python3
"""
Maat Memory MCP Server — The Memory Organ
Standalone MCP server for the Ka Architecture memory system.
Wraps maat_memory (Postgres backend) as a dedicated organ.

Any Ka body, agent, or framework can connect directly to memory
without going through Tehuti Core.
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("maat_memory.log"),
        logging.StreamHandler(sys.stderr),
    ],
)
log = logging.getLogger("maat_memory_mcp")

# Initialize FastMCP server
mcp = FastMCP("Maat Memory")

# Workspace root — env-driven, portable
from pathlib import Path as _PathForSetup

_workspace_root = os.environ.get("MAAT_WORKSPACE_ROOT")
if _workspace_root:
    WORKSPACE_ROOT = _PathForSetup(_workspace_root).expanduser()
else:
    _here = _PathForSetup(__file__).resolve()
    WORKSPACE_ROOT = None
    for _p in [_here] + list(_here.parents):
        if (_p / "maatlangchain").is_dir():
            WORKSPACE_ROOT = _p
            break
    if WORKSPACE_ROOT is None:
        WORKSPACE_ROOT = _PathForSetup.home() / ".n8n"

MAATLANGCHAIN_PATH = WORKSPACE_ROOT / "maatlangchain"

# Add maatlangchain to path
if str(MAATLANGCHAIN_PATH) not in sys.path:
    sys.path.insert(0, str(MAATLANGCHAIN_PATH))

# Load database URL
from maat_memory.paths import get_pgvector_db_url

PGVECTOR_DB_URL = get_pgvector_db_url()
if PGVECTOR_DB_URL:
    os.environ["PGVECTOR_DB_URL"] = PGVECTOR_DB_URL
    log.info("✅ Database URL loaded")
else:
    log.warning("⚠️  PGVECTOR_DB_URL not found — memory will be unavailable")


# --- Shared memory instance ---

_memory = None
_memory_error = None


def _get_memory():
    """Lazy-load MaatMemory singleton."""
    global _memory, _memory_error
    if _memory is not None:
        return _memory
    if _memory_error:
        raise _memory_error
    try:
        from maat_memory import MaatMemory
        _memory = MaatMemory()
        log.info("✅ MaatMemory connected")
        return _memory
    except Exception as e:
        _memory_error = e
        log.error(f"❌ MaatMemory init failed: {e}")
        raise


def _agent_id(agent: Optional[str] = None) -> str:
    """Resolve agent ID for read helpers (may fall back)."""
    if agent and str(agent).strip():
        return str(agent).strip()
    try:
        from maat_memory import get_unique_agent_id
        return get_unique_agent_id("maat_memory_mcp")
    except Exception:
        return "maat_memory_mcp"


def _require_agent(agent: Optional[str]) -> str:
    """Justice: every write must carry a non-empty agent for attribution."""
    if agent is None or not str(agent).strip():
        raise ValueError(
            "agent is required and must be non-empty "
            "(Justice — attribution; use e.g. cursor_staydangerous)"
        )
    return str(agent).strip()


# ============================================================
# STORE — Write to memory
# ============================================================

@mcp.tool()
async def memory_log_conversation(
    agent: str,
    role: str,
    content: str,
    session_id: Optional[str] = None,
    metadata_json: Optional[str] = None,
) -> str:
    """
    Log a conversation turn to memory.

    Args:
        agent: Agent identifier (required, non-empty; e.g. 'cursor_staydangerous')
        role: Message role (user, assistant, system)
        content: Message content
        session_id: Optional session ID to associate with
        metadata_json: Optional JSON object of extra metadata
    """
    try:
        agent = _require_agent(agent)
        mem = _get_memory()
        meta = json.loads(metadata_json) if metadata_json else {}
        role_l = (role or "user").lower()
        if role_l == "user":
            user_query, agent_response = content, ""
        elif role_l in ("assistant", "system"):
            user_query, agent_response = "", content
        else:
            user_query, agent_response = f"[{role}] {content}", ""
        if session_id:
            meta["session_id"] = session_id
        cid = mem.log_conversation(
            agent,
            user_query,
            agent_response,
            metadata=meta or None,
        )
        return json.dumps({"ok": True, "conversation_id": cid, "agent": agent})
    except Exception as e:
        return f"❌ {e}"


@mcp.tool()
async def memory_log_task(
    agent: str,
    title: str,
    description: str,
    status: str = "pending",
    priority: str = "medium",
    related_files_json: Optional[str] = None,
) -> str:
    """
    Log a task to Maat Memory.

    Args:
        agent: Agent identifier (required, non-empty)
        title: Short task title
        description: Full description
        status: pending | in_progress | completed
        priority: low | medium | high
        related_files_json: Optional JSON array of file paths
    """
    try:
        agent = _require_agent(agent)
        mem = _get_memory()
        from maat_memory.write_mediation import MediatedWriter, Principal, PrincipalKind

        writer = MediatedWriter(
            mem, Principal(agent_id=agent, kind=PrincipalKind.AGENT)
        )
        related = json.loads(related_files_json) if related_files_json else None
        tid = writer.log_task(
            title, description, status=status, priority=priority, related_files=related
        )
        return json.dumps(
            {
                "ok": True,
                "task_id": tid,
                "agent": agent,
                "content_origin": writer.origin.value,
            }
        )
    except Exception as e:
        return f"❌ {e}"


@mcp.tool()
async def memory_log_decision(
    agent: str,
    context: str,
    decision_made: str,
    rationale: str,
    options_considered_json: Optional[str] = None,
) -> str:
    """
    Log an architectural or process decision.

    Args:
        agent: Agent identifier (required, non-empty)
        context: What was being decided
        decision_made: The choice made
        rationale: Why this choice
        options_considered_json: Optional JSON array of alternatives
    """
    try:
        agent = _require_agent(agent)
        mem = _get_memory()
        from maat_memory.write_mediation import MediatedWriter, Principal, PrincipalKind

        writer = MediatedWriter(
            mem, Principal(agent_id=agent, kind=PrincipalKind.AGENT)
        )
        opts = json.loads(options_considered_json) if options_considered_json else None
        did = writer.log_decision(
            context, decision_made, rationale, options_considered=opts
        )
        return json.dumps(
            {
                "ok": True,
                "decision_id": did,
                "agent": agent,
                "content_origin": writer.origin.value,
            }
        )
    except Exception as e:
        return f"❌ {e}"


@mcp.tool()
async def memory_log_change(
    agent: str,
    file_path: str,
    change_type: str,
    summary: str,
    reason: str,
    diff_preview: Optional[str] = None,
) -> str:
    """
    Record a file change in memory.

    Args:
        agent: Agent identifier (required, non-empty)
        file_path: Path to the changed file
        change_type: create | update | delete | refactor
        summary: One-line summary
        reason: Why the change was made
        diff_preview: Optional short diff
    """
    try:
        agent = _require_agent(agent)
        mem = _get_memory()
        cid = mem.log_change(agent, file_path, change_type, summary, reason, diff_preview=diff_preview)
        return json.dumps({"ok": True, "change_id": cid, "agent": agent})
    except Exception as e:
        return f"❌ {e}"


@mcp.tool()
async def memory_log_learning(
    agent: str,
    topic: str,
    insight: str,
    source: str,
    confidence: float = 0.7,
) -> str:
    """
    Log a learning or Sankofa-style insight.

    Args:
        agent: Agent identifier (required, non-empty)
        topic: Short label
        insight: What was learned
        source: Where it came from (session, doc, failure, experiment)
        confidence: 0.0–1.0 confidence level
    """
    try:
        agent = _require_agent(agent)
        mem = _get_memory()
        lid = mem.log_learning(agent, topic, insight, source, confidence=confidence)
        return json.dumps({"ok": True, "learning_id": lid, "agent": agent})
    except Exception as e:
        return f"❌ {e}"


@mcp.tool()
async def memory_log_error(
    agent: str,
    error_type: str,
    message: str,
    context: Optional[str] = None,
) -> str:
    """
    Log an error to memory (Ka pain tracking).

    Args:
        agent: Agent identifier (required, non-empty)
        error_type: Category of error
        message: Error message
        context: Optional context about what was happening
    """
    try:
        agent = _require_agent(agent)
        mem = _get_memory()
        eid = mem.log_error(agent, error_type, message, context=context)
        return json.dumps({"ok": True, "error_id": eid, "agent": agent})
    except Exception as e:
        return f"❌ {e}"


@mcp.tool()
async def memory_log_audit(
    agent: str,
    action: str,
    details: str,
    result: str = "success",
) -> str:
    """
    Log an audit event (governance trail).

    Args:
        agent: Agent identifier (required, non-empty)
        action: What was done
        details: Full details
        result: success | failure | warning
    """
    try:
        agent = _require_agent(agent)
        mem = _get_memory()
        aid = mem.log_audit(
            agent,
            action=action,
            resource=(details or action)[:500],
            reason=f"{details} (result={result})" if details else str(result),
        )
        return json.dumps({"ok": True, "audit_id": aid, "agent": agent})
    except Exception as e:
        return f"❌ {e}"


# ============================================================
# RECALL — Read from memory
# ============================================================

@mcp.tool()
async def memory_search(
    query: str,
    agent: Optional[str] = None,
    limit: int = 10,
) -> str:
    """
    Search conversations by semantic query.

    Args:
        query: Natural language search query
        agent: Optional agent filter
        limit: Max results (default 10)
    """
    try:
        mem = _get_memory()
        results = mem.search_conversations(query, limit=limit)
        return json.dumps(results, indent=2, default=str)
    except Exception as e:
        return f"❌ {e}"


@mcp.tool()
async def memory_get_context(
    agent: str,
    limit: int = 10,
) -> str:
    """
    Get recent context for an agent.

    Args:
        agent: Agent identifier
        limit: Max entries (default 10)
    """
    try:
        mem = _get_memory()
        results = mem.get_context(agent, limit=limit)
        return json.dumps(results, indent=2, default=str)
    except Exception as e:
        return f"❌ {e}"


@mcp.tool()
async def memory_get_tasks(
    status: Optional[str] = None,
    limit: int = 10,
) -> str:
    """
    Get tasks from memory.

    Args:
        status: Filter by status (pending, in_progress, completed) or None for all
        limit: Max results (default 10)
    """
    try:
        mem = _get_memory()
        results = mem.get_tasks(status=status, limit=limit)
        return json.dumps(results, indent=2, default=str)
    except Exception as e:
        return f"❌ {e}"


@mcp.tool()
async def memory_get_recent_changes(
    limit: int = 10,
) -> str:
    """
    Get recent file changes from memory.

    Args:
        limit: Max results (default 10)
    """
    try:
        mem = _get_memory()
        results = mem.get_recent_changes(limit=limit)
        return json.dumps(results, indent=2, default=str)
    except Exception as e:
        return f"❌ {e}"


@mcp.tool()
async def memory_get_decisions(
    limit: int = 10,
) -> str:
    """
    Get recent decisions from memory.

    Args:
        limit: Max results (default 10)
    """
    try:
        mem = _get_memory()
        results = mem.get_decisions(limit=limit)
        return json.dumps(results, indent=2, default=str)
    except Exception as e:
        return f"❌ {e}"


@mcp.tool()
async def memory_get_learnings(
    limit: int = 10,
) -> str:
    """
    Get learnings and insights from memory.

    Args:
        limit: Max results (default 10)
    """
    try:
        mem = _get_memory()
        results = mem.get_learnings(limit=limit)
        return json.dumps(results, indent=2, default=str)
    except Exception as e:
        return f"❌ {e}"


@mcp.tool()
async def memory_get_recent_work(
    agent: str,
    limit: int = 10,
) -> str:
    """
    Get recent work history for an agent.

    Args:
        agent: Agent identifier
        limit: Max results (default 10)
    """
    try:
        mem = _get_memory()
        results = mem.get_recent_work(agent, limit=limit)
        return json.dumps(results, indent=2, default=str)
    except Exception as e:
        return f"❌ {e}"


# ============================================================
# SESSION — Manage memory sessions
# ============================================================

@mcp.tool()
async def memory_start_session(
    agent: str,
    summary: Optional[str] = None,
) -> str:
    """
    Start a new memory session for an agent.

    Args:
        agent: Agent identifier
        summary: Optional session summary/purpose
    """
    try:
        mem = _get_memory()
        sid = mem.start_session(agent, summary=summary)
        return json.dumps({"ok": True, "session_id": sid, "agent": agent})
    except Exception as e:
        return f"❌ {e}"


@mcp.tool()
async def memory_end_session(
    agent: str,
    summary: str,
    key_points_json: Optional[str] = None,
) -> str:
    """
    End a memory session with summary.

    Args:
        agent: Agent identifier
        summary: Session summary
        key_points_json: Optional JSON array of key points
    """
    try:
        mem = _get_memory()
        kp = json.loads(key_points_json) if key_points_json else None
        mem.end_session(agent, summary, key_points=kp)
        return json.dumps({"ok": True, "agent": agent, "summary": summary})
    except Exception as e:
        return f"❌ {e}"


@mcp.tool()
async def memory_get_sessions(
    agent: Optional[str] = None,
    limit: int = 10,
) -> str:
    """
    Get memory sessions.

    Args:
        agent: Optional agent filter
        limit: Max results (default 10)
    """
    try:
        mem = _get_memory()
        results = mem.get_sessions(agent=agent, limit=limit)
        return json.dumps(results, indent=2, default=str)
    except Exception as e:
        return f"❌ {e}"


# ============================================================
# HEALTH — Ka organ monitoring
# ============================================================

@mcp.tool()
async def memory_health() -> str:
    """
    Check memory organ health. Returns connection status, stats, and vitals.
    Used by the Ka organ for health monitoring.
    """
    health = {
        "organ": "memory",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "unknown",
        "db_url_configured": bool(PGVECTOR_DB_URL),
        "maatlangchain_available": MAATLANGCHAIN_PATH.exists(),
    }

    try:
        mem = _get_memory()
        # Quick connectivity test — get one task
        mem.get_tasks(limit=1)
        health["status"] = "healthy"
        health["connection"] = "active"
    except Exception as e:
        health["status"] = "degraded"
        health["error"] = str(e)

    health["gitmaat_law"] = _agent_bootstrap_law()
    health["one_liner"] = health["gitmaat_law"].get("one_liner")
    return json.dumps(health, indent=2)


@mcp.tool()
async def memory_stats(
    agent: Optional[str] = None,
) -> str:
    """
    Get memory usage statistics — conversations, tasks, decisions, learnings counts.
    Like a memory bank meter.

    Args:
        agent: Optional agent filter for per-agent stats
    """
    try:
        mem = _get_memory()
        stats = {
            "organ": "memory",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Gather counts
        tasks = mem.get_tasks(limit=1000)
        decisions = mem.get_decisions(limit=1000)
        learnings = mem.get_learnings(limit=1000)
        changes = mem.get_recent_changes(limit=1000)

        stats["totals"] = {
            "tasks": len(tasks) if tasks else 0,
            "decisions": len(decisions) if decisions else 0,
            "learnings": len(learnings) if learnings else 0,
            "changes": len(changes) if changes else 0,
        }

        # Task breakdown
        if tasks:
            stats["tasks_by_status"] = {}
            for t in tasks:
                s = t.get("status", "unknown")
                stats["tasks_by_status"][s] = stats["tasks_by_status"].get(s, 0) + 1

        # Learning confidence distribution
        if learnings:
            confs = [l.get("confidence", 0) for l in learnings if "confidence" in l]
            if confs:
                stats["learning_confidence"] = {
                    "min": min(confs),
                    "max": max(confs),
                    "avg": round(sum(confs) / len(confs), 2),
                }

        stats["status"] = "healthy"
        stats["gitmaat_law"] = _agent_bootstrap_law()
        return json.dumps(stats, indent=2, default=str)
    except Exception as e:
        return json.dumps({"organ": "memory", "status": "error", "error": str(e)}, indent=2)


def _agent_bootstrap_law() -> dict:
    """Law lives in the organ (maat_metadata.agent_bootstrap), not in skill files."""
    fallback = {
        "id": "tehuti.gitmaat.agent_bootstrap.v1",
        "one_liner": (
            "If you can reach gitMaat, you can reach the artifact bank — "
            "use open/https or fetch-artifact; never require /mnt/data_drive or file://."
        ),
    }
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor

        url = os.environ.get("PGVECTOR_DB_URL") or PGVECTOR_DB_URL
        if not url:
            return fallback
        conn = psycopg2.connect(url)
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT value FROM maat_metadata WHERE key = %s",
                    ("agent_bootstrap",),
                )
                row = cur.fetchone()
                if row and isinstance(row.get("value"), dict):
                    return row["value"]
        finally:
            conn.close()
    except Exception as e:
        log.warning("agent_bootstrap load failed: %s", e)
    return fallback


@mcp.tool()
async def memory_law() -> str:
    """
    ONE call: how any agent that reaches gitMaat must open the artifact bank.
    Returns maat_metadata.agent_bootstrap (portable open/fetch contract).
    Call this before opening any artifact path.
    """
    return json.dumps(_agent_bootstrap_law(), indent=2, default=str)


@mcp.tool()
async def memory_get_artifacts(
    audience: Optional[str] = None,
    slug: Optional[str] = None,
    every_agent: bool = False,
    portable_only: bool = False,
    ring: Optional[str] = None,
    viewer_ring: Optional[str] = None,
    limit: int = 20,
) -> str:
    """
    List maat_artifacts catalog. Prefer artifacts[].open (https) or portable_uri.
    Never open host file:///mnt/... or C:\\ paths on another machine.

    Args:
        audience: Filter metadata.audience
        slug: Exact metadata.slug
        every_agent: Shorthand for audience=every_lab_agent
        portable_only: Only rows with content_sha256
        limit: Max rows
    """
    try:
        mem = _get_memory()
        aud = "every_lab_agent" if every_agent else audience
        if hasattr(mem, "get_artifacts"):
            rows = mem.get_artifacts(
                audience=aud,
                slug=slug,
                portable_only=portable_only,
                ring=ring,
                viewer_ring=viewer_ring,
                limit=limit,
            )
        else:
            return json.dumps({"error": "get_artifacts not on memory backend — upgrade maatlangchain"})
        out = []
        for r in rows or []:
            meta = r.get("metadata") or {}
            if not isinstance(meta, dict):
                meta = {}
            portable = r.get("portable_uri") or (
                f"maat://object/{r['content_sha256']}" if r.get("content_sha256") else None
            )
            public = meta.get("public_uri")
            raw = r.get("uri") or ""
            if public and str(public).startswith("http"):
                open_uri, open_via = public, "https"
            elif portable:
                open_uri, open_via = portable, "memory_fetch_artifact"
            elif raw.startswith("http"):
                open_uri, open_via = raw, "https"
            else:
                open_uri, open_via = None, "unavailable_on_remote"
            out.append(
                {
                    "id": r.get("id"),
                    "title": r.get("title"),
                    "open": open_uri,
                    "open_via": open_via,
                    "portable_uri": portable,
                    "public_uri": public,
                    "slug": meta.get("slug"),
                    "audience": meta.get("audience"),
                    "ring": r.get("ring") or meta.get("ring") or "outer",
                    "content_sha256": r.get("content_sha256"),
                }
            )
        return json.dumps(
            {
                "count": len(out),
                "gitmaat_law": _agent_bootstrap_law(),
                "artifacts": out,
            },
            indent=2,
            default=str,
        )
    except Exception as e:
        return f"❌ {e}"


@mcp.tool()
async def memory_fetch_artifact(uri: str) -> str:
    """
    Fetch portable artifact text/bytes from maat_artifact_objects.
    Accepts maat://object/<sha256>, maat://artifact/<slug>, or sha256.

    Args:
        uri: Portable URI (not a host file path)
    """
    try:
        mem = _get_memory()
        if hasattr(mem, "fetch_artifact"):
            out = mem.fetch_artifact(uri)
        else:
            sys.path.insert(0, str(MAATLANGCHAIN_PATH.parent if MAATLANGCHAIN_PATH.name == "maat_memory" else MAATLANGCHAIN_PATH))
            # MAATLANGCHAIN_PATH is usually .../maatlangchain
            root = Path(os.environ.get("MAATLANGCHAIN_ROOT", str(MAATLANGCHAIN_PATH)))
            if str(root) not in sys.path:
                sys.path.insert(0, str(root))
            from maat_memory.memory_plane import ArtifactBank

            out = ArtifactBank().fetch(uri)
        # Keep MCP payload lean
        if isinstance(out, dict) and isinstance(out.get("text"), str) and len(out["text"]) > 8000:
            out = {**out, "text": out["text"][:8000] + "…", "text_truncated": True}
        return json.dumps(out, indent=2, default=str)
    except Exception as e:
        return f"❌ {e}"



@mcp.tool()
async def memory_write_artifact(
    title: str,
    content: str,
    slug: Optional[str] = None,
    ring: str = "outer",
    audience: Optional[str] = "every_lab_agent",
    agent: Optional[str] = None,
    content_type: str = "text/markdown",
    principal_id: Optional[str] = None,
) -> str:
    """
    Write artifact bytes into object store + catalog with portable_uri + sha + ring.
    Use this instead of host file:// paths when publishing for the fleet.

    Args:
        title: Artifact title
        content: Text body to store
        slug: Stable slug (optional)
        ring: Visibility tier outer|middle|inner
        audience: metadata.audience (default every_lab_agent)
        agent: Agent id (optional; auto-detected)
        content_type: MIME type
        principal_id: TEPI principal (optional)
    """
    try:
        import tempfile
        from pathlib import Path as P
        sys.path.insert(0, str(MAATLANGCHAIN_PATH))
        from maat_memory.memory_plane import ArtifactBank, FleetRegistry, should_write_artifact
        from maat_memory.machine_info import get_unique_agent_id

        aid = agent or get_unique_agent_id("hermes")
        reg = FleetRegistry()
        ids = reg.ensure_local("hermes")
        agent_row = reg.get_agent(ids["agent_id"]) or {}
        agent_ring = agent_row.get("ring") or "outer"
        gate = should_write_artifact(agent_ring=agent_ring, artifact_ring=ring, title=title)
        if not gate.get("ok"):
            return json.dumps({"ok": False, "error": "guard_denied", "guard": gate})

        suffix = ".md" if "markdown" in content_type else ".txt"
        if content_type == "text/html":
            suffix = ".html"
        with tempfile.TemporaryDirectory() as td:
            path = P(td) / f"{(slug or 'artifact')}{suffix}"
            path.write_text(content, encoding="utf-8")
            out = ArtifactBank().promote_file(
                path,
                slug=slug,
                title=title,
                agent_id=aid,
                machine_id=ids.get("machine_id"),
                ring=ring,
                audience=audience,
            )
        if out.get("ok") and principal_id:
            # stamp principal on catalog metadata
            from maat_memory.memory_plane import db
            db.execute(
                """
                UPDATE maat_artifacts SET
                  metadata = COALESCE(metadata,'{}'::jsonb) || %s::jsonb,
                  updated_at = NOW()
                WHERE content_sha256 = %s
                """,
                (json.dumps({"principal_id": principal_id}), out.get("sha256")),
            )
            out["principal_id"] = principal_id
        return json.dumps(out, indent=2, default=str)
    except Exception as e:
        return f"❌ {e}"


@mcp.tool()
async def memory_conversation_sink(
    user_query: str,
    agent_response: str,
    agent: Optional[str] = None,
    channel: Optional[str] = None,
    generate_embedding: bool = False,
) -> str:
    """
    Sink a messaging turn into maat_conversations (Truth). Call from Hermes/Discord/etc.

    Args:
        user_query: User message
        agent_response: Agent reply
        agent: Agent id
        channel: discord|whatsapp|telegram|cursor|…
        generate_embedding: Optional vector (default false for speed)
    """
    try:
        mem = _get_memory()
        aid = _agent_id(agent)
        meta = {"channel": channel or "hermes", "sink": "memory_conversation_sink"}
        cid = mem.log_conversation(
            agent=aid,
            user_query=user_query,
            agent_response=agent_response,
            generate_embedding=generate_embedding,
            metadata=meta,
        )
        return json.dumps({"ok": True, "conversation_id": cid, "agent": aid}, indent=2, default=str)
    except Exception as e:
        return f"❌ {e}"



if __name__ == "__main__":
    mcp.run()
