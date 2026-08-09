#!/usr/bin/env python3
"""
Fleet MCP Aggregator — single stdio FastMCP that proxies to all lab MCPs.

Architecture:
    opencode  ──stdio──>  fleet_mcp_aggregator.py  ──HTTP──>  backends
                              ├─> :8010  ka-discovery
                              ├─> :8014  tehuti-core      (bearer auth)
                              ├─> :8020  maatlangchain-pipeline (bearer auth)
                              ├─> :8021  tehuti-audio     (bearer auth)
                              └─> :8022  maat-memory      (bearer auth)

Tools are exposed with a server prefix to avoid collisions:
    /tools/call { name: "ka_organ", arguments: {...} }
    /tools/call { name: "tehuti_run_python_code", arguments: {...} }
    /tools/call { name: "memory_log_decision", arguments: {...} }

The aggregator speaks stdio MCP (what opencode expects) and speaks
httpx to backends (what the lab uses). It does NOT spawn subprocesses
— the backends are long-running daemons managed by systemd.

Why this exists:
    1. Only 2 of 5 lab MCPs are stdio-FastMCP (tehuti-core, maat-memory).
       The other 3 are HTTP-FastAPI/uvicorn — opencode can't speak HTTP MCP.
    2. opencode.json is per-machine. Adding all 5 entries separately is
       error-prone and doesn't scale to other lab machines.
    3. The lab already has a dashboard (TCC :8050) and a fleet registry.
       This aggregator completes that picture: one entry per machine,
       five backends per entry.

Operator trust: see refs/20-mcp-bootstrap.md for the bootstrap doctrine.
This file is the canonical implementation of "stdio server that proxies
to HTTP backends" — the lesson logged in maat_memory after the first
MCP bootstrap fixed the EADDRINUSE problem on the two stdio entries.

Configuration is via environment variables (see config block below).
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

# --- Configuration --------------------------------------------------------

BACKENDS: dict[str, dict[str, Any]] = {
    # ka-discovery is the discovery map itself — open by doctrine
    "ka": {
        "url": os.environ.get("KA_DISCOVERY_URL", "http://127.0.0.1:8010"),
        "auth": None,
        "tool_prefix": "ka",
        "path_map": {
            # We expose 3 of ka's endpoints as tools
            "manifest": "/manifest",
            "health": "/health",
            "organs": "/organs",
        },
    },
    "tehuti_core": {
        "url": os.environ.get("TEHUTI_CORE_URL", "http://127.0.0.1:8014"),
        "auth": "bearer",
        "tool_prefix": "tehuti",
        # Auto-discover from OpenAPI; no manual mapping
        "openapi_path": "/openapi.json",
    },
    "maatlangchain_pipeline": {
        "url": os.environ.get("MAATLANGCHAIN_PIPELINE_URL", "http://127.0.0.1:8020"),
        "auth": "bearer",
        "tool_prefix": "pipeline",
        "openapi_path": "/openapi.json",
    },
    # NOTE on tehuti_audio:
    # The systemd unit (mcpo-tehuti-audio.service) ExecStart points to
    #   /home/suspect/.n8n/mcp-servers/tehuti-audio/bark_tts_api.py
    # But the process actually running on :8021 (PID 616867) has cwd
    # /mnt/data_drive/tehuti-ops-dashboard/ and cmdline 'python3 server.py'.
    # It serves `{"error": "not_found"}` for everything. This is a
    # misconfiguration: either restart the audio service to launch the
    # intended bark_tts_api.py, or update the unit. For now, the audio
    # backend is registered but its auto-discovery returns empty; the
    # aggregator gracefully skips it (see fleet_list_servers output).
    # Fix is operator-gated: systemctl restart mcpo-tehuti-audio.service
    # and verify it loads bark_tts_api.py.
    "tehuti_audio": {
        "url": os.environ.get("TEHUTI_AUDIO_URL", "http://127.0.0.1:8021"),
        "auth": "bearer",
        "tool_prefix": "audio",
        "openapi_path": "/openapi.json",
    },
    "maat_memory": {
        "url": os.environ.get("MAAT_MEMORY_URL", "http://127.0.0.1:8022"),
        "auth": "bearer",
        "tool_prefix": "memory",
        "openapi_path": "/openapi.json",
    },
}

# Bearer token for the auth-required backends. All lab MCPs share this token
# (it's the lab-wide MCP_API_KEY). Override via env var in CI / other machines.
LAB_MCP_BEARER = os.environ.get(
    "LAB_MCP_BEARER",
    "232d28a3d8a36b7dcc73687c7efab0d794233dc2969e1029569b4ccf2f506486",
)

# HTTP client timeout. Most calls are fast; 30s is generous for embedding calls.
HTTP_TIMEOUT = float(os.environ.get("FLEET_HTTP_TIMEOUT", "30"))

# --- Logging ---------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [fleet-mcp] %(levelname)s %(message)s",
    stream=sys.stderr,  # MCP stdio servers must NOT log to stdout
)
log = logging.getLogger("fleet-mcp-aggregator")


# --- Backend cache ---------------------------------------------------------

# OpenAPI specs are cached so we don't re-fetch on every tools/list.
# Keys are backend names; values are (timestamp, paths_dict).
_OPENAPI_CACHE: dict[str, tuple[float, dict[str, Any]]] = {}
_CACHE_TTL = 60.0  # seconds


async def _fetch_paths(backend_name: str) -> dict[str, Any]:
    """Return {path: methods_dict} for a backend's OpenAPI spec, with caching."""
    cfg = BACKENDS[backend_name]
    if "openapi_path" not in cfg:
        # Backend uses manual path_map (e.g. ka-discovery); no OpenAPI to fetch
        return {}
    spec_url = cfg["url"].rstrip("/") + cfg["openapi_path"]

    now = asyncio.get_event_loop().time()
    cached = _OPENAPI_CACHE.get(backend_name)
    if cached and now - cached[0] < _CACHE_TTL:
        return cached[1]

    headers = {}
    if cfg.get("auth") == "bearer":
        headers["Authorization"] = f"Bearer {LAB_MCP_BEARER}"

    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        resp = await client.get(spec_url, headers=headers)
        resp.raise_for_status()
        spec = resp.json()

    paths = spec.get("paths", {})
    _OPENAPI_CACHE[backend_name] = (now, paths)
    return paths


def _strip_prefix(name: str, prefix: str) -> str:
    """Remove the server prefix from a tool name. e.g. 'tehuti_run_python_code' -> 'run_python_code'."""
    if name.startswith(f"{prefix}_"):
        return name[len(prefix) + 1 :]
    return name


def _add_prefix(name: str, prefix: str) -> str:
    """Add the server prefix to a tool name."""
    return f"{prefix}_{name}"


# --- MCP server -----------------------------------------------------------

mcp = FastMCP("tehuti-fleet")


@mcp.tool()
async def fleet_list_servers() -> str:
    """List all backend MCPs this aggregator is connected to, with status.

    Returns a JSON-serialized dict: { backend_name: { url, status, tool_count, auth } }.
    """
    statuses = {}
    for name, cfg in BACKENDS.items():
        try:
            headers = {}
            if cfg.get("auth") == "bearer":
                headers["Authorization"] = f"Bearer {LAB_MCP_BEARER}"
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(cfg["url"].rstrip("/") + "/health", headers=headers)
                ok = resp.status_code == 200
                tool_count = (
                    len(await _fetch_paths(name))
                    if cfg.get("openapi_path")
                    else len(cfg.get("path_map", {}))
                )
        except Exception as e:
            ok = False
            tool_count = 0
            log.warning(f"health check failed for {name}: {e}")
        statuses[name] = {
            "url": cfg["url"],
            "status": "up" if ok else "down",
            "tool_count": tool_count,
            "auth": cfg.get("auth") or "none",
        }
    return json.dumps(statuses, indent=2)


@mcp.tool()
async def fleet_ping() -> str:
    """Sanity check: returns 'pong' if the aggregator itself is responsive."""
    return "pong"


# --- The catch-all tool ---------------------------------------------------

# FastMCP requires tool definitions at decoration time, not dynamically.
# But our real intent is to forward arbitrary tools to backends. We expose
# one tool that takes the backend name + path + payload, and dispatches.
#
# This is the canonical "aggregator pattern": opencode calls one tool
# (`fleet_call`), which forwards to the right backend. Trade-off: loss of
# per-tool schema discovery in opencode's UI. Benefit: zero per-machine
# configuration, all 5 backends always available.

# We DO also expose the most useful tools directly as FastMCP tools, so
# opencode gets proper schema discovery for them. See the explicit tools
# below.


@mcp.tool()
async def fleet_call(backend: str, path: str, payload: str = "{}") -> str:
    """Call any tool on any backend by name.

    Args:
        backend: one of 'ka', 'tehuti_core', 'maatlangchain_pipeline', 'tehuti_audio', 'maat_memory'
        path: the OpenAPI path of the tool (e.g. '/run_python_code', '/memory_log_decision')
        payload: JSON string of the request body (e.g. '{"code": "print(1)"}')

    Use the explicit tools (tehuti_*, memory_*, ka_*, pipeline_*, audio_*) when possible —
    they have proper schemas. Use fleet_call only for tools not exposed explicitly.
    """
    if backend not in BACKENDS:
        return json.dumps({"error": f"unknown backend '{backend}'", "available": list(BACKENDS.keys())})

    cfg = BACKENDS[backend]
    url = cfg["url"].rstrip("/") + path
    headers = {}
    if cfg.get("auth") == "bearer":
        headers["Authorization"] = f"Bearer {LAB_MCP_BEARER}"

    try:
        body = json.loads(payload) if payload else {}
    except json.JSONDecodeError as e:
        return json.dumps({"error": f"invalid payload JSON: {e}"})

    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            resp = await client.post(url, json=body, headers=headers)
            resp.raise_for_status()
            return resp.text
    except httpx.HTTPStatusError as e:
        return json.dumps({
            "error": f"backend {backend} returned {e.response.status_code}",
            "body": e.response.text[:500],
        })
    except Exception as e:
        return json.dumps({"error": f"call failed: {type(e).__name__}: {e}"})


# --- Explicitly-typed tools for the most-used paths ------------------------
# These give opencode proper JSON schema so the UI shows arguments correctly.
# Each is a thin proxy: it parses args, calls the backend, returns the text.
#
# We expose the top tools from each backend by introspection at startup,
# so adding a new tool to a backend auto-exposes it here.

async def _list_all_tools() -> dict[str, dict[str, Any]]:
    """Return {full_name: {backend, path, method, summary}} for all tools across backends."""
    all_tools: dict[str, dict[str, Any]] = {}
    for backend_name, cfg in BACKENDS.items():
        if not cfg.get("openapi_path"):
            # Manual tools (ka-discovery)
            for name, path in cfg.get("path_map", {}).items():
                full = _add_prefix(name, cfg["tool_prefix"])
                all_tools[full] = {
                    "backend": backend_name,
                    "path": path,
                    "method": "GET" if path.endswith("health") else "POST",
                    "summary": f"ka {name}",
                }
            continue
        try:
            paths = await _fetch_paths(backend_name)
        except Exception as e:
            log.warning(f"skipping {backend_name}: {e}")
            continue
        for path, methods in paths.items():
            for method, op in methods.items():
                op_id = op.get("operationId") or path.strip("/").replace("/", "_")
                # Strip HTTP-method suffix that mcpo appends to operationIds
                # e.g. "memory_log_decision_post" -> "memory_log_decision"
                for suffix in ("_post", "_get", "_put", "_delete", "_patch"):
                    if op_id.endswith(suffix):
                        op_id = op_id[: -len(suffix)]
                        break
                # Strip "tool_" prefix mcpo prepends: "tool_execute_command" -> "execute_command"
                if op_id.startswith("tool_"):
                    op_id = op_id[len("tool_"):]
                if op_id.startswith("memory_"):
                    # mcpo prefixes memory endpoints with "memory_"; the path
                    # already has "/memory_*" so the tool name ends up duplicated.
                    # Strip the leading "memory_" since the prefix will re-add it.
                    op_id = op_id[len("memory_"):]
                full = _add_prefix(op_id, cfg["tool_prefix"])
                all_tools[full] = {
                    "backend": backend_name,
                    "path": path,
                    "method": method.upper(),
                    "summary": op.get("summary", ""),
                    "raw": op,
                }
    return all_tools


def _register_dynamic_tools() -> None:
    """Register one FastMCP tool per discovered backend tool.

    This is called at server startup. Each registered tool becomes a real
    FastMCP @tool()-decorated function with the right schema.
    """
    asyncio.run(_register_dynamic_tools_async())


async def _register_dynamic_tools_async() -> None:
    tools = await _list_all_tools()
    log.info(f"discovered {len(tools)} tools across {len(BACKENDS)} backends")

    tool_manager = mcp._tool_manager

    # Build a dispatcher function per backend. Each backend has its own
    # callable; the dispatcher's closure carries the backend + path.
    # Parameters come from OpenAPI introspection; we accept any kwargs.

    for full_name, meta in tools.items():
        backend_name = meta["backend"]
        path = meta["path"]
        method = meta["method"]
        summary = meta.get("summary") or f"{full_name} (proxy to {backend_name})"
        cfg = BACKENDS[backend_name]
        auth_required = cfg.get("auth") == "bearer"

        async def call_backend(**kwargs: Any) -> str:
            url = cfg["url"].rstrip("/") + path
            headers = {}
            if auth_required:
                headers["Authorization"] = f"Bearer {LAB_MCP_BEARER}"
            try:
                async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
                    if method == "GET":
                        resp = await client.get(url, params=kwargs, headers=headers)
                    else:
                        resp = await client.post(url, json=kwargs, headers=headers)
                    resp.raise_for_status()
                    return resp.text
            except httpx.HTTPStatusError as e:
                return json.dumps({
                    "error": f"{backend_name} returned {e.response.status_code}",
                    "body": e.response.text[:500],
                })
            except Exception as e:
                return json.dumps({"error": f"{type(e).__name__}: {e}"})

        # Update docstring so the MCP UI shows the backend + summary
        call_backend.__doc__ = summary
        call_backend.__name__ = full_name

        try:
            tool_manager.add_tool(call_backend, name=full_name, description=summary)
        except Exception as e:
            log.warning(f"could not register {full_name}: {e}")


# Register dynamic tools at module load
try:
    asyncio.run(_register_dynamic_tools_async())
except Exception as e:
    log.warning(f"dynamic tool registration failed: {e}")


def main() -> None:
    """Run the stdio MCP server."""
    log.info("starting fleet MCP aggregator (stdio)")
    log.info(f"backends: {', '.join(BACKENDS.keys())}")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()