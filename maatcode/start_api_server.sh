#!/bin/bash
# Start MaatCode API Server for WebUI Integration

cd "$(dirname "$0")/.."

# Activate virtual environment if exists
if [ -d "maatlangchain/venv" ]; then
    source maatlangchain/venv/bin/activate
fi

# Start API server
python3 maatcode/api_server.py

