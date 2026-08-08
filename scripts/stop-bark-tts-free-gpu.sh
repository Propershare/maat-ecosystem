#!/bin/bash
# Stop Bark TTS (Tehuti Audio) and disable it so it doesn't respawn. Frees ~4.5 GB GPU.
# To re-enable later: systemctl --user enable mcpo-tehuti-audio.service && systemctl --user start mcpo-tehuti-audio.service

# Kill any running Bark TTS process
pkill -9 -f bark_tts_api.py 2>/dev/null || true
sleep 1

# Stop and disable (try user first, then system)
systemctl --user stop mcpo-tehuti-audio.service 2>/dev/null || true
systemctl --user disable mcpo-tehuti-audio.service 2>/dev/null || true
sudo systemctl stop mcpo-tehuti-audio.service 2>/dev/null || true
sudo systemctl disable mcpo-tehuti-audio.service 2>/dev/null || true

echo "Bark TTS stopped and disabled. Run 'nvidia-smi' to confirm GPU is free."
echo "To turn it back on (user): systemctl --user enable mcpo-tehuti-audio.service && systemctl --user start mcpo-tehuti-audio.service"
echo "To turn it back on (system): sudo systemctl enable mcpo-tehuti-audio.service && sudo systemctl start mcpo-tehuti-audio.service"
