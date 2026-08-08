#!/bin/bash
# Start Maat Memory MCP Server — The Memory Organ
# Port: 8022
#
# Ka immune: Bearer auth REQUIRED (--api-key + --strict-auth).
# Absence of a key is not an open organ.
#
# Use .venv (psycopg2-binary + mcp). First-time:
#   cd .../maat-memory && uv venv .venv && uv pip install -r requirements.txt

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKSPACE_ROOT="$HOME/.n8n"

# Load organ/broker secrets (DSN + API key) — never from agent-only env alone
_load_kv() {
  local file="$1"
  local pattern="$2"
  if [ -f "$file" ]; then
    # shellcheck disable=SC2046
    export $(grep -E "$pattern" "$file" | xargs) 2>/dev/null || true
  fi
}

# Broker/organ only — .ka-auth is quarantined (no key material for agents).
_load_kv "$WORKSPACE_ROOT/.env.broker" '^(PGVECTOR_DB_URL|MAAT_MEMORY_ALLOW_DSN|MAAT_CREDENTIAL_ROLE|MCPO_API_KEY|KA_API_KEY)='
_load_kv "$WORKSPACE_ROOT/.env" '^(PGVECTOR_DB_URL)='

export MAAT_MEMORY_ALLOW_DSN="${MAAT_MEMORY_ALLOW_DSN:-1}"
export MAAT_CREDENTIAL_ROLE="${MAAT_CREDENTIAL_ROLE:-broker}"

# Map KA_API_KEY → MCPO_API_KEY when organ key not set explicitly
if [ -z "${MCPO_API_KEY:-}" ] && [ -n "${KA_API_KEY:-}" ]; then
  export MCPO_API_KEY="$KA_API_KEY"
fi

if [ -z "${MCPO_API_KEY:-}" ]; then
  echo "Maat Memory: MCPO_API_KEY or KA_API_KEY required — absence is not an open organ" >&2
  echo "  Set in ~/.n8n/.env.broker (organ/broker). .ka-auth is quarantined." >&2
  exit 1
fi

cd "$SCRIPT_DIR"
PY="${SCRIPT_DIR}/.venv/bin/python"
if [ ! -x "$PY" ]; then
    echo "Maat Memory: missing $PY — uv venv .venv && uv pip install -r requirements.txt" >&2
    PY="python3"
fi

MCPO_ARGS=(
  --host 0.0.0.0
  --port 8022
  --api-key "${MCPO_API_KEY}"
  --strict-auth
)

# Prefer absolute uvx — systemd user units often lack ~/.local/bin on PATH
UVX="${UVX:-}"
if [[ -z "$UVX" ]]; then
  if [[ -x "${HOME}/.local/bin/uvx" ]]; then
    UVX="${HOME}/.local/bin/uvx"
  elif command -v uvx >/dev/null 2>&1; then
    UVX="$(command -v uvx)"
  else
    echo "Maat Memory: uvx not found (install uv or set UVX=)" >&2
    exit 127
  fi
fi

exec "$UVX" --with 'mcp==1.9.4' mcpo "${MCPO_ARGS[@]}" -- "$PY" "$SCRIPT_DIR/maat_memory_server.py"
