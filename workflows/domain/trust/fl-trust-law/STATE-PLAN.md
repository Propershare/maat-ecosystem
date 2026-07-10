# Florida Trust Law RAG — State Plan

**Pack ID:** `fl-trust-law`  
**Status:** Active (promoted 2026-05-09)  
**Last updated:** 2026-05-09T10:16Z

---

## 1. Current State

### What works ✅

| Area | Status | Notes |
|------|--------|-------|
| **Corpus** | ✅ 2,462 chunks from 39 source files | FL Statutes Ch. 731-736, 30+ cases, court rules |
| **Index** | ✅ FAISS 7.3MB, 768-dim, cosine | Built 2026-05-07, `nomic-embed-text` via Ollama |
| **Query CLI** | ✅ `scripts/query_rag.py` | Works with real embeddings + hash fallback |
| **MCP Tool** | ✅ `query_florida_trust_law` in Tehuti Core `:8014` | Runs query_rag.py as subprocess |
| **Gateway** | ✅ Registered in `registry.yaml` (status=active) | Tools: query_gitmaat, query_florida_trust_law, read_file, search |
| **Manifest** | ✅ `manifest.json` with full schema + guardrails | Content warnings, scope drift RBL flag |
| **Guard Contract** | ✅ `contracts/guard-contract.yaml` | Three-ring (scope/policy/audit) — defined but not yet wired |
| **Allowlist** | ✅ `gateways/allowlist.yaml` | Tools/agents blocked and allowed |
| **Maatbench fixture** | ✅ `pass_fl_pack.json` | Reference record, not test suite |
| **Canonical location** | ✅ `workflows/domain/trust/fl-trust-law/` | Registry points here |
| **Discovery** | ✅ Organ listed on `:8010` (brain/tehuti-core) | MCP endpoint `:8014` |
| **Postgres** | ✅ `PGVECTOR_DB_URL` configured | gitMaat available |
| **Ollama** | ✅ `nomic-embed-text:latest` loaded | Embedding model ready |

### What doesn't work yet ❌

| Area | Gap | Impact |
|------|-----|--------|
| **Guard wiring** | Guard contract defined but not enforced by query_rag.py | Current scope check is heuristic — not formal Tehuti Guard |
| **Maatbench suite** | Only reference fixture (`pass_fl_pack.json`) — no regression test suite | No automated quality checks for the pack |
| **Corpus refresh** | No pipeline to detect statute updates / re-index | Corpus drifts as FL law changes |
| **Legal advice guard** | No mandatory disclaimer injected into results | Results could be interpreted as legal advice |
| **Audit logging** | Guard contract requires audit but no logger exists | Compliance gap |
| **Non-dev access** | Allowlist not reviewed for broader access | Still dev-only |

---

## 2. Prioritized TODOs

### P0 — Must have (blocking production use)

| # | Task | Description | Effort |
|---|------|-------------|--------|
| 1 | **Wire Tehuti Guard three-ring** | Replace heuristic scope check in `query_rag.py` with formal `POST /decision` to Tehuti Guard `:8013`. Implement: Ring 1 scope gate, Ring 2 policy check, Ring 3 audit log. | Medium |
| 2 | **Add disclaimer injection** | Query results must prepend the guard contract disclaimer: *"This material is for research and citation purposes only. It does not constitute legal advice."* | Small |
| 3 | **Build Maatbench regression suite** | Write test suite with 10+ cases: in-scope queries (should pass), out-of-scope (should RBL-flag), mixed queries (should warn), edge cases. | Medium |

### P1 — Should have (quality of life)

| # | Task | Description | Effort |
|---|------|-------------|--------|
| 4 | **Corpus refresh pipeline** | Detect statute updates from FL Legislature, compare against existing chunks, rebuild index on diff. Schedule weekly. | Large |
| 5 | **Audit logger** | Log all legal queries (redacted) to Postgres or file-based audit log. Per guard contract. | Small |
| 6 | **Gateway allowlist review** | Review non-dev access policies for the pack. | Small |

### P2 — Nice to have

| # | Task | Description | Effort |
|---|------|-------------|--------|
| 7 | **Cross-pack correlation** | When querying FL trust law, also pull relevant gitMaat learnings/decisions for richer context. | Medium |
| 8 | **Maat Studio integration** | Expose pack in the dashboard (planned voice organ → Maat Studio). | N/A |
| 9 | **Multi-pack federation** | Add other state trust law packs (CA, NY) with cross-jurisdiction guardrails. | Large |

---

## 3. Architecture (current)

```
User query
    │
    ▼
Tehuti Core MCP (:8014)
    │  tool: query_florida_trust_law
    ▼
query_rag.py (CLI)
    │  1. Embed query (nomic-embed-text → Ollama :11434)
    │  2. FAISS search (7.3MB index, 2462 vectors)
    │  3. Return top-k results
    ▼
Results → disclaimer (pending) → user
```

**Pending architecture (after P0):**
```
User query
    │
    ▼
Tehuti Core MCP (:8014)
    │
    ▼
query_rag.py (CLI)
    │
    ├── Ring 1: Tehuti Guard scope check (POST /decision)
    │       └── BLOCK if out-of-scope (RBL flag)
    │
    ├── Ring 2: Policy check (research-only framing)
    │       └── Inject disclaimer into results
    │
    ├── Embed + FAISS search
    │
    └── Ring 3: Audit log
            └── Log to Postgres/file (redacted)
    │
    ▼
Results → user
```

---

## 4. Key Files

| File | Purpose |
|------|---------|
| `workflows/domain/trust/fl-trust-law/README.md` | Pack overview |
| `workflows/domain/trust/fl-trust-law/contracts/guard-contract.yaml` | Three-ring governance contract |
| `workflows/domain/trust/fl-trust-law/gateways/allowlist.yaml` | Tool/agent access control |
| `workflows/domain/trust/fl-trust-law/STATE-PLAN.md` | This file |
| `data/retrieval_packs/fl-trust-law/manifest.json` | Pack manifest (active) |
| `data/retrieval_packs/fl-trust-law/scripts/query_rag.py` | RAG query CLI |
| `data/retrieval_packs/fl-trust-law/documents/rag/` | FAISS index + chunks |
| `mcp-servers/tehuti-core/tehuti_core_server.py` | MCP tool (line ~1188) |
| `maat-ecosystem/skeleton/gateways/registry.yaml` | Gateway registry |
| `maat-ecosystem/maatbench/suites/gateway_contract/pass_fl_pack.json` | Reference fixture (not test) |

---

## 5. Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-09 | Promote fl-trust-law to active | Corpus + index + query tool fully built; registry updated |
| 2026-05-09 | Define guard contract before wiring | Contract-first: define the rings before implementing them |
| 2026-05-09 | Place canonical at `workflows/domain/trust/` | AGENTS.md canonical architecture; not `maatlabs/` |
