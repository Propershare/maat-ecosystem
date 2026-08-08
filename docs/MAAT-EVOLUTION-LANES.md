# MAAT Evolution Lanes

Companion to [`docs/MAAT-IMMUNE-SYSTEM.md`](MAAT-IMMUNE-SYSTEM.md),
[`docs/MAAT-LIGHTWEIGHT-INTELLIGENCE.md`](MAAT-LIGHTWEIGHT-INTELLIGENCE.md), and
[`docs/SCOUT-ANALYST-ARCHIVIST.md`](SCOUT-ANALYST-ARCHIVIST.md). Read alongside
[`data/tehuti/ukmt-rbg-dataset/ka2_agent_system_prompt.md`](../data/tehuti/ukmt-rbg-dataset/ka2_agent_system_prompt.md).

**Rule of the lab:** evolution is permitted along the lanes named below.
Anything outside those lanes is a constitutional change and must be
proposed, benched, and promoted under governance, not touched by a running
agent.

## Why lanes exist

Without a lane map, self-improvement collapses into prompt drift, silent
schema creep, and a fine-tune that happened to match last week's vibes. The
MAAT immune system (Sentinel, Bench, Forge, Guard) needs a crisp yes/no on
"is this change allowed here?" so it can let routine improvements through
fast and hold constitutional changes to a harder bar.

## Sacred layer — do not mutate at runtime

These are the constitutional anchors. Changing any of them counts as a
constitutional amendment; it requires a named proposal, a MAATBENCH v2 run
on the full suite (`intelligence / efficiency / governance / safety /
auditability`), an operator signature, and a promotion audit row.

| Anchor | Canonical location |
| --- | --- |
| KA2 ten-step method + forbidden actions | [`ka2_agent_system_prompt.md`](../data/tehuti/ukmt-rbg-dataset/ka2_agent_system_prompt.md) |
| Maat scorecard axes, weights, pass threshold (`pass_at=40`) | [`gateway_contract.py`](../gemma4-toolshim/swarm/gateway_contract.py), [`ka2_scorecard.schema.json`](../maat-ecosystem/skeleton/schemas/ka2_scorecard.schema.json) |
| RBL halt rule (`halt_flags >= 3`) | [`gateway_contract.py`](../gemma4-toolshim/swarm/gateway_contract.py) |
| Archivist record schema v1 + sibling schemas | [`maat-ecosystem/skeleton/schemas/`](../maat-ecosystem/skeleton/schemas/) |
| Tehuti Guard decision contract and promotion rules | [`tehuti-guard/`](../tehuti-guard/), Guard `POST /decision` |
| Three-ring boundaries | [`.cursorrules`](../.cursorrules), guard policies |
| Sacred file paths (secrets, identity, constitution) | lab `.env`, `SOUL.md`, `IDENTITY.md` |

If a Forge candidate wants to change any of the above, Forge must mark the
candidate `constitutional=true`, and Guard must hold it for human review —
no auto-promotion, no LoRA workaround.

## Replaceable lanes — evolution is allowed here

Each lane below has a shape, an allowed mutation, and a required gate. A
candidate that does not declare its lane is rejected by Forge.

### Lane 1 — Retrieval packs

- **Shape:** a folder or manifest describing a corpus (e.g.
  `data/retrieval_packs/fl-trust-law/`), its provenance, and the gateways
  allowed to use it.
- **Allowed mutations:** add pack, retire pack, re-rank within pack, bump
  pack version, change embedder or chunker inside the pack.
- **Gate:** MAATBENCH `models` suite on the gateways that consume the pack
  must not regress on intelligence or governance axes. Provenance row must
  exist.

### Lane 2 — Router tables and keyword weights

- **Shape:** the data in [`expert_config.py`](../gemma4-toolshim/swarm/expert_config.py)
  (`keywords`, `tools`, `description`) and any router config files.
- **Allowed mutations:** reorder keywords, add or remove keywords, adjust
  weights, add a new expert entry whose `research_type` aligns with one of
  [`RESEARCH_TYPES`](../gemma4-toolshim/swarm/gateway_contract.py).
- **Gate:** bench-gated A/B on saved session records (same inputs, scored
  by archivist record quality). No prompt text changes.

### Lane 3 — Prompt envelopes within the KA2 wrapper

- **Shape:** per-expert system prompt body. The KA2 method prompt itself is
  sacred; the envelope that introduces an expert to it is not.
- **Allowed mutations:** wording, tone, explicit examples, tightening
  existing forbidden-action reminders.
- **Forbidden mutations:** relaxing any forbidden action, lowering the
  scorecard floor, removing method naming, adding self-grading logic (the
  validator does that).
- **Gate:** diff goes to Forge as a versioned data file; MAATBENCH must
  pass before promotion; Guard signs the promotion row.

### Lane 4 — Guard rule parameters

- **Shape:** numeric parameters and allowlists in Guard policy, e.g.
  "max file size for a retrieval chunk", "allowed tool list for the scout
  gateway". **Not** the decision schema, not the three-ring boundaries.
- **Allowed mutations:** tighten a parameter, add an allowed tool to a
  specific gateway, add a domain tag to an allowlist.
- **Gate:** Guard runs the proposed rules over
  [`guard_cases/*.json`](../guard_cases/) plus the lived-truths policy
  fixtures; no new denies of previously allowed cases without a named
  reason.

### Lane 5 — Small local LoRAs for non-core experts

- **Shape:** one LoRA adapter per non-core expert (e.g. scout, archivist
  summariser), trained via [`gemma4-toolshim/finetune.py`](../gemma4-toolshim/finetune.py).
- **Allowed mutations:** produce a candidate adapter, promote it to an
  Ollama tag, update the `model` id in that expert's `expert_config` entry
  via a Guard-mediated patch.
- **Dataset constraints (sacred in this lane):** every training row comes
  from a real captured turn where the archivist record validated, the
  scorecard passed, there were zero RBL flags, and the Archivist tag policy
  approved the row. No scraped or synthesised rows.
- **Gate:** the new adapter must beat the current model id on the relevant
  MAATBENCH slice by the configured margin. Losers are deleted; winners
  write a promotion row with inputs hash, dataset hash, base model, adapter
  config, and bench delta.

### Lane 6 — MAATBENCH fixtures derived from lived truths

- **Shape:** JSON files under [`maat-ecosystem/maatbench/suites/`](../maat-ecosystem/maatbench/suites/).
- **Allowed mutations:** add a fixture derived from a real session record;
  mark an obsolete fixture deprecated with a reason; version a suite.
- **Forbidden mutations:** removing a failing fixture without replacing it,
  or editing a fixture to make a failing candidate pass.
- **Gate:** Sentinel signs that the fixture corresponds to a real
  correlation id; Guard denies silent deletions.

## How a change travels

```
        Lane 1..6 candidate
               │
               ▼
        Forge (proposes)
               │
        Sandbox gateway run
               │
               ▼
        MAATBENCH v2 (axes)
               │
        pass?  no ─► log learning, discard
               │ yes
               ▼
        Tehuti Guard /decision
               │
        allow? no ─► log denial, discard
               │ yes
               ▼
        Registry update + audit row
               │
               ▼
        Router picks up next turn
```

Every step writes a structured record — no prose-only decisions. The
Archivist record on the sandbox turn is the evidence body; the bench score
is the verdict; the Guard row is the seal; the registry update is the
effect.

## What this document is not

- Not a changelog. Changes to these lanes land as promotion rows in
  gitMaat plus file diffs, not English paragraphs.
- Not a schema reference. Schemas live in
  [`maat-ecosystem/skeleton/schemas/`](../maat-ecosystem/skeleton/schemas/).
- Not a policy file. Policies live in
  [`tehuti-guard/`](../tehuti-guard/) and in Guard rule parameters.

This is the map. The map names the roads. Drive in your lane.
