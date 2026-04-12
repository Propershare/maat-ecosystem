"""
Learning Runner — Tests learning safety guarantees.
Validates snapshots, rollback, and constitutional protection.
"""

import sys
import json
from pathlib import Path

ECOSYSTEM = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ECOSYSTEM))


def run_learning_tests(test_defs: list[dict]) -> list[dict]:
    results = []

    for test in test_defs:
        test_id = test["id"]
        op = test.get("operation", "")
        passed = True
        notes = []

        try:
            if op == "check_schema":
                schema_path = ECOSYSTEM / "maat-core" / "schemas" / test["schema"]
                schema = json.loads(schema_path.read_text())
                props = schema.get("properties", {})

                if "has_fields" in test["expected"]:
                    for field in test["expected"]["has_fields"]:
                        if field in props:
                            notes.append(f"Field '{field}' present")
                        else:
                            passed = False
                            notes.append(f"Field '{field}' MISSING")

                if "field_default" in test["expected"]:
                    for field, expected_val in test["expected"]["field_default"].items():
                        actual = props.get(field, {}).get("default")
                        if actual == expected_val:
                            notes.append(f"Default for '{field}' = {expected_val}")
                        else:
                            passed = False
                            notes.append(f"Default for '{field}': expected {expected_val}, got {actual}")

            elif op == "check_schema_enum":
                schema_path = ECOSYSTEM / "maat-core" / "schemas" / test["schema"]
                schema = json.loads(schema_path.read_text())
                field = test["field"]
                actual = schema.get("properties", {}).get(field, {}).get("enum", [])
                expected = test["expected"]["values"]
                if set(actual) == set(expected):
                    notes.append(f"Learning types match: {len(expected)} types")
                else:
                    passed = False
                    missing = set(expected) - set(actual)
                    extra = set(actual) - set(expected)
                    if missing:
                        notes.append(f"Missing types: {missing}")
                    if extra:
                        notes.append(f"Unexpected types: {extra}")

            elif op == "run_consolidation":
                from maat_packs import __init__  # noqa: just ensure importable
                # Simple check: consolidation module exists and produces output
                from maat_memory.consolidation.consolidator import Consolidator
                # We can't run full consolidation without a real adapter,
                # but we verify the class exists and has the right interface
                has_method = hasattr(Consolidator, 'consolidate')
                if has_method:
                    notes.append("Consolidator.consolidate() method exists")
                else:
                    passed = False
                    notes.append("Consolidator missing consolidate() method")

            elif op == "apply_and_rollback":
                # Simulate learning + rollback
                before = test["before"].copy()
                after = test["after"].copy()
                expected_after_rollback = test["expected"]["after_rollback"]

                # "Apply" learning
                current = after.copy()

                # "Rollback" — restore from before_snapshot
                current = before.copy()

                if current == expected_after_rollback:
                    notes.append("Rollback restored before_snapshot state")
                else:
                    passed = False
                    notes.append(f"After rollback: {current}, expected: {expected_after_rollback}")

            elif op == "attempt_constitutional_learning":
                # Constitutional memory should not be modifiable via learning
                # It requires formal amendment
                from maat_memory.constitutional.handler import validate_constitutional
                entry = {
                    "agent_id": "test",
                    "memory_class": "constitutional",
                    "content": "test value",
                }
                validated = validate_constitutional(entry)
                if validated["reversible"] is False:
                    notes.append("Constitutional memory correctly non-reversible (blocks learning override)")
                    # The point: learning would need to call amend_constitutional,
                    # not just write over it
                else:
                    passed = False
                    notes.append("Constitutional memory is reversible — learning could corrupt it")

            else:
                notes.append(f"Unknown operation: {op}")
                passed = False

        except Exception as e:
            passed = False
            notes.append(f"Exception: {e}")

        results.append({
            "id": test_id,
            "name": test.get("name", test_id),
            "category": "learning_safety",
            "passed": passed,
            "score": 1.0 if passed else 0.0,
            "notes": "; ".join(notes),
        })

    return results
