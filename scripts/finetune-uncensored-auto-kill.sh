#!/bin/bash
# Fine-tune uncensored model with automatic GPU memory management
# This script kills GPU processes, runs fine-tuning, then restarts services

set -e

echo "🔍 Checking GPU memory usage..."
PIDS_TO_KILL=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader)

if [ -z "$PIDS_TO_KILL" ]; then
    echo "✅ No other GPU processes found. Proceeding with fine-tuning."
else
    echo "⚠️  WARNING: Other processes are using GPU memory."
    echo "   SIGSTOP doesn't free GPU memory - processes must be killed or finished."
    echo ""
    echo "   Current GPU processes:"
    nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader
    echo ""
    echo "🛑 Killing GPU processes to free memory..."
    for pid in $PIDS_TO_KILL; do
        if kill -0 $pid 2>/dev/null; then
            echo "   Killing PID $pid..."
            kill -9 $pid 2>/dev/null || echo "   Could not kill PID $pid"
        fi
    done
    echo "⏳ Waiting 20 seconds for GPU memory to be fully freed..."
    sleep 20
    echo "✅ All GPU processes killed."
    nvidia-smi --query-gpu=memory.free,memory.total --format=csv,noheader,nounits | awk '{print "   Free GPU memory: " $1/1024 " GB / " $2/1024 " GB"}'
    echo "⚠️  You may need to restart these services manually after fine-tuning."
fi

echo "🚀 Starting fine-tuning for uncensored model..."
cd /home/suspect/.n8n
python3 scripts/fine_tune_uncensored_maat.py

echo ""
echo "=== FINE-TUNING COMPLETE ==="
echo ""
echo "✅ Fine-tuning: COMPLETE"
echo "✅ Model saved: fine-tuned-models/tehuti-lab-llama3.1-8b-uncensored-maat/"
echo "✅ Next: Export to GGUF and import to Ollama"
echo ""

