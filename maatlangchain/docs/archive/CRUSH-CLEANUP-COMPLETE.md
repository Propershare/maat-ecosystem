# Crush.json Cleanup - Complete ✅

## What Was Done

### 1. Created Audit Script
- **File:** `scripts/audit_crush_files.sh`
- **Purpose:** Find all `crush.json` files and references
- **Usage:** `./scripts/audit_crush_files.sh`

### 2. Created Cleanup Script
- **File:** `scripts/cleanup_crush_files.sh`
- **Purpose:** Remove all `crush.json` files and directories
- **Usage:** `./scripts/cleanup_crush_files.sh`
- **Safety:** Creates backup before deletion

### 3. Added Unique Agent ID System
- **File:** `maat_memory/machine_info.py` - Added `get_unique_agent_id()`
- **Purpose:** Each agent gets unique ID based on machine/terminal
- **Format:**
  - Cursor: `cursor_<hostname>`
  - OpenCode: `opencode_<hostname>_<terminal_id>`

### 4. Updated Documentation
- **`AGENTS.md`** - Added unique agent ID instructions
- **`AGENT-FILE-GUIDE.md`** - Guide on what files to use/ignore
- **`AGENT-COORDINATION.md`** - Coordination protocol with unique IDs
- **`AGENTS-MAAT-MEMORY.md`** - Updated with unique ID examples

### 5. Created .gitignore
- **File:** `.gitignore`
- **Purpose:** Prevent `crush.json` files from being committed
- **Includes:** `crush.json`, `.crush/`, backup files

### 6. Removed Old Files
- ✅ Removed `test_crush_integration.py` (already had `test_maat_memory_integration.py`)

## What Agents Need to Know

### ✅ DO THIS

1. **Use Unique Agent IDs:**
   ```python
   from maat_memory.machine_info import get_unique_agent_id
   agent_id = get_unique_agent_id("opencode")  # or "cursor"
   ```

2. **Use Maat Memory (PostgreSQL):**
   ```python
   from maat_memory import MaatMemory
   memory = MaatMemory()
   memory.start_session(agent_id, "task description")
   ```

3. **Read File Guide:**
   - See `AGENT-FILE-GUIDE.md` for what files to use/ignore

### ❌ DON'T DO THIS

1. **Don't use `crush.json` files** - They're from the old system
2. **Don't use generic agent IDs** - Always use `get_unique_agent_id()`
3. **Don't create `.crush/` directories** - Use Maat Memory instead

## For Other Laptops

**Run these commands on each laptop:**

```bash
cd ~/.n8n/maatlangchain

# 1. Audit for crush.json files
./scripts/audit_crush_files.sh

# 2. Clean up if needed
./scripts/cleanup_crush_files.sh

# 3. Verify unique agent ID works
python3 -c "from maat_memory.machine_info import get_unique_agent_id; print(get_unique_agent_id('opencode'))"
```

**Expected output:**
```
opencode_imhotep_terminal_12345
# or
opencode_macdaddy_terminal_67890
# or
opencode_imhotepjr_terminal_99999
```

## Current Status

✅ **Main server cleaned** - No `crush.json` files found  
✅ **Unique agent ID system** - Ready to use  
✅ **Documentation updated** - All agents know what to do  
✅ **Scripts created** - Ready for other laptops  

## Next Steps

1. **Run audit on other laptops** to check for `crush.json` files
2. **Run cleanup if needed** on other laptops
3. **Test unique agent IDs** on each laptop
4. **Use Maat Memory** with unique agent IDs going forward

---

**Remember:** Maat Memory (PostgreSQL) is the only memory system. Ignore any `crush.json` files you find.

