#!/usr/bin/env bash
# Tehuti Guard — canonical build + test for agents and CI.
#
# Builds and tests BOTH halves of this folder:
#   1. Python decision API  (guard/  -> package tehuti-guard-api, POST /decision :8013)
#   2. TS lab helpers        (src/   -> package @tehuti-lab/guard-ldap-helpers, three-ring/LDAP)
#
# Usage (from anywhere):
#   tehuti-guard/scripts/build-and-test.sh            # full build + test
#   tehuti-guard/scripts/build-and-test.sh --py       # Python only
#   tehuti-guard/scripts/build-and-test.sh --ts       # TypeScript only
#
# Exit non-zero on first failure so agents/CI can trust the signal.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GUARD_ROOT="$(cd "$HERE/.." && pwd)"

DO_PY=1
DO_TS=1
case "${1:-}" in
  --py) DO_TS=0 ;;
  --ts) DO_PY=0 ;;
  "" ) ;;
  * ) echo "unknown flag: $1 (use --py | --ts)" >&2; exit 2 ;;
esac

step() { printf '\n\033[1;36m== %s ==\033[0m\n' "$*"; }

if [ "$DO_PY" = "1" ]; then
  step "Python decision API (guard/)"
  cd "$GUARD_ROOT/guard"
  python3 -m pip install -e . >/dev/null
  # Rule unit tests run without network (Sentinel not required).
  PYTHONPATH="$GUARD_ROOT/guard" python3 -m unittest discover -s "$GUARD_ROOT/guard/tests" -v
  # Import smoke: server module must load and expose the CLI entrypoint.
  PYTHONPATH="$GUARD_ROOT/guard" python3 -c "import tehuti_guard.server, tehuti_guard.cli; print('guard import OK', tehuti_guard.__version__)"
fi

if [ "$DO_TS" = "1" ]; then
  step "TypeScript lab helpers (src/)"
  cd "$GUARD_ROOT"
  if [ ! -d node_modules ]; then
    pnpm install --frozen-lockfile || pnpm install
  fi
  pnpm build
  pnpm test
fi

step "Tehuti Guard build + test: ALL GREEN"
