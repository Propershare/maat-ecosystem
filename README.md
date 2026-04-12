# MAAT Ecosystem

> Not a repo. A constitutional ecology for evolving AI systems.

**MAAT is a local-first AI operating ecosystem where agents, memory, policies, and tools can evolve without forcing users to start over.**

Apps are downloadable roles. Packs are modular upgrades. Studio lets you inspect, govern, and replay what the agents do.

## Architecture

```
SCHEMAS (permanent, sacred)     ← never change
    ↓
KERNEL  (tiny, boring)          ← 8 jobs, no model logic
    ↓
ADAPTERS (swappable)            ← Ollama today, vLLM tomorrow
    ↓
APPS + PACKS (downloadable)     ← roles, policies, tools, learning
    ↓
STUDIO (observable)             ← dashboard, logs, replay, governance
    ↓
CLI (operator control)          ← maat status, maat migrate
    ↓
MAATBENCH (verified)            ← 49 tests, 6 categories, system-level proof
```

## The 7 Pillars

| # | Pillar | What It Does |
|---|--------|-------------|
| 1 | **MAAT Core** | Schemas + kernel. The constitutional layer. |
| 2 | **MAAT Memory** | 5 real memory classes: episodic, semantic, constitutional, task, working |
| 3 | **MAAT Policy** | Machine-readable moral + operational constitution. Not guardrails. |
| 4 | **MAAT Tools** | All actions through a standard contract. |
| 5 | **MAAT Learning** | Controlled adaptation. Always reversible. Rollback support. |
| 6 | **MAAT Runtime** | Kernel + adapters + event bus. Single or multi-agent. |
| 7 | **MAAT Commons** | Apps, packs, policies, skills — the download ecosystem. |

## Structure

```
maat-ecosystem/
├── maat-core/              ← Sacred: schemas, kernel, config
│   ├── schemas/            ← 7 JSON schemas (identity, memory, task, policy, event, tool, learning)
│   ├── kernel/             ← MaatKernel, EventBus, PolicyEngine, IdentityStore, Registry
│   ├── config.yaml         ← Swap adapters here, no code changes
│   └── SACRED.md           ← The line between sacred and replaceable
│
├── maat-adapters/          ← Replaceable: model, memory, tool backends
│   ├── models/             ← Ollama, OpenAI-compatible
│   ├── memory/             ← PostgreSQL, SQLite
│   └── tools/              ← MCP, native Python
│
├── maat-memory/            ← Memory class handlers
│   ├── episodic/           ← Time-bound, decays, consolidates
│   ├── semantic/           ← Stable knowledge, from consolidation
│   ├── constitutional/     ← Append-only, versioned, never silently overwritten
│   └── consolidation/      ← Episodic → semantic promotion engine
│
├── maat-apps/              ← Downloadable role packs
│   ├── receptionist/       ← Gold-standard: manifest + policy + 4 workflows + prompts
│   ├── researcher/         ← Deep research with citation and fact-checking
│   ├── operator/           ← System ops, deploy, monitor
│   └── teacher/            ← Tutoring, curriculum, progress tracking
│
├── maat-packs/             ← Modular capability packs
│   ├── policy-packs/       ← maat-default, strict-safety
│   ├── tool-packs/         ← filesystem tools
│   ├── agent-packs/        ← tehuti (default operator)
│   └── learning-packs/     ← self-improve (consolidation + refinement)
│
├── maat-studio/            ← Observability and governance
│   ├── dashboard/          ← Web-based agent/memory/event viewer
│   ├── logs/               ← Structured event log viewer with filters
│   ├── replay/             ← Session replay from event log
│   └── governance/         ← Policy audit trail and violation reports
│
├── maat-cli/               ← Operator CLI
│   └── maat               ← status, identity, memory, policy, events, apps, migrate
│
├── maat-openclaw-skill/    ← OpenClaw integration skill
│
├── maatbench/              ← System verification suite (49 tests, 6 categories)
│   ├── contracts/          ← Structured test definitions
│   ├── fixtures/           ← Test identities, policies
│   ├── runners/            ← Schema, policy, memory, event, portability, learning runners
│   ├── scorers/            ← Category + overall MAAT score
│   ├── reports/            ← Text + JSON report generation
│   └── run.py             ← Single entry point
│
├── CONSTITUTION.md         ← What is sacred vs replaceable
├── PORTABILITY.md          ← The migration guarantee
├── EVENTS.md               ← Canonical event taxonomy (40+ types)
├── POLICY.md               ← Policy doctrine (5 outcomes, evaluation order)
└── LEARNING.md             ← Learning doctrine (reversible, snapshot-backed)
```

## The 9 Questions Every MAAT Agent Can Answer

1. **Who am I?** → Identity schema + IdentityStore
2. **What am I allowed to do?** → PolicyEngine + Three-Ring governance
3. **What do I remember?** → Memory classes + MemoryAdapter
4. **What tools can I use?** → Tool contract + ring-based access
5. **What tasks exist?** → Task lifecycle (6 states)
6. **What events have occurred?** → EventBus + append-only log
7. **What can I learn?** → Learning contract (always reversible)
8. **What requires escalation?** → Policy escalation rules
9. **What part of me can be swapped?** → Everything in maat-adapters/

## Sacred vs Replaceable

**Sacred** (never changes silently):
- Schemas, policy semantics, event taxonomy, task lifecycle, memory classes, identity format

**Replaceable** (swap via config):
- Model provider, vector DB, SQL backend, tool transport, CLI framework, UI framework, agent runtime

See `CONSTITUTION.md` and `maat-core/SACRED.md` for the full line.

## Quick Start

```python
from maat_core.kernel.kernel import MaatKernel
import yaml

config = yaml.safe_load(open("maat-core/config.yaml"))
kernel = MaatKernel(config)

agent_id = kernel.register_agent({"name": "my-agent", "ring": "middle-ring"})
kernel.remember(agent_id, "First memory", memory_class="episodic")
results = kernel.recall(agent_id, "first")
```

## CLI

```bash
maat status              # Show ecosystem status
maat identity list       # List agents
maat memory search "x"   # Search memory
maat policy check agent action  # Check policy
maat events tail         # Tail event log
maat apps list           # List installed apps
maat migrate             # Export for migration
```

## MaatBench — System Verification

```bash
python3 -m maatbench.run --verbose
```

Tests 6 guarantee categories:
- **Contract Integrity** — schemas valid, fields correct, enums match
- **Policy Fidelity** — deny/allow/escalate enforced, fail-closed, no bypass
- **Memory Fidelity** — attribution, append-only, constitutional protection, rollback
- **Event Fidelity** — emission, subscription, persistence, replay
- **Portability** — identity/memory/policy survive adapter swaps
- **Learning Safety** — snapshots required, reversible, constitutional protected

## Portability Guarantee

> Any compliant MAAT implementation must preserve identity, policy, task lineage,
> and event history across adapter swaps.

See `PORTABILITY.md` for the full guarantee.

## Doctrine

- `CONSTITUTION.md` — What is sacred, what is replaceable, amendment process
- `PORTABILITY.md` — Migration guarantees, the 9-question test
- `EVENTS.md` — Canonical event taxonomy, 40+ typed events
- `POLICY.md` — 5 outcomes, evaluation order, Three-Ring governance
- `LEARNING.md` — Reversible always, snapshots mandatory, safety valve

## Philosophy

Built on stable meaning, not new tech.

- **Contracts at the center, not the tech**
- **Prompts are sand. Policies are stone.**
- **Constitutional memory is never silently overwritten. It is amended through traceable versioning.**
- **If learning is not reversible, the system becomes self-corrupting.**
- **Identity must outlive implementation.**

## Aligned with Maat

Truth. Balance. Order. Justice. Self-Reflection.

Built to outlast any single model, runtime, or technology.
