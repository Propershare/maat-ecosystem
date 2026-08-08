# MaatCode fork strategy

This document describes how **MaatCode** (planned fork of [OpenCode](https://opencode.ai)) relates to upstream OpenCode, what this workspace adds on top of vanilla OpenCode, and how to fork or maintain a long-lived derivative. It also records the **upstream baseline** pinned when the Maat overlay was last applied.

## Goal

**MaatCode** is intended to be an OpenCode-derived (or OpenCode-aligned) coding agent runtime that embeds **Maat governance**: coordination via gitMaat (Maat Memory), policy via TehutiGuard where applicable, and **three-ring** boundaries (canon / scholarship / monetized). This repository keeps **stock OpenCode** as the CLI/runtime and layers **config + instructions + documentation** until a source fork is justified.

## Upstream baseline (pinned)

| Field | Value |
|--------|--------|
| **OpenCode / npm package** | `opencode-ai@1.3.13` |
| **CLI version** (`opencode --version`) | `1.3.13` |
| **Install** | `npm i -g opencode-ai@latest` (see also [Hermes opencode skill](../hermes-agent/skills/autonomous-ai-agents/opencode/SKILL.md)) |
| **Config schema** | `https://opencode.ai/config.json` |

Re-pin this section after each deliberate OpenCode upgrade.

## This repository’s OpenCode delta (changelog)

Changes applied for **OpenCode + Maat overlay** (claw-code-inspired patterns expressed as config and rules, not Python ports):

1. **`autoupdate`**: `"notify"` in both [`opencode.json`](../opencode.json) and [`maatlangchain/opencode.json`](../maatlangchain/opencode.json).
2. **`permission`**: Conservative defaults — `bash`, `task`, `external_directory`, and `webfetch` set to `ask`; workspace file tools (`read`, `edit`, `glob`, `grep`, `list`) `allow`; `todowrite` and `question` `allow`.
3. **`agent.steps`**: Turn budget — `build` agent `80` steps, `plan` agent `40` steps.
4. **`instructions`**: Explicit inclusion of [`.cursor/rules/opencode-maat/RULE.md`](../.cursor/rules/opencode-maat/RULE.md) in workspace root [`opencode.json`](../opencode.json). [`maatlangchain/opencode.json`](../maatlangchain/opencode.json) does not repeat that path: OpenCode merges the parent directory config when you run from `maatlangchain/`, so the Maat rule still loads. If you ever use **only** `maatlangchain/opencode.json` without a parent `opencode.json`, add `../.cursor/rules/opencode-maat/RULE.md` to its `instructions` array.
5. **Maat instruction file**: The opencode-maat rule states that hard gates live in `opencode.json` and forbids loading claw-code JSON snapshots as instructions.
6. **`share`: `"manual"`** — session sharing only when you choose (privacy default).
7. **`watcher.ignore`** — ignores heavy dirs (`node_modules`, `.venv`, `chroma_db*`, caches, etc.) to reduce noise and churn.
8. **`skills.paths`** — adds `hermes-agent/skills` and repo `skills/` so OpenCode can load Hermes-style skill trees ([`maatlangchain/opencode.json`](../maatlangchain/opencode.json) uses `../hermes-agent/skills` and `../skills` when the project root is `maatlangchain/`).
9. **`command`** — built-in prompts: `maat-bootstrap` (plan), `review-change`, `summarize-thread` for structured workflows without claw-code.
10. **Drift check** — [`scripts/check-opencode-ollama-drift.py`](../scripts/check-opencode-ollama-drift.py) compares `ollama list` to `opencode.json` model keys.
11. **MCP `tehuti-core`** — Local stdio server ([`mcp-servers/tehuti-core/tehuti_core_server.py`](../mcp-servers/tehuti-core/tehuti_core_server.py)) registered under `mcp` in [`opencode.json`](../opencode.json) and `~/.config/opencode/opencode.json`. Exposes `query_gitmaat` plus **`log_gitmaat_task` / `log_gitmaat_change` / `log_gitmaat_decision` / `log_gitmaat_learning`** for PostgreSQL Maat Memory. Requires `PGVECTOR_DB_URL` and `python3` with `psycopg2` + `maatlangchain` on `PYTHONPATH` (server adds `maatlangchain` automatically).

Earlier state (pre-overlay): only `instructions` globs, `default_agent`, Ollama `provider`, and `keybinds`.

## Fork procedure (checklist)

When you are ready to maintain **MaatCode** as a separate codebase from upstream OpenCode:

1. **Identify upstream repo** and license — follow OpenCode’s official repository and contribution terms.
2. **Fork** (GitHub/GitLab) or add a **remote** and create a long-lived branch `maat` (or rename default after audit).
3. **Document patches** — keep a `MAAT_PATCHES.md` in the fork listing every intentional deviation from upstream (auth, providers, permissions defaults, branding).
4. **Build and CI** — reproduce upstream build; add CI jobs for your packaging target (npm, binary, etc.).
5. **Binary / package name** — decide whether the CLI remains `opencode` or becomes `maatcode` for installing side-by-side with upstream; update docs and Hermes skills accordingly.
6. **Workspace portability** — keep [`opencode.json`](../opencode.json) (or `maatcode.json` if renamed) schema-compatible where possible so Tehuti Lab configs move between vanilla OpenCode and MaatCode with minimal edits.
7. **Governance hooks** (future) — optional integration points: pre-tool TehutiGuard checks, gitMaat session logging, RAG context injection; specify each as a small plugin or forked module with tests.

## Parity / gap audit (OpenCode native vs Maat desired)

| Capability | OpenCode (this workspace) | Maat desired (future fork or glue) |
|------------|---------------------------|-------------------------------------|
| Tool permission UX | Native `permission` in JSON | Same; possible TehutiGuard veto layer |
| Iteration / turn cap | Native `agent.*.steps` | Tune per agent; optional Maat “task budget” from gitMaat |
| Task source of truth | Instructions + human | gitMaat DB when connected (see workspace rules) |
| Policy enforcement | Ask/allow/deny in config | TehutiGuard for deploy/canonical paths |
| Session / sharing | Upstream defaults + `share` in schema | Decide org policy; document in fork |
| Branding / distribution | `opencode-ai` npm package | MaatCode package/binary when fork ships |

Refresh this table periodically; do not generate it from claw-code tarball snapshots.

## References

- Workspace Cursor rule (mentions this doc): [`.cursor/rules/workspace-tehuti-lab/RULE.md`](../.cursor/rules/workspace-tehuti-lab/RULE.md)
- OpenCode Maat overlay rule: [`.cursor/rules/opencode-maat/RULE.md`](../.cursor/rules/opencode-maat/RULE.md)
- OpenCode docs: [https://opencode.ai](https://opencode.ai)
