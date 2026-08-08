"""Wrapper for every JSONL line: source, schema_version, ingested_at (evolution-safe)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


SENTINEL_SOURCE = "maat-sentinel"
# Wrapper around typed payloads; bump when the outer envelope shape changes.
WRAPPER_SCHEMA_VERSION = "1"


def now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def wrap_record(record_type: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "source": SENTINEL_SOURCE,
        "schema_version": WRAPPER_SCHEMA_VERSION,
        "ingested_at": now_iso(),
        "record_type": record_type,
        "payload": payload,
    }


def unwrap_row(row: dict[str, Any]) -> dict[str, Any]:
    """Return inner payload; support legacy flat lines (no wrapper)."""
    p = row.get("payload")
    if isinstance(p, dict):
        return p
    return row
