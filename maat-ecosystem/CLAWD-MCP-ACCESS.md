# Expose MCPs to Clawd + ComfyUI Access

**Goal:** Let Clawd (on your PC, e.g. D:\clawd) use the MCP tools (Tehuti Core, n8n, ComfyUI Intelligent, etc.) and have ComfyUI access for image generation.

---

## 1. Overview

- **MCPs** run on the **server** (this machine) via `mcpo` on ports **8011–8021**. By default they bind to `127.0.0.1`, so only localhost can connect.
- **Clawd** runs on another PC. To use those MCPs, the server must:
  1. Bind MCPs to the LAN (`0.0.0.0`) so Clawd can reach them.
  2. Open the MCP ports in the firewall.
- **ComfyUI access** for Clawd = Clawd uses the **ComfyUI Intelligent MCP** (port **8019**). That MCP talks to the **ComfyUI backend** (port **8188**) on the server. So you need:
  - ComfyUI backend running on the server (port 8188).
  - ComfyUI MCP (8019) exposed to the LAN so Clawd can call it.

---

## 2. Server: Expose MCPs to the LAN

### 2.1 Bind mcpo to `0.0.0.0`

Each MCP service runs something like:

```text
uvx mcpo --host 127.0.0.1 --port 8019 -- python3 ...
```

Change `--host 127.0.0.1` to `--host 0.0.0.0` so the port listens on all interfaces (LAN).

**Option A – systemd drop-in (recommended)**  
Create overrides so only the host changes:

```bash
# Example: ComfyUI Intelligent (8019)
sudo mkdir -p /etc/systemd/system/mcpo-comfyui-intelligent.service.d
sudo tee /etc/systemd/system/mcpo-comfyui-intelligent.service.d/override.conf << 'EOF'
[Service]
ExecStart=
ExecStart=/home/suspect/.local/bin/uvx mcpo --host 0.0.0.0 --port 8019 -- python3 /path/to/comfyui_intelligent_server.py
EOF
```

Use the real path to the ComfyUI MCP server. Repeat for every MCP you want Clawd to use (see port list below). Then:

```bash
sudo systemctl daemon-reload
sudo systemctl restart mcpo-comfyui-intelligent.service
```

**Option B – one script for all MCPs**  
If you have a single script that starts all MCPs, change every `--host 127.0.0.1` to `--host 0.0.0.0` in that script and (re)start the services.

### 2.2 Open MCP ports in the firewall

On the server, allow TCP **8011–8021** from the LAN (e.g. `192.168.4.0/24`):

```bash
# If using UFW
sudo ufw allow from 192.168.4.0/24 to any port 8011:8021 proto tcp comment "MCP for Clawd"
sudo ufw status
```

Or use the script below (see **Section 4**).

---

## 3. MCP URLs for Clawd

Replace `SERVER_IP` with the server’s LAN IP (e.g. `192.168.4.21`). Clawd (or whatever MCP client you use with Clawd) should use these **base URLs**:

| Port | Service              | Base URL (Clawd)              |
|------|----------------------|-------------------------------|
| 8011 | Tehuti Curriculum    | `http://SERVER_IP:8011`       |
| 8012 | Tehuti Research      | `http://SERVER_IP:8012`       |
| 8013 | Tehuti Integration   | `http://SERVER_IP:8013`       |
| 8014 | Tehuti Core          | `http://SERVER_IP:8014`       |
| 8015 | n8n MCP              | `http://SERVER_IP:8015`       |
| 8016 | Filesystem MCP       | `http://SERVER_IP:8016`       |
| 8017 | Postgres MCP         | `http://SERVER_IP:8017`       |
| 8018 | Memory MCP           | `http://SERVER_IP:8018`       |
| **8019** | **ComfyUI Intelligent** | `http://SERVER_IP:8019` |
| 8020 | MaatLangChain Pipeline | `http://SERVER_IP:8020`     |
| 8021 | Tehuti Audio         | `http://SERVER_IP:8021`       |

**ComfyUI for Clawd:** Use **port 8019** (ComfyUI Intelligent MCP). That gives Clawd tools like list models, list workflows, generate image, etc. The MCP talks to ComfyUI (8188) on the server; you don’t open 8188 to Clawd unless you want direct ComfyUI API access.

---

## 4. ComfyUI backend (required for ComfyUI MCP)

The ComfyUI Intelligent MCP (8019) calls the **ComfyUI** API on the server (default port **8188**). So on the server:

1. **Start ComfyUI** so it listens on `8188` (e.g. `python main.py --listen 0.0.0.0 --port 8188` or your existing `start_comfyui.sh`).
2. Ensure the ComfyUI MCP config points at that URL (e.g. `http://127.0.0.1:8188` if ComfyUI runs on the same machine).

If ComfyUI is not running, the MCP will respond but image generation and workflow execution will fail until ComfyUI is up.

---

## 5. Scripts on the server

**Open firewall (8011–8021):**
```bash
sudo bash /home/suspect/.n8n/scripts/open-mcp-to-lan.sh
```

**Bind one MCP to LAN (example: Tehuti Core 8014):**
```bash
sudo bash /home/suspect/.n8n/scripts/expose-mcp-bind-lan.sh
```
This creates a systemd override so `mcpo-tehuti-core-fixed` listens on `0.0.0.0:8014`. For ComfyUI (8019) and other MCPs, create the same kind of override (same `ExecStart` but `--host 0.0.0.0` and the correct `--port`).

---

## 6. Clawd: How to use these MCPs

Clawd’s docs (e.g. docs.clawd.bot) may describe an “MCP client” or “tools” config. If it supports **MCP over HTTP**:

- Add the **base URLs** from the table above (e.g. `http://192.168.4.21:8019` for ComfyUI).
- Clawd will then be able to call the tools exposed by each MCP (including ComfyUI image generation via 8019).

If Clawd does **not** support MCP directly:

- Use **n8n** as a bridge: create workflows that call the MCP HTTP endpoints (e.g. OpenAPI at `http://SERVER_IP:8019/openapi.json`) and expose those workflows to Clawd via webhooks or Gateway (see `CLAWDBOT-INTEGRATION.md`). Then “ComfyUI access” for Clawd = Clawd triggers an n8n workflow that calls the ComfyUI MCP (8019).

---

## 7. Quick checklist

- [ ] On server: MCP services bound to `0.0.0.0` (systemd override or script).
- [ ] On server: Firewall allows 8011–8021 from Clawd’s LAN.
- [ ] On server: ComfyUI backend running (port 8188) when using ComfyUI MCP.
- [ ] On Clawd PC: Configure MCP client or n8n with `http://SERVER_IP:8019` (and other ports) for MCP + ComfyUI access.
