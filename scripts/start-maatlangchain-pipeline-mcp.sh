#!/bin/bash
# Start MaatLangChain Pipeline MCP Server via mcpo wrapper (HTTP on port 8026)

cd /home/suspect/.n8n/mcp-servers/maatlangchain-pipeline

# Load environment variables
if [ -f /home/suspect/.n8n/tehuti-lab-webui/.env ]; then
    export $(cat /home/suspect/.n8n/tehuti-lab-webui/.env | grep -v '^#' | xargs)
fi

# Set defaults
export PGVECTOR_DB_URL="${PGVECTOR_DB_URL:-postgresql://suspect:disdick@localhost:5432/maat_memory}"
export TEHUTI_CORE_URL="${TEHUTI_CORE_URL:-http://127.0.0.1:8014}"
export WORKSPACE_ROOT="${WORKSPACE_ROOT:-/home/suspect/.n8n}"

echo "🚀 Starting MaatLangChain Pipeline MCP Server"
echo "   Port: 8026"
echo "   Tehuti Core: $TEHUTI_CORE_URL"
echo "   Database: ${PGVECTOR_DB_URL:0:50}..."
echo ""

# Start via mcpo wrapper (exposes stdio MCP server via HTTP)
uv tool uvx mcpo --host 127.0.0.1 --port 8026 -- python3 /home/suspect/.n8n/mcp-servers/maatlangchain-pipeline/maatlangchain_pipeline_server.py
