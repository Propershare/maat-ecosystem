#!/usr/bin/env bash
# Preload OpenClaw's default Ollama model so the first chat reply is fast.
# Run after Ollama starts (e.g. on boot or after: systemctl start ollama).
# Usage: OLLAMA_MODEL=qwen3:latest bash /home/suspect/.n8n/scripts/ollama-warmup.sh

set -e
MODEL="${OLLAMA_MODEL:-llama3.2:3b}"
OLLAMA_URL="${OLLAMA_URL:-http://127.0.0.1:11434}"

echo "Warming up Ollama model: $MODEL"
# Wait for Ollama to be up after a restart
for i in 1 2 3 4 5 6 7 8 9 10; do
  if curl -s -m 5 "${OLLAMA_URL}/api/tags" >/dev/null 2>&1; then break; fi
  echo "Waiting for Ollama... ($i/10)"
  sleep 3
done
# Load model and keep in memory 24h; minimal prompt
curl -s -X POST "${OLLAMA_URL}/api/generate" \
  -d "{\"model\":\"$MODEL\",\"prompt\":\"OK\",\"stream\":false,\"keep_alive\":\"24h\"}" \
  --max-time 180 -o /dev/null -w "HTTP %{http_code} in %{time_total}s\n" || true
echo "Done. Model $MODEL should stay loaded (OLLAMA_KEEP_ALIVE=24h)."
