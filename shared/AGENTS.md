# Global OpenCode Agent Instructions

## 📚 Maat Memory System

If you're working on a project that uses Maat Memory:

- **Import:** `from maat_memory import MaatMemory`
- **Status:** Auto-detects PostgreSQL if `PGVECTOR_DB_URL` is set
- **Usage:** `memory = MaatMemory()` then use `start_session()`, `log_conversation()`, etc.

## 🔧 Environment

- **Database:** Uses `PGVECTOR_DB_URL` environment variable
- **Backend:** Auto-detects PostgreSQL, falls back to JSON
- **Cross-machine:** All laptops share same database if `PGVECTOR_DB_URL` points to same server

## ✅ Setup

Maat Memory is ready to use if:
- `PGVECTOR_DB_URL` is set in your environment
- The `maat_memory` module is in your Python path

**Check project-specific `AGENTS.md` files for project details.**

