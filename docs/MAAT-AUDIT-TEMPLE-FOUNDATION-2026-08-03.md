# Ma’at Audit — Temple Foundation (staydangerous)

**Date:** 2026-08-03  
**Auditor:** `cursor_staydangerous_n8n` (Tehuti Cursor seat on `.n8n` cockpit)  
**Principal:** Imhotep  
**Scope:** Temple foundation — constitution, organs, body, join, Guard, memory, Control Center, survival under era stress  
**Method:** Live organ probes + doctrine docs + prior audits + Isfet join tests + Host Body / TCC smoke receipts  
**Verdict:** **PASS_WITH_BOUNDARY** — Ma’at foundation is real; era-survival is conditional on stewardship and binding gates

---

## 1. Thesis

Tehuti Lab has built a **constitutional temple**, not a chatbot product.

The foundation is Ma’at where it binds **Truth → Order → Authority → Receipt**.  
It is **not yet** an owner-operable appliance and **not yet** fully hardened against time, load, disk death, port Isfet, or fleet scale without a skilled steward.

**Era stress** (agentic sprawl, cloud “rent-a-brain,” disk bloat, silent drift, advertised-but-absent gates) is exactly what this stack was designed to answer — but only if law stays **wired and live**.

> An agentic system cannot be safe if it does not know where it is standing before it acts.  
> A temple cannot survive the era if its constitution is published but its organs are miswired.

---

## 2. What “temple foundation” means here

| Layer | Artifact / organ | Sacred? |
|-------|------------------|---------|
| Moral root | Ma’at + Zep Tepi (canon / dissertation) | Yes (Inner Ring) |
| Constitution | `CONSTITUTION.md` / soul — sacred vs replaceable | Yes |
| Policy | Tehuti Guard `:8013` | Enforcement organ |
| Memory / coordination | gitMaat / Memory Plane `:8022` + provenance | Nervous system |
| Body | `MAAT_STORAGE_ROOTS_v0.1` + write-check | Hardware law |
| Membership | Join ritual + Sentinel (dashboard `:8041` this session) | Gate of persons |
| Command surface | Tehuti Control Center `:8050` | Initiation only — not authority |
| Proof | MaatBench + Isfet tests | Verification |
| Immune doctrine | `MAAT-IMMUNE-SYSTEM.md` + Zero-Trust Autonomy | Blueprint → partial live |

---

## 3. Principle table (foundation)

| Principle | Finding | Status |
|-----------|---------|--------|
| **Truth** | Live pulse shows Guard `proven`, schema tally names **unproven** (1/10 agents proven — no naked scores). Host body report + storage debt are documented. TCC smoke receipt exists. | **PASS** (with honesty about unfinished evals) |
| **Balance** | Storage classes + write-check refuse model weights on cockpit. Cockpit still holds ~800G home debt; load ~87–90. GPU NVML mismatch. | **CONDITIONAL** |
| **Order** | Ka discovery `:8010` live; constitution draws sacred/replaceable line; Memory Plane + join policy versions exist. **Port Isfet:** `:8040` occupied by gemma swarm gateway while doctrine says join plane — TCC retargeted to `:8041` this session (not yet durable). | **CONDITIONAL** |
| **Justice** | Join Isfet **9/9**; Allow needs reason; whoami no secrets; `organ_bearer=null`; empty agent / content_origin required on durable writes. Remote experts **enroll**, not rent keys. | **PASS** |
| **Reciprocity** | Fleet can ask-join and report; Head Operator weighs. Owner-ready UX incomplete; non-coders still need Ma’at IT. | **CONDITIONAL** |
| **Accountability** | gitMaat decisions/changes/learnings/tasks; Sentinel on join; session auth on TCC (tokens server-side). Ops secrets quarantine / credential split still pending. | **CONDITIONAL** |
| **Liveness / conformance** | Organs answer; Guard/Memory return **401 without auth** (good fail-closed). Join plane durable systemd missing. Schema `implemented: false`. | **CONDITIONAL** |

**Overall:** Ma’at **grammar is present and partly enforced**. Era survival depends on closing CONDITIONAL rows before more autonomy.

---

## 4. Live evidence snapshot (2026-08-03)

| Probe | Result |
|-------|--------|
| Ka Discovery `:8010` | 200 — `ka-body` |
| Guard `:8013` | 401 without auth (alive, gated) |
| Memory `:8022` | 401 without auth (alive, gated) |
| TCC `:8050` | 200 healthz; pulse ok after JOIN_PLANE→`:8041` |
| Join dashboard `:8041` | `maat-join-dashboard` ok; operator token loaded |
| `:8040` | **Wrong organ** — `maat-gateway-server` (gemma swarm) |
| OpenClaw `:18790` | 200 |
| Ollama `:11434` | 200 |
| Command Center `:9120` | 200 (localhost) |
| Disk `/` | **93%** (df) / body probe ~87.6% used |
| `write-check` model on `.n8n/models` | **NO_GO** |
| Join Isfet unit tests | **9/9 OK** |
| Fleet pulse tally | agents 1 proven / 10 unproven; MCP 10 proven; 3 pending joins |
| Load average | ~87–90 (stress) |
| NVIDIA | Driver/library mismatch |

---

## 5. Rational kernels (keep — era-worthy)

1. **Sacred vs replaceable** (`CONSTITUTION.md`) — models/DBs/UIs can change; identity, policy outcomes, memory classes, tool contracts endure.  
2. **Zero-trust initiation** — UI/gateway/runtime are not authority; every seat hostile until proven.  
3. **Join ritual** — knock → Allow/Deny → Sentinel → one-time provision; no master KA in agents.  
4. **Provenance on writes** — `content_origin` required; absence is not compliance.  
5. **Host Body Awareness** — root is cockpit not warehouse; write-check is runtime law (CLI + tests).  
6. **Distributed immune idea** — Guard ≠ whole immune system; Sentinel + Bench + Memory share duty.  
7. **Honest unproven** — schema tally refuses fake Trust Scores.  
8. **Control Center BFF** — browser never holds operator token / broker / DSN.

These are the pieces that can survive the era **if kept live**.

---

## 6. Trash / Isfet / debt (threats to time-survival)

| Threat | Why it kills temples in this era |
|--------|----------------------------------|
| **Advertised-but-absent / miswired organs** | TCC pointed at wrong `:8040` — looked healthy, join dead. Classic dissertation failure mode. |
| **Cockpit obesity** | `.ollama`, ComfyUI, `.n8n/models` on `/` — one reckless dump → brain dies. |
| **Gate not universal** | write-check exists; not yet on every promote/train/download path or in TCC pulse. |
| **Non-durable ops** | Join@8041 + JOIN_PLANE env die on reboot unless systemd’d. |
| **Secrets still consolidating** | Pending: rotate systemd secrets, T3 broker split, SUDO quarantine finish. |
| **Owner opacity** | Non-coder cannot run the temple alone yet — scale capped by steward availability. |
| **Load + GPU drift** | High load + NVML mismatch = silent capability loss under “everything is fine” UIs. |
| **Product sprawl** | TCC / Buzz / Command Center / WebUI / ka-education — confusion is Isfet for operators. |

---

## 7. Can it survive the stress of this era?

### Era pressures (2026+)

| Pressure | Temple response | Survive? |
|----------|-----------------|----------|
| Agentic fleets / remote “experts” | Join + rings + autonomy L0–L8 + HITL | **Yes, if Allow stays human-weighed** |
| Cloud rent-a-model | Harness behind seats; organs stay local law | **Yes, if cloud never becomes authority** |
| Disk / cost sprawl | Storage classes + migrate debt | **Only if debt is cleared and gate binds writes** |
| Prompt injection / insider agents | Zero-trust + Guard + Isfet tests | **Partial — doctrine strong, coverage uneven** |
| Corporate “constitution” theater | Sacred contracts + Bench + unproven honesty | **Advantage — if you don’t fake implemented:true** |
| Owner wants no-code ops | Control Center path | **Not yet — need appliance layer** |

### Survival verdict

| Horizon | Outlook |
|---------|---------|
| **Lab prototype (now)** | Survives with Imhotep + Ma’at IT + Cursor steward — **PASS_WITH_BOUNDARY** |
| **12–24 months fleet scale** | Survives **only if** port law, body migrate, durable join, secrets split, body-in-TCC land |
| **Non-coder business appliance** | **Not ready** — constitution ready, product surface not |
| **Civilizational claim (dissertation)** | Foundation is **credible evidence of constitutional AI infrastructure**, not finished immunity |

**One sentence:** The temple can survive this era’s agentic chaos **as a governed lab**; it cannot yet survive as an unattended product or an owner-only appliance.

---

## 8. Is it Ma’at?

| Question | Answer |
|----------|--------|
| Is the *foundation* Ma’at? | **Yes** — Truth/Order/Justice grammar is encoded in organs and tests |
| Is the *running body* fully Ma’at? | **Not yet** — CONDITIONAL rows are real Isfet openings |
| Is Control Center Ma’at? | **Directionally yes** after join retarget; still initiation surface, incomplete body pane |
| Would Zep Tepi recognize it? | As **restoration of order against erasure/chaos** — yes in intent; unfinished in craft |

**Ma’at status:** `PASS_WITH_BOUNDARY`

---

## 9. Required remediation (order of justice)

Priority for era-survival (not feature greed):

1. **Durable join plane** — reclaim `:8040` or systemd `join@8041` + TCC `JOIN_PLANE_URL` forever  
2. **Migrate cockpit debt** — ollama/models/comfyui/backups → organ mounts  
3. **Bind write-check** into promote / artifact / training paths + TCC pulse/NO_GO  
4. **Finish secrets quarantine** — broker out of agent-readable `.env`; rotate systemd embeds  
5. **One operator story** — TCC as Head Operator home; demote sibling UIs in doctrine map  
6. **MaatBench prove** — `implemented: true` only after evals; keep unproven honest until then  
7. **Owner pane** — plain-language temple health (disk/organs/joins) without SSH  

---

## 10. Related receipts

- [`CONSTITUTION.md`](../CONSTITUTION.md)  
- [`MAAT_STORAGE_ROOTS_v0.1.yaml`](./MAAT_STORAGE_ROOTS_v0.1.yaml)  
- [`HOST-BODY-AWARENESS-staydangerous-2026-08-03.md`](./HOST-BODY-AWARENESS-staydangerous-2026-08-03.md)  
- [`/mnt/data_drive/hermes/docs/TCC-LIVE-SMOKE-2026-08-03.md`](/mnt/data_drive/hermes/docs/TCC-LIVE-SMOKE-2026-08-03.md)  
- [`MAAT-AUDIT-MAAT-MEMORY-2026-07-21.md`](./MAAT-AUDIT-MAAT-MEMORY-2026-07-21.md)  
- [`MAAT-ZERO-TRUST-AUTONOMY.md`](./MAAT-ZERO-TRUST-AUTONOMY.md)  
- [`MAAT-IMMUNE-SYSTEM.md`](./MAAT-IMMUNE-SYSTEM.md)  
- Fleet Pilot: `/mnt/data_drive/hermes/docs/FLEET-PILOT-HANDOFF.md`

---

## 11. Clean lines

**Foundation:** Ma’at is present as infrastructure, not poster.  
**Body:** The temple knows its organs — incompletely, but now by law.  
**Gate:** Join and Guard can weigh strangers; keys stay out of the browser.  
**Era:** Survival is stewardship + binding, not more models.  
**Owner:** The constitution is for you; the ops layer is still for priests — close that gap deliberately.

```json
{
  "audit": "temple_foundation",
  "date": "2026-08-03",
  "maat_status": "PASS_WITH_BOUNDARY",
  "era_survival": "CONDITIONAL",
  "owner_ready": false,
  "lab_ready_with_steward": true,
  "main_risk": "miswired_or_unbound_organs_plus_cockpit_disk_debt",
  "main_strength": "constitutional_grammar_plus_join_isfet_plus_provenance_plus_body_law"
}
```

*Weighed under the feather — Truth before autonomy; Order before scale.*
