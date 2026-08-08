# Tehuti Lab (staydangerous) — Global Agent Doctrine

This file is **synced to every machine** that runs opencode for the lab.
It is loaded on every session, in every directory, regardless of cwd.
Project-specific rules live in each repo's `AGENTS.md` and override where they conflict.

## Dual ingress (LAW)

| Agent id | Channel | Runtime |
|----------|---------|---------|
| `hermes_whatsapp` | WhatsApp | Hermes `/mnt/data_drive/hermes` |
| `openclaw_telegram` | Telegram | OpenClaw `~/.openclaw` + `~/.n8n` workspace |

They are **two agents** — separate birth, update, governance.
Doc: `/mnt/data_drive/hermes/docs/DUAL-AGENT-GOVERNANCE.md`.

OpenClaw must **keep up with Hermes** on Maat lab skills (gitMaat, messaging, governance) via `skills.load.extraDirs` pointing at Hermes skill trees — **do not** merge homes or migrate with `hermes setup`.

## Order of authority
1. **gitMaat** (`maatlangchain/maat_memory`) — query tasks and log changes first
2. **TehutiGuard** — policy before high-impact action
3. **MaatBench** — prove guarantees under stress
4. Project `AGENTS.md` — local conventions

## Spine organs (this host)
- MaatLangChain / Maat Memory — coordination
- Tehuti Guard — allow / review / quarantine / escalate / deny
- OpenClaw (`openclaw_telegram`) — Telegram ingress
- Hermes (`hermes_whatsapp`) — WhatsApp ingress + research skills
- ka-education / maatecosystem.com — public doctrine + receipts

## Evidence
Publish packs with `hermes/scripts/maat_evidence_publish.py`.
Public receipts: https://maatecosystem.com/evidence/

## Maat
Truth · Balance · Order · Justice · Reciprocity · Accountability

## Sync protocol
This file is the **single source of truth** for lab doctrine across machines.
- Source of truth: `git@github.com:<lab>/opencode-rules.git` (or equivalent) — TBD
- Local mirror: `~/.opencode-rules/`
- Re-sync command (on every machine): `opencode-rules pull`
- If a project repo needs a deviation, write it in the project's `AGENTS.md`, not here.
