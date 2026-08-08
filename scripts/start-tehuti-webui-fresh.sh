#!/bin/bash
# Start Tehuti Lab WebUI - ensures port is free first

echo "🛑 Stopping any existing processes on port 3000..."
lsof -ti:3000 | xargs -r kill -9 2>/dev/null
sleep 2

# Check if port is free
if lsof -ti:3000 >/dev/null 2>&1; then
    echo "❌ Port 3000 is still in use. Please check manually:"
    echo "   lsof -i:3000"
    exit 1
fi

echo "✅ Port 3000 is free"

cd /home/suspect/.n8n/tehuti-lab-webui

# Load environment variables from .env file
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

# Activate virtual environment
source /home/suspect/.n8n/tehuti-lab-webui-venv/bin/activate

# Set PYTHONPATH
export PYTHONPATH=/home/suspect/.n8n/tehuti-lab-webui/backend:$PYTHONPATH

# Set frontend build directory
export FRONTEND_BUILD_DIR=/home/suspect/.n8n/tehuti-lab-webui-venv/lib/python3.11/site-packages/open_webui/frontend

# Start the backend server
echo "🚀 Starting Tehuti Lab WebUI backend..."
echo "PGVECTOR_DB_URL: ${PGVECTOR_DB_URL:0:50}..."
echo "PYTHONPATH: $PYTHONPATH"
echo "FRONTEND_BUILD_DIR: $FRONTEND_BUILD_DIR"
echo ""
open-webui serve --host 0.0.0.0 --port 3000

