# MCP servers — Ka spine (canonical home)

**This folder is the canonical location** for MCP / HTTP organ processes that belong to the **maat-ecosystem** lab spine (Ka discovery, Tehuti Core, Maat Memory, pipeline, audio, etc.).

## Lab root compatibility

At the monorepo root (`/home/suspect/.n8n/`), **`mcp-servers` is a symlink** → `maat-ecosystem/mcp-servers/`. Existing systemd units, scripts, and docs that use `…/mcp-servers/...` keep working unchanged.

## Layout (piece by piece)

| Directory | Role (typical) |
|-----------|----------------|
| `ka-discovery/` | HTTP **8010** — manifest / health |
| `tehuti-core/` | MCP **8014** — Tehuti Core (legacy MCP; gitMaat tools when DB configured) |
| `maat-memory/` | MCP **8022** — Maat Memory (gitMaat) |
| `maatlangchain-pipeline/` | Pipeline / RAG MCP (see service notes) |
| `tehuti-audio/` | Audio / TTS helpers |
| `templates/` | Shared templates |

Other sibling dirs (`n8n-mcp/`, `system-mcp/`, etc.) are additional MCP-related stacks as deployed in this lab.

**Tehuti Guard:** HTTP **8013** (`tehuti-guard/` at **lab root**, not here) — advertised on **`GET :8010/manifest`** as organ **`policy`**. See [`MANIFEST.ka`](../../MANIFEST.ka) `network.services`.

## Relation to `hands/`

- **`maat-ecosystem/hands/`** — compositions (apps, skills, Python **adapters** like `hands/mcps/mcp.py`).
- **`maat-ecosystem/mcp-servers/`** — **running** MCP server code and start scripts referenced by discovery and operators.

## Discovery

Prefer live URLs from **`GET http://<host>:8010/manifest`** — do not hardcode LAN IPs in clients. See **`docs/GITMAAT-CONNECT.md`** (repo root `docs/`). **Full lab tree + stack:** [`docs/LAB-CANONICAL-TREE-AND-STACK.md`](../../docs/LAB-CANONICAL-TREE-AND-STACK.md).
