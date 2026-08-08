# OpenCode Quick Start - Cross-Terminal Memory

## 5-Minute Setup

### 1. Install Dependencies

```bash
cd /mnt/ai_backup/tehuti-memory
pip install psycopg2-binary pgvector langchain-huggingface sentence-transformers
```

### 2. Update Your MCP Server

**Replace this in `core/maat_memory_server.py`:**

```python
# OLD (file-based, no cross-terminal memory)
self.sessions: Dict[str, Dict[str, Any]] = {}

# NEW (PostgreSQL, cross-terminal memory)
import sys
sys.path.insert(0, "/home/suspect/.n8n/maatlangchain")
from maat_memory.memory_postgres import MaatMemoryPostgres
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
self.memory = MaatMemoryPostgres(embeddings_model=embeddings)
```

### 3. Update `save_session` Method

**Replace:**
```python
self.sessions[session_id] = session
```

**With:**
```python
session_id = self.memory.start_session(
    agent=agent_id,
    summary=session_data.get("summary", "")
)

# Log conversation with vector search
if "user_query" in session_data:
    self.memory.log_conversation(
        agent=agent_id,
        user_query=session_data["user_query"],
        agent_response=session_data["agent_response"],
        generate_embedding=True  # Enable semantic search!
    )
```

### 4. Update `search_sessions` Method

**Replace:**
```python
# Simple text search
if query.lower() in session_text:
    matching_sessions.append(session)
```

**With:**
```python
# Vector semantic search
results = self.memory.search_conversations(
    query=query,
    agent=agent_id,
    limit=10,
    use_vector_search=True  # Semantic search!
)
return {"sessions": results, "count": len(results)}
```

### 5. Test Cross-Terminal Memory

**Terminal 1:**
```bash
python3 -c "
import sys
sys.path.insert(0, '/home/suspect/.n8n/maatlangchain')
from maat_memory.memory_postgres import MaatMemoryPostgres
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
memory = MaatMemoryPostgres(embeddings_model=embeddings)

session_id = memory.start_session('opencode', 'Test from Terminal 1')
memory.log_conversation('opencode', 'What is Maat?', 'Maat is truth and balance.')
print(f'Session {session_id} saved')
"
```

**Terminal 2 (different terminal):**
```bash
python3 -c "
import sys
sys.path.insert(0, '/home/suspect/.n8n/maatlangchain')
from maat_memory.memory_postgres import MaatMemoryPostgres
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
memory = MaatMemoryPostgres(embeddings_model=embeddings)

results = memory.search_conversations('Maat', agent='opencode', limit=5)
print(f'Found {len(results)} conversations from Terminal 1!')
"
```

**Result:** ✅ Terminal 2 sees conversations from Terminal 1!

---

## What You Get

- ✅ **Cross-Terminal Memory**: All terminals share PostgreSQL database
- ✅ **Vector Search**: Semantic queries (find by meaning, not keywords)
- ✅ **No Data Loss**: PostgreSQL persistence (survives restarts)
- ✅ **Constitutional Governance**: Keep your validator, use our storage

---

## Full Integration Guide

See: `/home/suspect/.n8n/maatlangchain/maat_memory/OPencode-INTEGRATION-GUIDE.md`

---

## Architecture

```
OpenCode MCP Server (Your Code)
    ↓ uses
MaatMemoryPostgres (Our Backend)
    ↓ stores in
PostgreSQL Database (Shared across terminals)
```

**Result:** Cross-terminal memory guaranteed! 🎯

