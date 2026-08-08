# Fable 5 Staged Cross-Model Evidence Package

**Status:** Frozen  
**Frozen at:** 2026-07-07  
**Package version:** `fable5_capture_package_v1`  
**Manifest:** `fable5_capture_manifest.json`

---

## Research Question

Can a stronger model eliminate the need for constitutional runtime enforcement, or does it only reduce repair burden?

## Preliminary Answer (Staged Evidence)

**Stronger models can improve raw judgment and reduce repair burden, but they do not eliminate the need for constitutional runtime enforcement.**

Fable 5 improved covenant vocabulary, raw integrated validity on governance-stress cases, and repair burden versus the Ornith Pass 7A baseline — while compiler-enforced governance remained necessary and **unsafe allow stayed at 0%** across all arms.

---

## Scope Statement (Read First)

This package is **not** a full 251-case MaatBench benchmark.

It is a **staged cross-model capture** designed to test whether a frontier-class model changes the architecture claim across:

1. **Smoke default** — baseline Desktop behavior (16 cases)
2. **Smoke prompted** — same 16 case IDs with frozen covenant-record framing
3. **Tier B** — stratified governance stress sample (77 cases)

Do **not** compare these headline numbers directly to the frozen Ornith **251-case** evaluation without labeling adapter and denominator differences.

---

## Model Provenance

| Field | Value |
|-------|-------|
| Model label | `fable5_desktop` |
| Provider | Claude Desktop (Cowork mode) |
| Model ID | `claude-fable-5` |
| Machine | `imhotep` |
| Capture window | 2026-07-03T22:08:48Z → 2026-07-07T13:56:26Z |
| Adapter | `desktop_assisted_file_capture` (self-capture) |
| Model card | `fable5_model_card.json` |
| Screenshot | `fable5_model_card_screenshot.png` |
| Supplemental screenshot | `fable5_model_card_screenshot_chat.png` |

**Capture method:** Fable 5 read each case prompt in Claude Desktop Cowork mode and appended its raw JSON response to the target JSONL files. No API-pure adapter. No post-capture JSON repair. Refusals and malformed output would have been preserved.

**Scoring:** Offline on data_drive via `score_fable5_desktop_capture.py` against MaatBench 0.3.2 at `/mnt/ai_models/maatbench`.

---

## Capture Inventory

| Arm | Cases | Prompt mode | Raw file | Score file | Status |
|-----|------:|-------------|----------|------------|--------|
| Smoke default | 16 | `default` | `fable5_smoke_default_raw.jsonl` | `fable5_smoke_default_score.json` | scored |
| Smoke prompted | 16 | `prompted_covenant_record` | `fable5_smoke_prompted_raw.jsonl` | `fable5_smoke_prompted_score.json` | scored |
| Tier B | 77 | `default` | `fable5_tier_b_raw.jsonl` | `fable5_tier_b_score.json` | scored |
| **Total captures** | **109** | | | | |

Note: Smoke default and smoke prompted share the same 16 case IDs; Tier B is a distinct stratified slice. Total **109** counts prompt-mode runs, not 109 unique benchmark case IDs.

---

## Results Summary

### Headline metrics by arm

| Arm | Raw integrated validity | Compiler-enforced integrated validity | Exact decision token rate | Unsafe allow | Avg repairs/case | Avg repair burden score | Human review routed |
|-----|------------------------:|--------------------------------------:|--------------------------:|-------------:|-----------------:|------------------------:|--------------------:|
| Smoke default | 0.0% | 93.75% | 62.5% | 0.0% | 1.63 | 12.75 | 7 |
| Smoke prompted | 50.0% | 93.75% | 100.0% | 0.0% | 3.50 | 7.00 | 7 |
| Tier B | 41.56% | 92.21% | 100.0% | 0.0% | 1.29 | 5.60 | 29 |

### Reference baseline (Ornith Pass 7A, full 251-case MaatBench 0.3.2)

| Metric | Ornith 251-case | Fable Tier B (77 staged) |
|--------|----------------:|-------------------------:|
| Raw integrated validity | 0.0% | 41.56% |
| Compiler-enforced validity | 88.84% | 92.21% |
| Unsafe allow | 0.0% | 0.0% |
| Avg repair burden score | 12.94 | 5.60 |

Comparison is **directional only** — different model, adapter, and denominator.

---

## Interpretation

1. **Decision vocabulary:** Fable 5 uses wire tokens (`allow` / `review` / `deny`) on Tier B and prompted smoke at 100%; default smoke still emitted alias tokens (`defer`, `escalate`) at 37.5%.
2. **Raw validity:** Prompting moved smoke from 0% → 50% raw integrated validity on the same 16 IDs. Tier B default mode reached 41.56% without covenant framing on a harder stratified slice.
3. **Compiler necessity:** Compiler-enforced integrated validity stayed ~92–94% across arms. Raw alone does not clear governance gates.
4. **Safety:** **0% unsafe allow** on all arms — stronger drafting did not bypass unsafe-allow blocking.
5. **Repair burden:** Tier B avg burden (5.60) is materially below Ornith 251-case (12.94), consistent with “reduces burden, does not remove compiler.”

**Locked line:** Training can improve the model. Prompting can improve the draft. The compiler governs the record.

---

## Limitations

See `fable5_limitations.md`. Key points:

- Desktop-assisted capture, not API-pure evaluation
- Hidden Desktop system prompt may affect behavior
- Decoding parameters unknown (temperature / max_tokens null)
- **Not full 251-case eval** — `full_251` gate remains `optional_after_p0_p3`
- Two prompt arms; do not mix scores without labeling
- Refusals stay in denominator per cross-model design

---

## What This Package Can Support

- Dissertation subsection: preliminary cross-model evidence
- Architecture claim: constitutional runtime enforcement remains necessary on frontier models
- Product direction: Tehuti Guard as enforcement layer after covenant compilation
- Community dataset planning: sanitized judgment-record examples derived from MaatBench categories

## What This Package Cannot Support

- Claiming Fable 5 passed full MaatBench 0.3.2 on 251 cases
- Model promotion (gate remains **false**)
- Enterprise production readiness of Tehuti Guard
- Elimination of constitutional runtime enforcement without raw integrated validity gates

---

## Frozen Artifact Registry (SHA-256)

From `fable5_capture_manifest.json` (2026-07-07):

| Artifact | SHA-256 |
|----------|---------|
| `fable5_model_card.json` | `61bc5182d247d32e6f921cda21f1cb2eade432150ce749890c1f6c4849bb37a6` |
| `fable5_model_card_screenshot.png` | `2b9aaeea61705b8ebadfca91d918863868f49583f1afe22c38201b740f5acbbc` |
| `fable5_smoke_default_raw.jsonl` | `ef61056872e53b340bb5aaf4e31d3f713378439eac35b5ca57858780df021037` |
| `fable5_smoke_prompted_raw.jsonl` | `b77ea6496e0d27f535c02c488980dd0a36dc338d9da4cab250e38955fa183e0c` |
| `fable5_tier_b_raw.jsonl` | `aeb1f15ae65911265a9d9aa8a079d37d5ef7dcc9915819fd1f90f9397639bf03` |
| `fable5_smoke_default_score.json` | `b0253835f1c1b36aaa8b13e752433546e65562983e877123f0edf96f2a82b11d` |
| `fable5_smoke_prompted_score.json` | `2550654b4e505b5345af25cda56f0b0ddbaad8f75ee8dd4c87adb8f0987910a8` |
| `fable5_tier_b_score.json` | `4dcde5b4a3da28c006fc074ecc62615e7e7118363080bd76913ef04dc805ec01` |

---

## Gates (Unchanged)

- **Model promotion:** false
- **Training:** blocked (no Pack L, Pass 7B, DPO, broad SFT)
- **Full 251 Fable run:** optional — not required for this package

---

## Related Artifacts

- `MAATBENCH_CROSS_MODEL_EVAL_DESIGN.md` — full cross-model protocol
- `MAAT_DISSERTATION_OUTLINE.md` — dissertation packaging (§ Preliminary Cross-Model Evidence)
- `MAAT_JUDGMENT_RECORDS_COMMUNITY_DATASET_PLAN.md` — public dataset plan
- `maat-ecosystem/docs/TEHUTI_GUARD_V2_CONSTITUTIONAL_REBUILD.md` — product spec
- `FABLE5_PUBLIC_POST_DRAFT.md` — public-safe positioning draft
