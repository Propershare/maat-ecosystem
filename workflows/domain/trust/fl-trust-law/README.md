# fl-trust-law — Florida Trust Law RAG (Active)

**Status:** Active (promoted from test payload 2026-05-09)  
**Pack:** `data/retrieval_packs/fl-trust-law`  
**Gateway:** `fl-trust-law` (registry.yaml)  
**MCP Tool:** `query_florida_trust_law` (Tehuti Core `:8014`)

## Corpus

- 2,462 chunks from 39 source files (949KB text)
- FL Statutes Ch. 731-736 (Probate Code, Trusts, Nonprobate Property)
- FL Court Rules (Civil 12.01, Probate 5.010)
- 30+ FL case law opinions

## Index

- FAISS cosine-similarity, 7.3MB, 768-dim (`nomic-embed-text`, Ollama)
- Located at: `data/retrieval_packs/fl-trust-law/documents/rag/indexes/primary/index.faiss`

## Guardrails

- Scope check: only Florida trust/probate law queries answered
- Out-of-scope queries get RBL flag
- Research/citation only — no legal advice
- Tehuti Guard three-ring governance pending (see TODO below)

## Access

```bash
# CLI
python3 data/retrieval_packs/fl-trust-law/scripts/query_rag.py "homestead exemption" --top-k 5

# MCP
query_florida_trust_law(query="homestead exemption", top_k=5)
```

## TODO

- [ ] Tehuti Guard three-ring governance for legal queries (ring classification, policy checks)
- [ ] Maatbench regression test suite for common query patterns
- [ ] Corpus refresh pipeline (detect statute updates, re-index)
- [ ] Gateway allowlist review for non-dev access
