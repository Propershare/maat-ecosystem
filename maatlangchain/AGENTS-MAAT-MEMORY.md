# Maat Memory - Quick Guide for Agents

## ✅ Setup Complete

Maat Memory is already set up and ready to use. No configuration needed.

## 📍 Location

Maat Memory is in this project:
- **Path:** `/home/suspect/.n8n/maatlangchain/maat_memory/`
- **Import:** `from maat_memory import MaatMemory`

## 🚀 How to Use

### Basic Usage with Unique Agent ID

**IMPORTANT:** Always use unique agent IDs, not generic names like "cursor" or "opencode".

```python
from maat_memory import MaatMemory
from maat_memory.machine_info import get_unique_agent_id

# Get your unique agent ID (auto-detects machine and terminal)
agent_id = get_unique_agent_id("opencode")  # or "cursor"
# Example: "opencode_imhotep_terminal_12345"

# Initialize (automatically uses PostgreSQL if PGVECTOR_DB_URL is set)
memory = MaatMemory()

# You must explicitly call start_session()
# Machine info (hostname, terminal, etc.) is automatically detected when you call it
session_id = memory.start_session(agent_id, "working on feature X")

# You must explicitly call log_conversation()
# Machine info is automatically detected when you call it
memory.log_conversation(
    agent=agent_id,
    user_query="How do I implement feature Y?",
    agent_response="Here's how..."
)

# You must explicitly call end_session()
memory.end_session(agent_id, "Completed feature X", ["key point 1", "key point 2"])
```

## 🆔 Using Unique Agent IDs

**CRITICAL:** Each agent instance must use a unique ID based on machine and terminal.

**Why?** Each laptop/terminal needs unique ID for accurate tracking:
- `opencode_imhotep_terminal_12345` (OpenCode on Imhotep laptop)
- `opencode_macdaddy_terminal_67890` (OpenCode on MacDaddy laptop)
- `opencode_imhotepjr_terminal_99999` (OpenCode on Imhotepjr laptop)
- `cursor_imhotep` (Cursor IDE on Imhotep laptop)

**See:** `AGENT-COORDINATION.md` for full coordination protocol.

**What "Automatic" Means:**
- ✅ Machine info detection is automatic (you don't pass hostname/terminal manually)
- ❌ Session/conversation logging is NOT automatic (you must call the methods)

### Check What Backend You're Using

```python
from maat_memory import MaatMemory

memory = MaatMemory()
print(memory.__class__.__name__)
# Should print: "MaatMemoryPostgres" if connected to database
```

### Verify It's Working (Command Line)

```bash
cd /home/suspect/.n8n/maatlangchain
python3 -c "from maat_memory import MaatMemory; memory = MaatMemory(); print(f'✅ Backend: {memory.__class__.__name__}'); print('✅ Connected to shared database')"
```

## 🔍 How Agents Will Know It's Available

1. **It's in the project** - `maat_memory/` directory exists
2. **Import works** - `from maat_memory import MaatMemory` 
3. **Auto-detects backend** - Uses PostgreSQL if `PGVECTOR_DB_URL` is set
4. **Schema auto-creates** - First use creates tables automatically

## ✅ Verification

Run this to verify it's working:

```python
from maat_memory import MaatMemory

memory = MaatMemory()
print(f"✅ Backend: {memory.__class__.__name__}")
print(f"✅ Connected to shared database")
```

**Expected output:**
```
✅ Backend: MaatMemoryPostgres
✅ Connected to shared database
```

## 📝 What Agents Should Know

- **Location:** `maat_memory/` in this project
- **Import:** `from maat_memory import MaatMemory`
- **Setup:** Already done - just use it
- **Backend:** Auto-detects PostgreSQL or JSON
- **Cross-machine:** All laptops share same database automatically
- **Schema:** Auto-creates on first use (no manual setup)

## ❓ If Asked "Where is maat_memory?"

**Answer:** "It's in `/home/suspect/.n8n/maatlangchain/maat_memory/`. Import with `from maat_memory import MaatMemory`. Setup is complete - just use it."

## 🔧 Troubleshooting

**If you get "PostgreSQL backend not available":**
- Check `PGVECTOR_DB_URL` is set: `echo $PGVECTOR_DB_URL`
- If not set, run: `source ~/.bashrc` or restart terminal
- It will fallback to JSON backend automatically

**If import fails:**
- Make sure you're in the project directory: `cd /home/suspect/.n8n/maatlangchain`
- Or add to Python path: `export PYTHONPATH=/home/suspect/.n8n/maatlangchain:$PYTHONPATH`

