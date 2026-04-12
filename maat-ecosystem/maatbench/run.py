#!/usr/bin/env python3
"""
MaatBench v2 — Run all system verification tests.

Usage:
    python3 -m maatbench.run                    # run all
    python3 -m maatbench.run --category policy  # run one category
    python3 -m maatbench.run --report json      # JSON output
    python3 -m maatbench.run --verbose          # show each test
    python3 -m maatbench.run --save report.json # save to file
"""

import sys
import json
import argparse
from pathlib import Path

# Ensure ecosystem is importable
BENCH_DIR = Path(__file__).resolve().parent
ECOSYSTEM = BENCH_DIR.parent
sys.path.insert(0, str(ECOSYSTEM))
sys.path.insert(0, str(BENCH_DIR.parent))

from maatbench.scorers.scorer import score_category, score_overall
from maatbench.reports.reporter import generate_text_report, generate_json_report, save_report


def load_contract(name: str) -> dict:
    path = BENCH_DIR / "contracts" / name
    return json.loads(path.read_text())


def _runner_for(category: str):
    """Lazy import so `--category contract_integrity` works without optional maat_core."""
    if category == "contract_integrity":
        from maatbench.runners.schema_runner import run_schema_tests

        return run_schema_tests
    if category == "policy_fidelity":
        from maatbench.runners.policy_runner import run_policy_tests

        return run_policy_tests
    if category == "memory_fidelity":
        from maatbench.runners.memory_runner import run_memory_tests

        return run_memory_tests
    if category == "event_fidelity":
        from maatbench.runners.event_runner import run_event_tests

        return run_event_tests
    if category == "portability":
        from maatbench.runners.portability_runner import run_portability_tests

        return run_portability_tests
    if category == "learning_safety":
        from maatbench.runners.learning_runner import run_learning_tests

        return run_learning_tests
    raise ValueError(f"unknown category: {category}")


CATEGORIES = {
    "contract_integrity": "schema_tests.json",
    "policy_fidelity": "policy_tests.json",
    "memory_fidelity": "memory_tests.json",
    "event_fidelity": "event_tests.json",
    "portability": "portability_tests.json",
    "learning_safety": "learning_tests.json",
    # behavior_balance requires a running model — skip by default
}


def main():
    parser = argparse.ArgumentParser(description="MaatBench v2 — System Verification")
    parser.add_argument("--category", help="Run only this category")
    parser.add_argument("--report", choices=["text", "json"], default="text")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--save", help="Save report to file")
    args = parser.parse_args()

    # Select categories
    if args.category:
        if args.category not in CATEGORIES:
            print(f"Unknown category: {args.category}")
            print(f"Available: {', '.join(CATEGORIES.keys())}")
            sys.exit(1)
        cats = {args.category: CATEGORIES[args.category]}
    else:
        cats = dict(CATEGORIES)

    # Run tests
    all_results = {}
    all_scores = {}

    for cat_name, contract_file in cats.items():
        runner_fn = _runner_for(cat_name)
        contract = load_contract(contract_file)
        tests = contract.get("tests", [])

        if args.verbose:
            print(f"\n🧪 Running {cat_name} ({len(tests)} tests)...")

        results = runner_fn(tests)
        all_results[cat_name] = results
        all_scores[cat_name] = score_category(results)

        if args.verbose:
            for r in results:
                emoji = "✅" if r["passed"] else "❌"
                print(f"  {emoji} {r['name']}")
                if r.get("notes"):
                    print(f"     {r['notes']}")

    # Score
    overall = score_overall(all_scores)

    # Report
    if args.report == "json":
        output = generate_json_report(overall, all_results, all_scores)
    else:
        output = generate_text_report(overall, all_results, all_scores)

    print(output)

    # Save
    if args.save:
        ext = ".json" if args.report == "json" else ".txt"
        save_path = args.save if args.save.endswith(ext) else args.save + ext
        save_report(output, save_path)
        print(f"\n📊 Report saved to {save_path}")

    # Exit code
    if overall["maat_score"] >= 0.9:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
