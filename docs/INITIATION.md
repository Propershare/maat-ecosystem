# Initiation — Ma’at first (human language)

**Principle:** The system understands the human. The human does **not** need to learn product names, ports, or architecture to **start**.

This is **not** the same as “developer onboarding.” Developer terms belong **after** intent is clear — in the translation layer, not at the door.

**If you already know the stack:** use [`SETUP-WITH-AGENT.md`](SETUP-WITH-AGENT.md) for copy-paste prompts and ordered technical links.

---

## What the agent should sound like

Short. Warm. Plain words. No jargon in the first breath.

**Good opening:**

> I’ll set this up with you. Answer a few simple questions — there are no wrong answers. You don’t need to know any product names.

**Avoid at entry:** Sentinel, Guard, MCP, runtime, adapter, `POST /decision`, ports, schema — those are **ours** to translate, not **theirs** to memorize.

---

## The five questions (human-facing only)

Ask **one at a time** if that feels kinder; or all five if the human wants speed.

### 1. What are you trying to do?

- Run tools or helpers for myself  
- Move or save important data  
- Connect this machine to other systems  
- Try or test something  
- Something else — in your own words  

### 2. If it made a mistake, what could go wrong?

- Nothing serious — I’m just learning  
- Something could break or get messy  
- It could cost money or waste time  
- It could affect real people  

### 3. Where are you running this?

- On my own computer  
- On a server I control  
- In the cloud / many services  
- I’m not sure yet  

### 4. When something risky comes up, what do you want?

- Stop and ask me first  
- No — keep going unless it’s clearly unsafe  
- Only for the **big** actions — small stuff can move  

### 5. Are you bringing anything of your own?

- My own database or saved records  
- My own tools or integrations  
- My own AI / model  
- Nothing yet — I’m starting empty-handed  

That’s the whole entry ritual.

---

## What the human should hear back (plain English)

Before any commands, summarize in **their** words:

- What we’re protecting  
- How careful the system will be  
- Whether we’ll pause and ask before sharp moves  
- What we’ll connect later (only if they said they have something)  

**Example:**

> You’re experimenting on your own computer, but a mistake could break something you care about. We’ll set things so **big or risky moves pause for you**, and small routine steps don’t nag you. We won’t plug in your database until you say you’re ready.

No stack diagram required.

---

## Example flows (stories, not configs)

### A — Learning on a laptop

- **Do:** try tools, learn  
- **Risk:** “could break something”  
- **Where:** my computer  
- **Pause:** yes before risky  
- **Bring:** nothing yet  

**Outcome in plain language:** Light guardrails at home; careful mode when the action could hurt files or settings; no extra services until they want them.

### B — Money or people at stake

- **Do:** connect systems / move data  
- **Risk:** money or real users  
- **Where:** server or cloud  
- **Pause:** yes, or only big actions  
- **Bring:** own database or tools  

**Outcome in plain language:** Stronger checks, logging so we can trace what happened, and no silent “go ahead” on high-stakes moves if something is wrong or unclear.

### C — Fast and local

- **Do:** test something  
- **Risk:** nothing serious  
- **Where:** my computer  
- **Pause:** no, unless clearly unsafe  
- **Bring:** nothing  

**Outcome in plain language:** Get running quickly; still never bypass the hardest safety rules baked into the lab — but **you** aren’t asked to name components first.

---

## Internal translation (for builders and agents — not for the opening line)

**This section maps answers → technical behavior.** Use it **after** the human has answered in plain language. Do **not** read this table aloud as the first thing.

| Human signal | Typical mapping (lab stack) |
|--------------|-------------------------------|
| “Stop and ask before risky” | Prefer **hold / review / escalate** paths for high-impact actions; wire **central decision** when available; never silently downgrade a **stop** signal. |
| “Only for big actions” | Map to **review** on high-impact envelope; keep narrow deterministic checks local (paths, obvious blocks). |
| “Could break something” / “cost money” / “affect people” | Treat as **high-risk surface**; fail **closed** when the decision service or posture feed is missing; prefer **joinable IDs** in logs when DB is enabled. |
| “My computer” | Local dev: default ports and localhost; see [`FIRST-RUN.md`](FIRST-RUN.md) when you’re ready for commands. |
| “Server / cloud” | Bind addresses, secrets, Postgres for durable audit — see [`ENDPOINTS-AND-DECISIONS.md`](ENDPOINTS-AND-DECISIONS.md) BYO section. |
| “Own tools / connect systems” | Normalize actions into the **decision envelope** for protected routes; document MCP/tool wiring in technical docs **after** placement. |
| “Own database” | Governance rows optional; **correlation id** for joins — [`ENDPOINTS-AND-DECISIONS.md`](ENDPOINTS-AND-DECISIONS.md). |
| “Own AI / model” | Posture and ingest layers are swappable; **wire vocabulary** for decisions stays in one place — same doc. |

**Names you use only after placement:** live posture service (often **maat-sentinel** on **4242**), decision API (**Tehuti Guard** on **8013**), local fast checks (**maat-immune** in **maat-runtime**). The human still doesn’t need the names unless they want them.

---

## Order of layers (Ma’at alignment)

1. **Human** — intent, risk, care, place (simple words).  
2. **Translation** — agent maps answers → config and routes (this file + internal table).  
3. **System** — services, contracts, and enforcement run as designed — [`SYSTEM-CONNECTIONS.md`](SYSTEM-CONNECTIONS.md).

Truth for evaluation still comes from cases and review — [`TRUTH-AND-VERIFICATION.md`](TRUTH-AND-VERIFICATION.md) — but that is **not** part of day-one initiation for a new person.

---

## Validation ritual (one clean pass — do this next)

Design is closed until a **real human** stress-tests the entry. **No intervention** during the pass.

**Give them only:** this file (`docs/INITIATION.md`). No other docs, no verbal setup, no hints.

**Watch for (signals):**

1. **First question they ask** — biggest clarity leak.  
2. **First hesitation** — first friction point.  
3. **First wrong assumption** — translation gap.  
4. **When they reach for dev or product names** — “no jargon at entry” broke somewhere (in this file or in what they were given besides it).  
5. **Whether they can say “I know what to do next”** — not full stack mastery; enough to feel **guided**.

**Record (enough to improve, not a transcript):**

- **Three** confusion points  
- **Two** hesitation moments  
- **One** wrong mental model  

**Success looks like:** they did not need to ask “what is this system?” in order to answer the five questions; they did not **need** internal names to feel placed; they felt **guided**, not lost.

Improve the doc from **where they broke**, not from where you think it is already good.

---

## Related

- [`SETUP-WITH-AGENT.md`](SETUP-WITH-AGENT.md) — when the human **wants** prompts and technical link order  
- [`FIRST-RUN.md`](FIRST-RUN.md) — commands after placement  
- [`TEHUTI-SENTINEL-GUARD-ADAPTER-CONTRACT.md`](TEHUTI-SENTINEL-GUARD-ADAPTER-CONTRACT.md) — authority boundary (for builders)  
