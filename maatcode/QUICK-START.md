# MaatCode Quick Start

## Test Integration (30 seconds)

```bash
cd /home/suspect/.n8n/maatcode
python3 test_maatcode_integration.py
```

This verifies MaatCode can access gitMaat and all tools work.

## Start Servers

**MCP Server** (for OpenCode):
```bash
python3 mcp_server.py
```

**API Server** (for WebUI):
```bash
python3 api_server.py
```

## Use with OpenCode

OpenCode is already configured in `opencode.json`. Just run:
```bash
opencode
```

MaatCode tools are available via MCP protocol.

## What MaatCode Adds to OpenCode

✅ **Memory**: Remembers past work via gitMaat  
✅ **Coordination**: Works with other agents  
✅ **Discovery**: Knows what's missing in projects  
✅ **Knowledge**: Accesses your UKMT knowledge base  
✅ **Patterns**: Detects issues automatically  

## Example

**Tell OpenCode:**
```
"Build a new API endpoint /api/test"
```

**MaatCode automatically:**
- Logs the change to gitMaat
- Checks for similar endpoints
- Verifies Maat compliance
- Coordinates with other agents

## Full Guide

See `OPencode-INTEGRATION.md` for complete documentation.

