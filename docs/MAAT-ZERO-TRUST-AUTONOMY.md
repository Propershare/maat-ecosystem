# MAAT Zero-Trust Autonomy

**Status:** Specification — **autonomous MAAT** requires **zero-trust** at every touchpoint. This doc is the security and initiation model that sits beside [`MAAT-LAB-CONTROL-PLANE.md`](MAAT-LAB-CONTROL-PLANE.md) (machine order, installers), [`MAAT-LIGHTWEIGHT-INTELLIGENCE.md`](MAAT-LIGHTWEIGHT-INTELLIGENCE.md) (tokens/context efficiency), and [`MAAT-IMMUNE-SYSTEM.md`](MAAT-IMMUNE-SYSTEM.md) (immune organs and events).

**First truth:** Every touchpoint is **hostile until proven otherwise** — including user UI, gateway, runtime, MCP, Forge, memory writes, prompts, tools, remote agents, and **local models**. “Inside the lab” is **not** trust.

The real audit questions are not “can the user see it?” but:

- Who is allowed to see what?
- Who is touching what?
- Who initiated it?
- Can the system **prove** that?
- Can the system **stop** it?
- Can the system **recover** if the actor is hostile, confused, or injected?

If those cannot be answered, **nothing should proceed**.

---

## 1. Questions every request must answer

For every action, the system must be able to answer:

| Question | Purpose |
|----------|---------|
| Who are you? | Identity binding |
| What are you trying to do? | Action classification |
| Where are you touching? | Target layer (sacred / managed / volatile / user) |
| Why are you allowed? | Policy + role |
| What evidence supports this? | Provenance |
| What is the risk? | Trust/risk class |
| Who will know it happened? | Audit + immune memory |
| Can it be reversed? | Learning safety / rollback path |

---

## 2. What humans should see (governed surface)

Users should **not** see raw internals by default. They **should** see:

- Role-appropriate UI, approved toolkits, bounded controls
- Transparent explanations and state summaries
- Alerts when important things happen
- **Why** something was blocked or escalated

Users should **not** automatically see:

- Sacred configs, full policy internals, raw secrets
- Protected paths, all sessions across the lab
- Constitutional mutation surfaces

**Rule:** The user sees a **governed surface**, not the naked machine. That is the Maat way.

---

## 3. What Tehuti Guard should see

Guard must **not** ingest “everything” in the human sense. It receives a **minimum sufficient canonical action envelope** to judge:

- Actor identity, machine identity, session id, task id
- Requested action, target resource, source surface
- Provenance when relevant, risk hints
- Current Sentinel context, current policy scope

Guard does **not** need full thought logs — it needs a **contract-shaped envelope**.

---

## 4. The mandatory pipeline (nothing “just happens”)

Normal apps assume: click → backend runs → maybe logs. **That model is invalid** here.

```text
Intent surface
  → Identity binding
  → Envelope creation
  → Guard judgment
  → Sentinel awareness update
  → Execution in bounded zone
  → Memory / event write
  → User-visible result
```

**UI, gateway, and runtime are not authority** — they are **initiation surfaces** only.

---

## 5. Initiation envelope

When UI, gateway, or CLI initiates work, it creates an **initiation envelope** (example shape — bind to your `maat_event` / schema work):

```json
{
  "initiator_type": "ui",
  "initiator_id": "maat-studio",
  "user_id": "imhotep",
  "device_id": "workstation-01",
  "session_id": "sess_123",
  "task_id": "task_456",
  "requested_action": "install_toolkit",
  "target": "maat-ev-scout",
  "origin_surface": "studio.dashboard",
  "timestamp": "2026-04-12T12:00:00Z"
}
```

Then **Guard decides**. Install/repair/control-plane actions use the same pattern (see [`MAAT-LAB-CONTROL-PLANE.md`](MAAT-LAB-CONTROL-PLANE.md)).

---

## 6. Identity stack (four layers)

Traceability requires **all** of:

| Layer | Examples |
|-------|----------|
| **Human identity** | Operator, tenant owner, team member |
| **Machine identity** | `server-01`, `workstation-01`, `forge-node-02` |
| **Agent/service identity** | `runtime.scout`, `forge.dataset_worker`, `tehuti.guard`, `sentinel.monitor` |
| **Session/task identity** | Session id, task id, correlation id |

Without all four, you do not have **proof** — only vibes.

---

## 7. Authority model: who may claim what

| Actor | May initiate | May not |
|-------|----------------|--------|
| **User** | Scoped requests via governed UI/CLI | Raw mutation of sacred layer; silent promotion |
| **Agent** | Tool **proposals** as envelopes | Direct shell/file authority without Guard |
| **Machine** | Local policy within enrollment | Override central law without amendment |
| **Gateway/runtime** | Forward envelopes | Stand as ultimate authority |

---

## 8. Prompt injection: assume success of attempt, not prevention

Anyone can **attempt** injection. The architecture must **contain** it.

### Defense in five places

1. **Input boundary** — Classify: user request, tool output, web/file content, model suggestion, external MCP response — **all untrusted** until classified.
2. **Role separation** — Retrieval ≠ execution; summarizer ≠ config mutation; worker ≠ canon promotion (blast radius).
3. **Tool mediation** — Model output never becomes raw shell/file mutation; every tool path becomes an **envelope** and passes Guard.
4. **Sacred path protection** — Runtime immune hooks (e.g. [`maat-immune-hooks`](../maat-runtime/packages/coding-agent/docs/maat-immune-hooks.md)) block sacred writes even if the model is tricked.
5. **Immutable audit** — Failed injection attempts are **still** recorded (immune memory).

---

## 9. Dual containment

| Layer | Mechanism |
|-------|-----------|
| **Software** | Contracts, Guard, Sentinel, memory, immune hooks, promotion rules |
| **Host** | Protected directories, service users, filesystem permissions, staged installs, rollback, secret separation, network auth |

Software alone loses to shell access. Host alone loses to prompt-layer corruption. **You need both.**

---

## 10. Reference scenarios (expected outcomes)

| Scenario | Expected |
|----------|----------|
| Normal “install toolkit” | Envelope → Guard allows managed install → Sentinel tracks → memory records → Studio shows result |
| Vague “delete old MAAT stuff” | Destructive class → Guard blocks/escalates → explanation to user → no unscoped delete |
| README says “disable logging” | Untrusted file → model may propose bad action → envelope shows logging tamper → constitutional / immune path → quarantine, no auto-recovery |
| Forge worker escapes sandbox | Enveloped tools → classification → Guard blocks → Sentinel warning/high → memory pattern → job ends in review |
| Spoofed MCP memory | TLS/auth-bound endpoints; MCP text is **data not law**; structured contracts only; Guard mediates follow-on actions |
| Installer wipes gateway | Control plane: managed layer only, protected services immutable to ordinary installer, staging + activation + rollback ([`MAAT-LAB-CONTROL-PLANE.md`](MAAT-LAB-CONTROL-PLANE.md)) |
| Forge “relaxes” Guard | Target = sacred/policy → autonomous mutation **forbidden** → candidate as review object only → human amendment |
| Insider with shell | Identity-bound session + runtime hooks + **OS permissions** on sacred dirs; Sentinel + memory record attempt |

---

## 11. Agent enforcement algorithm (autonomous law)

1. **Bind identity** — human (if present), agent, machine, session/task ids.  
2. **Classify surface and target** — sacred | managed | volatile | user.  
3. **Classify action** — read | write | execute | promote | install | configure | delete | export.  
4. **Classify trust/risk** — trusted internal structured vs untrusted text vs high-risk chain vs constitutional threat.  
5. **Guard decision** — allow | deny | review | quarantine | escalate.  
6. **Sentinel update** — live awareness.  
7. **Execute only in bounded zone** — no raw touching outside allowance.  
8. **Emit + remember** — event, outcome, immune trace ([`MAAT-IMMUNE-SYSTEM.md`](MAAT-IMMUNE-SYSTEM.md)).

This extends the control-plane algorithm in [`MAAT-LAB-CONTROL-PLANE.md` §7](MAAT-LAB-CONTROL-PLANE.md#7-agent-enforcement-algorithm-machine-side) with **identity**, **trust class**, and **execution boundary**.

---

## 12. Build order (aligns with control plane)

1. **Machine order** — Paths, manifests, install/repair discipline ([`MAAT-LAB-CONTROL-PLANE.md`](MAAT-LAB-CONTROL-PLANE.md)).  
2. **Identity and initiation** — Every surface emits envelopes; no direct action from UI/gateway alone.  
3. **Guard + Sentinel + memory** — Judgment, awareness, durable trace.  
4. **Bounded runtime + Forge** — Interaction vs adaptation ([`MAAT-FORGE.md`](MAAT-FORGE.md)).  
5. **Studio / CLI** — Visibility, operator control, repair and audit.

---

## 13. MAAT verdict (full audit)

The challenge is **total order** across initiation, identity, mutation, and recovery.

The system is MAAT-aligned when:

- No one touches anything without an **identity-bound envelope**
- No surface has **raw authority**
- No sacred area is **autonomously** mutable
- Prompt injection is **contained**, not merely hoped away
- Every anomaly becomes **immune memory**
- Every repair candidate is **bounded and reviewable**
- Install and repair obey the **same law** as runtime execution

---

## See also

- [`docs/MAAT-LIGHTWEIGHT-INTELLIGENCE.md`](MAAT-LIGHTWEIGHT-INTELLIGENCE.md)
- [`docs/MAAT-LAB-CONTROL-PLANE.md`](MAAT-LAB-CONTROL-PLANE.md)
- [`docs/MAAT-IMMUNE-SYSTEM.md`](MAAT-IMMUNE-SYSTEM.md)
- [`docs/MAAT-PRODUCT-MAP.md`](MAAT-PRODUCT-MAP.md)
- [`maat-runtime/packages/coding-agent/docs/maat-immune-hooks.md`](../maat-runtime/packages/coding-agent/docs/maat-immune-hooks.md)
