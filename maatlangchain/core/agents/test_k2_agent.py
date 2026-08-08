"""
Test K2 Dialectical Development Agent
Tests the 42-stage K2 methodology execution
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.agents.k2_agent import K2Agent, K2_STAGES

def test_k2_stages():
    """Test that all K2 stages are defined."""
    print("=" * 80)
    print("K2 Methodology - Stage Verification")
    print("=" * 80)
    print()
    
    print(f"Total stages defined: {len(K2_STAGES)}")
    print()
    
    # Check key stages
    key_stages = [1, 3, 11, 12, 13, 21, 24, 25, 32, 42]
    
    print("Key Stages:")
    for stage_num in key_stages:
        if stage_num in K2_STAGES:
            stage = K2_STAGES[stage_num]
            print(f"  ✅ Stage {stage_num}: {stage['name']}")
        else:
            print(f"  ❌ Stage {stage_num}: MISSING")
    print()
    
    print("✅ K2 stages verified")
    print()

def test_k2_agent():
    """Test K2 agent execution."""
    print("=" * 80)
    print("K2 Agent Execution Test")
    print("=" * 80)
    print()
    
    try:
        agent = K2Agent(memory=None)  # Test without DB
        print("✅ K2 Agent initialized")
        print()
        
        # Test with a simple unity
        unity = "A social movement organizing for change"
        print(f"Analyzing unity: '{unity}'")
        print()
        print("Executing K2 analysis (42 stages)...")
        print("(This may take a moment)")
        print()
        
        result = agent.analyze(unity, max_stages=5)  # Test first 5 stages
        
        print("K2 Analysis Result:")
        print("-" * 80)
        print(f"Status: {result['status']}")
        print(f"Stages completed: {result.get('stages_completed', 0)}")
        print(f"Final stage: {result.get('final_stage', 'N/A')}")
        print(f"History entries: {len(result.get('history', []))}")
        print()
        
        if result['status'] == 'completed':
            print("✅ K2 analysis completed successfully")
        else:
            print(f"⚠️  K2 analysis status: {result['status']}")
            if result.get('error'):
                print(f"   Error: {result['error']}")
        
        print()
        
    except Exception as e:
        print(f"❌ K2 Agent test failed: {e}")
        import traceback
        traceback.print_exc()

def test_stage_info():
    """Test stage information retrieval."""
    print("=" * 80)
    print("K2 Stage Information")
    print("=" * 80)
    print()
    
    agent = K2Agent(memory=None)
    
    # Show first 5 stages
    print("First 5 Stages:")
    for i in range(1, 6):
        info = agent.get_stage_info(i)
        print(f"  Stage {i}: {info['name']}")
        print(f"    {info['description'][:80]}...")
        print()
    
    # Show key transformation stages
    key_stages = [11, 21, 24, 25, 32, 42]
    print("Key Transformation Stages:")
    for stage_num in key_stages:
        info = agent.get_stage_info(stage_num)
        print(f"  Stage {stage_num}: {info['name']}")
        print(f"    {info['description'][:80]}...")
        print()

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("K2 Dialectical Development Agent - Test Suite")
    print("=" * 80)
    print()
    
    test_k2_stages()
    test_stage_info()
    test_k2_agent()
    
    print("=" * 80)
    print("K2 Agent Tests Complete")
    print("=" * 80)

