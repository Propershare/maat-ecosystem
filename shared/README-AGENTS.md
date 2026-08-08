# OpenCode Global AGENTS.md Setup

## 📋 What This Is

This README explains how to set up OpenCode's global `AGENTS.md` file on other laptops so agents know about Maat Memory.

## 🎯 Purpose

OpenCode automatically reads `AGENTS.md` files:
- **Project-specific:** `AGENTS.md` in project root (already exists)
- **Global:** `~/.config/opencode/AGENTS.md` (needs to be copied to each laptop)

## 📝 Installation on Other Laptops

### Step 1: Copy the Global AGENTS.md

Create the global AGENTS.md file on each laptop:

```bash
mkdir -p ~/.config/opencode
cat > ~/.config/opencode/AGENTS.md << 'EOF'
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
EOF
```

### Step 2: Verify

```bash
cat ~/.config/opencode/AGENTS.md
```

Should show the global instructions.

## 🔍 How OpenCode Uses This

1. **Global rules:** `~/.config/opencode/AGENTS.md` applies to all OpenCode sessions
2. **Project rules:** `AGENTS.md` in project root applies when working in that directory
3. **Precedence:** Project-specific rules override global rules

## ✅ After Installation

OpenCode will automatically:
- Read global AGENTS.md on all sessions
- Read project-specific AGENTS.md when working in that project
- Know about Maat Memory system availability

## 📊 Maat Governance

Following Maat principles:
- **Truth:** Clear, accurate instructions
- **Order:** Consistent setup across all laptops
- **Balance:** Same access for all agents
- **Self-Reflection:** Documented process for future reference

---

**Quick Copy Command:**
```bash
mkdir -p ~/.config/opencode && cat > ~/.config/opencode/AGENTS.md << 'EOF'
# Global OpenCode Agent Instructions

## 📚 Maat Memory System

If you're working on a project that uses Maat Memory:
- Import: `from maat_memory import MaatMemory`
- Auto-detects PostgreSQL if `PGVECTOR_DB_URL` is set
- Cross-machine sync enabled

## ✅ Setup

Maat Memory is ready if `PGVECTOR_DB_URL` is set.
Check project-specific `AGENTS.md` files for details.
EOF
```

