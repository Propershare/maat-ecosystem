#!/usr/bin/env bash
# Video-style llama-server via official CUDA image. Requires: Docker with working `docker run --gpus all`
# (Snap Docker often breaks nvidia-container-cli — use docker-ce or fix Snap+NVIDIA.)
set -euo pipefail

IMAGE="${LLAMA_DOCKER_IMAGE:-ghcr.io/ggml-org/llama.cpp:server-cuda}"
MODEL_HOST_PATH="${LLAMA_MODEL:-/home/suspect/models/qwen-a3b-gguf/Qwen3.6-35B-A3B-Q4_K_M.gguf}"
CONTAINER_MODEL="/models/$(basename "$MODEL_HOST_PATH")"
HOST_PORT="${LLAMA_PORT:-9080}"

NGL="${NGL:-99}"
N_CPU_MOE="${N_CPU_MOE:-41}"
CTX="${CTX:-16384}"
CTK="${CTK:-q8_0}"
CTV="${CTV:-q8_0}"

exec docker run --rm --name llama-qwen36-a3b \
  --gpus all \
  --cap-add IPC_LOCK \
  --ulimit memlock=-1:-1 \
  -v "$(dirname "$MODEL_HOST_PATH"):/models:ro" \
  -p "127.0.0.1:${HOST_PORT}:8080" \
  "$IMAGE" \
  --model "$CONTAINER_MODEL" \
  --host 0.0.0.0 \
  --port 8080 \
  --n-gpu-layers "$NGL" \
  --n-cpu-moe "$N_CPU_MOE" \
  --no-mmap \
  --mlock \
  --ctx-size "$CTX" \
  --cache-type-k "$CTK" \
  --cache-type-v "$CTV"
