# Tasks: Vault HTML Artifact Pipeline

## 1. Proposal and Specification
- [ ] 1.1 Create `proposal.md` with Maat-aligned rationale and architecture
- [ ] 1.2 Create `specs/vault-entry/spec.md` (data contract)
- [ ] 1.3 Create `specs/vault-renderer/spec.md` (HTML + JSON-LD contract)
- [ ] 1.4 Create `specs/vault-router/spec.md` (gateway methods + policy gate)
- [ ] 1.5 Run `openspec validate add-vault-html-artifact-pipeline --strict` and resolve issues

## 2. Scaffold the Python Module
- [ ] 2.1 Create `maatlangchain/maat_vault/__init__.py` (public exports: `VaultEntry`, `render_entry`, `ingest_from_conversation`, `ingest_from_canon_chunk`, `router_get`, `router_search`, `router_claim`)
- [ ] 2.2 Create `maatlangchain/maat_vault/entry.py` — `VaultEntry` dataclass, `from_conversation_row(row)`, `from_canon_chunk(chunk, metadata)`, `to_dict()`, `to_json_ld()`; **no I/O**, no model calls in this file
- [ ] 2.3 Add `maat_vault/` to `maatlangchain/maat_memory/` Python path conventions (or document the import path in module docstring)

## 3. Implement `entry.py` — VaultEntry Data Contract
- [ ] 3.1 Define the `VaultEntry` dataclass with all required fields per `specs/vault-entry/spec.md`:
  - `vault_id: str` (pattern `^vault:[a-z0-9_]+:(essay|graph|brief|transcript|lesson):[0-9a-f]{8}$`)
  - `title: str`
  - `author: str`
  - `entry_type: Literal["essay","graph","brief","transcript","lesson"]`
  - `source_tier: Literal["PRIMARY_CANON","SECONDARY","COMMENTARY","AI_DRAFT"]`
  - `status: Literal["draft","reviewed","canonical","disputed"]`
  - `claims: list[Claim]`
  - `evidence: list[EvidenceRef]`
  - `maat_score: MaatScore`
  - `body_text: str`
  - `assets: list[AssetRef]`
  - `related_entries: list[str]` (other `vault_id`s)
  - `created_at: str` (ISO 8601)
  - `updated_at: str` (ISO 8601)
  - `model_used: str | None` (e.g. `gemma4:e4b`, `claude-sonnet-4-6`)
  - `agent_id: str`
  - `device_id: str | None`
- [ ] 3.2 Define nested `Claim` dataclass: `claim_id`, `text`, `evidence_claim_ids: list[str]`, `confidence: float ∈ [0.0,1.0]`, `status: Literal["canonical","proposed","disputed"]`
- [ ] 3.3 Define nested `EvidenceRef` dataclass: `ref_type: Literal["conversation","canon_chunk","graph","external_url","vault_claim"]`, `ref_id: str`, `note: str | None`
- [ ] 3.4 Define nested `MaatScore` dataclass: `truth: float`, `balance: float`, `clarity: float`, `provenance: float`, `derived_from: list[str]` (governance event ids that informed the score)
- [ ] 3.5 Define nested `AssetRef` dataclass: `kind: Literal["image","audio","video","graph","pdf"]`, `path: str`, `caption: str | None`
- [ ] 3.6 Implement `from_conversation_row(row: dict) -> VaultEntry` — reads `maat_conversations` row jsonb; requires `metadata.entry_type` to be set or raises `VaultEntryShapeError` with a clear message
- [ ] 3.7 Implement `from_canon_chunk(chunk: dict, metadata: dict) -> VaultEntry` — reads a `canon_kmt` retrieval result + the source markdown's frontmatter / path-derived `source_tier`
- [ ] 3.8 Implement `to_dict()` returning a plain dict suitable for JSON serialization
- [ ] 3.9 Implement `to_json_ld()` returning a dict matching `schema.org/ScholarlyArticle` + custom `maat` and `claims` fields per `specs/vault-entry/spec.md` Requirement: JSON-LD Emission
- [ ] 3.10 Add `validate()` method on `VaultEntry` that raises `VaultEntryValidationError` on:
  - missing required fields
  - `vault_id` not matching the documented pattern
  - `confidence` out of range
  - `maat_score.*` out of range
  - any `claim.claim_id` colliding with another claim in the same entry
  - any `evidence[].ref_id` referencing a `vault_claim` whose `vault_id` is not in `related_entries`
- [ ] 3.11 No network calls, no model calls, no DB calls in `entry.py`. Pure data layer.

## 4. Implement `renderer.py` — HTML + JSON-LD Shell
- [ ] 4.1 Create `maatlangchain/maat_vault/templates/vault_entry.html` (Jinja2) with the locked shell per `specs/vault-renderer/spec.md`:
  - `<!doctype html>` + `<html lang="en">` + `<head>` block with `<meta charset>`, `<meta name="vault-id">`, `<meta name="source-tier">`, `<meta name="status">`, `<title>{{ title }}</title>`
  - `<script type="application/ld+json">{{ json_ld | tojson(indent=2) }}</script>` in `<head>`
  - `<body>` with `<article data-vault-id="...">` containing fixed sections: `<header>` (title, author, source-tier badge, status badge, model-used chip, last-updated timestamp), `<section class="claims">` (numbered claim list with `id="claim-..."` anchors and per-claim confidence), `<section class="evidence">` (provenance list), `<section class="body">` (cleaned `body_text`), `<section class="related">` (linked `vault_id`s)
  - Visible provenance footer: source tier, status, model used, last-reviewed timestamp, claim count
  - One CSS block, no external stylesheets, no JavaScript (deliberate: portable, printable, sandbox-safe)
- [ ] 4.2 Implement `render_entry(entry: VaultEntry) -> str` — calls `entry.validate()`, then Jinja2 render of the template, returns the rendered HTML string
- [ ] 4.3 Implement `write_entry_to_wiki(entry, vault_root: Path) -> Path` — writes the rendered HTML into `<vault_root>/entries/<vault_id>.md` with a `<!-- vault:html:start -->` / `<!-- vault:html:end -->` managed block wrapper so the existing `memory-wiki` lint pass treats the page as wiki-owned
- [ ] 4.4 Determinism: the rendered HTML for a given `VaultEntry` MUST be byte-identical across calls (modulo the `last-updated` timestamp which is the only allowed variance). Add a test fixture that renders a fixed entry twice and asserts equality.
- [ ] 4.5 No model calls in `renderer.py`. The renderer is a pure function of the `VaultEntry` input.

## 5. Implement `ingest.py` — Pull Structured Records
- [ ] 5.1 Implement `ingest_from_conversation(conversation_id: str, agent_id: str) -> VaultEntry`:
  - calls `MaatMemoryPostgres.search_conversations(limit=1, ...)` filtered by `id` (or a direct `SELECT` helper)
  - requires `metadata.entry_type` to be set; otherwise raises `NotVaultShapedError`
  - calls `_fill_claims_and_evidence(entry)` (private helper, see 5.4)
  - calls `entry.validate()`
  - returns the populated entry
- [ ] 5.2 Implement `ingest_from_canon_chunk(chunk_id: str, source_path: str) -> VaultEntry`:
  - calls `MaatRAG.search_similar` (or a direct retrieval helper) to get the chunk
  - infers `source_tier` from path (`docs/canon/...` → `PRIMARY_CANON`, `docs/RBG_Library/...` → `SECONDARY`, agent-recorded → `COMMENTARY`, LLM-generated with no source → `AI_DRAFT`)
  - calls `_fill_claims_and_evidence(entry)` and validates
- [ ] 5.3 Implement `ingest_from_query(query: str, top_k: int = 5) -> list[VaultEntry]` — vector search via `MaatRAG.search_similar`, ingest each hit, return list
- [ ] 5.4 Implement `_fill_claims_and_evidence(entry: VaultEntry) -> None` (private):
  - if `entry.claims` is empty: split `body_text` into paragraphs, mint `claim-001..claim-NNN` ids, set initial `confidence=0.5`
  - for each claim, run a vector search against `maat_conversations` + `canon_kmt` for supporting chunks; if any chunk has cosine similarity > 0.78, attach it as an `evidence[]` entry with `ref_type=canon_chunk` and the chunk id
  - compute `maat_score.provenance` = `len(evidence) / max(len(claims), 1)` clamped to `[0.0, 1.0]`
  - query `maat_governance_events` for any prior decisions touching this entry's source ids; if all prior decisions were `allow`/`log`, set `truth_score=0.8`; if any were `escalate`/`quarantine`, set `truth_score=0.4`; record the relevant `governance_event_id`s in `maat_score.derived_from`
  - compute `maat_score.clarity` = mean cosine similarity of body paragraphs to the entry's primary claim embedding (rough but real)
- [ ] 5.5 Cache: `ingest.py` MUST NOT call the embedding model on every call. Use the existing `MaatRAG` cache + a simple in-process LRU keyed on `(source_id, source_version)` to avoid re-embedding unchanged rows.

## 6. Implement `router.py` — Gateway Methods + Policy Gate
- [ ] 6.1 Implement `gateway_method_names() -> list[str]` returning `["vault.get", "vault.search", "vault.claim"]`
- [ ] 6.2 Implement a single private `_gate(agent_id: str, action: str, resource: str, correlation_id: str) -> dict` that calls `POST http://127.0.0.1:8013/decision` with the Tehuti Guard envelope, including:
  - `actor.id = agent_id`
  - `actor.role = "agent"`
  - `action.kind = action` (one of `read`, `execute`)
  - `action.resource = resource` (e.g. `vault:essay:7c2f9a4b` or `vault:essay:7c2f9a4b#claim-001`)
  - `action.risk = "low"` for `get`/`claim`, `"medium"` for `search`
  - `correlation_id` echoed in header `X-Correlation-ID`
  - returns the Guard response dict verbatim; if Guard is unreachable, returns `{"decision": "review", "reason": "guard_unreachable"}` (matching Tehuti Guard's existing `sentinel_unreachable_review` semantics)
- [ ] 6.3 Implement `router_get(vault_id: str, agent_id: str, correlation_id: str | None = None) -> dict`:
  - calls `_gate(agent_id, "read", vault_id, correlation_id)`
  - if decision ≠ `allow`: returns `{"error": "denied", "decision": <Guard response>}`
  - else: loads the `VaultEntry` (from cache or by re-ingesting), renders to HTML, returns `{"vault_id": ..., "html": <rendered>, "json_ld": entry.to_json_ld()}`
  - writes a `maat_governance_events` row via `MaatMemoryPostgres.log_governance_event` with `record_type="vault.get"`, `source_service="vault-router"`, `correlation_id=<cid>`, `payload={"vault_id": ..., "agent_id": ...}`
- [ ] 6.4 Implement `router_search(query: str, agent_id: str, top_k: int = 5, correlation_id: str | None = None) -> list[dict]`:
  - calls `_gate(agent_id, "execute", "vault:search", correlation_id)`
  - if decision ≠ `allow`: returns `[{"error": "denied", "decision": <Guard response>}]`
  - else: `ingest_from_query(query, top_k)`; re-rank results so that `source_tier=PRIMARY_CANON` ranks above `AI_DRAFT` even at lower cosine similarity (weight: `PRIMARY_CANON=1.0`, `SECONDARY=0.8`, `COMMENTARY=0.6`, `AI_DRAFT=0.3`); return `[{vault_id, title, source_tier, status, similarity, claim_count, maat_score}]` (no full HTML in search results)
  - writes a `maat_governance_events` row
- [ ] 6.5 Implement `router_claim(vault_id: str, claim_id: str, agent_id: str, correlation_id: str | None = None) -> dict`:
  - resource = `f"{vault_id}#{claim_id}"`
  - calls `_gate(agent_id, "read", resource, correlation_id)`
  - if decision ≠ `allow`: returns `{"error": "denied", "decision": <Guard response>}`
  - else: returns the specific `Claim` object plus its full `evidence[]` array, plus the parent entry's `source_tier` and `status`
  - writes a `maat_governance_events` row
- [ ] 6.6 Every method accepts a `correlation_id: str | None`; if `None`, the router generates a uuid4 and uses it for both the Guard call and the governance event row.

## 7. Wire to OpenClaw Gateway
- [ ] 7.1 Add a new file `openclaw-integration/extensions/vault-router/openclaw.plugin.json` (or extend an existing extension's `commandAliases` if cleaner):
  - `id: "vault-router"`
  - `kind: "tool"`
  - `configSchema` declares optional `guardUrl` (default `http://127.0.0.1:8013`) and `vaultRoot` (default `~/.openclaw/wiki/main/entries`)
  - `commandAliases`: `{ "name": "vault" }`
- [ ] 7.2 Add a thin `index.ts` (or `index.py` if the gateway accepts Python handlers) that calls into `maat_vault/router.py` and exposes the three gateway methods
- [ ] 7.3 Verify the gateway discovery endpoint (`GET :18790/manifest` or `:8010/manifest` per the lab's discovery split) lists `vault-router` after a gateway restart

## 8. Memory-Wiki Bridge (Optional, opt-in)
- [ ] 8.1 Add `vaultBridge` to `openclaw-integration/extensions/memory-wiki/openclaw.plugin.json` `configSchema.properties`:
  - `vaultBridge.enabled: bool` (default `false`)
  - `vaultBridge.indexVaultEntries: bool` (default `false`)
  - `vaultBridge.followVaultEvents: bool` (default `false`, watches `maat_governance_events` for new `vault.*` rows)
- [ ] 8.2 When `vaultBridge.enabled` is true and the wiki is in `bridge` mode, the wiki's existing `wiki_apply` flow learns to ingest `<vault_root>/entries/<vault_id>.md` and produce a `WikiPage` with structured `claims` from the JSON-LD block
- [ ] 8.3 Do **not** enable by default. Operators opt in per environment.

## 9. Update `maat_agents.yaml` (read-only declarations)
- [ ] 9.1 For each existing agent (`tehuti`, `gemma4-rag-expert`, `gemma4-code-expert`, `gemma4-ops-expert`, `sentinel`, `n8n-workflows`):
  - add a `vault` sub-key with `get`, `search`, `claim` access values matching the agent's ring (e.g. `outer-ring` agents get all three; `middle-ring` agents get `get`+`search`+`claim`; `inner-ring` agents get none)
  - reference the existing `query` / `log_task` / `log_change` access types; **do not** invent new access types
- [ ] 9.2 Update the comment block at the top of `maat_agents.yaml` to document the new `vault.*` access rows

## 10. Tests
- [ ] 10.1 Unit test `entry.py`: `from_conversation_row` rejects rows without `metadata.entry_type`; `validate()` catches each documented failure mode
- [ ] 10.2 Unit test `renderer.py`: same input → byte-identical output (modulo timestamp); rendered HTML parses as valid HTML5; JSON-LD block parses as valid JSON
- [ ] 10.3 Unit test `ingest.py`: provenance score is `0.0` for entries with no evidence, `1.0` for entries where every claim has an evidence ref; `truth_score` reflects `maat_governance_events` history
- [ ] 10.4 Unit test `router.py` with a mocked Tehuti Guard:
  - inner-ring agent → `denied`
  - outer-ring agent → `allow` + governance event row written with `source_service="vault-router"`
  - Guard unreachable → `review` decision returned
  - `correlation_id` is echoed in both the Guard request and the governance event row
- [ ] 10.5 Integration test (requires live services): `vault.search("KMT state formation")` returns canon entries ranked above AI drafts; `vault.get(<known id>)` returns HTML that opens in a headless browser without errors
- [ ] 10.6 Run `openspec validate add-vault-html-artifact-pipeline --strict` and confirm clean

## 11. Documentation
- [ ] 11.1 Add `maatlangchain/maat_vault/README.md` with: module overview, public API, the "model in its lane" rule, the policy gate contract, an example end-to-end flow
- [ ] 11.2 Add an entry to `/home/suspect/.n8n/maatlangchain/maat_agents.yaml` header comment referencing `maat_vault/` as the source of truth for vault-shaped entries
- [ ] 11.3 Add a "Vault HTML Artifacts" section to `/home/suspect/.n8n/docs/MAAT-LAB-CONTROL-PLANE.md` (or the equivalent operator doc) so operators know where rendered pages live and how the gateway methods map to MCP resources
- [ ] 11.4 Do **not** write marketing prose. Documentation follows the lab's existing terse style.

## 12. Rollout Gate
- [ ] 12.1 All tasks 1–11 complete and `openspec validate` clean
- [ ] 12.2 At least one real canon entry (e.g. `kmt_state_evolution.md`) successfully rendered end-to-end
- [ ] 12.3 At least one real agent-recorded entry (a `maat_conversations` row with `metadata.entry_type`) successfully rendered end-to-end
- [ ] 12.4 `maat doctor` (from `maat-control-plane/`) reports no new failures
- [ ] 12.5 Move `add-vault-html-artifact-pipeline` from `changes/` to `changes/archive/YYYY-MM-DD-add-vault-html-artifact-pipeline/` per openspec Stage 3
- [ ] 12.6 Run `openspec archive add-vault-html-artifact-pipeline --yes` and `openspec validate --strict` to confirm
