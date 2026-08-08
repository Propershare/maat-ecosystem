# Maat Law: Task Storage and Coordination

## 🏛️ The Law

**Tasks MUST be stored in gitMaat (Maat Memory database). This is MAAT LAW.**

## 📋 The Rule

### Primary Source: gitMaat (Database)
- ✅ **MANDATORY:** All agents query gitMaat for tasks
- ✅ **Real-time:** All agents see same tasks immediately
- ✅ **Queryable:** Filter by status, priority, agent
- ✅ **Structured:** Title, description, status, priority, related_files
- ✅ **Updatable:** Agents can update status programmatically

### Secondary Source: PROMPT-NEXT-ACTION.md (Context Only)
- ⚠️ **Optional:** Read for high-level guidance
- ⚠️ **Context only:** Not for task assignment
- ⚠️ **Historical:** Shows what was done, not what to do

## 🔨 How Agents Must Work

### 1. Query gitMaat (MANDATORY)
```python
memory = MaatMemory()
tasks = memory.get_tasks(status="pending", limit=10)
```

### 2. Select Task from Database
```python
if tasks:
    task = tasks[0]  # Select from gitMaat results
    # Log that you're starting
    memory.log_task(agent_id, task['title'], task['description'], status="in_progress")
```

### 3. Update Status in gitMaat
```python
# When complete
memory.log_task(agent_id, task['title'], task['description'], status="completed")
```

### 4. Read .md (Optional, Context Only)
```python
# Only if you need context - NOT for task assignment
# Read PROMPT-NEXT-ACTION.md for historical context
```

## ❌ What NOT to Do

- ❌ **DON'T** use .md files as primary task source
- ❌ **DON'T** create tasks in .md files
- ❌ **DON'T** assign tasks via .md files
- ✅ **DO** query gitMaat for tasks
- ✅ **DO** create tasks in gitMaat
- ✅ **DO** update task status in gitMaat

## 🎯 Why This is Law

**Maat: Truth**
- Single source of truth (gitMaat database)
- No confusion about where tasks are
- Accurate task status across all agents

**Maat: Balance**
- No file conflicts (database handles concurrency)
- Real-time coordination (all agents see same tasks)
- Efficient querying (filter by status, priority, agent)

**Maat: Order**
- Consistent workflow (all agents follow same process)
- Structured data (database schema)
- Clear hierarchy (database primary, .md secondary)

**Maat: Justice**
- Fair access (all agents query same database)
- Equal treatment (same rules for all)
- Proper permissions (database handles access control)

**Maat: Self-Reflection**
- Audit trail (all task changes logged in database)
- System awareness (agents know where tasks are)
- Learning (can query task history)

## 📊 Task Schema (gitMaat)

Tasks in gitMaat have:
- `id` - Unique identifier
- `agent` - Assigned agent (optional)
- `title` - Task title
- `description` - Task description
- `status` - pending, in_progress, completed, blocked
- `priority` - high, medium, low
- `related_files` - Files related to task
- `dependencies` - Other tasks this depends on
- `created_at` - When task was created
- `updated_at` - When task was last updated

## 🔄 Task Lifecycle

1. **Create:** `memory.log_task(agent_id, title, description, status="pending")`
2. **Start:** Update status to "in_progress"
3. **Work:** Log changes, decisions, builds to gitMaat
4. **Complete:** Update status to "completed"
5. **Query:** Other agents see updated status immediately

## ✅ Verification

**To verify you're following the law:**

```python
# Check if tasks exist in gitMaat
tasks = memory.get_tasks(status="pending")
if tasks:
    print("✅ Following Maat Law - tasks from gitMaat")
else:
    print("⚠️  No tasks in gitMaat - check if you should create one")
```

---

**This is MAAT LAW. All agents must follow this. No exceptions.**

