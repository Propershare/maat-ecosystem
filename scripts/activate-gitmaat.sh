#!/bin/bash
# Maat Balance: gitMaat Activation Script
# Purpose: Activate gitMaat logging for all agents

set -e

WORKSPACE_ROOT="/home/suspect/.n8n"
cd "$WORKSPACE_ROOT"

echo "=== Maat Balance: gitMaat Activation ==="
echo ""

# Test gitMaat connection
echo "1. Testing gitMaat connection..."
python3 << 'EOF'
import sys
sys.path.insert(0, '/home/suspect/.n8n/maatlangchain')
from maat_memory import MaatMemory

try:
    memory = MaatMemory()
    tasks = memory.get_tasks(status='pending', limit=1)
    print("   ✅ gitMaat connection successful")
    print(f"   📊 Database operational")
except Exception as e:
    print(f"   ❌ gitMaat connection failed: {e}")
    sys.exit(1)
EOF

if [ $? -ne 0 ]; then
    echo "   ❌ Cannot proceed - gitMaat not accessible"
    exit 1
fi

# Activate gitMaat for test agent
echo ""
echo "2. Activating gitMaat logging..."
python3 << 'EOF'
import sys
sys.path.insert(0, '/home/suspect/.n8n/maatlangchain')
from maat_memory.activation import GitMaatActivator, get_unique_agent_id

activator = GitMaatActivator()
test_agent = get_unique_agent_id("activation_test")

if activator.enable_agent_logging(test_agent):
    print(f"   ✅ Activated gitMaat for: {test_agent}")
    
    # Test logging
    session_id = activator.auto_log_session(test_agent, "gitMaat activation test")
    task_id = activator.auto_log_task(test_agent, "Activation Test", "Testing gitMaat activation system")
    
    print(f"   ✅ Test session logged: {session_id}")
    print(f"   ✅ Test task logged: {task_id}")
    print("   ✅ gitMaat activation successful!")
else:
    print("   ❌ Activation failed")
    sys.exit(1)
EOF

if [ $? -ne 0 ]; then
    echo "   ❌ Activation failed"
    exit 1
fi

# Instructions for agents
echo ""
echo "3. Agent Integration Instructions:"
echo "   To use gitMaat in your agent code:"
echo ""
echo "   from maatlangchain.maat_memory.activation import activate_gitmaat, log_agent_action"
echo "   from maatlangchain.maat_memory import get_unique_agent_id"
echo ""
echo "   agent_id = get_unique_agent_id('your_agent_name')"
echo "   activate_gitmaat(agent_id)"
echo "   log_agent_action(agent_id, 'Action description')"
echo ""

# Summary
echo "=== Activation Summary ==="
echo "✅ gitMaat connection verified"
echo "✅ Activation system tested"
echo "✅ Ready for agent integration"
echo ""
echo "📋 Next steps:"
echo "   1. Integrate activation.py into agent code"
echo "   2. Enable logging in Cursor, OpenCode, MaatCode"
echo "   3. Start tracking sessions, tasks, changes"
echo ""
echo "=== Maat Balance: gitMaat activation complete ==="

