#!/usr/bin/env bash
# Idempotent Paperclip dev server: start only if http://127.0.0.1:3100/api/health is down.
#
# Env (optional):
#   PAPERCLIP_ROOT   - repo root (default: /mnt/data_drive/paperclip)
#   PAPERCLIP_DEV_ARGS - extra args for "pnpm dev" (e.g. --tailscale-auth)
#   NODE_BIN_DIR     - prepend to PATH (default: nvm Node 22 if present)
#
# OpenClaw join (employer/board flow — manual once per company):
#   1) Paperclip UI → company settings → "Generate OpenClaw Invite Prompt"
#   2) Paste prompt into OpenClaw main chat
#   3) Approve the join request in Paperclip
#   4) Gateway URL must match your OpenClaw listener, e.g. ws://<LAN-IP>:18790
#      plus header x-openclaw-token from ~/.openclaw/openclaw.json gateway.auth.token
#
set -euo pipefail

PAPERCLIP_ROOT="${PAPERCLIP_ROOT:-/mnt/data_drive/paperclip}"
HEALTH_URL="${PAPERCLIP_HEALTH_URL:-http://127.0.0.1:3100/api/health}"
LOG_DIR="${HOME}/.paperclip/instances/default/logs"
LOCK="${LOCK:-${HOME}/.paperclip/ensure-paperclip.lock}"
NODE_BIN_DIR="${NODE_BIN_DIR:-}"
if [[ -z "${NODE_BIN_DIR}" ]] && [[ -d "${HOME}/.nvm/versions/node/v22.22.0/bin" ]]; then
  NODE_BIN_DIR="${HOME}/.nvm/versions/node/v22.22.0/bin"
fi
if [[ -n "${NODE_BIN_DIR}" ]]; then
  export PATH="${NODE_BIN_DIR}:${PATH}"
fi

mkdir -p "$(dirname "$LOCK")" "$LOG_DIR"
START_LOG="${LOG_DIR}/ensure-paperclip-start.log"

is_healthy() {
  curl -fsS --connect-timeout 2 --max-time 5 "$HEALTH_URL" >/dev/null 2>&1
}

if is_healthy; then
  echo "[ensure-paperclip] OK (already up): $HEALTH_URL"
  exit 0
fi

(
  flock -n 200 || { echo "[ensure-paperclip] another start in progress; waiting..."; flock 200; }
  if is_healthy; then
    echo "[ensure-paperclip] OK (another instance brought it up)"
    exit 0
  fi

  if [[ ! -d "$PAPERCLIP_ROOT" ]]; then
    echo "[ensure-paperclip] ERROR: PAPERCLIP_ROOT not found: $PAPERCLIP_ROOT" >&2
    exit 1
  fi

  if ! command -v pnpm >/dev/null 2>&1; then
    echo "[ensure-paperclip] ERROR: pnpm not on PATH (set NODE_BIN_DIR or install pnpm)" >&2
    exit 1
  fi

  echo "[ensure-paperclip] starting Paperclip in $PAPERCLIP_ROOT ..."
  # shellcheck disable=SC2086
  nohup bash -c "cd \"$PAPERCLIP_ROOT\" && exec pnpm dev ${PAPERCLIP_DEV_ARGS:-}" \
    >>"$START_LOG" 2>&1 &
  echo $! >"${HOME}/.paperclip/paperclip-dev.pid"

  for _ in $(seq 1 60); do
    if is_healthy; then
      echo "[ensure-paperclip] OK (started): $HEALTH_URL — log: $START_LOG"
      exit 0
    fi
    sleep 1
  done

  echo "[ensure-paperclip] ERROR: health check still failing after 60s (see $START_LOG)" >&2
  exit 1
) 200>"$LOCK"
