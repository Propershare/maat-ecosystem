# Tehuti / UKMT knowledge — Maat audit before RAG

**Purpose:** Decide **what must be true** (governance + evidence + separation of concerns) before investing in chunking, embeddings, and retrieval. UKMT / RBG scholarship **is** lab knowledge — but it is **not** immutable canon unless explicitly promoted.

**Data layout (on disk):** [`data/tehuti/README.txt`](../data/tehuti/README.txt)

---

## 1. Ring placement (Maat order)

| Corpus | Ring (intent) | Why |
|--------|------------------|-----|
| **Soul / constitution / Ka schemas** (`maat-ecosystem/soul/`, `skeleton/schemas/`) | **Inner — canon** | Immutable doctrine; RAG must not silently “edit” or replace this via retrieved chunks. |
| **UKMT + RBG text** (`data/tehuti/ukmt-rbg-dataset/`, esp. `canon-UKMT/`, `rbg_library/`) | **Middle — scholarship** | Curated study material, proposals, interpretive layers — **knowledge for reasoning**, not deployment truth without Analyst + (where required) Guard. Aligns with `.cursorrules`: scholarship **proposes**, does not mutate canon without process. |
| **Large PDF library** (`data/tehuti/pdf-library/`) | **Scholarship / reference** (same tier as middle for retrieval policy) | Same policy as RBG-derived text: high volume, mixed provenance — **never** auto-promote to “fact” without citation and confidence. |
| **Operational RAG + agents** (`maatlangchain/`, products) | **Outer** when monetized / customer-facing | Tooling and pipelines live here; **ingest jobs** are `execute`/`write` surfaces per [`TEHUTI-GUARD-INTEGRATION-MATRIX.md`](TEHUTI-GUARD-INTEGRATION-MATRIX.md). |

**Implication:** UKMT scholarship **belongs in “knowledge”** for the system — but the **vector index** is a **scholarship instrument**, not a second canon store. Naming and metadata must say so (`collection`, `tags`, `ring: middle` or equivalent).

---

## 2. Truth — what we actually have (evidence)

| Asset | Location | Notes |
|-------|----------|--------|
| UKMT + RBG + ka2 configs | `data/tehuti/ukmt-rbg-dataset/` | Canonical **text-first** tree for UKMT work; includes `ka2_agent_config.json` / `ka2_agent_system_prompt.md`. |
| PDF corpus | `data/tehuti/pdf-library/` | ~5.5 GB from `Tehutidata.db.rar`; separate **retrieval policy** from UKMT `.txt` (OCR, scans, mixed quality). |
| Snapshot zip | `data/tehuti/archives/` | Provenance only. |
| Source RAR (duplicate of PDF pack) | `maatlangchain/docs/Tehutidata.db.rar` | Do not fork “truth” — one ingestion story; document which path is authoritative for re-index. |

**Gap:** On-disk layout is clean; **governance registration** of `data/tehuti/**` in Tehuti Guard `THREE_RING_GOVERNANCE` (or extended policy) is **not** done yet — ingest paths should map to **`write` / memory_write** with an explicit **namespace** (see matrix).

---

## 3. Balance — separation before one RAG “blob”

1. **Two logical collections (minimum):** e.g. `tehuti_ukmt_rbg` vs `tehuti_pdf_library` in Postgres/pgvector metadata — so routing and disclaimers can differ.
2. **No merge of canon:** soul/brain JSON graphs and UKMT chunks must not share a single undifferentiated index without **tags** — or answers will conflate doctrine with scholarship.
3. **gitMaat (Maat Memory):** Ingestion milestones should **`log_decision`** / **`log_change`** (or MCP equivalents): scope, chunk size, embedding model, **excluded paths**, and **policy version** — Archivist discipline ([`REMOTE_SWARM_SPEC.md`](REMOTE_SWARM_SPEC.md)).

---

## 4. Justice — permission & safety (pre-build)

Per [`TEHUTI-GUARD-INTEGRATION-MATRIX.md`](TEHUTI-GUARD-INTEGRATION-MATRIX.md) (memory writes / RAG ingest = **`write`**):

| Item | Status |
|------|--------|
| Define **Guard resource id** for “RAG ingest to collection X” (path or logical namespace) | **Open** |
| Decide **who may trigger ingest** (human operator only vs agent with elevation) | **Open** |
| **Secrets:** `PGVECTOR_DB_URL`, API keys — never in chunks; scrub in ETL | **Required** |
| **PII / sensitive paths:** exclude or quarantine before embed | **Open** |
| **Licensing / redistribution:** PDF pack is large and mixed — confirm **internal-only** vs product use | **Open** |

---

## 5. Order — technical prerequisites (engineering)

| Step | Purpose |
|------|---------|
| **A. Baseline DB** | `PGVECTOR_DB_URL` healthy; extension `vector`; same DB contract as [`GITMAAT-CONNECT.md`](GITMAAT-CONNECT.md). |
| **B. Chunking strategy** | UKMT `.txt` vs PDFs need **different** chunkers; table of params before code. |
| **C. Embedding model** | One model per collection or one global — document and pin in `maatlangchain` / pipeline config. |
| **D. Hygiene** | Dedup, filename normalization, optional virus scan on bulk PDFs if ingested from untrusted media. |
| **E. Evaluation** | Small **golden set** of UKMT queries (even 10) with expected “must cite” sources — before scaling. |
| **F. Observability** | Log ingest runs to gitMaat + optional metrics (chunk count, failures). |

---

## 6. Sankofa — what to log before first production ingest

- **Decision:** “Scholarship RAG” vs “Canon-adjacent” — **explicit**.
- **Change:** `data/tehuti/` layout version + `README.txt` commit hash.
- **Learning:** first retrieval failure modes (wrong chunk, wrong collection).

---

## 7. Recommended order of work (before “building RAG”)

1. **Confirm ring metadata** in index schema (`ring`, `corpus_id`, `source_path`).
2. **Register Guard policy** for ingest + query tools (even if v1 is “allow from localhost only”).
3. **Pilot ingest** — `ukmt-rbg-dataset` only, small slice, then measure.
4. **pdf-library** — second phase (OCR/quality gates).
5. **Wire swarm/bridge** — route “scholarship” queries to collections that include UKMT tags.

---

## 8. Freeze boundary (this document)

**In scope:** Governance placement, separation of corpora, checklist, logging expectations.  
**Out of scope:** Concrete chunk sizes, hybrid search, rerankers — **after** §7.1–7.3 are satisfied.

**Related:** [`MAAT-AUDIT-ACTION-PLAN.md`](MAAT-AUDIT-ACTION-PLAN.md), [`MAAT-ECOSYSTEM-CONNECTIVITY-FREEZE.md`](MAAT-ECOSYSTEM-CONNECTIVITY-FREEZE.md) (spine), [`docs/SCOUT-ANALYST-ARCHIVIST.md`](SCOUT-ANALYST-ARCHIVIST.md) (roles on retrieval).

---

*Last updated: 2026-04-14 — Tehuti data under `data/tehuti/` post-consolidation.*
