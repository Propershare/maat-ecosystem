# maat-memory-client

Zero-config Python client for **Maat Memory** (shared organ on `:8022`).

```bash
pip install ./maat-memory-client
maat-memory-client doctor
```

```python
from maat_memory_client import MaatMemoryClient

memory = MaatMemoryClient()  # auto-discovers endpoint + agent id
memory.remember("User prefers source-grounded answers.", tags=["preference"])
results = memory.recall("user preferences")
```

See [../docs/MAAT-MEMORY-ADOPTION.md](../docs/MAAT-MEMORY-ADOPTION.md).
