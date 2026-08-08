# Canon RAG Integration Guide

## Overview

The canon knowledge base (130+ markdown files in `docs/canon/`) has been integrated into the RAG system, enabling semantic search across all canon documents. This allows the AI assistant to provide accurate, canon-based responses with source citations.

## Architecture

```
Canon MD Files → DocumentProcessor → Chunking → Embeddings → Vector Store → canon_kmt Collection
                                                                                    ↓
User Query → RAG Query Helper → Semantic Search → Top-K Documents → LLM Answer + Sources
```

## Collection Details

- **Collection Name**: `canon_kmt`
- **Source**: `/home/suspect/.n8n/maatlangchain/docs/canon/`
- **File Type**: Markdown (`.md`)
- **Total Files**: 130+ files
- **Content**: KMT chronology, research methodologies, historical analysis, philosophical frameworks, etc.

## Ingestion

### Running Ingestion

To ingest all canon files into the RAG system:

```bash
cd /home/suspect/.n8n/maatlangchain
python3 scripts/ingest_canon_to_rag.py
```

### Ingestion Process

1. **Find Files**: Recursively finds all `.md` files in `docs/canon/`
2. **Load**: Uses `DocumentProcessor.load_markdown()` to load each file
3. **Chunk**: Splits documents into chunks (adaptive sizing based on content)
4. **Embed**: Generates embeddings for all chunks (batch processing)
5. **Store**: Stores chunks in `canon_kmt` collection in PostgreSQL vector store

### Ingestion Output

- **Log File**: `canon_ingestion.log` (in maatlangchain root)
- **Summary**: `canon_ingestion_summary.json` (in maatlangchain root)
- **Results**: `canon_ingestion_results_YYYYMMDD_HHMMSS.json` (detailed per-file results)

### Ingestion Metadata

Each document chunk includes:
- `file_name`: Original markdown filename
- `file_type`: "markdown"
- `source`: "canon"
- `title`: Extracted from first heading (if available)
- `file_path`: Full path to source file
- `processed_date`: ISO timestamp
- `extraction_method`: "text_loader"

## Querying Canon via RAG

### Using RAG Query Helper

The `rag_query_helper` module provides easy-to-use functions for querying canon:

```python
from core.utils.rag_query_helper import query_canon_rag, search_canon_similar, get_canon_context

# Full RAG query with LLM answer
result = query_canon_rag(
    question="What is the K2 methodology?",
    top_k=5
)

# Returns:
# {
#     "answer": "LLM-generated answer based on canon...",
#     "sources": [
#         {
#             "file_name": "21_KAZ_Methodology.md",
#             "page": 0,
#             "preview": "...",
#             "confidence": 0.85
#         },
#         ...
#     ],
#     "confidence": "high",
#     "metadata": {...}
# }

# Search for similar documents (no LLM)
documents = search_canon_similar(
    query="KMT chronology",
    top_k=10
)

# Get formatted context for AI assistant
context = get_canon_context(
    question="What are the stages of KMT development?",
    max_chars=2000
)
```

### Using RAG API Endpoint

You can also query via the FastAPI endpoint:

```bash
curl -X POST "http://localhost:8000/rag/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the K2 methodology?",
    "collection_name": "canon_kmt",
    "top_k": 5
  }'
```

## Integration with AI Assistant

### Automatic Canon Queries

The AI assistant can now query canon knowledge automatically:

1. **Import Helper**:
   ```python
   from core.utils.rag_query_helper import query_canon_rag
   ```

2. **Query Before Responding**:
   ```python
   # When user asks canon-related question
   canon_result = query_canon_rag(user_question, top_k=5)
   
   # Use result in response
   answer = canon_result["answer"]
   sources = canon_result["sources"]
   ```

3. **Include Sources**:
   Always cite sources from canon when using canon knowledge in responses.

### Example Integration

```python
def respond_with_canon_context(user_question: str) -> str:
    """Generate response with canon context."""
    from core.utils.rag_query_helper import query_canon_rag
    
    # Query canon
    canon_result = query_canon_rag(user_question, top_k=5)
    
    if canon_result["confidence"] != "error":
        # Build response with sources
        response = canon_result["answer"]
        response += "\n\n**Sources:**\n"
        for source in canon_result["sources"]:
            response += f"- {source['file_name']}\n"
        return response
    else:
        return "Unable to query canon knowledge base."
```

## File Structure

```
maatlangchain/
├── docs/
│   └── canon/                    # Source markdown files
│       ├── 01_United_States_Societal_Anatomy.md
│       ├── 21_KAZ_Methodology.md
│       ├── 23_KMT_Chronology_Eurocentric_vs_Scientific_African.md
│       └── ... (130+ files)
├── scripts/
│   └── ingest_canon_to_rag.py    # Ingestion script
├── core/
│   ├── chains/
│   │   └── document_processor.py  # Extended with load_markdown()
│   └── utils/
│       └── rag_query_helper.py   # Query helper functions
└── docs/
    └── CANON_RAG_INTEGRATION.md  # This file
```

## Troubleshooting

### Database Connection Issues

If ingestion fails with database connection errors:
1. Check `PGVECTOR_DB_URL` in `/home/suspect/.n8n/tehuti-lab-webui/.env`
2. Verify PostgreSQL is running
3. Ensure pgvector extension is installed

### Empty Results

If queries return no results:
1. Verify ingestion completed successfully (check `canon_ingestion_summary.json`)
2. Check collection name is `canon_kmt`
3. Verify files were actually ingested (check log file)

### Import Errors

If `rag_query_helper` import fails:
1. Ensure you're in the maatlangchain directory
2. Check Python path includes maatlangchain root
3. Verify `api.main` can be imported

## Best Practices

1. **Always Cite Sources**: When using canon knowledge, cite the source files
2. **Check Confidence**: Use confidence levels to determine answer quality
3. **Use Appropriate top_k**: Adjust `top_k` based on query complexity (3-10 typical)
4. **Handle Errors**: Always handle errors gracefully when querying RAG
5. **Log Queries**: Log canon queries for debugging and improvement

## Future Enhancements

- [ ] Add metadata filtering (e.g., query only specific categories)
- [ ] Implement query caching for common questions
- [ ] Add query analytics and usage tracking
- [ ] Support for updating individual files without full re-ingestion
- [ ] Integration with Maat Memory for query logging

## Related Documentation

- [RAG System Documentation](../API-DOCUMENTATION.md)
- [Document Processor](../core/chains/document_processor.py)
- [MaatRAG Implementation](../core/chains/maat_rag.py)

