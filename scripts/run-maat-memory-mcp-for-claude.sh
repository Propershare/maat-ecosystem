#!/usr/bin/env bash
# Server-side entrypoint: Maat Memory MCP over stdio (for Claude Desktop on another machine via SSH).
# Do not bind a port — Claude Desktop speaks JSON-RPC over stdin/stdout.
set -euo pipefail

LAB_ROOT="${MAAT_LAB_ROOT:-/home/suspect/.n8n}"
MEMORY_DIR="${LAB_ROOT}/maat-ecosystem/mcp-servers/maat-memory"
cd "${MEMORY_DIR}"

if [ -f "${LAB_ROOT}/.env" ]; then
  set -a
  # shellcheck disable=SC1090
  . "${LAB_ROOT}/.env"
  set +a
fi
if [ -f "${LAB_ROOT}/maatlangchain/.env" ]; then
  set -a
  # shellcheck disable=SC1090
  . "${LAB_ROOT}/maatlangchain/.env"
  set +a
fi

exec python3 "${MEMORY_DIR}/maat_memory_server.py"
