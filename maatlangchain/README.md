# MaatLangChain

Production-grade RAG system with Maat governance principles.

## Spine role (architecture)

MaatLangChain is the **durable orchestration spine** for this lab: **Maat Memory** (gitMaat / Postgres), agents, RAG, and coordination — not the constitutional schema layer (that lives under `maat-ecosystem` + [`maat_core`](../maat_core/)) and not “the MCP server is the brain.” MCP exposes tools; **this repo’s memory and task continuity** live here in `maat_memory/` and related agents.

- **Framework report:** [`docs/MAAT-FRAMEWORK-REPORT.md`](../docs/MAAT-FRAMEWORK-REPORT.md)
- **Core path locator:** [`maat_core/`](../maat_core/) (`SCHEMAS_DIR`, `SOUL_DIR`, bench contracts)

## 🚀 Quick Start

**For Agents:** Read `AGENTS.md` - Zero-config auto-setup handles everything.

**For Users:** See `ONBOARDING-GUIDE.md` for setup instructions.

## 📚 Essential Files

- **`AGENTS.md`** - Agent instructions (MANDATORY for all agents)
- **`PROMPT-NEXT-ACTION.md`** - High-level guidance (context only per Maat Law)
- **`AGENTS-MAAT-MEMORY.md`** - Maat Memory usage guide
- **`AGENT-COORDINATION.md`** - Agent coordination protocol
- **`AGENT-FILE-GUIDE.md`** - What files to use/ignore
- **`MAATLANGCHAIN-VALUE-PROPOSITION.md`** - Project value proposition

## 🏛️ Maat Principles

- **Truth:** Single source of truth (gitMaat database)
- **Balance:** Real-time coordination via gitMaat
- **Order:** Consistent workflow (query gitMaat for tasks)
- **Justice:** All agents query same gitMaat database
- **Self-Reflection:** All changes logged in gitMaat

## 🌐 gitMaat (Central Coordination)

**Maat Memory is gitMaat** - our central coordination system for all laptops and IDEs.

**Key Distinction:**
- **Maat Memory (gitMaat)** = Database system (`maatlangchain/maat_memory/`) - **QUERY FIRST FOR TASKS** (THIS IS LAW)
- **Memory Bank** = Documentation folder (`memory-bank/`) - Read for context only (optional)

All agents (Cursor, OpenCode, Claude Desktop, etc.) use the same Maat Memory database for coordination.

**Tasks are stored in gitMaat (database), not in Memory Bank or .md files.** This is MAAT LAW.

## 📖 Documentation

- **`docs/`** - Project documentation
- **`docs/archive/`** - Completed/historical work

## ✅ Core Status

**All core systems verified and ready:**
- ✅ Maat Memory (gitMaat) - Central coordination
- ✅ Auto-setup - Zero-config
- ✅ Project discovery - Auto-suggestions
- ✅ Maat Standards - Component validation
- ✅ Unique agent IDs - Machine/terminal tracking
- ✅ Task coordination - Maat Law in place

**See:** `docs/CORE-READY-STATUS.md` for complete verification.

---

**Ready to build!** 🚀

