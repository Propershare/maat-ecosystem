# Agent Coordination Protocol

## 🆔 Unique Agent IDs

**CRITICAL:** Each agent instance must use a unique ID. Never use generic "oc1" or "oc2".

### Agent ID Format

- **Cursor:** `cursor_<hostname>`
  - Example: `cursor_imhotep`, `cursor_macdaddy`
  
- **OpenCode:** `opencode_<hostname>_<terminal_id>`
  - Example: `opencode_imhotep_terminal_12345`
  - Example: `opencode_macdaddy_terminal_67890`
  - Example: `opencode_imhotepjr_terminal_99999`

### How to Get Your Agent ID

```python
from maat_memory.machine_info import get_unique_agent_id

# For Cursor
agent_id = get_unique_agent_id("cursor")

# For OpenCode
agent_id = get_unique_agent_id("opencode")
```

### Why Unique IDs Matter

1. **Accurate Tracking:** Know which agent (on which machine/terminal) did what
2. **Session History:** Each agent's sessions are tracked separately
3. **Task Reporting:** See which agent completed which task
4. **Workspace History:** Track changes by agent/machine/terminal
5. **No Conflicts:** Multiple OpenCode instances can work simultaneously

## 🔄 Coordination Workflow

### Starting Work
1. **Get your unique agent ID**
2. **Check Maat Memory** for recent work by other agents
3. **Start session** with your unique ID
4. **Log your start** to Maat Memory

### During Work
- **Log progress** with your unique agent ID
- **Update task files** when status changes
- **Check Maat Memory** before major changes

### Completing Work
1. **Log completion** with your unique agent ID
2. **Update task files** with completion status
3. **End session** properly

## 📋 Example Usage

```python
from maat_memory import MaatMemory
from maat_memory.machine_info import get_unique_agent_id

# Get your unique ID (auto-detects machine/terminal)
agent_id = get_unique_agent_id("opencode")
print(f"My agent ID: {agent_id}")
# Output: "opencode_imhotep_terminal_12345"

# Use it for all memory operations
memory = MaatMemory()

# Start session
session_id = memory.start_session(
    agent=agent_id,
    summary="Working on WebUI optimization"
)

# Log conversation
memory.log_conversation(
    agent=agent_id,
    user_query="How do I optimize embeddings?",
    agent_response="Use Redis caching..."
)

# End session
memory.end_session(
    agent=agent_id,
    summary="Completed embedding caching",
    key_points=["Added Redis cache", "1-hour TTL", "Batch support"]
)
```

## 🔍 Querying by Agent

```python
# Get sessions for your agent
sessions = memory.get_sessions(agent=agent_id)

# Get sessions for all agents on your machine
from maat_memory.machine_info import get_machine_info
machine_info = get_machine_info()
sessions = memory.get_sessions(hostname=machine_info["hostname"])

# Search conversations by agent
conversations = memory.search_conversations(
    query="embedding cache",
    agent=agent_id
)
```

## 🚫 What NOT to Do

- ❌ Don't use generic IDs like "opencode" or "oc1"
- ❌ Don't hardcode agent IDs
- ❌ Don't assume you're the only agent working
- ✅ Always use `get_unique_agent_id()` to get your ID
- ✅ Always check Maat Memory before starting work
- ✅ Use Maat Memory for all memory operations (PostgreSQL-backed)

**See:** `AGENT-FILE-GUIDE.md` for complete file guide.

---

**Remember**: Your unique agent ID ensures accurate tracking across all laptops and terminals.

