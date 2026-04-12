# Memory Adapters — Swappable Backends

Drop a new adapter file here. Point `banks.yaml` at it. Restart. Done.

## Interface

Every adapter must implement:

```python
class MemoryAdapter:
    def connect(config: dict) -> None
    def store(collection: str, data: dict) -> str
    def retrieve(collection: str, id: str) -> dict
    def search(collection: str, query: str, limit: int) -> list
    def health() -> dict         # {status, latency_ms, capacity_pct}
    def stats() -> dict          # {total_entries, size_bytes, ...}
    def close() -> None
```

## Available Adapters

| File | Backend | Best For |
|------|---------|----------|
| `postgres.py` | PostgreSQL + pgvector | Production, semantic search |
| `sqlite.py` | SQLite | Dev, edge devices, portable archives |

## Adding a New Adapter

1. Create `your_backend.py` in this folder
2. Implement the interface above
3. Add entry to `../banks.yaml` under `adapters:`
4. Point a bank to use it
5. Restart the memory organ

The memory organ doesn't care what's behind the adapter. It stores and retrieves. The adapter handles the how.
