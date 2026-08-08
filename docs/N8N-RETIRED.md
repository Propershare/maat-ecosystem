# n8n — retired from Tehuti Lab

**Decision:** 2026-06-18 (operator)  
**Status:** Retired — not part of the Ma'at product, public site, or agent canon.

## What changed

- n8n workflow automation and n8n MCP (`:8015`) are **removed** from Ka discovery manifest and `MANIFEST.ka`.
- Agent docs (`.cursorrules`, site briefs) no longer list n8n as infrastructure.
- Code moved to **`_retired/n8n/`** (recoverable archive, not active path).

## What we use instead

- **OpenClaw** — channels, cron, tool execution (`:18790`)
- **Tehuti Guard** — policy before high-impact action (`:8013`)
- **Maat Memory** — coordination and audit (`:8022`)
- **LangGraph / orchestration manifest** — when wired (`MAAT_ORCHESTRATION_MANIFEST.md`)

## Note on workspace path

The lab root folder is still `/home/suspect/.n8n` (historical name). That is **not** an endorsement of n8n the product.
