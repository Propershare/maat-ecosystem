# MAAT — checkpoint memo & next-tranche task list

**Audience:** Imhotep (principal) and build team.  
**Companion:** [`docs/MAAT-FRAMEWORK-REPORT.md`](MAAT-FRAMEWORK-REPORT.md) (Tranche 1: constitution located + documented).  
**Purpose:** Turn “well-described” into **structurally enforceable** work — without pretending the hard parts are done.

---

## A. CEO-level checkpoint (where we are)

**Done (Tranche 1):**

- Five-layer architecture is **written**, **indexed** (`maat_core` locator), and **linked** from ecosystem + MaatLangChain entry points.
- Live organs were **not** prematurely refactored; migration risk is controlled.

**Not done (the real work):**

The system is still **documentation-strong** and **runtime-weak** on:

1. **Canonical events** — replay, audit, benchmark, and trace-based training need one event stream and one taxonomy.
2. **Memory class separation** — five classes in constitution; **enforcement** in APIs/DB paths is still ahead.
3. **Tool facade** — orchestrator should call **capabilities**, not MCP/HTTP/stdio details.
4. **Pack/app install boundaries** — domain logic must not **import forbidden kernel internals**.
5. **Bench gating** — MaatBench must become the **judge**, not the README.

**Primary risk:** Stopping at prose. **Mitigation:** run [`scripts/enforce-maat-contracts.py`](../scripts/enforce-maat-contracts.py) in CI or pre-merge; expand it as each tranche lands.

---

## B. Next-tranche priorities (strict order)

### Tranche 2 — Events first

**Why first:** Without canonical events, memory refactors and tool polish **lack ground truth** for replay, MaatBench `event_fidelity`, and expert dataset exports.

**Deliver:**

- Emit events for at minimum: `task.created`, `task.updated`, `tool.requested`, `tool.executed`, `tool.denied`, `retrieval.run`, `memory.read`, `memory.write`, `policy.checked` / `policy.violated`, `escalation.raised`, `learning.recorded` (names align with [`maat_event.schema.json`](../maat-ecosystem/skeleton/schemas/maat_event.schema.json) — adjust to namespaced form, e.g. `task.created`, `tool.called`).
- Persist or stream to an **append-only** store (table, log, or bus) with schema validation.
- **Acceptance:** replay script can reconstruct a session ordering from events; MaatBench event runner extended or supplemented for **live** emission samples.

### Tranche 3 — Memory classes second

**Classes (constitution):** episodic, semantic, **constitutional**, task, working.

**Deliver:**

- API or table partition (or explicit `memory_class` discriminator) on **every** write path in `maat_memory` (and MCP mirrors where applicable).
- Docs: which class for which operation; no “dump everything in one blob.”
- **Acceptance:** contract tests fail if a write omits class or uses forbidden class for that operation.

### Tranche 4 — Tool facade third

**Deliver:**

- Internal Python interface (e.g. `Capability` / `invoke(name, args, ctx)`) with adapters: MCP, native, HTTP.
- MaatLangChain orchestration calls **only** the facade for tool execution.
- **Acceptance:** swap MCP mock vs native mock in tests without changing orchestrator code.

### Tranche 5 — Packs / apps fourth

**Deliver:**

- Manifest for packs (tool-pack, policy-pack, agent-pack, learning-pack) with declared **dependencies** and **forbidden imports** list.
- **Acceptance:** enforcement script fails CI if a pack imports spine internals directly (extend `enforce-maat-contracts.py`).

### Tranche 6 — Bench gating fifth

**Deliver:**

- Promotion rule: merge to “release” branch or tag requires **MaatBench** tier + log (categories per [`maat-ecosystem/maatbench/README.md`](../maat-ecosystem/maatbench/README.md)).
- **Acceptance:** CI job runs `python3 -m maatbench.run --category contract_integrity` (minimum) + agreed tier for that release.

---

## C. Enforcement script (architecture with teeth)

**Location:** [`scripts/enforce-maat-contracts.py`](../scripts/enforce-maat-contracts.py)

**Tranche today (starter):**

- Required schema files on disk.
- `maat_event.schema.json` parses; optional event `type.examples` sanity checks.
- `constitution.md` mentions five memory classes and five policy outcomes.

**Expand as tranches land:**

- Event name allowlist vs runtime emitters.
- Memory class registry checks.
- Static check: pack trees must not import forbidden modules.
- Tool adapters implement a named protocol (AST or `inspect`).

**Run:**

```bash
cd /path/to/.n8n
python3 scripts/enforce-maat-contracts.py
```

Exit `0` = pass, `1` = fail (suitable for CI).

---

## D. One-line accountability

| Role | Job |
|------|-----|
| Architecture | Keep contracts sacred; adapters swappable |
| Runtime | **Obey** contracts — provable by bench + enforcer |
| Leadership | **Refuse** “done” without green enforcer + agreed bench tier |

**Document version:** 1.0 — checkpoint memo + task queue for post–Tranche 1 execution.
