# Maat Memory Onboarding Guide - 3 Laptops + OpenCode

## Quick Start (5 Minutes Per Laptop)

### Step 1: Run Setup Script

On each laptop, run:

```bash
cd /path/to/maatlangchain
python3 scripts/setup_maat_memory.py
```

The script will:
- ✅ Check dependencies
- ✅ Configure database connection
- ✅ Test connection
- ✅ Migrate existing JSON data
- ✅ Verify everything works

### Step 2: Verify Cross-Machine Sync

**On Laptop 1:**
```python
from maat_memory import MaatMemory
memory = MaatMemory()
memory.start_session("cursor", "test-from-laptop-1")
```

**On Laptop 2:**
```python
from maat_memory import MaatMemory
memory = MaatMemory()
sessions = memory.get_sessions(agent="cursor", limit=5)
# Should see "test-from-laptop-1" session!
```

---

## Manual Setup (If Script Doesn't Work)

### 1. Install Dependencies

```bash
pip install psycopg2-binary pgvector langchain-huggingface
```

### 2. Set Database URL

**Option A: Central Server (Recommended)**

All laptops connect to the same PostgreSQL server:

```bash
# Add to ~/.bashrc on each laptop
export PGVECTOR_DB_URL="postgresql://user:pass@central-server-ip:5434/maat_memory"
```

**Option B: Local Database (If All Laptops Can Access)**

If you have a shared network database:

```bash
export PGVECTOR_DB_URL="postgresql://user:pass@192.168.1.100:5434/maat_memory"
```

**Option C: Cloud Database (If Acceptable)**

For cloud-hosted PostgreSQL:

```bash
export PGVECTOR_DB_URL="postgresql://user:pass@cloud-db.example.com:5432/maat_memory"
```

### 3. Test Connection

```python
from maat_memory import MaatMemory

memory = MaatMemory()
print(f"Backend: {memory.__class__.__name__}")
# Should print: MaatMemoryPostgres
```

### 4. Migrate Existing Data (If Any)

If you have existing `maat_memory.json` files:

```bash
python3 maat_memory/migrate_to_postgres.py
```

---

## OpenCode Integration

OpenCode (OC2) already has PostgreSQL integration! Just ensure it uses the same database:

### On OpenCode's Machine

```bash
# Set same database URL
export PGVECTOR_DB_URL="postgresql://user:pass@central-server:5434/maat_memory"

# Verify in OpenCode's code
# /mnt/ai_backup/tehuti-memory/core/maat_memory_server.py
# Already uses MaatMemoryPostgres - just needs PGVECTOR_DB_URL
```

### Test OpenCode Connection

```python
from core.maat_memory_server import MAATMemoryServer

server = MAATMemoryServer()
if server.use_postgres:
    print("✅ OpenCode connected to PostgreSQL!")
else:
    print("⚠️  Check PGVECTOR_DB_URL")
```

---

## Architecture

```
┌─────────────────┐
│  Laptop 1      │
│  (Cursor)       │──┐
└─────────────────┘  │
                     │
┌─────────────────┐  │
│  Laptop 2      │  │
│  (Cursor)       │──┼──> PostgreSQL Database
└─────────────────┘  │    (Single Source of Truth)
                     │
┌─────────────────┐  │
│  Laptop 3      │  │
│  (Cursor)       │──┤
└─────────────────┘  │
                     │
┌─────────────────┐  │
│  OpenCode       │  │
│  (OC2)          │──┘
└─────────────────┘
```

**All machines write to the same database = automatic sync!**

---

## Verification Checklist

For each laptop:

- [ ] Dependencies installed (`psycopg2-binary`, `pgvector`, `langchain-huggingface`)
- [ ] `PGVECTOR_DB_URL` environment variable set
- [ ] Connection test passes
- [ ] `MaatMemory()` uses PostgreSQL backend
- [ ] Can save and retrieve sessions
- [ ] Existing JSON data migrated (if any)

**Cross-Machine Test:**

- [ ] Save session on Laptop 1
- [ ] Retrieve session on Laptop 2 ✅
- [ ] Save session on Laptop 3
- [ ] Retrieve on Laptop 1 ✅
- [ ] OpenCode can see all sessions ✅

---

## Troubleshooting

### "PostgreSQL backend not available"

**Solution:** Install dependencies:
```bash
pip install psycopg2-binary pgvector langchain-huggingface
```

### "Connection refused"

**Solution:** Check:
- Database server is running
- Network connectivity
- Firewall rules
- Database credentials

### "pgvector extension not found"

**Solution:** The setup script creates it automatically, or manually:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### "Still using JSON backend"

**Solution:** 
1. Check `PGVECTOR_DB_URL` is set: `echo $PGVECTOR_DB_URL`
2. Restart terminal or run: `source ~/.bashrc`
3. Verify connection works

### "Data not syncing across laptops"

**Solution:**
1. Verify all laptops use the **same** `PGVECTOR_DB_URL`
2. Check database is accessible from all laptops
3. Test connection from each laptop
4. Verify `MaatMemory()` uses `MaatMemoryPostgres` on all laptops

---

## JSON Files Role

After migration, JSON files become:

- ✅ **Local backup** (automatic backup on save)
- ✅ **Fallback** (if PostgreSQL unavailable)
- ✅ **Development mode** (no database needed for testing)

**PostgreSQL is the source of truth for production.**

---

## Benefits

1. **Single Source of Truth**: One database, no conflicts
2. **Real-Time Sync**: Changes visible immediately
3. **Vector Search**: Semantic queries across all machines
4. **No File Conflicts**: Database handles concurrency
5. **Scalable**: Supports unlimited machines
6. **Backup/Recovery**: Standard PostgreSQL tools

---

## Next Steps

1. ✅ Run setup script on all 3 laptops
2. ✅ Verify cross-machine sync works
3. ✅ Configure OpenCode to use same database
4. ✅ Test end-to-end: Save on one, retrieve on another

---

## Support

If you encounter issues:

1. Check `ONBOARDING-GUIDE.md` (this file)
2. Run setup script with verbose output
3. Check PostgreSQL logs
4. Verify network connectivity

---

**The system is ready - no need to wait for core completion!**

