# Tehuti Lab (staydangerous) — Agent Instructions

Lab root for multi-organ Maat work. Project-specific rules live in each repo’s `AGENTS.md`.

## Dual ingress (LAW)

| Agent id | Channel | Runtime |
|----------|---------|---------|
| `hermes_whatsapp` | WhatsApp | Hermes `/mnt/data_drive/hermes` |
| `openclaw_telegram` | Telegram | OpenClaw `~/.openclaw` + this `~/.n8n` workspace |

They are **two agents** — separate birth, update, governance. Doc: `/mnt/data_drive/hermes/docs/DUAL-AGENT-GOVERNANCE.md`.

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
Publish packs with `hermes/scripts/maat_evidence_publish.py`. Public receipts: https://maatecosystem.com/evidence/

## Maat
Truth · Balance · Order · Justice · Reciprocity · Accountability

## Tools

### Local notes (migrated from TOOLS.md)

# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.
