"""
gateway_runner — validates ArchivistRecord fixtures and lived-truth Guard cases.

Two runners live here:

1. ``run_gateway_contract_tests``: runs each suite fixture under
   ``maatbench/suites/gateway_contract/`` through
   ``gemma4-toolshim/swarm/gateway_contract.validate_record``; asserts the
   expected pass/fail outcome and optional error-substring matches.
2. ``run_gateway_policy_tests``: reads ``guard_cases/*.json`` at the lab
   root and runs ``gemma4-toolshim/swarm/guard_validator.validate_turn``
   synthesised from the case; asserts the resulting decision bucket
   matches.

Stdlib only; the swarm modules are stdlib only.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

_HERE = Path(__file__).resolve()
_BENCH_ROOT = _HERE.parent.parent
_ECO_ROOT = _BENCH_ROOT.parent
_LAB_ROOT = _ECO_ROOT.parent
_SWARM = _LAB_ROOT / "gemma4-toolshim" / "swarm"

for candidate in (_LAB_ROOT, _SWARM):
    s = str(candidate)
    if s not in sys.path:
        sys.path.insert(0, s)

import gateway_contract as gc  # type: ignore  # noqa: E402
import guard_validator as gv  # type: ignore  # noqa: E402


SUITE_ROOT = _BENCH_ROOT / "suites"
GUARD_CASES_ROOT = _LAB_ROOT / "guard_cases"


def _load_fixture(subfolder: str, name: str) -> dict[str, Any]:
    path = SUITE_ROOT / subfolder / name
    return json.loads(path.read_text())


def run_gateway_contract_tests(test_defs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for test in test_defs:
        test_id = test["id"]
        try:
            fixture = _load_fixture("gateway_contract", test["fixture"])
        except FileNotFoundError as exc:
            results.append(
                {
                    "id": test_id,
                    "name": test.get("name", test_id),
                    "category": "gateway_contract",
                    "passed": False,
                    "score": 0.0,
                    "notes": f"fixture not found: {exc}",
                }
            )
            continue

        expected = fixture.get("expected", "pass")
        errors = gc.validate_record(fixture["record"])
        actual = "pass" if not errors else "fail"

        notes = [f"errors={errors}"] if errors else ["no contract violations"]
        passed = actual == expected

        for must_contain in fixture.get("expected_errors_contain", []):
            if not any(must_contain in e for e in errors):
                passed = False
                notes.append(f"missing expected error substring: {must_contain!r}")

        results.append(
            {
                "id": test_id,
                "name": test.get("name", test_id),
                "category": "gateway_contract",
                "passed": passed,
                "score": 1.0 if passed else 0.0,
                "notes": "; ".join(notes),
            }
        )
    return results


def _synthesise_record_from_guard_case(case: dict[str, Any]) -> dict[str, Any]:
    """Build a plausible ArchivistRecord dict from a guard_case fixture."""
    context = case.get("context") or {}
    evidence = case.get("evidence") or {}
    justification = case.get("justification") or {}
    surface = case.get("surface", "unknown")
    case_id = case.get("id", "guard_case_unknown")
    user_request = (case.get("input") or {}).get("user_request", "")

    return {
        "schema": gc.SCHEMA_RECORD,
        "record_id": case_id,
        "correlation_id": f"{case_id}:0001",
        "created_at": gc.now_iso(),
        "agent_id": f"guard_case:{surface}",
        "gateway_id": f"guard_case:{surface}",
        "research_grade": False,
        "tags": [
            f"surface:{surface}",
            f"reason_code:{case.get('label', {}).get('reason_code', 'unknown')}",
        ],
        "summary": user_request[:500] or f"Guard case {case_id} synthesised for bench.",
        "sources": [
            {"kind": "tool_result", "ref": f"guard_cases/{case_id}.json"},
            {
                "kind": "memory",
                "ref": evidence.get("source_ref", context.get("retrieval_source", "n/a")),
            },
        ],
        "rbl_flags": [],
        "forbidden_hits": [],
        "gateway_state": {
            "turn_index": 0,
            "tools_used": [],
            "model_id": "none",
        },
        "notes": justification.get("explanation", ""),
    }


def _bucket_of(decision: str) -> str:
    if decision == "allow":
        return "allow"
    if decision == "deny":
        return "deny"
    return "review"


def _expected_matches(expected_bucket: str, actual_bucket: str) -> bool:
    if expected_bucket == "any":
        return True
    if expected_bucket == "review_or_deny":
        return actual_bucket in {"review", "deny"}
    return expected_bucket == actual_bucket


def run_gateway_policy_tests(test_defs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for test in test_defs:
        test_id = test["id"]
        case_file = GUARD_CASES_ROOT / test["guard_case"]
        if not case_file.exists():
            results.append(
                {
                    "id": test_id,
                    "name": test.get("name", test_id),
                    "category": "gateway_policy",
                    "passed": False,
                    "score": 0.0,
                    "notes": f"guard_case not found: {case_file}",
                }
            )
            continue

        case = json.loads(case_file.read_text())
        record = _synthesise_record_from_guard_case(case)
        decision = gv.validate_turn(record, call_guard_http=False)
        actual_bucket = _bucket_of(decision.decision)
        expected_bucket = test.get("expected_bucket", "any")

        passed = _expected_matches(expected_bucket, actual_bucket)
        notes = [
            f"case={case.get('id')}",
            f"decision={decision.decision}",
            f"bucket={actual_bucket}",
            f"expected={expected_bucket}",
            f"reasons={decision.reasons}",
        ]

        results.append(
            {
                "id": test_id,
                "name": test.get("name", test_id),
                "category": "gateway_policy",
                "passed": passed,
                "score": 1.0 if passed else 0.0,
                "notes": "; ".join(notes),
            }
        )
    return results


__all__ = ["run_gateway_contract_tests", "run_gateway_policy_tests"]
