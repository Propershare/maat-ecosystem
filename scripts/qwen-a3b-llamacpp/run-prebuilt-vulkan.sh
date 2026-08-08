#!/usr/bin/env bash
# llama-server from GitHub release b9049 (bundles libggml-vulkan.so). GPU only if Vulkan ICD works.
set -euo pipefail

ROOT="/home/suspect/.n8n/vendor/llama-cpp-prebuilt/llama-b9049"
BIN="$ROOT/llama-server"
MODEL="${LLAMA_MODEL:-/home/suspect/models/qwen-a3b-gguf/Qwen3.6-35B-A3B-Q4_K_M.gguf}"
PORT="${LLAMA_PORT:-9080}"

NGL="${NGL:-99}"
N_CPU_MOE="${N_CPU_MOE:-41}"
CTX="${CTX:-16384}"
CTK="${CTK:-q8_0}"
CTV="${CTV:-q8_0}"

export LD_LIBRARY_PATH="$ROOT${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"

exec "$BIN" \
  --model "$MODEL" \
  --host 127.0.0.1 \
  --port "$PORT" \
  --n-gpu-layers "$NGL" \
  --n-cpu-moe "$N_CPU_MOE" \
  --no-mmap \
  --ctx-size "$CTX" \
  --cache-type-k "$CTK" \
  --cache-type-v "$CTV"
