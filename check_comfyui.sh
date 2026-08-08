#!/bin/bash
# ComfyUI Health Check Script - Maat-Aligned
# Verifies ComfyUI backend is running and responding

set -e

PORT=8188
URL="http://127.0.0.1:$PORT"

echo "🔍 Checking ComfyUI backend status..."
echo ""

# Check if process is running
if pgrep -f "main.py.*$PORT" > /dev/null; then
    PID=$(pgrep -f "main.py.*$PORT" | head -1)
    echo "✅ Process running (PID: $PID)"
else
    echo "❌ Process not running"
    exit 1
fi

# Check if port is listening
if lsof -i:$PORT > /dev/null 2>&1; then
    echo "✅ Port $PORT is listening"
else
    echo "⚠️  Port $PORT not listening (process may be starting)"
fi

# Check HTTP response
echo ""
echo "🌐 Testing HTTP endpoint..."
HTTP_CODE=$(curl -sS -o /dev/null -w "%{http_code}" --max-time 5 "$URL" 2>&1 || echo "000")

if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "000" ]; then
    if [ "$HTTP_CODE" = "200" ]; then
        echo "✅ HTTP endpoint responding (200 OK)"
    else
        echo "⚠️  HTTP endpoint not responding (may be starting)"
        echo "   Check logs: tail -50 /tmp/comfyui.log"
    fi
else
    echo "⚠️  HTTP endpoint returned: $HTTP_CODE"
fi

# Check GPU usage
echo ""
echo "🎮 GPU Status:"
if command -v nvidia-smi > /dev/null 2>&1; then
    nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv 2>&1 | grep -E "python|comfy" || echo "  No ComfyUI processes using GPU"
else
    echo "  nvidia-smi not available"
fi

# Check logs for errors
echo ""
echo "📋 Recent log entries:"
tail -10 /tmp/comfyui.log 2>/dev/null | grep -E "Error|Traceback|Segmentation|CUDA|listening|Started" || echo "  No relevant log entries"

echo ""
echo "✅ Health check complete"

