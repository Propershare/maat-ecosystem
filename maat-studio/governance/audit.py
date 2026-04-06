"""
MAAT Governance Audit

Track policy changes, violations, and escalations.
Constitutional-level visibility.
"""

import json
from pathlib import Path

MAAT_HOME = Path.home() / ".maat"


def audit_report():
    """Generate a governance audit report from the event log."""
    path = MAAT_HOME / "events.jsonl"
    if not path.exists():
        return {"error": "No event log"}

    violations = []
    escalations = []
    policy_evals = []

    for line in path.read_text().strip().split("\n"):
        try:
            event = json.loads(line)
            etype = event.get("type", "")

            if etype == "policy.violated":
                violations.append(event)
            elif "escalat" in etype:
                escalations.append(event)
            elif etype == "policy.evaluated":
                policy_evals.append(event)
        except Exception:
            pass

    report = {
        "total_policy_evaluations": len(policy_evals),
        "violations": len(violations),
        "escalations": len(escalations),
        "violation_details": [
            {
                "timestamp": v.get("timestamp"),
                "agent": v.get("payload", {}).get("agent_id"),
                "action": v.get("payload", {}).get("action"),
                "reason": v.get("payload", {}).get("reason"),
            }
            for v in violations
        ],
        "escalation_details": [
            {
                "timestamp": e.get("timestamp"),
                "type": e.get("type"),
                "payload": e.get("payload"),
            }
            for e in escalations
        ],
    }

    return report


def print_audit():
    report = audit_report()
    print("🏛️  MAAT Governance Audit\n")
    print(f"  Policy evaluations: {report.get('total_policy_evaluations', 0)}")
    print(f"  Violations:         {report.get('violations', 0)}")
    print(f"  Escalations:        {report.get('escalations', 0)}")

    if report.get("violation_details"):
        print("\n  Violations:")
        for v in report["violation_details"]:
            print(f"    ❌ {v['timestamp']} | {v['agent']} tried {v['action']}: {v['reason']}")

    if report.get("escalation_details"):
        print("\n  Escalations:")
        for e in report["escalation_details"]:
            print(f"    ⚠️  {e['timestamp']} | {e['type']}")


if __name__ == "__main__":
    print_audit()
