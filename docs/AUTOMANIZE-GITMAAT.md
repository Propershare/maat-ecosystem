# AutoManize Report → gitMaat Loop

OpenCode (or another agent) emits an **AutoManize report** (structured JSON: taskId, status, summary, files, commands). ClawdBot can parse it and push it to gitMaat so tasks and changes stay in sync across workstations.

---

## Flow

1. **OpenCode** runs a workflow and emits a report (REPORT_START/REPORT_END block or last JSON matching WorkflowReport).
2. **ClawdBot** (after `stopReason == 'end_turn'` or when it has the log) runs:
   - `parse_acp_report.py` on the stream/log → extracts the latest report JSON.
   - Pipes that JSON into `report_to_gitmaat.py` (or saves to file and passes `--file`).
3. **report_to_gitmaat.py** (this repo):
   - Reads JSON from stdin or `--file`.
   - If `taskId` is present: updates `maat_tasks` (status, completion_notes).
   - For each entry in `files`: inserts into `maat_changes` (agent, file_path, change_type, summary).
   - Uses `.env` with `PGVECTOR_DB_URL` (same as other gitMaat scripts).

Result: gitMaat gets the task status and file changes from the AutoManize run; ClawdBot doesn’t have to do it manually.

---

## JSON contract (align with WorkflowReport)

`report_to_gitmaat.py` expects JSON with at least:

| Field   | Type   | Required | Description |
|--------|--------|----------|-------------|
| taskId | string | no       | UUID of task to update in maat_tasks |
| status | string | yes      | completed, in_progress, failed, etc. |
| summary| string | no       | Completion notes / workflow summary  |
| files  | array  | no       | List of {path, action} or {file_path, change_type} |
| agent  | string | no       | Agent name (default opencode_clawd)  |

Optional: `commands` (can be folded into summary or ignored). Extra fields are ignored.

---

## Usage

**From ClawdBot (pipe):**
```powershell
cd D:\clawd
python parse_acp_report.py < opencode_log.txt | python report_to_gitmaat.py
```

**From file:**
```powershell
python parse_acp_report.py < log.txt --pretty > report.json
python report_to_gitmaat.py --file report.json
```

**Dry run (no DB write):**
```powershell
python report_to_gitmaat.py --file report.json --dry-run
```

---

## Where things live

- **maatbench/reports.py** (Maat-Node): WorkflowReport model, REPORT_START/REPORT_END parser, `last_report_from_stream` / `parse_reports_from_stream`.
- **scripts/parse_acp_report.py** (Maat-Node): CLI that reads stream/file, prints latest report JSON.
- **scripts/report_to_gitmaat.py** (this repo): Reads that JSON, updates gitMaat (tasks + changes).
- **AUTOMANIZE.md** (Maat-Node): Full AutoManize delivery options and report contract.

Copy `report_to_gitmaat.py` to D:\clawd (with the other gitMaat scripts) so ClawdBot can run the pipe after it has the OpenCode output.

---

## Validation without OpenCode (sample report)

You can validate the report → gitMaat flow **before** running OpenCode end-to-end:

1. **Sample reports** (in `maatlangchain/scripts/`):
   - `sample_automize_report.json` – no taskId; only logs file changes.
   - `sample_automize_report_with_task.json` – has taskId (use a real UUID from `maat_tasks` if you want to update an existing task).

2. **Dry run (no DB write):**
   ```powershell
   cd D:\clawd
   python report_to_gitmaat.py --file path\to\sample_automize_report.json --dry-run
   ```

3. **Push to gitMaat:**
   ```powershell
   python report_to_gitmaat.py --file path\to\sample_automize_report.json
   ```
   Then run `query_gitmaat.py` and confirm the new changes appear.

4. **Pipe (simulate parse_acp_report output):**
   ```powershell
   type sample_automize_report.json | python report_to_gitmaat.py
   ```

Once this works, run OpenCode, capture its log, run `parse_acp_report.py < log.txt | python report_to_gitmaat.py` for full end-to-end validation.

**Validated:** Sample report with taskId was run through `report_to_gitmaat.py`; task row updated (status + completion_notes) and change row inserted. `query_gitmaat.py` confirmed the update. Real OpenCode log can be piped through `parse_acp_report.py | report_to_gitmaat.py` the same way.
