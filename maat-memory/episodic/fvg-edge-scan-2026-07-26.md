# Episodic Memory — 2026-07-26
timestamp: 2026-07-26T12:58:22.405309+00:00
source: hermes-agent

2026-07-26 — Built Hermes Desktop ↔ Lab Brain bridge. Added @method('maat.artifacts.list') to tui_gateway/server.py that queries maat_artifacts table from Postgres. Modified ArtifactsView in apps/desktop/src/app/artifacts/index.tsx to fetch lab brain artifacts alongside session-scanned ones. Rebuilt desktop app. 42 artifacts now visible. Wrote full architecture + confusion log to semantic memory. Key insight: MCP tools (maat_memory_read_*) only expose git-based markdown files, NOT the Postgres maat_artifacts table — this is the core gap. Push to gitMaat failed (no git auth on this machine). The other agent on staydangerous needs to pull maat-ecosystem, deploy the backend/frontend changes, and build the maat.artifacts.create MCP tool to complete the push protocol.
