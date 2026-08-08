#!/bin/bash
# Start MaatLangChain API server

cd "$(dirname "$0")/.."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Start FastAPI server
python3 -m uvicorn api.main:app \
    --host 0.0.0.0 \
    --port 8019 \
    --reload \
    --log-level info

