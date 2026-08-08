#!/usr/bin/env bash
# SSH local forwards: your machine's 127.0.0.1:8011-8021 -> server's 127.0.0.1:8011-8021
# Use when MCPs on the server listen only on localhost, or you prefer not to open those ports on the LAN.
#
# Lab IPs (reference): server .21, Imhotep .25, MacDaddy .36, imhotepjr .81
#
# Env:
#   TEHUTI_SSH_HOST   default 192.168.4.21
#   TEHUTI_SSH_USER   default suspect
#   TEHUTI_SSH_KEY     optional path to identity, e.g. ~/.ssh/id_ed25519
#
# On your PC, point MCP / Clawd at http://127.0.0.1:8014 (etc.) while this runs.
#
# Requires: server sshd with AllowTcpForwarding (default yes). Keep this terminal open.
#
set -euo pipefail
HOST="${TEHUTI_SSH_HOST:-192.168.4.21}"
USER="${TEHUTI_SSH_USER:-suspect}"

FORWARDS=()
for p in $(seq 8011 8021); do
  FORWARDS+=("-L" "${p}:127.0.0.1:${p}")
done

SSH_CMD=(ssh -N -o ExitOnForwardFailure=yes -o ServerAliveInterval=60 -o ServerAliveCountMax=3)
if [[ -n "${TEHUTI_SSH_KEY:-}" ]]; then
  SSH_CMD+=(-i "$TEHUTI_SSH_KEY")
fi
SSH_CMD+=("${FORWARDS[@]}" "${USER}@${HOST}")

echo "[ssh-tunnel] ${USER}@${HOST}  ->  local ports 8011-8021"
echo "[ssh-tunnel] Use MCP base URLs: http://127.0.0.1:8014 (Tehuti Core), etc."
echo "[ssh-tunnel] Ctrl+C to stop."
exec "${SSH_CMD[@]}"
