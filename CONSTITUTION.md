# MAAT Constitution

> Not a repo. A constitutional ecology for evolving AI systems.

## What Is Sacred

These are permanent. They change only through formal amendment, never silently.

| Sacred | Why |
|--------|-----|
| Identity schema | An agent's identity must outlive any runtime |
| Memory class definitions | episodic, semantic, constitutional, task, working — these are the 5 |
| Policy semantics | allow, deny, escalate, require_approval, log — these are the 5 outcomes |
| Event taxonomy | Namespaced types (agent.*, memory.*, task.*, tool.*, policy.*, learning.*) |
| Task lifecycle states | pending → in_progress → completed/failed/blocked/escalated |
| Tool contract shape | id, name, description, parameters, required_ring, reversible |

## What Is Replaceable

Everything else. Specifically:

| Replaceable | Current Default | Alternatives |
|-------------|----------------|-------------|
| Model provider | Ollama/Gemma | OpenAI, Anthropic, vLLM, Groq, local GGUF |
| Vector DB | pgvector | Qdrant, Chroma, Pinecone, none |
| SQL backend | PostgreSQL | SQLite, DuckDB, any SQL |
| Tool transport | MCP | REST, gRPC, native Python, stdio |
| CLI framework | argparse | Click, Typer, none |
| UI framework | Flask (Studio) | React, htmx, terminal, none |
| Agent runtime | OpenClaw | LangChain, CrewAI, AutoGen, raw Python |

## The Line

If you cannot tell whether something is sacred or replaceable, it is replaceable.

Sacred things live in `maat-core/schemas/` and doctrine docs.
Everything else lives behind an adapter interface.

**If implementation details leak into the kernel, fix it immediately.**

## Amendment Process

Sacred contracts can be amended, never silently overwritten.

1. Propose amendment with rationale
2. Document what changes and why
3. Increment schema version
4. Old versions remain readable (backward compat)
5. Log amendment as `constitution.amended` event

This is how constitutions work. Not by deletion. By evolution.
