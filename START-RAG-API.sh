#!/bin/bash
# Start MaatLangChain RAG API Server for n8n workflow

cd /home/suspect/.n8n/maatlangchain/api

# Activate virtual environment if it exists
if [ -d "/home/suspect/.n8n/maatlangchain/venv" ]; then
    source /home/suspect/.n8n/maatlangchain/venv/bin/activate
fi

# Start FastAPI server
echo "Starting MaatLangChain RAG API on port 8019..."
python3 -m uvicorn main:app --host 127.0.0.1 --port 8019 --reload

