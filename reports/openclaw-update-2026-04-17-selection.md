# OpenClaw Update Selection - 2026-04-17

## Lane Topology

- Production lane: `/home/suspect/.n8n/openclaw` (local customized, dirty tree)
- Integration lane: `/home/suspect/.n8n/openclaw-integration` (fresh upstream shallow clone)
- Integration upstream HEAD: `5f3bb537888d5033b78aa2778752d0c63a686303`

## Selection Criteria Applied

Prioritize imports that reduce known risk:

1. Restore missing core agent/tool policy files in production lane.
2. Preserve local behavior in currently modified runner files.
3. Avoid broad merges while production lane remains heavily diverged.

## Candidate Modules for Selective Import

### Priority A (missing in production, present upstream)

- `src/agents/openclaw-tools.ts` (prod missing)
- `src/agents/tool-policy.ts` (prod missing)

Rationale: These are foundational for tool exposure/policy behavior and their absence likely contributes to agent/tool wiring inconsistencies.

### Priority B (present in both; compare and selectively adopt)

- `src/gateway/tools-invoke-http.ts`
- `src/agents/pi-embedded-runner/compact.ts`
- `src/agents/pi-embedded-runner/run/attempt.ts`

Rationale: These files are already locally modified in production. Import requires line-level diff review to avoid regressions.

## Explicit Deferrals

- No blanket merge/rebase of production lane.
- No direct pull into production lane.
- No promotion until validation gates pass in integration lane.

## Proposed Import Order

1. Restore missing Priority A files from integration lane into a controlled integration patch set.
2. Reconcile Priority B files with minimal-diff approach.
3. Run validation gates before any production promotion.
