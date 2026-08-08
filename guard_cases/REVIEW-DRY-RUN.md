# Dry run — Tehuti Sentinel starter batch

**Purpose:** Run the [five-point checklist](README.md#first-batch-review-checklist-tehuti-sentinel-v1) on the **synthetic** `guard_case_*.json` seeds before real traces dominate. Expose label drift early.

**Not** publishable evidence — **scaffolding** only.

Design is sufficient; **the system answers back** through this table and batch two.

---

## Disagreement cause (when `disagree?` = Y)

Tag **one primary cause** per disagreement (saves time later):

| Tag | Meaning |
|-----|--------|
| `policy_unclear` | Rule or allowlist not defined enough to decide |
| `schema_unclear` | `reason_code` / `decision` enums don’t fit the situation |
| `context_missing` | Need session, environment, or policy version not in the case |
| `reviewer_judgment` | Policy and schema are clear; reviewers still weigh tradeoffs differently |

### Resolution action (when `disagree?` = Y)

After tagging **disagreement cause**, add **one** `resolution_action` — detect → classify → **act**:

| `resolution_action` | Use when |
|---------------------|----------|
| `tighten_policy` | Rules/allowlists need clarity or new branches |
| `refine_schema` | Enums/fields don’t fit; forced labels |
| `add_context` | Case JSON needs session, env, policy version, etc. |
| `accept_ambiguity` | True gray zone; document and handle via escalation or human path |

**Typical mapping (not mandatory):** `policy_unclear` → `tighten_policy` · `schema_unclear` → `refine_schema` · `context_missing` → `add_context` · `reviewer_judgment` → often `accept_ambiguity` (or split: part policy, part schema).

---

## Review table

Fill with two reviewers (or two passes on different days). `disagree?` = **Y** if **`decision`** or **primary `reason_code`** differs.

| file | reviewer A `decision` | reviewer A `reason_code` | reviewer B `decision` | reviewer B `reason_code` | disagree? | disagreement cause | resolution_action | note |
|------|------------------------|----------------------------|------------------------|----------------------------|-----------|-------------------|-------------------|------|
| guard_case_tool_call_001.json | | | | | | | | |
| guard_case_memory_write_001.json | | | | | | | | |
| guard_case_retrieval_001.json | | | | | | | | |
| guard_case_retrieval_002.json | | | | | | | | |
| guard_case_shell_execution_001.json | | | | | | | | |
| guard_case_shell_execution_002.json | | | | | | | | |
| guard_case_scope_drift_001.json | | | | | | | | |
| guard_case_escalation_001.json | | | | | | | | |
| guard_case_plugin_or_mcp_001.json | | | | | | | | |
| guard_case_other_001.json | | | | | | | | |

---

## Checklist prompts (quick)

1. **Disagreement map** — rows with Y; use **disagreement cause** and **resolution_action**.  
2. **Reason code fit** — any forced fit?  
3. **Conditional vs escalate** — `retrieval_001` conditional: machine-checkable reroute? `scope_drift` vs `escalation` distinct?  
4. **Evidence** — is `source_ref` auditable for each row?  
5. **Classifier vs enforcement** — `label.decision` vs `outcome.final_action` story consistent?

---

## After the table is filled — read causes first (order matters)

1. **Do not** start by debating who was “right” on labels.  
2. **Tally** `disagreement cause` across Y rows — distribution tells you where the system is weak:  
   - **`policy_unclear` dominant** → tighten rules  
   - **`schema_unclear` dominant** → adjust schema  
   - **`context_missing` dominant** → improve case structure / required fields  
   - **`reviewer_judgment` dominant** → true gray zone (valuable; may need `accept_ambiguity` + escalation playbook)  
3. **Patterns to watch:** same file → different `reason_code` (schema pressure) · same file → conditional vs escalate (policy boundary) · same file → different `decision` entirely (serious ambiguity).  
4. **Apply stop/go below strictly** — do not override your own rules to rush batch two.

---

## Stop / go (after dry run)

| Signal | Action |
|--------|--------|
| Reviewers **mostly agree** | **Go** — move to **borderline, redacted real traces** for batch two. |
| **Often disagree** on **conditional vs escalate** or **primary `reason_code`** | **Stop** — tighten definitions / playbook **before** batch two. |
| **`evidence.source_ref` often weak** | **Stop** — fix evidence discipline **before** adding volume. |

**Do not cheat** this gate to avoid tightening work.

---

## Disagreement summary (for lineage review / dissertation appendix)

After dry run + cause tally, fill **one short block** (paste into gitMaat, cover note, or thesis appendix):

- **Date / batch:** (e.g. dry run synthetic, N cases)  
- **Agreement rate:** (e.g. 8/10 decision+reason match)  
- **Cause distribution:** (counts per tag)  
- **Resolution actions taken or queued:** (`tighten_policy` / `refine_schema` / `add_context` / `accept_ambiguity` with one line each)  
- **Stop/go result:** (go to batch two | tighten first — cite stop/go table)  
- **One sentence:** what the disagreement pattern **taught** about Tehuti Sentinel v1 (not slogans — diagnosis).

---

## Batch two — targets (borderline, disagreement-rich, redacted real)

Prioritize cases where labels are **not** obvious:

- Retrieval **useful but weakly sourced**  
- Memory writes with **partial** provenance  
- Shell: **safe in dev, risky in prod** (same or similar command)  
- Plugin/MCP: **allowed in one context, denied in another**  
- **Conditional** cases that could be mistaken for **escalate** (or vice versa)

That stress-tests whether Tehuti Sentinel is a **real classifier** or only a neat schema.

---

## After dry run

- Keep **2–4** seeds as **permanent fixtures** (document below).  
- **Replace** the rest over time with redacted real traces (retrieval, memory, shell first).

### Permanent seed picks (fill after review)

| file | keep as fixture? (Y/N) | why |
|------|-------------------------|-----|
| | | |

---

*Date dry run completed: _____________*
