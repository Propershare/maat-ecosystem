# OpenCode Lab Power-Up — Cross-Machine Reference

**Audience:** every_lab_agent  
**Slug:** `opencode/lab-powerup-2026-08-08`  
**Author:** opencode_staydangerous (operator + assistant collaboration)  
**Last touched:** 2026-08-08  
**Supersedes:** none

> **TL;DR for any agent that lands here from a sibling machine:**
> 1. Read `~/.opencode-rules/00-lab-doctrine.md` first (it's loaded by opencode automatically).
> 2. If you are running on a fresh machine, follow the **Bootstrap recipe** at the bottom of this doc.
> 3. If MCPs are missing, jump to **MCP bootstrap**.
> 4. If you need to reach another lab box, jump to **SSH / Tailscale topology**.

This doc is the **actionable summary** of decisions logged in maat_memory on 2026-08-08.
It is written once, stored as a portable artifact (`maat://object/<sha256>`), and
fetched by any agent on any machine that needs to recreate or repair the lab setup.

The raw decisions (with rationale) live in:
- decision_id `87e20198-6f0e-4b34-8b3b-f61d63f1baf8` — SSH topology
- decision_id `34993e13-8b48-4182-ba38-943a11f0bc24` — global rules directory
- decision_id `c6cc5aec-3f40-48bf-8a2e-f32b3a857b77` — MCP stdio bootstrap

---

## 1. Lab architecture in one paragraph

The lab is a **federation of Tailscale nodes**. Each node runs opencode with the
same global rules (loaded from `~/.opencode-rules/`), the same MAAT memory client
(writing to its local Postgres), and a per-machine ed25519 keypair that lets it
ssh to siblings over the Tailscale overlay. Files stay per-machine; a single
synced `~/.opencode-rules/` directory is the source of truth for global
behavior. Project-specific rules stay in each repo's `AGENTS.md` and override
the global ones when they conflict.

## 2. Global rules directory (LAW)

**Path:** `~/.opencode-rules/`  
**Loaded by:** `~/.config/opencode/opencode.json` → `instructions:` field  
**Fallback for old opencode:** `~/.config/opencode/AGENTS.md` (collapsed to a 9-line pointer)

Files (in load order):

| File | What it carries |
|------|----------------|
| `00-lab-doctrine.md` | Dual-agent law, order of authority, spine organs, evidence publishing |
| `10-agent-protocol.md` | Standard agents, MAAT memory protocol, constitutional compliance |
| `20-mcp-bootstrap.md` | stdio vs HTTP MCP lessons + diagnostic commands |
| `40-ssh-topology.md` | Lab inventory, trust model, file sharing, onboarding, recovery |
| `opencode-rules-sync.sh` | `opencode-rules pull` — fetch latest rules (git/rsync/curl) |
| `sshd/99-tehuti-lab.conf` | sshd hardening drop-in |
| `sshd/tehuti-lab-banner` | Banner shown on hardened sshd |

**Sync mechanism (TBD — pick one and uncomment in `opencode-rules-sync.sh`):**
- Option A: `git clone git@github.com:<lab>/opencode-rules.git`
- Option B: `rsync -a peer-host:/srv/opencode-rules/`
- Option C: `curl -L https://<host>/opencode-rules.tar.gz | tar -xz`

If none is set, the script exits with a clear error. **Do not silently fall back.**

## 3. MCP bootstrap (the most common failure)

Symptom: only `tehuti-core_*` tools appear; `maat_memory_*` is missing.

Root cause: `opencode.json` was pointing `maat-memory` at a bash launcher
(`start_maat_memory.sh`) that wraps a stdio server in mcpo as an HTTP proxy.
opencode expects stdio JSON-RPC; mcpo spawns a TCP daemon; opencode times out
waiting for stdio frames; the daemon holds the port; respawns die EADDRINUSE.

**Fix on any machine:**

```jsonc
// ~/.config/opencode/opencode.json  →  mcp block
"maat-memory": {
  "command": [
    "/home/suspect/.n8n/mcp-servers/maat-memory/.venv/bin/python",
    "/home/suspect/.n8n/mcp-servers/maat-memory/maat_memory_server.py"
  ],
  "enabled": true,
  "type": "local",
  "environment": {
    "PGVECTOR_DB_URL": "postgresql://suspect:disdick@localhost:5432/maat_memory"
  }
}
```

**Diagnostic commands (any machine):**

```bash
# 1. Find failures in the log
grep -E "server unavailable|EADDRINUSE" ~/.local/share/opencode/log/opencode.log | tail

# 2. Check what's holding the port
ss -ltnp | grep -E ":(8022|8010) "

# 3. Verify stdio server works on its own
{ printf '%s\n' \
  '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"smoke","version":"0"}}}' \
  '{"jsonrpc":"2.0","method":"notifications/initialized"}' \
  '{"jsonrpc":"2.0","id":2,"method":"tools/list"}'; sleep 2; } \
  | /home/suspect/.n8n/mcp-servers/maat-memory/.venv/bin/python \
    /home/suspect/.n8n/mcp-servers/maat-memory/maat_memory_server.py
```

**Expected:** the third frame returns a list of 23 tools including `memory_log_*`,
`memory_search`, `memory_law`, `memory_get_artifacts`, `memory_fetch_artifact`.

**Do NOT register `ka-discovery` as an MCP.** It's a BaseHTTP discovery map, not
a stdio MCP. If you need discovery, fetch it via the running HTTP server (`:8010`)
or write a stdio wrapper — but don't pretend it's an MCP.

## 4. SSH / Tailscale topology

**Transport:** Tailscale overlay, tailnet `psnpropershare@`.  
**Auth:** Tailscale handles identity; SSH handles commands/files with per-machine ed25519.  
**No password auth, ever.**  
**No root ssh, ever.**  
**File sharing:** per-machine dirs + `opencode-rules pull`. No NFS, no Syncthing.

**Current inventory (2026-08-08):**

| Host | Tailscale IP | OS | Status |
|------|--------------|----|--------|
| staydangerous | 100.77.143.8 | linux | online |
| desktop-ccitn8l | 100.116.101.98 | windows | offline (last seen 9h) |

When the topology changes, update `40-ssh-topology.md` (in `~/.opencode-rules/`)
and re-sync.

**Quick ssh sanity check from any box:**

```bash
ssh -G staydangerous        # resolves to 100.77.143.8, user suspect, key id_ed25519
ssh -o BatchMode=yes staydangerous 'echo OK'  # should print OK
ssh desktop-ccitn8l          # currently fails — Windows box is offline
```

## 5. Bootstrap recipe for a fresh lab machine

```bash
# 0. Assumptions: Ubuntu 22+ (or equivalent), user `suspect`, root via sudo.

# 1. Tailscale
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up    # log in to the psnpropershare tailnet

# 2. Generate this box's keypair (no passphrase for unattended sync)
ssh-keygen -t ed25519 -a 100 -C "$(hostname)@tehuti-lab-$(date +%F)" \
  -f ~/.ssh/id_ed25519 -N ""

# 3. Append own pubkey to authorized_keys (enables self-ssh via tailnet IP)
cat ~/.ssh/id_ed25519.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

# 4. Hardened sshd drop-in
sudo cp ~/.opencode-rules/sshd/99-tehuti-lab.conf /etc/ssh/sshd_config.d/
sudo cp ~/.opencode-rules/sshd/tehuti-lab-banner /etc/ssh/
sudo sshd -t && sudo systemctl reload ssh

# 5. Sync the opencode rules
git clone <lab-rules-repo> ~/.opencode-rules    # or rsync/curl — see §2

# 6. Wire opencode.json to load the rules
python3 - <<'PY'
import json, pathlib
p = pathlib.Path.home() / ".config/opencode/opencode.json"
d = json.loads(p.read_text()) if p.exists() else {}
d.setdefault("$schema", "https://opencode.ai/config.json")
instr = [
    "/home/suspect/.opencode-rules/00-lab-doctrine.md",
    "/home/suspect/.opencode-rules/10-agent-protocol.md",
    "/home/suspect/.opencode-rules/20-mcp-bootstrap.md",
    "/home/suspect/.opencode-rules/40-ssh-topology.md",
]
existing = set(d.get("instructions", []))
d["instructions"] = [x for x in instr if x not in existing] + \
                    [x for x in d.get("instructions", []) if x not in instr]
p.write_text(json.dumps(d, indent=2))
print("opencode.json updated")
PY

# 7. Replace global fallback AGENTS.md with the pointer
cat > ~/.config/opencode/AGENTS.md <<'EOF'
# Global OpenCode Agent Instructions
> Source of truth: ~/.opencode-rules/
> If you can read this, you should also be loading:
> - ~/.opencode-rules/00-lab-doctrine.md
> - ~/.opencode-rules/10-agent-protocol.md
> - ~/.opencode-rules/20-mcp-bootstrap.md
> - ~/.opencode-rules/40-ssh-topology.md
EOF

# 8. Verify stdio MCP (see §3 diagnostic)

# 9. Restart opencode, confirm `tehuti-core_*` AND `maat_memory_*` tools appear.
```

## 6. What NOT to do (lesson log)

- **Do not** register HTTP/Tailscale-only daemons as stdio MCPs. Opencode will
  not bridge them; you'll get "server unavailable" warnings and EADDRINUSE on
  respawn.
- **Do not** share a single "deploy key" across machines. Per-machine ed25519
  keeps revocation local.
- **Do not** re-enable password auth "just for now" — it's a footgun. Console
  in via Tailscale SSH instead, or use a live USB.
- **Do not** edit `/etc/ssh/sshd_config` directly. Use the drop-in under
  `sshd_config.d/` so the diff stays auditable and reversible.
- **Do not** invent duplicate AGENTS.md content. The pointer file at
  `~/.config/opencode/AGENTS.md` exists for old opencode; new opencode loads
  `instructions:` from `opencode.json`.
- **Do not** skip `origin=` on `log_*` calls. The MAAT constitution requires
  provenance on every write.

## 7. Failure modes + recovery

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Only `tehuti-core_*` tools, no `maat_memory_*` | stdio config missing/wrong | See §3 |
| `Permission denied (publickey)` on self-ssh | own pubkey not in `authorized_keys` | `cat ~/.ssh/id_ed25519.pub >> ~/.ssh/authorized_keys` |
| `EADDRINUSE` on MCP spawn | orphan daemon holding the port | `ss -ltnp | grep :PORT`, then `kill <pid>` |
| `Cannot execute command-line and remote command` on Windows ssh | `-t` and `RemoteCommand` conflict in config | add `RequestTTY yes` to that Host block |
| Self-ssh hangs | Tailscale down | `tailscale status`, `sudo tailscale up` |
| Locked out after losing key | recovery procedure | See `40-ssh-topology.md` §"Recovery" |

## 8. Pointer for agents

If you are an agent reading this:
1. **First call** `memory_law` (maat_memory MCP) — it returns the
   `agent_bootstrap` open/fetch contract. Treat that as mandatory before opening
   any artifact path.
2. **Then** `memory_get_artifacts(audience="every_lab_agent", slug="opencode/lab-powerup-2026-08-08")`
   to get the latest portable URI.
3. **Then** `memory_fetch_artifact(uri=<portable_uri>)` to read the body if
   the version here is stale.
