# Machine & Terminal Tracking - Maat Memory

**Date:** 2025-12-21  
**Purpose:** Track which agent, machine, and terminal each session/conversation comes from

---

## 🎯 What's Tracked

Every session and conversation now automatically includes:

- **Agent**: Which agent (cursor, opencode, etc.)
- **Hostname**: Machine name (imhotep, macdaddy, imhotepjr)
- **Machine ID**: Unique machine identifier (hostname + MAC address)
- **Terminal ID**: Terminal session identifier
- **Project Path**: Which project directory
- **Working Directory**: Current working directory
- **User**: System user
- **Platform**: Operating system

---

## 🚀 Usage

### Basic Usage (Machine Info Auto-Detected)

**Important:** You still need to explicitly call these methods. "Automatic" means machine info is detected automatically when you call them.

```python
from maat_memory import MaatMemory

memory = MaatMemory()

# You must explicitly call start_session()
# Machine info is auto-detected when you call it
session_id = memory.start_session("cursor", "working on feature X")

# You must explicitly call log_conversation()
# Machine info is auto-detected when you call it
memory.log_conversation(
    agent="cursor",
    user_query="How do I implement Y?",
    agent_response="Here's how..."
)
```

**What "Automatic" Means:**
- ✅ Machine info (hostname, terminal, etc.) is detected automatically
- ❌ Sessions/conversations are NOT logged automatically - you must call the methods

### Query by Machine/Terminal

```python
from maat_memory import MaatMemory

memory = MaatMemory()

# Get all sessions from specific machine
sessions = memory.get_sessions(hostname="imhotep")

# Get sessions from specific terminal
sessions = memory.get_sessions(terminal_id="terminal-12345")

# Get sessions from specific agent on specific machine
sessions = memory.get_sessions(
    agent="cursor",
    hostname="imhotep"
)

# Search conversations from specific machine
conversations = memory.search_conversations(
    query="implement feature",
    hostname="imhotep",
    limit=10
)
```

### Display Session Info

```python
from maat_memory import MaatMemory
from maat_memory.format_session import format_session_info

memory = MaatMemory()
sessions = memory.get_sessions(limit=5)

for session in sessions:
    print(format_session_info(session))
    print("---")
```

**Output:**
```
Session ID: a1b2c3d4...
Agent: cursor
Machine: imhotep (imhotep-aa:bb:cc:dd:ee:ff)
Terminal: terminal-12345
Project: /home/suspect/.n8n/maatlangchain
Working Dir: /home/suspect/.n8n/maatlangchain
Started: 2025-12-21 10:00:00+00:00
Summary: working on feature X
---
```

---

## 🔍 Query Examples

### Find All Sessions from a Machine

```python
sessions = memory.get_sessions(hostname="imhotep")
for session in sessions:
    print(f"Agent: {session['agent']}")
    print(f"Terminal: {session['metadata']['terminal_id']}")
    print(f"Project: {session['metadata']['project_path']}")
```

### Find Conversations from Specific Terminal

```python
conversations = memory.search_conversations(
    query="RAG implementation",
    terminal_id="terminal-12345",
    limit=10
)
```

### Find All Cursor Sessions on MacDaddy

```python
sessions = memory.get_sessions(
    agent="cursor",
    hostname="macdaddy"
)
```

### Find Sessions by Project Path

```python
# Get all sessions and filter by project
sessions = memory.get_sessions(limit=100)
maatlangchain_sessions = [
    s for s in sessions 
    if s['metadata'].get('project_path', '').endswith('maatlangchain')
]
```

---

## 📊 Metadata Structure

Each session/conversation has a `metadata` JSONB field:

```json
{
  "hostname": "imhotep",
  "machine_id": "imhotep-aa:bb:cc:dd:ee:ff",
  "terminal_id": "terminal-12345",
  "working_directory": "/home/suspect/.n8n/maatlangchain",
  "project_path": "/home/suspect/.n8n/maatlangchain",
  "user": "suspect",
  "platform": "posix",
  "env": {
    "TERM": "xterm-256color",
    "SHELL": "/bin/bash"
  }
}
```

---

## 🔧 Custom Metadata

You can add custom metadata when creating sessions:

```python
memory.start_session(
    agent="cursor",
    summary="working on feature X",
    metadata={
        "custom_field": "custom_value",
        "project_version": "1.0.0"
    }
)
```

Custom metadata is merged with auto-detected machine info.

---

## ✅ Benefits

1. **Know Where Data Comes From**: Always know which machine/terminal
2. **Filter by Machine**: Query sessions from specific machines
3. **Filter by Terminal**: Query sessions from specific terminals
4. **Track Project Context**: Know which project directory
5. **Debug Issues**: Identify which machine had problems
6. **Audit Trail**: Complete tracking of where actions occurred

---

## 🏛️ Maat Principles

- **Truth**: Always know where data comes from
- **Order**: Clear structure for tracking
- **Self-Reflection**: Can review where work was done

---

**Machine and terminal tracking is now automatic. Just use Maat Memory normally!**

