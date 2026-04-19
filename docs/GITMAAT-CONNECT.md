# How agents connect to Maat Memory (gitMaat) — exact steps

**Network plane (SSH, LAN, ComfyUI/MCP ports, future VPN — single source):** [MAAT-NETWORK-PLANE.md](MAAT-NETWORK-PLANE.md)

**Connectivity freeze (test matrix, per-agent wiring, health snapshot):** [MAAT-ECOSYSTEM-CONNECTIVITY-FREEZE.md](MAAT-ECOSYSTEM-CONNECTIVITY-FREEZE.md)

## 0. Ka Discovery first (Maat Ecosystem design)

On the **Tehuti Lab / Ka** network, agents should **not hardcode** organ URLs. **Ka Discovery** on port **8010** publishes the live body map with the server’s **primary LAN IP** (`HOST_IP` in `maat-ecosystem/mcp-servers/ka-discovery/ka_discovery_server.py`).

1. `GET http://<server-lan-ip>:8010/manifest` — JSON lists `organs.memory.endpoint` (**8022** Maat Memory MCP), `organs.brain.endpoint` (**8014** Tehuti Core, includes gitMaat tools), etc.
2. `GET http://<server-lan-ip>:8010/connect` — connection recipe + curl examples (uses LAN IP).
3. **Persistence** for gitMaat is still **PostgreSQL** via **`PGVECTOR_DB_URL`** (below); MCP wraps the same DB.

Canonical Ka DNA file: `maat-ecosystem/MANIFEST.ka` (`network:` block mirrors intended ports).

---

**Reference values (this workspace / Imhotep server):**
| What | Value |
|------|--------|
| Postgres user | `suspect` |
| Postgres password | In `.env`; example in `scripts/start-tehuti-core-mcp.sh` and `systemd-services/maatlangchain-pipeline-mcp.service` |
| Host (same machine) | `localhost` |
| Host (server from LAN) | `192.168.4.21` |
| DB port | `5432` (not 5434) |
| Workspace root | `/home/suspect/.n8n` |
| Tehuti Core (brain service) port | `8014` (may appear under legacy label `maat-core` in older configs/docs) |
| Ka Discovery (HTTP) | `8010` |
| Maat Memory MCP (organ) | `8022` |

**Postgres data directory:** whatever your cluster uses (native `/var/lib/postgresql/...` or Docker named volume). Agents do **not** read those files — they use **`PGVECTOR_DB_URL`** so everyone hits the **same** `maat_memory` database.

---

## 1. Database URL (required)

**Workspace `.env`:** `/home/suspect/.n8n/.env`

```bash
# Same machine as Postgres (e.g. server)
PGVECTOR_DB_URL=postgresql://suspect:YOUR_PASSWORD@localhost:5432/maat_memory

# Or from another machine (workstation → server)
PGVECTOR_DB_URL=postgresql://suspect:YOUR_PASSWORD@192.168.4.21:5432/maat_memory
```

- Replace `YOUR_PASSWORD` with the real Postgres password for user `suspect`. No password → `fe_sendauth: no password supplied`.
- **Port:** `5432` (gitMaat); do not use 5434.

---

## 2. Tehuti Core MCP (gateway to gitMaat)

- **Port:** `8014`
- **Base URL (same machine):** `http://127.0.0.1:8014`
- **Base URL (from another machine):** `http://192.168.4.21:8014` (server LAN IP)

**Start/check:**

```bash
# Running?
curl -s http://127.0.0.1:8014/openapi.json | head -5

# Start (manual)
/home/suspect/.n8n/scripts/start-tehuti-core-mcp.sh

# Or systemd
sudo systemctl start mcpo-tehuti-core
sudo systemctl status mcpo-tehuti-core
```

**So the MCP sees the DB:** Either set `PGVECTOR_DB_URL` in the environment before starting (e.g. in `.env` and `EnvironmentFile=-/home/suspect/.n8n/.env` in the systemd unit), or rely on Tehuti Core reading workspace root `.env` at startup.

---

## 3. Client: point the agent at Tehuti Core

### OpenClaw (primary)

- **Embedded Pi / gateway tools:** register **stdio** MCP servers for Tehuti Core and Maat Memory so OpenClaw loads real MCP tools (e.g. `tehuti-core__query_gitmaat`, `maat-memory__memory_get_tasks`). The lab’s **mcpo** ports **8014** / **8022** expose **OpenAPI** to the network; they are **not** a drop-in `mcp.servers.*.url` for OpenClaw’s MCP HTTP client. Full layout, JSON snippets, and verification: [`docs/OPENCLAW-MAAT-MCP.md`](OPENCLAW-MAAT-MCP.md).
- Set **`plugins.slots.memory`** to **`memory-core`** (and enable the **memory-core** plugin entry) so the bundled memory plugin slot is explicit.
- **OpenAPI-only** integrations (no OpenClaw) can still call **`http://127.0.0.1:8014`** / **`http://192.168.4.21:8014`** as a REST/OpenAPI surface (`/openapi.json`).

### Open WebUI (still in use)

- **Chat settings** for the model → **External Tools** (or MCP / tool servers).
- Add or enable **Tehuti Core** with URL: `http://127.0.0.1:8014` (same machine) or `http://192.168.4.21:8014` (remote).
- Save. The model will see `tool_query_gitmaat_post` (or equivalent) and can call gitMaat.

---

## 4. Verify

**MCP up:**

```bash
curl -s http://127.0.0.1:8014/openapi.json | head -20
```

**DB from workspace (same env the MCP uses):**

```bash
cd /home/suspect/.n8n/maatlangchain && python3 -c "
from maat_memory import MaatMemory
m = MaatMemory()
print('Backend:', type(m).__name__)
print('Tasks:', len(m.get_tasks(limit=5)))
"
```

Expect: `Backend: MaatMemoryPostgres` and a number. If you see JSON backend or an error, fix `PGVECTOR_DB_URL` and/or Postgres access.

---

**Summary:** Set `PGVECTOR_DB_URL` in workspace `.env` → run Tehuti Core MCP on **8014** (mcpo/OpenAPI for HTTP clients) → **Open WebUI** and similar: tool server URL `http://127.0.0.1:8014` or `http://192.168.4.21:8014` → **OpenClaw:** stdio `mcp.servers` + memory slot per [`docs/OPENCLAW-MAAT-MCP.md`](OPENCLAW-MAAT-MCP.md).
