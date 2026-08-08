"""Deprecated alias — use maatbench.scorers.maat_attest_gate (Maat Attest)."""

from maatbench.scorers.maat_attest_gate import (  # noqa: F401
    evaluate_from_isfet_report,
    evaluate_maat_attest,
    evaluate_security_certification,
    load_rubric,
)

if __name__ == "__main__":
    import json
    import sys

    from maatbench.scorers.maat_attest_gate import evaluate_maat_attest

    out = evaluate_maat_attest(
        isfet_results=[
            {"id": "demo.1", "class": "role_collapse", "passed": True, "leaked": False}
        ],
        security_results=[],
        meta={
            "subject": "demo",
            "git_sha": "deadbeef",
            "policy_version": "maat-governance-0.2.4",
        },
        tier="lab_harness",
    )
    print(json.dumps(out, indent=2))
    sys.exit(0 if out["promote_decision"] == "lab_only" else 1)
