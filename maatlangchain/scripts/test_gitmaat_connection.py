#!/usr/bin/env python3
"""
Standalone gitMaat connection test. Needs only psycopg2-binary and PGVECTOR_DB_URL.
Use this when maat_memory package is not yet available (e.g. partial clone).
Loads .env from script dir, cwd, or parent of cwd.
"""
import os
import sys
from pathlib import Path

# Load PGVECTOR_DB_URL: prefer .env over process env so workspace config wins
def _load_env():
    script_dir = Path(__file__).resolve().parent
    candidates = [
        script_dir / ".env",
        Path.cwd() / ".env",
        Path.cwd().parent / ".env",
        script_dir.parent / ".env",
        script_dir.parent.parent / ".env",
    ]
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
        print("ERROR: PGVECTOR_DB_URL not set and no .env found.", file=sys.stderr)
        print("Create .env in workspace root with: PGVECTOR_DB_URL=postgresql://user:pass@host:5432/maat_memory", file=sys.stderr)
        sys.exit(1)
    try:
        import psycopg2
    except ImportError:
        print("ERROR: psycopg2 not installed. Run: pip install psycopg2-binary", file=sys.stderr)
        sys.exit(1)
    try:
        conn = psycopg2.connect(url)
        cur = conn.cursor()
        try:
            cur.execute("SELECT COUNT(*) FROM maat_tasks")
            task_count = cur.fetchone()[0]
        except Exception as te:
            task_count = None
            print(f"Tasks: (error: {te})", file=sys.stderr)
        try:
            cur.execute("SELECT COUNT(*) FROM maat_sessions")
            session_count = cur.fetchone()[0]
        except Exception as se:
            session_count = None
            print(f"Sessions: (error: {se})", file=sys.stderr)
        cur.close()
        conn.close()
        print("Backend: MaatMemoryPostgres")
        print(f"Tasks: {task_count if task_count is not None else 'N/A (see stderr)'}")
        print(f"Sessions: {session_count if session_count is not None else 'N/A (see stderr)'}")
        return 0
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    sys.exit(main())
