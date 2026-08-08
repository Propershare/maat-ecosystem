# MAAT Forge (blueprint)

**Status:** Skeleton in **`maat-forge/`** at lab root — first bounded job (`jobs/first-bounded-loop.mjs`) only; scheduler/MCP server still future. Use this doc to keep **forge** separate from **`maat-runtime`** and **`maat-ecosystem`**.

## What forge is

**MAAT Forge** is the planned **autonomous local workhorse**: scheduled jobs, Python (or SDK) execution loops, bounded experiments, dataset prep, small-model train/eval, and **structured write-back** to gitMaat / Maat Memory. Other agents (OpenClaw, Cursor, `maat-runtime` clients) **invoke** it over MCP or HTTP; forge does **not** replace the interactive coding-agent runtime.

## What forge is not

- **Not `maat-runtime`** — the TS Pi-fork monorepo (`maat-runtime/`) remains the user-facing CLI/TUI/web toolkit and MCP **client** surface.
- **Not `maat-ecosystem`** — constitutional law, Ka-body organs, and sacred schemas stay in `maat-ecosystem/`; forge **consumes** contracts, it does not redefine them.
- **Not unbounded self-modification** of soul/skeleton — experiments run in **sandboxes** and **branches**; no direct edits to canon without Guard.

## Core responsibilities (target)

| Area | Responsibility |
|------|----------------|
| Scheduler | Cron-like or queue-driven job triggers |
| Workers | Process isolation for long-running tasks |
| Python SDK layer | Run scripts with pinned envs; optional notebook-style flows |
| Model / expert runners | Ollama, small local experts, Gemma-style swarms (config-driven) |
| Memory sink | Report outcomes to gitMaat (`maatlangchain/maat_memory` patterns) |
| MCP / API | Expose tools: `submit_job`, `job_status`, `list_artifacts` |

## Autoresearch pattern (borrowed, bounded)

Patterns like Karpathy **autoresearch** (fixed wall-clock budget, one metric, keep/discard) belong **inside forge jobs** as a **template**, for:

- Prompt / scoring experiments
- Small expert evaluation
- Template optimization for sellable **maat-runtime** kits

They must **not** become the architecture for the whole lab or mutate protected components.

## Layout (lab)

See [`maat-forge/README.md`](../maat-forge/README.md). Current tree:

```
maat-forge/
├── README.md
├── jobs/
│   └── first-bounded-loop.mjs   # first safe job (reports only)
└── reports/                     # job artifacts
```

Future (optional repo): `config/`, `forge/`, `experts/`, `adapters/`, `memory/`, `mcp/`, `tests/`.

## See also

- [`docs/MAAT-IMMUNE-SYSTEM.md`](MAAT-IMMUNE-SYSTEM.md) — Forge’s place in the **immune** loop (bounded adaptation, not sacred mutation)
- [`docs/MAAT-PRODUCT-MAP.md`](MAAT-PRODUCT-MAP.md) — product boundaries
- [`docs/MAAT-FRAMEWORK-REPORT.md`](MAAT-FRAMEWORK-REPORT.md) — five-layer architecture (MCP is transport, not truth)
