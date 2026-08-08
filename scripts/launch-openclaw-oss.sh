#!/usr/bin/env bash
# Launch OpenClaw with the OSS model (gpt-oss:20b). Use this instead of
# plain "ollama launch openclaw" so Ollama doesn't default to kimi.
set -e
OSS_MODEL="${OPENCLAW_OSS_MODEL:-gpt-oss:20b}"
exec ollama launch openclaw --model "$OSS_MODEL"
