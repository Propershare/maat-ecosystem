#!/usr/bin/env python3
"""
MAAT contract smoke (starter "architecture with teeth").

Verifies constitutional artifacts exist and basic doctrine strings are present.
Expand this file as Tranches 2–6 land (events, memory classes, tool facade, packs).

Usage (from workspace root):
  python3 scripts/enforce-maat-contracts.py

Exit code: 0 = pass, 1 = failures.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# Workspace root: parent of scripts/
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

try:
    import maat_core  # noqa: E402
except ImportError:
    print(
        "ERROR: import maat_core failed — run from workspace root or "
        "set PYTHONPATH to it.",
        file=sys.stderr,
    )
    sys.exit(1)

REQUIRED_SCHEMA_BASENAMES = {
    "maat_event.schema.json",
    "maat_identity.schema.json",
    "maat_learning.schema.json",
    "maat_memory.schema.json",
    "maat_policy.schema.json",
    "maat_task.schema.json",
    "maat_tool.schema.json",
}

MEMORY_CLASSES = ("episodic", "semantic", "constitutional", "task", "working")
POLICY_OUTCOMES = ("allow", "deny", "escalate", "require_approval", "log")


def _fail(msgs: list[str]) -> int:
    for m in msgs:
        print(m, file=sys.stderr)
    return 1


def main() -> int:
    errors: list[str] = []

    if not maat_core.paths_ok():
        errors.append(
            "maat_core.paths_ok() is False — schemas/soul/bench "
            "contracts dirs missing."
        )

    basenames = {p.name for p in maat_core.list_schema_paths()}
    missing = REQUIRED_SCHEMA_BASENAMES - basenames
    extra = basenames - REQUIRED_SCHEMA_BASENAMES
    if missing:
        errors.append(f"Missing schema files: {sorted(missing)}")
    if extra:
        # Informational: new schemas may be intentional
        print(
            f"NOTE: Unexpected schema files (allowed if intentional): "
            f"{sorted(extra)}",
            file=sys.stderr,
        )

    event_path = maat_core.SCHEMAS_DIR / "maat_event.schema.json"
    if event_path.is_file():
        try:
            data = json.loads(event_path.read_text(encoding="utf-8"))
            props = data.get("properties") or {}
            typ = props.get("type") or {}
            examples = typ.get("examples") or []
            if not examples:
                errors.append(
                    "maat_event.schema.json: properties.type.examples is empty."
                )
            else:
                for ex in examples:
                    if not isinstance(ex, str):
                        errors.append(
                            "maat_event.schema.json: example is not a string: "
                            f"{ex!r}"
                        )
                        continue
                    if not re.match(r"^[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*$", ex):
                        errors.append(
                            "maat_event.schema.json: example type should look "
                            f"like 'domain.name', got: {ex!r}"
                        )
        except json.JSONDecodeError as e:
            errors.append(f"maat_event.schema.json: invalid JSON — {e}")
    else:
        errors.append(f"Missing {event_path}")

    const_path = maat_core.SOUL_DIR / "constitution.md"
    if const_path.is_file():
        text = const_path.read_text(encoding="utf-8").lower()
        for mc in MEMORY_CLASSES:
            if mc not in text:
                errors.append(
                    f"constitution.md: memory class '{mc}' not found in text."
                )
        for po in POLICY_OUTCOMES:
            if po not in text:
                errors.append(
                    f"constitution.md: policy outcome '{po}' not found in text."
                )
    else:
        errors.append(f"Missing {const_path}")

    # Placeholders for future tranches
    print(
        "SKIP (Tranche 4+): tool facade adapter interface check — "
        "not implemented yet."
    )
    print(
        "SKIP (Tranche 5+): pack forbidden-import scan — not implemented yet."
    )

    if errors:
        return _fail(errors)

    print("enforce-maat-contracts: OK (schemas + constitution smoke).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
