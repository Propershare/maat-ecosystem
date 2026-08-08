#!/usr/bin/env bash
# Run Paperclip first, then start the OpenClaw gateway (replaces `openclaw gateway run ...`).
# Example:
#   ./start-openclaw-with-paperclip.sh --port 18790 --bind lan --verbose
#
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"${SCRIPT_DIR}/ensure-paperclip.sh"
exec openclaw gateway run "$@"
