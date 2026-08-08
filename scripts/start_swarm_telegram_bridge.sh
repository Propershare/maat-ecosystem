#!/usr/bin/env bash
# Start gemma4-toolshim swarm HTTP bridge (router + gitMaat + RAG + Ollama).
# Default: http://127.0.0.1:18080  — see openclaw/skills/swarm-telegram-bridge/SKILL.md

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export SWARM_BRIDGE_HOST="${SWARM_BRIDGE_HOST:-127.0.0.1}"
export SWARM_BRIDGE_PORT="${SWARM_BRIDGE_PORT:-18080}"
cd "$ROOT/gemma4-toolshim/swarm"
exec python3 -m uvicorn bridge_service:app \
  --host "$SWARM_BRIDGE_HOST" \
  --port "$SWARM_BRIDGE_PORT"
