# Maat Memory PostgreSQL Backend

Maat Memory now supports PostgreSQL with pgvector for production-grade storage and semantic search.

## Features

- **PostgreSQL Storage**: All memory data stored in PostgreSQL tables
- **Vector Search**: Semantic search on conversations using pgvector
- **Automatic Schema**: Schema created automatically on first use
- **Migration Tool**: Migrate existing JSON data to PostgreSQL
- **Backward Compatible**: Falls back to JSON if PostgreSQL unavailable

## Setup

### 1. Ensure PostgreSQL with pgvector is running

```bash
# Check if PGVECTOR_DB_URL is set
echo $PGVECTOR_DB_URL

# Or check in .env file
cat /home/suspect/.n8n/open-webui/.env | grep PGVECTOR_DB_URL
```

### 2. Run Migration (Optional)

If you have existing JSON data, migrate it to PostgreSQL:

```bash
cd /home/suspect/.n8n/maatlangchain
python3 maat_memory/migrate_to_postgres.py
```

This will:
- Create PostgreSQL schema
- Migrate all sessions, conversations, audit trail, tasks, etc.
- Validate the migration
- Keep JSON file as backup

### 3. Use PostgreSQL Backend

The system automatically uses PostgreSQL if available:

```python
from maat_memory import MaatMemory

# Automatically uses PostgreSQL if PGVECTOR_DB_URL is set
memory = MaatMemory()

# Or explicitly use PostgreSQL
from maat_memory.memory_postgres import MaatMemoryPostgres
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
memory = MaatMemoryPostgres(embeddings_model=embeddings)
```

## Schema

The PostgreSQL schema includes:

- `maat_sessions`: Agent sessions
- `maat_conversations`: Conversations with vector embeddings
- `maat_audit_trail`: Audit log entries
- `maat_tasks`: Task tracking
- `maat_decisions`: Decision log
- `maat_changes`: File change history
- `maat_errors`: Error log
- `maat_learnings`: Learning/insight capture
- `maat_agent_memory`: Agent-specific memory
- `maat_metadata`: System metadata

## Vector Search

Conversations are automatically embedded using the configured embeddings model:

```python
# Search with vector similarity
results = memory.search_conversations(
    query="What did we decide about the API?",
    agent="cursor",
    limit=5,
    use_vector_search=True
)

for result in results:
    print(f"Similarity: {result['similarity']}")
    print(f"Query: {result['user_query']}")
    print(f"Response: {result['agent_response']}")
```

## Testing

Test the PostgreSQL backend:

```bash
cd /home/suspect/.n8n/maatlangchain
python3 maat_memory/test_postgres.py
```

## Environment Variables

- `MAAT_MEMORY_BACKEND`: Set to `"postgres"` (default) or `"json"` to force backend
- `PGVECTOR_DB_URL`: PostgreSQL connection string (required for PostgreSQL backend)

## Benefits Over JSON

1. **Scalability**: Handle millions of conversations
2. **Semantic Search**: Find conversations by meaning, not just keywords
3. **Concurrent Access**: Multiple agents can write simultaneously
4. **Data Integrity**: ACID transactions, foreign keys, constraints
5. **Query Performance**: Indexed queries, optimized for large datasets
6. **Backup/Recovery**: Standard PostgreSQL backup tools
7. **Multi-Computer Sync**: Single source of truth in database

## Migration Notes

- JSON file is kept as backup after migration
- Migration is idempotent (safe to run multiple times)
- Embeddings are generated on-demand during queries (not during migration)
- Use `generate_embedding=True` when logging conversations to enable vector search

