#!/usr/bin/env bash
# Refresh GITMAAT-CONTEXT.md from gitMaat. For use from cron or systemd timer.
# Run from workspace root: /home/suspect/.n8n
# Example cron (hourly): 0 * * * * /home/suspect/.n8n/scripts/refresh-gitmaat-context-cron.sh

set -e
WORKSPACE_ROOT="${OPENCLAW_WORKSPACE:-/home/suspect/.n8n}"
cd "$WORKSPACE_ROOT"
SCRIPT_DIR="${WORKSPACE_ROOT}/maatlangchain/scripts"
if [[ -x "${SCRIPT_DIR}/refresh_gitmaat_context.sh" ]]; then
  bash "${SCRIPT_DIR}/refresh_gitmaat_context.sh"
elif [[ -f "${SCRIPT_DIR}/query_gitmaat.py" ]]; then
  python3 "${SCRIPT_DIR}/query_gitmaat.py" --out GITMAAT-CONTEXT.md
fi
