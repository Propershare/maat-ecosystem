#!/usr/bin/env bash
# Start the MAAT Sentinel daemon — subscribes to archivist stream,
# writes alerts and per-session state. See docs/USING-GATEWAYS-FROM-ANY-CHANNEL.md.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LAB_ROOT="$(cd "$HERE/.." && pwd)"

if [ -f "$LAB_ROOT/.env" ]; then
  set -a
  # shellcheck disable=SC1091
  source "$LAB_ROOT/.env"
  set +a
fi

cd "$LAB_ROOT"
exec python3 -u "$LAB_ROOT/gemma4-toolshim/swarm/sentinel_daemon.py" "$@"
