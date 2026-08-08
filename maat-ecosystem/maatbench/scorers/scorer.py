"""
MAAT Scorer — Computes category scores and overall MAAT compliance score.

Law: Absence is not compliance.
A check that did not run is unproven, never passed, and unproven is reported
wherever the score is reported.

Publish form (audit B-2):
  "6/9 runnable, 6/6 passed, 3 unproven" — never a silent 9/9 at 1.0.
Unproven categories do not enter the runnable mean; they block COMPLETE claims.
"""


def score_category(results: list[dict]) -> dict:
    """Score a single test category."""
    if not results:
        return {
            "score": 0.0,
            "passed": 0,
            "failed": 0,
            "total": 0,
            "status": "unproven",
        }

    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    score = passed / total if total > 0 else 0.0

    return {
        "score": round(score, 4),
        "passed": passed,
        "failed": total - passed,
        "total": total,
        "status": "tested",
    }


def score_overall(category_scores: dict[str, dict]) -> dict:
    """
    Overall score over *runnable* categories only; unproven listed beside it.

    claim_status is COMPLETE only when every declared category produced tests.
    """
    if not category_scores:
        return {
            "maat_score": 0.0,
            "categories_declared": 0,
            "categories_tested": 0,
            "categories_unproven": [],
            "runnable_passed": 0,
            "runnable_total": 0,
            "claim_status": "UNPROVEN",
            "summary": "0/0 runnable, 0 unproven — nothing declared",
            "note": "No categories declared — absence is not compliance.",
        }

    unproven: list[str] = []
    runnable_scores: list[float] = []
    runnable_passed = 0
    runnable_total = 0

    for name, row in category_scores.items():
        total = int(row.get("total") or 0)
        if total > 0:
            runnable_scores.append(float(row["score"]))
            runnable_passed += int(row.get("passed") or 0)
            runnable_total += total
        else:
            unproven.append(name)

    declared = len(category_scores)
    tested = declared - len(unproven)
    maat_score = (sum(runnable_scores) / len(runnable_scores)) if runnable_scores else 0.0
    claim_status = "UNPROVEN" if unproven or not runnable_scores else "COMPLETE"
    summary = (
        f"{tested}/{declared} runnable, "
        f"{runnable_passed}/{runnable_total} checks passed, "
        f"{len(unproven)} unproven"
    )

    return {
        "maat_score": round(maat_score, 4),
        "categories_declared": declared,
        "categories_tested": tested,
        "categories_unproven": unproven,
        "runnable_passed": runnable_passed,
        "runnable_total": runnable_total,
        "claim_status": claim_status,
        "summary": summary,
        "category_scores": {k: v["score"] for k, v in category_scores.items()},
        "note": (
            "Unproven excluded from runnable mean but always reported (fail-closed claim)."
            if unproven
            else "All declared categories produced tests."
        ),
    }
