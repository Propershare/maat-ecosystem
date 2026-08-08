#!/bin/bash
# MaatLangChain Pipeline Startup Script
# Ensures correct environment variables are set

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Load environment from .env if it exists
if [ -f "/home/suspect/.n8n/tehuti-lab-webui/.env" ]; then
    export PGVECTOR_DB_URL=$(grep "^PGVECTOR_DB_URL=" "/home/suspect/.n8n/tehuti-lab-webui/.env" | cut -d'=' -f2 | tr -d '"' | tr -d "'")
fi

# Set defaults if not set
export PGVECTOR_DB_URL="${PGVECTOR_DB_URL:-postgresql://suspect:disdick@localhost:5432/maat_memory}"
export TEHUTI_CORE_URL="${TEHUTI_CORE_URL:-http://127.0.0.1:8014}"

# Kill any existing process on port 8020
lsof -ti:8020 | xargs kill -9 2>/dev/null || true
sleep 1

# Start the pipeline API
echo "Starting MaatLangChain Pipeline API..."
echo "  Database: $PGVECTOR_DB_URL"
echo "  Core URL: $TEHUTI_CORE_URL"

nohup python3 maatlangchain_pipeline_api.py > /tmp/maatlangchain-pipeline-api.log 2>&1 &
PID=$!

sleep 3

# Check if it started successfully
if ps -p $PID > /dev/null 2>&1; then
    echo "✅ Pipeline started (PID: $PID)"
    echo "📋 Logs: /tmp/maatlangchain-pipeline-api.log"
    echo "🔍 Health: curl http://127.0.0.1:8020/health"
else
    echo "❌ Failed to start Pipeline"
    tail -20 /tmp/maatlangchain-pipeline-api.log
    exit 1
fi

