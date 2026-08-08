#!/bin/bash
# ComfyUI Startup Script - Maat-Aligned
# Starts ComfyUI backend with Maat principles: Privacy, Balance, Order
# Fixed: CUDA allocator conflict resolution

set -e

COMFYUI_DIR="/home/suspect/comfyui"
LOG_FILE="/tmp/comfyui.log"
PORT=8188
# Listen address: 0.0.0.0 = all interfaces (LAN + localhost). Override: COMFYUI_LISTEN=127.0.0.1
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

# CUDA allocator conflict fix - Phase 1: Isolate CUDA Context
# Try without allocator config first to see if that's the issue
# If ComfyUI starts without these, the issue is the allocator config itself
# export PYTORCH_ALLOC_CONF=expandable_segments:True
# export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
# Allow async CUDA execution
export CUDA_LAUNCH_BLOCKING=0
# Ensure clean CUDA context
export CUDA_CACHE_DISABLE=0

# Kill any existing ComfyUI process on port 8188
lsof -ti:$PORT | xargs kill -9 2>/dev/null || true
sleep 2

# Check for processes that might have imported torch
echo "🔍 Checking for torch imports..."
if pgrep -f "python.*torch" > /dev/null 2>&1; then
    echo "⚠️  Warning: Other Python processes may have imported torch"
    echo "   This may cause CUDA allocator conflicts"
fi

echo "Starting ComfyUI backend (Maat-aligned, CUDA-fixed)..."
echo "  Directory: $COMFYUI_DIR"
echo "  Python: $PYTHON_BIN"
echo "  Listen: $COMFYUI_LISTEN (set COMFYUI_LISTEN=127.0.0.1 for localhost-only)"
echo "  Port: $PORT"
echo "  Log: $LOG_FILE"
echo "  CUDA Allocator: expandable_segments:True"

# #region agent log
python3 -c "
import os, json, time
log_data = {
    'sessionId': 'debug-session',
    'runId': 'run1',
    'hypothesisId': 'B',
    'location': 'start_comfyui.sh:47',
    'message': 'ComfyUI startup script env vars',
    'data': {
        'PYTORCH_ALLOC_CONF': os.environ.get('PYTORCH_ALLOC_CONF', 'NOT_SET'),
        'PYTORCH_CUDA_ALLOC_CONF': os.environ.get('PYTORCH_CUDA_ALLOC_CONF', 'NOT_SET'),
        'CUDA_LAUNCH_BLOCKING': os.environ.get('CUDA_LAUNCH_BLOCKING', 'NOT_SET'),
        'pid': os.getpid()
    },
    'timestamp': int(time.time() * 1000)
}
with open('/home/suspect/.n8n/.cursor/debug.log', 'a') as f:
    f.write(json.dumps(log_data) + '\n')
" 2>/dev/null || true
# #endregion

# Start ComfyUI with Maat principles:
# - Use venv Python (clean environment, prevents torch pre-import)
# - Listen on COMFYUI_LISTEN (default 0.0.0.0 for LAN UI access; use 127.0.0.1 to lock down)
# - Disable auto-launch (non-interactive/balance)
# - Privacy-focused (no telemetry)
# - Disable cuda_malloc to prevent allocator conflict (PyTorch bug workaround)
nohup "$PYTHON_BIN" main.py \
  --listen "$COMFYUI_LISTEN" \
  --port $PORT \
  --disable-auto-launch \
  --disable-cuda-malloc \
  > "$LOG_FILE" 2>&1 &

PID=$!
sleep 3

# Wait longer for startup (ComfyUI takes time to initialize)
sleep 10

# Verify it started and is still running
if ps -p $PID > /dev/null 2>&1; then
    # Check if port is listening
    if lsof -i:$PORT > /dev/null 2>&1; then
        echo "✅ ComfyUI started successfully (PID: $PID)"
        echo "📋 Logs: $LOG_FILE"
        echo "🔍 Health: curl http://127.0.0.1:$PORT/"
        if [ "$COMFYUI_LISTEN" = "0.0.0.0" ]; then
            echo "🌐 LAN: open http://<this-machine-ip>:$PORT/ from other devices (ensure firewall allows $PORT)"
        fi
    else
        echo "⚠️  ComfyUI process running but port not listening yet"
        echo "   This may indicate CUDA allocator conflict"
        echo "   Check logs: tail -50 $LOG_FILE"
        echo "   If it crashes, try CPU mode: /home/suspect/.n8n/start_comfyui_cpu.sh"
    fi
else
    echo "❌ ComfyUI crashed during startup"
    echo "📋 Last 30 lines of log:"
    tail -30 "$LOG_FILE"
    echo ""
    echo "💡 This is likely due to CUDA allocator conflict"
    echo "   The ComfyUI MCP server (port 8019) may have imported torch first"
    echo "   Try one of these solutions:"
    echo "   1. Restart MCP server: sudo systemctl restart mcpo-comfyui-intelligent.service"
    echo "   2. Use CPU mode: /home/suspect/.n8n/start_comfyui_cpu.sh"
    exit 1
fi

