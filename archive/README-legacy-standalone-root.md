# Legacy: standalone MAAT README (archived full text)

**Status:** Historical. Merged into this monorepo from `Propershare/maat-ecosystem` before the **canonical Ka-body** was established at [`maat-ecosystem/`](../maat-ecosystem/).

**Canonical today:** [`../maat-ecosystem/README.md`](../maat-ecosystem/README.md), [`../maat-ecosystem/MANIFEST.ka`](../maat-ecosystem/MANIFEST.ka).

---

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

*(Full legacy document continues in git history; structure diagram referenced root-level `maat-core/`, `maatbench/`, etc.)*

For **MaatBench**, use **`maat-ecosystem/maatbench/`** as the path aligned with the current Ka layout — see [`../maat-ecosystem/maatbench/README.md`](../maat-ecosystem/maatbench/README.md).
