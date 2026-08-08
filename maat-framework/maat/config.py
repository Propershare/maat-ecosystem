"""
Maat Config — Load, save, get, set configuration.

Config lives at ~/.maat/config.yaml. Created with defaults on first run.
Uses dot-paths for get/set: config.get("agent.model") → "gemma4:e4b"
"""

import copy
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

# ─── Defaults ──────────────────────────────────────────────────────

DEFAULT_CONFIG: Dict[str, Any] = {
    "agent": {
        "name": "maat",
        "model": "gemma4:e4b",
        "personality": "concise and helpful",
    },
    "memory": {
        "backend": "postgres",
        "database_url": "",
        "embedding_model": "nomic-embed-text",
        "context_limit": 10,
    },
    "security": {
        "governance": "three-ring",
        "default_role": "outer-ring",
        "scan_commands": True,
    },
    "tools": {
        "mcp_servers": [],
    },
    "ollama": {
        "host": "http://localhost:11434",
        "models": [],
    },
}

CONFIG_DIR = Path.home() / ".maat"
CONFIG_PATH = CONFIG_DIR / "config.yaml"

# Module-level cache so repeated calls don't re-read disk
_config_cache: Optional[Dict[str, Any]] = None


# ─── Helpers ───────────────────────────────────────────────────────

def _ensure_dir() -> None:
    """Create ~/.maat/ if it doesn't exist."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def _deep_merge(base: Dict, override: Dict) -> Dict:
    """
    Recursively merge override into base.
    Keys in override win. Missing keys fall back to base.
    """
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _walk(data: Any, keys: list[str]) -> Any:
    """Walk a nested dict by key path. Returns None if path doesn't exist."""
    current = data
    for k in keys:
        if isinstance(current, dict) and k in current:
            current = current[k]
        else:
            return None
    return current


# ─── Public API ────────────────────────────────────────────────────

def load_config(path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load config from disk, merged with defaults.

    Args:
        path: Override config file path (default: ~/.maat/config.yaml).

    Returns:
        Complete config dict with all defaults filled in.
    """
    global _config_cache
    target = path or CONFIG_PATH
    _ensure_dir()

    if not target.exists():
        _config_cache = copy.deepcopy(DEFAULT_CONFIG)
        return _config_cache

    try:
        with open(target) as f:
            on_disk = yaml.safe_load(f) or {}
        _config_cache = _deep_merge(copy.deepcopy(DEFAULT_CONFIG), on_disk)
        return _config_cache
    except (yaml.YAMLError, OSError) as e:
        print(f"[maat.config] Error loading {target}: {e} — using defaults")
        _config_cache = copy.deepcopy(DEFAULT_CONFIG)
        return _config_cache


def save_config(config: Optional[Dict[str, Any]] = None, path: Optional[Path] = None) -> None:
    """
    Save config to disk.

    Args:
        config: Config dict to save (uses cached if None).
        path: Override file path (default: ~/.maat/config.yaml).
    """
    global _config_cache
    target = path or CONFIG_PATH
    data = config or _config_cache or load_config()
    _ensure_dir()

    try:
        with open(target, "w") as f:
            yaml.safe_dump(data, f, sort_keys=False, default_flow_style=False)
        _config_cache = data
    except OSError as e:
        print(f"[maat.config] Error saving {target}: {e}")


def get(key: str) -> Any:
    """
    Get a config value by dot-path.

    Args:
        key: Dot-separated path, e.g. "agent.model"

    Returns:
        The value, or None if path doesn't exist.

    Example:
        >>> get("agent.model")
        'gemma4:e4b'
        >>> get("memory.context_limit")
        10
    """
    config = _config_cache or load_config()
    return _walk(config, key.split("."))


def set(key: str, value: Any, save: bool = True) -> None:
    """
    Set a config value by dot-path.

    Args:
        key: Dot-separated path, e.g. "agent.model"
        value: Value to set.
        save: Write to disk immediately (default True).

    Example:
        >>> set("agent.model", "gemma4:26b")
    """
    global _config_cache
    config = _config_cache or load_config()
    keys = key.split(".")

    # Walk to parent, creating dicts as needed
    current = config
    for k in keys[:-1]:
        if k not in current or not isinstance(current[k], dict):
            current[k] = {}
        current = current[k]

    current[keys[-1]] = value
    _config_cache = config

    if save:
        save_config(config)


def reset() -> Dict[str, Any]:
    """Reset config to defaults and save."""
    global _config_cache
    _config_cache = copy.deepcopy(DEFAULT_CONFIG)
    save_config(_config_cache)
    return _config_cache


# ─── Quick Test ────────────────────────────────────────────────────

if __name__ == "__main__":
    print("🔧 Maat Config Test\n")
    cfg = load_config()
    print(f"  Agent name:  {get('agent.name')}")
    print(f"  Model:       {get('agent.model')}")
    print(f"  Memory:      {get('memory.backend')}")
    print(f"  Governance:  {get('security.governance')}")
    print(f"  Ollama host: {get('ollama.host')}")
    print(f"\n  Config path: {CONFIG_PATH}")
