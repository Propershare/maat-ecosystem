# OpenCode MCP Bootstrap — Lessons

## What works
- **stdio JSON-RPC** servers (FastMCP) — `type: local`, `command: [python, server.py]`
- Example: `tehuti-core` (`/home/suspect/.n8n/mcp-servers/tehuti-core/tehuti_core_server.py`)
- Example: `maat-memory` (`/home/suspect/.n8n/mcp-servers/maat-memory/.venv/bin/python maat_memory_server.py`)

## What DOES NOT work
- **HTTP/TCP daemons** (mcpo, raw uvicorn, BaseHTTP) launched as stdio MCPs
  - opencode times out waiting for stdio JSON-RPC frames → `WARN server unavailable status=failed`
  - Long-lived orphan daemons on the same port then cause `EADDRINUSE` on respawn
- **bash launchers** that wrap a stdio server in mcpo for HTTP auth — the bash exits to mcpo, not to stdio JSON-RPC

## Diagnostic commands
```bash
# 1. Find failures in the log
grep -E "server unavailable|EADDRINUSE" ~/.local/share/opencode/log/opencode.log | tail

# 2. Check what's holding the port
ss -ltnp | grep -E ":(8022|8010) "

# 3. Verify stdio server works on its own
{ printf '%s\n' \
  '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"smoke","version":"0"}}}' \
  '{"jsonrpc":"2.0","method":"notifications/initialized"}' \
  '{"jsonrpc":"2.0","id":2,"method":"tools/list"}'; sleep 2; } \
  | /path/to/.venv/bin/python /path/to/server.py
```

## Available MCP servers (this host)
- `tehuti-core` — file ops, gitMaat, Florida trust law RAG (stdio, working)
- `maat-memory` — 23 tools, log_* / get_* / search / artifacts (stdio, fixed 2026-08-08)
- `ka-discovery` — HTTP-only, no stdio equivalent, **removed from opencode.json**

## Open MCPs that need stdio wrappers (deferred)
- `ka-discovery` (HTTP, :8010)
- `maatlangchain-pipeline` (HTTP, uvicorn)
- `tehuti-audio` (HTTP, uvicorn)
- `n8n-mcp`, `system-mcp`, `monetization-mcp`, `ka-education` — empty dirs

## Config location
`/home/suspect/.config/opencode/opencode.json` → `mcp.*` block
