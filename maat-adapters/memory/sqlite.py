"""
MAAT SQLite Memory Adapter

Lightweight alternative to Postgres.
Perfect for single-user local installs with no DB server.
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from pathlib import Path
from typing import Optional

from maat_adapters.base import MemoryAdapter


class SQLiteAdapter(MemoryAdapter):

    def __init__(self, config: dict):
        super().__init__(config)
        db_path = config.get("path", Path.home() / ".maat" / "memory.db")
        self._path = Path(db_path)
        self._init_db()

    def _connect(self):
        self._path.parent.mkdir(parents=True, exist_ok=True)
        return sqlite3.connect(self._path)

    def _init_db(self):
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS maat_memories (
                    id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    memory_class TEXT DEFAULT 'episodic',
                    content TEXT NOT NULL,
                    summary TEXT,
                    source TEXT,
                    tags TEXT DEFAULT '[]',
                    timestamp TEXT NOT NULL,
                    reversible INTEGER DEFAULT 1
                )
            """)
            conn.commit()

    def write(self, entry: dict) -> bool:
        try:
            with self._connect() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO maat_memories
                        (id, agent_id, memory_class, content, summary, source, tags, timestamp, reversible)
                    VALUES (?,?,?,?,?,?,?,?,?)
                """, (
                    entry.get("id", str(uuid.uuid4())),
                    entry["agent_id"],
                    entry.get("memory_class", "episodic"),
                    entry["content"],
                    entry.get("summary"),
                    entry.get("source"),
                    json.dumps(entry.get("tags", [])),
                    entry["timestamp"],
                    1 if entry.get("reversible", True) else 0,
                ))
                conn.commit()
            return True
        except Exception as e:
            print(f"[sqlite] write error: {e}")
            return False

    def search(self, query: str, agent_id: str = "", memory_class: str = None, limit: int = 5) -> list[dict]:
        try:
            with self._connect() as conn:
                sql = "SELECT id, agent_id, memory_class, content, summary, timestamp FROM maat_memories WHERE content LIKE ?"
                params = [f"%{query}%"]
                if agent_id:
                    sql += " AND agent_id = ?"
                    params.append(agent_id)
                if memory_class:
                    sql += " AND memory_class = ?"
                    params.append(memory_class)
                sql += " ORDER BY timestamp DESC LIMIT ?"
                params.append(limit)
                cur = conn.execute(sql, params)
                cols = ["id", "agent_id", "memory_class", "content", "summary", "timestamp"]
                return [dict(zip(cols, row)) for row in cur.fetchall()]
        except Exception as e:
            print(f"[sqlite] search error: {e}")
            return []

    def get(self, memory_id: str) -> Optional[dict]:
        try:
            with self._connect() as conn:
                cur = conn.execute("SELECT * FROM maat_memories WHERE id = ?", (memory_id,))
                row = cur.fetchone()
                if row:
                    cols = [d[0] for d in cur.description]
                    return dict(zip(cols, row))
        except Exception as e:
            print(f"[sqlite] get error: {e}")
        return None

    def delete(self, memory_id: str) -> bool:
        try:
            with self._connect() as conn:
                conn.execute("DELETE FROM maat_memories WHERE id = ? AND reversible = 1", (memory_id,))
                conn.commit()
            return True
        except Exception as e:
            print(f"[sqlite] delete error: {e}")
            return False
