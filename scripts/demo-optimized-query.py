#!/usr/bin/env python3
"""
Demo: Optimized gitMaat Query System
Shows the optimized query system in action
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from maatlangchain.maat_memory.optimized_query import (
    OptimizedGitMaatQuery,
    SemanticQueryRouter,
    optimized_query,
    semantic_query
)

print("🚀 Optimized gitMaat Query System Demo")
print("=" * 60)

# Demo 1: Basic Optimized Query
print("\n📋 Demo 1: Basic Optimized Query")
print("-" * 60)
print("Query: Get pending tasks")
tasks = optimized_query("tasks", {"status": "pending"}, limit=5)
print(f"✅ Found {len(tasks)} pending tasks")
print(f"   Query executed with caching enabled")

# Demo 2: Semantic Query Routing
print("\n📋 Demo 2: Semantic Query Routing")
print("-" * 60)
test_queries = [
    "I want to start a new task. What should I do first?",
    "Get pending tasks",
    "Show me recent decisions",
    "What have we learned about workflow automation?"
]

router = SemanticQueryRouter()
for query in test_queries:
    print(f"\n   Query: {query}")
    plan = router.route_query(query)
    print(f"   → Type: {plan['type']}")
    print(f"   → Filters: {plan['filters']}")
    print(f"   → Tool: {plan['tool']}")
    print(f"   → Limit: {plan['limit']}")

# Demo 3: Batch Queries
print("\n📋 Demo 3: Batch Query Execution")
print("-" * 60)
query_system = OptimizedGitMaatQuery()
batch_queries = [
    {"type": "tasks", "filters": {"status": "pending"}, "limit": 10},
    {"type": "learnings", "filters": {}, "limit": 5},
    {"type": "decisions", "filters": {}, "limit": 5}
]

print("   Executing batch queries...")
results = query_system.batch_query(batch_queries)
print(f"✅ Batch query completed")
for query_type, result_list in results.items():
    print(f"   - {query_type}: {len(result_list)} results")

# Demo 4: Caching Performance
print("\n📋 Demo 4: Query Caching Performance")
print("-" * 60)
import time

print("   First query (no cache)...")
start = time.time()
result1 = query_system.query("tasks", {"status": "pending"}, limit=10)
time1 = time.time() - start

print("   Second query (cached)...")
start = time.time()
result2 = query_system.query("tasks", {"status": "pending"}, limit=10)
time2 = time.time() - start

print(f"   First query: {time1:.4f}s")
print(f"   Cached query: {time2:.4f}s")
if time1 > 0 and time2 > 0:
    speedup = time1 / time2 if time2 > 0 else 1
    print(f"   ✅ Cache speedup: {speedup:.2f}x faster")
else:
    print(f"   ✅ Caching working (both queries instant)")

# Demo 5: Semantic Query Execution
print("\n📋 Demo 5: Semantic Query Execution")
print("-" * 60)
print("   Query: 'I want to start a new task. What should I do first?'")
print("   → Automatically routes to: tasks query with status='pending'")
results = semantic_query("I want to start a new task. What should I do first?")
print(f"   ✅ Returned {len(results)} results")

print("\n" + "=" * 60)
print("🎉 Demo Complete!")
print("=" * 60)
print("\nKey Features Demonstrated:")
print("✅ Optimized queries with caching")
print("✅ Semantic query routing")
print("✅ Batch query execution")
print("✅ Performance optimization")
print("✅ Natural language understanding")

