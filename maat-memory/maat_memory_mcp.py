#!/usr/bin/env python3
"""
maat-memory MCP Server — exposes maat-memory as MCP tools.

Registers tools:
  - maat_memory_write_episodic  — write what happened
  - maat_memory_write_semantic  — write what is known
  - maat_memory_read_episodic   — read recent episodic memories
  - maat_memory_read_semantic   — read semantic knowledge
  - maat_memory_commit          — commit and push to git
  - maat_memory_read_artifacts  — read artifacts from lab brain Postgres
  - maat_memory_write_artifact  — write artifact to lab brain Postgres

Run:
  python3 maat_memory_mcp.py

Then in Hermes:
  hermes mcp add maat-memory --command python3 --args /path/to/maat_memory_mcp.py
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from typing import Any

# ── Paths ─────────────────────────────────────────────────────────────────

MAAT_ECOSYSTEM = os.path.expanduser("~/maat-ecosystem")
MEMORY_DIR = os.path.join(MAAT_ECOSYSTEM, "maat-memory")
EPISODIC_DIR = os.path.join(MEMORY_DIR, "episodic")
SEMANTIC_DIR = os.path.join(MEMORY_DIR, "semantic")

# ── MCP Protocol ─────────────────────────────────────────────────────────


def send_response(response: dict):
    """Send a JSON-RPC response to stdout."""
    print(json.dumps(response), flush=True)


def send_error(request_id: Any, code: int, message: str):
    send_response({
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": code, "message": message},
    })


def send_result(request_id: Any, result: Any):
    send_response({
        "jsonrpc": "2.0",
        "id": request_id,
        "result": result,
    })


# ── Lab Brain Postgres ────────────────────────────────────────────────────
# Reads PGVECTOR_DB_URL from ~/.openclaw/.env (the lab's canonical env)
LAB_ENV_PATH = os.path.expanduser("~/.openclaw/.env")
PGVECTOR_URL = ""
if os.path.exists(LAB_ENV_PATH):
    with open(LAB_ENV_PATH) as f:
        for line in f:
            if line.startswith("PGVECTOR_DB_URL="):
                PGVECTOR_URL = line.split("=", 1)[1].strip().strip("\"'")
                break


def _pg_connect():
    """Connect to the lab brain Postgres. Returns None if unavailable."""
    if not PGVECTOR_URL:
        return None
    try:
        import psycopg2
        return psycopg2.connect(PGVECTOR_URL)
    except Exception:
        return None


# ── Tool Implementations ─────────────────────────────────────────────────


def tool_write_episodic(args: dict) -> dict:
    """Write an episodic memory (what happened)."""
    content = args.get("content", "")
    if not content:
        return {"error": "content is required"}

    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    timestamp = datetime.now(timezone.utc).isoformat()
    filename = f"fvg-edge-scan-{date_str}.md"
    path = os.path.join(EPISODIC_DIR, filename)
    os.makedirs(EPISODIC_DIR, exist_ok=True)

    entry = (
        f"# Episodic Memory — {date_str}\n"
        f"timestamp: {timestamp}\n"
        f"source: {args.get('source', 'hermes-mcp')}\n"
        f"\n"
        f"{content}\n"
    )

    existing = ""
    if os.path.exists(path):
        with open(path) as f:
            existing = f.read()

    if existing == entry:
        return {"status": "unchanged", "filename": filename}

    with open(path, "w") as f:
        f.write(entry)

    return {"status": "written", "filename": filename, "path": path}


def tool_write_semantic(args: dict) -> dict:
    """Write a semantic memory (what is known)."""
    domain = args.get("domain", "general")
    content = args.get("content", "")
    if not content:
        return {"error": "content is required"}

    filename = f"{domain.replace(' ', '-').lower()}.md"
    path = os.path.join(SEMANTIC_DIR, filename)
    os.makedirs(SEMANTIC_DIR, exist_ok=True)

    existing = ""
    if os.path.exists(path):
        with open(path) as f:
            existing = f.read()

    if existing == content:
        return {"status": "unchanged", "filename": filename}

    with open(path, "w") as f:
        f.write(content)

    return {"status": "written", "filename": filename, "path": path}


def tool_read_episodic(args: dict) -> dict:
    """Read recent episodic memories."""
    limit = args.get("limit", 5)
    files = []
    if os.path.isdir(EPISODIC_DIR):
        for f in sorted(os.listdir(EPISODIC_DIR), reverse=True):
            if f.endswith(".md") and f != "__init__.py":
                path = os.path.join(EPISODIC_DIR, f)
                with open(path) as fh:
                    content = fh.read()
                files.append({"filename": f, "content": content[:2000]})
                if len(files) >= limit:
                    break
    return {"memories": files}


def tool_read_semantic(args: dict) -> dict:
    """Read semantic knowledge."""
    domain = args.get("domain", None)
    files = []
    if os.path.isdir(SEMANTIC_DIR):
        for f in sorted(os.listdir(SEMANTIC_DIR)):
            if f.endswith(".md") and f != "__init__.py":
                if domain and domain not in f:
                    continue
                path = os.path.join(SEMANTIC_DIR, f)
                with open(path) as fh:
                    content = fh.read()
                files.append({"filename": f, "content": content[:3000]})
    return {"memories": files}


def tool_commit(args: dict) -> dict:
    """Commit and push to git."""
    message = args.get("message", f"maat-memory: update {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")

    try:
        subprocess.run(
            ["git", "-C", MAAT_ECOSYSTEM, "add", "maat-memory/"],
            capture_output=True, text=True, timeout=10, check=True,
        )
    except subprocess.CalledProcessError as e:
        return {"error": f"git add failed: {e.stderr[:200]}"}

    # Check for changes
    result = subprocess.run(
        ["git", "-C", MAAT_ECOSYSTEM, "status", "--porcelain", "maat-memory/"],
        capture_output=True, text=True, timeout=10,
    )
    if not result.stdout.strip():
        return {"status": "no_changes"}

    try:
        subprocess.run(
            ["git", "-C", MAAT_ECOSYSTEM, "commit", "-m", message],
            capture_output=True, text=True, timeout=10, check=True,
        )
    except subprocess.CalledProcessError as e:
        return {"error": f"git commit failed: {e.stderr[:200]}"}

    # Try push
    push = subprocess.run(
        ["git", "-C", MAAT_ECOSYSTEM, "push", "origin", "main"],
        capture_output=True, text=True, timeout=30,
    )

    return {
        "status": "committed",
        "message": message,
        "pushed": push.returncode == 0,
        "push_error": push.stderr[:200] if push.returncode != 0 else None,
    }


# ── Lab Brain Artifact Tools ──────────────────────────────────────────────


def tool_read_artifacts(args: dict) -> dict:
    """Read artifacts from the lab brain's maat_artifacts table."""
    conn = _pg_connect()
    if not conn:
        return {"artifacts": [], "note": "lab brain Postgres unavailable"}

    try:
        cur = conn.cursor()
        limit = int(args.get("limit", 50))
        artifact_type = args.get("artifact_type", None)

        if artifact_type:
            cur.execute(
                "SELECT id, uri, title, artifact_type, status, agent, "
                "EXTRACT(EPOCH FROM produced_at)::bigint AS produced_epoch, "
                "description "
                "FROM maat_artifacts "
                "WHERE artifact_type = %s "
                "ORDER BY produced_at DESC LIMIT %s",
                (artifact_type, limit),
            )
        else:
            cur.execute(
                "SELECT id, uri, title, artifact_type, status, agent, "
                "EXTRACT(EPOCH FROM produced_at)::bigint AS produced_epoch, "
                "description "
                "FROM maat_artifacts "
                "ORDER BY produced_at DESC LIMIT %s",
                (limit,),
            )

        rows = []
        for r in cur.fetchall():
            rows.append({
                "id": str(r[0]),
                "uri": r[1] or "",
                "title": r[2] or "",
                "artifact_type": r[3] or "",
                "status": r[4] or "",
                "agent": r[5] or "",
                "produced_at": r[6] or 0,
                "description": r[7] or "",
            })
        cur.close()
        conn.close()
        return {"artifacts": rows}
    except Exception as e:
        return {"artifacts": [], "error": str(e)}


def tool_write_artifact(args: dict) -> dict:
    """Write an artifact to the lab brain's maat_artifacts table.

    Creates a record in maat_artifacts and optionally stores content
    in maat_artifact_objects.
    """
    conn = _pg_connect()
    if not conn:
        return {"error": "lab brain Postgres unavailable"}

    try:
        import uuid
        import hashlib
        cur = conn.cursor()
        now = datetime.now(timezone.utc)
        artifact_id = str(uuid.uuid4())

        uri = args.get("uri", f"maat://artifact/{artifact_id}")
        title = args.get("title", "")
        artifact_type = args.get("artifact_type", "tool")
        status = args.get("status", "active")
        agent = args.get("agent", "hermes-mcp")
        description = args.get("description", "")
        content = args.get("content", None)
        content_type = args.get("content_type", "text/plain")

        # content_origin and storage_class are NOT NULL without defaults —
        # set them explicitly so writes don't violate the schema.
        content_origin = args.get("content_origin", "agent_authored")
        storage_class = args.get("storage_class", "object_backed" if content is not None else "reference_only")

        # The storage_coherence check requires object_backed artifacts to
        # carry content_sha256 — compute it up front so the INSERT passes.
        content_sha256 = None
        if content is not None:
            content_bytes = content.encode("utf-8") if isinstance(content, str) else content
            content_sha256 = hashlib.sha256(content_bytes).hexdigest()

        cur.execute(
            "INSERT INTO maat_artifacts "
            "(id, uri, title, artifact_type, status, agent, produced_at, created_at, updated_at, "
            "description, content_origin, storage_class, content_sha256) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (artifact_id, uri, title, artifact_type, status, agent,
             now, now, now, description, content_origin, storage_class, content_sha256),
        )

        if content is not None:
            slug = title.lower().replace(" ", "-").replace("/", "-")[:64] or artifact_id[:8]

            cur.execute(
                "INSERT INTO maat_artifact_objects "
                "(slug, logical_path, content, content_type, byte_len, sha256, "
                "machine_id, created_at, updated_at) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (slug, args.get("logical_path", slug),
                 content_bytes, content_type, len(content_bytes),
                 content_sha256, agent, now, now),
            )

        conn.commit()
        cur.close()
        conn.close()
        return {
            "status": "created",
            "id": artifact_id,
            "uri": uri,
            "title": title,
            "artifact_type": artifact_type,
        }
    except Exception as e:
        return {"error": str(e)}


# ── Tool Registry ────────────────────────────────────────────────────────

TOOLS = {
    "maat_memory_write_episodic": {
        "description": "Write an episodic memory (what happened today). Stores timestamped events in maat-memory.",
        "input_schema": {
            "type": "object",
            "properties": {
                "content": {"type": "string", "description": "The episodic content to store"},
                "source": {"type": "string", "description": "Source identifier (default: hermes-mcp)"},
            },
            "required": ["content"],
        },
        "handler": tool_write_episodic,
    },
    "maat_memory_write_semantic": {
        "description": "Write a semantic memory (what is known). Stores stable knowledge in maat-memory.",
        "input_schema": {
            "type": "object",
            "properties": {
                "domain": {"type": "string", "description": "Knowledge domain (e.g. fvg-edge-system, methodology)"},
                "content": {"type": "string", "description": "The semantic content to store"},
            },
            "required": ["content"],
        },
        "handler": tool_write_semantic,
    },
    "maat_memory_read_episodic": {
        "description": "Read recent episodic memories from maat-memory.",
        "input_schema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Max memories to return (default: 5)"},
            },
        },
        "handler": tool_read_episodic,
    },
    "maat_memory_read_semantic": {
        "description": "Read semantic knowledge from maat-memory.",
        "input_schema": {
            "type": "object",
            "properties": {
                "domain": {"type": "string", "description": "Optional domain filter (e.g. fvg-edge)"},
            },
        },
        "handler": tool_read_semantic,
    },
    "maat_memory_commit": {
        "description": "Commit and push maat-memory changes to git.",
        "input_schema": {
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "Commit message"},
            },
        },
        "handler": tool_commit,
    },
    "maat_memory_read_artifacts": {
        "description": "Read artifacts from the lab brain's maat_artifacts table. Returns artifact records with type, title, URI, and timestamp.",
        "input_schema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Max artifacts to return (default: 50)"},
                "artifact_type": {"type": "string", "description": "Optional filter by artifact type (e.g. workflowware_package, guard_decision_receipt)"},
            },
        },
        "handler": tool_read_artifacts,
    },
    "maat_memory_write_artifact": {
        "description": "Write an artifact to the lab brain's maat_artifacts table. Creates a record and optionally stores content in maat_artifact_objects.",
        "input_schema": {
            "type": "object",
            "properties": {
                "uri": {"type": "string", "description": "Artifact URI (default: auto-generated maat://artifact/<uuid>)"},
                "title": {"type": "string", "description": "Artifact title"},
                "artifact_type": {"type": "string", "description": "Artifact type (e.g. workflowware_package, guard_decision_receipt, trade_log)"},
                "status": {"type": "string", "description": "Status (default: active)"},
                "agent": {"type": "string", "description": "Source agent identifier (default: hermes-mcp)"},
                "description": {"type": "string", "description": "Artifact description"},
                "content": {"type": "string", "description": "Optional file content to store in maat_artifact_objects"},
                "content_type": {"type": "string", "description": "MIME type for content (default: text/plain)"},
                "logical_path": {"type": "string", "description": "Logical file path for content storage"},
            },
            "required": ["title", "artifact_type"],
        },
        "handler": tool_write_artifact,
    },
}


# ── MCP Server Loop ─────────────────────────────────────────────────────


def handle_request(request: dict):
    """Handle a single JSON-RPC request."""
    req_id = request.get("id")
    method = request.get("method", "")

    if method == "initialize":
        send_result(req_id, {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {},
            },
            "serverInfo": {
                "name": "maat-memory",
                "version": "1.0.0",
            },
        })

    elif method == "tools/list":
        tools_list = []
        for name, tool in TOOLS.items():
            tools_list.append({
                "name": name,
                "description": tool["description"],
                "inputSchema": tool["input_schema"],
            })
        send_result(req_id, {"tools": tools_list})

    elif method == "tools/call":
        tool_name = request.get("params", {}).get("name", "")
        arguments = request.get("params", {}).get("arguments", {})

        if tool_name not in TOOLS:
            send_error(req_id, -32601, f"Tool not found: {tool_name}")
            return

        try:
            result = TOOLS[tool_name]["handler"](arguments)
            send_result(req_id, {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]})
        except Exception as e:
            send_error(req_id, -32603, str(e))

    elif method == "notifications/initialized":
        pass  # no response needed

    else:
        send_error(req_id, -32601, f"Method not found: {method}")


def main():
    """Read JSON-RPC requests from stdin, write responses to stdout."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
            handle_request(request)
        except json.JSONDecodeError as e:
            # Can't send error without an ID
            pass


if __name__ == "__main__":
    main()