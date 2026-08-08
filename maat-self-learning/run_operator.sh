#!/usr/bin/env bash
# MAAT Self-Learning Agent — Increment 1 launcher.
# Wires a tool-capable OPERATOR into maat-runtime with the immune hook enabled,
# runs one bounded sandboxed task, and writes the immune trail + session events.
#
# Design rules honored:
#   - Does NOT build or modify maat-runtime (respects its AGENTS.md).
#   - Refuses cleanly if no operator credential is present (no faked runs).
#   - All writes happen inside ./workspace ; the task includes a sacred-path tripwire
#     that the immune hook must block.
#
# Usage:
#   ./run_operator.sh                 # frontier operator (loads /mnt/data_drive/hermes/.env by default)
#   ./run_operator.sh --local         # local Ollama operator (plumbing proof only)
#   PROVIDER=anthropic MODEL=anthropic/claude-sonnet-4 ./run_operator.sh
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNTIME="${MAAT_RUNTIME_ROOT:-/home/suspect/.n8n/maat-runtime}"
CLI="$RUNTIME/packages/coding-agent/dist/cli.js"
IMMUNE_EXT="$RUNTIME/packages/coding-agent/examples/extensions/maat-immune/index.ts"
ENV_FILE="${MAAT_OPERATOR_ENV_FILE:-/mnt/data_drive/hermes/.env}"
RUN_TIMEOUT="${MAAT_OPERATOR_TIMEOUT:-240}"

STAMP="$(date +%Y%m%d_%H%M%S)"
RUN_DIR="$HERE/runs/$STAMP"
WORKSPACE="$RUN_DIR/workspace"
IMMUNE_LOG="$RUN_DIR/immune.jsonl"
SESSION_LOG="$RUN_DIR/session.jsonl"

LOCAL=false
[[ "${1:-}" == "--local" ]] && LOCAL=true

# --- safe env loading --------------------------------------------------------
# Load key=value lines without `source`/`eval` so secrets are not executed as shell.
if [[ -f "$ENV_FILE" ]]; then
  loaded_keys=()
  while IFS='=' read -r raw_key raw_value || [[ -n "$raw_key" ]]; do
    key="${raw_key#export }"
    key="${key//[[:space:]]/}"
    [[ -z "$key" || "${key:0:1}" == "#" ]] && continue
    [[ "$key" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]] || continue
    value="${raw_value#"${raw_value%%[![:space:]]*}"}"
    value="${value%"${value##*[![:space:]]}"}"
    value="${value%\"}"; value="${value#\"}"
    value="${value%\'}"; value="${value#\'}"
    export "$key=$value"
    case "$key" in
      ANTHROPIC_API_KEY|OPENAI_API_KEY|OPENROUTER_API_KEY|PGVECTOR_DB_URL)
        loaded_keys+=("$key")
        ;;
    esac
  done < "$ENV_FILE"
  if [[ "${#loaded_keys[@]}" -gt 0 ]]; then
    printf 'loaded env keys from %s: %s\n' "$ENV_FILE" "${loaded_keys[*]}"
  else
    printf 'loaded env file %s (no recognized operator/db keys)\n' "$ENV_FILE"
  fi
fi

# --- choose operator ---------------------------------------------------------
PROVIDER="${PROVIDER:-}"
MODEL="${MODEL:-}"
API_KEY="${API_KEY:-}"

is_real_key() {
  local value="${1:-}"
  [[ -n "$value" ]] || return 1
  [[ "$value" != "..." && "$value" != "changeme" && "$value" != "TODO" ]] || return 1
  [[ "${#value}" -ge 20 ]] || return 1
  return 0
}

if [[ "$LOCAL" == "true" ]]; then
  # Local Ollama via OpenAI-compatible endpoint. PLUMBING PROOF ONLY:
  # current local models are weak tool-callers; this proves the trail, not competence.
  PROVIDER="${PROVIDER:-openai}"
  MODEL="${MODEL:-openai/qwen2.5-coder:7b}"   # adjust to a tool-capable model you have pulled
  export OPENAI_BASE_URL="${OPENAI_BASE_URL:-http://127.0.0.1:11434/v1}"
  export OPENAI_API_KEY="${OPENAI_API_KEY:-ollama}"
else
  # Frontier operator. Detect a usable key; refuse cleanly if none.
  if is_real_key "${ANTHROPIC_API_KEY:-}"; then
    PROVIDER="${PROVIDER:-anthropic}"; MODEL="${MODEL:-anthropic/claude-sonnet-4}"
    API_KEY="${API_KEY:-$ANTHROPIC_API_KEY}"
  elif is_real_key "${OPENAI_API_KEY:-}"; then
    PROVIDER="${PROVIDER:-openai}"; MODEL="${MODEL:-openai/gpt-4o}"
    API_KEY="${API_KEY:-$OPENAI_API_KEY}"
  elif is_real_key "${OPENROUTER_API_KEY:-}"; then
    PROVIDER="${PROVIDER:-openrouter}"; MODEL="${MODEL:-anthropic/claude-sonnet-4}"
    API_KEY="${API_KEY:-$OPENROUTER_API_KEY}"
  else
    cat >&2 <<'MSG'
REFUSING TO RUN: no frontier operator credential found.
Maat requires honesty over a faked run. Provide one of:
  export ANTHROPIC_API_KEY=...      (or OPENAI_API_KEY / OPENROUTER_API_KEY)
then re-run:  ./run_operator.sh
Or prove the plumbing locally (weak tool-caller, trail only):
  ./run_operator.sh --local
MSG
    exit 3
  fi
fi

# --- preflight ---------------------------------------------------------------
[[ -f "$CLI" ]] || { echo "maat-runtime CLI not found at $CLI (is the runtime built?)" >&2; exit 4; }
[[ -f "$IMMUNE_EXT" ]] || { echo "immune extension not found at $IMMUNE_EXT" >&2; exit 4; }

mkdir -p "$WORKSPACE"
echo "# scratch workspace for MAAT self-learning increment 1" > "$WORKSPACE/README.md"

PROMPT="$(sed -n '/^```$/,/^```$/p' "$HERE/tasks/bounded_task_01.md" | sed '1d;$d')"
[[ -n "$PROMPT" ]] || { echo "could not extract prompt from tasks/bounded_task_01.md" >&2; exit 5; }

# --- immune env (canonical envelope identity) --------------------------------
export MAAT_IMMUNE_LOG="$IMMUNE_LOG"
export MAAT_IMMUNE_STDERR=1
export MAAT_AGENT_ID="operator-${PROVIDER}"
export MAAT_DEVICE_ID="$(hostname)"
export MAAT_TASK_ID="bounded_task_01"

echo "operator   : $PROVIDER / $MODEL"
echo "timeout    : ${RUN_TIMEOUT}s"
echo "workspace  : $WORKSPACE"
echo "immune log : $IMMUNE_LOG"
echo "session    : $SESSION_LOG"
echo "---"

# --- run (non-interactive, json events, immune ext, default tools, ephemeral) 
cd "$WORKSPACE"
: > "$SESSION_LOG"
: > "$RUN_DIR/stderr.log"
set +e
timeout "$RUN_TIMEOUT" node "$CLI" -p --mode json \
  --provider "$PROVIDER" --model "$MODEL" \
  ${API_KEY:+--api-key "$API_KEY"} \
  -e "$IMMUNE_EXT" \
  --tools read,bash,edit,write \
  --no-session \
  "$PROMPT" > "$SESSION_LOG" 2>"$RUN_DIR/stderr.log"
RC=$?
set -e

echo "--- run exited rc=$RC ---"
echo "Harvest the grounded trail with:"
echo "  python3 \"$HERE/harvest_trail.py\" \"$RUN_DIR\""
exit $RC
