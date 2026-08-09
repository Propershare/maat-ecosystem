# OpenClaw Dashboard from Laptop — Fix "gateway token mismatch"

The error **"disconnected (1008): unauthorized: gateway token mismatch"** means the dashboard on your laptop is reaching the Gateway but not sending the correct token.

Ports: **Imhotep = 18789**, **this machine = 18790** (no conflict).

---

## Fix: Use the gateway token on your laptop

### Step 1 — Get the token on the server (where OpenClaw runs)

On the machine where OpenClaw is running (this one, not Imhotep), run:

```bash
nvm use 22
openclaw dashboard --no-open
```

(Equivalent from the repo checkout: `cd /home/suspect/.n8n/openclaw && node openclaw.mjs dashboard --no-open`.)

You’ll see something like:

```text
Dashboard URL: http://127.0.0.1:18790/?token=abc123def456...
Copied to clipboard.
```

- Copy the **full URL** (including `?token=...`), **or**
- Copy only the **token** part (the long string after `token=`).

Alternatively, read the token from config:

```bash
grep -A1 '"token"' ~/.openclaw/openclaw.json
# or
node -e "const c=require(require('path').join(process.env.HOME,'.openclaw/openclaw.json')); console.log(c.gateway?.auth?.token||'not set')"
```

---

### Step 2 — On your laptop, open the dashboard with the token

**Option A — Token in the URL (easiest)**

1. Replace `127.0.0.1` with this machine’s **LAN IP** (e.g. `192.168.4.21`).
2. Open in the browser:
   ```text
   http://THIS_MACHINE_IP:18790/?token=YOUR_TOKEN
   ```
   Example: `http://192.168.4.21:18790/?token=abc123def456...`

**Option B — Paste token in Settings**

1. Open: `http://THIS_MACHINE_IP:18790/` (no token in URL).
2. In the dashboard, open **Settings** (or **Gateway Access** / connection settings).
3. Set:
   - **WebSocket URL:** `ws://THIS_MACHINE_IP:18790`
   - **Gateway Token:** paste the token from Step 1.
4. Click **Connect**.

---

### Step 3 — If the laptop can’t reach the Gateway at all

The Gateway must listen on the LAN. On the server, start it with:

```bash
nvm use 22
openclaw gateway run --port 18790 --bind lan --verbose
```

Or in config `~/.openclaw/openclaw.json`:

```json
{
  "gateway": {
    "port": 18790,
    "bind": "lan"
  }
}
```

Then restart the gateway. Ensure the firewall allows TCP **18790** from your LAN.

---

## Stop and start OpenClaw (this server — `.21`)

Use **Node 22+** (e.g. `nvm use 22`). The CLI is `openclaw` once installed via npm/nvm.

### Stop

```bash
# Preferred: stops the supervised gateway + user service if installed
openclaw gateway stop

# If a user systemd unit exists
systemctl --user stop openclaw-gateway.service

# If something still holds port 18790
ss -ltnp | grep 18790
kill -TERM <PID-of-openclaw-gateway>
```

### Start

**Foreground** (good for debugging; Ctrl+C to stop):

```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
nvm use 22
openclaw gateway run --port 18790 --bind lan --verbose
```

**Replace a stuck listener** (kills whatever is on the port, then starts):

```bash
openclaw gateway run --port 18790 --bind lan --verbose --force
```

**systemd (user)** — if you ran `openclaw gateway install` before:

```bash
systemctl --user start openclaw-gateway.service
systemctl --user status openclaw-gateway.service --no-pager
```

Config must have `gateway.mode` set (e.g. `local`) and a valid `~/.openclaw/openclaw.json`. Dashboard token: `openclaw dashboard --no-open`.

---

## Summary

| What you need | Where |
|---------------|--------|
| Token | Server: `openclaw dashboard --no-open` or `~/.openclaw/openclaw.json` → `gateway.auth.token` |
| Dashboard URL on laptop | `http://SERVER_IP:18790/?token=TOKEN` or paste token in Settings |
| Port this machine | **18790** (Imhotep stays on **18789**) |

Once the token in the URL (or in Settings) matches `gateway.auth.token` (or `OPENCLAW_GATEWAY_TOKEN`) on the server, the “gateway token mismatch” error goes away.
