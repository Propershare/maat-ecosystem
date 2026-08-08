# Handoff: UKMT canon + Ka Education backend → UI

Use this document to **review what exists** before the UI developer wires anything. Nothing here *requires* embedding heavy content in the marketing site on day one.

---

## What was built (summary)

### A. Ka Education Backend (`ka-education-backend/`)

- **Stack:** Fastify, Prisma, PostgreSQL, JWT, OpenAPI at `/docs`.
- **DNA:** Root `MANIFEST.ka` for this body (`ka-education-body`).
- **Nine organs:** Exposed as HTTP route groups (`/soul`, `/skeleton`, `/memory`, `/voice`, `/ka`, …) — see repo `README.md`.
- **UKMT pipeline in DB:** Each `StageDefinition` row is seeded from the **University of KMT** primary table (Preschool / K–12 → Post-PhD), with:
  - `canonReference` = `UKMT_EDUCATION_PIPELINE_TABLE_V1`
  - `stepwiseBuildActions` = the “build actions” checklist column
  - Full text fields: institutional form (incl. translit → English), core purpose, curriculum/pedagogy split, credential/cadre, transitions, Maat obligations, etc.

### B. Canon files (primary source mirror)

| Path | Purpose |
|------|---------|
| `ka-education-backend/docs/canon/README.md` | Explains canon vs 42 nomes vs Maat evaluation |
| `ka-education-backend/docs/canon/UKMT_EDUCATION_PIPELINE.md` | Text table mirror for quick read / diffs |
| `ka-education-backend/docs/canon/UKMT_PIPELINE_TABLE.png` | Raster of the source graphic |

### C. Constitution pointer

Seed constitution (`1.0.0`) explicitly references the canon paths and tag `UKMT_EDUCATION_PIPELINE_TABLE_V1`, and states **do not flatten**: nine stages ≠ 42 nomes ≠ Maat score layer.

### D. API endpoints the UI can consume

**Public / low friction**

- `GET /health` — boot + DB + active constitution
- `GET /manifest` — YAML + parsed JSON for `MANIFEST.ka`
- `GET /soul/constitution` — active constitution text
- `GET /skeleton/stages` — **all stage rows including `stepwiseBuildActions` and `canonReference`**
- `GET /skeleton/stages/:code` — single stage (same fields)
- `GET /soul/nomes` — structural nome registry (42 entries in seed)
- `GET /soul/maat/principles` — **evaluation-layer** principles (labeled in API as not structural)

**Auth typically required** (JWT from `POST /auth/login`)

- Dashboard-style: `GET /voice/dashboard/overview`, etc.
- Writes: institutions, learners, enrollment, progression, …

**OpenAPI:** `GET {API_BASE}/docs` after backend is running.

---

## Do we need to embed this in the UI?

**Not as a hard requirement.** Three sane options:

| Approach | When to use |
|----------|-------------|
| **1. Link out only** | Marketing site stays light: one sentence + link to canonical `.md` or a “Canon” page in docs. |
| **2. Thin section + API** | MAAT Studio / education app calls `GET /skeleton/stages` and renders a **filterable table** or accordion (title, institution line, build actions). Source of truth stays the backend. |
| **3. Full static embed** | Duplicate long copy or PNG in `index.html` — **not recommended** (drift vs DB/canon files). If you need offline marketing PDF, export from canon `.md` / PNG intentionally. |

**Recommendation:** **(2) for product UIs**, **(1) for the public Ka landing** — one new nav item e.g. “Education pipeline” or “UKMT canon” pointing to hosted docs or a minimal page that **fetches** stages when the API URL is configured.

---

## Where on the existing site (`maat-ecosystem/site/index.html`)

Rough map (no code changes in this handoff — for your UI dev):

1. **Public static site** (`site/index.html`)
   - Add a short **#education** or **#ukmt-pipeline** section: one paragraph + link to `ka-education-backend/docs/canon/UKMT_EDUCATION_PIPELINE.md` (if docs are published) **or** to your GitBook / Replit docs.
   - Optional: thumbnail + link to `UKMT_PIPELINE_TABLE.png` (“View primary source table”).

2. **MAAT Studio / Replit app** (operational UI)
   - **Settings:** “Education API base URL” + optional API key.
   - **Screen:** “Pipeline stages” = `GET /skeleton/stages` rendered as cards (institution line, build actions, Maat obligations collapsed).
   - **Governance:** “Constitution” tab = `GET /soul/constitution`.

3. **Ka landing (Replit)** you already have  
   - Align copy: **nine organs** (architecture) vs **nine pipeline stages** (UKMT product) — use labels so visitors don’t confuse them with **42 nomes**.

---

## Checklist for UI developer

- [ ] Confirm **API base URL** and CORS if browser calls API directly.
- [ ] Prefer **SSR or BFF** if you want to hide JWT from the browser for dashboard routes.
- [ ] Display **`canonReference`** somewhere in dev/stage admin UI for traceability.
- [ ] Never show a single number like “49/42” without label: **structure vs evaluation**.
- [ ] Long table content: **render from API** or **from published markdown**, not duplicated by hand in HTML.

---

## Files to open for review

1. `ka-education-backend/README.md` — how to run API + quick endpoints  
2. `ka-education-backend/docs/canon/UKMT_EDUCATION_PIPELINE.md` — human-readable canon  
3. `ka-education-backend/prisma/seed.ts` — exact seeded strings (search `STAGE_SEEDS`)  
4. `ka-education-backend/prisma/migrations/` — schema additions for `canonReference`, `stepwiseBuildActions`  

---

## Changelog (what changed for UKMT)

- Added `docs/canon/` with PNG + markdown + README.  
- Extended `StageDefinition` with `canonReference` and `stepwiseBuildActions`.  
- Replaced generic stage seed text with **UKMT-aligned** institutional names (hwt-mꜣꜥt, pr-mꜣꜥt, pr-ꜥnḫ, Per-Ankh, pr-ꜥnḫ-wr, Council of Sesh, etc.) and build-action lists.  
- Constitution body updated to cite canon.  
- `GET /skeleton/stages` returns the new fields.  

---

*Prepared for Imhotep / Tehuti Lab — review before UI integration.*
