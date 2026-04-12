# MAAT Ecosystem

**Canonical Ka-body in the Tehuti Lab monorepo.** If the repo root also contains a legacy standalone layout (`maatbench/`, `maat-core/` at root), treat **`maat-ecosystem/`** here as **one truth** for organs, `MANIFEST.ka`, and current MaatBench — see [`../README.md`](../README.md) and [`../archive/README.md`](../archive/README.md).

**Ka Architecture — Bodies, not machines. Souls, not configs.**

A Kemetic framework for building living intelligent systems with moral governance at their core. Every agent is a body with nine organs, a soul that boots first, and an immune system that heals itself.

## Quick Start

```bash
# Discover the body (replace staydangerous with your host — see MANIFEST.ka network:)
curl http://staydangerous:8010/manifest

# Check all organ health
curl http://staydangerous:8010/health

# Connect to memory
curl -H "Authorization: Bearer $KA_API_KEY" http://staydangerous:8022/docs
```

Requires a running **Ka discovery** service on `:8010` when using those URLs; the reference body may not ship the daemon yet — see `docs/ka-audit-2026-04-06.md`.

## Constitutional core (MAAT Core)

Sacred contracts and doctrine — **not** MCP transport, not client UIs:

- **Schemas:** `skeleton/schemas/` (`*.schema.json` — event, task, memory, policy, tool, identity, learning)
- **Soul:** `soul/` — start with `constitution.md`
- **Bench contracts:** `maatbench/contracts/`
- **Programmatic paths (monorepo):** Python package [`maat_core/`](../maat_core/) at workspace root — `import maat_core` → `SCHEMAS_DIR`, `SOUL_DIR`, `list_schema_paths()`, etc.
- **Full framework map:** [`docs/MAAT-FRAMEWORK-REPORT.md`](../docs/MAAT-FRAMEWORK-REPORT.md) (layers, as-is vs to-be, Tranche 1 changelog)

## The Body

```
maat-ecosystem/
├── MANIFEST.ka           ← DNA — machine-readable body map
├── soul/                 ← Identity, constitution, governance
│   ├── constitution.md   ← The 42 Laws (boots first)
│   ├── identity.yaml     ← Who this body is
│   ├── sacred.md         ← Immutable principles
│   ├── policy.py         ← Policy enforcement
│   └── policies/         ← Behavioral rule sets
├── brain/                ← Reasoning, models, learning
│   ├── reasoning/        ← Core decision engine
│   ├── models/           ← LLM adapters (Ollama, OpenAI)
│   ├── learning/         ← What the system has learned
│   └── config.yaml       ← Runtime configuration
├── memory/               ← Persistence, recall, patterns
│   ├── episodic/         ← What happened (events, conversations)
│   ├── semantic/         ← What I know (facts, relationships)
│   ├── patterns/         ← What I've noticed (recurring themes)
│   └── task/             ← What I'm doing (active work)
├── hands/                ← Action, tool use, interaction
│   ├── tools/            ← Individual tool definitions
│   ├── skills/           ← Composed multi-tool capabilities
│   ├── mcps/             ← MCP server connections
│   └── apps/             ← Full workflow apps
│       ├── operator/
│       ├── receptionist/
│       ├── researcher/
│       └── teacher/
├── senses/               ← Perception, events, triggers
├── voice/                ← Communication, output, UI
├── ka/                   ← Health monitoring, self-healing
│   ├── health/           ← Current state of every organ
│   ├── healing/          ← Auto-retry, fallback rules
│   ├── pain/             ← Error patterns
│   └── pulse.yaml        ← Heartbeat configuration
├── skeleton/             ← Structure, contracts
│   └── schemas/          ← 7 JSON schemas
├── blood/                ← Inter-organ communication
│   ├── events/           ← Event bus definitions
│   ├── state/            ← Shared state
│   └── packs/            ← Shareable extensions
│       ├── agent-packs/
│       ├── policy-packs/
│       ├── tool-packs/
│       └── learning-packs/
├── maatbench/            ← The doctor (tests bodies)
├── maat-cli/             ← Command line interface
├── docs/                 ← Documentation
│   ├── architecture.md
│   ├── ka-architecture-paper.md
│   ├── ka-audit-2026-04-06.md
│   └── UI-SPEC.md
└── site/                 ← Public website
```

## Boot Sequence

Ka bodies are born, not deployed:

1. **Read constitution** — know your laws (soul loads first)
2. **Load identity** — know who you are
3. **Restore memory** — know what you remember
4. **Check health** — are all organs alive
5. **Activate senses** — start perceiving
6. **Ready** — the body is alive

## Network

**Discovery** is HTTP on `:8010` (manifest / health — not MCP). **Organ tools** use **MCP** on the other ports when those servers are running.

Canonical map is **`MANIFEST.ka` → `network:`** (this table mirrors it for humans).

| Port | Protocol | Primary organ | Server / role |
|------|----------|---------------|---------------|
| 8010 | HTTP | Ka | Ka Discovery — body map & health |
| 8014 | MCP | Brain (+ Hands + Memory paths) | Tehuti Core — reference body fuses these; see audit |
| 8015 | MCP | Blood | n8n MCP — workflows / event-shaped circulation |
| 8016 | MCP | Hands (files) | Filesystem MCP |
| 8017 | MCP | Skeleton | Postgres MCP |
| 8018 | MCP | Memory (kv) | Memory MCP |
| 8019 | MCP | Hands (image) | ComfyUI MCP |
| 8020 | MCP | Blood | MaatLangChain pipeline — RAG / embeddings |
| 8022 | MCP | Memory (main) | Maat Memory |

**Senses:** no dedicated MCP port in this reference map; perception is via gateways, webhooks, and apps (`docs/ka-audit-2026-04-06.md`).

Discovery at `:8010` is intended to be open. Organ MCP endpoints typically require **Bearer** token auth where enabled.

## Core Principles

- **Nine organs** — the body plan is fixed; implementations are swappable
- **Soul boots first** — moral constraints before capabilities
- **Constitutional memory** — append-only, never silently overwritten
- **Self-healing** — the Ka organ monitors, heals, escalates
- **Universal body plan** — same structure for chatbot, robot, or building
- **Learning is reversible** — rollback is the system working correctly
- **Prompts are sand. Policies are stone. Constitutions are bedrock.**

## Attribution

Ka Architecture is built on the **KA2 Methodology** by **Dr. Tdka Kilimanjaro** at the **[University of KMT](https://universityofkmt.myshopify.com)**.

## License

**Code** in this repository: [MIT License](LICENSE). **`docs/ka-architecture-paper.md`** (and Ka spec text there): **CC BY 4.0** as stated in that file.

---

## Distribute / run on another machine

Not everything in the Ka map lives **inside** this folder. See **[`DISTRIBUTION.md`](DISTRIBUTION.md)** — tiers (schemas-only vs full lab), detaching to its own Git repo, packaging, and diagrams.

---

*Ka Architecture™ — From backbone to body. From policy to constitution. From optimization to Maat.*
