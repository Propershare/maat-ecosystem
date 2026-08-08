"""
MAAT Report Generator — Produces human-readable and machine-readable reports.
"""

import json
from datetime import datetime, timezone
from pathlib import Path


def generate_text_report(
    overall: dict, category_results: dict[str, list[dict]], category_scores: dict[str, dict]
) -> str:
    """Generate a human-readable text report."""
    lines = []
    lines.append("=" * 60)
    lines.append("🏛️  MaatBench v2 — System Verification Report")
    lines.append("=" * 60)
    lines.append(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    lines.append(f"MAAT Score (runnable mean): {overall['maat_score']:.2%}")
    lines.append(f"Claim status: {overall.get('claim_status', 'UNKNOWN')}")
    if overall.get("summary"):
        lines.append(f"Summary: {overall['summary']}")
    lines.append(f"Categories tested: {overall['categories_tested']}")
    unproven = overall.get("categories_unproven") or []
    if unproven:
        lines.append(f"Categories unproven: {', '.join(unproven)}")
    if overall.get("git_sha") or overall.get("machine_id"):
        lines.append(
            f"Provenance: sha={overall.get('git_sha')} machine={overall.get('machine_id')} "
            f"dirty={overall.get('dirty')} publishable={overall.get('publishable')}"
        )
        if overall.get("runner_path"):
            lines.append(f"Runner: {overall['runner_path']}")
    if overall.get("note"):
        lines.append(f"Note: {overall['note']}")
    lines.append("")

    # Category breakdown
    lines.append("─" * 60)
    lines.append("Category Scores")
    lines.append("─" * 60)

    for cat, score_info in category_scores.items():
        if int(score_info.get("total") or 0) == 0:
            emoji = "◯"
            lines.append(
                f"  {emoji} {cat:25s}  unproven  "
                f"(0/0 — absence is not compliance)"
            )
            continue
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

    # Bottom line — never call COMPLIANT when any declared category is unproven
    lines.append("=" * 60)
    maat = overall["maat_score"]
    if overall.get("publishable") is False and overall.get("dirty"):
        verdict = "🚫  NOT PUBLISHABLE — dirty working tree (or --allow-dirty). No clean SHA claim."
    elif overall.get("claim_status") == "UNPROVEN" or unproven:
        verdict = "◯  UNPROVEN — Some declared checks did not run (absence ≠ compliance)."
    elif maat >= 0.95:
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


def generate_json_report(
    overall: dict, category_results: dict[str, list[dict]], category_scores: dict[str, dict]
) -> str:
    """Generate a machine-readable JSON report."""
    report = {
        "benchmark": "maatbench-v2",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "maat_score": overall["maat_score"],
        "claim_status": overall.get("claim_status", "UNKNOWN"),
        "summary": overall.get("summary"),
        "categories_tested": overall["categories_tested"],
        "categories_declared": overall.get("categories_declared"),
        "categories_unproven": overall.get("categories_unproven") or [],
        "git_sha": overall.get("git_sha"),
        "git_sha_full": overall.get("git_sha_full"),
        "dirty": overall.get("dirty"),
        "machine_id": overall.get("machine_id"),
        "runner_path": overall.get("runner_path"),
        "publishable": overall.get("publishable"),
        "category_scores": {k: v for k, v in category_scores.items()},
        "results": {k: v for k, v in category_results.items()},
    }
    if overall.get("isfet"):
        report["isfet"] = overall["isfet"]
    if overall.get("note"):
        report["note"] = overall["note"]
    return json.dumps(report, indent=2)


def save_report(content: str, path: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
