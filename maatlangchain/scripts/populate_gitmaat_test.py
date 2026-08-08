#!/usr/bin/env python3
"""
Insert test data into gitMaat and list tasks/changes. Standalone: needs only psycopg2 and .env with PGVECTOR_DB_URL.
Run from D:\\clawd (or anywhere with .env): python populate_gitmaat_test.py
"""
import json
import os
import sys
import uuid
from pathlib import Path

def _load_env():
    script_dir = Path(__file__).resolve().parent
    candidates = [script_dir / ".env", Path.cwd() / ".env", script_dir.parent / ".env", script_dir.parent.parent / ".env"]
    for p in candidates:
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
    url = _load_env()
    if not url:
        print("ERROR: PGVECTOR_DB_URL not set. Create .env with PGVECTOR_DB_URL=postgresql://user:pass@host:5432/maat_memory", file=sys.stderr)
        sys.exit(1)
    try:
        import psycopg2
    except ImportError:
        print("ERROR: pip install psycopg2-binary", file=sys.stderr)
        sys.exit(1)

    agent = "cursor_clawd"  # or use socket.gethostname() for machine name
    conn = psycopg2.connect(url)
    cur = conn.cursor()

    # 1) Insert one test task
    task_id = str(uuid.uuid4())
    cur.execute("""
        INSERT INTO maat_tasks (id, agent, title, description, status, priority, related_files, dependencies)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (task_id, agent, "Test task from PC", "Populated via populate_gitmaat_test.py", "pending", "medium", "[]", "[]"))
    conn.commit()
    print("Inserted 1 task:", task_id)

    # 2) Insert one test change
    change_id = str(uuid.uuid4())
    cur.execute("""
        INSERT INTO maat_changes (id, agent, file_path, change_type, summary, diff_preview, reason)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (change_id, agent, "D:\\clawd\\.env", "modify", "Test change from PC", None, "Testing gitMaat from Windows"))
    conn.commit()
    print("Inserted 1 change:", change_id)

    # 3) List recent tasks and changes
    cur.execute("SELECT id, agent, title, status, created_at FROM maat_tasks ORDER BY created_at DESC LIMIT 10")
    rows = cur.fetchall()
    print("\n--- Recent tasks ---")
    for r in rows:
        print(f"  {r[2]} | {r[3]} | {r[1]} | {r[4]}")

    cur.execute("SELECT id, agent, file_path, change_type, summary, created_at FROM maat_changes ORDER BY created_at DESC LIMIT 10")
    rows = cur.fetchall()
    print("\n--- Recent changes ---")
    for r in rows:
        print(f"  {r[2]} | {r[3]} | {r[1]} | {r[5]}")

    cur.close()
    conn.close()
    print("\nDone. gitMaat is writable from this PC.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
