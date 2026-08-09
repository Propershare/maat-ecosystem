# Workspace Inventory & Bill of Materials — Tehuti Lab (2026-08-08)

**Slug:** `refs/workspace-inventory-bom-2026-08-08`
**Type:** Inventory + bill of materials + Ma'at audit
**Audience:** `every_lab_agent`
**Author:** opencode_staydangerous (operator-collaborated)
**Provenance:** Direct filesystem inspection; not synthesized

---

## 0. Executive summary

**Two physical volumes** mounted under `/home/suspect/.n8n` and `/mnt/data_drive`. They share **one specific directory** (`maatlangchain/`) via the same LVM volume. The rest of the inventory is genuinely split.

| Volume | Mount | Size | Used | Available | Use% |
|--------|-------|------|------|-----------|------|
| `ubuntu--vg-myRoots` | `/home` (and `/mnt/data_drive/maatlangchain`) | 1.8 TB | 1.5 TB | 234 GB | **87%** |
| `nvme0n1` | `/mnt/data_drive` (most of it) | 916 GB | 428 GB | 442 GB | 50% |

**Critical findings:**
1. `/home/suspect/.n8n` is at **87% full** — within weeks of running out of space.
2. `maatlangchain/` is **duplicated** across both volumes via the same physical files (same inode).
3. `/home/suspect/.n8n/staydangerous/` is a **157 GB snapshot of `~/`** sitting inside the lab workspace — including FiveM game server data, FXServer resources, personal files.
4. **`models/` appears on both volumes** (113 GB on ubuntu--vg-myRoots, 34 GB on nvme0n1) — both are Ollama model stores; probably not the same models.
5. **41 root-level `.md` files** in `~/.n8n/` and most are *not* git-tracked — they're personal notes, debug logs, setup docs that have no home.
6. **Empty directories**: 22+ at depth ≤3 in `~/.n8n`, 10+ in `/mnt/data_drive` — most are git bookkeeping (`/branches`, `/.git/branches`, `node_modules/.vite-temp`).

## 1. Inventory — `~/.n8n/` (ubuntu--vg-myRoots)

**Total: ~1.5 TB across 167 top-level entries** (excluding hidden files).

### Top 15 by size

| Path | Bytes | Files | Type | Last mod |
|------|-------|-------|------|----------|
| `staydangerous/` | 157 GB | 139,448 | personal snapshot of `~/` | 2026-08-03 |
| `models/` | 113 GB | 90 | Ollama model store | 2025-12-28 |
| `fine-tuned-models/` | 22 GB | 82 | GGUF/safetensors | 2025-12-27 |
| `maatlangchain/` | 11 GB | 2,236 | **lab core (duplicated)** | 2026-08-08 |
| `tehuti-lab-webui-venv/` | 10 GB | 87,595 | Python venv | 2026-01-02 |
| `tehuti-lab-webui-venv.backup.20260102_202352/` | 9.4 GB | 76,998 | venv backup | 2026-01-02 |
| `data/` | 6.1 GB | 1,401 | lab data (retrieval_packs, tehuti) | 2026-08-08 |
| `Legal_AI_FL/` | 5.4 GB | 35,827 | **embedded git repo (operator-protected)** | 2026-07-28 |
| `openclaw/` | 4.6 GB | 152,719 | **embedded git repo** | 2026-08-03 |
| `backups/` | 3.5 GB | 59,928 | old backups | 2026-04-19 |
| `openclaw-integration/` | 2.3 GB | 129,619 | **embedded git repo** | 2026-04-17 |
| `maat-runtime/` | 1.1 GB | 68,255 | **embedded git repo** | 2026-07-23 |
| `vendor/` | 855 MB | 4,986 | llama-cpp checkout | 2026-05-07 |
| `enwiki-latest-pages-articles.xml.bz2` | 676 MB | 1 | orphan Wikipedia dump | 2026-04-09 |
| `hermes-agent/` | 614 MB | 16,632 | **embedded git repo** | 2026-04-14 |

### Smaller notable entries

| Path | Size | What it is |
|------|------|-----------|
| `comfyui-output/` | 591 MB | ComfyUI image generation outputs |
| `ka-education-backend/` | 304 MB | educational organ |
| `gemma4-toolshim/` | 303 MB | custom model tooling |
| `maatbench.rar` | 297 MB | archive — status unknown |
| `maat-ecosystem/` | 262 MB | **lab core (NOT a duplicate)** |
| `n8n/` | — | n8n workflow engine data |
| `open-webui/data` | 8 B (empty) | root-owned, blocks git operations |
| `.git/` | — | the outer repo (only on `cursor/fix-join-review-decide-66e9` and `opencode-rules` branches) |

### Embedded git repos (`d8a6636` + `opencode-rules` history)

These have their own `.git/` and their own work-in-progress. They are tracked only by path-name in the outer `.n8n` repo's history; the inner `.git/` is itself gitignored.

- `Legal_AI_FL/`, `Legal_AI_FL.tmp/` — legal AI (operator-protected, never touch)
- `openclaw/`, `openclaw-integration/`, `openclaw-backup/` — Telegram ingress
- `hermes-agent/`, `maat-runtime/`, `agent-skills/`, `maatcode/`
- `vendor/llama-cpp/`, `self-hosted-ai-starter-kit/`, `langgraph-agent-demo/`
- `ollama-nuggets/`, `weknora-analysis/`, `legal-ecosystem/`

### Files at root (41 `.md` + others)

The doctrine's `~/.opencode-rules/30-lab-powerup.md` is the canonical reference. Many of these root `.md` files overlap or duplicate content. Categories (best-effort classification):

| Category | Files | Notes |
|----------|-------|-------|
| Identity / doctrine | AGENTS.md, IDENTITY.md, MANIFEST.md, SOUL.md, CONSTITUTION.md, POLICY.md, HEARTBEAT.md, EVENTS.md, LEARNING.md, PORTABILITY.md | some duplicates of canonical docs |
| Operational runbooks | SSH-CREDENTIALS.md, GATEWAYS.md, GITMAAT-*.md, OPENCLAW-*.md, OPENCODE-*.md, SYSTEM_ARCHITECTURE.md, README-502-FIX.md, TEHUTI-LAB-WEBUI-MOVED.md, RBG_LIBRARY_INTEGRATION.md, MAAT_ORCHESTRATION_MANIFEST.md, TEHUTI_GUARD_2.0.md | overlap with project-level docs |
| Setup / debug records | CLAWDBOT-*.md, CLAUDE-*.md, CLAWD-*.md, CRITICAL-DEBUG-STEPS.md, DEBUG-TOOL-RESULTS.md, FINAL-DEBUG-CHECK.md, QUICK-DEBUG-CHECK.md, DREAMS.md, AK47_SMOKINGV2_ISSUE.md, BETTER_DISCORD_UI_IDEAS.md, PRD_Draft_Maat_Legal_Runtime.md, CANON_PROTECTION_COMPLETE.md | one-off session logs that probably shouldn't be root-level |
| Templates | tehuti-lab-ollama-template.md, tehuti-lab-system-prompt.md | lab-asset templates |
| Project root README | README.md | should exist |

**41 .md files at repo root is a doctrine violation.** Each should either be moved into the project it documents or deleted. The doctrine calls for **structure enforced by tooling**, not "loose notes everywhere".

### Empty directories (22+)

Most are git internals (`.git/branches/`, `node_modules/.git/branches/`) or empty placeholder dirs (`open-webui/data/` root-owned, blocks git operations). All should be in `.gitignore` so they don't get re-detected.

## 2. Inventory — `/mnt/data_drive/` (nvme0n1, mostly)

**Total: ~570 GB across 56 top-level entries**.

### Top 20 by size

| Path | Bytes | Files | Type |
|------|-------|-------|------|
| `unsloth-studio/` | 366 GB | 135,079 | model training studio (embedded-git) |
| `models/` | 34 GB | 7 | Ollama models |
| `tehuti-lab-webui/` | 13 GB | 154,812 | lab webui (embedded-git) |
| `maatlangchain/` | 11 GB | 2,236 | **DUPLICATE of `~/.n8n/maatlangchain`** (same inode, same LVM volume) |
| `autoresearch/` | 7.3 GB | 24,482 | (embedded-git) |
| `tehuti-control-center/` | 7.1 GB | 96,031 | (embedded-git) |
| `Tehutidata.db/` | 5.8 GB | 573 | data dir |
| `OpenMAIC/` | 3.7 GB | 154,331 | (embedded-git) |
| `backups/` | 3.5 GB | 3,681 | backups |
| `llama.cpp/` | 2.2 GB | 141,616 | (embedded-git) |
| `paperclip/` | 1.7 GB | 62,343 | (embedded-git) |
| `hermes/` | 1.5 GB | 24,569 | Hermes runtime (NOT a git repo) |
| `traycer/` | 1.4 GB | 141,053 | (embedded-git) |
| `Hood_Memes/` | 1.2 GB | 46,347 | old project, last mod 2025-03 (17 months stale) |
| `Maat-runtime/` | 1.1 GB | 67,455 | **note cap-case vs `~/.n8n/maat-runtime`** (lowercase) |
| `video-studio/` | 748 MB | 18,020 | |
| `cmux/` | 668 MB | 4,366 | (embedded-git) |
| `solana/` | 612 MB | 2,213 | (embedded-git, last mod 2025-03 — stale) |
| `traycer-releases/` | 330 MB | 3 | only 3 files; possibly a tarball location |
| `Tehuti-Dataset/` | 270 MB | 1,176 | |
| `ka-education/`, `space-agent/`, `voicebox-src/`, `maat-ecosystem/` | <130 MB each | smaller organs |

### Stale entries (last modified >6 months ago)

| Path | Last mod | Note |
|------|----------|------|
| `Hood_Memes/` | 2025-03-17 | 17 months old; possibly abandoned |
| `solana/` | 2025-03-15 | 17 months old; abandoned? |

These should be reviewed for archival. The doctrine's Balance pillar says don't optimize non-bottlenecks; an abandoned repo IS a non-bottleneck.

## 3. Duplications

| Resource | `/home/suspect/.n8n/` | `/mnt/data_drive/` | Status |
|----------|----------------------|--------------------|--------|
| `maatlangchain/` | 11 GB | 11 GB | **Same files** (same inode, same LVM volume). Path-only duplication. |
| `models/` (Ollama) | 113 GB | 34 GB | Different volumes; probably different models |
| `maat-runtime/` vs `Maat-runtime/` | 1.1 GB (lowercase) | 1.1 GB (capitalized) | Different filesystems; possibly different versions |
| `maat-ecosystem/` | 262 MB | 53 MB | Different filesystems; maat-ecosystem outer is mostly outer-repo docs, mnt/maat-ecosystem is the embedded organ |

## 4. Empty directories (sample)

| Path | Why empty | Action |
|------|-----------|--------|
| `~/.n8n/.vscode/` | uninitialized | add to .gitignore |
| `~/.n8n/open-webui/data/` | root-owned, blocks git checkout | `sudo rmdir` |
| `~/.n8n/.git/branches/` | git bookkeeping | never tracked, no action |
| `~/.n8n/tehuti-lab-webui-venv.backup.20260102_202352/include/python3.12` | empty header dir | ok |
| `~/.n8n/openclaw/node_modules/@protobufjs` etc. | npm hoist directories | ok, npm-managed |
| `/mnt/data_drive/cmux/ghostty/` | uninitialized | review |
| `/mnt/data_drive/ka-education/types/`, `ka-education/docs/` | uninitialized | review |
| `/mnt/data_drive/backups/openclaw-untracked-20260803T111702Z/skills` | empty backup dir | review |

## 5. Disk pressure analysis

`ubuntu--vg-myRoots` is **87% full** (1.5 TB used of 1.8 TB). At current growth rates, full in weeks. **Biggest reclaimable**:

| Path | Size | Reclaim? | Risk |
|------|------|----------|------|
| `tehuti-lab-webui-venv.backup.20260102_202352/` | 9.4 GB | YES if not needed | low — it's a venv backup from January |
| `staydangerous/` | 157 GB | **MOSTLY YES** but careful | high — contains `~/` snapshot with FXServer, RAG data, etc. |
| `fine-tuned-models/` | 22 GB | NO | model weights, .gitignore'd |
| `models/` | 113 GB | NO | Ollama models in use |
| `backups/` | 3.5 GB | review contents | depends on what's archived |

**Quick win: `tehuti-lab-webui-venv.backup.20260102_202352/` = 9.4 GB**. If a working venv exists, the backup is likely redundant. Deletable today, low risk.

## 6. Bill of materials (BOM)

A `Bill of Materials` for the lab includes: physical volumes, embedded repos, models, datasets, services. Listing here:

### Physical infrastructure

| Item | Location | Size | Purpose |
|------|----------|------|---------|
| LVM `ubuntu--vg-myRoots` | `/home` + `/mnt/data_drive/maatlangchain` | 1.8 TB | primary lab volume, 87% full |
| NVMe `nvme0n1` | `/mnt/data_drive` | 916 GB | secondary volume, 50% full |
| Tailscale overlay | `100.77.143.8` (staydangerous), `100.116.101.98` (desktop-ccitn8l, offline) | n/a | cross-machine fabric |

### Software (embedded git repos)

| Repo | Path | Size | Status |
|------|------|------|--------|
| maatlangchain | `~/.n8n/maatlangchain` AND `/mnt/data_drive/maatlangchain` | 11 GB | tracked on cursor/fix-join-review-decide-66e9 |
| maat-ecosystem | `~/.n8n/maat-ecosystem` AND `/mnt/data_drive/maat-ecosystem` (different filesystems) | 262 MB + 53 MB | tracked on origin/main |
| Legal_AI_FL | `~/.n8n/Legal_AI_FL/` | 5.4 GB | **operator-protected, never touch** |
| openclaw / openclaw-integration / openclaw-backup | `~/.n8n/openclaw*` | 4.6 GB + 2.3 GB + 93 MB | embedded |
| hermes / hermes-agent | `/mnt/data_drive/hermes` + `~/.n8n/hermes-agent` | 1.5 GB + 614 MB | Hermes/WhatsApp ingress |
| maat-runtime / Maat-runtime | `~/.n8n/maat-runtime` + `/mnt/data_drive/Maat-runtime` | 1.1 GB each | case mismatch, possibly duplicates |
| paperclip | `/mnt/data_drive/paperclip` | 1.7 GB | embedded |
| ka-education / ka-education-backend | both volumes | 124 MB + 304 MB | embedded |
| + 15 more smaller embedded repos | scattered | <500 MB each | various |

### Models

| Item | Path | Size | Status |
|------|------|------|--------|
| Ollama models | `~/.n8n/models/` | 113 GB | in use, do not delete |
| Ollama models | `/mnt/data_drive/models/` | 34 GB | in use, do not delete |
| Fine-tuned models | `~/.n8n/fine-tuned-models/` | 22 GB | .gitignored, do not move to git |

### Datasets (working)

| Item | Path | Size | Status |
|------|------|------|--------|
| Lab retrieval packs | `~/.n8n/data/retrieval_packs/` | part of 6.1 GB | working data |
| Tehuti corpus | `~/.n8n/data/tehuti/` | part of 6.1 GB | working data |
| RBG Library | `~/.n8n/maatlangchain/docs/RBG_Library/` | ~9 GB | gitignored, reference |
| Tehuti-Dataset | `/mnt/data_drive/Tehuti-Dataset/` | 270 MB | working |

### Services (currently running)

| Service | Port | Where | Purpose |
|---------|------|-------|---------|
| sshd | 22 | local | remote access |
| ollama | 11434 | local | LLM serving |
| n8n | (TBD) | local | workflow engine |
| Postgres | 5432 | local | maat_memory + others |
| Redis | 6379 | local | cache |
| webui (law-rag) | 8024 | local | lab webui |
| Hermes / OpenClaw | various | various | messaging ingress |
| STT server (whisper) | 8766 | local | voice |
| TTS server | 8767 | local | voice |
| maat-memory MCP | 8022 (mcpo) | local | MCP server |

## 7. Ma'at audit on workspace hygiene

Scored against the canonical 7-pillar rubric (`refs/maat-scoring-canon-2026-08-08`).

| Pillar | Score | Note |
|--------|-------|------|
| Truth (Khet) | 1 (WEAK) | Duplicate `maatlangchain/` via two paths is technically the same files but presented as two locations — confusing. 41 root `.md` files include one-off debug notes masquerading as canon. |
| Balance (Maat) | 2 (PASS) | Volume allocation between the two workspaces is fine; the 87% fill on `ubuntu--vg-myRoots` is the actual imbalance. |
| Order (Nfr) | 1 (WEAK) | 41 root `.md` files violate the principle of structure-enforced-by-tooling. Embedded repos lack consistent namespacing (lowercase `maat-runtime` vs `Maat-runtime`). |
| Justice (Sia) | 1 (WEAK) | No audit trail for what gets deleted/archived. Personal snapshot of `~/` (`staydangerous/`) is mixed with lab code — hard to reason about who owns what. |
| Reciprocity | 2 (PASS) | Two physical volumes and a Tailscale overlay give the lab a recovery story (cross-machine, cross-volume). |
| Accountability | 1 (WEAK) | No inventory script in the repo; this artifact exists but isn't reproducible from CI. |
| Self-Reflection (Heka) | 2 (PASS) | This audit exists. The doctrine's §11.5 cadence exists (operator runs grep weekly). |

**Total: 10/21 — REJECT** (threshold for ADOPT is ≥ 12 with no pillar = 0).

Remediation backlog (must complete before next re-audit):

1. **Move or delete `~/.n8n/staydangerous/`** (157 GB). It is a snapshot of `~/` inside the lab repo. Either move to a non-repo location, or split into lab-doctrine files (move to `~/.opencode-rules/`) and personal data (move to `~/`).
2. ~~**Delete `tehuti-lab-webui-venv.backup.20260102_202352/`** (9.4 GB)~~ — **RESOLVED 2026-08-08.** Operator ran `sudo rm -rf`. 8 GB reclaimed (234→242 GB free); working venv intact.
3. **Move `open-webui/data/` root-owned empty dir** (sudo rmdir).
4. **Categorize and relocate the 41 root `.md` files.** Move project-level docs into their projects (e.g. `GITMAAT-OPENCODE-STARTUP.md` → `maatlangchain/`); delete one-off debug logs.
5. **Decide on the `maat-runtime` (lowercase) vs `Maat-runtime` (capitalized) duplication.** Either consolidate to one path, or document which is the live one.
6. **Add an inventory script** (the one in `/tmp/workspace-inventory.sh` here) to a reproducible location, e.g. `maatlangchain/scripts/workspace_inventory.py`.
7. **Decide on stale entries**: `Hood_Memes/` (17 months old), `solana/` (17 months old) — review for archival.
8. ~~**Investigate `maatlangchain/api/main*.py` redundancy**~~ — **RESOLVED 2026-08-08.** Investigation revealed the naming was reversed: `main_original.py` was the live code (imported by 7+ files via `from api.main import app, get_rag_instance, get_vector_store`), `main_backup.py` and `main_backup_rag.py` were old snapshots, and `main.py` was a 6-line shim. Resolution: `main_original.py` → `main.py` (canonical), shim + old backups deleted. Verified: imports resolve; 15/15 unit tests pass. Commit `587be65`.

## 8. Recommendations (in priority order)

**Do today** (low risk, high reclaim):

1. `git rm` the `tehuti-lab-webui-venv.backup.20260102_202352/` directory — it's a January backup, the working venv exists. **9.4 GB freed.**

**Do this week** (medium risk, structured cleanup):

2. Move the 41 root `.md` files into project directories. Delete debug-log ones. **Estimated: 4 hours; 0 bytes freed but huge clarity gain.**
3. Move `~/.n8n/staydangerous/` to a non-repo location. **Up to 157 GB freed** (depends on what overlaps with `~/`).

**Do this month** (requires operator decisions):

4. Resolve `maat-runtime` (lowercase) vs `Maat-runtime` (capitalized). Pick one canonical path.
5. Decide on `Hood_Memes/` and `solana/` (17 months stale). Archive or delete.
6. Address root-owned empty dirs (`open-webui/data/`).
7. **Move `models/` (113 GB) off the 87%-full volume.** Ollama models can live on `/mnt/data_drive/` (50% full) by symlink or by re-pointing `OLLAMA_MODELS` env var. **113 GB freed from `ubuntu--vg-myRoots`.**

**Deferred** (lower priority):

8. Inventory script in version control (`maatlangchain/scripts/workspace_inventory.py`).
9. Schedule weekly inventory diffs to detect drift.
10. Resync the 234 GB free space with `ubuntu--vg-myRoots` or repurpose the volume.

## 9. Reproducibility

This inventory was generated by:

```bash
# See /tmp/workspace-inventory.sh for the script
/tmp/workspace-inventory.sh /home/suspect/.n8n > /tmp/inventory-n8n.tsv
/tmp/workspace-inventory.sh /mnt/data_drive > /tmp/inventory-mnt.tsv

# Inspect duplicates
for d in maatlangchain models maat-ecosystem; do
  stat -c '%i %n' /home/suspect/.n8n/$d /mnt/data_drive/$d 2>/dev/null
done

# Empty dirs
find /home/suspect/.n8n -maxdepth 3 -type d -empty
find /mnt/data_drive -maxdepth 3 -type d -empty
```

For weekly regen: add a cron entry that runs the script and diffs against the previous week's output.

## 10. Related artifacts

- `refs/agentic-engineering-doctrine-2026-08-08` — the doctrine requiring this hygiene audit
- `refs/slop-grep-report-2026-08-08` — code slop baseline (companion to this hygiene audit)
- `~/.opencode-rules/40-ssh-topology.md` — cross-machine topology context
- `/tmp/workspace-inventory.sh` — reproducible inventory script
- `/tmp/inventory-n8n.tsv`, `/tmp/inventory-mnt.tsv` — raw inventory data
