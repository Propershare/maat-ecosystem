# Why Agents Can't Access Maat Memory (gitMaat) — Causes & Fixes

This doc explains common reasons agents (Cursor, OpenClaw, Open WebUI models, MCP servers, n8n, ClawdBot, etc.) fail to access Maat Memory and how to fix them. **Primary client:** OpenClaw on all machines; Open WebUI is still used where needed.

---

## 1. **PGVECTOR_DB_URL not available to the process**

**Cause:** The agent runs in a process that never loads your workspace `.env` (e.g. Tehuti Core MCP started by systemd, or OpenClaw/Open WebUI calling MCP). Without `PGVECTOR_DB_URL`, `maat_memory` either falls back to JSON or fails when using PostgreSQL.

**Fixes:**

- **Workspace root `.env`:** Ensure `/home/suspect/.n8n/.env` contains:
  ```bash
  # This workspace: user suspect, server 192.168.4.21, port 5432
  PGVECTOR_DB_URL=postgresql://suspect:YOUR_PASSWORD@localhost:5432/maat_memory
  # Or from another machine:
  PGVECTOR_DB_URL=postgresql://suspect:YOUR_PASSWORD@192.168.4.21:5432/maat_memory
  ```
  Replace `YOUR_PASSWORD` with the real Postgres password. No password → `fe_sendauth: no password supplied`.

- **Tehuti Core MCP:** It now loads `PGVECTOR_DB_URL` from (in order) workspace root `.env`, `maatlangchain/.env`, `tehuti-lab-webui/.env`, `open-webui/.env`. Restart the MCP after adding/editing `.env`:
  ```bash
  sudo systemctl restart mcpo-tehuti-core
  ```

- **Systemd:** The unit `mcpo-tehuti-core-fixed.service` includes `EnvironmentFile=-/home/suspect/.n8n/.env` so the service gets `PGVECTOR_DB_URL` from workspace `.env` when present. Reinstall/update the unit if you use a custom one.

---

## 2. **Cursor / IDE “agents” don’t run Python automatically**

**Cause:** The `.cursorrules` “query gitMaat first” snippet is **instructional**. Cursor doesn’t execute that Python by itself; it only runs code when you run a terminal command or use a tool (e.g. MCP).

**Fixes:**

- Use **Tehuti Core MCP** and enable it in Cursor, OpenClaw, or Open WebUI (whichever client you use) so the model can call `query_gitmaat` (or `tool_query_gitmaat_post`).
- Or run gitMaat explicitly in the terminal when you need it:
  ```bash
  cd /home/suspect/.n8n/maatlangchain && python3 -c "
  from maat_memory import MaatMemory
  m = MaatMemory()
  print(m.get_tasks(limit=5))
  "
  ```

---

## 3. **Python path / no `maat_memory` package**

**Cause:** Scripts or MCPs run with a different CWD or `PYTHONPATH` that doesn’t include the `maatlangchain` directory, so `from maat_memory import MaatMemory` fails with `ModuleNotFoundError`.

**Fixes:**

- Run from workspace root and add `maatlangchain` to the path before importing:
  ```python
  import sys
  from pathlib import Path
  workspace_root = Path("/home/suspect/.n8n")  # or detect via (path / "maatlangchain").exists()
  sys.path.insert(0, str(workspace_root / "maatlangchain"))
  from maat_memory import MaatMemory
  ```
- Tehuti Core MCP already does this with `WORKSPACE_ROOT` (detected from CWD/parents). Ensure the MCP is started from a directory under the workspace (e.g. `mcp-servers/tehuti-core`) so `WORKSPACE_ROOT` is correct.

---

## 4. **Tehuti Core MCP not enabled or not running**

**Cause:** OpenClaw, Open WebUI, or other clients only expose gitMaat if the model can call Tehuti Core tools. If Tehuti Core isn’t enabled or the service isn’t running, “query gitMaat first” can’t be executed.

**Fixes:**

- **Enable in client:** In **OpenClaw** (primary on all machines) or **Open WebUI** (still in use): ensure Tehuti Core / gitMaat tools are enabled for the agent (e.g. Open WebUI → Chat settings → External Tools → **Tehuti Core** or `server:openapi:tehuti-core`).
- **Check process:** `systemctl status mcpo-tehuti-core` or `curl -s http://127.0.0.1:8014/openapi.json`.
- **Restart after .env changes:** `sudo systemctl restart mcpo-tehuti-core`.

---

## 5. **PostgreSQL unreachable or wrong credentials**

**Cause:** Wrong host/port, firewall, or invalid user/password. Typical error: `connection to server at "localhost" (127.0.0.1), port 5432 failed: fe_sendauth: no password supplied` or `connection refused`.

**Fixes:**

- Confirm `PGVECTOR_DB_URL` has the correct host, port (`5432` for gitMaat, not 5434), **username**, and **password**.
- From the machine where the agent runs: `psql "$PGVECTOR_DB_URL" -c 'SELECT 1'`.
- If PostgreSQL is on another host (e.g. `192.168.4.21`), ensure `pg_hba.conf` allows the agent’s host and that the password is correct. See `GITMAAT-WORKSTATIONS.md` for LAN setup.

---

## Quick verification

From workspace root (with `.env` containing `PGVECTOR_DB_URL`):

```bash
cd /home/suspect/.n8n/maatlangchain && python3 -c "
from maat_memory import MaatMemory
m = MaatMemory()
print('Backend:', type(m).__name__)
print('Tasks:', len(m.get_tasks(limit=5)))
"
```

You should see `Backend: MaatMemoryPostgres` and a number of tasks. If you see `MaatMemory` (JSON backend) or an error, fix `PGVECTOR_DB_URL` and/or connectivity as above.
