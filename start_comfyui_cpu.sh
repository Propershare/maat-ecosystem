#!/bin/bash
# ComfyUI CPU-Only Startup Script - Maat-Aligned Fallback
# Use this if GPU/CUDA conflicts persist

set -e

COMFYUI_DIR="/home/suspect/comfyui"
LOG_FILE="/tmp/comfyui-cpu.log"
PORT=8188
COMFYUI_LISTEN="${COMFYUI_LISTEN:-0.0.0.0}"
PYTHON_BIN="$COMFYUI_DIR/venv/bin/python3"

cd "$COMFYUI_DIR"

# Verify venv Python exists
if [ ! -f "$PYTHON_BIN" ]; then
    echo "❌ Error: venv Python not found at $PYTHON_BIN"
    exit 1
fi

# Maat-aligned: Privacy-focused (disable telemetry)
export HF_HUB_DISABLE_TELEMETRY=1
export DO_NOT_TRACK=1
export PYTHONUNBUFFERED=1

# Force CPU-only mode (no CUDA)
export CUDA_VISIBLE_DEVICES=""

# Kill any existing ComfyUI process on port 8188
lsof -ti:$PORT | xargs kill -9 2>/dev/null || true
sleep 2

echo "Starting ComfyUI backend (CPU-only mode, Maat-aligned)..."
echo "  Directory: $COMFYUI_DIR"
echo "  Python: $PYTHON_BIN"
echo "  Listen: $COMFYUI_LISTEN"
echo "  Port: $PORT"
echo "  Mode: CPU-only (no GPU)"
echo "  Log: $LOG_FILE"

# Start ComfyUI with CPU-only mode
# - Use venv Python (clean environment)
# - Listen on COMFYUI_LISTEN (default 0.0.0.0 for LAN)
# - Disable auto-launch (non-interactive/balance)
# - Privacy-focused (no telemetry)
# - CPU-only (avoids CUDA conflicts)
nohup "$PYTHON_BIN" main.py \
  --listen "$COMFYUI_LISTEN" \
  --port $PORT \
  --disable-auto-launch \
  --cpu \
  > "$LOG_FILE" 2>&1 &

PID=$!
sleep 5

# Verify it started
if ps -p $PID > /dev/null 2>&1; then
    echo "✅ ComfyUI started in CPU mode (PID: $PID)"
    echo "📋 Logs: $LOG_FILE"
    echo "🔍 Health: curl http://127.0.0.1:$PORT/"
    if [ "$COMFYUI_LISTEN" = "0.0.0.0" ]; then
        echo "🌐 LAN: http://<this-machine-ip>:$PORT/ (firewall must allow $PORT)"
    fi
    echo "⚠️  Note: Running in CPU mode (slower but avoids CUDA conflicts)"
else
    echo "❌ Failed to start ComfyUI"
    tail -30 "$LOG_FILE"
    exit 1
fi

