# Maat workspace audit (operator)

**Purpose:** One honest snapshot of what was broken vs what is canonical—no new product layers.

## Fixed (2026-04)

| Issue | Fix |
|-------|-----|
| Missing **`core/chains/maat_rag.py`** | Restored **`MaatRAG`** (search, store, query, stats) — tests `tests/unit/test_maat_rag.py` pass. |
| **`main_original.py`** referenced **`MaatMemory`** without import | **Lazy-import** inside `get_maat_memory()`; `Optional[Any]` for global. |
| **`rag_query_helper`** imports **`api.main`** but no **`main.py`** | Added **`maatlangchain/api/main.py`** re-exporting **`app`**, **`get_rag_instance`** from **`main_original`**. |

## Two `maat-ecosystem` trees on disk

See **`docs/MAAT-ECOSYSTEM-TWO-HOMES.md`**. **`~/.n8n/maat-ecosystem/`** is the lab spine (includes **`mcp-servers/`**). **`~/maat-ecosystem/`** is a second checkout—do not edit both blindly.

## AGENTS.md “Maat Core”

The **central `maat/authority/`** folder described historically is **not** a separate shipped package today; policy is **`tehuti-guard/`** at **`POST /decision`** (`:8013`). Prefer **`maat_core/`** for schemas and **`maatlangchain/maat_memory/`** for gitMaat until a single `maat` facade is explicitly designed (avoid duplicate `maat` Python package names vs **`maat-framework`**).

## What to run

```bash
cd /home/suspect/.n8n/maatlangchain && python -m pytest tests/unit/test_maat_rag.py -q
```

**End-to-end RAG (DB + embed + write + read):**

```bash
cd /home/suspect/.n8n && python3 scripts/rag_smoke_test.py
```

Expect `PASS:` when Postgres has `pgvector` and `PGVECTOR_DB_URL` is set (or `.env` at lab root).
