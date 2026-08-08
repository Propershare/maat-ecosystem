"""
Maat Learn — Memory layer connecting agents to gitMaat.

All memory lives in PostgreSQL + pgvector. This module provides
simple read/write functions that any agent can use.

Every function handles its own connection and never crashes.

Usage:
    from maat.learn import query_memory, log_task, log_learning

    results = query_memory("what did we decide about auth?")
    log_task("deployed v2", "Pushed to production", agent="tehuti")
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import psycopg2
from psycopg2 import OperationalError, ProgrammingError
from psycopg2.extras import RealDictCursor


# ─── DB URL Resolution ─────────────────────────────────────────────

def _resolve_db_url(db_url: str = "") -> str:
    """
    Find the database URL from (in order):
    1. Explicit argument
    2. PGVECTOR_DB_URL environment variable
    3. ~/.maat/config.yaml
    4. ~/.n8n/.env file

    Raises ValueError if none found.
    """
    if db_url:
        return db_url

    # Env var
    env_url = os.environ.get("PGVECTOR_DB_URL")
    if env_url:
        return env_url

    # Maat config
    try:
        from maat.config import get
        cfg_url = get("memory.database_url")
        if cfg_url:
            return cfg_url
    except Exception:
        pass

    # Fallback: ~/.n8n/.env
    for env_path in [
        Path.home() / ".n8n" / ".env",
        Path.home() / ".n8n" / "maatlangchain" / ".env",
    ]:
        if env_path.exists():
            try:
                with open(env_path) as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("PGVECTOR_DB_URL="):
                            return line.split("=", 1)[1].strip().strip("\"'")
            except Exception:
                pass

    raise ValueError(
        "Database URL not found. Set PGVECTOR_DB_URL env var, "
        "or configure memory.database_url in ~/.maat/config.yaml"
    )


def _get_conn(db_url: str = "") -> Optional[psycopg2.extensions.connection]:
    """Get a database connection. Returns None on failure."""
    try:
        url = _resolve_db_url(db_url)
        return psycopg2.connect(url)
    except (OperationalError, ValueError) as e:
        print(f"[maat.learn] DB connection failed: {e}")
        return None
    except Exception as e:
        print(f"[maat.learn] Unexpected connection error: {e}")
        return None


# ─── Read Functions ────────────────────────────────────────────────

def query_memory(query: str, agent: str = "", limit: int = 5, db_url: str = "") -> List[Dict[str, Any]]:
    """
    Search conversations by text similarity.

    Args:
        query: Search string (uses ILIKE %query%).
        agent: Filter by agent name (optional).
        limit: Max results.
        db_url: Override database URL.

    Returns:
        List of dicts with timestamp, agent, user_query, agent_response.
        Empty list on error.
    """
    conn = _get_conn(db_url)
    if not conn:
        return []

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            sql = """
                SELECT timestamp, agent, user_query, agent_response
                FROM maat_conversations
                WHERE (user_query ILIKE %s OR agent_response ILIKE %s)
            """
            params: list = [f"%{query}%", f"%{query}%"]

            if agent:
                sql += " AND agent = %s"
                params.append(agent)

            sql += " ORDER BY timestamp DESC LIMIT %s"
            params.append(limit)

            cur.execute(sql, params)
            return [dict(row) for row in cur.fetchall()]
    except Exception as e:
        print(f"[maat.learn] query_memory error: {e}")
        return []
    finally:
        conn.close()


def get_recent_tasks(agent: str = "", limit: int = 10, db_url: str = "") -> List[Dict[str, Any]]:
    """
    Get recent tasks, optionally filtered by agent.

    Returns:
        List of task dicts. Empty list on error.
    """
    conn = _get_conn(db_url)
    if not conn:
        return []

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            sql = "SELECT id, created_at, agent, title, description, status, priority FROM maat_tasks"
            params: list = []

            if agent:
                sql += " WHERE agent = %s"
                params.append(agent)

            sql += " ORDER BY created_at DESC LIMIT %s"
            params.append(limit)

            cur.execute(sql, params)
            return [dict(row) for row in cur.fetchall()]
    except Exception as e:
        print(f"[maat.learn] get_recent_tasks error: {e}")
        return []
    finally:
        conn.close()


# ─── Write Functions ───────────────────────────────────────────────

def log_conversation(user_query: str, agent_response: str, agent: str, db_url: str = "") -> bool:
    """
    Log a conversation turn.

    Args:
        user_query: What the user said.
        agent_response: What the agent replied.
        agent: Agent identifier.

    Returns:
        True on success, False on error.
    """
    conn = _get_conn(db_url)
    if not conn:
        return False

    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO maat_conversations (agent, user_query, agent_response) VALUES (%s, %s, %s)",
                (agent, user_query, agent_response),
            )
        conn.commit()
        return True
    except Exception as e:
        print(f"[maat.learn] log_conversation error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def log_task(title: str, description: str, agent: str, status: str = "pending", db_url: str = "") -> bool:
    """
    Log a task.

    Args:
        title: Short task title.
        description: What needs to be done.
        agent: Who owns it.
        status: pending, in_progress, completed, blocked.

    Returns:
        True on success.
    """
    conn = _get_conn(db_url)
    if not conn:
        return False

    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO maat_tasks (agent, title, description, status, priority) VALUES (%s, %s, %s, %s, %s)",
                (agent, title, description, status, "medium"),
            )
        conn.commit()
        return True
    except Exception as e:
        print(f"[maat.learn] log_task error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def log_decision(context: str, decision: str, rationale: str, agent: str, db_url: str = "") -> bool:
    """
    Log a significant decision.

    Args:
        context: What prompted the decision.
        decision: What was decided.
        rationale: Why.
        agent: Who decided.

    Returns:
        True on success.
    """
    conn = _get_conn(db_url)
    if not conn:
        return False

    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO maat_decisions (agent, context, decision_made, rationale) VALUES (%s, %s, %s, %s)",
                (agent, context, decision, rationale),
            )
        conn.commit()
        return True
    except Exception as e:
        print(f"[maat.learn] log_decision error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def log_learning(category: str, description: str, context: str, agent: str, db_url: str = "") -> bool:
    """
    Log something learned.

    Args:
        category: Topic area (e.g., "tool-calling", "architecture").
        description: The insight.
        context: Where/how it was learned.
        agent: Who learned it.

    Returns:
        True on success.
    """
    conn = _get_conn(db_url)
    if not conn:
        return False

    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO maat_learnings (agent, category, description, context) VALUES (%s, %s, %s, %s)",
                (agent, category, description, context),
            )
        conn.commit()
        return True
    except Exception as e:
        print(f"[maat.learn] log_learning error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def log_change(change_type: str, description: str, files: List[str], agent: str, db_url: str = "") -> bool:
    """
    Log a code/config change.

    Args:
        change_type: "code", "config", "infrastructure", etc.
        description: What changed.
        files: List of affected file paths.
        agent: Who made the change.

    Returns:
        True on success.
    """
    conn = _get_conn(db_url)
    if not conn:
        return False

    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO maat_changes (agent, change_type, description, files_affected) VALUES (%s, %s, %s, %s)",
                (agent, change_type, description, json.dumps(files)),
            )
        conn.commit()
        return True
    except Exception as e:
        print(f"[maat.learn] log_change error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


# ─── Quick Test ────────────────────────────────────────────────────

if __name__ == "__main__":
    print("📚 Maat Learn — Connection Test\n")

    try:
        url = _resolve_db_url()
        print(f"  DB URL: {url[:30]}...")
    except ValueError as e:
        print(f"  ⚠️  {e}")
        exit(1)

    conn = _get_conn()
    if conn:
        print("  ✅ Connected to gitMaat")
        conn.close()
    else:
        print("  ❌ Connection failed")
        exit(1)

    print("\n  Querying recent tasks...")
    tasks = get_recent_tasks(limit=3)
    for t in tasks:
        print(f"    [{t['status']}] {t['title']} ({t['agent']})")

    if not tasks:
        print("    (no tasks found)")

    print("\n  Querying memory for 'maat'...")
    results = query_memory("maat", limit=3)
    for r in results:
        print(f"    {r['agent']}: {r['user_query'][:60]}...")

    if not results:
        print("    (no conversations found)")
