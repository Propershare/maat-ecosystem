#!/bin/bash
# Automatically kill all GPU processes and run fine-tuning
# This is a non-interactive version for automated execution

set -e

echo "🔍 Checking GPU processes..."
PIDS=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader | grep -v "^$" || true)

if [ -z "$PIDS" ]; then
    echo "✅ No GPU processes found. GPU memory is free."
else
    echo "   Current GPU processes:"
    nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader
    echo ""
    echo "🛑 Automatically killing all GPU processes..."
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
    echo "⚠️  You may need to restart these services manually after fine-tuning."
fi

echo ""
echo "🚀 Starting fine-tuning..."
cd /home/suspect/.n8n
python3 scripts/fine_tune_maat.py 2>&1 | tee fine-tuned-models/training.log

echo ""
echo "✅ Fine-tuning complete!"

