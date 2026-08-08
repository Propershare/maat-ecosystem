# Claude Desktop → lab MCP over SSH (Imhotep PC → server)

Claude Desktop runs on your **workstation**; Maat Memory / Tehuti Core MCP run on **this lab server**. Desktop only speaks **stdio** MCP, so we **SSH** to the server and run the Python FastMCP servers with **stdin/stdout** wired through the tunnel.

**This is not the same** as the HTTP Maat Memory on **:8022** (`mcpo` in `start_maat_memory.sh`). That process is for LAN/WebUI-style HTTP; Claude Desktop here uses **stdio** via `maat_memory_server.py` directly.

## Prerequisites

1. **Same SSH** you use for Cursor (key-based login, no password prompt). `BatchMode=yes` in the example fails fast if a password is required.
2. From the **Imhotep PC**, reach the server: `ssh REPLACE_SSH_TARGET` works (hostname from `~/.ssh/config` or `user@host`).
3. **Paths** below assume server user and lab root: `suspect` and `/home/suspect/.n8n` (adjust if your server account differs).

## Server (already in this repo)

- `scripts/run-maat-memory-mcp-for-claude.sh` — loads `.env` / `maatlangchain/.env`, runs Maat Memory MCP stdio.
- `scripts/run-tehuti-core-mcp-for-claude.sh` — optional; **high power** (shell/tools on server). Disable in JSON if you do not want it.

Make them executable on the server:

```bash
chmod +x /home/suspect/.n8n/scripts/run-maat-memory-mcp-for-claude.sh
chmod +x /home/suspect/.n8n/scripts/run-tehuti-core-mcp-for-claude.sh
```

## Imhotep PC — Claude Desktop config

**Linux:** `~/.config/Claude/claude_desktop_config.json`  
**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

1. Merge or create the file so it contains a top-level `"mcpServers"` object.
2. Copy from `docs/examples/claude_desktop_config.remote-lab.example.json`.
3. Replace **`REPLACE_SSH_TARGET`** with your real target, e.g. `suspect@192.168.4.21` or `suspect@staydangerous` (whatever matches `ssh` from the PC).
4. Remove the **`tehuti-core-optional`** block entirely if you only want gitMaat memory tools, not Tehuti Core execution tools.

### Windows note

If `ssh` is not on `PATH`, set `"command"` to the full path of OpenSSH, e.g. `C:\\Windows\\System32\\OpenSSH\\ssh.exe`, and keep the same `args`.

### Quick SSH test (from Imhotep PC)

```bash
ssh -T YOUR_TARGET /home/suspect/.n8n/scripts/run-maat-memory-mcp-for-claude.sh </dev/null
```

You should see log lines on stderr and **no** prompt; press Ctrl+C if it does not exit (stdio server may wait — that is OK when Claude spawns it).

## After editing

Fully quit Claude Desktop and reopen. Check **Settings → Developer** (or MCP) that servers show connected.

## Security

- **SSH** is your trust boundary; use keys, consider `AllowUsers`, firewall LAN-only SSH if appropriate.
- **Tehuti Core** MCP can run commands on the server — treat it like root-level access to the lab. Prefer **Maat Memory only** until you explicitly need Core from Desktop.

## See also

- `docs/GITMAAT-CONNECT.md` — DB and organ ports on the LAN (`8022` HTTP is separate from this stdio path).
