#!/usr/bin/env bash
#
# Start the MAAT Gateway HTTP server.
#
# Defaults: binds 127.0.0.1:8040, no auth token (local only).
# For LAN exposure: set GATEWAY_SERVER_BIND=0.0.0.0 and GATEWAY_SERVER_TOKEN=<secret>.
#
# Env vars respected:
#   GATEWAY_SERVER_BIND     (default 127.0.0.1)
#   GATEWAY_SERVER_PORT     (default 8040)
#   GATEWAY_SERVER_TOKEN    (optional Bearer token; required for non-loopback)
#   OLLAMA_URL              (default http://127.0.0.1:11434)
#   GATEWAY_OLLAMA_TIMEOUT  (default 120)

set -euo pipefail

LAB_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$LAB_ROOT/gemma4-toolshim/swarm"

# Source .env if present so PGVECTOR_DB_URL etc. are available to gitMaat.
if [[ -f "$LAB_ROOT/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$LAB_ROOT/.env"
  set +a
fi

exec python3 gateway_server.py "$@"
