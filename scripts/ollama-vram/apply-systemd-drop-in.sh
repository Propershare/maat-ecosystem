#!/usr/bin/env bash
# Apply Ollama systemd overrides (needs sudo). Restarts ollama.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DROP_IN="$SCRIPT_DIR/systemd-ollama-drop-in.conf"
TARGET_DIR="/etc/systemd/system/ollama.service.d"
TARGET_FILE="$TARGET_DIR/override.conf"

if [[ ! -f "$DROP_IN" ]]; then
  echo "Missing $DROP_IN"
  exit 1
fi

sudo mkdir -p "$TARGET_DIR"
sudo cp "$DROP_IN" "$TARGET_FILE"
sudo systemctl daemon-reload
sudo systemctl restart ollama
echo "Installed $TARGET_FILE and restarted ollama."
