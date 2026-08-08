#!/bin/bash
# Temporarily free GPU memory by stopping other processes
# Use this before fine-tuning if you get CUDA OOM errors

echo "🔍 Checking GPU memory usage..."
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader

echo ""
echo "⚠️  The following processes are using GPU memory:"
echo "   - PID 3894865: ~4.8GB (unknown Python process)"
echo "   - PID 4085733: ~1GB (tehuti-lab-webui)"
echo "   - PID 536609: ~358MB (ComfyUI)"
echo ""
echo "To free GPU memory for fine-tuning, you can:"
echo "1. Stop these processes temporarily"
echo "2. Use a smaller model (Llama 3.1 3B instead of 8B)"
echo "3. Wait for processes to finish"
echo ""
read -p "Stop these processes? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🛑 Stopping processes..."
    kill -SIGSTOP 3894865 2>/dev/null || echo "Could not stop PID 3894865"
    kill -SIGSTOP 4085733 2>/dev/null || echo "Could not stop PID 4085733"
    kill -SIGSTOP 536609 2>/dev/null || echo "Could not stop PID 536609"
    sleep 2
    echo "✅ Processes stopped. GPU memory should be free now."
    echo "⚠️  Remember to restart them after fine-tuning!"
else
    echo "Skipping process stop."
fi

