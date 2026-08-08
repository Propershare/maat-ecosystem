# Spec: vault-router

## ADDED Requirements

### Requirement: Three Gateway Methods
The vault-router SHALL expose exactly three gateway methods: `vault.get(vault_id)`, `vault.search(query)`, `vault.claim(vault_id, claim_id)`. No other methods are part of this spec. Future methods require a new openspec change.

#### Scenario: Method names are stable strings
- **WHEN** the gateway manifest is queried (`GET :18790/manifest` or `:8010/manifest` per the lab's discovery split)
- **THEN** the response includes `vault-router` with `methods: ["vault.get", "vault.search", "vault.claim"]`
- **AND** no other method names are exposed by this router

#### Scenario: Method signatures are stable
- **WHEN** any of the three methods is called
- **THEN** the argument names are exactly as documented: `vault.get(vault_id: str, agent_id: str, correlation_id: str | None = None)`, `vault.search(query: str, agent_id: str, top_k: int = 5, correlation_id: str | None = None)`, `vault.claim(vault_id: str, claim_id: str, agent_id: str, correlation_id: str | None = None)`
- **AND** additional arguments are rejected with `400 Bad Request`
- **AND** missing required arguments are rejected with `400 Bad Request` and a message naming the missing field

### Requirement: Tehuti Guard Policy Gate
Every gateway method call SHALL be gated by `POST /decision` to Tehuti Guard (default `http://127.0.0.1:8013`). The agent's `maat_agents.yaml` ring drives the policy outcome. No method is permitted to bypass the gate, even for read-only operations.

#### Scenario: Each method calls POST /decision before any work
- **WHEN** any of `vault.get`, `vault.search`, `vault.claim` is called
- **THEN** the implementation calls `POST http://127.0.0.1:8013/decision` first
- **AND** the request body is:
  ```json
  {
    "machine_id": "<device_id from caller, or 'unknown'>",
    "actor": {"id": "<agent_id>", "role": "agent"},
    "action": {
      "kind": "read" | "execute",
      "resource": "<vault_id> | vault:search | <vault_id>#<claim_id>",
      "risk": "low" | "medium"
    }
  }
  ```
- **AND** the request includes the header `X-Correlation-ID: <correlation_id>` (or a generated one if not supplied)
- **AND** the implementation does NOT proceed with any DB query, render, or response until the decision is `allow`

#### Scenario: Risk level is set per method
- **WHEN** a method is called
- **THEN** `vault.get` and `vault.claim` use `action.risk = "low"`
- **AND** `vault.search` uses `action.risk = "medium"` (it may surface multiple entries, increasing blast radius if leaked)

#### Scenario: Inner-ring agents are denied
- **WHEN** an inner-ring agent (per `maat_agents.yaml`) calls any vault method
- **THEN** Tehuti Guard returns `{"decision": "deny", "reason": "..."}` (or the equivalent `require_approval` outcome)
- **AND** the router returns `{"error": "denied", "decision": <Guard response>}` with HTTP status 403
- **AND** no data is fetched, no render is performed, no HTML is written
- **AND** a `maat_governance_events` row is written with `record_type="vault.<method>"`, `payload.decision="deny"`, `payload.reason=<Guard reason>`

#### Scenario: Unknown agents fail closed
- **WHEN** a vault method is called with an `agent_id` not present in `maat_agents.yaml`
- **THEN** Tehuti Guard returns the default inner-ring denial (the policy engine's unknown-agent fail-closed default)
- **AND** the same denial path as the inner-ring scenario applies

#### Scenario: Guard unreachable returns review
- **WHEN** Tehuti Guard at `:8013` is unreachable (connection refused, timeout)
- **THEN** the router returns `{"error": "review", "decision": {"decision": "review", "reason": "guard_unreachable"}, ...}` with HTTP status 503
- **AND** a `maat_governance_events` row is written with `record_type="vault.<method>"`, `payload.decision="review"`, `payload.reason="guard_unreachable"`
- **AND** the caller (an MCP-aware agent) is expected to surface the `review` outcome to the operator rather than retrying indefinitely
- **AND** the implementation does NOT fall through to an "allow if guard is down" path

### Requirement: Correlation ID Propagation
Every gateway method call SHALL accept a `correlation_id: str | None` parameter. If not supplied, the router SHALL generate a uuid4. The `correlation_id` SHALL flow through the Guard call (as `X-Correlation-ID` header and `correlation_id` in the request body if accepted) and SHALL be recorded in the `maat_governance_events` row written by the router.

#### Scenario: Caller-supplied correlation_id is honored
- **WHEN** `vault.get(vault_id, agent_id, correlation_id="abc-123")` is called
- **THEN** the Guard call includes `X-Correlation-ID: abc-123`
- **AND** the `maat_governance_events` row has `correlation_id="abc-123"`

#### Scenario: Generated correlation_id is a uuid4
- **WHEN** `vault.search(query, agent_id)` is called without a `correlation_id`
- **THEN** the router generates a uuid4 (e.g. via `uuid.uuid4().hex` or `str(uuid.uuid4())`)
- **AND** the same uuid4 is used in the Guard call and the governance event row
- **AND** the response includes the generated `correlation_id` in a `X-Correlation-ID` response header (echoed back to the caller)

#### Scenario: Correlation ID is logged
- **WHEN** any vault method is called
- **THEN** the implementation logs at INFO level: `vault.<method> agent_id=<agent_id> correlation_id=<cid> decision=<allow|deny|review> latency_ms=<N>`
- **AND** the log line is written to the standard logger (which by default routes to the lab's `~/.maat/events.jsonl` if configured)

### Requirement: vault.get
`vault.get(vault_id, agent_id, correlation_id=None)` SHALL return the rendered HTML for a known `vault_id`, plus its JSON-LD block, after passing the Guard gate.

#### Scenario: vault.get returns rendered HTML and JSON-LD
- **WHEN** `vault.get(vault_id, agent_id)` is called and Guard returns `allow`
- **THEN** the implementation loads the `VaultEntry` (from in-process cache or by re-ingesting from the source)
- **AND** calls `render_entry(entry)` to produce the HTML
- **AND** returns `{"vault_id": "<vault_id>", "html": "<rendered html>", "json_ld": <dict>}` with HTTP status 200

#### Scenario: vault.get on unknown vault_id returns 404
- **WHEN** `vault.get(vault_id="vault:nonexistent_agent:essay:00000000", agent_id)` is called
- **THEN** Guard returns `allow` (the resource is the read, not the existence of the entry)
- **AND** the implementation attempts to load the entry, fails to find it
- **AND** returns `{"error": "not_found", "vault_id": "..."}` with HTTP status 404
- **AND** a `maat_governance_events` row is written with `record_type="vault.get"`, `payload.outcome="not_found"`

#### Scenario: vault.get does not include the full body in the response when the entry is large
- **WHEN** the rendered HTML exceeds 1 MB (large body_text, many claims)
- **THEN** the implementation writes the HTML to a wiki page file (`<vault_root>/entries/<vault_id>.md`) instead of returning it inline
- **AND** the response includes `{"vault_id": "...", "wiki_path": "<absolute path>", "json_ld": <dict>}` with HTTP status 200
- **AND** the response does NOT include the full HTML string in `response.html`

### Requirement: vault.search
`vault.search(query, agent_id, top_k=5, correlation_id=None)` SHALL return a list of `VaultEntry` summaries, after passing the Guard gate. The list SHALL be re-ranked so source tier is honored.

#### Scenario: vault.search returns a list of summaries
- **WHEN** `vault.search(query, agent_id)` is called and Guard returns `allow`
- **THEN** the implementation calls `ingest_from_query(query, top_k)` to get a list of `VaultEntry` objects
- **AND** returns a list of summary dicts, each with: `vault_id`, `title`, `author`, `source_tier`, `status`, `similarity` (raw cosine), `claim_count`, `maat_score`, `excerpt` (first 200 chars of `body_text`, HTML-escaped)
- **AND** the list length is at most `top_k` (default 5)
- **AND** the list is re-ranked by `similarity * source_tier_weight` descending, where weights are `PRIMARY_CANON=1.0`, `SECONDARY=0.8`, `COMMENTARY=0.6`, `AI_DRAFT=0.3`

#### Scenario: vault.search excludes denied results
- **WHEN** the underlying retrieval returns a result whose `vault_id` is in a deny-list (e.g. a `disputed` entry marked hidden)
- **THEN** that result is excluded from the response
- **AND** the exclusion is logged at INFO level with the `vault_id` and reason

#### Scenario: vault.search on empty query returns 400
- **WHEN** `vault.search(query="", agent_id)` is called
- **THEN** the implementation returns `{"error": "empty_query"}` with HTTP status 400
- **AND** Guard is NOT called (validation happens before the gate for trivially invalid input)

### Requirement: vault.claim
`vault.claim(vault_id, claim_id, agent_id, correlation_id=None)` SHALL return a specific `Claim` object plus its full `evidence[]` array, after passing the Guard gate.

#### Scenario: vault.claim returns the claim and its evidence
- **WHEN** `vault.claim(vault_id, agent_id, claim_id="claim-001")` is called and Guard returns `allow`
- **THEN** the implementation loads the parent `VaultEntry`
- **AND** returns `{"vault_id": "<vault_id>", "claim_id": "claim-001", "claim": <Claim dict>, "evidence": [<EvidenceRef dict>, ...], "parent_source_tier": "<source_tier>", "parent_status": "<status>"}` with HTTP status 200

#### Scenario: vault.claim on unknown claim_id returns 404
- **WHEN** `vault.claim(vault_id, agent_id, claim_id="claim-999")` is called and the parent entry has only 3 claims
- **THEN** the implementation returns `{"error": "claim_not_found", "vault_id": "...", "claim_id": "claim-999", "available_claim_ids": ["claim-001", "claim-002", "claim-003"]}` with HTTP status 404
- **AND** the `available_claim_ids` field is included so the caller can self-correct

#### Scenario: vault.claim uses the fragment identifier as the Guard resource
- **WHEN** the Guard call is made
- **THEN** `action.resource` is `f"{vault_id}#{claim_id}"` (the fragment identifier is the permissioned resource, not just the entry)
- **AND** this means an agent with `claim`-level permission on a parent entry does not automatically have `claim`-level permission on every claim in that entry

### Requirement: Governance Event Logging
Every gateway method call SHALL write a `maat_governance_events` row via `MaatMemoryPostgres.log_governance_event`. The row SHALL include `record_type`, `source_service`, `correlation_id`, `agent`, and a `payload` that captures the relevant fields for audit.

#### Scenario: log_governance_event is called with the documented fields
- **WHEN** any vault method completes (regardless of decision)
- **THEN** the implementation calls `MaatMemoryPostgres.log_governance_event` with:
  - `record_type="vault.get" | "vault.search" | "vault.claim"`
  - `agent=<agent_id>`
  - `source_service="vault-router"`
  - `correlation_id=<cid>`
  - `payload={
      "vault_id" | "query" | "vault_id+claim_id": <resource>,
      "decision": "allow" | "deny" | "review",
      "reason": "<Guard reason or router reason>",
      "outcome": "success" | "not_found" | "empty_query" | "denied" | "guard_unreachable",
      "latency_ms": <int>,
      "result_count": <int, for search>,
    }`

#### Scenario: Failed writes do not break the response
- **WHEN** the `maat_governance_events` insert fails (DB unreachable, schema mismatch)
- **THEN** the implementation logs the failure at WARNING level with the full payload
- **AND** the method response is still returned to the caller with the documented success body
- **AND** the implementation does NOT raise the DB error to the caller (governance is observability, not gating)

### Requirement: MCP Resource Surface
The vault-router SHALL expose vault entries as MCP resources accessible via the openclaw gateway. Each `vault_id` SHALL be a unique resource URI.

#### Scenario: Resource URI scheme
- **WHEN** an MCP-aware agent lists resources via the gateway
- **THEN** each vault entry appears as `vault://<vault_id>` (e.g. `vault://vault:opencode_imhotep_terminal_12345:essay:7c2f9a4b`)
- **AND** the resource's `mimeType` is `text/html` (the rendered page)
- **AND** a companion resource `vault://<vault_id>/jsonld` is exposed with `mimeType: application/ld+json`

#### Scenario: Reading the resource returns the rendered HTML
- **WHEN** an MCP consumer reads `vault://<vault_id>`
- **THEN** the response body is the rendered HTML string
- **AND** the response includes a `correlation_id` header for trace continuity
- **AND** the Guard gate has already been evaluated (the read is not permitted without a decision)

### Requirement: Agent Access Declarations
The `maat_agents.yaml` file SHALL be updated to declare vault-router access per agent, using the existing access types (`query`, `log_task`, `log_change`, `*`). No new access types are introduced.

#### Scenario: outer-ring agents get full vault access
- **WHEN** an agent has `access: ["*"]` (or is mapped to `outer-ring` in `PolicyEngine._ring_map`)
- **THEN** it can call `vault.get`, `vault.search`, and `vault.claim`
- **AND** Tehuti Guard returns `allow` for all three

#### Scenario: middle-ring agents get read-only vault access
- **WHEN** an agent has `access: ["query", "log_learning"]` (mapped to `middle-ring`)
- **THEN** it can call `vault.get` and `vault.search`
- **AND** `vault.claim` returns `deny` from Guard with reason `"middle-ring cannot perform tool.vault.claim"` (or equivalent)
- **AND** the deny event is logged in `maat_governance_events`

#### Scenario: inner-ring agents get no vault access
- **WHEN** an agent has `access: ["read", "memory.read"]` (mapped to `inner-ring`)
- **THEN** all three vault methods return `deny` from Guard
- **AND** the deny events are logged

#### Scenario: maat_agents.yaml uses existing access types only
- **WHEN** the `maat_agents.yaml` file is updated
- **THEN** the new vault access declarations use only the existing access types: `query`, `log_task`, `log_learning`, `log_change`, `log_decision`, `*`
- **AND** no new access type string is introduced
- **AND** the YAML file passes the existing schema validation (if any)
