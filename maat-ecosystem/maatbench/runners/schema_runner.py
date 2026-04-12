"""
Schema Runner — Tests contract integrity.
Validates MAAT JSON schemas are correct and complete.
"""

import json
from pathlib import Path
from typing import Any


# Canonical schemas live under skeleton/ (maat-core/ is legacy path)
_SCHEMA_ROOT = Path(__file__).resolve().parent.parent.parent
SCHEMA_DIR = _SCHEMA_ROOT / "skeleton" / "schemas"
if not SCHEMA_DIR.is_dir():
    SCHEMA_DIR = _SCHEMA_ROOT / "maat-core" / "schemas"


def load_schema(name: str) -> dict:
    path = SCHEMA_DIR / name
    if not path.exists():
        return {"error": f"Schema not found: {path}"}
    return json.loads(path.read_text())


def assert_valid_json_schema(schema: dict) -> tuple[bool, str]:
    """Check basic JSON Schema structure."""
    if "error" in schema:
        return False, schema["error"]
    if "$schema" not in schema and "$id" not in schema:
        return False, "Missing $schema or $id"
    if "type" not in schema:
        return False, "Missing type field"
    return True, "Valid JSON Schema structure"


def assert_has_required_fields(schema: dict) -> tuple[bool, str]:
    """Check that schema defines required fields."""
    if "required" not in schema:
        return False, "No required fields defined"
    if not schema["required"]:
        return False, "Required fields array is empty"
    return True, f"Has {len(schema['required'])} required fields"


def assert_has_field(schema: dict, field: str) -> tuple[bool, str]:
    """Check that schema defines a specific field in properties."""
    props = schema.get("properties", {})
    if field in props:
        return True, f"Field '{field}' exists"
    return False, f"Field '{field}' missing from properties"


def assert_enum_values(schema: dict, field: str, expected: list) -> tuple[bool, str]:
    """Check that a field has exactly the expected enum values."""
    props = schema.get("properties", {})
    field_def = props.get(field, {})
    actual = field_def.get("enum", [])
    if set(actual) == set(expected):
        return True, f"Enum values match: {expected}"
    return False, f"Expected {expected}, got {actual}"


def assert_field_default(schema: dict, field: str, expected_default: Any) -> tuple[bool, str]:
    """Check that a field has the expected default value."""
    props = schema.get("properties", {})
    field_def = props.get(field, {})
    actual = field_def.get("default")
    if actual == expected_default:
        return True, f"Default for '{field}' is {expected_default}"
    return False, f"Expected default {expected_default}, got {actual}"


def run_schema_tests(test_defs: list[dict]) -> list[dict]:
    """Run all schema tests. Returns list of results."""
    results = []
    for test in test_defs:
        schema = load_schema(test["schema"])
        test_id = test["id"]
        passed = True
        notes = []

        # Run assertions
        for assertion in test.get("assertions", []):
            if assertion == "valid_json_schema":
                ok, msg = assert_valid_json_schema(schema)
            elif assertion == "has_required_fields":
                ok, msg = assert_has_required_fields(schema)
            elif assertion == "has_id_field":
                ok, msg = assert_has_field(schema, "id")
            elif assertion == "has_memory_classes":
                ok, msg = assert_has_field(schema, "memory_class")
            elif assertion == "has_task_states":
                ok, msg = assert_has_field(schema, "status")
            elif assertion == "has_rules_array":
                ok, msg = assert_has_field(schema, "rules")
            elif assertion == "has_event_type":
                ok, msg = assert_has_field(schema, "type")
            elif assertion == "has_ring_field":
                ok, msg = assert_has_field(schema, "required_ring")
            elif assertion == "has_snapshot_fields":
                ok1, m1 = assert_has_field(schema, "before_snapshot")
                ok2, m2 = assert_has_field(schema, "after_snapshot")
                ok = ok1 and ok2
                msg = f"{m1}; {m2}"
            else:
                ok, msg = False, f"Unknown assertion: {assertion}"

            if not ok:
                passed = False
            notes.append(msg)

        # Check expected required fields
        if "expected_required" in test:
            actual_required = set(schema.get("required", []))
            expected = set(test["expected_required"])
            if expected.issubset(actual_required):
                notes.append(f"Required fields present: {test['expected_required']}")
            else:
                passed = False
                missing = expected - actual_required
                notes.append(f"Missing required fields: {missing}")

        # Check expected enum
        if "expected_enum" in test:
            field = test["expected_enum"]["field"]
            expected_vals = test["expected_enum"]["values"]
            ok, msg = assert_enum_values(schema, field, expected_vals)
            if not ok:
                passed = False
            notes.append(msg)

        results.append({
            "id": test_id,
            "name": test.get("name", test_id),
            "category": "contract_integrity",
            "passed": passed,
            "score": 1.0 if passed else 0.0,
            "notes": "; ".join(notes),
        })

    return results
