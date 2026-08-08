"""Shared DB helpers for Memory Plane (uses PGVECTOR_DB_URL)."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import psycopg2
from psycopg2.extras import RealDictCursor


def load_dotenv_pg() -> None:
    env = Path.home() / ".n8n" / ".env"
    if not env.is_file():
        return
    for line in env.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def get_conn():
    load_dotenv_pg()
    url = os.environ.get("PGVECTOR_DB_URL")
    if not url:
        raise RuntimeError("PGVECTOR_DB_URL required for Memory Plane")
    return psycopg2.connect(url)


def permissive() -> bool:
    return os.environ.get("MAAT_MEMORY_PLANE_PERMISSIVE", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )


def fetchall(sql: str, params: tuple | list | None = None) -> list[dict[str, Any]]:
    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params or ())
            return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def fetchone(sql: str, params: tuple | list | None = None) -> dict[str, Any] | None:
    rows = fetchall(sql, params)
    return rows[0] if rows else None


def execute(sql: str, params: tuple | list | None = None) -> None:
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def execute_returning(sql: str, params: tuple | list | None = None) -> dict[str, Any] | None:
    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params or ())
            row = cur.fetchone()
        conn.commit()
        return dict(row) if row else None
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
