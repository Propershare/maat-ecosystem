#!/usr/bin/env bash
# Lab runtime spine check — Discovery, Tehuti Core, Maat Memory, optional Guard/Sentinel/DB/gateway.
# Usage: from lab root, optional: source .env
#   LAB_HOST=127.0.0.1 ./scripts/lab-runtime-check.sh
#   LAB_HOST=192.168.4.21 ./scripts/lab-runtime-check.sh
#
# Guard policy smoke (when 8013 /health is 2xx):
#   Sends low-risk POST /decision and asserts JSON has decision + correlation_id echo
#   (same envelope spirit as docs/FIRST-RUN.md). Override correlation:
#     LAB_GUARD_CORRELATION_ID=my-trace-id
#   Skip POST even if Guard is up:
#     LAB_SKIP_GUARD_DECISION=1
set -euo pipefail

LAB_HOST="${LAB_HOST:-127.0.0.1}"
FAIL=0
CRIT_FAIL=0

pass() { echo "  [PASS] $*"; }
fail() { echo "  [FAIL] $*"; FAIL=1; }
crit_fail() { echo "  [FAIL] (critical) $*"; CRIT_FAIL=1; FAIL=1; }

http_code() {
  local url="$1"
  local c
  # Do not use `|| echo 000`: curl may print 000 from -w and still exit non-zero, doubling output.
  c=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 "$url" 2>/dev/null) || true
  [[ -z "$c" ]] && c="000"
  echo "${c//$'\r'/}"
}

# POST /decision smoke: returns 0 if HTTP 200 and body has decision + correlation_id matches header.
# Args: LAB_HOST, correlation id in LAB_GUARD_CORRELATION_ID or auto-generated.
guard_decision_smoke() {
  local host="$1"
  local corr="${LAB_GUARD_CORRELATION_ID:-lab-runtime-check-$(date +%s)-${RANDOM:-0}}"
  local tmp
  tmp=$(mktemp)
  trap 'rm -f "$tmp"' RETURN
  local http
  http="000"
  http=$(curl -sS --connect-timeout 3 -o "$tmp" -w "%{http_code}" -X POST "http://${host}:8013/decision" \
    -H 'Content-Type: application/json' \
    -H "X-Correlation-ID: ${corr}" \
    -d '{"machine_id":"staydangerous","actor":{"id":"lab-runtime-check","role":"agent"},"action":{"kind":"read","resource":"/tmp/.lab-runtime-check","risk":"low"}}' \
    2>/dev/null) || true
  [[ -z "$http" ]] && http="000"
  http="${http//$'\r'/}"
  if [[ ! "$http" =~ ^200$ ]]; then
    echo "    (HTTP $http, body: $(head -c 200 "$tmp" 2>/dev/null | tr -d '\r' | tr '\n' ' '))"
    return 1
  fi
  if ! command -v python3 >/dev/null 2>&1; then
    echo "    (python3 missing; cannot assert JSON — install python3 or set LAB_SKIP_GUARD_DECISION=1)"
    return 1
  fi
  if ! python3 - "$tmp" "$corr" <<'PY'
import json
import sys

path, expect_cid = sys.argv[1], sys.argv[2]
with open(path, encoding="utf-8", errors="replace") as f:
    raw = f.read()
try:
    d = json.loads(raw)
except json.JSONDecodeError:
    sys.exit(2)
cid = d.get("correlation_id")
if cid != expect_cid:
    sys.exit(3)
dec = d.get("decision")
if not isinstance(dec, str) or not dec:
    sys.exit(4)
sys.exit(0)
PY
  then
    local st=$?
    echo "    (assert exit $st; correlation expected: $corr; body head: $(head -c 300 "$tmp" 2>/dev/null | tr -d '\r' | tr '\n' ' '))"
    return 1
  fi
  return 0
}

echo "=== Lab runtime check (host: $LAB_HOST) ==="

# Critical spine: Ka discovery + brain + memory MCP
code=$(http_code "http://${LAB_HOST}:8010/manifest")
if [[ "$code" =~ ^2 ]]; then pass "8010 /manifest -> HTTP $code"; else crit_fail "8010 /manifest -> HTTP $code (expected 2xx)"; fi

code=$(http_code "http://${LAB_HOST}:8010/health")
if [[ "$code" =~ ^2 ]]; then pass "8010 /health -> HTTP $code"; else crit_fail "8010 /health -> HTTP $code"; fi

code=$(http_code "http://${LAB_HOST}:8014/openapi.json")
if [[ "$code" =~ ^2 ]]; then pass "8014 openapi.json -> HTTP $code"; else crit_fail "8014 openapi.json -> HTTP $code"; fi

code=$(http_code "http://${LAB_HOST}:8022/docs")
if [[ "$code" =~ ^2 ]]; then pass "8022 /docs -> HTTP $code"; else crit_fail "8022 /docs -> HTTP $code"; fi

# Optional: Tehuti Guard (+ POST /decision smoke when health OK)
code=$(http_code "http://${LAB_HOST}:8013/health")
if [[ "$code" =~ ^2 ]]; then
  pass "8013 /health -> HTTP $code"
  if [[ "${LAB_SKIP_GUARD_DECISION:-}" == "1" ]]; then
    echo "  [--] LAB_SKIP_GUARD_DECISION=1; skip POST /decision smoke"
  elif guard_decision_smoke "$LAB_HOST"; then
    pass "8013 POST /decision -> 200 + correlation_id echo + decision (smoke)"
  else
    fail "8013 POST /decision smoke (optional)"
  fi
else
  fail "8013 /health -> HTTP $code (optional)"
  echo "  [--] Guard /health unreachable; skip POST /decision smoke"
fi

# Optional: maat-sentinel
code=$(http_code "http://${LAB_HOST}:4242/machines")
if [[ "$code" =~ ^2 ]]; then pass "4242 /machines -> HTTP $code"; else fail "4242 /machines -> HTTP $code (optional)"; fi

if [[ -n "${MAAT_MACHINE_ID:-}" ]]; then
  code=$(http_code "http://${LAB_HOST}:4242/status/${MAAT_MACHINE_ID}")
  if [[ "$code" =~ ^2 ]]; then pass "4242 /status/${MAAT_MACHINE_ID} -> HTTP $code"; else fail "4242 /status/${MAAT_MACHINE_ID} -> HTTP $code"; fi
else
  echo "  [--] MAAT_MACHINE_ID unset; skip 4242 /status/<id>"
fi

# Optional: OpenClaw gateway (may be LAN-only; try loopback)
code=$(http_code "http://127.0.0.1:18790/")
if [[ "$code" =~ ^[23][0-9][0-9]$ ]]; then pass "18790 gateway (127.0.0.1) -> HTTP $code"; else
  code2=$(http_code "http://${LAB_HOST}:18790/")
  if [[ "$code2" =~ ^[23][0-9][0-9]$ ]]; then pass "18790 gateway ($LAB_HOST) -> HTTP $code2"; else
    fail "18790 gateway -> HTTP $code / $code2 (optional; may bind LAN only)"
  fi
fi

# Optional: MAAT Gateway HTTP (scout/analyst/archivist expert surface)
code=$(http_code "http://${LAB_HOST}:8040/health")
if [[ "$code" =~ ^2 ]]; then pass "8040 /health -> HTTP $code"; else fail "8040 /health -> HTTP $code (optional; maat-gateway-server.service)"; fi

# Optional: Postgres reachability if pg_isready exists and we can infer host
if command -v pg_isready >/dev/null 2>&1; then
  if [[ -n "${PGVECTOR_DB_URL:-}" ]]; then
    rest="${PGVECTOR_DB_URL#*@}"
    if [[ "$rest" =~ ^([^:/]+)(:([0-9]+))?/ ]]; then
      PGH="${BASH_REMATCH[1]}"
      PGPORT="${BASH_REMATCH[3]:-5432}"
      if pg_isready -h "$PGH" -p "$PGPORT" >/dev/null 2>&1; then pass "Postgres pg_isready $PGH:$PGPORT"; else fail "Postgres pg_isready $PGH:$PGPORT"; fi
    else
      echo "  [--] Could not parse host from PGVECTOR_DB_URL; skip pg_isready"
    fi
  elif [[ -n "${PGHOST:-}" ]]; then
    PGPORT="${PGPORT:-5432}"
    if pg_isready -h "$PGHOST" -p "$PGPORT" >/dev/null 2>&1; then pass "Postgres pg_isready $PGHOST:$PGPORT"; else fail "Postgres pg_isready $PGHOST:$PGPORT"; fi
  else
    echo "  [--] PGVECTOR_DB_URL / PGHOST unset; skip pg_isready (source .env to enable)"
  fi
else
  echo "  [--] pg_isready not installed; skip Postgres check"
fi

echo "=== Summary ==="
if [[ "$CRIT_FAIL" -eq 0 ]]; then
  echo "Critical spine (8010, 8014,8022): OK"
else
  echo "Critical spine: FAILED — fix Discovery / Tehuti Core / Maat Memory MCP"
fi
if [[ "$FAIL" -eq 0 ]]; then
  echo "All checks passed."
  exit 0
fi
if [[ "$CRIT_FAIL" -ne 0 ]]; then
  echo "Critical failures present — exit 2."
  exit 2
fi
echo "Only optional checks failed — exit 1."
exit 1
