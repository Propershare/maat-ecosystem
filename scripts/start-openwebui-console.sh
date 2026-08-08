#!/bin/bash
# Start Open WebUI backend in console mode with proper environment variables

cd /home/suspect/.n8n/open-webui

# Load environment variables from .env file
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

# Activate virtual environment (venv is at workspace root, not inside open-webui)
source /home/suspect/.n8n/open-webui-venv/bin/activate

# Set PYTHONPATH to use fork's backend (MUST be first in path)
export PYTHONPATH=/home/suspect/.n8n/open-webui/backend:$PYTHONPATH

# Set frontend build directory (same as systemd service)
export FRONTEND_BUILD_DIR=/home/suspect/.n8n/open-webui-venv/lib/python3.11/site-packages/open_webui/frontend

# Start the backend server
echo "Starting Open WebUI backend..."
echo "PGVECTOR_DB_URL: ${PGVECTOR_DB_URL:0:50}..."
echo "PYTHONPATH: $PYTHONPATH"
echo "FRONTEND_BUILD_DIR: $FRONTEND_BUILD_DIR"
echo ""
# Use the open-webui CLI which will import from PYTHONPATH first
/home/suspect/.n8n/open-webui-venv/bin/open-webui serve --host 0.0.0.0 --port 3000

