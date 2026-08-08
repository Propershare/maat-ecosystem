# Architecture

## Design Principles

1. **One command** — `maat start` brings everything up
2. **No duplicated state** — gitMaat is the single source of truth
3. **Fail-closed security** — unknown agents get read-only access
4. **Plug-and-play tools** — MCP servers drop in, `maat adapt` picks them up
5. **Local-first** — everything runs on your machine, no cloud required

## Component Map

```
maat/
├── cli.py      → Entry point. Parses commands, delegates.
├── config.py   → Loads ~/.maat/config.yaml. Dot-path get/set.
├── adapt.py    → Probes system (Ollama, MCP, Postgres). Auto-configures.
├── learn.py    → Reads/writes gitMaat (Postgres + pgvector). Memory layer.
├── guard.py    → Three-Ring access control + command scanning. Security.
├── agent.py    → Conversation loop. Ties model + memory + tools together.
└── tools.py    → MCP client + custom tool registration (future).
```

## Data Flow

```
User speaks
    │
    ▼
agent.py receives message
    │
    ├──► learn.py: query_memory("relevant context")
    │       └──► Postgres: SELECT from maat_conversations WHERE ILIKE
    │
    ├──► guard.py: check_access(agent, action)
    │       └──► Three-Ring: is this agent allowed?
    │
    ├──► _build_system_prompt(config, memory_context)
    │       └──► Minimal prompt + injected memory
    │
    ├──► _call_ollama(prompt, model, system)
    │       └──► Ollama: /api/chat → response
    │
    ├──► learn.py: log_conversation(query, response)
    │       └──► Postgres: INSERT into maat_conversations
    │
    └──► Return response to user
```

## Why These Choices

### gitMaat over flat files
Flat file memory (MEMORY.md) gets injected into every API call. At 280k chars,
that's thousands of tokens burned just to say hello. Postgres + pgvector lets
us query for relevant context only — targeted retrieval, not bulk injection.

### Three-Ring over RBAC
Traditional role-based access is complex. Three rings is simple: inner (read),
middle (read + propose), outer (full). You can explain it to anyone in 10 seconds.

### MCP over custom APIs
MCP is becoming the standard protocol for AI tool access. Any MCP server works
with any MCP client. We don't invent our own protocol.

### Ollama over cloud APIs
Sovereignty. Your data stays on your machine. Your model runs locally.
Cloud APIs are supported but not the default.

### Single agent over swarm
A "swarm" of keyword-routed models is just a fancy if/else. One good model
with good memory and tools beats three specialized models with no context.
The swarm pattern can be added later as a router inside agent.py.
```

## Adding a New Component

1. Create `maat/newcomponent.py`
2. Add a CLI command in `maat/cli.py`
3. Import where needed
4. Write a test in `tests/test_newcomponent.py`
5. Update this doc
