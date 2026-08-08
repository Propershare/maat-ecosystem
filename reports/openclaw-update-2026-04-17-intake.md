# OpenClaw Update Intake - 2026-04-17

## Production Fingerprint

- Repo path: `/home/suspect/.n8n/openclaw`
- Remote: `https://github.com/openclaw/openclaw.git`
- Branch: `main`
- HEAD: `718dba8cb69201e3163a62a3542a9777e4df0538`
- Upstream relation: `main...origin/main [behind 20605]`
- Rollback checkpoint timestamp: `2026-04-17T15:21:25+00:00`

## Runtime Config Metadata (redacted source)

- Config path: `~/.openclaw/openclaw.json`
- `meta.lastTouchedVersion`: `2026.4.14`
- `meta.lastTouchedAt`: `2026-04-15T12:07:24.260Z`
- `wizard.lastRunVersion`: `2026.4.2`
- `wizard.lastRunAt`: `2026-04-14T21:08:22.525Z`
- `agents.defaults.workspace`: `/home/suspect/.n8n`
- `agents.defaults.model.primary`: `ollama/gemma4:e4b`

## Baseline Risk Notes

- Production tree has significant local drift (modified/deleted/untracked files).
- Direct pull/update in production tree is high-risk.
- Runtime and source versions are not aligned to a clean upstream baseline.

## Recovery Artifacts

- Sanitized config backup: `/home/suspect/.n8n/backups/openclaw-config-sanitized-2026-04-17.json`
- (Pending in this SOP) Production diff patch backup + integration-lane promotion bundle.
