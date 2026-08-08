#!/usr/bin/env bash
# OPTIONAL. Tehuti Core MCP over stdio — exposes powerful tools (execute_command, etc.).
# Only enable from Claude Desktop if you accept remote execution on this server.
set -euo pipefail

LAB_ROOT="${MAAT_LAB_ROOT:-/home/suspect/.n8n}"
CORE_DIR="${LAB_ROOT}/maat-ecosystem/mcp-servers/tehuti-core"
cd "${CORE_DIR}"

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

exec python3 "${CORE_DIR}/tehuti_core_server.py"
