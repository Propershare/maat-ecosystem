#!/usr/bin/env bash
# Atomic lab bench workflow — all agents, all tiers, one MaatBench Evidence Record.
#
# Covers: MCP spine, OpenClaw (:18790), MAAT Gateway (:8040), Hermes skills,
# gemma4 swarm pytest, MaatBench (contracts + lab_spine + evidence record).
#
# Usage (from anywhere):
#   bash scripts/run-lab-bench-workflow.sh
#   LAB_BENCH_LIVE=1 bash scripts/run-lab-bench-workflow.sh
#   LAB_HOST=192.168.4.21 bash scripts/run-lab-bench-workflow.sh
#
# Backward-compatible artifacts:
#   appendices/lab-bench-YYYY-MM-DD.json
#   logs/lab-bench-YYYY-MM-DD.log
# Formal audit artifact:
#   appendices/evidence-records/maatbench-evidence-record-*.json
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
DATE_TAG="$(date +%F)"
REPORT_DIR="$ROOT/docs/Maat-Constitutional-Infrastructure-Dissertation/appendices"
EVIDENCE_DIR="$REPORT_DIR/evidence-records"
REPORT_JSON="$REPORT_DIR/lab-bench-${DATE_TAG}.json"
LOG_DIR="$ROOT/logs"
STATE_JSON="$LOG_DIR/lab-bench-${DATE_TAG}-state.json"
WORKFLOW_LOG="$LOG_DIR/lab-bench-${DATE_TAG}.log"
SCRIPT_INVOKED="${BASH_SOURCE[0]}"
RUN_ID="bench-$(date -u +%Y%m%dT%H%M%SZ)-$$"

mkdir -p "$REPORT_DIR" "$EVIDENCE_DIR" "$LOG_DIR"

LAB_HOST="${LAB_HOST:-127.0.0.1}"
FAIL=0
PYTEST_PASSED=0
PYTEST_FAILED=0
PYTEST_SKIPPED=0
PYTEST_ERRORS=0
PYTEST_EXIT=-1
GATEWAY_8040_CODE="000"

step() { echo ""; echo "=== $* ==="; }
mark_fail() { echo "  [FAIL] $*"; FAIL=1; }
mark_pass() { echo "  [PASS] $*"; }

write_state() {
  LAB_BENCH_LIVE_PY=$([[ "${LAB_BENCH_LIVE:-0}" == "1" ]] && echo "True" || echo "False")
  python3 - <<PY
import json
from pathlib import Path
state = {
    "run_id": "$RUN_ID",
    "started_at": "$STARTED_AT",
    "lab_host": "$LAB_HOST",
    "workflow_fail": $FAIL,
    "tiers": {
        "lab_bench_live": $LAB_BENCH_LIVE_PY,
        "gateway_8040_http_code": "$GATEWAY_8040_CODE",
    },
    "pytest": {
        "passed": $PYTEST_PASSED,
        "failed": $PYTEST_FAILED,
        "skipped": $PYTEST_SKIPPED,
        "errors": $PYTEST_ERRORS,
        "exit_code": $PYTEST_EXIT,
    },
}
Path("$STATE_JSON").write_text(json.dumps(state, indent=2) + "\\n")
PY
}

emit_evidence_record() {
  write_state
  if [[ ! -f "$REPORT_JSON" ]]; then
    echo "  [WARN] No MaatBench report at $REPORT_JSON — evidence record will be partial"
    echo '{"benchmark":"maatbench-v2","results":{},"category_scores":{},"categories_tested":0,"maat_score":0}' > "$REPORT_JSON"
  fi
  echo ""
  echo "=== MaatBench Evidence Record ==="
  python3 "$ROOT/maat-ecosystem/maatbench/evidence/record.py" \
    --state "$STATE_JSON" \
    --maatbench-report "$REPORT_JSON" \
    --workflow-log "$WORKFLOW_LOG" \
    --lab-root "$ROOT" \
    --script "$SCRIPT_INVOKED" \
    --out-dir "docs/Maat-Constitutional-Infrastructure-Dissertation/appendices/evidence-records" \
    || echo "  [WARN] Evidence record generation failed"
}

trap emit_evidence_record EXIT

exec > >(tee -a "$WORKFLOW_LOG") 2>&1

STARTED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "Run ID: $RUN_ID"
echo "Started: $STARTED_AT"

if [[ -f "$ROOT/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$ROOT/.env"
  set +a
fi

step "Tier 0 — Runtime spine (MCP, Guard, OpenClaw, Postgres)"
if bash "$ROOT/scripts/lab-runtime-check.sh"; then
  mark_pass "lab-runtime-check"
else
  rc=$?
  if [[ "$rc" -eq 2 ]]; then
    mark_fail "lab-runtime-check (critical MCP spine)"
  else
    echo "  [WARN] lab-runtime-check optional failures only (exit $rc)"
  fi
fi

step "Tier 0b — MAAT Gateway :8040"
GATEWAY_8040_CODE=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 "http://${LAB_HOST}:8040/health" 2>/dev/null || echo "000")
if [[ "$GATEWAY_8040_CODE" =~ ^2 ]]; then
  mark_pass "8040 /health -> HTTP $GATEWAY_8040_CODE"
else
  echo "  [WARN] 8040 /health -> HTTP $GATEWAY_8040_CODE (optional; start: bash scripts/start-gateway-server.sh)"
fi

step "Tier 1 — Swarm unit tests (offline, all gemma4 experts/gateway)"
PYTEST_TMP="$(mktemp)"
set +e
(
  cd "$ROOT/gemma4-toolshim/swarm"
  python3 -m pytest tests/ -q --tb=no 2>&1 | tee "$PYTEST_TMP"
)
PYTEST_EXIT=$?
set -e
read -r PYTEST_PASSED PYTEST_FAILED PYTEST_SKIPPED PYTEST_ERRORS <<< "$(python3 - <<PY
import re
text = open("$PYTEST_TMP", encoding="utf-8", errors="replace").read()
passed = failed = skipped = errors = 0
m = re.search(r"(\\d+) passed", text)
if m: passed = int(m.group(1))
m = re.search(r"(\\d+) failed", text)
if m: failed = int(m.group(1))
m = re.search(r"(\\d+) skipped", text)
if m: skipped = int(m.group(1))
m = re.search(r"(\\d+) error", text)
if m: errors = int(m.group(1))
print(passed, failed, skipped, errors)
PY
)"
rm -f "$PYTEST_TMP"
if [[ "$PYTEST_EXIT" -eq 0 ]]; then
  mark_pass "pytest gemma4-toolshim/swarm/tests ($PYTEST_PASSED passed)"
else
  mark_fail "pytest swarm tests (exit $PYTEST_EXIT)"
fi

step "Tier 2 — MaatBench (contracts + gateway + lab_spine)"
set +e
(
  cd "$ROOT/maat-ecosystem"
  python3 -m maatbench.run --report json --save "$REPORT_JSON"
)
MB_EXIT=$?
set -e
if [[ "$MB_EXIT" -eq 0 ]]; then
  mark_pass "MaatBench full + lab_spine"
else
  mark_fail "MaatBench (exit $MB_EXIT)"
fi

if [[ "${LAB_BENCH_LIVE:-0}" == "1" ]]; then
  step "Tier 3 — Live model smoke (Ollama + Gemma)"
  if curl -s --max-time 5 "http://127.0.0.1:11434/api/tags" >/dev/null 2>&1; then
    python3 "$ROOT/gemma4-toolshim/test_gemma4_e2b_local.py" && mark_pass "gemma4 e2b"
    OLLAMA_TEST_MODEL=gemma4:e4b python3 "$ROOT/gemma4-toolshim/test_gemma4_e2b_local.py" && mark_pass "gemma4 e4b"
  else
    echo "  [WARN] Ollama not reachable; skip live tier"
  fi
else
  echo ""
  echo "  [--] LAB_BENCH_LIVE=0; skip Ollama/Gemma smoke (set LAB_BENCH_LIVE=1 to enable)"
fi

step "Tier 4 — Hermes skills presence"
HERMES_ROOT="${HERMES_SKILLS_ROOT:-/mnt/data_drive/hermes/skills}"
if [[ -d "$HERMES_ROOT/research/last30days" ]]; then
  mark_pass "Hermes last30days skill"
else
  echo "  [WARN] Hermes skills not at $HERMES_ROOT (mount data drive or set HERMES_SKILLS_ROOT)"
fi

step "Tier 5 — OpenClaw agents (if CLI available)"
if command -v openclaw >/dev/null 2>&1; then
  openclaw agents list 2>/dev/null | head -20 || echo "  [WARN] openclaw agents list failed (gateway down?)"
else
  echo "  [--] openclaw CLI not on PATH"
fi

step "Summary"
if [[ -f "$REPORT_JSON" ]]; then
  python3 - <<PY
import json
from pathlib import Path
p = Path("$REPORT_JSON")
d = json.loads(p.read_text())
cats = d.get("category_scores") or {}
passed = sum(v.get("passed", 0) for v in cats.values())
total = sum(v.get("total", 0) for v in cats.values())
print(f"  MaatBench: {passed}/{total} tests across {d.get('categories_tested', '?')} categories (configured score {d.get('maat_score', '?')})")
print(f"  Report: {p}")
PY
fi
echo "  Workflow log: $WORKFLOW_LOG"
echo "  Evidence records: $EVIDENCE_DIR"

if [[ "$FAIL" -ne 0 ]]; then
  echo "Lab bench workflow FAILED"
  exit 1
fi
echo "Lab bench workflow OK"
exit 0
