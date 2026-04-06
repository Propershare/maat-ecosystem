"""
MAAT PostgreSQL + pgvector Memory Adapter

Swap for sqlite.py or json_file.py without touching the kernel.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

from maat_adapters.base import MemoryAdapter


class PostgresAdapter(MemoryAdapter):

    def __init__(self, config: dict):
        super().__init__(config)
        self._url = self._resolve_url(config.get("url", ""))

    @staticmethod
    def _resolve_url(url: str) -> str:
        if url:
            return url
        env = os.environ.get("PGVECTOR_DB_URL", "")
        if env:
            return env
        for p in [Path.home() / ".n8n" / ".env"]:
            if p.exists():
                for line in p.read_text().splitlines():
                    if line.startswith("PGVECTOR_DB_URL="):
                        return line.split("=", 1)[1].strip().strip("\"'")
        return ""

    def _connect(self):
        import psycopg2
        return psycopg2.connect(self._url)

    def write(self, entry: dict) -> bool:
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO maat_memories
                            (id, agent_id, memory_class, content, summary, source, tags, timestamp, reversible)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        ON CONFLICT (id) DO UPDATE SET content = EXCLUDED.content
                    """, (
                        entry["id"], entry["agent_id"], entry.get("memory_class", "episodic"),
                        entry["content"], entry.get("summary"), entry.get("source"),
                        json.dumps(entry.get("tags", [])), entry["timestamp"],
                        entry.get("reversible", True),
                    ))
                conn.commit()
            return True
        except Exception as e:
            print(f"[postgres] write error: {e}")
            return False

    def search(self, query: str, agent_id: str = "", memory_class: str = None, limit: int = 5) -> list[dict]:
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    sql = "SELECT id, agent_id, memory_class, content, summary, timestamp FROM maat_memories WHERE content ILIKE %s"
                    params = [f"%{query}%"]
                    if agent_id:
                        sql += " AND agent_id = %s"
                        params.append(agent_id)
                    if memory_class:
                        sql += " AND memory_class = %s"
                        params.append(memory_class)
                    sql += " ORDER BY timestamp DESC LIMIT %s"
                    params.append(limit)
                    cur.execute(sql, params)
                    cols = ["id", "agent_id", "memory_class", "content", "summary", "timestamp"]
                    return [dict(zip(cols, row)) for row in cur.fetchall()]
        except Exception as e:
            print(f"[postgres] search error: {e}")
            return []

    def get(self, memory_id: str) -> Optional[dict]:
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM maat_memories WHERE id = %s", (memory_id,))
                    row = cur.fetchone()
                    if row:
                        cols = [d[0] for d in cur.description]
                        return dict(zip(cols, row))
        except Exception as e:
            print(f"[postgres] get error: {e}")
        return None

    def delete(self, memory_id: str) -> bool:
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM maat_memories WHERE id = %s AND reversible = true", (memory_id,))
                conn.commit()
            return True
        except Exception as e:
            print(f"[postgres] delete error: {e}")
            return False
