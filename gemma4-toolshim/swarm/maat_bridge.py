"""
Maat Bridge — HTTP calls to Maat Memory MCP (mcpo on :8022).

Default base: http://127.0.0.1:8022
(see maat-ecosystem/mcp-servers/maat-memory/start_maat_memory.sh).

Environment:
  MAAT_MEMORY_MCP_BASE — override base URL (no trailing slash)
  MAAT_MEMORY_MCP_API_KEY — Bearer (or MCPO_API_KEY / KA_API_KEY)

mcpo: POST /{tool_name} + JSON body (OpenAPI), not POST /call.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

TIMEOUT = 30


def _base_url() -> str:
    default = "http://127.0.0.1:8022"
    return os.environ.get("MAAT_MEMORY_MCP_BASE", default).rstrip("/")


def _auth_headers() -> Dict[str, str]:
    h: Dict[str, str] = {"Content-Type": "application/json"}
    key = (
        os.environ.get("MAAT_MEMORY_MCP_API_KEY")
        or os.environ.get("MCPO_API_KEY")
        or os.environ.get("KA_API_KEY")
    )
    if key:
        h["Authorization"] = f"Bearer {key.strip()}"
    return h


def _call_mcp(tool_name: str, arguments: Dict[str, Any]) -> Optional[Any]:
    """Call Maat Memory MCP via mcpo (POST base/tool_name, JSON body)."""
    url = f"{_base_url()}/{tool_name}"
    payload = json.dumps(arguments).encode("utf-8")
    req = Request(url, data=payload, headers=_auth_headers(), method="POST")

    try:
        with urlopen(req, timeout=TIMEOUT) as resp:
            body = resp.read().decode("utf-8")
    except HTTPError as e:
        err = e.read().decode("utf-8", errors="replace") if e.fp else str(e)
        print(f"[maat_bridge] HTTP {e.code} for {tool_name}: {err[:500]}")
        return None
    except URLError as e:
        print(f"[maat_bridge] Connection error for {tool_name}: {e}")
        return None
    except Exception as e:
        print(f"[maat_bridge] Unexpected error for {tool_name}: {e}")
        return None

    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return body


def _unwrap_results(raw: Any) -> List[Dict[str, Any]]:
    """Normalize memory_search tool output into a list of dict-like entries."""
    if raw is None:
        return []
    if isinstance(raw, list):
        return [x for x in raw if isinstance(x, dict)]
    if isinstance(raw, dict):
        return [raw]
    if isinstance(raw, str):
        s = raw.strip()
        if s.startswith("❌"):
            print(f"[maat_bridge] {s[:300]}")
            return []
        try:
            parsed = json.loads(s)
        except json.JSONDecodeError:
            return [{"summary": s[:2000]}]
        if isinstance(parsed, list):
            return [x for x in parsed if isinstance(x, dict)]
        if isinstance(parsed, dict):
            return [parsed]
    return []


def query_memory(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Search gitMaat / conversation memory (memory_search MCP tool).
    """
    raw = _call_mcp("memory_search", {"query": query, "limit": limit})
    return _unwrap_results(raw)[:limit]


def log_task(description: str, agent: str) -> bool:
    raw = _call_mcp(
        "memory_log_task",
        {
            "agent": agent,
            "title": "Bridge task",
            "description": description,
            "status": "pending",
        },
    )
    bad = isinstance(raw, str) and raw.strip().startswith("❌")
    return raw is not None and not bad


def log_decision(description: str, agent: str) -> bool:
    raw = _call_mcp(
        "memory_log_decision",
        {
            "agent": agent,
            "context": "maat_bridge",
            "decision_made": description[:2000],
            "rationale": description,
        },
    )
    bad = isinstance(raw, str) and raw.strip().startswith("❌")
    return raw is not None and not bad


def log_learning(description: str, agent: str) -> bool:
    raw = _call_mcp(
        "memory_log_learning",
        {
            "agent": agent,
            "topic": "insight",
            "insight": description,
            "source": "maat_bridge",
        },
    )
    bad = isinstance(raw, str) and raw.strip().startswith("❌")
    return raw is not None and not bad


def log_change(description: str, agent: str) -> bool:
    raw = _call_mcp(
        "memory_log_change",
        {
            "agent": agent,
            "file_path": "(unspecified)",
            "change_type": "update",
            "summary": description[:500],
            "reason": "maat_bridge",
        },
    )
    bad = isinstance(raw, str) and raw.strip().startswith("❌")
    return raw is not None and not bad


if __name__ == "__main__":
    print("Maat Bridge — connection test\n")
    print(f"Base: {_base_url()}\n")

    print("memory_health...")
    h = _call_mcp("memory_health", {})
    print(f"  {h}\n")

    print("memory_search (sample)...")
    results = query_memory("recent work", limit=2)
    print(f"  {len(results)} result(s)")

    print("\nlog_task (may fail if DB unavailable)...")
    ok = log_task("maat_bridge connection test", agent="test-runner")
    print(f"  {'ok' if ok else 'failed'}")
