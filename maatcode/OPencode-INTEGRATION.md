# OpenCode + MaatCode Integration Guide

## Overview

This guide shows how to use OpenCode with MaatCode tools for enhanced building capabilities.

## What You Get

**OpenCode** (base agent):
- Terminal-based AI coding agent
- Can read/write files
- Can run commands
- Can build projects autonomously
- Uses your Ollama models (`qwen2.5:14b`)

**MaatCode** (enhancements):
- ✅ gitMaat memory (remembers past work)
- ✅ Task coordination (works with other agents)
- ✅ Project discovery (knows what's missing)
- ✅ Pattern detection (finds issues automatically)
- ✅ Knowledge base access (your UKMT knowledge)

## Setup

### 1. Test MaatCode Integration

```bash
cd /home/suspect/.n8n/maatcode
python3 test_maatcode_integration.py
```

This verifies:
- gitMaat connection
- Task retrieval
- Change logging
- Conversation search
- Project discovery

### 2. Start MaatCode Servers

**MCP Server** (for OpenCode integration):
```bash
cd /home/suspect/.n8n/maatcode
python3 mcp_server.py
```

**API Server** (for WebUI integration):
```bash
cd /home/suspect/.n8n/maatcode
python3 api_server.py
```

### 3. Configure OpenCode

Your `opencode.json` is already configured with:
- Models: `qwen2.5:14b` and `llama3.2:3b`
- Instructions: `.cursor/rules/**/*.md` and `**/AGENTS.md`
- Default agent: `build`

## Using OpenCode with MaatCode

### Basic Usage

OpenCode works in your terminal. Just run:
```bash
opencode
```

Or use the default agent:
```bash
opencode build
```

### MaatCode Tools Available

When OpenCode is running, it can use MaatCode tools via MCP:

**1. Get Tasks:**
```
"Get my pending tasks from gitMaat"
```

**2. Log Changes:**
```
"Log that I created api/main.py"
```

**3. Search Past Work:**
```
"Search for conversations about RAG integration"
```

**4. Discover Project:**
```
"Discover what's missing in maatlangchain project"
```

**5. Ask Questions:**
```
"Ask: How do I integrate RAG with OpenCode?"
```

## Example: Building with OpenCode + MaatCode

### Scenario: Build a new API endpoint

**1. OpenCode can:**
- Create the file
- Write the code
- Test it
- Run commands

**2. MaatCode adds:**
- Remembers similar endpoints you built before
- Checks if endpoint follows Maat principles
- Logs the change to gitMaat
- Coordinates with other agents if needed

### Example Commands

**To OpenCode:**
```
"Build a new API endpoint /api/test that returns 'Hello Maat'"
```

**What happens:**
1. OpenCode creates `api/test.py`
2. OpenCode writes the endpoint code
3. MaatCode logs the change to gitMaat
4. MaatCode checks for similar endpoints
5. MaatCode verifies Maat compliance

## Advantages Over Claude Code

### 1. Memory
- **Claude Code**: Forgets between sessions
- **MaatCode**: Remembers everything via gitMaat

### 2. Coordination
- **Claude Code**: Single agent
- **MaatCode**: Coordinates with OC1, OC2, other agents

### 3. Knowledge
- **Claude Code**: Generic knowledge
- **MaatCode**: Your UKMT knowledge base + past work

### 4. Project Awareness
- **Claude Code**: Sees current files
- **MaatCode**: Knows what's missing, suggests builds

## Troubleshooting

### MaatCode tools not available?

1. Check MCP server is running:
```bash
ps aux | grep mcp_server.py
```

2. Check gitMaat connection:
```bash
python3 test_maatcode_integration.py
```

3. Verify environment:
```bash
echo $PGVECTOR_DB_URL
```

### OpenCode not finding tools?

1. Check OpenCode config:
```bash
cat opencode.json
```

2. Verify MCP server connection
3. Check OpenCode logs

## Next Steps

1. ✅ Test MaatCode integration
2. ✅ Start MaatCode servers
3. ✅ Use OpenCode with MaatCode tools
4. ✅ Build something and see the difference!

## Support

- MaatCode MCP Server: `/home/suspect/.n8n/maatcode/mcp_server.py`
- MaatCode API Server: `/home/suspect/.n8n/maatcode/api_server.py`
- Test Script: `/home/suspect/.n8n/maatcode/test_maatcode_integration.py`

