# OpenCode Rules — sync source

This dir is the **single source of truth** for global opencode rules across
every machine that runs opencode for the Tehuti Lab.

Files (loaded in lexical order by opencode's `instructions:` field):

| File | Purpose |
|------|---------|
| `00-lab-doctrine.md` | Dual-agent law, order of authority, spine organs, evidence publishing |
| `10-agent-protocol.md` | Standard agents, MAAT memory, constitutional compliance |
| `20-mcp-bootstrap.md` | MCP stdio vs HTTP lessons (live doc) |

## Sync mechanism (TBD)

Edit `opencode-rules-sync.sh` and uncomment the option that fits:

- **Option A** — `git clone` from a private repo (recommended)
- **Option B** — `rsync` from a peer (LAN)
- **Option C** — HTTPS tarball (read-only)

## Bootstrap on a new machine

```bash
# 1. Sync the rules
opencode-rules pull

# 2. Append the instructions block to opencode.json (or merge if it already exists)
python3 - <<'PY'
import json, pathlib
p = pathlib.Path.home() / ".config/opencode/opencode.json"
d = json.loads(p.read_text()) if p.exists() else {}
d.setdefault("$schema", "https://opencode.ai/config.json")
instr = [
    "/home/suspect/.opencode-rules/00-lab-doctrine.md",
    "/home/suspect/.opencode-rules/10-agent-protocol.md",
    "/home/suspect/.opencode-rules/20-mcp-bootstrap.md",
]
existing = set(d.get("instructions", []))
d["instructions"] = [x for x in instr if x not in existing] + [x for x in d.get("instructions", []) if x not in instr]
p.write_text(json.dumps(d, indent=2))
print("opencode.json updated")
PY

# 3. Replace the global fallback AGENTS.md with the pointer
cat > ~/.config/opencode/AGENTS.md <<'EOF'
# Global OpenCode Agent Instructions
> Source of truth: ~/.opencode-rules/
> If you can read this, you should also be loading:
> - ~/.opencode-rules/00-lab-doctrine.md
> - ~/.opencode-rules/10-agent-protocol.md
> - ~/.opencode-rules/20-mcp-bootstrap.md
EOF

# 4. Restart opencode
```
