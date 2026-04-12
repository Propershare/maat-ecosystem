# Ma’at audit → action plan

**Purpose:** Single checklist for **truth, order, balance**, and execution — not more philosophy.

---

## 1. Truth — one canonical tree

| Status | Action |
|--------|--------|
| **Done** | Canonical Ka-body: **`maat-ecosystem/`** — root [`README.md`](../README.md) states this. |
| **Done** | Root-level standalone copy (`maatbench/`, etc.) marked **legacy** — [`archive/README.md`](../archive/README.md), [`maatbench/README.md`](../maatbench/README.md). |

**Goal:** One obvious “what is real” for new contributors.

---

## 2. Order — entry obvious

| Status | Action |
|--------|--------|
| **Done** | Root [`README.md`](../README.md) lists **INITIATION → FIRST-RUN → ENDPOINTS** + product map. |

**Goal:** No one asks “where do I start?”

---

## 3. Balance — no parallel development on legacy

| Status | Action |
|--------|--------|
| **Policy** | Root legacy dirs are **read-only** for new features; extend **`maat-ecosystem/`** only. |

**Goal:** No silent drift between two benches.

---

## 4. Initiation — validate, don’t redesign

| Status | Action |
|--------|--------|
| **Open** | Run [`INITIATION.md`](INITIATION.md) validation ritual with a **real user** (no hints). |

**Goal:** Evidence, not more doc churn.

---

## 5. Contract alignment — wire vocabulary

| Status | Action |
|--------|--------|
| **Done** | Guard wire: `allow` \| `deny` \| `review` \| `quarantine` \| `escalate` — [`ENDPOINTS-AND-DECISIONS.md`](ENDPOINTS-AND-DECISIONS.md). |
| **Done** | **`conditional`** = explanation / label only — [`TEHUTI-SENTINEL-JUDGMENTS.md`](TEHUTI-SENTINEL-JUDGMENTS.md) §Pressure path. |

**Goal:** Adapters never invent a fifth wire value.

---

## 6. Runtime — one end-to-end path (open)

| Status | Action |
|--------|--------|
| **Open** | One path: **adapter → `POST /decision` → enforce → log `correlation_id`** (tool call *or* shell — pick one). |

**Goal:** Prove the loop once.

---

## 7. Test — real Ma’at test (open)

| Status | Action |
|--------|--------|
| **Open** | Give **only** [`INITIATION.md`](INITIATION.md); record 3 confusion points, 2 hesitations, 1 wrong model. |

---

## Final state target

- One repo truth (`maat-ecosystem/` + honest legacy note)  
- One entry path (root README)  
- One decision vocabulary (wire terms)  
- One working runtime path (pending)  
- One real user test (pending)  

---

## Related

- [`MAAT-PRODUCT-MAP.md`](MAAT-PRODUCT-MAP.md)  
- [`TEHUTI-SENTINEL-GUARD-ADAPTER-CONTRACT.md`](TEHUTI-SENTINEL-GUARD-ADAPTER-CONTRACT.md)  
