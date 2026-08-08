# Agent File Guide - What Files to Use

## ✅ Files Agents SHOULD Use

### Task & Coordination Files
- **`PROMPT-NEXT-ACTION.md`** - High-level guidance (context only, not tasks)
- **`AGENTS.md`** - Project-specific agent instructions (MANDATORY)
- **`AGENT-COORDINATION.md`** - How to coordinate with other agents
- **`AGENTS-MAAT-MEMORY.md`** - How to use Maat Memory

### Code & Libraries
- **`maat_memory/`** - Maat Memory system (PostgreSQL-backed)
- **`core/`** - Core MaatLangChain code
- **`api/`** - API endpoints
- **`scripts/`** - Utility scripts

### Documentation
- **`docs/`** - Project documentation
- **`README.md`** - Project overview

## ❌ Files Agents SHOULD IGNORE

### Temporary Files
- **`*.tmp`**, **`*.bak`**, **`*.save`** - Temporary/backup files
- **`.cleanup_backup_*`** - Cleanup backups

### Cache & Build Artifacts
- **`__pycache__/`** - Python cache
- **`.cache/`** - Cache directories
- **`dist/`**, **`build/`**, **`.egg-info/`** - Build artifacts

### Data Files (Not Config)
- **`chunks.json`** - PDF chunk data (not a config file, safe to ignore)

## 🆔 Your Unique Agent ID

**IMPORTANT:** Always use unique agent IDs, never generic names.

```python
from maat_memory.machine_info import get_unique_agent_id

# Get your unique ID (auto-detects machine and terminal)
agent_id = get_unique_agent_id("opencode")  # or "cursor"
# Example: "opencode_imhotep_terminal_12345"
# Example: "opencode_macdaddy_terminal_67890"
```

## 📋 File Organization Rules

### Root Directory
- ✅ Keep only essential files (README, AGENTS.md, PROMPT-NEXT-ACTION.md)
- ❌ Don't put config files in root (use `config/` directory)

### Memory System
- ✅ Use `maat_memory/` directory
- ✅ Use PostgreSQL backend (via `PGVECTOR_DB_URL`)
- ✅ All memory operations use Maat Memory

### Scripts
- ✅ Put scripts in `scripts/` directory
- ✅ Use descriptive names

## 🏛️ Maat Memory (gitMaat)

**Maat Memory is the ONLY memory system:**
- ✅ PostgreSQL-backed (shared across all laptops)
- ✅ Task coordination (query for tasks)
- ✅ Session tracking
- ✅ Change logging
- ✅ Decision tracking

**No legacy systems exist - Maat Memory is it.**

---

**Remember**: Maat Memory (PostgreSQL) is the only memory system. Use it for all memory operations.
