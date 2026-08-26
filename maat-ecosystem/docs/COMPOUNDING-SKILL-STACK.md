# Compounding Skill Stack

**Status:** Constitutional contracts + maat-runtime operator playbook.

When building gets easier, demand becomes the bottleneck. The compounding skill stack encodes six capabilities as **structured workflows**, not giant prompts:

| Skill | Runtime role | Schema |
|-------|--------------|--------|
| Agents | Operator / Builder | (governed maat-runtime session) |
| Distribution | Distributor | `maat.distribution_map.v1` |
| Curation | Curator | `maat.content_sprint.v1` |
| Builder-distributor | Loop orchestrator | `maat.build_loop_state.v1` |
| IRL community | Community host | `maat.community_session.v1` |
| Robotics | Optional domain pack | (out of v1 scope) |

## Design law

Per [`docs/MAAT-LIGHTWEIGHT-INTELLIGENCE.md`](../../docs/MAAT-LIGHTWEIGHT-INTELLIGENCE.md):

- **MAAT governs the system, not the prompt.**
- Thin Foundation identity (~5 bullets) + skills on demand + subagent chains.
- Structured records in gitMaat / `.maat/compounding/events.jsonl`, not chat logs.

Per [`docs/SCOUT-ANALYST-ARCHIVIST.md`](../../docs/SCOUT-ANALYST-ARCHIVIST.md):

- **Scout finds** → **Analyst decides** → **Archivist remembers.**

## Schemas

Canonical JSON Schema files live in [`skeleton/schemas/`](../skeleton/schemas/):

| File | `$id` | `schema` const |
|------|-------|----------------|
| `maat_distribution_map.schema.json` | `maat:distribution_map:v1` | `maat.distribution_map.v1` |
| `maat_build_loop_state.schema.json` | `maat:build_loop_state:v1` | `maat.build_loop_state.v1` |
| `maat_content_sprint.schema.json` | `maat:content_sprint:v1` | `maat.content_sprint.v1` |
| `maat_community_session.schema.json` | `maat:community_session:v1` | `maat.community_session.v1` |

Examples: [`skeleton/schemas/examples/`](../skeleton/schemas/examples/).

## Canonical loop events

Emit alongside structured records (namespaced, no drift):

| Event | When |
|-------|------|
| `loop.build_tiny.started` | Builder begins tiny ship |
| `loop.build_tiny.completed` | Artifact ready |
| `loop.exposure.logged` | Showed to audience |
| `loop.confusion.captured` | Confusion signal recorded |
| `loop.story.revised` | Product + story updated |

## Builder-distributor loop

```
build_tiny → show_100 → watch_confusion → change_story → (repeat)
```

**48-hour sprint outputs:** 1 tiny tool, 1 landing page, 1 demo video, 3 clips, 3 posts, 2 DMs.

**Rule:** Confusion is data. Log it with `compounding_log` before revising story.

## Distribution map (pre-build)

1. Map where attention lives (newsletters, creators, communities, search terms).
2. Steal buyer language from the market.
3. Write pain sentence: "I know I should … but I never …"
4. Draft hooks (curiosity, fear, status, money).
5. **Demand before product** — validate pull before building OS-scale infrastructure.

## Curator 7-day sprint

```
I saw this → most people think → I think it means → here's the move
```

Timeline chaos → POV → short video (fast, opinionated, useful, entertaining).

**Rule:** `external_publish: true` only after explicit human approval.

## IRL community

- Start small: 8 people, one room, one sharp question.
- Send recap: best ideas, best quotes, one follow-up.
- `external_send: true` only after explicit human approval.

## maat-runtime integration

Operator guide: [`maat-runtime/packages/coding-agent/docs/compounding-skill-stack.md`](../../maat-runtime/packages/coding-agent/docs/compounding-skill-stack.md).

Enable via `maat startup` (business or agent-workflow foundation) or `.maat/settings.json`:

- Skills: `examples/skills/` (compounding-stack, builder-distributor, …)
- Extension: `examples/extensions/compounding-stack/`

Persistence:

- Local: `.maat/compounding/events.jsonl`
- gitMaat: `log_governance_event` with `record_type` matching schema family

## Compounding depth

| Depth | Outcome |
|-------|---------|
| Pick one skill | Useful |
| Combine two | Leverage |
| Combine three | One-person company |

## See also

- [`MAAT_ORCHESTRATION_MANIFEST.md`](../../MAAT_ORCHESTRATION_MANIFEST.md) — LangGraph when wired (future)
- [`docs/MAAT-PRODUCT-MAP.md`](../../docs/MAAT-PRODUCT-MAP.md) — product split
