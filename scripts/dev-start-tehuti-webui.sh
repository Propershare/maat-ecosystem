#!/bin/bash
# Development startup script for Tehuti Lab WebUI
# Starts Vite dev server (frontend) and backend API server

cd /home/suspect/.n8n/tehuti-lab-webui

echo "🚀 Starting Tehuti Lab WebUI Development Mode"
echo ""
echo "📋 This script will start:"
echo "   1. Frontend: Vite dev server (hot reload)"
echo "   2. Backend: FastAPI server (API only)"
echo ""
echo "⚠️  You'll need TWO terminals:"
echo "   Terminal 1: Frontend (npm run dev)"
echo "   Terminal 2: Backend (this script)"
echo ""
read -p "Press Enter to start backend server, or Ctrl+C to cancel..."

# Activate virtual environment
source venv/bin/activate

# Set environment variables
export PGVECTOR_DB_URL="${PGVECTOR_DB_URL:-postgresql://suspect:disdick@localhost:5432/maat_memory}"
export OLLAMA_BASE_URL="${OLLAMA_BASE_URL:-http://127.0.0.1:11434}"
export WEBUI_URL="${WEBUI_URL:-https://ai.suspecttv.com}"
export ENABLE_SIGNUP="${ENABLE_SIGNUP:-true}"
export DEFAULT_USER_ROLE="${DEFAULT_USER_ROLE:-user}"

# Don't set FRONTEND_BUILD_DIR - we're using Vite dev server
# Backend will serve API only

echo "🔧 Environment:"
echo "   PGVECTOR_DB_URL: ${PGVECTOR_DB_URL:0:50}..."
echo "   OLLAMA_BASE_URL: $OLLAMA_BASE_URL"
echo "   WEBUI_URL: $WEBUI_URL"
echo ""
echo "🌐 Starting backend API server on port 3000..."
echo "   Frontend should be running on Vite port (usually 5173)"
echo "   Frontend will proxy /api/* requests to this backend"
echo ""

open-webui serve --host 0.0.0.0 --port 3000

