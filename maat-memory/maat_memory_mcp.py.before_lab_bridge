#!/usr/bin/env python3
"""
maat-memory MCP Server — exposes maat-memory as MCP tools.

Registers tools:
  - maat_memory_write_episodic  — write what happened
  - maat_memory_write_semantic  — write what is known
  - maat_memory_read_episodic   — read recent episodic memories
  - maat_memory_read_semantic   — read semantic knowledge
  - maat_memory_commit          — commit and push to git

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