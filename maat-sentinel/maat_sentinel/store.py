"""Append-only JSONL persistence under ~/.maat/sentinel/ (or MAAT_SENTINEL_STATE_DIR)."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Iterator


def state_dir() -> Path:
    raw = os.environ.get("MAAT_SENTINEL_STATE_DIR", "").strip()
    if raw:
        return Path(raw).expanduser().resolve()
    return Path.home() / ".maat" / "sentinel"


def ensure_state_dir() -> Path:
    d = state_dir()
    d.mkdir(parents=True, exist_ok=True)
    return d


def append_jsonl(name: str, obj: dict[str, Any]) -> Path:
    d = ensure_state_dir()
    path = d / f"{name}.jsonl"
    line = json.dumps(obj, separators=(",", ":"), ensure_ascii=False) + "\n"
    with path.open("a", encoding="utf-8") as f:
        f.write(line)
    return path


def tail_jsonl(name: str, limit: int = 100) -> list[dict[str, Any]]:
    path = state_dir() / f"{name}.jsonl"
    if not path.is_file():
        return []
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    out: list[dict[str, Any]] = []
    for line in lines[-limit:]:
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def iter_jsonl(name: str) -> Iterator[dict[str, Any]]:
    path = state_dir() / f"{name}.jsonl"
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            yield json.loads(line)
        except json.JSONDecodeError:
            continue
