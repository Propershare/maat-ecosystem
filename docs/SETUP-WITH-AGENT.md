# Set up Tehuti with an agent (human-first)

**Purpose:** Documentation that behaves like a **good installer** — not only reference material. You should not have to read every doctrine file before your first tool call.

**Ma’at entry (no jargon):** If the human should **not** see product names or dev terms at the door, start with **[`INITIATION.md`](INITIATION.md)** — five plain questions, then translation. **This page** is for when you already want **component names**, copy-paste prompts, and ordered technical links.

**If you’re the human:** copy a **starter prompt** below into your agent, or answer the **six questions** so the agent can narrow the path.

---

## What the agent should do first

Do **not** open with full architecture. Open with:

> I can set up Tehuti with you in a few steps. I need a few facts (local vs prod, what you already run, whether you want Sentinel as a service, and what matters most). Then I’ll give you exact commands and only the docs you need.

---

## Six initiation questions (agent asks; human answers)

| # | Question | Why it matters |
|---|------------|----------------|
| 1 | **Where?** `local dev` · `staging` · `production` | Ports, bind addresses, fail posture |
| 2 | **What do you already have?** `OpenClaw` · `maat-runtime` · `MCP tools` · `PostgreSQL` · `none yet` | What to wire vs install |
| 3 | **What role for Tehuti?** `local guard only` · `Sentinel + Guard stack` · `not sure` | Whether to run **maat-sentinel** (4242) + **Guard** (8013) or adapters only |
| 4 | **Separate Sentinel service?** `yes, Python sidecar` · `no, local heuristics only` · `not sure` | Confirms **POST /decision** path vs **maat-immune**-only |
| 5 | **Bring your own?** `database` · `model/brain` · `tools/MCP` · `none` | BYO section in endpoints doc |
| 6 | **Priority?** `easiest setup` · `strongest safety` · `low latency` · `eval/research` · `production readiness` | Order of rollout |

**Optional drill-down** (only if needed):

- What are you trying to protect first? `tool calls` · `shell` · `memory writes` · `external MCP` · `all`
- **Environment:** `laptop` · `single server` · `Docker` · `cloud / multi-service`

---

## Two modes (agent)

| Mode | When |
|------|------|
| **Quick setup** | Minimal questions → get **Guard + Sentinel** healthy with one `/decision` and a correlation id (see [`FIRST-RUN.md`](FIRST-RUN.md)). |
| **Guided** | More questions → map to connections, BYO, and production fail-closed rules. |

---

## Copy-paste prompts for humans (tell the agent this)

### Fast start (local)

```
I want a local Tehuti setup: OpenClaw (or maat-runtime), Python Sentinel + Tehuti Guard on default ports, local MCP tools, no external Postgres yet. Route high-impact tool calls to POST /decision with joinable correlation IDs; keep simple path checks local. Walk me through commands only—link me to first run and endpoints in order.
```

### Production-oriented

```
I want Tehuti Guard for a production-style path: Postgres for governance rows, joinable correlation IDs everywhere, fail-closed high-risk routes when Guard or Sentinel is down, documented timeouts (client-side). No silent downgrade of escalate. Point me to endpoints + connections; skip philosophy.
```

### BYO brain / tools

```
I want to bring my own model or ingest for Sentinel posture, keep TypeScript adapters in-process where possible, and preserve the wire decision contract (allow | deny | review | quarantine | escalate). Tell me what I must not violate and which docs define BYO.
```

---

## What the agent should return after you answer

1. **Plain-language summary** — One paragraph: environment, what runs where, what is out of scope for this pass.  
2. **Exact next steps** — Numbered: e.g. start Sentinel → start Guard → `curl /health` → sample `POST /decision` → verify `correlation_id`.  
3. **Links in order** — Usually **three**, not ten:

| Order | Doc |
|-------|-----|
| 1 | [`SYSTEM-CONNECTIONS.md`](SYSTEM-CONNECTIONS.md) — what talks to what |
| 2 | [`FIRST-RUN.md`](FIRST-RUN.md) — bootstrap curls |
| 3 | [`ENDPOINTS-AND-DECISIONS.md`](ENDPOINTS-AND-DECISIONS.md) — wire vocabulary + tables |

**Only if needed:**

- [`TRUTH-AND-VERIFICATION.md`](TRUTH-AND-VERIFICATION.md) — labeled cases vs MaatBench  
- [`TEHUTI-SENTINEL-JUDGMENTS.md`](TEHUTI-SENTINEL-JUDGMENTS.md) — Sentinel office + schema  
- [`TEHUTI-SENTINEL-GUARD-ADAPTER-CONTRACT.md`](TEHUTI-SENTINEL-GUARD-ADAPTER-CONTRACT.md) — adapter vs judgment boundary  

---

## Defaults if you say nothing

| Topic | Reasonable default |
|-------|---------------------|
| Ports | Sentinel **4242**, Guard **8013** ([`MAAT-PRODUCT-MAP.md`](MAAT-PRODUCT-MAP.md)) |
| First goal | **`GET /health`** + one **`POST /decision`** with echoed **`correlation_id`** |
| Adapters | **maat-immune** is **local-only** until wired — do not assume OpenClaw calls Guard HTTP |

---

## Simplest agent opening (copy for agent system prompt or template)

```
I can help you set up Tehuti in a few steps. Tell me:
(1) local, staging, or production
(2) what runtime you already have (OpenClaw, maat-runtime, none)
(3) whether you want Sentinel as a separate Python service
(4) whether you’re bringing Postgres, your own model, or custom MCP
(5) whether you want easiest setup or strongest enforcement first

Then I’ll give you exact commands and 2–3 doc links in order—not the whole library.
```

---

## Related

- [`FIRST-RUN.md`](FIRST-RUN.md)  
- [`AGENTS.md`](../AGENTS.md) — lab root, OpenClaw workspace  
