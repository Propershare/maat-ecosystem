"""
Event Runner — Tests event system fidelity.
Validates emission, subscription, persistence, and replay.
"""

import sys
import json
import uuid
import tempfile
from pathlib import Path
from datetime import datetime, timezone

ECOSYSTEM = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ECOSYSTEM))

from maat_core.kernel.events import EventBus, CANONICAL_EVENTS


def make_event(event_type: str, payload: dict = None, session_id: str = "test") -> dict:
    return {
        "id": str(uuid.uuid4()),
        "type": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "severity": "info",
        "payload": payload or {},
    }


def run_event_tests(test_defs: list[dict]) -> list[dict]:
    results = []

    for test in test_defs:
        test_id = test["id"]
        op = test.get("operation", "")
        passed = True
        notes = []

        try:
            if op == "emit_and_capture":
                captured = []
                bus = EventBus()
                bus.subscribe(test["event_type"], lambda e: captured.append(e))
                bus.emit(make_event(test["event_type"], test.get("payload")))
                if captured:
                    notes.append("Event captured by subscriber")
                else:
                    passed = False
                    notes.append("Event NOT captured")

            elif op == "subscribe_and_filter":
                captured = []
                bus = EventBus()
                bus.subscribe(test["subscribe_to"], lambda e: captured.append(e))
                for etype in test["emit_events"]:
                    bus.emit(make_event(etype))
                expected_count = test["expected"]["received_count"]
                if len(captured) == expected_count:
                    notes.append(f"Received {expected_count} events as expected")
                else:
                    passed = False
                    notes.append(f"Expected {expected_count}, received {len(captured)}")

            elif op == "emit_and_check_log":
                tmp = tempfile.mktemp(suffix=".jsonl")
                bus = EventBus({"log_path": tmp})
                bus.emit(make_event(test["event_type"]))
                log_content = Path(tmp).read_text().strip()
                if log_content:
                    parsed = json.loads(log_content.split("\n")[-1])
                    if parsed.get("type") == test["event_type"]:
                        notes.append("Event persisted to JSONL log")
                    else:
                        passed = False
                        notes.append("Event type mismatch in log")
                else:
                    passed = False
                    notes.append("Log file is empty")

            elif op == "emit_and_validate":
                captured = []
                bus = EventBus()
                bus.subscribe("*", lambda e: captured.append(e))
                bus.emit(make_event(test["event_type"]))
                if captured:
                    event = captured[0]
                    for field in test["expected"]["has_fields"]:
                        if field not in event:
                            passed = False
                            notes.append(f"Missing field: {field}")
                    if passed:
                        notes.append("All required fields present")
                else:
                    passed = False
                    notes.append("No event captured")

            elif op == "check_canonical":
                for etype in test["event_types"]:
                    if etype not in CANONICAL_EVENTS:
                        passed = False
                        notes.append(f"Non-canonical: {etype}")
                if passed:
                    notes.append("All event types are canonical")

            elif op == "emit_session_and_replay":
                tmp = tempfile.mktemp(suffix=".jsonl")
                session_id = str(uuid.uuid4())
                bus = EventBus({"log_path": tmp})
                for evt_def in test["events"]:
                    bus.emit(make_event(evt_def["type"], evt_def.get("payload"), session_id))

                # Replay
                log_lines = Path(tmp).read_text().strip().split("\n")
                replayed = [json.loads(l) for l in log_lines if json.loads(l).get("session_id") == session_id]

                expected_count = test["expected"]["replay_count"]
                if len(replayed) == expected_count:
                    notes.append(f"Replayed {expected_count} events")
                else:
                    passed = False
                    notes.append(f"Expected {expected_count} replay events, got {len(replayed)}")

                if test["expected"].get("order_preserved"):
                    types = [e["type"] for e in replayed]
                    expected_types = [e["type"] for e in test["events"]]
                    if types == expected_types:
                        notes.append("Order preserved")
                    else:
                        passed = False
                        notes.append("Order NOT preserved")

            else:
                notes.append(f"Unknown operation: {op}")
                passed = False

        except Exception as e:
            passed = False
            notes.append(f"Exception: {e}")

        results.append({
            "id": test_id,
            "name": test.get("name", test_id),
            "category": "event_fidelity",
            "passed": passed,
            "score": 1.0 if passed else 0.0,
            "notes": "; ".join(notes),
        })

    return results
