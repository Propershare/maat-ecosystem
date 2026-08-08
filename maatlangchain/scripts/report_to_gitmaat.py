#!/usr/bin/env python3
"""
Consume AutoManize/ACP report JSON (from parse_acp_report.py or stdin) and update gitMaat:
- Update maat_tasks (status, completion_notes) by taskId if present
- Log each reported file to maat_changes

Expected JSON shape (align with WorkflowReport in maatbench/reports.py):
  taskId (str, optional)  - UUID of task to update
  status (str)            - e.g. completed, in_progress, failed
  summary (str)           - workflow summary / completion notes
  files (list, optional) - [{"path": "...", "action": "modify"|"create"|"delete"}, ...]
  commands (list, optional) - list of commands run (stored in summary if needed)
  agent (str, optional)   - agent name (default: opencode_clawd)

Usage:
  python parse_acp_report.py < log.txt | python report_to_gitmaat.py
  python report_to_gitmaat.py --file report.json
  echo '{"status":"completed","summary":"Done"}' | python report_to_gitmaat.py
"""
import argparse
import json
import os
import sys
import uuid
from pathlib import Path

def _load_env():
    script_dir = Path(__file__).resolve().parent
    for p in [script_dir / ".env", Path.cwd() / ".env", script_dir.parent / ".env", script_dir.parent.parent / ".env"]:
        if p.exists():
            try:
                with open(p) as f:
                    for line in f:
                        if line.startswith("PGVECTOR_DB_URL="):
                            return line.split("=", 1)[1].strip().strip('"').strip("'")
            except Exception:
                pass
    return os.environ.get("PGVECTOR_DB_URL")

def main():
    ap = argparse.ArgumentParser(description="Push AutoManize report JSON to gitMaat")
    ap.add_argument("--file", "-f", help="Read JSON from file instead of stdin")
    ap.add_argument("--agent", default="opencode_clawd", help="Agent name for changes")
    ap.add_argument("--dry-run", action="store_true", help="Print what would be done, do not write")
    args = ap.parse_args()

    if args.file:
        with open(args.file) as f:
            data = json.load(f)
    else:
        try:
            data = json.load(sys.stdin)
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON: {e}", file=sys.stderr)
            sys.exit(1)

    task_id = data.get("taskId")
    status = (data.get("status") or "completed").strip().lower()
    summary = data.get("summary") or ""
    files = data.get("files") or []
    agent = data.get("agent") or args.agent

    url = _load_env()
    if not url:
        print("ERROR: PGVECTOR_DB_URL not set.", file=sys.stderr)
        sys.exit(1)
    try:
        import psycopg2
    except ImportError:
        print("ERROR: pip install psycopg2-binary", file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        print(f"Would update taskId={task_id} -> status={status}, summary={summary[:80]}...")
        print(f"Would log {len(files)} file(s) as agent={agent}")
        for f in files:
            path = f.get("path") if isinstance(f, dict) else str(f)
            action = f.get("action", "modify") if isinstance(f, dict) else "modify"
            print(f"  - {path} ({action})")
        return 0

    conn = psycopg2.connect(url)
    cur = conn.cursor()

    # 1) Update task by taskId if present
    if task_id:
        cur.execute("""
            UPDATE maat_tasks SET status = %s, completion_notes = %s, updated_at = NOW()
            WHERE id = %s
        """, (status, summary[:5000] if summary else None, task_id))
        if cur.rowcount:
            conn.commit()
            print(f"Updated task {task_id} -> status={status}")
        else:
            print(f"No task found with id={task_id}", file=sys.stderr)

    # 2) Log each file to maat_changes
    for f in files:
        if isinstance(f, dict):
            path = f.get("path") or f.get("file_path") or ""
            action = (f.get("action") or f.get("change_type") or "modify").lower()[:20]
        else:
            path = str(f)
            action = "modify"
        if not path:
            continue
        change_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO maat_changes (id, agent, file_path, change_type, summary, reason)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (change_id, agent, path[:2000], action, (summary or "Reported by AutoManize")[:500], "AutoManize report"))
    if files:
        conn.commit()
        print(f"Logged {len(files)} change(s) for agent={agent}")

    cur.close()
    conn.close()
    return 0

if __name__ == "__main__":
    sys.exit(main())
