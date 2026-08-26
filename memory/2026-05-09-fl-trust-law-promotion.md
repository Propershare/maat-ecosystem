# Florida Trust Law RAG — Promotion 2026-05-09

## Status: test-payload → **active**

### What was done

1. **Created canonical structure** under `/workflows/domain/trust/fl-trust-law/`:
   - `README.md` — pack overview, access instructions, TODOs
   - `contracts/guard-contract.yaml` — Tehuti Guard three-ring contract (scope, policy, audit)
   - `gateways/allowlist.yaml` — tool/agent access control

2. **Updated registry.yaml** (`maat-ecosystem/skeleton/gateways/`):
   - `fl-trust-law` status changed from `test-payload` to `active`
   - Added `promoted_at` and `guard_contract` pointers
   - Updated description to reflect active status

3. **Updated manifest.json** (`data/retrieval_packs/fl-trust-law/`):
   - Added `status: "active"`, `promoted_at`, `promoted_by` fields
   - Updated notes to reference guard contract location

### Remaining (TODOs)

- [ ] Tehuti Guard three-ring governance implementation (current scope check is heuristic in `query_rag.py`)
- [ ] Maatbench regression test suite for common query patterns
- [ ] Corpus refresh pipeline (detect statute updates, re-index)
- [ ] Gateway allowlist review for non-dev access

### Key files

- `workflows/domain/trust/fl-trust-law/` — canonical pack location
- `contracts/guard-contract.yaml` — scope/policy/audit contract
- `data/retrieval_packs/fl-trust-law/documents/rag/indexes/primary/index.faiss` — 2462-vector FAISS index
- `scripts/query_rag.py` — RAG query CLI with scope guardrails
- `mcp-servers/tehuti-core/tehuti_core_server.py` — `query_florida_trust_law` MCP tool
