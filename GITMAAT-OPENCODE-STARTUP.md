# How OpenCode (and other agents) know what to do when they open up

**Problem:** OpenCode on one PC doesn’t automatically know what another PC (or Cursor on the server) is doing. gitMaat holds the shared state, but agents need to **read** it when they start.

**Solution:** Use a **generated context file** that any workstation can refresh from gitMaat. When you open the project on a PC, refresh that file once; then OpenCode (and Cursor, ClawdBot, etc.) read it first and see current tasks and recent activity from **all** workstations.

---

## 1. One file: `GITMAAT-CONTEXT.md`

- **What it is:** A markdown file in the **workspace root** that contains:
  - Pending / in-progress tasks (from all agents)
  - Recent changes (by workstation/agent)
  - Learnings and decisions
- **Who writes it:** The script `query_gitmaat.py --out GITMAAT-CONTEXT.md` (or the refresh scripts below).
- **Who reads it:** Agents (OpenCode, Cursor, etc.) are told in AGENTS.md / cursorrules to **read `GITMAAT-CONTEXT.md` first** when they start. Then they know what this PC and the others are doing.

---

## 2. When to refresh

- **When you open the project** on a PC (recommended): run the refresh once so the context file is up to date before you ask OpenCode to do anything.
- **Periodically:** e.g. after pulling git, or every hour if you leave the project open.
- **Optional:** You can also tell the agent to run the refresh if the file is missing or stale (see AGENTS.md).

---

## 3. How to refresh (any PC)

From the **workspace root** (the folder that contains `maatlangchain`):

**Linux / Mac:**
```bash
bash maatlangchain/scripts/refresh_gitmaat_context.sh
```
Or directly:
```bash
python3 maatlangchain/scripts/query_gitmaat.py --out GITMAAT-CONTEXT.md
```

**Windows (e.g. D:\clawd):**
```bat
python maatlangchain\scripts\query_gitmaat.py --out GITMAAT-CONTEXT.md
```
Or from inside `maatlangchain\scripts`:
```bat
refresh_gitmaat_context.bat
```
(Then move `GITMAAT-CONTEXT.md` to workspace root if the script put it in `scripts`; the `.bat` above assumes you `cd` to workspace root first.)

**Requirements:** Same as gitMaat on that PC: `.env` with `PGVECTOR_DB_URL`, and `pip install psycopg2-binary`. See `GITMAAT-WORKSTATIONS.md` if the connection fails.

---

## 4. What agents do when they open

1. **Read `GITMAAT-CONTEXT.md` first** (if present) – current tasks and recent activity from all workstations.
2. If the file is missing or you want a fresh pull: run `python maatlangchain/scripts/query_gitmaat.py --out GITMAAT-CONTEXT.md` from workspace root, then read the file again.
3. Then continue with project-specific instructions (e.g. `PROMPT-NEXT-ACTION.md` for MaatLangChain, or OC2’s task file).

That way OpenCode on the other PC “knows what this one is doing” because it reads the same shared context generated from gitMaat.

---

## 5. Summary

| Step | Who | Action |
|------|-----|--------|
| 1 | You (on any PC) | When you open the project, run the refresh script or `query_gitmaat.py --out GITMAAT-CONTEXT.md` from workspace root. |
| 2 | OpenCode / Cursor / agent | Reads `GITMAAT-CONTEXT.md` first (per AGENTS.md / cursorrules). |
| 3 | Agent | Sees pending tasks and recent changes from all PCs and continues with its task. |

No extra services needed; the shared state is in gitMaat (PostgreSQL), and the context file is just a local snapshot so agents know what to do when they open up.
