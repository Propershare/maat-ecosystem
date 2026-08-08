#!/usr/bin/env python3
"""
Verify Cross-Machine Sync - Test that all laptops share the same memory.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from maat_memory import MaatMemory

def main():
    """Verify cross-machine sync."""
    print("=" * 60)
    print("Maat Memory Cross-Machine Sync Verification")
    print("=" * 60)
    print()
    
    # Check backend
    memory = MaatMemory()
    backend = memory.__class__.__name__
    
    print(f"Backend: {backend}")
    
    if "Postgres" not in backend:
        print("⚠️  WARNING: Not using PostgreSQL backend!")
        print("   Cross-machine sync requires PostgreSQL.")
        print("   Set PGVECTOR_DB_URL environment variable.")
        return False
    
    print("✅ Using PostgreSQL backend - cross-machine sync enabled!")
    print()
    
    # Get machine identifier
    import socket
    machine_name = socket.gethostname()
    print(f"Machine: {machine_name}")
    print()
    
    # Create test session
    print("Creating test session...")
    session_id = memory.start_session(
        agent="cursor",
        summary=f"Sync test from {machine_name} at {datetime.now().isoformat()}"
    )
    print(f"✅ Session created: {session_id}")
    print()
    
    # List all sessions
    print("Retrieving all sessions...")
    all_sessions = memory.get_sessions(agent="cursor", limit=10)
    print(f"✅ Found {len(all_sessions)} session(s)")
    print()
    
    if all_sessions:
        print("Recent sessions:")
        for i, session in enumerate(all_sessions[:5], 1):
            summary = session.get("summary", "No summary")
            created = session.get("started_at", "Unknown")
            print(f"  {i}. {summary[:50]}...")
            print(f"     Created: {created}")
        print()
    
    # Test conversation
    print("Creating test conversation...")
    memory.log_conversation(
        agent="cursor",
        user_query=f"Test query from {machine_name}",
        agent_response="This is a test response to verify cross-machine sync",
        tools_used=["verify_sync"],
        files_accessed=[],
        decisions_made=["Testing cross-machine memory sync"]
    )
    print("✅ Conversation logged")
    print()
    
    # Search conversations
    print("Searching conversations...")
    results = memory.search_conversations(
        query="test query",
        agent="cursor",
        limit=5
    )
    print(f"✅ Found {len(results)} conversation(s)")
    print()
    
    print("=" * 60)
    print("✅ Verification Complete!")
    print("=" * 60)
    print()
    print("To verify cross-machine sync:")
    print("1. Run this script on another laptop")
    print("2. You should see sessions/conversations from this machine")
    print("3. Create a session on the other laptop")
    print("4. Run this script again - you should see it here!")
    
    return True

if __name__ == "__main__":
    main()

