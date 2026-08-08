# Replit / Site Brief — Ma'at Constitutional Infrastructure (maatecosystem.com)

**Status:** Active brief — supersedes `maat-ecosystem/docs/REPLIT-CONTINUE.md`  
**Date:** 2026-06-18 (revised: product scope only)  
**Manuscript:** [`Maat-Constitutional-Infrastructure-Dissertation/manuscript/V1-MANUSCRIPT.md`](Maat-Constitutional-Infrastructure-Dissertation/manuscript/V1-MANUSCRIPT.md)

---

## What we are building (ONLY these on the public site)

1. **Ma'at** — constitutional principles for governed AI (truth, balance, order, justice, reciprocity, accountability)
2. **MaatBench** — verification layer (seven guarantee categories; tier + date on every score)
3. **Tehuti Guard** — policy gate (`POST /decision`)
4. **Maat Memory** — shared coordination / gitMaat (`:8022`, installable client)
5. **Wire contracts** — versioned Guard + Memory envelopes
6. **42 Laws of Ma'at for Technology** — interactive browser (dissertation Ch. 8)

**Do not build, mention, or link:** n8n, workflow automation, ComfyUI, swarm demos, vehicle assistants, RAG pipeline marketing, Ka body anatomy, UKMT scholar portal, or any legacy lab tool not in the list above.

---

## Purpose

Interactive site teaching **Ma'at as constitutional infrastructure** and **MaatBench** as proof — not a lab inventory or organ map.

---

## What this site is NOT

- Ka nine-organ body diagram hero
- UKMT education / nome / boot-sequence portal
- Static scroll-only page
- Advertisement for tools we retired or never productized

---

## Homepage hierarchy

| Block | Message |
|-------|---------|
| Hero | Ma'at as Constitutional Infrastructure |
| Principles | Six pillars (+ liveness as seventh engineering requirement) |
| Stack | Data → model → orchestration → memory → tools → monitoring (text layers) |
| Proof | MaatBench snapshot — **tier + ISO date** always visible |
| Frameworks | Tehuti Guard · Maat Memory · wire contracts |
| Laws | 42 Laws teaser → `/laws` |
| Lab | Dissertation case study — **Guard + Memory verified only** |

---

## Required interactivity

1. **Principle explorer** — each principle → engineering obligation + failure mode  
2. **MaatBench panel** — from `src/data/bench-snapshot.json`  
3. **Stack walkthrough** — constitutional layers with Guard/Memory callouts  
4. **42 Laws browser** — `src/data/laws-42.json` (seed from dissertation Ch. 8)  
5. **Lab evidence** — two badges only: **Tehuti Guard** and **Maat Memory** = verified in lab  

No "pending" laundry list of other systems on the public site.

---

## Tech

React 19 · Vite · Tailwind 4 · Express BFF · **PORT 3008**  
Repo: `https://github.com/Propershare/ka-education`  
Restore interactivity in **current** `src/App.tsx` — **never** restore commit `a6a1d37` or old Ka-body App (contains n8n, nine organs, scholar portal).

---

## Replit prompt (paste this)

```
Build maatecosystem.com — interactive Ma'at constitutional infrastructure site.

PRODUCT ONLY (nothing else on the site):
- Ma'at six principles (+ liveness as 7th engineering requirement)
- MaatBench (src/data/bench-snapshot.json — always show tier + date)
- Tehuti Guard, Maat Memory, wire contracts
- 42 Laws browser (dissertation Ch. 8)

DO NOT restore git commit a6a1d37 — that file has n8n and Ka body. Use src/App.tsx as-is from repo.

DO NOT mention or build UI for: n8n, ComfyUI, swarm, RAG pipelines, Ka body diagram, scholar portal, nomes, port 8015.

Read ka-education/docs/PRODUCT-SCOPE.md first.

Stack: React 19, Vite, Tailwind 4, Express on PORT 3008.
Visual: #000000 black, #8f0000 red, green + gold accents — mobile-first, subtle motion.
Label MaatBench panel: "Published lab snapshot" with tier + date — not live simulation.
Footer: UKMT lineage transparency (see brief) — not a UKMT official site.
```

---

## Visual language (operator palette)

**No indigo.** Deepest black, blood red, green, gold:

```css
--bg: #000000;
--red: #8f0000;
--gold: #c9a84c;
--green: #2d8f4e;
```

---

## UKMT / lineage (required transparency)

**This site is Tehuti Research Lab / MAAT Ecosystem — not an official UKMT product.**

> Independent project by Imhotep. We lean heavily on African-centered systems thinking and Ka methodology associated with Dr. Tdka Kilimanjaro and UKMT scholarship — that is **intellectual lineage**, not ownership or endorsement. Do not present this as the UKMT education portal.

---

## MaatBench — connected how?

| | |
|---|---|
| **Real scores?** | Yes — from `python3 -m maatbench.run` on the lab machine |
| **Live on every visit?** | No — static snapshot in `bench-snapshot.json` until refreshed |
| **Simulated / fake?** | No — forbidden. Label: **"Published lab snapshot"** + tier + date |

Optional later: `GET /api/maatbench/snapshot` reads latest JSON from disk so rebuild is not required after each run.

---

## Related

- [`docs/MAAT-ECOSYSTEM-SITE-DIRECTION.md`](MAAT-ECOSYSTEM-SITE-DIRECTION.md)
- [`docs/N8N-RETIRED.md`](N8N-RETIRED.md) — n8n removed from lab product surface
