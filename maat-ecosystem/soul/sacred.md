# Sacred vs Replaceable

This is the line. If you cannot tell which side something falls on, it is replaceable.

## Sacred (lives in maat-core/schemas/ and doctrine docs)

- `maat_identity.schema.json` — agent identity format
- `maat_memory.schema.json` — memory entry format + 5 classes
- `maat_task.schema.json` — task lifecycle + 6 states
- `maat_policy.schema.json` — policy rules + 5 outcomes
- `maat_event.schema.json` — event structure + canonical taxonomy
- `maat_tool.schema.json` — tool contract shape
- `maat_learning.schema.json` — learning record + rollback

### Sacred Invariants

- Memory classes: episodic, semantic, constitutional, task, working
- Policy outcomes: allow, deny, escalate, require_approval, log
- Task states: pending, in_progress, completed, failed, blocked, escalated
- Three rings: inner-ring, middle-ring, outer-ring
- Constitutional memory: append-only, versioned, never silently overwritten
- Events: append-only log, structured, namespaced
- Learning: always reversible (except constitutional amendment)

## Replaceable (lives in maat-adapters/ and config)

- Model provider (Ollama, OpenAI, Anthropic, vLLM, Groq, local GGUF)
- Vector DB (pgvector, Qdrant, Chroma, Pinecone, none)
- SQL backend (PostgreSQL, SQLite, DuckDB)
- Tool transport (MCP, REST, gRPC, native Python, stdio)
- Embedding model (nomic, OpenAI, Cohere, any)
- CLI framework (argparse, Click, Typer)
- UI framework (Flask, React, htmx, terminal)
- Agent runtime engine (OpenClaw, LangChain, CrewAI, AutoGen, raw Python)
- Messaging transport (Telegram, Discord, WhatsApp, WebSocket)

## The Rule

If implementation details leak into the kernel → fix immediately.
If sacred things depend on a specific adapter → architecture violation.
If a replaceable thing stops being swappable → it leaked into sacred territory.
