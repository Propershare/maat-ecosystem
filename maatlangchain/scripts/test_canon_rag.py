#!/usr/bin/env python3
"""
Test Canon RAG Queries
Verifies that canon_kmt collection is accessible and queries work
"""

import sys
from pathlib import Path

# Setup paths
maatlangchain_root = Path(__file__).parent.parent
sys.path.insert(0, str(maatlangchain_root))

from core.utils.rag_query_helper import query_canon_rag, search_canon_similar, get_canon_context

def test_canon_queries():
    """Test various canon RAG queries."""
    print("=" * 80)
    print("Testing Canon RAG Queries")
    print("=" * 80)
    print()
    
    # Test 1: Simple search
    print("Test 1: Search for similar documents")
    print("-" * 80)
    try:
        results = search_canon_similar("KMT chronology", top_k=3)
        if results:
            print(f"✓ Found {len(results)} documents")
            for i, result in enumerate(results[:2], 1):
                print(f"  {i}. {result['file_name']}")
                print(f"     Title: {result.get('title', 'N/A')}")
                print(f"     Preview: {result['content'][:100]}...")
        else:
            print("✗ No documents found - collection may be empty")
    except Exception as e:
        print(f"✗ Error: {e}")
    print()
    
    # Test 2: Full RAG query
    print("Test 2: Full RAG query with LLM")
    print("-" * 80)
    try:
        result = query_canon_rag("What is the K2 methodology?", top_k=3)
        if result["confidence"] != "error":
            print(f"✓ Query successful (confidence: {result['confidence']})")
            print(f"  Answer preview: {result['answer'][:200]}...")
            print(f"  Sources: {len(result['sources'])}")
            for source in result['sources'][:2]:
                print(f"    - {source.get('file_name', 'unknown')}")
        else:
            print(f"✗ Query failed: {result.get('metadata', {}).get('error', 'Unknown error')}")
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
    print()
    
    # Test 3: Get context
    print("Test 3: Get formatted context")
    print("-" * 80)
    try:
        context = get_canon_context("KMT state formation", max_chars=500)
        if context and "Error" not in context:
            print(f"✓ Context retrieved ({len(context)} chars)")
            print(f"  Preview: {context[:200]}...")
        else:
            print(f"✗ Failed to get context: {context}")
    except Exception as e:
        print(f"✗ Error: {e}")
    print()
    
    print("=" * 80)
    print("Test Complete")
    print("=" * 80)
    print()
    print("Note: If tests fail, ensure:")
    print("  1. Canon files have been ingested (run ingest_canon_to_rag.py)")
    print("  2. Database connection is working")
    print("  3. Collection 'canon_kmt' exists in vector store")

if __name__ == "__main__":
    test_canon_queries()

