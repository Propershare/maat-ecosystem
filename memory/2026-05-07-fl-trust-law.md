# Florida Trust Law RAG — Session 2026-05-07 (activation)

## Status: Test payload → Active (RAG query available)

### What was done
1. **Rebuilt FAISS index** with `nomic-embed-text` (768-dim, Ollama)
   - 2462 chunks from 39 source files (949KB of text)
   - Covers FL Statutes (731-736), FL Court Rules, FL Case Law (30+ opinions)
   - Saved to `documents/rag/indexes/primary/index.faiss`
   - Chunks saved to `documents/rag/chunks/chunks.jsonl`

2. **RAG Query CLI** — `scripts/query_rag.py`
   - Works with real semantic embeddings via Ollama
   - Scope check: blocks out-of-scope queries (California, divorce, criminal, etc.)
   - Returns similarity-scored results with section/source metadata
   - Example: `"fiduciary duties"` → hits Fla. Stat. §736.1001, case law on trustee accounting
   - Tested and confirmed working

3. **Tehuti Core MCP** — added `query_florida_trust_law` tool
   - Wraps the RAG CLI as an MCP tool
   - Available when gateway runs with Tehuti Core connected
   - Parameters: query, top_k, threshold, as_json

4. **Gateway registry updated** — `fl-trust-law` tool allowlist:
   - `query_gitmaat`, `query_florida_trust_law`, `read_file`, `search_files`, `read_multiple_files`
   - `log_gitmaat_task`, `log_gitmaat_change`, `log_gitmaat_decision`, `log_gitmaat_learning`

### Key files
- `data/retrieval_packs/fl-trust-law/scripts/query_rag.py` — RAG query CLI
- `data/retrieval_packs/fl-trust-law/scripts/build_index.py` — rebuild index tool
- `data/retrieval_packs/fl-trust-law/documents/rag/chunks/chunks.jsonl` — chunk metadata (2462)
- `data/retrieval_packs/fl-trust-law/documents/rag/indexes/primary/index.faiss` — FAISS index
- `data/retrieval_packs/fl-trust-law/manifest.json` — updated with build metadata
- `mcp-servers/tehuti-core/tehuti_core_server.py` — added `query_florida_trust_law` tool
- `maat-ecosystem/skeleton/gateways/registry.yaml` — updated `fl-trust-law` tool allowlist

### What's NOT done yet
- gitMaat integration for persistent memory (tools exist in Tehuti Core but not wired for fl-trust-law queries)
- OpenClaw preset for fl-trust-law (currently shares ka2-research preset)
- Tehuti Guard three-ring governance for legal queries
- Promotion from staging to active domain

### Notes
- Embedding model: `nomic-embed-text` via Ollama (768-dim)
- Index is cosine-similarity via FAISS inner product on L2-normalized vectors
- Scope drift detection: checks for non-Florida/non-trust signals
- Legal advice warning: built into scope check (blocks non-scope queries)
- No n8n workflow (per user constraint: "we are not using n8n")
