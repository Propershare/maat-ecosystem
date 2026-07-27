# Lab Brain Bridge — Corrected Architecture

## Date: 2026-07-26
## Author: Hermes Agent (middle-ring)
## Status: Implemented

## What Was Built

Two new MCP tools added to `maat_memory_mcp.py` in `~/maat-ecosystem/maat-memory/`:

### `maat_memory_read_artifacts`
Queries the lab brain Postgres `maat_artifacts` table directly. Returns artifact records with id, uri, title, artifact_type, status, agent, produced_at, description. Supports optional `limit` and `artifact_type` filter.

### `maat_memory_write_artifact`
Inserts into `maat_artifacts` table. Optionally stores content in `maat_artifact_objects` with SHA256 content addressing. Accepts: uri, title, artifact_type, status, agent, description, content, content_type, logical_path.

## Corrected Architecture (from earlier mistake)

**WRONG approach (reverted):** Adding `@method("maat.artifacts.list")` to Hermes backend (`tui_gateway/server.py`) — only works in the desktop app on one machine.

**RIGHT approach (implemented):** Adding tools to `maat_memory_mcp.py` — the shared MCP server that every agent on every machine already has configured. Any agent can call `maat_memory_read_artifacts` or `maat_memory_write_artifact` immediately after pulling the updated maat-ecosystem.

## Key Insight
The MCP tools (`maat_memory_read_*`) previously only exposed git-based markdown files in `~/maat-ecosystem/maat-memory/`. They did NOT query the Postgres `maat_artifacts` table. This was the core gap — the lab brain has two separate memory systems that didn't talk to each other. Now they do.

## Next Steps
1. Other agents pull maat-ecosystem to get the new tools
2. Wire Hermes agent to call `maat_memory_write_artifact` on file/image generation (push protocol replaces session-scanning)
3. Add `ring` column to `maat_artifacts` for visibility tiers
4. Remove the Hermes-specific backend method once push protocol is verified