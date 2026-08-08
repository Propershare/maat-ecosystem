# MaatLangChain FastAPI Documentation

## Overview
The MaatLangChain FastAPI server provides REST endpoints for querying and managing the RAG (Retrieval-Augmented Generation) system with Maat governance principles.

## Starting the Server
```bash
cd /home/suspect/.n8n/maatlangchain
python3 api/main.py
```
Server runs on `http://localhost:8019`

## Endpoints

### Health & Status

#### GET `/health`
Check API health and database connection.
```json
{
  "status": "healthy",
  "database_connected": true,
  "embeddings_ready": true,
  "timestamp": "2025-12-21 02:05:00",
  "version": "1.0.0"
}
```

#### GET `/`
Basic server info.
```json
{
  "name": "MaatLangChain RAG API",
  "version": "1.0.0", 
  "status": "running"
}
```

### RAG Operations

#### POST `/rag/query`
Ask questions to the RAG system.

**Request:**
```json
{
  "question": "What is Maat?",
  "top_k": 5,
  "collection_name": "maat_knowledge",
  "min_score": 0.0
}
```

**Response:**
```json
{
  "answer": "Maat is the ancient Egyptian concept of truth, balance, order, harmony, law, morality, and justice...",
  "sources": [
    {
      "file_name": "Ancient Egypt.pdf",
      "page": 45,
      "preview": "Maat represents the cosmic order and divine truth...",
      "score": 0.89
    }
  ],
  "metadata": {
    "question": "What is Maat?",
    "top_k": 5,
    "sources_found": 3,
    "collection_name": "maat_knowledge"
  },
  "query_time": 0.234
}
```

#### POST `/rag/chunks`
View document chunks from the vector store.

**Request:**
```json
{
  "pdf_name": "Africa and the Americas.pdf",
  "limit": 10,
  "skip_toc": true
}
```

**Response:**
```json
{
  "chunks": [
    {
      "chunk_id": "chunk_0",
      "content": "Full chunk content...",
      "pdf_name": "Africa and the Americas.pdf", 
      "page": 25,
      "metadata": {...},
      "preview": "Preview of chunk..."
    }
  ],
  "total_count": 2444,
  "filtered_count": 2444,
  "metadata": {
    "filters": {...},
    "query_executed": "SELECT document, cmetadata FROM..."
  }
}
```

### Document Management

#### POST `/rag/ingest_pdf`
Process and ingest a PDF into the RAG system.

**Request:**
```json
{
  "pdf_path": "/path/to/document.pdf",
  "collection_name": "my_collection",
  "chunk_size": 1000,
  "chunk_overlap": 200,
  "skip_front_pages": 5
}
```

**Response:**
```json
{
  "status": "success",
  "message": "PDF document.pdf ingested successfully",
  "pdf_name": "document.pdf",
  "chunks_created": 45,
  "processing_time": 12.3,
  "error_details": null
}
```

#### GET `/rag/stats`
Get statistics about collections.

**Query Parameters:**
- `collection_name`: Collection name (default: "maat_knowledge")

**Response:**
```json
{
  "collection": "maat_knowledge",
  "status": "active",
  "total_chunks": 2444,
  "total_pdfs": 15,
  "chunk_stats": {
    "avg_length": 1250,
    "min_length": 200,
    "max_length": 2500
  },
  "top_pdfs": [
    {"name": "Africa and the Americas.pdf", "chunks": 2444}
  ]
}
```

#### GET `/rag/collections`
List all available collections.

**Response:**
```json
{
  "collections": [
    {
      "name": "maat_knowledge",
      "uuid": "12345-...",
      "chunk_count": 2444,
      "metadata": {...}
    }
  ],
  "count": 1
}
```

### OpenAPI Integration

#### GET `/openapi.json`
Returns the OpenAPI specification for tool server integration with OpenWebUI.

## Error Handling
All endpoints return appropriate HTTP status codes:
- `200`: Success
- `400`: Bad Request (e.g., invalid PDF path)
- `404`: Not Found (e.g., PDF doesn't exist)
- `500`: Server Error (e.g., database connection issues)

## Maat Principles Integration
- **Truth**: All responses include source citations
- **Balance**: Query results are ranked by relevance
- **Order**: Chunks are processed systematically
- **Self-Reflection**: Performance metrics are tracked

## Testing with curl

```bash
# Health check
curl http://localhost:8019/health

# Query RAG
curl -X POST http://localhost:8019/rag/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Maat?", "top_k": 3}'

# View chunks
curl -X POST http://localhost:8019/rag/chunks \
  -H "Content-Type: application/json" \
  -d '{"limit": 5, "skip_toc": true}'

# Get stats
curl "http://localhost:8019/rag/stats?collection_name=maat_knowledge"
```

## Integration with OpenWebUI
The API provides OpenAPI specification at `/openapi.json` for easy integration with OpenWebUI as a tool server.