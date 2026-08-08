#!/usr/bin/env python3
"""
Query gitMaat: pending tasks, recent changes by agent, learnings, decisions.
Standalone: needs psycopg2 and .env with PGVECTOR_DB_URL. Prefers .env over env.
Output: human-readable summary (default) or --json for ClawdBot/parsing.
Usage: python query_gitmaat.py [--json] [--tasks N] [--changes N]
"""
import argparse
import json
import os
import sys
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
    ap = argparse.ArgumentParser(description="Query gitMaat (tasks, changes, learnings, decisions)")
    ap.add_argument("--json", action="store_true", help="Output JSON for ClawdBot/parsing")
    ap.add_argument("--tasks", type=int, default=20, help="Max pending/recent tasks (default 20)")
    ap.add_argument("--changes", type=int, default=20, help="Max recent changes (default 20)")
    ap.add_argument("--learnings", type=int, default=5, help="Max learnings (default 5)")
    ap.add_argument("--decisions", type=int, default=5, help="Max decisions (default 5)")
    ap.add_argument("--out", "-o", metavar="FILE", help="Write human-readable summary to FILE (e.g. GITMAAT-CONTEXT.md)")
    args = ap.parse_args()

    url = _load_env()
    if not url:
        print("ERROR: PGVECTOR_DB_URL not set. Create .env with PGVECTOR_DB_URL=postgresql://...", file=sys.stderr)
        sys.exit(1)
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
    except ImportError:
        print("ERROR: pip install psycopg2-binary", file=sys.stderr)
        sys.exit(1)

    conn = psycopg2.connect(url)
    cur = conn.cursor(cursor_factory=RealDictCursor)

    out = {}
    # Pending tasks
    cur.execute("""
        SELECT id, agent, title, description, status, priority, created_at
        FROM maat_tasks WHERE status IN ('pending', 'in_progress')
        ORDER BY created_at DESC LIMIT %s
    """, (args.tasks,))
    tasks = [dict(r) for r in cur.fetchall()]
    for t in tasks:
        if t.get("created_at"):
            t["created_at"] = str(t["created_at"])
    out["tasks"] = tasks

    # Recent changes (by agent = workstation)
    cur.execute("""
        SELECT id, agent, file_path, change_type, summary, created_at
        FROM maat_changes ORDER BY created_at DESC LIMIT %s
    """, (args.changes,))
    changes = [dict(r) for r in cur.fetchall()]
    for c in changes:
        if c.get("created_at"):
            c["created_at"] = str(c["created_at"])
    out["changes"] = changes

    # Learnings
    try:
        cur.execute("""
            SELECT topic, insight, source, timestamp FROM maat_learnings
            ORDER BY timestamp DESC LIMIT %s
        """, (args.learnings,))
        learnings = [dict(r) for r in cur.fetchall()]
        for l in learnings:
            if l.get("timestamp"):
                l["timestamp"] = str(l["timestamp"])
        out["learnings"] = learnings
    except Exception:
        out["learnings"] = []

    # Decisions
    try:
        cur.execute("""
            SELECT context, decision_made, rationale, timestamp FROM maat_decisions
            ORDER BY timestamp DESC LIMIT %s
        """, (args.decisions,))
        decisions = [dict(r) for r in cur.fetchall()]
        for d in decisions:
            if d.get("timestamp"):
                d["timestamp"] = str(d["timestamp"])
        out["decisions"] = decisions
    except Exception:
        out["decisions"] = []

    cur.close()
    conn.close()

    if args.json:
        print(json.dumps(out, indent=2))
        return 0

    # Human-readable summary for ClawdBot / OpenCode / agents
    lines = []
    lines.append("# gitMaat context (all workstations)")
    lines.append("")
    lines.append("**Refreshed from shared gitMaat.** Read this first so you know what other PCs/agents are doing.")
    lines.append("")
    lines.append("## Pending / in-progress tasks")
    lines.append("")
    lines.append(f"Count: {len(out['tasks'])}")
    for t in out["tasks"][:15]:
        lines.append(f"- [{t.get('status','')}] {t.get('title','')} (agent: {t.get('agent','')})")
    lines.append("")
    lines.append("## Recent changes (by workstation/agent)")
    lines.append("")
    lines.append(f"Count: {len(out['changes'])}")
    for c in out["changes"][:15]:
        lines.append(f"- {c.get('agent','')}: {c.get('file_path','')} | {c.get('summary','')[:60]}")
    if out.get("learnings"):
        lines.append("")
        lines.append("## Learnings")
        lines.append("")
        for l in out["learnings"][:5]:
            lines.append(f"- {str(l.get('insight', l.get('topic', l)))[:80]}")
    if out.get("decisions"):
        lines.append("")
        lines.append("## Decisions")
        lines.append("")
        for d in out["decisions"][:5]:
            lines.append(f"- {str(d.get('decision_made', d))[:80]}")
    lines.append("")
    lines.append("---")
    lines.append("*To refresh: run `python maatlangchain/scripts/query_gitmaat.py --out GITMAAT-CONTEXT.md` from workspace root.*")
    text = "\n".join(lines)

    if args.out:
        out_path = Path(args.out)
        if not out_path.is_absolute():
            out_path = Path.cwd() / out_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text, encoding="utf-8")
        print(f"Wrote {out_path}", file=sys.stderr)
    else:
        # Legacy: also print a short summary to stdout
        lines_short = ["=== gitMaat summary ===", f"Pending/in-progress tasks: {len(out['tasks'])}"]
        for t in out["tasks"][:15]:
            lines_short.append(f"  - [{t.get('status','')}] {t.get('title','')} (agent: {t.get('agent','')})")
        lines_short.append(f"\nRecent changes: {len(out['changes'])}")
        for c in out["changes"][:15]:
            lines_short.append(f"  - {c.get('agent','')}: {c.get('file_path','')} | {c.get('summary','')[:60]}")
        print("\n".join(lines_short))
    return 0

if __name__ == "__main__":
    sys.exit(main())
