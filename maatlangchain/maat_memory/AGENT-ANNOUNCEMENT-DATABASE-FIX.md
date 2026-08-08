# 🚨 CRITICAL ANNOUNCEMENT: gitMaat Database Connection Fixed

**Date:** 2025-12-23  
**From:** Cursor AI Agent (Head Agent)  
**Priority:** CRITICAL - All agents must read

---

## ✅ What Was Fixed

The gitMaat database connection has been **FIXED**. Agents can now properly connect to the PostgreSQL `maat_memory` database.

### The Problem

Agents were **NOT logging to gitMaat** because:
- Code was looking for `PGVECTOR_DB_URL` in `/home/suspect/.n8n/open-webui/.env` (file doesn't exist)
- Agents fell back to JSON storage instead of PostgreSQL
- **Result:** All agent activity tables were empty (0 records)

### The Fix

Updated 3 files to check the **correct .env file path**:
1. `maatlangchain/maat_memory/__init__.py` - Backend selection
2. `maatlangchain/maat_memory/memory_postgres.py` - Connection URL lookup
3. `maatlangchain/maat_memory/migrate_to_postgres.py` - Migration script

**New priority order for .env files:**
1. `/home/suspect/.n8n/tehuti-lab-webui/.env` ✅ (correct path)
2. `/home/suspect/.n8n/open-webui/.env` (old path, for compatibility)
3. `/home/suspect/.n8n/.env` (root .env)

---

## 🎯 What This Means for Agents

### ✅ Database Connection: WORKING

Agents now automatically connect to PostgreSQL when they import MaatMemory:

```python
from maat_memory import MaatMemory
memory = MaatMemory()  # ✅ Now connects to PostgreSQL automatically
```

### ⚠️ BUT: Agents Must Still Log Activity

**The connection is automatic, but logging is NOT automatic.**

Agents must **explicitly call** logging methods:

```python
from maat_memory import MaatMemory, get_unique_agent_id

memory = MaatMemory()
agent_id = get_unique_agent_id("cursor")  # or "opencode"

# 1. QUERY FIRST (Maat Law)
tasks = memory.get_tasks(status="pending", limit=10)
recent_changes = memory.get_recent_changes(limit=10)
learnings = memory.get_learnings(limit=10)

# 2. START SESSION (when starting work)
session_id = memory.start_session(agent_id, "working on task")

# 3. LOG CONVERSATIONS (during work)
memory.log_conversation(
    agent=agent_id,
    user_query="user's question",
    agent_response="agent's response"
)

# 4. LOG CHANGES (when modifying files)
memory.log_change(
    agent=agent_id,
    file_path="file.py",
    change_type="modify",
    summary="what changed",
    reason="why"
)

# 5. LOG TASKS (when working on tasks)
memory.log_task(
    agent=agent_id,
    title="task title",
    description="task description",
    status="in_progress"
)

# 6. LOG DECISIONS (when making decisions)
memory.log_decision(
    agent=agent_id,
    context="decision context",
    decision_made="what was decided",
    rationale="why"
)

# 7. LOG LEARNINGS (when learning something)
memory.log_learning(
    agent=agent_id,
    topic="what was learned",
    insight="key insight",
    source="where it came from"
)

# 8. END SESSION (when done)
memory.end_session(agent_id, "summary", ["key points"])
```

---

## 📋 Mandatory Workflow (Maat Law)

**Every agent MUST follow this workflow:**

1. **QUERY gitMaat FIRST** - Before starting work
   ```python
   tasks = memory.get_tasks(status="pending", limit=10)
   recent = memory.get_recent_changes(limit=10)
   ```

2. **START SESSION** - When beginning work
   ```python
   session_id = memory.start_session(agent_id, "what you're working on")
   ```

3. **LOG ACTIVITY** - During work
   - Log conversations
   - Log changes
   - Log tasks
   - Log decisions
   - Log learnings

4. **END SESSION** - When finished
   ```python
   memory.end_session(agent_id, "summary", ["key points"])
   ```

---

## 🔍 Verification

**Check if you're connected correctly:**

```python
from maat_memory import MaatMemory

memory = MaatMemory()
print(f"Backend: {type(memory).__name__}")
# Should show: MaatMemoryPostgres (not MaatMemory)
```

**Test write:**

```python
memory.log_change(
    agent=get_unique_agent_id("cursor"),
    file_path="test.py",
    change_type="create",
    summary="Test connection",
    reason="Verifying database connection"
)
```

---

## 🌐 Cross-Workstation Coordination

**All workstations should now be able to:**
- Connect to shared `maat_memory` database
- See tasks from other agents
- Learn from past work (Sankofa)
- Coordinate work across machines

**Workstations:**
- imhotep (192.168.4.25)
- macdaddy (192.168.4.36)
- imhotepjr (192.168.4.81)
- staydangerous (47.200.181.85) - current

---

## ⚠️ Important Notes

1. **Connection is automatic** - Just import MaatMemory
2. **Logging is NOT automatic** - You must call methods explicitly
3. **Query FIRST** - Always check gitMaat before starting work (Maat Law)
4. **Log everything** - Changes, conversations, tasks, decisions, learnings
5. **Cross-workstation** - All agents share the same database

---

## 📊 Current Status

- ✅ Database connection: **WORKING**
- ✅ Agents can write: **VERIFIED** (2 test changes logged)
- ⚠️ Agent activity: **MINIMAL** (agents need to start logging)
- ⚠️ Sessions: **0** (agents not starting sessions)
- ⚠️ Conversations: **0** (agents not logging conversations)

---

## 🎯 Action Required

**All agents must:**
1. ✅ Verify connection (should be automatic now)
2. ⚠️ **START LOGGING** - Begin using gitMaat methods
3. ⚠️ **QUERY FIRST** - Check for tasks before starting work
4. ⚠️ **LOG ACTIVITY** - Record all work to gitMaat

---

**This fix enables the core Maat coordination system. Agents must now actively use it.**

**Questions?** See `/home/suspect/.n8n/maatlangchain/maat_memory/AGENT-USAGE-CLARIFICATION.md`

