"""Discover Maat Memory MCP base URL."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Optional


DEFAULT_MEMORY_URL = "http://127.0.0.1:8022"
DEFAULT_KA_DISCOVERY = "http://127.0.0.1:8010/manifest"

_API_KEY_NAMES = (
    "MAAT_MEMORY_API_KEY",
    "MAAT_MEMORY_MCP_API_KEY",
    "MCPO_API_KEY",
    "KA_API_KEY",
)


def _env_file_candidates() -> list[Path]:
    candidates: list[Path] = []
    cwd = Path.cwd()
    for path in [cwd] + list(cwd.parents):
        if (path / "maatlangchain").is_dir():
            candidates.extend(
                [
                    path / ".env",
                    path / "maatlangchain" / ".env",
                ]
            )
            break
    candidates.append(cwd / ".env")
    seen: set[Path] = set()
    out: list[Path] = []
    for p in candidates:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


def _read_key_from_env_files(key: str) -> Optional[str]:
    for env_file in _env_file_candidates():
        if not env_file.exists():
            continue
        try:
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith(f"{key}="):
                        return line.split("=", 1)[1].strip().strip('"').strip("'")
        except OSError:
            pass
    return None


def discover_memory_url() -> str:
    """Resolve memory service URL: env -> Ka manifest -> localhost default."""
    for key in ("MAAT_MEMORY_URL", "MAAT_MEMORY_MCP_BASE"):
        val = os.environ.get(key, "").strip()
        if val:
            return val.rstrip("/")

    ka = os.environ.get("KA_DISCOVERY_URL", DEFAULT_KA_DISCOVERY).strip()
    if ka:
        try:
            with urllib.request.urlopen(ka, timeout=3) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            organs = data.get("organs") or {}
            mem = organs.get("memory") or {}
            endpoint = mem.get("endpoint")
            if isinstance(endpoint, str) and endpoint.startswith("http"):
                return endpoint.rstrip("/")
        except (urllib.error.URLError, OSError, json.JSONDecodeError, ValueError):
            pass

    return DEFAULT_MEMORY_URL


def resolve_api_key() -> Optional[str]:
    for key in _API_KEY_NAMES:
        val = os.environ.get(key, "").strip()
        if val:
            return val
    for key in _API_KEY_NAMES:
        val = _read_key_from_env_files(key)
        if val:
            os.environ.setdefault(key, val)
            return val
    return None
