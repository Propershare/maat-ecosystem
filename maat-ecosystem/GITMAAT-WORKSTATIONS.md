# gitMaat Workstation Setup

**Purpose:** Connect each workstation (Imhotep PC, imhotepjr 3060, MacDaddy) to the shared gitMaat PostgreSQL on this server so all machines see the same tasks, changes, and learnings.

**Server:** gitMaat runs here. PostgreSQL is the canonical store. Workstations connect to it over the network.

---

## 1. Server (this machine) – open PostgreSQL to the LAN

PostgreSQL with `maat_memory` runs on this server but by default listens only on `127.0.0.1:5432`, so workstations get a connection timeout. Do one of the following.

**Option A – run the script (recommended)**  
On this server, in a terminal:
```bash
cd /home/suspect/.n8n/scripts
sudo bash open-postgres-to-lan.sh
```
This sets `listen_addresses = '*'`, adds a `pg_hba.conf` rule for `192.168.4.0/24`, restarts Postgres, and (if UFW is active) allows port 5432.

**Option B – manual steps**  
- In `postgresql.conf` (e.g. `/etc/postgresql/14/main/postgresql.conf`): set `listen_addresses = '*'`.
- In `pg_hba.conf`: add  
  `host  maat_memory  all  192.168.4.0/24  scram-sha-256`  
  (adjust subnet if your LAN is different).
- Restart: `sudo systemctl restart postgresql`.
- If you use UFW: `sudo ufw allow 5432/tcp`.

**Connection string to give workstations (replace USER, PASSWORD if different):**

```
postgresql://USER:PASSWORD@192.168.4.21:5432/maat_memory
```

Use this server’s LAN IP and **port 5432** (system PostgreSQL where `maat_memory` lives). Do **not** use port 5434 (that was a Docker container; use 5432).

---

## 2. Imhotep PC (Mac) – instruct your agent

Tell your agent on the Imhotep Mac to do the following:

1. **Have the repo (or at least maatlangchain) on the Mac**  
   Clone the workspace so you have a folder that contains `maatlangchain` (with `maat_memory` inside). The “workspace root” is the directory that contains `maatlangchain`.

2. **Create a `.env` in the workspace root** (same folder that contains `maatlangchain`), with one line:
   ```bash
   PGVECTOR_DB_URL=postgresql://USER:PASSWORD@192.168.4.21:5432/maat_memory
   ```
   Replace `USER`, `PASSWORD`, and `5432` with the real Postgres user, password, and port. Use the server’s LAN IP (e.g. `192.168.4.21`).

3. **Install dependency (once):**
   ```bash
   pip install psycopg2-binary
   ```

4. **Test connection:**
   - **If you have the full maatlangchain repo** (including `maat_memory/`): from workspace root run  
     `cd maatlangchain && python3 -c "from maat_memory import MaatMemory; m = MaatMemory(); print('Backend:', type(m).__name__); print('Tasks:', len(m.get_tasks(limit=5)))"`
   - **If you only have a partial repo** (no `maat_memory` package): use the standalone test. Copy `maatlangchain/scripts/test_gitmaat_connection.py` from the server into your project (e.g. into `maatlangchain/scripts/` or workspace root). Put `.env` with `PGVECTOR_DB_URL=...` in the same directory as the script or in the parent (workspace root). Then run:  
     `python3 test_gitmaat_connection.py`  
     You should see `Backend: MaatMemoryPostgres`, `Tasks: N`, and `Sessions: N`. That confirms gitMaat is reachable; later, sync the full repo to use `from maat_memory import MaatMemory` in code.

---

## 3. imhotepjr 3060 – instruct your agent

Same as Imhotep PC, but on the imhotepjr machine:

1. Workspace root = directory that contains `maatlangchain`.
2. In workspace root, create `.env` with:
   ```bash
   PGVECTOR_DB_URL=postgresql://USER:PASSWORD@192.168.4.21:5432/maat_memory
   ```
3. `pip install psycopg2-binary`
4. Test: if full maatlangchain (with `maat_memory/`), run the one-liner from workspace root; if not, use `test_gitmaat_connection.py` as in section 2.

---

## 4. MacDaddy – instruct your agent

Same steps as Imhotep PC (Mac). If MacDaddy is Windows instead of Mac:

- Create `.env` in the workspace root with the same `PGVECTOR_DB_URL=...` line (no `export`).
- Install: `pip install psycopg2-binary`
- Test: if full maatlangchain (with `maat_memory/`), run the one-liner from workspace root; if not, use `test_gitmaat_connection.py` as in section 2.

---

## Summary

| Machine       | OS     | Workspace root = folder containing `maatlangchain` | Action |
|--------------|--------|-----------------------------------------------------|--------|
| Server       | Linux  | (already set)                                      | Ensure Postgres allows LAN; share connection string. |
| Imhotep PC   | Mac    | e.g. `~/path/to/workspace`                         | Add `.env` with `PGVECTOR_DB_URL`, pip install, test. |
| imhotepjr    | Linux  | same idea                                          | Same. |
| MacDaddy     | Mac/Win| same idea                                          | Same; on Windows use `python` in PowerShell. |

After each workstation passes the test, that machine is connected to gitMaat. All of them read and write the same PostgreSQL database on the server.

---

## Test and populate (from your PC)

Once `test_gitmaat_connection.py` works, you can insert test data and list it:

1. **Copy the populate script** from the server: `maatlangchain/scripts/populate_gitmaat_test.py` → into `D:\clawd\` (same folder as `.env` and `test_gitmaat_connection.py`).
2. **Run it** (same .env; use 5432 in PGVECTOR_DB_URL):
   ```powershell
   cd D:\clawd
   python populate_gitmaat_test.py
   ```
   It inserts one task and one change, then prints the last 10 tasks and 10 changes. If that runs, gitMaat is writable from your PC.
3. **Use the full API** when you have the repo: `from maat_memory import MaatMemory` then `memory.log_task(...)`, `memory.get_tasks(...)`, etc. See `maatlangchain/maat_memory/MAAT_LAW_TASKS.md` and `AGENT-ANNOUNCEMENT-DATABASE-FIX.md` for the full workflow.

---

## Standalone script (copy to PC)

If you don't have the full maatlangchain repo, create a file named `test_gitmaat_connection.py` in your workspace (e.g. `D:\clawd\`) with the contents below. Put `.env` in the **same folder** with one line: `PGVECTOR_DB_URL=postgresql://USER:PASSWORD@192.168.4.21:5432/maat_memory`. The scripts **prefer .env over the process environment**, so the workspace URL (5432 for gitMaat) wins even if Windows has an old `PGVECTOR_DB_URL` (e.g. 5434) set. Then run `python test_gitmaat_connection.py` (Windows) or `python3 test_gitmaat_connection.py` (Mac/Linux).

```python
#!/usr/bin/env python3
"""Standalone gitMaat connection test. Needs psycopg2-binary and PGVECTOR_DB_URL in .env (same dir or parent)."""
import os
import sys
from pathlib import Path

def _load_env():
    url = os.environ.get("PGVECTOR_DB_URL")
    if url:
        return url
    script_dir = Path(__file__).resolve().parent
    for p in [script_dir / ".env", Path.cwd() / ".env", script_dir.parent / ".env"]:
        if p.exists():
            try:
                with open(p) as f:
                    for line in f:
                        if line.startswith("PGVECTOR_DB_URL="):
                            return line.split("=", 1)[1].strip().strip('"').strip("'")
            except Exception:
                pass
    return None

def main():
    url = _load_env()
    if not url:
        print("ERROR: PGVECTOR_DB_URL not set. Create .env with PGVECTOR_DB_URL=postgresql://user:pass@host:5432/maat_memory", file=sys.stderr)
        sys.exit(1)
    try:
        import psycopg2
    except ImportError:
        print("ERROR: pip install psycopg2-binary", file=sys.stderr)
        sys.exit(1)
    try:
        conn = psycopg2.connect(url)
        cur = conn.cursor()
        try:
            cur.execute("SELECT COUNT(*) FROM maat_tasks")
            task_count = cur.fetchone()[0]
        except Exception as te:
            task_count = None
            print(f"Tasks: (error: {te})", file=sys.stderr)
        try:
            cur.execute("SELECT COUNT(*) FROM maat_sessions")
            session_count = cur.fetchone()[0]
        except Exception as se:
            session_count = None
            print(f"Sessions: (error: {se})", file=sys.stderr)
        cur.close()
        conn.close()
        print("Backend: MaatMemoryPostgres")
        print(f"Tasks: {task_count if task_count is not None else 'N/A (see stderr)'}")
        print(f"Sessions: {session_count if session_count is not None else 'N/A (see stderr)'}")
        return 0
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    sys.exit(main())
```

---

## Copy-paste instructions for your agent

**Imhotep PC (Mac):** Give your agent this:

```
1. In the workspace root (or the folder that contains maatlangchain), create .env with:
   PGVECTOR_DB_URL=postgresql://USER:PASSWORD@192.168.4.21:5432/maat_memory
   (Replace USER, PASSWORD, 5432 with real values.)

2. pip install psycopg2-binary

3. Test:
   - If you have the full maatlangchain repo (with maat_memory/): from workspace root:
     cd maatlangchain && python3 -c "from maat_memory import MaatMemory; m = MaatMemory(); print('Backend:', type(m).__name__); print('Tasks:', len(m.get_tasks(limit=5)))"
   - If you do NOT have maat_memory (partial clone): copy test_gitmaat_connection.py from the server into your project; put .env in the same dir or parent; run: `python3 test_gitmaat_connection.py` (Mac/Linux) or `python test_gitmaat_connection.py` (Windows PowerShell).
   You should see Backend: MaatMemoryPostgres and task/session counts. Then gitMaat is connected.
```

**imhotepjr 3060 / MacDaddy:** Same as above. **On Windows (PowerShell):** use `python` instead of `python3` (e.g. `python test_gitmaat_connection.py`).

**If the script is not in your repo:** Create `test_gitmaat_connection.py` in your workspace (e.g. `D:\clawd\`) with the contents from the "Standalone script (copy to PC)" section below. Put `.env` in the same folder with `PGVECTOR_DB_URL=postgresql://...`, then run `python test_gitmaat_connection.py`.
