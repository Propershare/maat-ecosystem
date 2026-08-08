# OpenClaw + gitMaat evolving setup (Tehuti Lab)

This doc describes how OpenClaw is wired for an **evolving** loop: bootstrap → run → memory flush → session-memory → gitMaat.

## 1. Bootstrap: gitMaat in every turn

- **Hook:** `hooks/gitmaat-bootstrap/`  
  Injects `GITMAAT-CONTEXT.md` into the agent bootstrap so every run sees current tasks and recent activity (Maat: query first).
- **Config:** `~/.openclaw/openclaw.json` has `hooks.internal.enabled: true`.
- **Your part:** Keep `GITMAAT-CONTEXT.md` in the workspace root. From workspace root:
  - `bash maatlangchain/scripts/refresh_gitmaat_context.sh`, or
  - `python maatlangchain/scripts/query_gitmaat.py --out GITMAAT-CONTEXT.md`
  Run after important changes or on a schedule (see “Closing the loop” below).

## 2. Memory: flush + session-memory

- **Memory flush** (default on): Before compaction, a turn runs that writes durable memories to `memory/YYYY-MM-DD.md`. So long conversations are distilled into the workspace; `memory_search` can recall them later.
- **Session-memory** (bundled): On `/new`, the previous session is written to `memory/YYYY-MM-DD-<slug>.md`. So each new session is persisted and indexed.
- **Optional:** Tune the memory-flush prompt in config so distillations align with Maat (decisions, learnings, next steps). See OpenClaw docs for `agents.defaults.compaction.memoryFlush`.

## 3. Closing the loop with gitMaat

So that OpenClaw’s evolution and gitMaat stay in sync:

- **Refresh context:** Run the query script on a schedule (cron or n8n) so `GITMAAT-CONTEXT.md` is up to date before agents run. Example cron (from workspace root):
  - `0 * * * * cd /home/suspect/.n8n && python maatlangchain/scripts/query_gitmaat.py --out GITMAAT-CONTEXT.md`
- **Push learnings (optional):** If you want gitMaat to get summaries of what’s in `MEMORY.md` or `memory/*`, add a cron job or n8n workflow that reads those files and calls your gitMaat logging API (or script). The script `maatlangchain/scripts/refresh_gitmaat_context.sh` is the standard way to pull from gitMaat; pushing back is project-specific.

## 4. One workspace

OpenClaw workspace is `/home/suspect/.n8n`. So identity (SOUL, USER, IDENTITY), hooks (`hooks/`), memory (`memory/`, `MEMORY.md`), and gitMaat context (`GITMAAT-CONTEXT.md`) all live in one repo and stay in sync.

## Quick checklist

- [x] `hooks.internal.enabled: true` in `~/.openclaw/openclaw.json`
- [x] `hooks/gitmaat-bootstrap/` hook in place
- [ ] Generate/refresh `GITMAAT-CONTEXT.md` when needed (manual or cron)
- [ ] (Optional) Cron or n8n to push memory summaries to gitMaat
- Restart OpenClaw gateway after any config change so hooks load.
