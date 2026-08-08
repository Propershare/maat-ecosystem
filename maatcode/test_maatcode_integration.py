#!/usr/bin/env python3
"""
Test MaatCode Integration
Verifies that MaatCode can access gitMaat and all tools work
"""

import sys
import os
from pathlib import Path

# CRITICAL: Load PGVECTOR_DB_URL BEFORE importing maat_memory
# Add maatlangchain to path
workspace_root = Path(__file__).parent.parent
maatlangchain_path = workspace_root / "maatlangchain"
if str(maatlangchain_path) not in sys.path:
    sys.path.insert(0, str(maatlangchain_path))

# Load PGVECTOR_DB_URL from .env file if not set
print("=" * 60)
print("Loading Database Configuration")
print("=" * 60)

# Check current environment variable (but always reload from .env to ensure correct format)
current_env = os.environ.get("PGVECTOR_DB_URL")
if current_env:
    print(f"⚠️  PGVECTOR_DB_URL already set in environment")
    if "@" in current_env:
        parts = current_env.split("@")
        if len(parts) == 2:
            masked = parts[0].split(":")[0] + ":****@" + parts[1]
            print(f"   Current value: {masked}")
        else:
            print(f"   Current value: {current_env[:50]}...")
    else:
        print(f"   Current value: {current_env[:50]}...")
    print("   (Will reload from .env file to ensure correct format)")

print("🔍 Loading PGVECTOR_DB_URL from .env files...")
# Try multiple possible .env file locations (in priority order)
env_files = [
    workspace_root / "tehuti-lab-webui" / ".env",  # Correct path
    workspace_root / "open-webui" / ".env",  # Old path (for compatibility)
    workspace_root / ".env",  # Root .env
]

found = False
for env_file in env_files:
    if env_file.exists():
        print(f"📁 Checking .env file: {env_file}")
        with open(env_file, "r") as f:
            for line in f:
                if line.startswith("PGVECTOR_DB_URL="):
                    db_url = line.split("=", 1)[1].strip().strip('"').strip("'")
                    # Override environment variable with .env file value
                    os.environ["PGVECTOR_DB_URL"] = db_url
                    # Mask password for display
                    if "@" in db_url:
                        parts = db_url.split("@")
                        if len(parts) == 2:
                            masked = parts[0].split(":")[0] + ":****@" + parts[1]
                            print(f"✅ Loaded PGVECTOR_DB_URL from .env: {masked}")
                        else:
                            print(f"✅ Loaded PGVECTOR_DB_URL from .env: {db_url[:50]}...")
                    else:
                        print(f"✅ Loaded PGVECTOR_DB_URL from .env: {db_url[:50]}...")
                    found = True
                    break
        if found:
            break

if not found:
    print("⚠️  No .env file found with PGVECTOR_DB_URL")
    print(f"   Checked: {[str(f) for f in env_files]}")
    if not os.environ.get("PGVECTOR_DB_URL"):
        print("\n❌ Cannot proceed without database connection string")
        print("   Please set PGVECTOR_DB_URL environment variable or add it to .env file")
        sys.exit(1)
    else:
        print("   Using existing environment variable (may be incomplete)")

print("=" * 60)
print()

# NOW import maat_memory (after setting environment variable)
from maat_memory import MaatMemory, get_unique_agent_id

def test_gitmaat_connection():
    """Test gitMaat connection"""
    print("🔍 Testing gitMaat connection...")
    try:
        memory = MaatMemory()
        agent_id = get_unique_agent_id("test_maatcode")
        print(f"✅ gitMaat connected! Agent ID: {agent_id}")
        return True, memory, agent_id
    except Exception as e:
        print(f"❌ gitMaat connection failed: {e}")
        return False, None, None

def test_get_tasks(memory, agent_id):
    """Test getting tasks"""
    print("\n📋 Testing get_tasks...")
    try:
        tasks = memory.get_tasks(status="pending", limit=5)
        print(f"✅ Found {len(tasks)} pending tasks")
        if tasks:
            print(f"   Example: {tasks[0].get('title', 'N/A')[:50]}")
        return True
    except Exception as e:
        print(f"❌ get_tasks failed: {e}")
        return False

def test_log_change(memory, agent_id):
    """Test logging a change"""
    print("\n📝 Testing log_change...")
    try:
        memory.log_change(
            agent=agent_id,
            file_path="test_file.py",
            change_type="create",
            summary="Test change for MaatCode integration",
            reason="Testing MaatCode tools"
        )
        print("✅ log_change successful")
        return True
    except Exception as e:
        print(f"❌ log_change failed: {e}")
        return False

def test_search_conversations(memory, agent_id):
    """Test searching conversations"""
    print("\n🔎 Testing search_conversations...")
    try:
        results = memory.search_conversations(query="test", limit=5)
        print(f"✅ Found {len(results)} conversations")
        return True
    except Exception as e:
        print(f"❌ search_conversations failed: {e}")
        return False

def test_project_discovery():
    """Test project discovery"""
    print("\n🗂️  Testing project_discovery...")
    try:
        from maat_memory.project_discovery import discover_project
        discovery = discover_project(workspace_root / "maatlangchain")
        print(f"✅ Project discovery successful")
        print(f"   Missing: {len(discovery.get('missing', []))} components")
        print(f"   Suggestions: {len(discovery.get('suggestions', []))} builds")
        return True
    except Exception as e:
        print(f"❌ project_discovery failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("MaatCode Integration Test")
    print("=" * 60)
    
    # Test gitMaat connection
    success, memory, agent_id = test_gitmaat_connection()
    if not success:
        print("\n❌ Cannot proceed without gitMaat connection")
        return 1
    
    # Run all tests
    tests = [
        ("Get Tasks", lambda: test_get_tasks(memory, agent_id)),
        ("Log Change", lambda: test_log_change(memory, agent_id)),
        ("Search Conversations", lambda: test_search_conversations(memory, agent_id)),
        ("Project Discovery", test_project_discovery),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! MaatCode is ready to use.")
        print("\nNext steps:")
        print("1. Start MaatCode MCP server: python3 mcp_server.py")
        print("2. Start MaatCode API server: python3 api_server.py")
        print("3. Configure OpenCode to use MaatCode tools")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

