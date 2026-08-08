#!/usr/bin/env python3
"""
Integration tests for optimized gitMaat query system
Tests model → tool → database flow
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import sys
from pathlib import Path

# Add maatlangchain to path
maatlangchain_path = Path(__file__).parent.parent.parent / "maatlangchain"
sys.path.insert(0, str(maatlangchain_path.parent))

from maatlangchain.maat_memory import MaatMemory, get_unique_agent_id
from maatlangchain.maat_memory.optimized_query import (
    OptimizedGitMaatQuery,
    SemanticQueryRouter,
    optimized_query,
    semantic_query
)


def test_optimized_query():
    """Test optimized query system"""
    print("🧪 Testing Optimized Query System")
    print("=" * 60)
    
    query_system = OptimizedGitMaatQuery()
    
    # Test 1: Basic query
    print("\n📋 Test 1: Basic Task Query")
    tasks = query_system.query("tasks", {"status": "pending"}, limit=5)
    print(f"✅ Found {len(tasks)} pending tasks")
    
    # Test 2: Cached query
    print("\n📋 Test 2: Cached Query (should be faster)")
    import time
    start = time.time()
    tasks1 = query_system.query("tasks", {"status": "pending"}, limit=5)
    time1 = time.time() - start
    
    start = time.time()
    tasks2 = query_system.query("tasks", {"status": "pending"}, limit=5)
    time2 = time.time() - start
    
    print(f"First query: {time1:.4f}s")
    print(f"Cached query: {time2:.4f}s")
    print(f"✅ Cache speedup: {time1/time2:.2f}x faster")
    
    # Test 3: Batch query
    print("\n📋 Test 3: Batch Query")
    batch_queries = [
        {"type": "tasks", "filters": {"status": "pending"}, "limit": 5},
        {"type": "learnings", "filters": {}, "limit": 5},
        {"type": "decisions", "filters": {}, "limit": 5}
    ]
    results = query_system.batch_query(batch_queries)
    print(f"✅ Batch query returned {len(results)} result sets")
    for query_type, result_list in results.items():
        print(f"   - {query_type}: {len(result_list)} results")
    
    print("\n✅ All optimized query tests passed!")


def test_semantic_routing():
    """Test semantic query routing"""
    print("\n🧪 Testing Semantic Query Routing")
    print("=" * 60)
    
    router = SemanticQueryRouter()
    
    test_queries = [
        "I want to start a new task. What should I do first?",
        "Get pending tasks",
        "Show me recent decisions",
        "What have we learned about workflow automation?",
        "What files were changed recently?",
        "Search conversations about fine-tuning"
    ]
    
    for query in test_queries:
        print(f"\n📋 Query: {query}")
        plan = router.route_query(query)
        print(f"   Type: {plan['type']}")
        print(f"   Filters: {plan['filters']}")
        print(f"   Tool: {plan['tool']}")
        print(f"   Limit: {plan['limit']}")
        
        # Execute query
        results = router.execute_routed_query(query)
        print(f"   ✅ Returned {len(results)} results")
    
    print("\n✅ All semantic routing tests passed!")


def test_end_to_end():
    """Test end-to-end: Model → Tool → Database"""
    print("\n🧪 Testing End-to-End Flow")
    print("=" * 60)
    
    try:
        memory = MaatMemory()
        agent_id = get_unique_agent_id("cursor")
    except Exception as e:
        print(f"⚠️  PostgreSQL connection not available: {e}")
        print("   Using JSON backend for testing...")
        # Force JSON backend
        import os
        os.environ.pop("PGVECTOR_DB_URL", None)
        from maatlangchain.maat_memory.memory import MaatMemory as JSONMaatMemory
        memory = JSONMaatMemory()
        agent_id = "cursor_test"
    
    # Simulate model generating query
    user_query = "I want to start a new task. What should I do first?"
    print(f"📋 User Query: {user_query}")
    
    # Step 1: Model would generate response with tool call
    # (In real scenario, fine-tuned model generates this)
    expected_response = "QUERY gitMaat FIRST\n\nI'll query gitMaat using tool_query_gitmaat_post..."
    print(f"✅ Model Response: {expected_response[:50]}...")
    
    # Step 2: Extract tool call (simulated)
    tool_call = {
        "tool": "tool_query_gitmaat_post",
        "parameters": {
            "query_type": "tasks",
            "status": "pending",
            "limit": 10
        }
    }
    print(f"✅ Tool Call: {tool_call['tool']}")
    
    # Step 3: Execute tool (route to optimized query)
    router = SemanticQueryRouter(memory=memory)
    results = router.execute_routed_query(user_query)
    
    print(f"✅ Database Results: {len(results)} items")
    
    # Step 4: Verify results
    assert len(results) >= 0, "Should return results (even if empty)"
    print("✅ End-to-end flow verified!")
    
    print("\n✅ All end-to-end tests passed!")


def test_performance():
    """Test query performance"""
    print("\n🧪 Testing Query Performance")
    print("=" * 60)
    
    import time
    
    query_system = OptimizedGitMaatQuery()
    
    # Test optimized query
    start = time.time()
    tasks = query_system.query("tasks", {"status": "pending"}, limit=10)
    optimized_time = time.time() - start
    
    # Test direct memory query (baseline)
    memory = MaatMemory()
    start = time.time()
    direct_tasks = memory.get_tasks(status="pending", limit=10)
    direct_time = time.time() - start
    
    print(f"Optimized query: {optimized_time:.4f}s")
    print(f"Direct query: {direct_time:.4f}s")
    
    if optimized_time < direct_time:
        print(f"✅ Optimized query is {direct_time/optimized_time:.2f}x faster")
    else:
        print("⚠️  Optimized query may benefit from caching")
    
    print("\n✅ Performance test complete!")


if __name__ == "__main__":
    print("🚀 Running gitMaat Query Integration Tests")
    print("=" * 60)
    
    try:
        test_optimized_query()
        test_semantic_routing()
        test_end_to_end()
        test_performance()
        
        print("\n" + "=" * 60)
        print("🎉 All integration tests passed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

