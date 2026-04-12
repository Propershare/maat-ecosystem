"""
MAAT Report Generator — Produces human-readable and machine-readable reports.
"""

import json
from datetime import datetime, timezone
from pathlib import Path


def generate_text_report(overall: dict, category_results: dict[str, list[dict]],
                         category_scores: dict[str, dict]) -> str:
    """Generate a human-readable text report."""
    lines = []
    lines.append("=" * 60)
    lines.append("🏛️  MaatBench v2 — System Verification Report")
    lines.append("=" * 60)
    lines.append(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    lines.append(f"MAAT Score: {overall['maat_score']:.2%}")
    lines.append(f"Categories tested: {overall['categories_tested']}")
    lines.append("")

    # Category breakdown
    lines.append("─" * 60)
    lines.append("Category Scores")
    lines.append("─" * 60)

    for cat, score_info in category_scores.items():
        emoji = "✅" if score_info["score"] >= 1.0 else "⚠️" if score_info["score"] >= 0.7 else "❌"
        lines.append(
            f"  {emoji} {cat:25s}  {score_info['score']:6.2%}  "
            f"({score_info['passed']}/{score_info['total']} passed)"
        )

    lines.append("")

    # Individual test results
    for cat, results in category_results.items():
        lines.append("─" * 60)
        lines.append(f"  {cat}")
        lines.append("─" * 60)
        for r in results:
            emoji = "✅" if r["passed"] else "❌"
            lines.append(f"    {emoji} {r['name']}")
            if r.get("notes"):
                lines.append(f"       {r['notes']}")
        lines.append("")

    # Bottom line
    lines.append("=" * 60)
    maat = overall["maat_score"]
    if maat >= 0.95:
        verdict = "🏛️  MAAT COMPLIANT — System guarantees verified."
    elif maat >= 0.8:
        verdict = "⚠️  MOSTLY COMPLIANT — Some guarantees need attention."
    elif maat >= 0.5:
        verdict = "🔧 PARTIAL — Significant gaps in system guarantees."
    else:
        verdict = "❌ NON-COMPLIANT — Claims cannot be defended."

    lines.append(verdict)
    lines.append(f"MAAT Compliance: {maat:.2%}")
    lines.append("=" * 60)

    return "\n".join(lines)


def generate_json_report(overall: dict, category_results: dict[str, list[dict]],
                         category_scores: dict[str, dict]) -> str:
    """Generate a machine-readable JSON report."""
    report = {
        "benchmark": "maatbench-v2",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "maat_score": overall["maat_score"],
        "categories_tested": overall["categories_tested"],
        "category_scores": {k: v for k, v in category_scores.items()},
        "results": {k: v for k, v in category_results.items()},
    }
    return json.dumps(report, indent=2)


def save_report(content: str, path: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
