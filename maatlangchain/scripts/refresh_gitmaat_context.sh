#!/usr/bin/env bash
# Refresh GITMAAT-CONTEXT.md from shared gitMaat so OpenCode/agents on this PC
# see current tasks and recent activity from all workstations.
# Run from workspace root when you open the project (or periodically).

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Workspace root = parent of maatlangchain (script lives in maatlangchain/scripts)
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$WORKSPACE_ROOT"
python3 "$SCRIPT_DIR/query_gitmaat.py" --out GITMAAT-CONTEXT.md
echo "Refreshed GITMAAT-CONTEXT.md in $(pwd)"
