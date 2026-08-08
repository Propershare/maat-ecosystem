# Maat Ecosystem — connectivity freeze (agent spine)

**Status:** Freeze for **connectivity and discovery** only. **Tehuti Guard** is the **next** layer: policy, validation gates, and three-ring rules—**not** a prerequisite for proving that agents can reach the Ka body via Discovery and organs.

**Network plane (Wi‑Fi / Ethernet / SSH / VPN intent, ComfyUI + MCP ports, UFW):** [MAAT-NETWORK-PLANE.md](MAAT-NETWORK-PLANE.md) — **canonical**; do not fork connectivity stories elsewhere.

**Canonical connect guide:** [GITMAAT-CONNECT.md](GITMAAT-CONNECT.md) (database URL, Tehuti Core, verification commands).

**Ka DNA on disk:** `maat-ecosystem/MANIFEST.ka` (intended ports; Discovery is the live map).

---

## 1. What we proved (design)

Any agent that can speak **HTTP** (and optionally **PostgreSQL** for direct DB use) can join the ecosystem **without hardcoding** every organ:

1. **`GET http://<host-lan-ip>:8010/manifest`** — full body map (brain, memory, hands, etc.) with **LAN endpoints**.
2. **`GET http://<host-lan-ip>:8010/health`** — aggregate organ health.
3. **`GET http://<host-lan-ip>:8010/connect`** — human-readable connection recipe and examples.

**Policy (Tehuti Guard):** HTTP **`8013`** — `POST /decision`; **not** under `mcp-servers/` (source **`tehuti-guard/`** at lab root). Live **`/manifest`** includes organ **`policy`** with endpoint and `source_path`.

**Brain (gitMaat tools):** Tehuti Core MCP, typically **`8014`** — `openapi.json` documents tool calls.

**Memory organ (Maat Memory MCP):** typically **`8022`** — richer memory/logging tools; brain may expose a subset (`legacy_*` in manifest).

**Persistence truth:** one PostgreSQL database via **`PGVECTOR_DB_URL`** (same DB that MCP servers use when started with workspace `.env`).

**Organ auth:** manifest advertises **Bearer `KA_API_KEY`** on organ routes; keep the key in env or `.ka-auth` as you already do for operators—**do not commit secrets**.

---

## 2. Smoke test snapshot — host `staydangerous` (2026-04-07)

Recorded from this workspace after live `curl` checks:

| Check | Result |
|--------|--------|
| `8010` listening | `0.0.0.0:8010` (reachable on LAN) |
| `/manifest` | `kind: ka-body`, `discovery: http://192.168.4.21:8010`, organs include **policy 8013** (Tehuti Guard), **brain 8014**, **memory 8022** |
| `/health` | **7 healthy / 8 organs** — **`8015` (n8n MCP) dead**; overall `degraded` |
| `8014/openapi.json` | OK (Tehuti Core) |
| `8022/docs` | HTTP 200 (Maat Memory MCP docs) |

### 2.1 Soul path in manifest (restart required)

Repo code sets the soul filesystem root to **`$HOME/.n8n/maat-ecosystem/soul/`** (see `maat-ecosystem/mcp-servers/ka-discovery/ka_discovery_server.py`).  

The **running** `ka-discovery` process may still serve **`/home/suspect/maat-ecosystem/soul/`** if it was started **before** that change.

**Fix (operator, once):**

```bash
sudo systemctl restart ka-discovery.service
```

Then re-check:

```bash
curl -s http://127.0.0.1:8010/manifest | jq -r '.organs.soul.path'
```

Expect: `/home/suspect/.n8n/maat-ecosystem/soul/` (or your `$HOME` equivalent).

---

## 3. Per-agent wiring (minimal)

Goal: **same spine** for Cursor, OpenCode, OpenClaw, WebUI, or a custom bot: **Discovery first**, then organs.

| Agent / surface | How it connects | Notes |
|-------------------|-----------------|--------|
| **Cursor** | Project MCP HTTP tools pointing at **`8014`** / **`8022`**, or read Discovery **`8010`** once and configure | Cursor already uses MCP descriptors under the IDE project; LAN IP required from **another** machine. |
| **OpenCode** | **On host:** stdio MCP to local Tehuti script is fine. **Remote:** HTTP/OpenAPI base **`http://<lan>:8014`**, server process must have **`PGVECTOR_DB_URL`**. | See `opencode.json` patterns in repo; align with [GITMAAT-CONNECT.md](GITMAAT-CONNECT.md). |
| **OpenClaw** | Register **HTTP MCP** (OpenAPI) for **`8014`** (and optionally **`8022`**) per OpenClaw/mcporter docs; agents can also use **mcporter** to call organs ad hoc | **`~/.openclaw/openclaw.json`** does not embed Tehuti URLs by default—connection is **skill/config**, not blocked by missing code. |
| **Open WebUI / others** | External tools / MCP URL **`http://<lan>:8014`** | Same as GITMAAT-CONNECT §3. |

**Nothing in this freeze blocks** wiring the above: they are all **HTTP + env** clients of the same organs.

---

## 4. Optional / follow-ups (out of freeze scope)

- **Port `8015` (n8n MCP):** currently **dead** in health check; either restore the service or treat n8n as **optional** for the minimal “brain + memory + discovery” pivot.
- **Tehuti Guard:** add as **post-connection** validation (approve/block/propose) once every agent reliably reaches Discovery and Tehuti Core.
- **Direct `MaatMemory()` from a shell:** requires **`PGVECTOR_DB_URL`** loaded in **that** shell; MCP units may still work via `EnvironmentFile` in systemd.

---

## 5. Quick verification commands (copy-paste)

Replace `<LAN>` with your server IP (example: `192.168.4.21`).

```bash
# Discovery
curl -s "http://<LAN>:8010/manifest" | head -c 1200
curl -s "http://<LAN>:8010/health" | jq .

# Brain + memory organs
curl -s "http://<LAN>:8014/openapi.json" | head -c 400
curl -s -o /dev/null -w "%{http_code}\n" "http://<LAN>:8022/docs"
```

---

## 6. Freeze boundary

**In scope (done / documented):** Ka Discovery as the **single front door**, organ ports, health semantics, **`PGVECTOR_DB_URL`** as DB contract, and a **repeatable test matrix**.

**Out of scope (next phase):** Tehuti Guard enforcement in the request path, n8n MCP recovery, and product-specific UIs (e.g. Ka Education) — they **ride on top of** this spine.

When operators complete **`ka-discovery` restart** and confirm the soul path, treat **connectivity** as **green** for the pivot; treat **`8015`** and **Guard** as **separate work tracks**.
