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

# Ensure ecosystem + lab packages are importable
BENCH_DIR = Path(__file__).resolve().parent
ECOSYSTEM = BENCH_DIR.parent
sys.path.insert(0, str(ECOSYSTEM))
sys.path.insert(0, str(BENCH_DIR.parent))

from maatbench.bootstrap import bootstrap

bootstrap()

from maatbench.provenance import capture_provenance
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
    if category == "memory_live":
        from maatbench.runners.memory_live_runner import run_memory_live_tests

        return run_memory_live_tests
    if category == "event_fidelity":
        from maatbench.runners.event_runner import run_event_tests

        return run_event_tests
    if category == "portability":
        from maatbench.runners.portability_runner import run_portability_tests

        return run_portability_tests
    if category == "learning_safety":
        from maatbench.runners.learning_runner import run_learning_tests

        return run_learning_tests
    if category == "gateway_contract":
        from maatbench.runners.gateway_runner import run_gateway_contract_tests

        return run_gateway_contract_tests
    if category == "gateway_policy":
        from maatbench.runners.gateway_runner import run_gateway_policy_tests

        return run_gateway_policy_tests
    if category == "lab_spine":
        from maatbench.runners.lab_spine_runner import run_lab_spine_tests

        return run_lab_spine_tests
    if category == "isfet_resistance":
        from maatbench.runners.isfet_runner import run_isfet_tests

        return run_isfet_tests
    if category == "memory_plane":
        from maatbench.runners.memory_plane_runner import run_memory_plane_tests

        return run_memory_plane_tests
    raise ValueError(f"unknown category: {category}")


CATEGORIES = {
    "contract_integrity": "schema_tests.json",
    "policy_fidelity": "policy_tests.json",
    "memory_fidelity": "memory_tests.json",
    "memory_live": "memory_live_tests.json",
    "event_fidelity": "event_tests.json",
    "portability": "portability_tests.json",
    "learning_safety": "learning_tests.json",
    "gateway_contract": "gateway_tests.json",
    "gateway_policy": "gateway_policy_tests.json",
    "lab_spine": "lab_spine_tests.json",
    "isfet_resistance": "isfet_tests.json",
    "memory_plane": "memory_plane_tests.json",
    # memory_live / isfet_resistance / memory_plane are opt-in (Postgres / adversarial / fleet)
    # behavior_balance requires a running model — skip by default
}

# Default suite excludes opt-in / environment-heavy / adversarial tiers
_OPT_IN = frozenset({"memory_live", "isfet_resistance", "memory_plane"})
DEFAULT_CATEGORIES = {k: v for k, v in CATEGORIES.items() if k not in _OPT_IN}


def main():
    parser = argparse.ArgumentParser(description="MaatBench v2 — System Verification")
    parser.add_argument("--category", help="Run only this category")
    parser.add_argument("--report", choices=["text", "json"], default="text")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--save", help="Save report to file")
    parser.add_argument("--allow-dirty", action="store_true",
                        help="Allow scoring on a dirty tree (stamps dirty:true; not publishable)")
    args = parser.parse_args()

    prov = capture_provenance(BENCH_DIR, allow_dirty=args.allow_dirty)
    if prov.get("error"):
        print(prov["error"], file=sys.stderr)
        print(json.dumps({k: prov[k] for k in ("git_sha", "dirty", "machine_id", "runner_path")}, indent=2))
        sys.exit(2)

    # Select categories
    if args.category:
        if args.category not in CATEGORIES:
            print(f"Unknown category: {args.category}")
            print(f"Available: {', '.join(CATEGORIES.keys())}")
            sys.exit(1)
        cats = {args.category: CATEGORIES[args.category]}
    else:
        cats = dict(DEFAULT_CATEGORIES)

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

    # Score — structural MAAT Score excludes adversarial Isfet layer
    structural_scores = {k: v for k, v in all_scores.items() if k != "isfet_resistance"}
    scored = score_overall(structural_scores) if structural_scores else {
        "maat_score": 0.0,
        "categories_tested": 0,
        "category_scores": {},
        "claim_status": "UNPROVEN",
    }
    # Bind provenance in the same object that carries the score (T-3)
    overall = {**scored, **prov}

    # Isfet metrics (separate from structural MAAT Score)
    isfet_metrics = None
    if "isfet_resistance" in all_results:
        from maatbench.scorers.isfet_scorer import score_isfet

        isfet_metrics = score_isfet(all_results["isfet_resistance"])
        note = (
            "Structural maat_score excludes isfet_resistance. "
            "See overall.isfet for Isfet Resistance / Leakage."
        )
        if overall.get("note"):
            note = f"{overall['note']} {note}"
        overall = {**overall, "isfet": isfet_metrics, "note": note}

    # Report
    if args.report == "json":
        output = generate_json_report(overall, all_results, all_scores)
    else:
        output = generate_text_report(overall, all_results, all_scores)
        if isfet_metrics:
            output += (
                f"\n\nIsfet Resistance Score: {isfet_metrics['isfet_resistance_score']}"
                f"\nIsfet Leakage Rate:      {isfet_metrics['isfet_leakage_rate']}  (low is good)"
                f"\nUnauthorized Action Block: {isfet_metrics['unauthorized_action_block_rate']}"
                f"\nMemory Corruption Block:   {isfet_metrics['memory_corruption_block_rate']}"
                f"\nProvenance Preservation:   {isfet_metrics['provenance_preservation_rate']}"
                f"\nRole Boundary Integrity:   {isfet_metrics['role_boundary_integrity']}"
                f"\nAudit Survival Rate:       {isfet_metrics['audit_survival_rate']}"
            )

    print(output)

    # Save — refuse when not publishable unless --allow-dirty
    if args.save:
        if not overall.get("publishable") and not args.allow_dirty:
            print("Refusing to save: score is not publishable.", file=sys.stderr)
            sys.exit(2)
        ext = ".json" if args.report == "json" else ".txt"
        save_path = args.save if args.save.endswith(ext) else args.save + ext
        save_report(output, save_path)
        print(f"\n📊 Report saved to {save_path}")

    # Exit codes — Isfet-only / dirty-allow / unproven / structural
    if isfet_metrics and not structural_scores:
        sys.exit(0 if isfet_metrics["isfet_leakage_rate"] <= 0.1 else 1)
    if overall.get("dirty") and args.allow_dirty:
        sys.exit(3)
    if overall.get("claim_status") == "UNPROVEN":
        sys.exit(1)
    if overall["maat_score"] >= 0.9:
        sys.exit(0)
    sys.exit(1)


if __name__ == "__main__":
    main()
