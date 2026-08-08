# Maat Memory Write Mediation (T1 integrity)

**The thing that mints trust does not live in the process that could be compromised.**

Agents must not hold `PGVECTOR_DB_URL`. A DSN holder can `INSERT ... content_origin='human_authored'` on poisoned text — every CHECK green, quarantine bypassed.

## Control

| Layer | Who | Holds DSN? | Stamps origin? |
|-------|-----|------------|----------------|
| Agent | Cursor / Hermes workers | No | No — token only |
| Write service `:8023` | `maat-memory-write.service` | Yes | Yes — from token → Principal |
| MCP organ `:8022` | `mcpo-maat-memory` | Yes | Yes — MediatedWriter (agent kind) |

Client-supplied `content_origin` / `origin` → **HTTP 400** / `ProvenanceError`.
Even a matching claim is refused — the client is not the mint.

## Tests

```bash
cd /mnt/data_drive/maatlangchain
python3 maat_memory/test_write_mediation.py   # 20/20
```

## Agent config

```bash
# .env.agent
MAAT_MEMORY_WRITE_URL=http://127.0.0.1:8023
MAAT_MEMORY_AGENT_TOKEN=<issued>
MAAT_MEMORY_MEDIATED=1
# no PGVECTOR_DB_URL
```

## Issue a token (broker host)

```python
from pathlib import Path
from maat_memory.write_mediation import TokenRegistry, PrincipalKind
reg = TokenRegistry.load(Path.home()/'.maat/credentials/memory-agent-tokens.json')
print(reg.issue('cursor_other_host', kind=PrincipalKind.AGENT))
```

## Proven on staydangerous

- `POST /v1/decisions` with `content_origin=human_authored` → 400
- Honest write → DB row `content_origin=agent_authored`
- `PGVECTOR_DB_URL` reclassified **broker** (T3 credentials)
- `~/.n8n/.env.agent` has no DSN; `.env.broker` holds it
- Live `n8n.service` still reads combined `.env` until sudo updates EnvironmentFile (see `docs/T3-SYSTEMD-SECRET-SCRUB-HANDOFF.md`)

## Honest remaining gap

- MCP `:8022` still trusts client-supplied `agent` string for Principal (spoofable attribution until MCP auth tokens)
- Same-user can still read `.env.broker` / token registry files on disk
- `.ka-auth` impersonation still open
- Systemd-embedded encryption key staged for scrub; needs sudo + later rotate
