# Maat Credentials (T3)

**Broker keys do not sit in the same `.env` every agent can read.**

## Control

| Layer | Path | Who loads |
|-------|------|-----------|
| Agent | `.env.agent` (+ rewritten `.env`) | Agents, coordination |
| Broker | `.env.broker` (mode 0600) | Gateway / Meta-BLR / spend processes with `MAAT_CREDENTIAL_ROLE=broker` |

Absence of `MAAT_CREDENTIAL_ROLE=broker` is not broker access.

## Run tests

```bash
cd /mnt/data_drive/maatlangchain
python3 maat_memory/maat_credentials/test_credentials.py
# → 20/20 controls held
```

## Split a monolithic env

```bash
python3 -c "
from pathlib import Path
from maat_memory.maat_credentials import split_dotenv
print(split_dotenv(Path.home()/'.hermes'/'.env'))
"
```

## Applied on staydangerous

- `/mnt/data_drive/hermes/.env` → `.env.agent` + `.env.broker` (OPENROUTER, Discord, gateway token out of agent path)
- `~/.hermes/.env` → same (+ Meta tokens to broker)
- `hermes-datadrive-gateway.service` loads both files + `MAAT_CREDENTIAL_ROLE=broker`
- Meta-BLR loaders prefer `.env.broker`

Backups: `*.pre-t3-<timestamp>`

## Declared debt (not closed)

- `PGVECTOR_DB_URL` — **broker now**; write mediation on `:8023` stamps origin. Agents use `.env.agent` (no DSN). Live `n8n.service` still loads combined `.env` until sudo updates EnvironmentFile.
- `~/.n8n/.ka-auth` — organ EnvironmentFile only; agents use memory token / mediated path. Same-user file read still possible (broker daemon next).
- Systemd-embedded encryption key — staged to 0600 file; scrub+rotate needs sudo (see `hermes/docs/T3-SYSTEMD-SECRET-SCRUB-HANDOFF.md`)
- Same-user file reads of `.env.broker` — broker daemon / separate uid
- Full broker *daemon* for spend keys — next slice after ka-auth

## Law

Pattern-matching key names is defense-in-depth. The control is **file separation + role**. Putting spend tokens back into `.env` undoes T3.
