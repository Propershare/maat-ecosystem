# Spec: vault-entry

## ADDED Requirements

### Requirement: VaultEntry Data Contract
The `VaultEntry` dataclass SHALL represent a single structured record that is the **single source of truth** for any vault-shaped artifact. It SHALL be derivable from an existing `maat_conversations` row (with `metadata.entry_type` set) or a `canon_kmt` chunk, and SHALL be serializable to a JSON object that round-trips losslessly.

#### Scenario: VaultEntry built from a conversation row
- **WHEN** `VaultEntry.from_conversation_row(row)` is called with a `maat_conversations` row whose `metadata` jsonb contains `"entry_type": "essay"`
- **THEN** the returned `VaultEntry` has all required fields populated from the row
- **AND** `vault_id` is namespaced as `vault:{agent_id}:{entry_type}:{short_uuid8}`
- **AND** `entry_type` is `"essay"`
- **AND** `source_tier` is inferred from `metadata.source_tier` if present, else defaults to `COMMENTARY`
- **AND** `status` is inferred from `metadata.status` if present, else defaults to `"draft"`

#### Scenario: VaultEntry built from a canon_kmt chunk
- **WHEN** `VaultEntry.from_canon_chunk(chunk, metadata)` is called with a `canon_kmt` retrieval result and the source markdown's path
- **THEN** the returned `VaultEntry` has `entry_type="essay"` and `source_tier="PRIMARY_CANON"` if the path begins with `docs/canon/`
- **AND** `author` is parsed from the markdown frontmatter if present, else defaults to the lab default (`"Tdka Kilimanjaro"` for canon paths, `agent_id` for agent-recorded paths)
- **AND** `model_used` is `None` (canon chunks are human-authored)

#### Scenario: VaultEntry rejects rows without entry_type
- **WHEN** `from_conversation_row(row)` is called with a row whose `metadata` jsonb has no `entry_type` key
- **THEN** the method raises `VaultEntryShapeError` with a message that includes the row's `id` and the missing field name
- **AND** the error message names the field and suggests `Set metadata.entry_type to one of: essay, graph, brief, transcript, lesson`

#### Scenario: VaultEntry round-trips losslessly through to_dict
- **WHEN** `entry.to_dict()` is called and the result is passed back through `VaultEntry.from_dict(dict)`
- **THEN** the new `VaultEntry` is equal to the original (excluding ephemeral fields like `updated_at` which the round-trip is allowed to preserve verbatim)
- **AND** the dict is JSON-serializable (no `datetime`, no `Decimal`, no custom classes that fail `json.dumps`)

### Requirement: vault_id Namespace
Every `VaultEntry` SHALL have a `vault_id` matching the pattern `^vault:[a-z0-9_]+:(essay|graph|brief|transcript|lesson):[0-9a-f]{8}$`. The `vault_id` SHALL be the canonical addressable handle used by every gateway method, every JSON-LD `@id`, and every wiki page filename.

#### Scenario: vault_id is constructed from agent_id, entry_type, and a short uuid
- **WHEN** a `VaultEntry` is constructed
- **THEN** `vault_id` is `f"vault:{agent_id}:{entry_type}:{uuid4().hex[:8]}"`
- **AND** the short uuid segment SHALL be exactly 8 lowercase hex characters
- **AND** collision probability across the lab's multi-agent, multi-machine footprint is negligible (24 bits of entropy per `vault_id` per `(agent_id, entry_type)` pair)

#### Scenario: vault_id validation rejects malformed values
- **WHEN** a `VaultEntry` is constructed with a `vault_id` not matching the documented pattern
- **THEN** `entry.validate()` raises `VaultEntryValidationError` with the message `vault_id <value> does not match pattern ^vault:[a-z0-9_]+:(essay|graph|brief|transcript|lesson):[0-9a-f]{8}$`

#### Scenario: vault_id is the same across the rendered HTML, JSON-LD block, and wiki page filename
- **WHEN** the same `VaultEntry` is rendered to HTML and emitted to JSON-LD
- **THEN** the HTML's `<meta name="vault-id">`, the `<article data-vault-id="...">`, and the JSON-LD `@id` all carry the same `vault_id` value
- **AND** the wiki page filename is `<vault_root>/entries/<vault_id>.md`

### Requirement: Claim-Level Addressability
Every `VaultEntry` SHALL have a `claims: list[Claim]` field where each `Claim` has a stable `claim_id` of the form `claim-NNN` (zero-padded 3 digits) unique within the entry. The `claim_id` SHALL be the addressable unit for the `vault.claim(id, claim_id)` gateway method and the fragment identifier in the rendered HTML.

#### Scenario: Claim IDs are stable and unique within an entry
- **WHEN** `VaultEntry.validate()` is called
- **THEN** every `Claim.claim_id` matches `^claim-[0-9]{3}$`
- **AND** no two claims in the same entry share the same `claim_id`
- **AND** claims are stored in the order they appear in `body_text` (left-to-right, top-to-bottom), so the rendered HTML's `<li id="claim-001">` matches the order in `claims[0]`

#### Scenario: Claim fragment identifier in the rendered HTML
- **WHEN** the entry is rendered
- **THEN** each claim appears in the HTML as `<li id="claim-NNN" data-confidence="0.XN">` with the claim text as the linkable text
- **AND** the JSON-LD `claims[N].id` field matches the `claim-NNN` value
- **AND** `vault.claim(vault_id, "claim-001")` returns the same `Claim` object

#### Scenario: Claim confidence is in [0.0, 1.0]
- **WHEN** `VaultEntry.validate()` is called
- **THEN** every `Claim.confidence` is a float in `[0.0, 1.0]`
- **AND** out-of-range confidence values raise `VaultEntryValidationError` citing the offending claim id and the value

#### Scenario: Claim with no evidence still validates
- **WHEN** a `Claim` has `evidence_claim_ids = []` (no supporting evidence in the same entry)
- **THEN** the claim still validates
- **AND** its `confidence` defaults to `0.5` if not explicitly set
- **AND** the rendered HTML visibly marks the claim as `ungrounded` (e.g. `<span class="ungrounded">ungrounded</span>`) so a human reader can see the claim has no internal evidence chain

### Requirement: Evidence References
Every `VaultEntry` SHALL have an `evidence: list[EvidenceRef]` field. Each `EvidenceRef.ref_id` SHALL be a stable id from gitMaat (e.g. `maat_conversations.id` uuid, `canon_kmt` chunk id, or a `vault:...#claim-NNN` claim reference).

#### Scenario: EvidenceRef with ref_type=vault_claim references a related entry
- **WHEN** an `EvidenceRef` has `ref_type="vault_claim"`
- **THEN** its `ref_id` matches `^vault:[a-z0-9_]+:(essay|graph|brief|transcript|lesson):[0-9a-f]{8}#claim-[0-9]{3}$`
- **AND** the parent `vault_id` portion of the ref_id is in the parent `VaultEntry.related_entries` list
- **AND** `VaultEntry.validate()` raises `VaultEntryValidationError` if the parent `vault_id` is not in `related_entries`

#### Scenario: EvidenceRef with ref_type=conversation references a maat_conversations row
- **WHEN** an `EvidenceRef` has `ref_type="conversation"`
- **THEN** its `ref_id` is a valid uuid4 matching an existing row in `maat_conversations.id`
- **AND** `VaultEntry.validate()` does not require a DB lookup (validation is local); runtime fetch errors are surfaced by the router, not the validator

#### Scenario: EvidenceRef with ref_type=canon_chunk references a canon_kmt chunk
- **WHEN** an `EvidenceRef` has `ref_type="canon_chunk"`
- **THEN** its `ref_id` is a stable chunk id (the chunk's pgvector row id, exposed by the existing retrieval layer)
- **AND** the evidence ref carries a `note` field describing the relevance (set by the LLM, ≤ 200 chars)

### Requirement: maat_score Derivation
Every `VaultEntry` SHALL have a `maat_score: MaatScore` field. The score SHALL be **derived from gitMaat history** (not assigned by the LLM), and SHALL include a `derived_from: list[str]` field listing the `maat_governance_events.id` uuids (or other row ids) that informed each sub-score.

#### Scenario: provenance_score is the ratio of evidence-supported claims
- **WHEN** `maat_score.provenance` is computed
- **THEN** `provenance = min(1.0, len(evidence) / max(len(claims), 1))`
- **AND** `derived_from` includes the ids of the evidence rows that were counted

#### Scenario: truth_score reflects prior maat_governance_events outcomes
- **WHEN** `maat_score.truth` is computed
- **THEN** the implementation queries `maat_governance_events` for any prior decisions touching the entry's source ids (conversation id, canon chunk id)
- **AND** if all prior decisions are `allow` or `log`, `truth = 0.8`
- **AND** if any prior decision is `escalate` or `quarantine`, `truth = 0.4`
- **AND** if there are no prior decisions, `truth = 0.5` (neutral default)
- **AND** `derived_from` includes the relevant `maat_governance_events.id` uuids

#### Scenario: clarity_score is the mean cosine similarity of body paragraphs to the primary claim
- **WHEN** `maat_score.clarity` is computed
- **THEN** the implementation embeds each `body_text` paragraph and the primary (first) claim, then computes `clarity = mean(cosine_similarity(p_i, claim_embedding) for p_i in paragraphs)`
- **AND** `clarity` is in `[0.0, 1.0]`
- **AND** `derived_from` includes the embedding model identifier (e.g. `nomic-embed-text`) so the score is reproducible

#### Scenario: balance_score is left to the operator
- **WHEN** `maat_score.balance` is read but the entry has no operator-assigned balance
- **THEN** `balance = 0.5` (neutral default)
- **AND** `derived_from` is empty
- **AND** the field exists in the contract so a future operator-tooling change can populate it without breaking the schema

#### Scenario: maat_score validation enforces range
- **WHEN** `VaultEntry.validate()` is called
- **THEN** every sub-score (`truth`, `balance`, `clarity`, `provenance`) is a float in `[0.0, 1.0]`
- **AND** out-of-range values raise `VaultEntryValidationError`

### Requirement: Source-Tier Visibility
Every `VaultEntry` SHALL have a `source_tier` field with one of four values, and the field SHALL be visible in the rendered HTML, the JSON-LD block, and the gateway response.

#### Scenario: source_tier is one of four documented values
- **WHEN** a `VaultEntry` is constructed
- **THEN** `source_tier` is one of `"PRIMARY_CANON"`, `"SECONDARY"`, `"COMMENTARY"`, `"AI_DRAFT"`
- **AND** `VaultEntry.validate()` raises `VaultEntryValidationError` for any other value

#### Scenario: source_tier is rendered as a visible badge
- **WHEN** the entry is rendered
- **THEN** the HTML `<header>` contains a `<span class="source-tier" data-tier="PRIMARY_CANON">PRIMARY_CANON</span>` (or the appropriate tier value)
- **AND** the JSON-LD `sourceTier` field carries the same value
- **AND** the badge is visible above the fold in a default browser viewport (no scrolling required to see it)

#### Scenario: source_tier ranking is honored in vault.search
- **WHEN** `vault.search(query)` is called
- **THEN** the result list is re-ranked so `PRIMARY_CANON` entries outrank `AI_DRAFT` entries even at lower raw cosine similarity
- **AND** the re-ranking weights are `PRIMARY_CANON=1.0`, `SECONDARY=0.8`, `COMMENTARY=0.6`, `AI_DRAFT=0.3` applied multiplicatively to the cosine similarity

### Requirement: Status Field
Every `VaultEntry` SHALL have a `status` field with one of four values: `"draft"`, `"reviewed"`, `"canonical"`, `"disputed"`. Status transitions SHALL be append-only — a `canonical` entry never silently reverts to `draft`; the transition is logged in `maat_learnings` with the prior and new status.

#### Scenario: Status transitions are append-only
- **WHEN** a status transition is recorded (e.g. `draft` → `reviewed`)
- **THEN** a `maat_learnings` row is written with `topic="vault.status_transition"`, `insight=f"{vault_id}: {old} -> {new}"`, `source="vault-router"`, `confidence=1.0`
- **AND** the entry's `updated_at` is updated
- **AND** the JSON-LD `vaultStatus` field reflects the new value

#### Scenario: Disputed entries are visibly marked
- **WHEN** an entry has `status="disputed"`
- **THEN** the rendered HTML shows a red `disputed` badge in the header
- **AND** the JSON-LD `vaultStatus` is `"disputed"`
- **AND** `vault.search` results for `disputed` entries include the dispute count from `maat_learnings` in the response

### Requirement: JSON-LD Emission
Every `VaultEntry` SHALL emit a JSON-LD block via `to_json_ld()` matching `schema.org/ScholarlyArticle` with the lab's custom `maat`, `claims`, `sourceTier`, and `vaultStatus` fields. The block SHALL be valid JSON-LD 1.1 and parseable by any JSON-LD consumer.

#### Scenario: JSON-LD block has the documented shape
- **WHEN** `entry.to_json_ld()` is called
- **THEN** the returned dict has:
  - `"@context": "https://schema.org"`
  - `"@type": "ScholarlyArticle"`
  - `"@id": "vault:{...}"`
  - `"identifier": "<vault_id>"`
  - `"name": "<title>"`
  - `"author": {"@type": "Person", "name": "<author>"}`
  - `"dateCreated": "<created_at ISO 8601>"`
  - `"dateModified": "<updated_at ISO 8601>"`
  - `"sourceTier": "PRIMARY_CANON|SECONDARY|COMMENTARY|AI_DRAFT"`
  - `"vaultStatus": "draft|reviewed|canonical|disputed"`
  - `"maat": {"truth": ..., "balance": ..., "clarity": ..., "provenance": ...}`
  - `"claims": [{"id": "claim-NNN", "text": "...", "evidence": [...], "confidence": ...}, ...]`
  - `"isBasedOn": [...]` (a list of `EvidenceRef` objects serialized as schema.org `CreativeWork` references when applicable)
  - `"url": "vault://<vault_id>"` (the dereferenceable resource handle for the gateway)

#### Scenario: JSON-LD round-trips through json.dumps
- **WHEN** `json.dumps(entry.to_json_ld(), indent=2)` is called
- **THEN** the result is valid JSON
- **AND** every field documented in the previous scenario is present
- **AND** the result is < 100 KB for a typical 20-claim entry (no embedding vectors are serialized into the JSON-LD block — those stay in gitMaat)

#### Scenario: JSON-LD claims reference matches rendered HTML fragment ids
- **WHEN** the same entry is rendered to HTML and emitted to JSON-LD
- **THEN** `JSON-LD.claims[N].id == HTML <li id="claim-NNN">` for every N
- **AND** an MCP consumer reading the JSON-LD can use `claim.id` as a fragment identifier to dereference via `vault.claim(vault_id, claim_id)`
