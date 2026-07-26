# Lab Brain Bridge — Architecture & Confusion Log

## The Problem
Hermes Desktop has an Artifacts view that only scans chat transcripts for URLs/paths. The lab brain Postgres has a `maat_artifacts` table with 42 real artifacts (workflowware, guard decisions, audit reports, trade logs, command centers) from all lab machines. But the MCP tools (`maat_memory_read_*`) only expose the git-based markdown files in `~/maat-ecosystem/maat-memory/` — they do NOT query the Postgres `maat_artifacts` table.

## What Was Built Today (2026-07-26)

### Backend: `tui_gateway/server.py`
Added `@method("maat.artifacts.list")` — a JSON-RPC method that:
- Reads `PGVECTOR_DB_URL` from `~/.openclaw/.env`
- Queries `maat_artifacts` table (id, uri, title, artifact_type, status, agent, produced_at, description)
- Returns artifact records sorted by produced_at DESC

### Frontend: `apps/desktop/src/app/artifacts/index.tsx`
Modified `ArtifactsView` to:
- Import `useGatewayRequest` hook
- Call `requestGateway('maat.artifacts.list', { limit: 50 })` alongside the existing session scan
- Merge lab brain artifacts into the same display grid/table
- Each maat artifact gets a `🧠` badge showing type + source agent

### Files Changed
1. `/Users/ps/.hermes/hermes-agent/tui_gateway/server.py` — added ~55 lines for `@method("maat.artifacts.list")`
2. `/Users/ps/.hermes/hermes-agent/apps/desktop/src/types/hermes.ts` — added `MaatArtifact` + `MaatArtifactsResponse` types
3. `/Users/ps/.hermes/hermes-agent/apps/desktop/src/app/artifacts/index.tsx` — added `useGatewayRequest` import + maat fetch logic

### Build
`hermes desktop --force-build` completed successfully. New Hermes.app at `apps/desktop/release/mac/Hermes.app`.

## Git Status
- maat-ecosystem commit: `0bd3756 maat-memory: lab-brain bridge audit + architecture proposal`
- Push FAILED: no git auth on this machine (no GH_TOKEN, no SSH keys, gh not logged in)
- Remote: `https://github.com/Propershare/maat-ecosystem.git`

## What the Other Agent Needs to Do
1. Pull maat-ecosystem on staydangerous machine (has git auth)
2. Deploy the `@method("maat.artifacts.list")` backend change to that machine's Hermes
3. Deploy the frontend changes + rebuild desktop app there
4. Add `ring` column to `maat_artifacts` table for visibility tiers
5. Build `maat.artifacts.create` MCP tool so agents can push artifacts on creation
6. Wire Hermes agent to push artifacts on file/image generation (replace session-scanning)
7. Remove session-scanning fallback once push protocol is verified

## Key Insight
The MCP tools (`maat_memory_read_episodic`, `maat_memory_read_semantic`) only read git-based markdown files. They do NOT expose the Postgres `maat_artifacts` table. This is the core confusion — the lab brain has two separate memory systems that don't talk to each other. The bridge built today connects Hermes Desktop to Postgres directly, but the MCP tools still need updating to expose `maat_artifacts` as a first-class resource.