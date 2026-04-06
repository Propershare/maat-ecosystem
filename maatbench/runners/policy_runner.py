"""
Policy Runner — Tests policy enforcement.
Deliberately tries to break rules and verifies enforcement.
"""

import sys
from pathlib import Path

ECOSYSTEM = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ECOSYSTEM))

from maat_core.kernel.policy import PolicyEngine


def run_policy_tests(test_defs: list[dict]) -> list[dict]:
    """Run all policy tests. Returns list of results."""
    results = []

    for test in test_defs:
        test_id = test["id"]
        passed = True
        notes = []

        # Create fresh policy engine for each test
        engine = PolicyEngine()

        # Register agent ring
        if test.get("agent_ring"):
            engine.register_agent(test["agent_id"], test["agent_ring"])

        # Load custom policy if present
        if "policy" in test:
            engine.load_policy(test["policy"])

        # Evaluate
        result = engine.evaluate(
            agent_id=test["agent_id"],
            action=test["action"],
            resource=test.get("resource", ""),
        )

        expected = test["expected"]

        # Check allowed
        if "allowed" in expected:
            if result["allowed"] != expected["allowed"]:
                passed = False
                notes.append(f"Expected allowed={expected['allowed']}, got {result['allowed']}")
            else:
                notes.append(f"Correctly {'allowed' if result['allowed'] else 'denied'}")

        # Check escalate flag
        if "escalate" in expected:
            if result.get("escalate") != expected["escalate"]:
                passed = False
                notes.append(f"Expected escalate={expected['escalate']}, got {result.get('escalate')}")
            else:
                notes.append("Escalation triggered correctly")

        # Check reason exists
        if result.get("reason"):
            notes.append(f"Reason: {result['reason']}")

        results.append({
            "id": test_id,
            "name": test.get("name", test_id),
            "category": "policy_fidelity",
            "passed": passed,
            "score": 1.0 if passed else 0.0,
            "notes": "; ".join(notes),
        })

    return results
