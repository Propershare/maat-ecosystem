"""Load YAML/JSON manifest and profile."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_document(path: Path) -> dict[str, Any] | None:
    """Load YAML or JSON; return a dict or None if missing, unreadable, or invalid."""
    if not path.is_file():
        return None
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError:
        return None
    suffix = path.suffix.lower()
    if suffix in (".yaml", ".yml"):
        try:
            import yaml  # type: ignore[import-untyped]
        except ImportError:
            return None
        try:
            data = yaml.safe_load(raw)
        except Exception:
            return None
        if not isinstance(data, dict):
            return None
        return data
    if suffix == ".json":
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return None
        if not isinstance(data, dict):
            return None
        return data
    return None
