# MAAT Audit — Tehuti Guard repo structure repair

**Purpose:** Record the constitutional repair that separated **Git ownership** and **delivery paths** for two distinct products both named “Tehuti Guard” in conversation. **No philosophy** beyond what is evidenced.

---

## Truth

The **lab Guard** (Python HTTP decision API and private TS helpers) in **`maat-ecosystem`** at [`tehuti-guard/`](../tehuti-guard/) and the **npm MCP security proxy** in **`Propershare/tehuti-guard`** are **distinct products** with **distinct Git ownership** and **distinct delivery paths**.

- **Lab:** versioned in the monorepo; operators install the Python API from `tehuti-guard/guard/` per [`tehuti-guard/guard/README.md`](../tehuti-guard/guard/README.md).
- **npm product:** developed and published from a **separate clone** of the GitHub repo, not from the monorepo tree as a substitute source.

Canonical disambiguation: [`TEHUTI-GUARD-PRODUCTS.md`](TEHUTI-GUARD-PRODUCTS.md).

---

## Order

The following **mechanical order** was applied:

1. **Nested repository removed:** `tehuti-guard/.git` deleted so the lab folder is no longer a repo-inside-a-repo.
2. **Parent ownership:** `tehuti-guard/` is tracked as normal paths under **`maat-ecosystem`** (`main`).
3. **Backup before migration:** operator-local directory pattern `backups/tehuti-guard-pre-monorepo-*` holding a **git bundle**, **working-tree patch**, **status/untracked lists**, and a **tree tarball** (excluding `node_modules` and `.git`). That path is **gitignored** so bundles do not enter the monorepo by accident.
4. **Gitignore protections:** root [`.gitignore`](../.gitignore) includes `tehuti-guard/node_modules/` and `backups/tehuti-guard-pre-monorepo-*/`.
5. **Canonical wording:** [`TEHUTI-GUARD-PRODUCTS.md`](TEHUTI-GUARD-PRODUCTS.md) updated with **Option A** (monorepo canonical for lab) and explicit separation from the npm repo.
6. **Pushed:** migration landed on `main` (e.g. commit `c1d8006` — *chore(tehuti-guard): vendor lab tree in monorepo, drop nested git*; prior E2E/docs work e.g. `b642f8b`).

---

## Balance

This migration **did not** collapse the two products into one repository or one binary.

- The **lab policy brain** (Python `POST /decision`) and the **npm MCP wrapper** remain **separate by design**.
- The main **ongoing** risk is no longer “which folder is Git root?” but **doctrinal drift**: the two codebases can diverge on **wire contract** unless deliberately synced.

---

## Evidence

| Item | Status |
|------|--------|
| Backup directory | Created under `backups/tehuti-guard-pre-monorepo-*` (local; gitignored) |
| Bundle and patch | `repo-all.bundle`, `working-tree.patch`, plus snapshot `tehuti-guard-tree-snapshot.tgz` |
| Canonical choice | Documented in [`TEHUTI-GUARD-PRODUCTS.md`](TEHUTI-GUARD-PRODUCTS.md) (Option A + “Canonical layout”) |
| Migration | Committed and pushed to **`Propershare/maat-ecosystem`** `main` |
| Tests | `python3 -m unittest discover` in `tehuti-guard/guard`; `pnpm test` in `tehuti-guard` — passing at time of repair |

### Runtime proof status (two layers — do not conflate)

**Repo-structure repair** and **runtime-proof maturity** are **different layers**.

- **Lab proof (narrow, real):** A reference path exists: [`scripts/guard_adapter_e2e_demo.py`](../scripts/guard_adapter_e2e_demo.py) — envelope → `POST /decision` → enforce → JSONL log with joinable **`correlation_id`**, documented in [`RUNTIME-HOOKUP.md`](RUNTIME-HOOKUP.md) and [`MAAT-AUDIT-ACTION-PLAN.md`](MAAT-AUDIT-ACTION-PLAN.md). The lab is **not** starting from zero on proof.
- **Production proof (open):** Extension into **real adapters**, **production logging**, and **real operating surfaces** (channels, IDE hooks, etc.) remains **incomplete** where it matters most for shipped behavior.

---

## Remaining risks

1. **Contract drift** between Python lab Guard and the npm MCP repo (vocabulary, envelope, correlation, fail posture, `policy_version`).
2. **Ambiguous “Tehuti Guard”** wording in docs or conversation without naming **which** product.
3. **Accidental mixed-repo development** — npm ship work done inside the monorepo tree or lab edits pushed to `Propershare/tehuti-guard` without intent.
4. **Demo proof ≠ production proof** — the narrow script proves the loop; it does not replace integration on live surfaces.

---

## Immediate next actions

1. Add **one short shared contract doc** (or a pinned section) covering: decision **vocabulary**, request **envelope**, **`correlation_id`** handling, **fail-open / fail-closed** posture, **`policy_version`** — kept aligned across lab Python and npm repo (with owners and review cadence).
2. **Disambiguate product wording** anywhere it still blends the two products.
3. Treat **separate clone for npm ship** as **standing law**, not a one-time cleanup (reinforce in onboarding / operator checklists).
4. **Extend** the demo path into **one real integrated path** on an operating surface you care about (then log and correlate like production).

---

## Judgment

This was a **constitutional repair**, not a cosmetic cleanup.

It did **not** finish Tehuti Guard as a **complete product** on every surface, but it **did** finish the **truth about where each Guard lives** and removed a **dangerous mixed-identity folder** in favor of a **governed structure**.

That is a **proper MAAT move** on the **truth/order** plane; **balance** and **discipline** must now be **maintained** through contracts and wording, not assumed from folder layout alone.

---

## Related

- [`TEHUTI-GUARD-PRODUCTS.md`](TEHUTI-GUARD-PRODUCTS.md)  
- [`ENDPOINTS-AND-DECISIONS.md`](ENDPOINTS-AND-DECISIONS.md)  
- [`TEHUTI-SENTINEL-GUARD-ADAPTER-CONTRACT.md`](TEHUTI-SENTINEL-GUARD-ADAPTER-CONTRACT.md)  
- [`RUNTIME-HOOKUP.md`](RUNTIME-HOOKUP.md)  
- [`MAAT-AUDIT-ACTION-PLAN.md`](MAAT-AUDIT-ACTION-PLAN.md)
