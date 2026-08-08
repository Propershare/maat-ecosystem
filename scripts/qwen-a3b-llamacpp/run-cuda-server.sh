#!/usr/bin/env bash
# CUDA-built llama-server for Qwen3.6 35B A3B (Hermes / OpenClaw).
set -euo pipefail

BIN="${LLAMA_BIN:-/home/suspect/.n8n/vendor/llama-cpp/build/bin/llama-server}"
MODEL="${LLAMA_MODEL:-/home/suspect/models/qwen-a3b-gguf/Qwen3.6-35B-A3B-Q4_K_M.gguf}"
PORT="${LLAMA_PORT:-9080}"
NGL="${NGL:-99}"
N_CPU_MOE="${N_CPU_MOE:-41}"
CTX="${CTX:-65536}"
CTK="${CTK:-q8_0}"
CTV="${CTV:-q8_0}"

exec "$BIN" \
  --model "$MODEL" \
  --host 127.0.0.1 \
  --port "$PORT" \
  --ctx-size "$CTX" \
  --cache-type-k "$CTK" \
  --cache-type-v "$CTV" \
  --n-gpu-layers "$NGL" \
  --n-cpu-moe "$N_CPU_MOE" \
  --no-mmap \
  --reasoning off \
  --reasoning-budget 0
