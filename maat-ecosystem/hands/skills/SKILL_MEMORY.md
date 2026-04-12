# MAAT Memory — Full Reference

## Memory Classes

| Class | Use For | Reversible |
|-------|---------|-----------|
| `episodic` | Conversations, events, interactions | Yes |
| `semantic` | Facts, knowledge, domain info | Yes |
| `constitutional` | Identity, values, core beliefs | No |
| `task` | TODOs, decisions, plans | Yes |
| `working` | Current session only (expires) | Yes |

## Write

```python
from maat_adapters.memory.postgres import PostgresAdapter
import uuid
from datetime import datetime, timezone

mem = PostgresAdapter({})  # auto-resolves PGVECTOR_DB_URL

mem.write({
    "id": str(uuid.uuid4()),
    "agent_id": "tehuti",
    "memory_class": "semantic",
    "content": "The full content of what to remember",
    "summary": "Short summary (optional)",
    "source": "conversation/2026-04-06",
    "tags": ["architecture", "decision"],
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "reversible": True,
})
```

## Search

```python
results = mem.search(
    query="authentication decision",
    agent_id="tehuti",           # optional filter
    memory_class="task",          # optional filter
    limit=5,
)
for r in results:
    print(r["memory_class"], r["content"][:80])
```

## Delete (Rollback)

```python
mem.delete(memory_id)  # only works if reversible=True
```

## Fallback: SQLite (no Postgres)

```python
from maat_adapters.memory.sqlite import SQLiteAdapter
mem = SQLiteAdapter({"path": "~/.maat/memory.db"})
# Same API as Postgres
```
