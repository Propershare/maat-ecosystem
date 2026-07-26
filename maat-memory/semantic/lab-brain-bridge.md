# MAAT Audit — Hermes Desktop ↔ Lab Brain Bridge

## Date: 2026-07-26
## Author: Hermes Agent (middle-ring)
## Status: Proposed

## Issues Identified

1. **Token waste**: Artifacts view fetches 30 sessions + all messages + regex-scans every line, THEN also queries Postgres. O(n*m) with no caching.
2. **Dual source, no dedup**: Same artifact can appear in both chat history and maat_artifacts — no merge key.
3. **One-way bridge**: Hermes reads from maat_artifacts but never writes back. Generated images/files only live in chat transcripts.
4. **No ring enforcement**: maat_artifacts has no ring/visibility tier column. Middle-ring agents can read everything.

## Proposed Architecture

### Push Protocol (replaces scan)
- Every agent pushes artifact records when they produce them (generalize maat_memory_bridge.py pattern)
- Content addressing via SHA256 in maat_artifact_objects (already exists)
- Hermes Desktop artifacts view becomes a thin client: query maat.artifacts.list as PRIMARY source, drop session-scanning

### Ring Model
- Add `ring` column to maat_artifacts: inner (constitutional), middle (operational), outer (public)
- Guard enforces at query time

### Multi-Machine
- maat_machines + maat_storage_roots already track machines
- Each machine runs local agent that syncs to central Postgres
- URI scheme (maat://artifact/<id>) + maat_storage_roots for resolution

### Agent-Side Push
- Every tool call that produces a file, image, or execution result should push an artifact record
- maat_governance_events + maat_audit_trail already provide accountability
- maat_learnings with before_snapshot/after_snapshot/reversible enables learning doctrine

## Next Steps
1. Add `ring` column to maat_artifacts
2. Build maat.artifacts.create MCP tool
3. Wire Hermes agent to push artifacts on file/image generation
4. Test on gitmaat machine (staydangerous)
5. Remove session-scanning fallback once push protocol is verified