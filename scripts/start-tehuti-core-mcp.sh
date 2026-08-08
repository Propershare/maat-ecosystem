#!/bin/bash
# Start Tehuti Core MCP server via mcpo wrapper (HTTP on port 8014)

cd /home/suspect/.n8n/mcp-servers/tehuti-core

# Load environment variables
export PGVECTOR_DB_URL="${PGVECTOR_DB_URL:-postgresql://suspect:disdick@localhost:5432/maat_memory}"
export WORKSPACE_ROOT="/home/suspect/.n8n"

# Start via mcpo wrapper (exposes stdio MCP server via HTTP)
uv tool uvx mcpo --host 127.0.0.1 --port 8014 -- python3 /home/suspect/.n8n/mcp-servers/tehuti-core/tehuti_core_server.py

