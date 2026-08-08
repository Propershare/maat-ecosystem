#!/usr/bin/env bash
# Quick OpenAI-compatible chat against a local llama-server.
set -euo pipefail
PORT="${LLAMA_PORT:-9080}"
curl -sS "http://127.0.0.1:${PORT}/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen","messages":[{"role":"user","content":"Reply with exactly: OK"}],"max_tokens":32,"temperature":0}' | head -c 2000
echo
