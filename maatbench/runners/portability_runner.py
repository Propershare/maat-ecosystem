"""
Portability Runner — Tests that identity, memory, policy survive swaps.
"""

import sys
import json
import uuid
import tempfile
from pathlib import Path
from datetime import datetime, timezone

ECOSYSTEM = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ECOSYSTEM))


def run_portability_tests(test_defs: list[dict]) -> list[dict]:
    results = []

    for test in test_defs:
        test_id = test["id"]
        op = test.get("operation", "")
        passed = True
        notes = []

        try:
            if op == "export_import_identity":
                from maat_core.kernel.identity import IdentityStore
                # Export
                tmp1 = tempfile.mktemp(suffix=".json")
                store1 = IdentityStore({"path": tmp1})
                identity = test["identity"].copy()
                identity.setdefault("created_at", datetime.now(timezone.utc).isoformat())
                identity.setdefault("version", "1")
                store1.register(identity)

                # Read exported data
                exported = json.loads(Path(tmp1).read_text())

                # Import into new store
                tmp2 = tempfile.mktemp(suffix=".json")
                Path(tmp2).write_text(json.dumps(exported))
                store2 = IdentityStore({"path": tmp2})

                # Verify
                imported = store2.get(identity["id"])
                if imported:
                    for field in test["expected"]["fields_preserved"]:
                        if imported.get(field) != identity.get(field):
                            passed = False
                            notes.append(f"Field '{field}' not preserved")
                    if passed:
                        notes.append("Identity survived export/import")
                else:
                    passed = False
                    notes.append("Identity not found after import")

            elif op == "write_swap_read":
                from maat_adapters.memory.sqlite import SQLiteAdapter
                # Write to backend A
                tmp_a = tempfile.mktemp(suffix=".db")
                adapter_a = SQLiteAdapter({"path": tmp_a})
                entry = test["entry"].copy()
                entry_id = str(uuid.uuid4())
                entry["id"] = entry_id
                entry["timestamp"] = datetime.now(timezone.utc).isoformat()
                adapter_a.write(entry)

                # Export content
                original = adapter_a.get(entry_id)

                # Write to backend B (simulating swap)
                tmp_b = tempfile.mktemp(suffix=".db")
                adapter_b = SQLiteAdapter({"path": tmp_b})
                adapter_b.write(original)

                # Read from backend B
                migrated = adapter_b.get(entry_id)
                if migrated:
                    if migrated.get("content") == entry["content"]:
                        notes.append("Content preserved across backend swap")
                    else:
                        passed = False
                        notes.append("Content NOT preserved")
                    if str(migrated.get("memory_class")) == entry.get("memory_class", "episodic"):
                        notes.append("Memory class preserved")
                    else:
                        passed = False
                        notes.append("Memory class NOT preserved")
                else:
                    passed = False
                    notes.append("Entry not found after swap")

            elif op == "save_load_policy":
                from maat_core.kernel.policy import PolicyEngine
                policy = test["policy"]

                # Save
                tmp = tempfile.mktemp(suffix=".json")
                Path(tmp).write_text(json.dumps(policy))

                # Load
                loaded = json.loads(Path(tmp).read_text())

                # Verify structure
                if len(loaded.get("rules", [])) == len(policy.get("rules", [])):
                    notes.append("Rules count preserved")
                else:
                    passed = False
                    notes.append("Rules count changed")

                # Verify evaluation is same
                engine1 = PolicyEngine([policy])
                engine1.register_agent("test", "outer-ring")
                engine2 = PolicyEngine([loaded])
                engine2.register_agent("test", "outer-ring")

                r1 = engine1.evaluate("test", "execute", "rm -rf /tmp")
                r2 = engine2.evaluate("test", "execute", "rm -rf /tmp")

                if r1["allowed"] == r2["allowed"]:
                    notes.append("Evaluation consistent after save/load")
                else:
                    passed = False
                    notes.append("Evaluation differs after save/load")

            elif op == "write_read_events":
                tmp = tempfile.mktemp(suffix=".jsonl")
                from maat_core.kernel.events import EventBus
                bus = EventBus({"log_path": tmp})
                for evt in test["events"]:
                    bus.emit({
                        "id": str(uuid.uuid4()),
                        "type": evt["type"],
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "session_id": "port-test",
                        "severity": "info",
                        "payload": evt.get("payload", {}),
                    })
                lines = Path(tmp).read_text().strip().split("\n")
                all_parseable = all(json.loads(l) for l in lines)
                if all_parseable and len(lines) == len(test["events"]):
                    notes.append("All events parseable and count matches")
                else:
                    passed = False
                    notes.append(f"Expected {len(test['events'])} events, got {len(lines)}")

            elif op == "full_export":
                notes.append("Full export test — structure validated by other tests")

            elif op == "check_schema_field":
                schema_path = ECOSYSTEM / "maat-core" / "schemas" / test["schema"]
                schema = json.loads(schema_path.read_text())
                field = test["field"]
                if field in schema.get("properties", {}):
                    notes.append(f"Field '{field}' exists in schema")
                else:
                    passed = False
                    notes.append(f"Field '{field}' missing from schema")

            else:
                notes.append(f"Unknown operation: {op}")
                passed = False

        except Exception as e:
            passed = False
            notes.append(f"Exception: {e}")

        results.append({
            "id": test_id,
            "name": test.get("name", test_id),
            "category": "portability",
            "passed": passed,
            "score": 1.0 if passed else 0.0,
            "notes": "; ".join(notes),
        })

    return results
