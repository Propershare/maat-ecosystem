# Simple start — before the full review

If the long doc feels like too much: **you don’t have to use it yet.**  
The big system is still there when you’re ready. This is the **small** version.

---

## What you’re actually doing (one sentence)

**Look at a case, say what you’d do (allow / block / need a person), and why in plain language.**

That’s the same idea as Tehuti Sentinel — without the formality.

---

## Easiest path (one person, one pass)

1. Open **one** file: `guard_case_tool_call_001.json` (or any `guard_case_*.json`).
2. Read **`input`** + **`label`** in the file (the file is already “the example”).
3. Ask yourself only:
   - **Would I allow this in my lab?** (yes / no / not without a human)
   - **Why?** (one or two sentences in a notebook, not in the schema)

Do **2–3 files**, then stop. You’re learning the **shape** of the problem, not finishing a process.

---

## Slightly more (still simple)

Use a **notes file** or paper with **three columns** — no enums, no taxonomy:

| file | my answer (allow / block / human) | why |
|------|-----------------------------------|-----|

When that feels easy, you can add a fourth column **“does the JSON match my gut?”** (yes / no).  
**No** = that’s disagreement — worth a sentence in a note. Still no need for `policy_unclear` tags until you want them.

---

## When to open `REVIEW-DRY-RUN.md`

Only when:

- you’ve read a few cases and they make sense, **and**
- you want **two opinions** on the same case, **or**
- you need **evidence** for the dissertation / a reviewer.

Until then, **ignore** the full table. It’s not homework — it’s an **optional** tight protocol.

---

## What *not* to worry about yet

- `reason_code`, `conditional` vs `escalate`, `resolution_action` — learn by **reading** the JSON examples first.
- Filling every column — **optional**.
- Being consistent — **truth first** (your earlier note): if you’re unsure, write “unsure” in **why**.

---

## Link to the full ritual (later)

[`REVIEW-DRY-RUN.md`](REVIEW-DRY-RUN.md) — dual pass, causes, stop/go — when you choose to level up.

---

*Same logic, smaller door.*
