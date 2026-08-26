#!/usr/bin/env bash
# Local smoke — delegates to the full atomic lab bench workflow.
# Run from anywhere: bash scripts/run-tehuti-local-tests.sh
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export LAB_BENCH_LIVE=1
exec bash "$ROOT/scripts/run-lab-bench-workflow.sh"
