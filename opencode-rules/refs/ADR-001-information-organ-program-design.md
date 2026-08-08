# ADR-001: Information Organ — Program Design (Stage 3)

**Status:** Proposed (lab doctrine requires Stage 3 before agents build)
**Author:** opencode_staydangerous (operator-collaborated)
**Date:** 2026-08-08
**Supersedes:** none
**Stage:** 3 of 4 (per `refs/agentic-engineering-doctrine-2026-08-08` §3)
**Review cadence:** re-evaluate before Stage 4 implementation begins

---

## 0. Context

The doctrine canonized at `refs/agentic-engineering-doctrine-2026-08-08`
requires Stage 3 program design before any agent writes implementation
code for a new system. The "Information organ" (OCR + Postgres + Ollama +
retrieval) was identified in the doctrine's §7.3 as the current focus
and explicitly named as needing Stage 3 NOW.

This ADR is that Stage 3 deliverable. It defines the call stack, types,
call signatures, and the test that proves "retrievable" — without
writing implementation. The implementation ADR (Stage 4) will reference
this one.

**Existing surface** (per `git log` of `~/.n8n`):
- `Legal_AI_FL/agentic/rag/` has `bm25.py`, `chunker.py`, `retriever.py`,
  `store.py`, `rerank.py`, `router.py`, `citation.py` — a working
  legal-domain RAG (TypeScript? No — these are .py). But no types, no
  schema, no `ContentPiece`/`Chunk`/`SearchResult` table definitions.
- `weknora-analysis/` is a third-party RAG system we studied; not "ours".
- No `doc/ADR/` exists anywhere in the lab repo.

**Scope of this organ:** Lab-wide. The legal RAG is the first consumer;
trading (Alpaca options), MAAT memory recall, and any future knowledge
surface should use the same primitives.

## 1. Goals (in priority order)

1. **Retrievable** — given a natural-language query, return the
   semantically-relevant chunks ranked by a deterministic scorer.
2. **Verifiable** — given a known query, the system reproduces the
   same top-K results across runs and across machines.
3. **Portable** — chunks, embeddings, and metadata survive machine
   boundaries via the existing maat object store.
4. **Auditable** — every retrieval logs the query, the embedding model,
   the candidate set size, and the top-K result ids to maat_memory.

Non-goals (deferred):

- OCR service implementation (assume it exists or is being built
  separately by another organ; this ADR assumes OCR-clean text input).
- Multi-modal embeddings (text-only for v1).
- Cross-language retrieval (English-only for v1).
- Streaming responses from the retrieval service.

## 2. Call stack

```
                       Lab Operator / Agent
                              │
                              ▼
                  ┌─────────────────────────┐
                  │ information.search(query,│  ← single entry point
                  │   top_k=10, filters={})  │
                  └─────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
      ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
      │ chunker.    │ │ embedder.   │ │ store.      │
      │ split(text, │ │ embed(text) │ │ get(vec,    │  ← pure functions
      │   strategy) │ │  → number[] │ │   filters)  │     no I/O
      └─────────────┘ └─────────────┘ └─────────────┘
              │               │               │
              ▼               ▼               ▼
                  Postgres + pgvector + ollama + maat object store
```

Three pure functions above the storage layer. The entry point
`information.search()` orchestrates them.

## 3. Types (Stage 3 — signatures only, no implementation)

```python
# information/types.py

from dataclasses import dataclass
from typing import Optional

# --- Core domain types ---

@dataclass(frozen=True)
class ContentPiece:
    """A single source document or book chapter. The unit that goes in."""
    piece_id: str           # sha256 of source_uri + content_hash
    source_uri: str          # maat://object/<sha> or file://...
    title: str
    author: Optional[str]
    created_at: str          # ISO 8601
    content_type: str        # "book_chapter" | "transcript" | "note" | ...
    byte_count: int
    metadata: dict           # free-form: chapter, page_range, etc.

@dataclass(frozen=True)
class Chunk:
    """A retrievable unit. Comes from chunking a ContentPiece."""
    chunk_id: str            # sha256 of piece_id + chunk_index + content_hash
    piece_id: str            # FK to ContentPiece
    chunk_index: int         # 0..N within the piece
    text: str                # the actual chunk content (cleaned, no OCR artifacts)
    token_count: int
    embedding: list[float]   # 1024-d for the default model; see §4
    embedding_model: str     # e.g. "mxbai-embed-large"
    metadata: dict           # inherited from ContentPiece + chunk-level

@dataclass(frozen=True)
class SearchResult:
    """What the caller gets back. Top-K ranked chunks with provenance."""
    chunk_id: str            # FK to Chunk
    piece_id: str            # FK to ContentPiece (for back-link)
    text: str                # the chunk text
    score: float             # similarity score (cosine, 0..1)
    rank: int                # 1..K
    source_uri: str          # for the citation trail

@dataclass(frozen=True)
class SearchQuery:
    """What the caller sends in."""
    query_text: str
    top_k: int = 10
    filters: Optional[dict] = None  # piece.content_type, piece.metadata.*, etc.
    embedding_model: Optional[str] = None  # override default

# --- Service result types ---

@dataclass(frozen=True)
class SearchResponse:
    query: SearchQuery
    results: list[SearchResult]
    candidate_count: int      # total candidates before top-K
    retrieval_ms: float        # wall-clock
    embedding_model: str       # what was actually used
```

## 4. Function signatures (Stage 3 — no implementation)

```python
# information/chunker.py

def split(
    piece: ContentPiece,
    strategy: str = "sliding_window",   # "sliding_window" | "semantic" | "fixed"
    max_tokens: int = 512,
    overlap_tokens: int = 64,
) -> list[Chunk]:
    """Split a ContentPiece into Chunks per the strategy.
    Pure: deterministic given (piece, strategy, params). No I/O.
    Embeddings NOT generated here — see embedder.embed_chunks().
    """

# information/embedder.py

def embed_text(text: str, model: str = DEFAULT_EMBED_MODEL) -> list[float]:
    """Embed a single string. Pure given (text, model, ollama_version).
    Default model: 'mxbai-embed-large' (1024-d, fast on CPU).
    """

def embed_chunks(
    chunks: list[Chunk],
    model: str = DEFAULT_EMBED_MODEL,
) -> list[Chunk]:
    """Return new Chunk objects with .embedding populated. Pure: no I/O
    outside the ollama call.
    """

# information/store.py

def upsert(pieces_and_chunks: list[tuple[ContentPiece, list[Chunk]]]) -> int:
    """Idempotent insert. Returns count of chunks written. Transactional.
    Uses maat portable_uris for source files.
    """

def get(embedding: list[float], top_k: int, filters: Optional[dict] = None) -> list[SearchResult]:
    """Vector similarity search. Cosine distance via pgvector.
    Returns top-K ranked by similarity score (descending).
    """

# information/search.py  (the entry point)

def search(query: SearchQuery) -> SearchResponse:
    """Orchestrates: embed query -> vector search -> format response.
    Pure orchestration: delegates to embedder + store.
    Logs to maat_memory on every call (query, candidate_count, top_k).
    """
```

## 5. Ollama call signature (canonical)

```python
# Single ollama call we make. Recorded so any agent or operator can audit.

OLLAMA_EMBED_REQUEST = {
    "model": "mxbai-embed-large",
    "prompt": "<text>",     # up to ~2048 tokens for mxbai
    "options": {
        "num_ctx": 2048,
        "num_gpu": 0,        # CPU-only on staydangerous
        "num_thread": 8,
    },
}
# Response shape:
OLLAMA_EMBED_RESPONSE = {
    "embedding": list[float],   # length 1024 for mxbai-embed-large
}
# Endpoint: POST http://127.0.0.1:11434/api/embeddings
# Latency target: < 200ms per chunk on CPU
# Failure modes: connection refused (ollama down), timeout, malformed response
```

**Chunk size rationale**: `max_tokens=512, overlap=64` is the standard
for mxbai-embed-large. 512 covers a paragraph; 64 overlap preserves
context at boundaries. v1 is fixed; v2 may go semantic.

## 6. "Retrievable" — the test

A retrieval is **retrievable** iff:

```python
def test_retrievable():
    """The canonical Stage-3 acceptance test. Green before any Stage 4 code."""
    # 1. Seed: 1 book chapter (any ContentPiece with >5 paragraphs)
    piece = seed_fixture_piece()       # known, deterministic

    # 2. Run the full pipeline (chunker + embedder + store)
    chunks = chunker.split(piece)
    embedded = embedder.embed_chunks(chunks)
    store.upsert([(piece, embedded)])

    # 3. Known query — manually authored to test recall, not precision
    query = SearchQuery(query_text="<known sentence from the chapter>",
                        top_k=10)

    # 4. Must return the chunk containing that sentence in the top 1
    response = search(query)
    assert response.results[0].rank == 1
    assert query.query_text in response.results[0].text

    # 5. Determinism — same query, same machine, same result
    response2 = search(query)
    assert response.results[0].chunk_id == response2.results[0].chunk_id

    # 6. Audit trail — every search logs to maat_memory
    assert maat_search_logged(query.query_text, response.results[0].chunk_id)
```

**Stage 3 done = this test is green.** The test must pass with the
STUB implementations in place. Stage 4 (vertical slice) replaces stubs
with real implementations, but the test must remain green across
refactors.

## 7. Postgres schema (Stage 3 — DDL is fine, this is not implementation)

```sql
-- Run against maat_memory database; uses pgvector extension (already installed)

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS information_piece (
    piece_id      TEXT PRIMARY KEY,
    source_uri    TEXT NOT NULL,
    title         TEXT NOT NULL,
    author        TEXT,
    created_at    TIMESTAMPTZ NOT NULL,
    content_type  TEXT NOT NULL,
    byte_count    INTEGER NOT NULL,
    metadata      JSONB NOT NULL DEFAULT '{}'::jsonb,
    -- provenance
    origin        TEXT NOT NULL,  -- 'agent_authored' | 'operator_supplied' | ...
    ingested_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS information_chunk (
    chunk_id        TEXT PRIMARY KEY,
    piece_id        TEXT NOT NULL REFERENCES information_piece(piece_id) ON DELETE CASCADE,
    chunk_index     INTEGER NOT NULL,
    text            TEXT NOT NULL,
    token_count     INTEGER NOT NULL,
    embedding       vector(1024) NOT NULL,         -- mxbai-embed-large dim
    embedding_model TEXT NOT NULL,
    metadata        JSONB NOT NULL DEFAULT '{}'::jsonb,
    UNIQUE (piece_id, chunk_index)
);

-- HNSW index for fast approximate nearest neighbor
CREATE INDEX IF NOT EXISTS information_chunk_embedding_hnsw
    ON information_chunk USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- Filter indexes for the most common filter columns
CREATE INDEX IF NOT EXISTS information_chunk_piece_id_idx
    ON information_chunk (piece_id);
CREATE INDEX IF NOT EXISTS information_piece_content_type_idx
    ON information_piece (content_type);
```

## 8. Vertical slice (Stage 4 plan — referenced, not implemented here)

**Deployment boundary** (from doctrine §3, cross-machine variant):
OCR service + Postgres + Ollama + retrieval. In the lab today that
spans:

| Component | Machine today | Notes |
|-----------|---------------|-------|
| OCR service | TBD (worker or cloud) | Stage 4 picks |
| Postgres + pgvector | staydangerous (localhost:5432/maat_memory) | already running |
| Ollama | staydangerous (localhost:11434) | already running |
| Retrieval service | staydangerous (Python module, called by agents) | this ADR's deliverable |
| Caller | any agent on any machine via maat_memory MCP | "fetch_chunk" + "search" tools |

**Slice = one book chapter end-to-end**:

1. Pick a known book chapter fixture (or generate one from `tehuti-search` data).
2. OCR → clean text (mock for Stage 4 v1; real OCR is another organ's job).
3. `chunker.split()` → Chunks.
4. `embedder.embed_chunks()` → Chunks with embeddings.
5. `store.upsert()` → Postgres rows.
6. `search()` with a known query → SearchResponse.
7. Assert `test_retrievable()` is green.
8. Log receipt to maat_memory (provenance: `agent_authored`).

**Then** add features (deferred from this slice):
- Multi-category routing
- Metadata extraction
- Citation pinning (already exists in `Legal_AI_FL/agentic/rag/citation.py`)
- Cross-machine caching

## 9. Decisions called out

- **Embedding model: mxbai-embed-large (1024-d).** Why: fast on CPU,
  well-supported in ollama, common baseline. To change in the future,
  this ADR gets superseded; do not silently swap models.
- **Vector distance: cosine.** Why: standard for normalized embeddings;
  pgvector's `<=>` operator.
- **Chunk strategy default: sliding window.** Why: simple, deterministic,
  matches the `test_retrievable` fixture. Semantic chunking deferred.
- **Source URIs: maat://object/<sha>.** Why: portable, fetchable from
  any machine via the artifact bank contract.
- **Audit: every search logs to maat_memory.** Why: doctrine §8
  demands falsifiable signals; the retrieval log is the falsifiability
  signal for "is this system actually retrieving correctly?"

## 10. Forbidden (Stage 4 will inherit these)

- Skip Stage 3 and start coding (doctrine §2 — lights-off failure).
- Hard-code embedding model strings outside this ADR.
- Store embeddings in anything other than pgvector on `maat_memory`.
- Skip the audit log on any search call.
- Deploy to production without `test_retrievable` green for 7 consecutive runs.

## 11. Open questions (to resolve before Stage 4)

1. **Which OCR service?** Candidate: tesseract locally on staydangerous,
   or cloud OCR. Cost vs latency vs accuracy.
2. **Filter syntax.** Current `filters: dict` is vague. Need a small DSL
   like `{ "and": [{"content_type": "book_chapter"}, {"metadata.chapter": 3}] }`.
3. **Multi-machine retrieval.** When the operator is on desktop-ccitn8l
   and wants to search staydangerous's Postgres, do we tunnel via SSH or
   expose a service on a Tailscale IP? Deferred until desktop comes online.
4. **Embedding model upgrade path.** When the next mxbai ships with
   2048-d, what's the migration? Re-embed everything? Re-ADR?

## 12. Related

- `refs/agentic-engineering-doctrine-2026-08-08` §3, §7.3 — the doctrine
  requiring this Stage 3 artifact
- `Legal_AI_FL/agentic/rag/` — existing partial implementation (in the
  Legal_AI_FL clone; not modified by this ADR)
- `weknora-analysis/migrations/versioned/` — reference for vector schema
  patterns (also not modified)
- `~/.opencode-rules/40-ssh-topology.md` — cross-machine deployment context
