#!/bin/bash
# Kill all GPU processes to free memory for fine-tuning
# WARNING: This will kill ALL processes using the GPU

set -e

echo "🔍 Checking GPU processes..."
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader

echo ""
echo "⚠️  WARNING: This will KILL ALL processes using the GPU!"
echo "   This includes:"
echo "   - WebUI processes"
echo "   - ComfyUI processes"
echo "   - Any other GPU-accelerated applications"
echo ""
read -p "Continue? (yes/no): " -r
echo

if [[ $REPLY != "yes" ]]; then
    echo "❌ Aborted."
    exit 1
fi

echo "🛑 Killing all GPU processes..."
PIDS=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader | grep -v "^$" || true)

if [ -z "$PIDS" ]; then
    echo "✅ No GPU processes found. GPU memory is already free."
else
    for pid in $PIDS; do
        if kill -0 $pid 2>/dev/null; then
            echo "   Killing PID $pid..."
            kill -9 $pid 2>/dev/null || echo "   Could not kill PID $pid"
        fi
    done
    
    echo "⏳ Waiting 20 seconds for GPU memory to be fully freed..."
    sleep 20
    
    echo "✅ All GPU processes killed."
    nvidia-smi --query-gpu=memory.free,memory.total --format=csv,noheader | awk -F',' '{printf "   Free GPU memory: %.1f GB / %.1f GB\n", $1/1024, $2/1024}'
fi

