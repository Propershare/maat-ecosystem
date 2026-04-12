"""
MAAT Scorer — Computes category scores and overall MAAT compliance score.
"""

from typing import Any


def score_category(results: list[dict]) -> dict:
    """Score a single test category."""
    if not results:
        return {"score": 0.0, "passed": 0, "failed": 0, "total": 0}

    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    score = passed / total if total > 0 else 0.0

    return {
        "score": round(score, 4),
        "passed": passed,
        "failed": total - passed,
        "total": total,
    }


def score_overall(category_scores: dict[str, dict]) -> dict:
    """
    Compute overall MAAT compliance score.

    MAAT Score = average of all category scores.

    Categories:
    - contract_integrity
    - policy_fidelity
    - memory_fidelity
    - event_fidelity
    - portability
    - behavior_balance (optional — requires running model)
    - learning_safety
    """
    scores = [v["score"] for v in category_scores.values() if v["total"] > 0]

    if not scores:
        return {"maat_score": 0.0, "categories_tested": 0}

    maat_score = sum(scores) / len(scores)

    return {
        "maat_score": round(maat_score, 4),
        "categories_tested": len(scores),
        "category_scores": {k: v["score"] for k, v in category_scores.items()},
    }
