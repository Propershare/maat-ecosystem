# Change: Vault HTML Artifact Pipeline (Structured Record → JSON-LD → HTML → MCP Resource)

## Why

The lab has accumulated a large canon of Tdka Kilimanjaro / KMT scholarship (130+ markdown files in `maatlangchain/docs/canon/`, ingested into the `canon_kmt` collection in `maat_memory`) plus an ongoing stream of agent conversations, decisions, changes, and learnings recorded in gitMaat (`maat_sessions`, `maat_conversations`, `maat_decisions`, `maat_changes`, `maat_learnings`, `maat_governance_events`).

Today, those records live in two layers that don't talk to each other well:

1. **Structured truth** — gitMaat tables + `canon_kmt` vector collection. Queryable, embeddable, cite-able, but ugly to read and not shareable as a single object.
2. **Human presentation** — static markdown, the open-webui chat surface, the existing `maat-ecosystem/site/index.html` marketing page. Pretty, but disconnected from provenance, claim IDs, and source tiers.

A piece of canon scholarship like *"KMT State-Planned Economy into Modernity"* or a structured agent output like *"extract_from_graphs.py claim audit for 03/2026"* has no portable, shareable, machine-readable artifact form that:

- a human can open in a browser and read as a finished document
- an MCP-aware agent can fetch as a typed resource with stable claim IDs
- the lab can print, archive, post, or index without losing provenance
- a future agent can ground against at the **claim** level (not just document level)

We need a thin pipeline that:

1. Treats a gitMaat row (or a `canon_kmt` chunk) as the **structured record** (truth).
2. Derives a `VaultEntry` with stable IDs, claim objects, and source-tier metadata.
3. Renders that record as a **self-contained HTML artifact** (presentation).
4. Embeds a **JSON-LD** block inside the HTML so the artifact is its own contract (machine-readable).
5. Registers the artifact as a **gateway resource** that MCP-aware agents (and the existing openclaw-integration's `memory-wiki` extension) can fetch by `vault_id` and `claim_id`.

**The design law this change applies:** *HTML is the display shell, not the truth engine. Structured records stay in gitMaat. The model fills JSON, not HTML. The HTML must visibly show source tier, status, confidence, and provenance — pretty pages with no provenance are propaganda wallpaper.*

This change does not invent a new "Vault" namespace from scratch. It maps onto:

- `maat_conversations` (entries) and `canon_kmt` (canon chunks) as the source of structured truth
- `maat_governance_events` (via Tehuti Guard `POST /decision` at `:8013`) as the policy gate
- `openclaw-integration/extensions/memory-wiki` (the existing wiki compiler) as the filesystem and managed-block renderer
- the openclaw gateway (default `:18790`) as the MCP resource surface

The change is **wiring + one new Python module + one new openspec spec family**. No new database tables. No new dashboard. No new policy engine.

## What Changes

- **ADDED**: `vault-entry` capability — the `VaultEntry` data contract (id, title, author, entry_type, source_tier, status, claims, evidence, maat_score, body_text, assets, related_entries, timestamps). Derives from existing gitMaat rows; no schema change to sacred tables.
- **ADDED**: `vault-renderer` capability — the HTML shell contract. Single locked template. JSON-LD block is the machine contract; the `<article>` body is the human view. Embeds provenance visibility (source tier badge, status badge, confidence, last-reviewed timestamp, model used). Compatible with `memory-wiki` managed-block conventions so existing `wiki_lint` and `wiki_apply` flows keep working.
- **ADDED**: `vault-router` capability — three gateway methods: `vault.get(id)`, `vault.search(query)`, `vault.claim(id, claim_id)`. Every call is gated by `POST /decision` to Tehuti Guard. The agent's `maat_agents.yaml` ring drives the policy outcome.
- **ADDED**: One Python module `maatlangchain/maat_vault/` with `entry.py`, `renderer.py`, `ingest.py`, `router.py`. Pure functions, no new schema, calls existing `MaatRAG` and `MaatMemoryPostgres`.
- **ADDED**: openspec change `add-vault-html-artifact-pipeline` (this change).
- **MODIFIED**: `maat_agents.yaml` gains `vault.get`, `vault.search`, `vault.claim` entries on the `outer-ring` (full access) and `middle-ring` (read-only) agents; does **not** add a new access type, only references the existing three (`query`, `log_task`, `log_change`).
- **MODIFIED**: `openclaw-integration/extensions/memory-wiki/openclaw.plugin.json` `configSchema` gains an optional `vaultBridge` field so the wiki can index vault entries when in `bridge` mode (read-only). Optional and opt-in; default off.

## Non-Goals

- **NOT** building a new database, table, or vector collection. All persistence stays in existing `maat_conversations`, `canon_kmt`, and `maat_governance_events`.
- **NOT** building a new dashboard or new chat surface. The openclaw gateway control UI and open-webui's existing `index.html` are sufficient.
- **NOT** letting the LLM write HTML. The model only fills `VaultEntry` JSON (coarse structuring); a deterministic code layer does fine structuring (claim extraction, evidence linking, score inference) and rendering.
- **NOT** replacing markdown or open-webui rendering. The vault HTML is a **derived artifact** of a gitMaat record. If the underlying row updates, the artifact re-renders; the markdown is unaffected.
- **NOT** making pretty HTML authoritative. Every rendered page must visibly show source tier, status, model used, last-reviewed timestamp, and claim-level confidence. Pages without these badges are invalid by spec.
- **NOT** a multi-tenant redesign of gitMaat. Namespacing is `vault:{agent_id}:{entry_type}:{short_uuid}` to avoid collision across the lab's multi-agent, multi-machine footprint.
- **NOT** a new policy engine. All gates go through Tehuti Guard `POST /decision`. No new outcomes (allow/deny/escalate/require_approval/log are the 5, per `maat_policy.schema.json`).

## Impact

- **Affected specs** (new):
  - `specs/vault-entry/spec.md`
  - `specs/vault-renderer/spec.md`
  - `specs/vault-router/spec.md`
- **Affected code** (new files only — no edits to sacred modules):
  - `maatlangchain/maat_vault/__init__.py`
  - `maatlangchain/maat_vault/entry.py` — `VaultEntry` dataclass + adapters from `maat_conversations` row + `canon_kmt` chunk
  - `maatlangchain/maat_vault/renderer.py` — HTML shell + JSON-LD emitter
  - `maatlangchain/maat_vault/ingest.py` — pulls structured records, calls `MaatRAG.search_similar` for related claims
  - `maatlangchain/maat_vault/router.py` — gateway method handlers + Tehuti Guard gate
  - `maatlangchain/maat_vault/templates/vault_entry.html` — single locked Jinja2 template
- **Affected config** (small additions):
  - `maatlangchain/maat_agents.yaml` — add `vault.get/search/claim` access rows
  - `openclaw-integration/extensions/memory-wiki/openclaw.plugin.json` — add `vaultBridge` to `configSchema.properties` (optional, default off)
- **User impact**:
  - Existing agent chats can mark an entry as vault-shaped via `metadata.entry_type`; the pipeline renders an HTML page on demand.
  - Existing canon markdown files can be re-ingested as vault entries without changing their source files.
  - MCP-aware agents (Cursor, OpenCode, future Hermes-gateway tools) can fetch `vault.get` / `vault.claim` via the openclaw gateway.
  - Operators browsing the lab control UI can open the rendered HTML in a browser for any `vault_id`.
- **Breaking changes**: None. All new behavior is additive. The `metadata.entry_type` field on `maat_conversations.metadata` jsonb is opt-in; rows without it behave exactly as before.

## Maat Principles Applied

- **Truth**: Source-of-truth is the gitMaat row. The HTML is a derived artifact; the JSON-LD block is a generated mirror of the same row. The rendered page must visibly show `source_tier` and `status`. A beautiful page with no provenance is propaganda wallpaper — this spec requires the badge to be present or the render is invalid.
- **Balance**: Claim-level grounding is the addressable unit, not document level. Every claim gets a stable `claim_id`; agents cite claims, not pages. `vault.search` returns a mix of canon chunks and agent-recorded entries, ranked by vector similarity + `source_tier` weight, so a pretty AI draft can't outrank a primary canon entry.
- **Order**: One renderer, one template, one schema. The LLM fills the `VaultEntry` JSON; the code layer is the only thing that touches HTML. No CSS classes invented on the fly. The renderer's output is byte-stable for a given input (modulo timestamps) so diffs are meaningful.
- **Justice**: Every read and write is gated by Tehuti Guard with the agent's `maat_agents.yaml` ring. Every gateway call writes a `maat_governance_events` row with `correlation_id` and `source_service=vault-router`. Inner-ring agents can't fetch. Unknown agents fail closed.
- **Self-Reflection**: `maat_score` is **derived from gitMaat history**, not vibes. `provenance_score` = ratio of related rows with `source_tier` set, `truth_score` = ratio of rows that survived `review` (no `quarantine`/`escalate` outcome in `maat_governance_events`), `clarity_score` = mean cosine similarity of body chunks to canonical theme vectors. The score is traceable to actual rows.

## Architecture

```
gitMaat row                canon_kmt chunk
(maat_conversations        (pgvector collection)
 +metadata.entry_type)
        │                          │
        └──────────┬───────────────┘
                   ▼
        ┌──────────────────┐
        │ VaultEntry       │   ← entry.py: pure dataclass, no I/O
        │ (id, claims[],   │      LLM fills coarse fields; code fills fine fields
        │  evidence[],     │      (claim extraction, score inference)
        │  maat_score,     │
        │  body_text, ...) │
        └────────┬─────────┘
                 │
       ┌─────────┴──────────┐
       ▼                    ▼
┌──────────────┐    ┌────────────────┐
│ renderer.py  │    │ ingest.py      │
│ → HTML +     │    │ → search-      │
│   JSON-LD    │    │   similar via  │
│   block      │    │   MaatRAG      │
└──────┬───────┘    └───────┬────────┘
       │                    │
       ▼                    ▼
  ~/.openclaw/wiki/    maat_conversations
  main/entries/        + maat_learnings
  <vault_id>.md        (new rows for
  (memory-wiki)        related claims)

       │
       ▼
┌──────────────────────────────────┐
│ router.py (gateway methods)      │
│  vault.get(id)                   │
│  vault.search(query)             │
│  vault.claim(id, claim_id)       │
│  → POST /decision → Tehuti Guard │
│  → source_service=vault-router   │
│  → writes maat_governance_events │
└──────────────────────────────────┘
       │
       ▼
  openclaw gateway :18790
  (MCP resource surface)
```

## Design Decisions (with rationale)

1. **Reuse `maat_conversations.metadata.entry_type` instead of a new `maat_vault_entries` table.** Adding a table requires a schema version bump (sacred-tier concern per `maat-core/schemas/maat_memory.schema.json`). The existing `metadata` jsonb column is already a freeform slot. We document `entry_type ∈ {essay, graph, brief, transcript, lesson}` as a convention, not a constraint, and validate at the Python layer. If validation proves insufficient after real use, the next change escalates to a new table — and that's an explicit decision, not drift.

2. **Reuse the `memory-wiki` extension as the filesystem and managed-block renderer.** It already handles `WIKI_VAULT_DIRECTORIES`, `wiki_apply` for structured claim payloads, `.openclaw-wiki/cache/agent-digest.json` as the machine view, and `wiki_lint` for provenance checks. Building a parallel renderer is exactly the kind of fragmentation the lab's constitution warns against.

3. **JSON-LD inside HTML, not as a separate file.** Schema.org's pattern (and the take the user gave) is sound: one artifact, two seams. The same `vault_id` URL in the JSON-LD `@id` field can be dereferenced by `vault.get(id)` to return the JSON-LD block, and by `vault.get(id, format=html)` to return the rendered article. The gateway is the single source of resource dereferencing.

4. **`vault_id` is namespaced.** Format: `vault:{agent_id}:{entry_type}:{short_uuid8}`. Example: `vault:opencode_imhotep_terminal_12345:essay:7c2f9a4b`. This matches `maat_agents.yaml`'s agent-id convention (`cursor_<host>`, `opencode_<host>_<terminal>`) and prevents cross-machine collisions. The `:short_uuid8` is the first 8 hex chars of a v4 uuid; collision risk is negligible at the lab's scale.

5. **The LLM does coarse, the code does fine.** Smaller local models (gemma4:e2b, e4b) cannot reliably extract claim-level JSON from long canon docs. Practical split: the LLM fills `title`, `author`, `entry_type`, `body_text`, and an initial `claims[]` list (free-form prose claims). The code layer then (a) mints stable `claim_id`s, (b) attempts evidence linking against `maat_conversations.id` and `canon_kmt` chunk ids, (c) computes `maat_score` from gitMaat history, (d) sets `source_tier` from filename/path/agent, (e) infers `status` from `maat_governance_events` history. This is the "model in its lane" principle, applied honestly to a small-model lab.

6. **Every gateway method calls Tehuti Guard.** Even `vault.search`. Even `vault.get`. This is the only way the lab's policy surface stays the single source of permission truth. `correlation_id` flows from the gateway request into the `POST /decision` body and into the resulting `maat_governance_events` row, so a Vault call is fully traceable in gitMaat.

7. **The HTML is not the source of truth for retrieval.** `vault.search` does **not** scrape the rendered HTML. It queries `maat_conversations` + `canon_kmt` directly. The HTML is for humans and for the MCP resource surface. Retrieval stays on the structured layer. This is the "showcase layer separated from retrieval layer" principle the take articulated.

## Success Criteria

1. A `vault.get` call on a known `vault_id` returns an HTML page that opens correctly in any modern browser, with the JSON-LD block visible via `view-source` and parseable by any JSON-LD consumer.
2. A `vault.claim` call returns the specific claim object with its `evidence[]` array, sourced from gitMaat.
3. A `vault.search` call returns results where the top hit's `source_tier` is honored — a `PRIMARY_CANON` entry outranks an `AI_DRAFT` entry with higher raw cosine similarity.
4. Every gateway method writes a `maat_governance_events` row with `source_service=vault-router` and a valid `correlation_id`.
5. An inner-ring agent calling `vault.get` is denied by Tehuti Guard, and the denial is logged.
6. A pretty HTML page rendered for an AI_DRAFT entry visibly shows `source_tier=AI_DRAFT`, `status=unreviewed`, the model that produced it, and a confidence range — no exceptions.
7. The `memory-wiki` extension in `bridge` mode indexes the rendered entries; `wiki_lint` flags entries with low `provenance_score` and unresolved claims.
8. `openspec validate add-vault-html-artifact-pipeline --strict` passes.

## Related Lab Context

- **Lab root**: `/home/suspect/.n8n`
- **Sacred schemas** (do not modify): `maat-core/schemas/maat_{memory,task,policy,event,identity,tool,learning}.schema.json`
- **Existing Maat Memory**: `/home/suspect/.n8n/maatlangchain/maat_memory/` (PostgreSQL + pgvector, schema in `maatlangchain/maat_memory/schema.sql`)
- **Existing wiki renderer**: `/home/suspect/.n8n/openclaw-integration/extensions/memory-wiki/` (managed blocks, Obsidian mode, `wiki_apply` for structured claim payloads)
- **Existing policy surface**: `/home/suspect/.n8n/tehuti-guard/` (`POST /decision` on `:8013`, deterministic `explanation_id = sha256(...)`)
- **OpenSpec protocol**: `/home/suspect/.n8n/openspec/openspec/AGENTS.md` — verb-led kebab-case `change-id`, `## ADDED|MODIFIED|REMOVED Requirements` with at least one `#### Scenario:` per requirement
- **Constitution (sacred vs replaceable)**: `/mnt/data_drive/maat-ecosystem/CONSTITUTION.md` and `/home/suspect/maat-ecosystem/soul/constitution.md`
- **Two-homes audit**: `/home/suspect/.n8n/docs/MAAT-ECOSYSTEM-TWO-HOMES.md` — note that `/mnt/data_drive/maat-ecosystem/` (Python facade) and `/home/suspect/maat-ecosystem/` (Ka body) coexist intentionally
