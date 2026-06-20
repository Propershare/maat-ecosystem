#!/usr/bin/env bash
# Install automated lab bench — systemd timer and/or OpenClaw cron.
#
# Usage:
#   bash scripts/setup-lab-bench-automation.sh systemd    # daily 07:00 via systemd
#   bash scripts/setup-lab-bench-automation.sh openclaw   # register OpenClaw cron job
#   bash scripts/setup-lab-bench-automation.sh status     # show timer/cron state
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKFLOW="$ROOT/scripts/run-lab-bench-workflow.sh"
MODE="${1:-status}"

install_systemd() {
  echo "Installing lab-bench-workflow systemd units (user must run sudo for system scope)..."
  sudo cp "$ROOT/systemd-services/lab-bench-workflow.service" /etc/systemd/system/
  sudo cp "$ROOT/systemd-services/lab-bench-workflow.timer" /etc/systemd/system/
  sudo systemctl daemon-reload
  sudo systemctl enable --now lab-bench-workflow.timer
  systemctl status lab-bench-workflow.timer --no-pager || true
  echo "Next run: systemctl list-timers lab-bench-workflow.timer"
}

install_openclaw_cron() {
  if ! command -v openclaw >/dev/null 2>&1; then
    echo "openclaw CLI not on PATH — install OpenClaw first."
    exit 1
  fi
  echo "Registering OpenClaw cron job: lab-bench-daily (07:00 local, isolated run)..."
  # Hermes-style positional schedule; command runs the atomic workflow script.
  openclaw cron add "0 7 * * *" \
    --name "lab-bench-daily" \
    --command "bash $WORKFLOW" \
    --session isolated \
    --announce false \
    || echo "If job exists, use: openclaw cron list"
  openclaw cron list 2>/dev/null || true
}

show_status() {
  echo "=== systemd timer ==="
  systemctl is-active lab-bench-workflow.timer 2>/dev/null || echo "  (not installed)"
  systemctl list-timers lab-bench-workflow.timer 2>/dev/null || true
  echo ""
  echo "=== OpenClaw cron ==="
  if command -v openclaw >/dev/null 2>&1; then
    openclaw cron list 2>/dev/null || echo "  (gateway unreachable or no jobs)"
  else
    echo "  openclaw not on PATH"
  fi
  echo ""
  echo "Manual run: bash $WORKFLOW"
}

case "$MODE" in
  systemd) install_systemd ;;
  openclaw) install_openclaw_cron ;;
  status) show_status ;;
  *)
    echo "Usage: $0 {systemd|openclaw|status}"
    exit 1
    ;;
esac
