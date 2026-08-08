# Windows Quick Start Guide

## You're on Windows! Here's what to do:

### Step 1: Find Your Project

The project should be somewhere like:
- `C:\Users\Imhotep\.n8n\maatlangchain\`
- Or wherever you have the maatlangchain folder

### Step 2: Install Dependencies

```powershell
pip install psycopg2-binary pgvector langchain-huggingface
```

### Step 3: Set Database URL

```powershell
$env:PGVECTOR_DB_URL = "postgresql://suspect:<password>@192.168.4.21:5434/n8n_ai_starter"
```

Or add to System Environment Variables permanently.

### Step 4: Run Setup

```powershell
cd C:\path\to\maatlangchain
python scripts\setup_maat_memory.py
```

**Note:** Use `python` not `python3` on Windows!

### Step 5: Verify

```powershell
python -c "from maat_memory import MaatMemory; m = MaatMemory(); print('✅ Working!')"
```

---

**See:** `ONBOARDING-GUIDE.md` for complete Linux/Windows instructions.

