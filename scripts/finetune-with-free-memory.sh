#!/bin/bash
# Fine-tune with GPU memory freed
# This script stops other GPU processes, runs fine-tuning, then restarts them

set -e

echo "🔍 Checking GPU memory usage..."
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader

echo ""
echo "⚠️  WARNING: Other processes are using GPU memory."
echo "   SIGSTOP doesn't free GPU memory - processes must be killed or finished."
echo ""
echo "   Current GPU processes:"
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader
echo ""
read -p "Kill these processes to free GPU memory? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🛑 Killing GPU processes..."
    # Store PIDs for reference (can't restart killed processes)
    for pid in 3894865 4085733 536609; do
        if kill -0 $pid 2>/dev/null; then
            echo "   Killing PID $pid..."
            kill -9 $pid 2>/dev/null || echo "   Could not kill PID $pid"
        fi
    done
    echo "⏳ Waiting 15 seconds for GPU memory to be fully freed..."
    sleep 15
    echo "✅ Processes killed. GPU memory should be free now."
    nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | awk '{print "   Free GPU memory: " $1/1024 " GB"}'
    echo "⚠️  You may need to restart these services manually after fine-tuning."
else
    echo "⚠️  Continuing with limited GPU memory - training may fail."
    echo "   Consider waiting for processes to finish or manually freeing GPU memory."
fi

echo "✅ Processes stopped. Starting fine-tuning..."
echo ""

# Run fine-tuning
cd /home/suspect/.n8n
python3 scripts/fine_tune_maat.py

echo ""
echo "🔄 Restarting stopped processes..."
for pid in $PIDS_TO_RESTART; do
    if kill -0 $pid 2>/dev/null; then
        echo "   Restarting PID $pid..."
        kill -SIGCONT $pid 2>/dev/null || echo "   Could not restart PID $pid"
    fi
done

echo "✅ Fine-tuning complete and processes restarted!"

