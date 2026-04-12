# Tehuti Sentinel / Guard adapter contract

**Status:** Draft (canonical boundary for the lab).  
**Resolves:** Tehuti Guard is **not** one monolith — it is a **layered system**: Sentinel (judgment), adapters (interceptors), policy/schema/evals (contract).

---

## 1. Purpose

This contract defines the boundary between:

- **Tehuti Sentinel** — authoritative constitutional judgment service  
- **Guard adapters** — local runtime interceptors and heuristics in Node/TypeScript (and similar) environments  

**Goals:** centralized judgment, local performance, auditable authority boundaries.

---

## 2. Source of truth

**Wire authority** for Tehuti Guard v1 is the **`decision`** field from **`POST /decision`** — canonical values:

`allow` | `deny` | `review` | `quarantine` | `escalate`

**Doctrine** sometimes uses **“conditional”** for “only if gates pass.” That is **not** a separate wire value today. Map it to **`review`** (human / gate) or **`quarantine`** (hold / isolate) per [`ENDPOINTS-AND-DECISIONS.md`](ENDPOINTS-AND-DECISIONS.md) §1.

**Posture / machine truth** for Guard comes from **maat-sentinel** `unified_view` (Sentinel is authoritative for **live posture**; Guard combines it with rules).

Local adapters may perform pre-checks, but they **do not** redefine wire **`decision`** meanings.

---

## 3. What must go through Python `/decision`

The following requests **must** be sent to Sentinel for judgment:

- High-impact tool calls  
- Memory writes intended to become durable  
- Retrieval results that may alter plan or authority  
- Shell execution beyond a safe local allowlist  
- Plugin / MCP calls with external side effects  
- Scope drift or cross-repo / cross-domain operations  
- Any action that may require human escalation  
- Any case where local heuristics return uncertain / mixed signal  

*(Implementation: Tehuti Guard v1 HTTP API — see `tehuti-guard/guard/README.md`.)*

---

## 4. What may stay local in TypeScript

Adapters may decide **locally** only for narrow, deterministic checks such as:

- Path allowlist / denylist  
- Static pattern blocks  
- Rate limits  
- Schema validation  
- Safe read-only commands on explicit allowlist  
- Transport-level hygiene  
- Clearly invalid requests that never require constitutional interpretation  

These are **heuristics and enforcement gates**, not the constitutional brain.

---

## 5. Escalation rule

If a local adapter **cannot prove** a request is safely resolvable by deterministic rules, it must:

- call Sentinel `/decision`, or  
- **hold** the action  

Adapters must **never** guess past ambiguity.

---

## 6. Authority hierarchy

**Order of authority:**

1. Hard policy / deterministic rule  
2. **`POST /decision`** result (Guard v1 combines **maat-sentinel** posture + rules)  
3. Adapter convenience logic  

**Meaning:**

- Local code may **block faster** than calling Guard.  
- Local code may **not** silently **weaken** the structured **`decision`** from **`/decision`**.  
- If Guard returns **escalate**, the adapter cannot downgrade to **review**, **quarantine**, or **allow**.

---

## 7. Review / quarantine handling (“conditional” in doctrine)

If Guard returns **`review`** or **`quarantine`** (doctrine: **conditional** proceed-only-with-gates), the adapter may execute **only if**:

- All stated machine-checkable gates pass (use **`blocking_actions`** from the response and posture context as hints, not as a substitute for **`decision`**)  
- The checks are logged  
- No local rule contradicts the action  

If gates fail, execution stops.

---

## 8. Explain surface

- **`/explain`** — advisory and diagnostic.  
- **`/decision`** — operational.  

No adapter should treat explanation text as executable authority instead of the **structured** decision.

---

## 9. Logging and joins

Every request sent to Sentinel should carry:

- Request id  
- Policy version  
- Surface type  
- Actor / session role  
- Correlation id when available  

Adapter logs and Sentinel logs must be **joinable**.

---

## 10. Schema alignment

Sentinel inputs and outputs should map cleanly to the **`tehuti_sentinel_case`** structure where practical (`maat:tehuti_sentinel_case:v1`):

- `surface`, `input`, `context`, `evidence`, `label`, `outcome`  

That keeps runtime decisions compatible with review, eval, and MaatBench later.

---

## 11. Failure posture

If **Guard** is unreachable or **Sentinel** is unreachable (Guard may still return **`review`** with `sentinel_unreachable` — adapters must treat non-`allow` as **hold** for high-impact work):

- High-risk actions default to **hold** / **escalate**  
- Low-risk deterministic **denies** still deny  
- Low-risk local **allows** may proceed **only** if explicitly approved by policy  

**No** silent fail-open for high-impact actions.

---

## 12. Design principle

> **Adapters intercept. Sentinel judges. Rules enforce. Humans arbitrate the highest-risk edge cases.**

---

## Related

- [`SYSTEM-CONNECTIONS.md`](SYSTEM-CONNECTIONS.md) — who calls whom  
- [`ENDPOINTS-AND-DECISIONS.md`](ENDPOINTS-AND-DECISIONS.md) — wire vocabulary, endpoints, BYO  
- [`FIRST-RUN.md`](FIRST-RUN.md) — bootstrap curl path  
- [`TEHUTI-SENTINEL-JUDGMENTS.md`](TEHUTI-SENTINEL-JUDGMENTS.md) — office, schema, cases  
- [`TRUTH-AND-VERIFICATION.md`](TRUTH-AND-VERIFICATION.md) — truth vs verification  
- [`../tehuti-guard/guard/README.md`](../tehuti-guard/guard/README.md) — `/decision`, `/explain`, logging  
