# Tools — Plug & Play

## How Tools Work

Maat agents use tools via [MCP (Model Context Protocol)](https://modelcontextprotocol.io).
Any MCP server is automatically a Maat tool.

## Adding an MCP Server

### 1. Start the server

```bash
# Example: a custom MCP server on port 9000
python my_mcp_server.py --port 9000
```

### 2. Run adapt

```bash
maat adapt
```

If the server is on a known port (8011-8021), it's auto-detected.
Otherwise, add it manually:

### 3. Or add to config

```yaml
# ~/.maat/config.yaml
tools:
  mcp_servers:
    - name: "my-tool"
      url: "http://localhost:9000"
```

### 4. Restart

```bash
maat start
```

The agent now has access to all tools exposed by that MCP server.

## Built-in MCP Servers

| Server | Port | Tools |
|--------|------|-------|
| maat-core | 8014 | `execute_command`, `read_file`, `write_file`, `query_gitmaat`, `list_files` |
| maat-research | 8012 | `search_documents`, `ingest_document`, `web_search` |
| maat-creative | 8019 | `generate_image`, `text_to_speech`, `list_models` |
| maat-memory | 8018 | `query_memory`, `log_task`, `log_decision`, `log_learning` |
| maat-filesystem | 8016 | `read`, `write`, `list`, `search` |
| maat-postgres | 8017 | `query`, `execute` |

## Writing a Custom MCP Server

```python
# my_tool_server.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("My Custom Tool")

@mcp.tool()
async def search_notes(query: str, limit: int = 5) -> str:
    """Search my personal notes for a topic."""
    # Your implementation
    results = my_db.search(query, limit)
    return format_results(results)

@mcp.tool()
async def create_note(title: str, content: str) -> str:
    """Create a new note."""
    my_db.insert(title, content)
    return f"Created note: {title}"

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

Run it with mcpo to expose as HTTP:

```bash
uvx mcpo --host 0.0.0.0 --port 9000 -- python my_tool_server.py
```

## Tool Security

All tool calls pass through Guard:

1. **Access check** — Does this agent have `execute` permission?
2. **Command scan** — If the tool runs a shell command, is it safe?
3. **Audit log** — Every tool call is logged to `maat_audit_trail`

Tools from inner-ring agents can only call `read`-type tools.
Tools from middle-ring agents can `propose` actions (queued for review).
Tools from outer-ring agents can execute anything.

## Auto-Discovery

When you run `maat adapt`, it:

1. Probes ports 8011-8021 for TCP connections
2. For each live port, checks against known MCP server list
3. Adds discovered servers to config
4. The agent can now use them

No manual configuration needed for standard ports.
