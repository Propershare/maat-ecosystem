# Transition Scorecard Data Map

Companion to `docs/TRANSITION-SCORECARD.md`.
Goal: make weekly scoring evidence-driven with concrete sources and repeatable pulls.

## Weekly run order (30-45 min)

1. Run spine and policy smoke (`scripts/lab-runtime-check.sh`).
2. Pull core service health (`:8010`, `:8013`, `:8014`, `:8022`, `:4242`).
3. Pull gitMaat-backed task/change/decision counts (when Postgres is reachable).
4. Collect governance decision samples (`POST /decision` logs + optional DB rows).
5. Score indicators with evidence links.

If Postgres is down, mark impacted indicators as `blocked` and continue scoring the rest.

## Indicator-to-data mapping

| # | Indicator | Primary evidence | Backup evidence | Collection method |
|---|-----------|------------------|-----------------|-------------------|
| 1 | Useful throughput | gitMaat task completions/week | merged PR/commit count for governed work | Query `maat_memory` tasks by `status=completed` in 7d |
| 2 | Reliability | `scripts/lab-runtime-check.sh` pass/fail history | service health snapshots (`/health`, `/manifest`) | Run smoke 1-3x/day, weekly success % |
| 3 | Recovery discipline | incident log timestamps (`down_at`, `restored_at`) | terminal/service restart logs | MTTR from incident records |
| 4 | Memory durability | gitMaat `log_change/log_decision/log_learning` within 24h | dated notes if DB unavailable | % substantive changes logged in 24h |
| 5 | Contract coverage | schema inventory (`maat-contracts`, `maat-ecosystem/skeleton/schemas`) | contract refs in READMEs/docs | count high-impact flows with explicit schema/contract |
| 6 | Governance enforcement | Tehuti Guard `POST /decision` outcomes + matched_rules | forge preflight guard checks | % protected actions with decision-gate evidence |
| 7 | Human override quality | escalation records with rationale | PR comments/decision docs | % escalations with explicit rationale + closure |
| 8 | Cross-node federation | connected nodes from discovery + session index usage | active multi-node workflows | count nodes interoperating this week |
| 9 | Economic efficiency | cost per successful governed workflow | GPU/runtime utilization trend | 4-week trend of cost/workflow |
| 10 | Reuse vs reinvention | workflows/components reused vs net-new | import/module reuse in new workflows | % new workflows built from existing components |
| 11 | Security posture | unresolved high-risk findings backlog | guard/security audit docs | count unresolved >7 days |
| 12 | Learning velocity | learnings converted to standards/playbooks | docs diffs tagged from incidents | # validated learnings operationalized/week |
| 13 | External legitimacy | repeat external users/stakeholders consuming outputs | recurring external requests fulfilled | count repeat external consumers/week |
| 14 | Institutional autonomy | core ops runnable without external dominant providers | fallback modes working (local models/tools) | % core operations completed with internal stack |
| 15 | Labor transformation | automated pipeline runs vs manual interventions | runbooks replacing ad hoc ops | % work shifted to reproducible pipelines |
| 16 | Mission alignment | outputs mapped to strategic priorities | weekly review notes | % outputs linked to declared priorities |

## Concrete source anchors in this workspace

- Spine and smoke checks: `scripts/lab-runtime-check.sh`, `docs/RUNTIME-HOOKUP.md`
- Guard wire contract and decisions: `docs/ENDPOINTS-AND-DECISIONS.md`, `tehuti-guard/guard/README.md`
- System topology + dependencies: `docs/SYSTEM-CONNECTIONS.md`, `docs/GITMAAT-CONNECT.md`
- Forge preflight with guard: `maat-forge/README.md`, `maat-forge/lib/guard-preflight.mjs`
- Sentinel posture view: `maat-sentinel/README.md`
- Contract and schema loci: `maat-contracts/`, `maat-ecosystem/skeleton/schemas/`
- gitMaat memory endpoints: `maatlangchain/maat_memory/`, `maat-ecosystem/mcp-servers/maat-memory/`

## Baseline worksheet (week 0)

Use this once, then copy weekly.

| # | Score (0/1/2) | Status | Evidence | Note |
|---|---------------|--------|----------|------|
| 1 |  | blocked/ready | gitMaat tasks query | Postgres dependency |
| 2 |  | ready | `lab-runtime-check` runs | no DB required |
| 3 |  | blocked/partial | incident timestamps | needs incident log discipline |
| 4 |  | blocked/ready | gitMaat log rows | blocked if DB down |
| 5 |  | ready | schema/contract inventory | file-based |
| 6 |  | ready | Guard decision samples | no DB required for API check |
| 7 |  | partial | escalation rationale records | process maturity dependent |
| 8 |  | partial | discovery + active nodes | depends on active multi-node sessions |
| 9 |  | blocked/partial | workflow cost records | needs cost ledger |
| 10 |  | partial | reuse stats in new workflows | needs tagging discipline |
| 11 |  | partial | security backlog list | needs central queue |
| 12 |  | partial | playbook/standard updates | needs weekly tagging |
| 13 |  | partial | repeat stakeholder usage | needs external usage log |
| 14 |  | partial | local-only run capability checks | can be tested per path |
| 15 |  | partial | pipeline vs manual counts | needs run tracking |
| 16 |  | ready | weekly outputs mapped to priorities | review-driven |

## Minimum evidence pack per week

- 1 screenshot/text capture of spine health (`lab-runtime-check` output).
- 1 guard decision sample with `correlation_id`.
- 1 gitMaat query snapshot (or explicit DB outage note).
- 1 contract coverage delta (new/updated schema or contract check).
- 1 decision memo: top 2 weak indicators and next-week fixes.

This sheet is intentionally strict: unknown metrics should be marked `blocked` or `partial`, not guessed.
