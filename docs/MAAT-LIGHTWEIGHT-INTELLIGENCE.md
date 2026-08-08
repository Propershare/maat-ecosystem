# MAAT Lightweight Intelligence

**Status:** Specification — how the lab stays **fast**, **cheap in tokens**, and **context-efficient** while remaining MAAT-governed. Complements [`MAAT-ZERO-TRUST-AUTONOMY.md`](MAAT-ZERO-TRUST-AUTONOMY.md) (who may act) and [`MAAT-IMMUNE-SYSTEM.md`](MAAT-IMMUNE-SYSTEM.md) (immune events).

**Team sentence:** We are **not** encoding MAAT as a giant prompt; we encode it as **contracts, guards, routing, and memory structure** so models stay **lightweight, fast, and context-efficient**.

**The trap to avoid:** Building the lab like one giant always-on “AI brain” — that becomes slow, expensive, context-window fragile, token-hungry, and brittle.

**The rule:** **MAAT governs the system, not the prompt.**

---

## 1. Design principle

| Wrong | Right |
|--------|--------|
| MAAT = 8k tokens of constitution in every call | MAAT = **middleware + schemas + rules** |
| Full history every turn | **Short working context** + retrieval on demand |
| Model “remembers” everything | **maat-memory** stores; model **retrieves** |
| Raw event logs in prompts | **Compressed status** + anomalies only |

**Use tokens for thought only when thought is needed.** Use **code, rules, and memory indexes** for everything else.

---

## 2. Keep the model stateless by default

- **Short** working context for the **current** task.
- **Task-local** memory; older history **out of prompt**, in store.
- **Summaries** only when compaction or handoff requires them.

**Pattern:** current task → current context; older history → retrieval, not injection.

---

## 3. Memory: retrieval-first, not dump-first

| Bad | Good |
|-----|------|
| Inject all memory into prompt | Retrieve **3–10** relevant records |
| | Tiny **structured** snippets + **IDs** + **scores** |
| | Runtime chooses what to load |

This keeps context lean and reduces “context stupidity.”

---

## 4. MAAT in middleware, not prompt text

Instead of repeating in prose (every call):

- provenance, sacred paths, policy, identity, roles

**Implement in architecture:**

- **Guard** — blocks sacred / forbidden actions  
- **Runtime** — injects identity fields automatically where applicable  
- **Memory adapter** — enforces provenance fields on write  
- **Sentinel** — session/health state (machine-readable)  
- **Promotion** — blocks autonomous canon changes  

That saves tokens **on every** call.

---

## 5. Split fast vs deep agents (swarm discipline)

| Role | Typical model / cost |
|------|----------------------|
| **Scout** | Small, fast — coverage |
| **Analyst** | Medium — only when judgment needed |
| **Archivist** | Mostly **structured** logic, minimal LLM |
| **Forge workers** | Bounded tasks; often small local experts |

Not every job needs large reasoning.

---

## 6. Structured envelopes, not prose

Prefer compact machine state:

- `agent_id`, `task_id`, `action`, `target`, `risk`, `status`

Not long contextual paragraphs. Aligns with [`MAAT-ZERO-TRUST-AUTONOMY.md`](MAAT-ZERO-TRUST-AUTONOMY.md) initiation envelopes.

---

## 7. Let maat-memory remember; let the model think now

- **Model:** think for this turn, retrieve what it needs, act **within bounds**, “forget” unless promoted to durable memory.  
- **Memory:** stored **outside** context, **indexed**, **filtered**, **promoted** only when useful.

---

## 8. Event compression

- **Sentinel** and pipelines may emit many events — **do not** feed raw logs into model prompts by default.  
- **Compress** to status summaries, **aggregate** streaks, **surface** anomalies; **detail on demand** only.

---

## 9. Bounded tool wrappers

- Narrow tool sets, **pre-scoped** paths, **short** result formats.  
- Reduces tool confusion, tokens, injection surface, and latency.

---

## 10. Tiers of intelligence

| Tier | Mechanism | Use for |
|------|-----------|---------|
| **1 — Rules / code** | Path checks, schema validation, role checks, install safety, routing | Fastest, cheapest |
| **2 — Small local models** | Classification, summarization, ranking, extraction, drafts | Gemma e2b/e4b class |
| **3 — Deeper models** | Synthesis, hard debugging, research, planning | **Escalation only** |

---

## 11. Good vs bad MAAT token patterns

| Good (target pattern) | Bad |
|------------------------|-----|
| **~100–300** token policy **summary** when a model must see policy at all | Multi-k constitution in **every** call |
| **≤1–2 KB** retrieved memory, structured | Full session replay |
| Structured task state + compact response schema | Raw logs in context |
| | Repeated giant agent biographies |

---

## 12. Where logic lives

| Where | What |
|-------|------|
| **Code** | Identity binding, enforcement, sacred path blocking, install safety, memory **schemas**, promotion rules, severity, routing |
| **Memory** | Lessons, outcomes, preferences, anomalies, approved patterns |
| **Models** | Interpretation, flexible reasoning, summarization, synthesis, **candidate** generation (then Guard/promotion) |

---

## 13. Lab hardware sketch (example)

| Resource | Use |
|----------|-----|
| **Workstations / smaller** | Scouts, classifiers, extraction, watchdogs, low-cost Forge |
| **GPU server** | Medium-depth reasoning, batching, memory services, Sentinel/Guard **service** work, background eval |
| **OpenClaw / maat-runtime** | Orchestrator and user-facing execution — **not** a single giant always-thinking brain |

---

## 14. Performance principle

**The smarter the architecture, the dumber the prompt can be.**

If tight:

- Less unnecessary thinking  
- Shorter context  
- Lower cost  
- Higher responsiveness  

---

## 15. Build checklist

- Short prompts  
- Structured state  
- Retrieval on demand  
- Small models first; **deep models only on escalation**  
- MAAT in the **system layer**, not giant context  

---

## See also

- [`docs/MAAT-ZERO-TRUST-AUTONOMY.md`](MAAT-ZERO-TRUST-AUTONOMY.md)
- [`docs/MAAT-IMMUNE-SYSTEM.md`](MAAT-IMMUNE-SYSTEM.md)
- [`docs/MAAT-LAB-CONTROL-PLANE.md`](MAAT-LAB-CONTROL-PLANE.md)
- [`AGENTS.md`](../AGENTS.md) — Scout / Analyst / Archivist line
- [`docs/SCOUT-ANALYST-ARCHIVIST.md`](SCOUT-ANALYST-ARCHIVIST.md) if present
