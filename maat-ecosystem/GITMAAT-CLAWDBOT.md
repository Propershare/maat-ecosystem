# ClawdBot + gitMaat: Keep Up to Date and Manage All Workstations

ClawdBot can stay up to date with gitMaat and act as your single interface to manage tasks across all workstations (Cursor, OpenCode, Imhotep, imhotepjr, MacDaddy). All workstations read/write the same gitMaat DB; ClawdBot queries and writes from your PC (D:\clawd).

---

## 1. Scripts ClawdBot Uses (copy to D:\clawd)

Copy these from the server into `D:\clawd\` (same folder as `.env`):

| Script | Purpose |
|--------|---------|
| `query_gitmaat.py` | Read: pending tasks, recent changes by agent, learnings, decisions |
| `log_gitmaat_task.py` | Write: add task, mark task completed, list pending |
| `test_gitmaat_connection.py` | Check connectivity (optional) |
| `populate_gitmaat_test.py` | One-off test insert (optional) |

Ensure `.env` in `D:\clawd` has:
```
PGVECTOR_DB_URL=postgresql://suspect:disdick@192.168.4.21:5432/maat_memory
```
Scripts prefer `.env` over the Windows env var so the correct URL (5432) is always used.

---

## 2. Keep ClawdBot Up to Date

**Option A – On user request**  
When you ask ClawdBot “what’s pending?” or “what did the workstations do?”, ClawdBot runs:

```powershell
cd D:\clawd
python query_gitmaat.py
```

It will print a short summary: pending tasks, recent changes per agent (workstation), learnings, decisions. ClawdBot can then answer you from that output.

**Option B – Scheduled digest**  
If ClawdBot supports cron/scheduled commands, run the same command every N minutes (e.g. every 15) and have ClawdBot store or surface the summary so it’s “up to date” when you chat.

**Option C – JSON for parsing**  
If ClawdBot can parse JSON:

```powershell
python query_gitmaat.py --json
```

Use `--tasks 30 --changes 30` to control how many items are returned.

---

## 3. ClawdBot as Manager (add / complete tasks)

**Add a task**  
When you say “add task: fix the login bug” or “create task: deploy to staging”, ClawdBot runs:

```powershell
python log_gitmaat_task.py "fix the login bug" "Description optional" --agent clawdbot
python log_gitmaat_task.py "deploy to staging"
```

**Mark a task completed**  
When you say “mark task X done” or “complete fix the login bug”:

```powershell
python log_gitmaat_task.py --complete "fix the login bug"
```

**List pending**  
When you say “list tasks” or “what’s pending”:

```powershell
python log_gitmaat_task.py --list
```
Or use `query_gitmaat.py` for the full summary (tasks + changes + learnings).

---

## 4. Wiring ClawdBot (hooks / skills)

How you wire these depends on ClawdBot’s features:

- **If ClawdBot has “skills” or “commands”**: Register a skill that runs `python D:\clawd\query_gitmaat.py` (and optionally `log_gitmaat_task.py` with args from the user message). Map natural language like “what’s pending” → `query_gitmaat.py`, “add task …” → `log_gitmaat_task.py "…"`, “mark … done” → `log_gitmaat_task.py --complete "…"`.
- **If ClawdBot uses hooks**: On “gitmaat” or “tasks” keyword, run the appropriate script and reply with its stdout.
- **If ClawdBot can call external scripts**: Same idea: invoke the scripts above and use their output in the reply.

No n8n is required for this: ClawdBot runs the scripts locally on your PC; the scripts talk directly to gitMaat (Postgres) on the server.

---

## 5. How “Management of All Workstations” Works

- **Single source of truth**: gitMaat (Postgres on 192.168.4.21:5432) holds all tasks, changes, learnings, decisions.
- **All workstations** (Imhotep, imhotepjr, MacDaddy, and the PC running ClawdBot) use the same `PGVECTOR_DB_URL` (or the same DB via n8n on the server). Cursor, OpenCode, and any script that uses `maat_memory` or these scripts read/write the same data.
- **ClawdBot** = your single interface: it runs `query_gitmaat.py` and `log_gitmaat_task.py` on your PC, so you can ask “what’s pending?”, “what did imhotep do?”, “add task …”, “mark … done” without opening each workstation. The other agents (Cursor, OpenCode) stay in sync because they all use gitMaat; ClawdBot just surfaces and updates it for you.

---

## 6. Quick Reference

| You say (example) | ClawdBot runs |
|-------------------|---------------|
| “What’s pending?” / “gitMaat summary” | `python query_gitmaat.py` |
| “Add task: …” | `python log_gitmaat_task.py "…"` |
| “Mark … done” | `python log_gitmaat_task.py --complete "…"` |
| “List tasks” | `python log_gitmaat_task.py --list` or `query_gitmaat.py` |

All from `D:\clawd` with `.env` set. ClawdBot stays up to date by running `query_gitmaat.py` when you ask; it manages workstations by reading/writing the same gitMaat DB they all use.

---

## 7. AutoManize report → gitMaat (automatic updates)

When OpenCode (or another agent) emits an **AutoManize report** (taskId, status, summary, files), ClawdBot can push it to gitMaat so tasks and changes stay in sync:

1. Run `parse_acp_report.py` on the OpenCode log/output → get the latest report JSON.
2. Pipe that into `report_to_gitmaat.py`:  
   `python parse_acp_report.py < log.txt | python report_to_gitmaat.py`

**report_to_gitmaat.py** (copy from server: `maatlangchain/scripts/report_to_gitmaat.py`):
- Reads JSON from stdin or `--file`
- Updates `maat_tasks` (status, completion_notes) if `taskId` is present
- Logs each reported file to `maat_changes`

See **docs/AUTOMANIZE-GITMAAT.md** for the JSON contract and flow. That way ClawdBot can update gitMaat automatically after each OpenCode run without you doing it by hand.
