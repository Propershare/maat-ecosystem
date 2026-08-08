#!/usr/bin/env python3
"""
Test the retriever against existing corpus connectivity.
Tests the retriever integration with your existing RAG infrastructure.
"""

import os
import sys

# Add project root to path
sys.path.insert(0, '/home/suspect/.n8n')

from maat_legal_runtime_phase3 import (
    GraphState,
    retrieve_authorities,
    LegalAdvisorySynthesis,
    AuthorityType,
    AuthorityWeight
)

def test_retriever_connectivity():
    """Test retriever connectivity and corpus access."""
    print("=" * 70)
    print("Maat Legal Runtime - Retriever Connectivity Test")
    print("=" * 70)
    
    # Create a test state
    state = GraphState()
    
    print("\n1. Testing corpus configuration...")
    print(f"   Domain Pack: fl-trust-law")
    print(f"   Corpus Status: STUBBED (NOT_CONNECTED)")
    print(f"   Corpus Path: (not configured)")
    
    # Run the stub retriever
    print("\n2. Running stub retriever...")
    state = retrieve_authorities(state)
    
    print(f"   Authorities Retrieved: {len(state.sources_consulted)}")
    for authority in state.sources_consulted:
        print(f"   - {authority.title}: {authority.authority_weight.value}")
    
    print("\n3. Corpus Connectivity Status:")
    if state.sources_consulted:
        print(f"   ✅ CONNECTED - Retrieved {len(state.sources_consulted)} authorities")
        print(f"   Available Authorities:")
        for auth in state.sources_consulted:
            print(f"      • {auth.title} ({auth.authority_type.value})")
    else:
        print(f"   ❌ NOT_CONNECTED - No corpus configured")
    
    return state

def test_corpus_integration():
    """Test with a real corpus if available."""
    print("\n" + "=" * 70)
    print("Maat Legal Runtime - Corpus Integration Test")
    print("=" * 70)
    
    # Check for corpus in workspace
    corpus_paths = [
        "/home/suspect/.n8n/data/fl-trust-law",
        "/home/suspect/.n8n/maatlabs/trust-lifecycle",
        "/home/suspect/.n8n/Legal_AI_FL"
    ]
    
    for corpus_path in corpus_paths:
        if os.path.exists(corpus_path):
            print(f"\n✅ Found corpus at: {corpus_path}")
            print(f"   Contents:")
            for root, dirs, files in os.walk(corpus_path):
                for file in files:
                    print(f"      - {os.path.join(root, file)}")
            print(f"   Corpus Status: CONFIGURED")
            return True
    
    print(f"\n⚠️ No corpus found at configured paths:")
    for path in corpus_paths:
        print(f"   - {path}")
    print(f"   \n   Configure corpus path or use stub retriever.")
    return False

def main():
    """Run all tests."""
    # Test 1: Retriever connectivity
    state = test_retriever_connectivity()
    
    # Test 2: Corpus integration
    test_corpus_integration()
    
    # Print final status
    print("\n" + "=" * 70)
    print("Final Status Summary")
    print("=" * 70)
    print(f"Corpus Status: {'CONFIGURED' if state.sources_consulted else 'NOT_CONNECTED'}")
    print(f"Authorities Available: {len(state.sources_consulted) if state.sources_consulted else 0}")
    print(f"Retriever Type: {'STUBBED' if not state.sources_consulted else 'FUNCTIONAL'}")
    print("=" * 70)
    
    return state

if __name__ == "__main__":
    main()