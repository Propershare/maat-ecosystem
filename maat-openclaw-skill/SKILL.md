---
name: maat
description: Connect to the MAAT ecosystem from OpenClaw. Use when an agent needs persistent memory (query or write to gitMaat), policy enforcement (Three-Ring), task lifecycle management, or tool dispatch via the MAAT kernel. Also use when asked to "remember" something long-term, check what tasks exist, or log a decision/learning/change.
---

# MAAT Ecosystem Skill

Connects OpenClaw agents to the MAAT Protocol: memory, policy, tasks, events, tools.

## Quick Reference

```python
import sys
sys.path.insert(0, "/home/suspect/.n8n/maat-ecosystem")

from maat_core.kernel.kernel import MaatKernel
from maat_core.kernel.policy import PolicyEngine
```

## Config

Default config path: `~/.maat/config.yaml`
Default identity store: `~/.maat/identities.json`
DB URL: `PGVECTOR_DB_URL` env var or in config

## Memory Operations

```python
# Read memory (read SKILL_MEMORY.md for full API)
from maat_adapters.memory.postgres import PostgresAdapter
mem = PostgresAdapter({"url": ""})  # auto-resolves DB URL
results = mem.search("what did we decide about auth?", limit=5)

# Write memory
mem.write({
    "id": str(uuid.uuid4()),
    "agent_id": "tehuti",
    "memory_class": "episodic",   # episodic|semantic|constitutional|task|working
    "content": "Decided to use REST over GraphQL for simplicity",
    "timestamp": datetime.now(timezone.utc).isoformat(),
})
```

Memory classes:
- `episodic` — past events, conversations
- `semantic` — facts, knowledge
- `constitutional` — identity, values (non-reversible)
- `task` — todos, decisions
- `working` — current session only

## Policy / Security

```python
from maat_core.kernel.policy import PolicyEngine
policy = PolicyEngine()
policy.register_agent("tehuti", "outer-ring")
result = policy.evaluate("tehuti", "execute", "/bin/backup.sh")
# {"allowed": True, "reason": "...", "policy_id": None}
```

Rings: `inner-ring` (read) → `middle-ring` (read+propose) → `outer-ring` (full)

## Task Management

```python
kernel = MaatKernel(config)
task = kernel.create_task("tehuti-id", "Deploy v2", loop_mode="on-the-loop")
kernel.update_task(task, "completed")
```

## Event Subscription

```python
def on_memory_write(event):
    print(f"Memory written by {event['payload']['agent_id']}")

kernel.events.subscribe("memory.written", on_memory_write)
kernel.events.subscribe("*", lambda e: print(e["type"]))  # all events
```

## Adapter Swap

To switch model or memory backend — edit `~/.maat/config.yaml`:
```yaml
adapters:
  model: maat_adapters.models.openai_compat.OpenAICompatAdapter
  memory: maat_adapters.memory.sqlite.SQLiteAdapter
```
No kernel restart required for hot-swap via `kernel.adapters.swap_model(new_adapter)`.

## See Also

- `SKILL_MEMORY.md` — full memory API
- `SKILL_POLICY.md` — policy rules and examples
- `/home/suspect/.n8n/maat-ecosystem/maat-core/schemas/` — all MAAT schemas
