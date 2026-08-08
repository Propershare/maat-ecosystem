#!/usr/bin/env python3
"""Log task execution to gitMaat"""
import sys
import json
from pathlib import Path

workspace_root = Path("/home/suspect/.n8n")
sys.path.insert(0, str(workspace_root / "maatlangchain"))

# Set environment variable for database connection
import os
os.environ["PGVECTOR_DB_URL"] = "postgresql://suspect:disdick@localhost:5432/maat_memory"

try:
    from maat_memory import MaatMemory, get_unique_agent_id
    
    agent_id = get_unique_agent_id("clawdbot")
    memory = MaatMemory()
    
    task = sys.argv[1] if len(sys.argv) > 1 else "Unknown task"
    result = sys.argv[2] if len(sys.argv) > 2 else "No result"
    status = sys.argv[3] if len(sys.argv) > 3 else "unknown"
    
    # Log as change
    memory.log_change(
        agent_id,
        "clawdbot-task",
        "execute",
        f"Task: {task}\nResult: {result}\nStatus: {status}",
        "Clawdbot AI Employee execution"
    )
    
    # Log as learning if successful
    if status == "completed":
        memory.log_learning(
            agent_id,
            "Clawdbot Task Execution",
            f"Successfully executed: {task}",
            "Clawdbot AI Employee",
            confidence=0.8,
            applied=True,
            application_context=f"Task: {task}, Result: {result}"
        )
    
    print(json.dumps({"success": True, "logged": True}))
except Exception as e:
    print(json.dumps({"success": False, "error": str(e)}))
