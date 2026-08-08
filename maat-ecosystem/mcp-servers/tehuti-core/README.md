# Tehuti Core MCP Server - MaatCode Powers

## 🎯 Purpose

Tehuti Core provides **MaatCode powers** - terminal execution, code running, and system management capabilities through the WebUI.

## 🛠️ Tools Available

1. **`execute_command`** - Run shell commands in terminal
2. **`run_python_code`** - Execute Python code
3. **`get_system_info`** - Get system/workspace information
4. **`list_directory`** - List directory contents
5. **`read_file`** - Read files (with safety limits)
6. **`query_gitmaat`** - Query Maat Memory (tasks, changes, learnings, decisions)
7. **`log_gitmaat_task`** - Insert a task (`maat_tasks`)
8. **`log_gitmaat_change`** - Log a file change (`maat_changes`)
9. **`log_gitmaat_decision`** - Log a decision (`maat_decisions`)
10. **`log_gitmaat_learning`** - Log a learning (`maat_learnings`)

Writes use `get_unique_agent_id("opencode")` for attribution.

## 🚀 Running the Server

### Standalone Test
```bash
cd /home/suspect/.n8n/mcp-servers/tehuti-core
python3 tehuti_core_server.py
```

### With MCP Inspector (for testing)
```bash
mcp-inspector stdio python3 /home/suspect/.n8n/mcp-servers/tehuti-core/tehuti_core_server.py
```

### Register in OpenCode

In workspace [`opencode.json`](../../opencode.json) (and optionally `~/.config/opencode/opencode.json` for IDE-wide use), an `mcp` entry runs this server over stdio:

```json
"mcp": {
  "tehuti-core": {
    "type": "local",
    "command": [
      "python3",
      "/home/suspect/.n8n/mcp-servers/tehuti-core/tehuti_core_server.py"
    ],
    "enabled": true
  }
}
```

Requirements: **`PGVECTOR_DB_URL`** reachable (server loads it from env or `.env` under the workspace). Use system `python3` with **`psycopg2`** (or adjust `command` to a venv that has `maat_memory` deps). Restart OpenCode after editing config.

### Register in Open WebUI

Add to WebUI's `TOOL_SERVER_CONNECTIONS` config:

```json
{
  "type": "mcp",
  "server_id": "tehuti-core",
  "command": "python3",
  "args": ["/home/suspect/.n8n/mcp-servers/tehuti-core/tehuti_core_server.py"],
  "env": {}
}
```

## 🔒 Security Features

- ✅ Workspace boundary enforcement (can't access outside workspace)
- ✅ Dangerous command blocking (rm -rf /, format, etc.)
- ✅ File read limits (max 1000 lines by default)
- ✅ Timeout protection (30s default, 60s for Python)

## 🏛️ Maat Principles

- **Truth**: Accurate command execution and results
- **Balance**: Safe but powerful terminal access
- **Order**: Structured tool interface, clear boundaries
- **Justice**: Fair access, proper error handling
- **Self-Reflection**: Logging all actions for learning

## 📝 Next Steps

1. Test server standalone
2. Register in Open WebUI
3. Test tool execution from WebUI
4. Add more tools as needed

