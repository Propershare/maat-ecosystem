#!/usr/bin/env python3
"""
Query gitMaat for Clawdbot integration
Usage: python3 query-gitmaat-clawdbot.py "command text"
"""

import sys
import json
from pathlib import Path

# Find workspace root
workspace_root = None
current = Path.cwd()
for path in [current] + list(current.parents):
    if (path / "maatlangchain").exists():
        workspace_root = path
        break

if not workspace_root:
    print(json.dumps({"error": "Workspace root not found"}))
    sys.exit(1)

# Import Maat Memory
sys.path.insert(0, str(workspace_root / "maatlangchain"))
try:
    from maat_memory import MaatMemory
except ImportError as e:
    print(json.dumps({"error": f"Failed to import MaatMemory: {e}"}))
    sys.exit(1)

def query_gitmaat(command):
    """Query gitMaat based on command text"""
    memory = MaatMemory()
    result = {}
    
    command_lower = command.lower()
    
    # Query tasks
    if 'task' in command_lower or 'pending' in command_lower:
        tasks = memory.get_tasks(status="pending", limit=10)
        result['tasks'] = [
            {
                'title': task.get('title', 'Untitled'),
                'description': task.get('description', ''),
                'status': task.get('status', 'unknown'),
                'created_at': str(task.get('created_at', ''))
            }
            for task in tasks
        ]
    
    # Query changes
    if 'change' in command_lower or 'recent' in command_lower:
        changes = memory.get_recent_changes(limit=10)
        result['changes'] = [
            {
                'file': change.get('file', 'unknown'),
                'description': change.get('description', ''),
                'action': change.get('action', 'unknown'),
                'timestamp': str(change.get('timestamp', ''))
            }
            for change in changes
        ]
    
    # Query learnings
    if 'learning' in command_lower or 'learn' in command_lower:
        learnings = memory.get_learnings(limit=10)
        result['learnings'] = [
            {
                'content': learning.get('content', ''),
                'context': learning.get('context', ''),
                'timestamp': str(learning.get('timestamp', ''))
            }
            for learning in learnings
        ]
    
    # Query decisions
    if 'decision' in command_lower:
        decisions = memory.get_decisions(limit=10)
        result['decisions'] = [
            {
                'context': decision.get('context', ''),
                'decision': decision.get('decision', ''),
                'rationale': decision.get('rationale', ''),
                'timestamp': str(decision.get('timestamp', ''))
            }
            for decision in decisions
        ]
    
    # If no specific query, return general info
    if not result:
        tasks = memory.get_tasks(status="pending", limit=5)
        result['tasks'] = [
            {
                'title': task.get('title', 'Untitled'),
                'description': task.get('description', ''),
                'status': task.get('status', 'unknown')
            }
            for task in tasks
        ]
        result['message'] = 'Showing pending tasks. Use "tasks", "changes", "learnings", or "decisions" for specific queries.'
    
    return result

if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else ""
    result = query_gitmaat(command)
    print(json.dumps(result, indent=2))
