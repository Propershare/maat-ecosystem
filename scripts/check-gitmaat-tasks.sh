#!/bin/bash
# Check gitMaat for pending tasks
# Can be run as cron job or manually

WORKSPACE_ROOT="/home/suspect/.n8n"
cd "$WORKSPACE_ROOT/maatlangchain" || exit 1

# Activate virtual environment if it exists
if [ -d "$WORKSPACE_ROOT/.venv" ]; then
    source "$WORKSPACE_ROOT/.venv/bin/activate"
fi

# Query gitMaat for pending tasks
python3 << 'EOF'
import sys
from pathlib import Path

workspace_root = Path("/home/suspect/.n8n")
sys.path.insert(0, str(workspace_root / "maatlangchain"))

try:
    from maat_memory import MaatMemory
    
    memory = MaatMemory()
    tasks = memory.get_tasks(status="pending", limit=10)
    
    if tasks:
        print(f"Found {len(tasks)} pending tasks:")
        for task in tasks:
            print(f"  - {task.get('title', 'Untitled')}: {task.get('description', 'No description')[:100]}")
    else:
        print("No pending tasks found.")
except Exception as e:
    print(f"Error querying gitMaat: {e}")
EOF
