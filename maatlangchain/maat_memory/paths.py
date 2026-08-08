"""Portable path and env resolution for Maat Memory."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable, Optional


def find_workspace_root(start: Optional[Path] = None) -> Optional[Path]:
    """Find lab root: directory containing maatlangchain/."""
    for path in [start or Path.cwd()] + list((start or Path.cwd()).parents):
        if (path / "maatlangchain").is_dir():
            return path
    for path in Path(__file__).resolve().parents:
        if (path / "maatlangchain").is_dir():
            return path
        if path.name == "maatlangchain" and path.parent:
            return path.parent
    return None


def env_file_candidates(workspace_root: Optional[Path] = None) -> list[Path]:
    """Ordered .env files to scan for PGVECTOR_DB_URL and related vars."""
    root = workspace_root or find_workspace_root()
    candidates: list[Path] = []
    if root:
        candidates.extend(
            [
                root / ".env",
                root / "maatlangchain" / ".env",
                root / "tehuti-lab-webui" / ".env",
                root / "open-webui" / ".env",
            ]
        )
    candidates.append(Path.cwd() / ".env")
    # Dedupe while preserving order
    seen: set[Path] = set()
    out: list[Path] = []
    for p in candidates:
        rp = p.resolve() if p.exists() else p
        if rp not in seen:
            seen.add(rp)
            out.append(p)
    return out


def read_env_value(key: str, workspace_root: Optional[Path] = None) -> Optional[str]:
    """Read a key from os.environ or workspace .env files."""
    val = os.environ.get(key)
    if val:
        return val.strip().strip('"').strip("'")
    for env_file in env_file_candidates(workspace_root):
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


def get_pgvector_db_url() -> Optional[str]:
    url = read_env_value("PGVECTOR_DB_URL")
    if url:
        os.environ.setdefault("PGVECTOR_DB_URL", url)
    return url


def get_maat_memory_json_path() -> Path:
    explicit = os.environ.get("MAAT_MEMORY_JSON_PATH")
    if explicit:
        return Path(explicit).expanduser()
    root = find_workspace_root()
    if root:
        return root / ".maat_memory" / "maat_memory.json"
    return Path.home() / ".maat_memory" / "maat_memory.json"


def get_maat_memory_backup_dir() -> Path:
    explicit = os.environ.get("MAAT_MEMORY_BACKUP_DIR")
    if explicit:
        return Path(explicit).expanduser()
    return get_maat_memory_json_path().parent / "backups"


def get_maatlangchain_path() -> Optional[Path]:
    root = find_workspace_root()
    if root:
        return root / "maatlangchain"
    env_root = os.environ.get("MAAT_WORKSPACE_ROOT")
    if env_root:
        p = Path(env_root).expanduser() / "maatlangchain"
        if p.is_dir():
            return p
    return None
