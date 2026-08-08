"""
Maat Adapt — Auto-discover system capabilities and configure the agent.

Scans for:
- Ollama models available locally
- MCP servers running on known ports
- PostgreSQL connection
- Available tools

Usage:
    from maat.adapt import discover, auto_configure

    # See what's available
    system = discover()
    print(system["ollama"]["models"])
    print(system["mcp_servers"])

    # Auto-generate config from what's found
    auto_configure()  # Writes to ~/.maat/config.yaml
"""

import json
import socket
from typing import Any, Dict, List, Optional
from urllib.error import URLError
from urllib.request import Request, urlopen

from maat.config import load_config, save_config

# ─── Known MCP Servers ─────────────────────────────────────────────

# These are the consolidated Maat servers + common extras.
# adapt.py probes each port to see what's actually running.

KNOWN_MCP_SERVERS = [
    {"name": "maat-core", "port": 8014, "description": "Shell, filesystem, gitMaat queries"},
    {"name": "maat-research", "port": 8012, "description": "RAG search, document ingestion"},
    {"name": "maat-creative", "port": 8019, "description": "Image generation, audio"},
    {"name": "maat-curriculum", "port": 8011, "description": "Education tools"},
    {"name": "maat-memory", "port": 8018, "description": "Memory MCP (gitMaat)"},
    {"name": "maat-filesystem", "port": 8016, "description": "Filesystem operations"},
    {"name": "maat-postgres", "port": 8017, "description": "Database queries"},
    {"name": "maat-n8n", "port": 8015, "description": "n8n workflow triggers"},
    {"name": "maat-audio", "port": 8021, "description": "Bark TTS"},
    {"name": "maat-langchain", "port": 8020, "description": "MaatLangChain pipeline"},
]


# ─── Probes ────────────────────────────────────────────────────────

def _probe_port(host: str, port: int, timeout: float = 2.0) -> bool:
    """Check if a TCP port is open."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (OSError, socket.timeout):
        return False


def _http_get_json(url: str, timeout: float = 5.0) -> Optional[Any]:
    """GET a URL and parse JSON. Returns None on any error."""
    try:
        req = Request(url, headers={"Accept": "application/json"})
        with urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None


def discover_ollama(host: str = "http://localhost:11434") -> Dict[str, Any]:
    """
    Discover Ollama instance and available models.

    Returns:
        Dict with "available" (bool), "host" (str), "models" (list of names).
    """
    result: Dict[str, Any] = {"available": False, "host": host, "models": []}

    data = _http_get_json(f"{host}/api/tags")
    if data and "models" in data:
        result["available"] = True
        result["models"] = [m["name"] for m in data["models"]]

    return result


def discover_mcp_servers(host: str = "localhost") -> List[Dict[str, Any]]:
    """
    Probe known MCP server ports and return which ones are alive.

    Returns:
        List of dicts with name, port, url, description for each running server.
    """
    alive = []
    for server in KNOWN_MCP_SERVERS:
        if _probe_port(host, server["port"]):
            alive.append({
                "name": server["name"],
                "port": server["port"],
                "url": f"http://{host}:{server['port']}",
                "description": server["description"],
            })
    return alive


def discover_postgres() -> Dict[str, Any]:
    """
    Check if PostgreSQL is reachable (port 5432) and if we have a connection URL.

    Returns:
        Dict with "available" (bool), "url" (str or empty).
    """
    result: Dict[str, Any] = {"available": False, "url": ""}

    # Check port
    if not _probe_port("localhost", 5432):
        return result

    # Try to find the URL
    try:
        from maat.learn import _resolve_db_url
        url = _resolve_db_url()
        result["available"] = True
        result["url"] = url
    except (ValueError, ImportError):
        # Port is open but we don't have credentials
        result["available"] = True
        result["url"] = ""

    return result


def discover() -> Dict[str, Any]:
    """
    Run full system discovery.

    Returns:
        Dict with ollama, mcp_servers, postgres info.

    Example:
        >>> system = discover()
        >>> system["ollama"]["models"]
        ['gemma4:e4b', 'maat-compact-v1', 'nomic-embed-text']
        >>> len(system["mcp_servers"])
        6
    """
    return {
        "ollama": discover_ollama(),
        "mcp_servers": discover_mcp_servers(),
        "postgres": discover_postgres(),
    }


# ─── Auto-Configure ───────────────────────────────────────────────

def auto_configure(save: bool = True) -> Dict[str, Any]:
    """
    Discover the system and generate/update config automatically.

    Picks the best model, registers discovered MCP servers,
    sets up the database URL.

    Args:
        save: Write config to disk (default True).

    Returns:
        The generated config dict.
    """
    system = discover()
    config = load_config()

    # ── Ollama ──
    if system["ollama"]["available"]:
        config["ollama"]["host"] = system["ollama"]["host"]
        config["ollama"]["models"] = system["ollama"]["models"]

        # Pick the best model (prefer gemma4, then maat-compact, then first available)
        models = system["ollama"]["models"]
        preferred = ["gemma4:e4b", "gemma4:26b", "maat-compact-v1:latest"]
        chosen = None
        for pref in preferred:
            if pref in models:
                chosen = pref
                break
        if not chosen and models:
            # Skip embedding models
            for m in models:
                if "embed" not in m and "minilm" not in m:
                    chosen = m
                    break
        if chosen:
            config["agent"]["model"] = chosen

    # ── MCP Servers ──
    config["tools"]["mcp_servers"] = [
        {"name": s["name"], "url": s["url"]}
        for s in system["mcp_servers"]
    ]

    # ── Postgres ──
    if system["postgres"]["available"] and system["postgres"]["url"]:
        config["memory"]["database_url"] = system["postgres"]["url"]
        config["memory"]["backend"] = "postgres"

    if save:
        save_config(config)

    return config


# ─── Quick Test ────────────────────────────────────────────────────

if __name__ == "__main__":
    print("🔍 Maat Adapt — System Discovery\n")

    system = discover()

    # Ollama
    ollama = system["ollama"]
    if ollama["available"]:
        print(f"  ✅ Ollama ({ollama['host']})")
        print(f"     Models: {', '.join(ollama['models'][:8])}")
        if len(ollama["models"]) > 8:
            print(f"     ... and {len(ollama['models']) - 8} more")
    else:
        print("  ❌ Ollama not found")

    # MCP Servers
    servers = system["mcp_servers"]
    print(f"\n  {'✅' if servers else '❌'} MCP Servers: {len(servers)} running")
    for s in servers:
        print(f"     {s['name']:20} → {s['url']} ({s['description']})")

    # Postgres
    pg = system["postgres"]
    if pg["available"]:
        print(f"\n  ✅ PostgreSQL {'(URL found)' if pg['url'] else '(port open, no URL)'}")
    else:
        print("\n  ❌ PostgreSQL not reachable")

    print(f"\n  Total capabilities: {len(ollama.get('models', []))} models, {len(servers)} MCP servers")
