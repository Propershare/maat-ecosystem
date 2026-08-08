# Canon vs domain knowledge — architectural boundary

**Principle:** The lab ecosystem is the **constitution** (MAAT / KA2 governance), not the **law library**. Positive-law corpora and subject-matter packs are **secondary evidence**: consultable, provenance-bearing, and interpreted **only** through sacred scoring, routing, guard, and audit logic.

This document is the **refactor handoff** for moving Florida (and future) legal corpora **out** of the canonical tree while keeping **interfaces** in core.

---

## 1. Layers (strict split)

| Layer | Contents | Lives in canon tree? |
|-------|----------|----------------------|
| **Canon / governance** | MAAT runtime logic, KA2 schemas & methodology, constitutional scorecards, planner/routing **rules**, contracts (`maat.archivist_record.v1`, etc.), guard/audit, **abstract** retriever & tool interfaces | **Yes** — versioned, reviewed, minimal surface |
| **Secondary knowledge** | Florida trust law, other states, treatises, statutes, cases, domain RAG corpora | **No** — external packs, volumes, or services |

**Rule:** Canon **governs how** external knowledge is trusted, escalated, synthesized, and flagged for human review. Canon **does not** embed domain text as canonical truth.

---

## 2. Current state (proof of concept — wrong long-term placement)

Today, Florida trust material is **physically and logically** inside the monorepo:

| Artifact | Path | Issue for long-term model |
|----------|------|---------------------------|
| FL pack corpus + manifest | `data/retrieval_packs/fl-trust-law/` | Treated like repo-owned “product data” next to governance code |
| Gateway binding FL + pack id | `maat-ecosystem/skeleton/gateways/registry.yaml` (`fl-trust-law`) | Reads as if FL gateway were **canonical** product surface |
| BM25 retrieval root | `gemma4-toolshim/swarm/retrieval.py` → `LAB_ROOT/data/retrieval_packs` | Hard-couples governance shim to on-disk pack layout |
| Bench fixtures citing FL paths | `maat-ecosystem/maatbench/suites/gateway_contract/pass_fl_pack.json` | Fine as **contract tests** if paths become configurable or mock-only |
| Lab-root drop zone | `Legal_AI_FL/`, `Legal_AI_FL.rar` | Operational; should not imply canon ownership |

**What is correctly in core (keep):**

- `gemma4-toolshim/swarm/gateway_contract.py` — schemas, `PASS_AT`, RBL/forbidden detectors
- `gemma4-toolshim/swarm/guard_validator.py` — post-turn decisions
- `gemma4-toolshim/swarm/ka2_router.py` — tagging / routing policy
- `gemma4-toolshim/swarm/gateway_server.py` — **mechanism** of `/ask` (should eventually call **abstract** retrieval only)
- `maat-ecosystem/skeleton/schemas/*.json` — KA2 / archivist contracts
- `gateway_registry.py` + **generic** registry shape — gateway ids as **policy slots**, not as “Florida lives here forever”

---

## 3. Target architecture

```
                    ┌─────────────────────────────────────┐
                    │  Canon: MAAT / KA2 / contracts      │
                    │  scoring · guard · audit · routing   │
                    └─────────────────┬───────────────────┘
                                      │ abstract calls only
              ┌───────────────────────┼───────────────────────┐
              ▼                       ▼                       ▼
     ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
     │ Domain adapter  │    │ Domain adapter  │    │ Domain adapter  │
     │ legal-fl-trust  │    │ legal-fl-probate│    │ … (future)      │
     └────────┬────────┘    └────────┬────────┘    └────────┬────────┘
              │                      │                      │
              └──────────────────────┴──────────────────────┘
                         external repo / volume / MCP
```

- **Core** returns / enforces: `ArchivistRecord`, scorecard, `decision`, provenance **slots** (filled from adapter responses).
- **Adapters** return: chunk text, **authority refs**, **jurisdiction**, **confidence**, **contradictions** (per adapter contract), **never** “truth” that bypasses MAAT.

---

## 4. Refactor plan (phased)

### Phase A — Document & configure (no big move yet)

1. Mark `data/retrieval_packs/fl-trust-law/` as **legacy PoC location** in `README` (pack README + this doc).
2. Add env/config: `DOMAIN_PACKS_ROOT` or `RETRIEVAL_PACKS_EXTRA_PATHS` so `retrieval.py` resolves packs from **multiple roots** (canon tree + one or more external directories).
3. Keep tests green by pointing tests at a **temp** or **fixtures** tree for CI, not only `data/retrieval_packs/fl-trust-law/`.

### Phase B — Relocate corpus (physical split)

1. Create **`tehuti-domain-packs`** (name TBD) repo or **`/var/lib/tehuti/domain-packs/`** (or NFS) containing:
   - `fl-trust-law/manifest.json` + `documents/` (same logical layout as today).
2. Remove or **gitignore** bulk `documents/` under the monorepo pack path; keep only a **stub** manifest pointer or symlink policy documented in ops.
3. Update install scripts to sync from external volume or `git clone` shallow.

### Phase C — Registry semantics (logical split)

1. In `registry.yaml`, treat **`fl-trust-law`** (or rename to **`legal-fl-trust`**) as a **domain gateway profile**: same schema, same immune pipeline, **`pack_uri` or `adapter_id`** pointing to **external** pack id resolved via `DOMAIN_PACKS_ROOT`.
2. Add a **generic** gateway entry pattern: `retrieval_adapter: http+mcp://...` or `pack_path: ${DOMAIN_PACKS_ROOT}/fl-trust-law` — **no** Florida-specific strings hardcoded in Python except default env examples.

### Phase D — MCP / HTTP sidecar (optional, cleanest ops)

1. Standalone **small service**: “Domain Retrieval API” — `POST /search` `{ pack_id, query, top_k }` → hits + provenance.
2. Core `gateway_server` calls that URL via **abstract** `RetrieverClient` (stdlib HTTP first).
3. Tehuti Guard / Ka Discovery register the sidecar as **non-canon organ** (tool only).

### Phase E — Bench & Forge

1. `maatbench` fixtures: replace hardcoded `data/retrieval_packs/fl-trust-law/...` paths with **env-relative** or **minimal synthetic** records (contract-only).
2. `forge/retrieval_proposals.py`: target paths under **external** pack roots for promotions, not monorepo `data/` by default.

---

## 5. What stays in core (non-negotiable list)

| Stay | Path / component |
|------|------------------|
| Archivist + KA2 contracts | `maat-ecosystem/skeleton/schemas/`, `gateway_contract.py` |
| Scorecard thresholds & forbidden vocabulary | `gateway_contract.py`, `guard_validator.py` |
| HTTP gateway **shell** | `gateway_server.py` (after abstract retrieval) |
| Registry **loader** & `GatewayEntry` shape | `gateway_registry.py` |
| Sentinel / archivist stream / gitMaat adapter | `sentinel_stream.py`, `archivist_gitmaat.py` |
| Evolution lanes doc | `docs/MAAT-EVOLUTION-LANES.md` (update with pointer to this doc) |

---

## 6. What moves out or becomes external

| Move | From | To |
|------|------|-----|
| FL statute/case bulk | `data/retrieval_packs/fl-trust-law/documents/` | External repo or data volume |
| Optional: entire pack folder | `data/retrieval_packs/fl-trust-law/` | Same; monorepo retains **link manifest** or **empty stub** |
| Lab convenience copies | `Legal_AI_FL/` at lab root | Ops-only; not canon |

**Stays in monorepo as stubs only (acceptable):**

- Minimal **contract tests** JSON under `maatbench/suites/` (synthetic records, no real corpus).
- **Documentation** of adapter API (`docs/DOMAIN-RETRIEVAL-ADAPTER.md` — add when implementing Phase D).

---

## 7. How core queries without absorbing canon

1. **Interface:** `RetrieverProtocol.search(pack_id, query) -> list[RetrievalHit]` with required fields: `text`, `source_uri`, `jurisdiction`, `authority_type` (optional), `score`, `chunk_id`.
2. **Implementations:** `FilesystemRetriever(packs_root=env)`, `HttpRetriever(base_url=...)`, later `McpRetriever(...)`.
3. **Gateway:** Only passes adapter output into `ArchivistRecord.sources` and `payload.retrieved_excerpts` — **MAAT** decides allow/review/deny; corpus never updates `PASS_AT`, schemas, or guard rules.

---

## 8. Goal restated

**MAAT/KA2 governs interpretation of all evidence; domain law is evidence, not part of governance source code.**

The current ecosystem-attached FL pack was the right **PoC** to prove packs + gateway + bench; the **correct long-term** placement is **outside** the canonical tree, wired through **abstract adapters** and **policy-only** registry entries.

---

## 9. Immediate next step for implementers

1. Implement **`DOMAIN_PACKS_ROOT`** (or multi-root) in `retrieval.py` + tests.
2. Relocate **`fl-trust-law` documents** to first external path; verify `gateway_server` + one live `/ask` query.
3. Trim repo copy to stub + update `.gitignore` / docs.
4. (Later) Extract MCP/HTTP sidecar if multi-host or multi-tenant retrieval is required.

---

*Related: `docs/MAAT-EVOLUTION-LANES.md`, `docs/MAAT-GATEWAY-REGISTRY.md`, `PRD_Draft_Maat_Legal_Runtime.md` (planner-first product — separate from canon purity).*
