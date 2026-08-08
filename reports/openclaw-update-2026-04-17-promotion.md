# OpenClaw Update Promotion Decision - 2026-04-17

## Decision

**NO-GO** for production promotion in this cycle.

## Why

Validation gate summary:

- Runtime health: pass
- Behavior parity (smoke): pass
- Maat memory gate: fail (config wiring gap)
- Safety gate: pass

Promotion criterion requires all gates to pass; memory gate did not.

## Rollback Marker (active baseline)

Keep production at:

- Repo: `/home/suspect/.n8n/openclaw`
- Commit: `718dba8cb69201e3163a62a3542a9777e4df0538`
- Config metadata marker:
  - `meta.lastTouchedVersion=2026.4.14`
  - `meta.lastTouchedAt=2026-04-15T12:07:24.260Z`

Recovery artifacts retained:

- `/home/suspect/.n8n/backups/openclaw-config-sanitized-2026-04-17.json`
- `/home/suspect/.n8n/backups/openclaw-prod-working-diff-2026-04-17.patch`

## Iteration Plan (integration lane only)

1. Add explicit memory/MCP wiring in runtime config expectations:
   - memory slot mapping
   - MCP bridge (mcporter-equivalent) endpoints for 8010/8022/8014
2. Re-run validation gates:
   - verify actual agent memory tool invocation, not just HTTP reachability
3. Re-issue promotion decision only after memory gate passes.
