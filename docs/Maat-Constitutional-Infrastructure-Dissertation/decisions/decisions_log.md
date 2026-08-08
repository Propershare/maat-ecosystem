# Decisions log (curated memory)

**Rule:** Each entry answers: *What changed?* *Why?* *What evidence supports it?*

---

## Example format

**Decision:** (one line)  
**Reason:**  
**Evidence:** (citation, test, governance row, bench result, etc.)  
**Impact:**  
**Date:** ISO-8601  

---

## Decisions

**Decision:** Add scholarship layer for Kilimanjaro AI/political-economy essay — reading list, youth notes, dissertation bridge.
**Reason:** User affirmed analysis ("ase'"); essay supplies mode-of-production literacy that complements Ma'at constitutional infrastructure without collapsing political economy into tech governance alone.
**Evidence:** `scholarship/kilimanjaro-automation-essay-READING-LIST.md`, `scholarship/youth-facing-economics-and-ai-NOTES.md`, `scholarship/DISSERTATION-BRIDGE-kilimanjaro-automation-essay.md`; index + V1 bibliography updated.
**Impact:** Middle-ring study material for youth and manuscript integration; ka-education display link deferred (last priority).
**Date:** 2026-06-20

**Decision:** The dissertation gains an empirical case-study layer ("Tehuti Research Lab as a Ma'at-Governed AI Infrastructure Prototype") alongside the normative argument.
**Reason:** The blueprint argues Ma'at *should* govern AI; the lab now has running artifacts (Guard decision API, Maat Memory organ + client, wire contracts, governance event rows) that let us argue from evidence, not only principle.
**Evidence:** `tehuti-guard/guard/` tests; `maat-memory-client/` clean-venv run; `maat_governance_events` 2026-06-06 green run; `docs/TEHUTI-GUARD-WIRE-CONTRACT.md`, `docs/MAAT-MEMORY-WIRE-CONTRACT.md`; see `notes/raw_notes.md`.
**Impact:** Adds a Section to the manuscript and an evidence appendix; converts thesis from "design-oriented" to "design + prototype-validated."
**Date:** 2026-06-15

**Decision:** Treat "advertised-but-absent governance" and "silent contract drift" as named, original failure modes in the dissertation.
**Reason:** The most dangerous observed state was not "no governance" but governance that *appears* present (organ on the manifest, a client that calls Guard, policy docs) while being unenforced (service down) or mis-spoken (wrong wire contract → 400). This is a genuine contribution: constitutional infrastructure must be continuously *verified*, not merely *declared*.
**Evidence:** Ka `:8010` manifest listing `policy:8013` while `:8013` refused connections + no systemd unit; `maat-runtime/guard-client.ts` flat body vs nested envelope expected by the API.
**Impact:** Strengthens Chapter 1 (Crisis of Ungoverned Intelligence) and Chapter 7 (Tehuti Guard); motivates a "liveness + contract conformance" requirement in the Ma'at-at-every-layer argument.
**Date:** 2026-06-15

**Decision:** "Ma'at as constitutional infrastructure" is concretized as a **shared-organ architecture** (Memory `:8022`, Policy/Guard `:8013`, Brain `:8014`, Discovery `:8010`, Posture/Sentinel `:4242`) with **versioned wire contracts** and **thin installable clients**, rather than embedding logic per-build.
**Reason:** Per-build embedding caused drift; full centralization is brittle. The validated pattern is a layered hybrid: deterministic local checks + central posture-aware service.
**Evidence:** `docs/MAAT-AUDIT-DO-WE-NEED-GUARD-IN-BUILDS-2026-06-13.md`; `maat-memory-client` adoption model; both wire-contract docs.
**Impact:** Gives Chapters 6–7 concrete referents; the "shared organ" becomes the dissertation's reference architecture.
**Date:** 2026-06-15

**Decision:** Treat the contemporary AI-governance citations as source-verified but not yet citation-style formatted.
**Reason:** A web verification pass on 2026-06-15 confirmed Anthropic's Claude's Constitution, Claude's new constitution, Project Glasswing, Claude Mythos Preview, NIST AI RMF 1.0, NIST AI 600-1, UNESCO, OECD, OWASP, and Karenga source details. The NIST critical-infrastructure item must be described precisely as a concept note / profile in development, not as a finalized profile.
**Evidence:** `appendices/CITATION-VERIFICATION-2026-06-15.md`.
**Impact:** Removes the strongest citation uncertainty from the manuscript; next task is formatting and inserting formal citations/footnotes.
**Date:** 2026-06-15

**Decision:** Promote operator's Version 1 manuscript draft to canonical on-disk source; replace Chapter 7 placeholders with verified lab evidence only.
**Reason:** The pasted V1 (9 chapters, 42 Laws as Ch. 8) is the real dissertation; the short repo draft was a blueprint-era stub. Chapter 7 must not invent unaudited subsystem claims.
**Evidence:** Transcript V1 paste; `manuscript/V1-MANUSCRIPT.md`; `manuscript/chapter-07-evidence-filled.md`; `appendices/EVIDENCE-APPENDIX-2026-06-15.md`.
**Impact:** Canonical file is ~1090 lines; Ch. 7 includes Guard/Memory/liveness findings and honest "pending" labels for unaudited systems.
**Date:** 2026-06-18

**Decision:** Public site brief (`docs/REPLIT-MAAT-SITE-BRIEF.md`) supersedes Ka-body `REPLIT-CONTINUE.md` for maatecosystem.com.
**Reason:** Product story is Ma'at + MaatBench + governed frameworks; user rejected static page and Ka anatomy hero; wants interactivity.
**Evidence:** `docs/MAAT-ECOSYSTEM-SITE-DIRECTION.md`; ka-education interactive history (`a6a1d37`).
**Impact:** Replit/self-hosted work should follow new brief: principle explorer, bench panel, 42 Laws browser — **Ma'at product only** (no n8n or legacy lab tools on public site).
**Date:** 2026-06-18

**Decision:** Retire n8n from lab product surface, Ka manifest, and agent canon.
**Reason:** Operator will not use n8n again; public site and agent prompts must not advertise tools outside the Ma'at product.
**Evidence:** `docs/N8N-RETIRED.md`; `_retired/n8n/`; MANIFEST.ka + ka-discovery updated; `n8n-mcp` removed from active tree.
**Impact:** Port 8015 no longer in manifest; OpenClaw :18790 is senses/gateway organ.
**Date:** 2026-06-18
