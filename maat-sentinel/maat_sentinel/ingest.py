"""Ingest doctor snapshots, immune envelopes, and presence records."""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from typing import Any, TextIO

from maat_sentinel.envelope import now_iso, wrap_record
from maat_sentinel.models import DoctorSnapshot, ImmuneEventInput, PresenceRecord
from maat_sentinel import store


def ingest_doctor_json(doc: dict[str, Any]) -> DoctorSnapshot:
    if "timestamp" not in doc or not doc["timestamp"]:
        doc = {**doc, "timestamp": now_iso()}
    snap = DoctorSnapshot.from_doctor_json(doc)
    inner = {
        **asdict(snap),
        "payload_schema": "maat-sentinel/doctor-snapshot/v1",
    }
    store.append_jsonl("doctor_snapshots", wrap_record("doctor_snapshot", inner))
    try:
        from maat_sentinel import governance_memory

        governance_memory.after_ingest(snap.machine_id)
    except Exception:
        pass
    return snap


def ingest_immune_dict(row: dict[str, Any]) -> ImmuneEventInput:
    ev = ImmuneEventInput.from_envelope_dict(row)
    inner = {
        **asdict(ev),
        "payload_schema": "maat-sentinel/immune-event/v1",
    }
    store.append_jsonl("immune_events", wrap_record("immune_event", inner))
    try:
        from maat_sentinel import governance_memory

        governance_memory.after_immune_constitutional(ev)
        governance_memory.after_ingest(ev.machine_id)
    except Exception:
        pass
    return ev


def ingest_presence(rec: PresenceRecord) -> None:
    inner = {
        **asdict(rec),
        "payload_schema": "maat-sentinel/presence/v1",
        "recorded_at": now_iso(),
    }
    store.append_jsonl("presence", wrap_record("presence", inner))
    try:
        from maat_sentinel import governance_memory

        governance_memory.after_ingest(rec.machine_id)
    except Exception:
        pass


def ingest_immune_jsonl_stream(stream: TextIO) -> int:
    """Read JSONL from stream (e.g. stdin); one immune envelope per line."""
    n = 0
    for line in stream:
        line = line.strip()
        if not line:
            continue
        try:
            ingest_immune_dict(json.loads(line))
            n += 1
        except json.JSONDecodeError:
            continue
    return n


def ingest_stdin_immune() -> int:
    return ingest_immune_jsonl_stream(sys.stdin)
