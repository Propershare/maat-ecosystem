"""
Memory Runner — Tests memory integrity.
Validates attribution, append-only, rollback, and constitutional rules.
"""

import sys
import uuid
import tempfile
from pathlib import Path
from datetime import datetime, timezone

ECOSYSTEM = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ECOSYSTEM))


def get_test_adapter():
    """Get a fresh SQLite adapter pointing to a temp DB."""
    from maat_adapters.memory.sqlite import SQLiteAdapter
    tmp = tempfile.mktemp(suffix=".db")
    return SQLiteAdapter({"path": tmp}), tmp


def run_memory_tests(test_defs: list[dict]) -> list[dict]:
    results = []

    for test in test_defs:
        test_id = test["id"]
        op = test.get("operation", "")
        passed = True
        notes = []

        try:
            if op == "write":
                adapter, tmp = get_test_adapter()
                entry = test["entry"].copy()
                entry["id"] = str(uuid.uuid4())
                entry["timestamp"] = datetime.now(timezone.utc).isoformat()
                success = adapter.write(entry)
                if test["expected"].get("success") and not success:
                    passed = False
                    notes.append("Write failed")
                else:
                    notes.append("Write succeeded")

            elif op == "search":
                adapter, tmp = get_test_adapter()
                # Write precondition
                pre = test["precondition"]["write"].copy()
                pre["id"] = str(uuid.uuid4())
                pre["timestamp"] = datetime.now(timezone.utc).isoformat()
                adapter.write(pre)
                # Search
                found = adapter.search(test["query"])
                min_expected = test["expected"].get("min_results", 1)
                if len(found) < min_expected:
                    passed = False
                    notes.append(f"Expected >= {min_expected} results, got {len(found)}")
                else:
                    notes.append(f"Found {len(found)} results")

            elif op == "delete":
                adapter, tmp = get_test_adapter()
                pre = test["precondition"]["write"].copy()
                entry_id = str(uuid.uuid4())
                pre["id"] = entry_id
                pre["timestamp"] = datetime.now(timezone.utc).isoformat()
                adapter.write(pre)
                success = adapter.delete(entry_id)
                if test["expected"].get("success") and not success:
                    passed = False
                    notes.append("Delete failed")
                else:
                    notes.append("Delete succeeded (rollback works)")

            elif op == "write_and_read":
                adapter, tmp = get_test_adapter()
                entry = test["entry"].copy()
                entry_id = str(uuid.uuid4())
                entry["id"] = entry_id
                entry["timestamp"] = datetime.now(timezone.utc).isoformat()
                adapter.write(entry)
                retrieved = adapter.get(entry_id)
                field = test["expected"].get("field_present", "")
                if retrieved and retrieved.get(field):
                    notes.append(f"Field '{field}' present and non-empty")
                else:
                    passed = False
                    notes.append(f"Field '{field}' missing or empty")

            elif op == "validate_constitutional":
                from maat_memory.constitutional.handler import validate_constitutional
                entry = test["entry"].copy()
                entry["id"] = str(uuid.uuid4())
                entry["timestamp"] = datetime.now(timezone.utc).isoformat()
                validated = validate_constitutional(entry)
                if validated.get("reversible") == test["expected"].get("reversible"):
                    notes.append("Constitutional correctly marked non-reversible")
                else:
                    passed = False
                    notes.append("Constitutional memory was not marked non-reversible")

            elif op == "amend_constitutional":
                from maat_memory.constitutional.handler import amend_constitutional
                original = test["original"].copy()
                amended = amend_constitutional(original, test["amendment"], test["reason"])
                expected = test["expected"]

                if expected.get("version_incremented"):
                    if amended["version"] > original.get("version", 1):
                        notes.append("Version incremented")
                    else:
                        passed = False
                        notes.append("Version NOT incremented")

                if expected.get("original_preserved_in_amendments"):
                    trail = amended.get("amendments", [])
                    originals_in_trail = [a.get("previous_content") for a in trail]
                    if original["content"] in originals_in_trail:
                        notes.append("Original content preserved in amendment trail")
                    else:
                        passed = False
                        notes.append("Original content NOT in amendment trail")

                if expected.get("content_updated"):
                    if amended["content"] == test["amendment"]:
                        notes.append("Content updated to new value")
                    else:
                        passed = False
                        notes.append("Content was not updated")

                if expected.get("amendments_array_grows"):
                    if len(amended.get("amendments", [])) > len(original.get("amendments", [])):
                        notes.append("Amendments array grew")
                    else:
                        passed = False
                        notes.append("Amendments array did not grow")

                if expected.get("previous_content_in_trail"):
                    trail = amended.get("amendments", [])
                    found_prev = any(
                        a.get("previous_content") == expected["previous_content_in_trail"]
                        for a in trail
                    )
                    if found_prev:
                        notes.append("Previous content found in audit trail")
                    else:
                        passed = False
                        notes.append("Previous content NOT in audit trail")

            else:
                notes.append(f"Unknown operation: {op}")
                passed = False

        except Exception as e:
            passed = False
            notes.append(f"Exception: {e}")

        results.append({
            "id": test_id,
            "name": test.get("name", test_id),
            "category": "memory_fidelity",
            "passed": passed,
            "score": 1.0 if passed else 0.0,
            "notes": "; ".join(notes),
        })

    return results
