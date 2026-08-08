# Knowledge Base Location

## Main Knowledge Base (MaatLangChain)

### PostgreSQL/pgvector (Production)
**Location**: PostgreSQL database with pgvector extension
**Connection**: Configured via `PGVECTOR_DB_URL`

**Tables**:
- `langchain_pg_collection`: Collections (knowledge bases)
- `langchain_pg_embedding`: Document chunks with embeddings

**Current Status**:
- ✅ **1 Collection**: `maat_knowledge`
- ✅ **2,444 Chunks**: Processed RBG Library PDFs and documents
- ✅ **Production Ready**: PostgreSQL with pgvector

**How to Access**:
```python
from core.integrations.tehuti_lab import TehutiLabIntegration

lab = TehutiLabIntegration()
vector_store = lab.get_vector_store()
# Use vector_store for RAG queries
```

**Query Examples**:
```python
# Search knowledge base
results = vector_store.similarity_search("your question", k=5)

# Get all chunks from a file
results = vector_store.similarity_search_with_score(
    "query",
    filter={"file_name": "Africa and the Americas.pdf"}
)
```

## OpenWebUI Knowledge (Separate)

### Local SQLite (OpenWebUI's own RAG)
**Location**: `/home/suspect/.n8n/open-webui/data/webui.db`

**Tables**:
- `knowledge`: OpenWebUI's knowledge entries (currently empty)
- `document`: Uploaded documents
- `knowledge_file`: Knowledge file references

**Status**: 
- ⚠️ Currently empty (0 knowledge entries)
- This is separate from MaatLangChain's PostgreSQL knowledge base

### Local ChromaDB (OpenWebUI)
**Location**: `/home/suspect/.n8n/open-webui/data/vector_db/chroma.sqlite3`

**Status**: 
- Small file (168KB)
- Likely empty or minimal data
- Used by OpenWebUI's built-in RAG features

## Old/Backup Knowledge

### Local ChromaDB (MaatLangChain backup)
**Location**: `/home/suspect/.n8n/chroma_db_maat/`

**Status**: 
- Old backup from before PostgreSQL migration
- 308KB size
- Not actively used (PostgreSQL is production)

## Summary

**Your main knowledge base is in PostgreSQL**:
- ✅ 2,444 processed chunks
- ✅ RBG Library PDFs
- ✅ Production-grade storage
- ✅ Accessible via MaatLangChain RAG API

**OpenWebUI's knowledge is separate**:
- Empty (0 entries)
- Used for OpenWebUI's own RAG features
- Not connected to MaatLangChain's PostgreSQL

## To Use the Knowledge

1. **Via MaatLangChain API**:
   ```bash
   curl -X POST http://localhost:8019/rag/query \
     -H "Content-Type: application/json" \
     -d '{"query": "your question", "collection_name": "maat_knowledge"}'
   ```

2. **Via Python**:
   ```python
   from core.chains.maat_rag import MaatRAG
   
   rag = MaatRAG()
   response = rag.query("your question", "maat_knowledge")
   ```

3. **View chunks**:
   ```bash
   python3 scripts/view_chunks.py --list
   python3 scripts/view_chunks.py --pdf "Africa and the Americas.pdf"
   ```

## Connection String

The PostgreSQL connection is configured in:
- Environment variable: `PGVECTOR_DB_URL`
- Or: `/home/suspect/.n8n/open-webui/.env`

Format: `postgresql://user:password@host:port/database`

