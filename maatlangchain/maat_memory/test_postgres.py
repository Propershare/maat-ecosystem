#!/usr/bin/env python3
"""
Test script for PostgreSQL-backed Maat Memory.

Tests:
1. Schema creation
2. Session management
3. Conversation logging with embeddings
4. Vector search
5. Audit trail
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from maat_memory.memory_postgres import MaatMemoryPostgres

# Try to get embeddings model
try:
    from langchain_huggingface import HuggingFaceEmbeddings
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    print("✅ Embeddings model loaded")
except ImportError:
    try:
        from langchain_community.embeddings import HuggingFaceEmbeddings
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        print("✅ Embeddings model loaded (langchain_community)")
    except ImportError:
        embeddings = None
        print("⚠️  Embeddings model not available - vector search disabled")

def test_sessions(memory):
    """Test session management."""
    print("\n=== Testing Sessions ===")
    
    session_id = memory.start_session("test_agent", "Test session")
    print(f"✅ Started session: {session_id}")
    
    memory.end_session("test_agent", "Test session complete", ["Test point 1", "Test point 2"])
    print("✅ Ended session")

def test_conversations(memory):
    """Test conversation logging."""
    print("\n=== Testing Conversations ===")
    
    memory.start_session("test_agent", "Conversation test")
    
    conv_id = memory.log_conversation(
        agent="test_agent",
        user_query="What is Maat?",
        agent_response="Maat is the ancient Egyptian concept of truth, balance, order, and justice.",
        tools_used=["search", "rag"],
        files_accessed=["/path/to/file.md"],
        decisions_made=["Use RAG for answer"]
    )
    print(f"✅ Logged conversation: {conv_id}")
    
    # Test search
    results = memory.search_conversations("Maat principles", agent="test_agent", limit=5)
    print(f"✅ Found {len(results)} conversations")
    if results:
        print(f"   First result similarity: {results[0].get('similarity', 'N/A')}")
    
    memory.end_session("test_agent", "Conversation test complete")

def test_audit(memory):
    """Test audit trail."""
    print("\n=== Testing Audit Trail ===")
    
    audit_id = memory.log_audit(
        agent="test_agent",
        action="test_action",
        resource="test_resource",
        before={"old": "value"},
        after={"new": "value"},
        reason="Testing audit trail",
        maat_compliance={"truth": True, "balance": True, "order": True, "self_reflection": True}
    )
    print(f"✅ Logged audit entry: {audit_id}")

def test_tasks(memory):
    """Test task management."""
    print("\n=== Testing Tasks ===")
    
    task_id = memory.log_task(
        agent="test_agent",
        title="Test Task",
        description="This is a test task",
        status="in_progress",
        priority="high",
        related_files=["/path/to/file.py"],
        dependencies=[]
    )
    print(f"✅ Logged task: {task_id}")

def main():
    """Run all tests."""
    print("Starting Maat Memory PostgreSQL tests...")
    
    try:
        memory = MaatMemoryPostgres(embeddings_model=embeddings)
        print("✅ Maat Memory initialized with PostgreSQL")
        
        test_sessions(memory)
        test_conversations(memory)
        test_audit(memory)
        test_tasks(memory)
        
        memory.close()
        print("\n✅ All tests passed!")
        return 0
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

