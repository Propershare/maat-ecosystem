# FastAPI Endpoints - Complete ✅

## Status
All FastAPI endpoints have been completed and tested.

## Available Endpoints

### Core Endpoints
- `GET /` - Root endpoint (API info)
- `GET /health` - Health check
- `GET /openapi.json` - OpenAPI spec for OpenWebUI

### RAG Endpoints
- `POST /rag/query` - Query the RAG system
- `GET /rag/chunks` - View chunks (with filters)
- `POST /rag/ingest_pdf` - Ingest PDF documents
- `GET /rag/stats` - Get RAG statistics
- `GET /rag/collections` - List all collections

## Usage Examples

### Query RAG
```bash
curl -X POST http://localhost:8019/rag/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Maat?", "top_k": 5}'
```

### View Chunks
```bash
curl "http://localhost:8019/rag/chunks?pdf_name=Africa%20and%20the%20Americas.pdf&limit=10&skip_toc=true"
```

### Get Stats
```bash
curl "http://localhost:8019/rag/stats?collection_name=maat_knowledge"
```

### List Collections
```bash
curl "http://localhost:8019/rag/collections"
```

### Ingest PDF
```bash
curl -X POST http://localhost:8019/rag/ingest_pdf \
  -H "Content-Type: application/json" \
  -d '{"pdf_path": "/path/to/file.pdf", "collection_name": "maat_knowledge"}'
```

## Start API
```bash
cd /home/suspect/.n8n/maatlangchain
python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8019
```

## Next Steps
- Integrate Maat Memory logging
- Add authentication (if needed)
- Connect to OpenWebUI as external tool
