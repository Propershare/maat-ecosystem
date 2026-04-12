# UI copy — Maat Ecosystem strip (canonical)

Use this file as the **single source of truth** for the Ka intro landing page and MAAT Studio (Replit). Keep static `site/index.html` and Replit components aligned with this text.

## Headline

**Maat Ecosystem — reference body (Tehuti Lab)**

## Subhead (optional)

**Ka Architecture (framework) · Maat Ecosystem (implementation)**

## Lead sentence

Ka Architecture is the **pattern** — nine organs, one body, moral governance first. **Maat Ecosystem** is the **living codebase** that implements that pattern: nine organ directories, `MANIFEST.ka` as machine-readable DNA, and `maatbench/` as the constitutional doctor.

## Bullets (implementation pointers)

- **`MANIFEST.ka`** (repo root) — organ map; agents read this first.
- **`LAB-WORKSPACE.md`** — how this tree sits in the Tehuti Lab monorepo vs. a standalone `~/maat-ecosystem` clone.
- **`README.md`** — ecosystem overview, ports, boot narrative.
- **`maatbench/README.md`** — evaluation harness (“the doctor”) for Ka bodies.
- **`docs/WORKSPACE-KA-MAP.md`** (parent monorepo: `docs/` at lab root) — maps the full lab tree to the same nine-organ metaphor for day-to-day work.

## CTA

- **Public repo (when available):** `GITHUB_REPO_URL` — replace with your GitHub / Forgejo URL.
- **Private / local until then:** Tehuti Lab monorepo path: `…/maat-ecosystem/` (no public link required for the UI strip).

## Attribution (unchanged — framework lineage)

Ka Architecture methodology and attribution remain with **Dr. Tdka Kilimanjaro** and **University of KMT** as in `MANIFEST.ka` and the Ka landing narrative. Maat Ecosystem is the **reference implementation body** that runs on that architecture — not a replacement brand.

## Replit / React notes

- One scroll section + optional nav anchor `#ecosystem`.
- Style: reuse `--gold`, `--bg-card`, `--text`, `--text-dim` from `REPLIT-PROMPTS.md`.
- Do not vendor the full monorepo into Replit; **links + short copy only**.
