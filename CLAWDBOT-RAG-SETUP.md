# Clawdbot RAG & Dataset Access - Setup Complete ✅

## What Was Created

### 1. RAG Search Script
**File**: `/home/suspect/.n8n/scripts/search-rag-clawdbot.py`
- Searches UKMT RAG knowledge base using MaatMemory
- Uses PostgreSQL + pgvector for semantic search
- Returns formatted JSON results

### 2. n8n Workflows Created

#### Workflow 1: RAG Search
**File**: `/home/suspect/.n8n/n8n-workflows/clawdbot-rag-search.json`
- **Webhook**: `http://192.168.4.21:5678/webhook/rag-search`
- **Purpose**: Search UKMT research knowledge base
- **Status**: Imported and activated ✅

#### Workflow 2: Dataset Query
**File**: `/home/suspect/.n8n/n8n-workflows/clawdbot-dataset-query.json`
- **Webhook**: `http://192.168.4.21:5678/webhook/dataset-query`
- **Purpose**: Query datasets via RAG search
- **Status**: Imported and activated ✅

## Clawdbot Configuration

Add these hooks to `~/.clawdbot/clawdbot.json`:

```json
{
  "hooks": {
    "mappings": {
      "ai-employee": {
        "url": "http://192.168.4.21:5678/webhook/ai-employee",
        "method": "POST"
      },
      "rag-search": {
        "url": "http://192.168.4.21:5678/webhook/rag-search",
        "method": "POST",
        "headers": {
          "Content-Type": "application/json"
        }
      },
      "dataset-query": {
        "url": "http://192.168.4.21:5678/webhook/dataset-query",
        "method": "POST",
        "headers": {
          "Content-Type": "application/json"
        }
      }
    }
  }
}
```

## Usage via WhatsApp

### RAG Search Commands:
- "Search UKMT research on [topic]"
- "RAG search: [query]"
- "Search knowledge base: [query]"

### Dataset Query Commands:
- "Query dataset for [query]"
- "Search dataset: [query]"
- "Dataset query: [query] [dataset_name]"

## What Clawdbot Can Now Access

✅ **UKMT RAG Knowledge Base**
- Semantic search over UKMT research content
- PostgreSQL + pgvector powered
- Returns relevant research documents

✅ **Your Datasets**
- Query datasets via RAG search
- Filter by dataset name
- Semantic search across all datasets

✅ **MaatLangChain Integration**
- Uses `maatlangchain-pipeline` MCP server
- Connects to MaatMemory for RAG queries
- Follows Maat principles

## Testing

### Test RAG Search:
```bash
curl -X POST "http://192.168.4.21:5678/webhook/rag-search" \
  -H "Content-Type: application/json" \
  -d '{"query": "UKMT research", "limit": 5}'
```

### Test Dataset Query:
```bash
curl -X POST "http://192.168.4.21:5678/webhook/dataset-query" \
  -H "Content-Type: application/json" \
  -d '{"query": "test query", "dataset": "all"}'
```

## Integration Points

- **MCP Server**: `maatlangchain-pipeline` (port 8020/8026)
- **Database**: PostgreSQL + pgvector (`maat_memory` database)
- **RAG System**: MaatLangChain RAG with semantic search
- **Knowledge Base**: UKMT research content stored in vector database

## Next Steps

1. ✅ Scripts created
2. ✅ Workflows imported
3. ✅ Workflows activated
4. ⏳ Configure Clawdbot hooks (add rag-search and dataset-query mappings)
5. ⏳ Test via WhatsApp

Once hooks are configured, Clawdbot will have full access to your UKMT RAG and datasets!
