#!/bin/bash
# Reload NVIDIA driver without reboot.
# GPU was held by: Bark TTS (mcpo-tehuti-audio) and Ollama.
# Run this script: bash /home/suspect/.n8n/scripts/nvidia-driver-reload-without-reboot.sh
# You will be prompted for sudo for: stopping/starting ollama, rmmod, modprobe.

set -e

echo "=== 1. Stop services holding the GPU ==="
# Stop Tehuti Audio (Bark TTS) - holds /dev/nvidia*
systemctl --user stop mcpo-tehuti-audio.service 2>/dev/null || true
# Stop Ollama (may hold GPU or subprocesses)
sudo systemctl stop ollama 2>/dev/null || true

# Kill any process using nvidia devices (by PID from lsof)
for pid in $(lsof -t /dev/nvidia* 2>/dev/null); do
  echo "Killing PID $pid (had nvidia device open)"
  kill -9 "$pid" 2>/dev/null || true
done

# If Bark TTS was not managed by systemd, kill the process we found
BARK_PID=$(pgrep -f "bark_tts_api.py" 2>/dev/null || true)
if [ -n "$BARK_PID" ]; then
  echo "Stopping Bark TTS process(es) $BARK_PID"
  kill -9 $BARK_PID 2>/dev/null || true
fi

# Kill any remaining ollama processes (runner subprocesses)
sudo pkill -9 -f "ollama" 2>/dev/null || true

echo "Waiting 8s for device release and refcount drop..."
sleep 8

echo "=== 2. Check nothing is using /dev/nvidia* ==="
PIDS=$(lsof -t /dev/nvidia* 2>/dev/null || true)
if [ -n "$PIDS" ]; then
  echo "WARNING: These PIDs still have nvidia devices open: $PIDS"
  for p in $PIDS; do sudo kill -9 "$p" 2>/dev/null; done
  sleep 3
fi
if fuser -v /dev/nvidia* 2>/dev/null; then
  echo "ERROR: Something still using GPU. Aborting."
  exit 1
fi
echo "OK - no processes using GPU."

echo "=== 3. Unload NVIDIA kernel modules ==="
# Order: unload consumers first (drm, modeset), then nvidia_uvm, then nvidia
sudo rmmod nvidia_drm     2>/dev/null || true
sudo rmmod nvidia_modeset 2>/dev/null || true
if ! sudo rmmod nvidia_uvm 2>/dev/null; then
  echo "rmmod nvidia_uvm failed (module in use)."
  echo "The refcount is often from inside the driver, not a user process."
  echo "If no PIDs had /dev/nvidia* open above, the only fix is: sudo reboot"
  exit 1
fi
sudo rmmod nvidia         || { echo "rmmod nvidia failed"; exit 1; }

echo "=== 4. Reload NVIDIA kernel modules ==="
sudo modprobe nvidia
sudo modprobe nvidia_modeset
sudo modprobe nvidia_drm
sudo modprobe nvidia_uvm

echo "=== 5. Verify driver ==="
nvidia-smi || { echo "nvidia-smi failed"; exit 1; }

echo "=== 6. Restart services ==="
sudo systemctl start ollama
systemctl --user start mcpo-tehuti-audio.service 2>/dev/null || true

echo "=== Done. Driver reloaded. Ollama and (if enabled) Tehuti Audio restarted. ==="
