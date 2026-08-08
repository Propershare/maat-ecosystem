# MAAT Self-Learning Agent

**How to build a self-learning agent that is governed into Maat by its environment — for any model, any domain.**

> Companion to [`MAAT-FINETUNING-METHOD.md`](MAAT-FINETUNING-METHOD.md). That doc covers tuning a model's
> *weights* toward Maat. This doc covers the stronger, complementary path: **containing** a model inside a
> governed runtime so Maat is **enforced**, and letting the model **learn from real consequences**.

---

## 0. Thesis (why this beats baking Maat into weights)

We proved, with evidence, that trying to make a model "be Maat" purely through fine-tuning is weak: the
base model's disposition (sycophancy, compulsive scaffolding, fabrication, won't-stop-when-told) dominates,
and small SFT cannot overwrite it (see `Tehuti-Dataset/MODEL_REGISTRY.md`, the "who built kemet" lived
failure). A model trained on *who knows what* cannot be **trusted** to be Maat.

The answer is not a better prompt. It is **containment + grounded learning**:

1. **Contain** the model inside `maat-runtime`, where every action it proposes is intercepted by the
   **immune hooks** and **Tehuti Guard** *before the effect lands*. Maat becomes **enforced**, not hoped.
2. **Ground** the model's learning in the **real outcomes** of its actions (allowed / blocked / errored),
   captured as an append-only immune trail — a far more honest signal than imitating essays.
3. **Graduate** autonomy: the operator earns the right to **self-approve** low-risk actions on
   **replaceable** layers as it builds a track record, while **sacred** layers stay frozen.

A model we cannot trust to *be* Maat, we **contain into** Maat — and it improves by mastering a governed
environment. This is why the runtime is the right substrate for **any** self-learning agent.

---

## 1. Roles (who is who)

| Role | Who | Why |
|------|-----|-----|
| **Operator** | A **tool-capable driver model** (frontier API now to prove the loop; local `packages/pods` model — qwen3-coder / gpt-oss / glm-4.5 — later) | Acts in the environment: proposes `read/bash/edit/write` tool calls. `packages/ai` only admits tool-calling models. |
| **Knowledge tool** | **Tehuti Scholar** (served via Ollama), exposed as a **callable Maat tool/skill** | Tehuti Scholar is a *teacher, not a driver* — under tool scaffolding it emits garbled tool tokens (`MODEL_REGISTRY.md` known issues). It is consulted, not in the driver's seat. |
| **Enforcement** | **Immune hooks** (`maat-runtime` coding-agent) + **Tehuti Guard** | Deterministic gate: block sacred-path writes / dangerous bash / log-tamper *before* effect; emit immune events. |
| **Sensing / memory / proof / adaptation** | **Sentinel / Maat-Memory / MaatBench / Forge** | The rest of the immune loop (`MAAT-IMMUNE-SYSTEM.md`). |

**Critical correction (lived truth):** do **not** put `tehuti-scholar` in the operator seat. Operator =
capable driver; Scholar = governed knowledge tool; Maat = enforced by hooks. This preserves capable agency,
Maat reasoning, Maat enforcement, and grounded learning all at once.

---

## 2. The mandatory action pipeline (from MAAT-ZERO-TRUST-AUTONOMY §4)

Nothing "just happens." Every operator action follows:

```
Intent (operator proposes tool call)
  → Identity binding (agent/device/session/task)
  → Envelope creation
  → Guard / immune-hook judgment (allow | deny | review | quarantine | escalate)
  → Execute ONLY in bounded zone
  → Immune event + memory write (append-only)
  → Result back to operator
```

The runtime, gateway, and UI are **initiation surfaces only — never authority** (zero-trust §4).

---

## 3. The grounded learning loop (where "self-learning" comes from)

Every proposed tool call produces an **immune envelope** (`maat-immune-hooks.md`): `tool_call → classify →
allow/block → outcome → JSONL`. That append-only trail **is** the training signal, and it unifies with the
preference-learning lever from `MAAT-FINETUNING-METHOD.md`:

```
Sentinel sense → Guard allow? → Runtime act → Bench verify → Memory log → Forge candidate → Review → Promote
        (MAAT-IMMUNE-SYSTEM.md §9 self-debugging loop)
```

- **Preference pairs from consequences:** `chosen` = trajectories that were **Guard-approved and
  Bench-green**; `rejected` = trajectories that were **blocked, quarantined, or errored**. This is DPO/ORPO
  data harvested from *reality*, not hand-written essays. Failures are first-class learning signal.
- **Lessons:** repeated anomalies/denials distill into `lesson.distilled` rows (Maat-Memory incident lane).
- **Repairs:** Forge proposes *bounded* fixes (safer prompts, routing) from the trail — never autonomous
  mutation of sacred Core.

The operator literally learns to **master its environment**: act → see real Maat-governed consequence →
adjust. No fabrication survives, because fabricated-then-write attempts are blocked and *recorded as
rejected*.

---

## 4. Graduation: earned self-approval (instance of the promotion matrix)

"Self-approve from there" is **graduated autonomy**, bounded by `MAAT-IMMUNE-SYSTEM.md §5–6`. The operator
does not start trusted; it **earns** scope.

| Tier | Action class | Approval required | Self-approve when… |
|------|--------------|-------------------|--------------------|
| **T0 Observe** | read, grep, find, ls | none (read-only) | always (volatile/user layer) |
| **T1 Propose** | write/edit in **scratch workspace**, non-dangerous bash | immune-hook allow | always within bounded zone |
| **T2 Earned** | write/edit in **managed (replaceable)** project areas | human/Guard at first | after N consecutive Guard-approved + Bench-green T1 actions, **for that action class only** |
| **T3 Governed** | new Guard candidate rules, prompts to prod defaults | review (human/governance) | **never** auto-applied |
| **T4 Sacred (frozen)** | schemas / soul / policy semantics / identity / audit contract | explicit human amendment | **never** — constitutional freeze |

**Promotion is per-action-class and revocable.** A `regression.detected` or `policy.bypass_attempt` demotes
the operator. Constitutional-severity events trigger §5.3: **halt first**, human review before any resume.
This is autonomy without ungoverned drift.

---

## 5. Why it generalizes (any model, any domain)

- **Swap the operator** — frontier or local, "trained on who knows what." Containment + grounded learning
  don't depend on the model being pre-aligned.
- **Swap the knowledge tool** — Tehuti Scholar for KMT scholarship; a legal/medical model for that domain.
- **Keep the substrate** — runtime + immune hooks + Guard + Memory + Bench + Forge + promotion matrix.

The self-learning agent = **capable operator + immune containment + grounded-trail learning + graduated
promotion**. The model is *contained into* Maat, then *improves by experience* under that containment.

---

## 6. Reconciling the two paths (weights vs containment)

| Concern | Lever |
|---------|-------|
| Capability / knowledge / disposition | fine-tuning + DPO (`MAAT-FINETUNING-METHOD.md`) |
| Safety / Maat enforcement | **immune hooks + Guard** (this doc) — does not trust the model |
| Honest learning signal | **immune trail → preference pairs** (this doc feeds the DPO of the other) |
| Knowledge the weights can't hold (glyphs, dates) | retrieval/tool + abstention |
| Corrigibility / multi-turn | runtime conversation + promotion/demotion |

They are one system: containment produces the grounded data that fine-tuning consumes; fine-tuning raises
the operator's competence inside the containment.

---

## 7. Build order & first increment

Aligned with `MAAT-ZERO-TRUST-AUTONOMY §12`:

1. **Increment 1 (this cycle):** Wire a tool-capable operator into `maat-runtime` with the **immune
   extension enabled**; run one **bounded, sandboxed** task; **harvest the immune trail** = first grounded
   dataset. Define (not yet automate) the promotion tiers (§4).
2. Add **Tehuti Scholar as a callable tool/skill**.
3. Wire **Guard HTTP** into `classify` (immune-hooks "Limits": HTTP Guard can extend classify later).
4. Wire **Forge** to consume the trail and emit bounded repair/preference candidates.
5. **Studio/CLI** for operator visibility + promotion review.

### The increment harness

Lives **outside** `maat-runtime` (respects its `AGENTS.md`; does not diverge the fork):
`maat-self-learning/` —
- `run_operator.sh` — sets immune env, launches `pi -p --mode json -e <immune ext> --provider/--model …`
  in a scratch workspace; **refuses cleanly if no operator credential is present** (no faked runs).
- `tasks/bounded_task_01.md` — the sandboxed task.
- `harvest_trail.py` — immune JSONL + session JSONL → grounded lesson/preference candidates.
- `operator-models.json` — local Ollama (OpenAI-compatible) operator option for later.

---

## 8. Honest status / blockers

- **Operator = frontier** (chosen to prove the loop). **No frontier API key is currently set**
  (`ANTHROPIC/OPENAI/OPENROUTER/GROQ` unset). The harness is ready and refuses cleanly until a key is
  provided; it can fall back to a **local Ollama operator** (`--local`) to prove the *plumbing* only.
- Local Ollama currently holds Gemma-4-E4B teachers (weak tool-callers); a real local operator needs a
  tool-capable pull (qwen3-coder / gpt-oss via `packages/pods`).
- `maat-runtime` is built (`dist/cli.js`) and runnable; we do **not** build/modify it for Increment 1.

---

## See also
- [`docs/MAAT-IMMUNE-SYSTEM.md`](MAAT-IMMUNE-SYSTEM.md) — organs, severities, promotion authority, §9 loop.
- [`docs/MAAT-ZERO-TRUST-AUTONOMY.md`](MAAT-ZERO-TRUST-AUTONOMY.md) — envelopes, identity, containment.
- [`docs/MAAT-FINETUNING-METHOD.md`](MAAT-FINETUNING-METHOD.md) — the weights path; consumes this trail.
- [`maat-runtime/packages/coding-agent/docs/maat-immune-hooks.md`](../maat-runtime/packages/coding-agent/docs/maat-immune-hooks.md) — envelope shape, enable env vars.
- [`docs/MAATBENCH-v2.md`](MAATBENCH-v2.md) — the proof organ (`models` + runtime suites).
