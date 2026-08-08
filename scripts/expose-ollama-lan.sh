#!/usr/bin/env bash
#
# Expose the tuned Ollama (suspect's /home/suspect/.ollama store, 0.20.0)
# on the LAN as the canonical systemd `ollama.service`.
#
#   - Runs as user `suspect` (so it uses /home/suspect/.ollama -> your tehuti-scholar models)
#   - Binds 0.0.0.0:11434 (reachable from other machines as http://192.168.4.21:11434)
#   - Keeps the tuned GPU env from the current hand-started instance
#   - Opens ufw for 11434/tcp
#
# Run with sudo:  sudo bash scripts/expose-ollama-lan.sh
set -euo pipefail

OLLAMA_BIN="/home/suspect/.local/ollama-0.20.0/bin/ollama"
PORT="11434"
DROPIN_DIR="/etc/systemd/system/ollama.service.d"

if [[ $EUID -ne 0 ]]; then
  echo "Run this with sudo: sudo bash scripts/expose-ollama-lan.sh" >&2
  exit 1
fi

echo "==> Stopping any hand-started loopback serve (port 11435) ..."
pkill -f "ollama serve" 2>/dev/null || true
sleep 2

echo "==> Writing systemd drop-in: ${DROPIN_DIR}/override.conf"
mkdir -p "$DROPIN_DIR"
cat > "${DROPIN_DIR}/override.conf" <<EOF
[Service]
# Run as the lab user so the 80G /home/suspect/.ollama model store is used
User=suspect
Group=suspect
Environment="HOME=/home/suspect"

# Use the pinned 0.20.0 binary that matches the tuned instance
ExecStart=
ExecStart=${OLLAMA_BIN} serve

# --- Network: LAN-reachable ---
Environment="OLLAMA_HOST=0.0.0.0:${PORT}"
Environment="OLLAMA_ORIGINS=*"

# --- Tuned GPU env (carried over from the hand-started instance) ---
Environment="OLLAMA_CUDA=1"
Environment="OLLAMA_NUM_GPU_LAYERS=99"
Environment="OLLAMA_GPU_MEMORY_FRACTION=0.85"
Environment="OLLAMA_MAX_VRAM=12GB"
Environment="OLLAMA_FLASH_ATTENTION=true"
Environment="OLLAMA_KV_CACHE_TYPE=q4_0"
Environment="OLLAMA_NUM_CTX=8192"
Environment="OLLAMA_NUM_BATCH=512"
Environment="OLLAMA_NUM_THREADS=24"
Environment="OLLAMA_NUM_PARALLEL=1"
Environment="OLLAMA_MAX_LOADED_MODELS=4"
Environment="OLLAMA_KEEP_ALIVE=30m"
Environment="OLLAMA_REQUEST_TIMEOUT=900"
Environment="OLLAMA_METRICS=1"
Environment="OLLAMA_LOG_LEVEL=info"
EOF

echo "==> Reloading systemd and (re)starting ollama.service ..."
systemctl daemon-reload
systemctl enable ollama.service
systemctl restart ollama.service
sleep 4

echo "==> Opening firewall for ${PORT}/tcp ..."
if command -v ufw >/dev/null 2>&1; then
  ufw allow "${PORT}/tcp" || true
fi

echo "==> Verifying ..."
systemctl --no-pager --full status ollama.service | head -12 || true
echo "--- local API ---"
curl -s --max-time 6 "http://127.0.0.1:${PORT}/api/version" && echo
echo "--- LAN API (192.168.4.21) ---"
curl -s --max-time 6 "http://192.168.4.21:${PORT}/api/version" && echo
echo
echo "Done. From other machines point tools at:  http://192.168.4.21:${PORT}"
