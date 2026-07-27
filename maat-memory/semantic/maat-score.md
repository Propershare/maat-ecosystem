# MAAT Score — Lab Brain Bridge (2026-07-26)

## Score: 6.5 / 10

### What Works (Score: 8/10)
- maat_artifacts table: 50 artifacts across 36 types
- maat_artifact_objects: content-addressed storage with SHA256
- maat_memory_mcp.py: 7 tools (5 git-based + 2 Postgres)
- Multi-machine: 6 agents writing (cursor_staydangerous_data_drive, hermes-agent, cursor_staydangerous, hermes-default, tehuti-scholar, tehuti)
- Fleet handoff artifacts already exist (Lab Spine, Fleet Handoff doc)
- MAAT-HANDOFF-PROTOCOL-v0.md and MAAT-AGENT-SIGNUP-LAYMAN-v0.md now being defined by staydangerous agent

### What's Missing (Score: 4/10)
- No push protocol: agents don't call maat_memory_write_artifact on creation
- No ring column: no visibility tiers (inner/middle/outer)
- No handoff protocol: agent A writes → agent B picks up → acknowledges
- MCP tools still don't expose maat_artifact_objects content (only metadata)
- Hermes Desktop still session-scans instead of using MCP tools
- No git auth on this machine (can't push to GitHub)

### Fleet Handoff Readiness: 5/10
- Handoff artifacts exist (Lab Spine, Fleet Handoff doc, Tehuti Guard handoff)
- maat_memory_write_artifact can create handoff records
- MAAT-HANDOFF-PROTOCOL-v0.md being drafted by staydangerous agent
- No acknowledgment/verification flow yet
- No standard handoff schema enforced

### Next Priority
1. Define handoff protocol schema (what fields every handoff must have)
2. Add ring column to maat_artifacts
3. Wire Hermes agent to call maat_memory_write_artifact on file/image gen
4. Build acknowledgment flow (agent B reads → marks received)

### Artifact ID in Lab Brain
maat://artifact/19736fc6-d881-475d-8eb4-fc8e5ba4442f