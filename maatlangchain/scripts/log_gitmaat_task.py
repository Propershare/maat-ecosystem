#!/usr/bin/env python3
"""
Add or update a task in gitMaat. Standalone: needs psycopg2 and .env with PGVECTOR_DB_URL.
Usage:
  python log_gitmaat_task.py "Task title" [description] [--status pending|in_progress|completed]
  python log_gitmaat_task.py --complete "Task title"   # set status=completed
  python log_gitmaat_task.py --list                   # list pending tasks (same as query_gitmaat --tasks)
"""
import argparse
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
    ap = argparse.ArgumentParser(description="Add or update gitMaat task")
    ap.add_argument("title", nargs="?", help="Task title")
    ap.add_argument("description", nargs="?", default="", help="Task description")
    ap.add_argument("--status", choices=["pending", "in_progress", "completed"], default="pending")
    ap.add_argument("--complete", action="store_true", help="Set status to completed (use with title)")
    ap.add_argument("--list", action="store_true", help="List pending tasks and exit")
    ap.add_argument("--agent", default="clawdbot", help="Agent name (default clawdbot)")
    args = ap.parse_args()

    url = _load_env()
    if not url:
        print("ERROR: PGVECTOR_DB_URL not set.", file=sys.stderr)
        sys.exit(1)
    try:
        import psycopg2
    except ImportError:
        print("ERROR: pip install psycopg2-binary", file=sys.stderr)
        sys.exit(1)

    conn = psycopg2.connect(url)
    cur = conn.cursor()

    if args.list:
        cur.execute("""
            SELECT id, agent, title, status, created_at FROM maat_tasks
            WHERE status IN ('pending', 'in_progress') ORDER BY created_at DESC LIMIT 30
        """)
        for r in cur.fetchall():
            print(f"  {r[0]} | {r[2]} | {r[3]} | {r[1]}")
        cur.close()
        conn.close()
        return 0

    status = "completed" if args.complete else args.status
    title = args.title or ""
    if not title and not args.list:
        print("ERROR: Give a task title, or use --list", file=sys.stderr)
        sys.exit(1)

    if args.complete or (args.title and status == "completed"):
        cur.execute("""
            SELECT id, title FROM maat_tasks
            WHERE status IN ('pending', 'in_progress') AND (title ILIKE %s OR title ILIKE %s)
            ORDER BY created_at DESC LIMIT 1
        """, (title, f"%{title}%"))
        row = cur.fetchone()
        if row:
            cur.execute("UPDATE maat_tasks SET status = 'completed', updated_at = NOW() WHERE id = %s", (row[0],))
            conn.commit()
            print(f"Marked task completed: {row[1]}")
        else:
            print(f"No pending/in_progress task found matching: {title}", file=sys.stderr)
            sys.exit(1)
    else:
        # Insert new task
        task_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO maat_tasks (id, agent, title, description, status, priority, related_files, dependencies)
            VALUES (%s, %s, %s, %s, %s, 'medium', '[]', '[]')
        """, (task_id, args.agent, title, args.description or "", status))
        conn.commit()
        print(f"Added task: {title} (id: {task_id})")

    cur.close()
    conn.close()
    return 0

if __name__ == "__main__":
    sys.exit(main())
