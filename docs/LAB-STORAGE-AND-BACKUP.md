# Lab storage, local memory, and backup

**Purpose:** Make **physical disk cost** visible, tie it to **what “local memory” means** in this lab (Postgres/gitMaat, corpora, models, venvs), and document **best practices + backup** so new machines and agents don’t silently fill disks.

**Audience:** Operators on Imhotep’s server and any laptop that mounts the same workflow.

---

## 1. What “local memory” costs (categories)

| Category | Typical location | Role | Grows when… |
|----------|------------------|------|-------------|
| **gitMaat / Postgres** | Server: Postgres data dir (not in repo). Clients: **no** local DB files — only **`PGVECTOR_DB_URL`**. | Tasks, sessions, governance rows, vectors if you store them in PG | Tasks, embeddings in `maat_memory`, retention not pruned |
| **Tehuti text corpus** | `data/tehuti/ukmt-rbg-dataset/` | UKMT/RBG + KA2 files | Adding snapshots |
| **Tehuti PDF pack** | `data/tehuti/pdf-library/` (~5.5 GB class) | Scholarship / RAG source | One-time or re-extract |
| **Archives** | `data/tehuti/archives/` | Provenance zips | New USB drops |
| **Vector DB (non-PG)** | e.g. `chroma_db_maat/`, project-specific dirs | RAG experiments | Re-ingest, new collections |
| **Ollama models** | Usually `~/.ollama/models` (not under repo) | Local inference | Every `ollama pull` |
| **Python venvs** | `.venv/`, `tehuti-lab-webui-venv/`, etc. | Dependencies | New stacks, duplicate venvs |
| **Node / build** | `openclaw/node_modules`, etc. | Gateway build | `pnpm install` / upgrades |
| **Fine-tunes / checkpoints** | `fine-tuned-models/`, `training/` | ML artifacts | Training runs |
| **Logs / sessions** | `~/.openclaw`, `logs/`, app-specific | Runtime | Left unrotated |

**Rule of thumb:** **Coordination memory** (gitMaat) is **small compared to models + PDF corpora + venvs** — but **Postgres** still needs **capacity planning** and **backup**, not just “it’s on the server.”

---

## 2. Measuring usage (test + document)

### Automated snapshot (repo paths)

From the lab root:

```bash
./scripts/lab-storage-audit.sh
```

- **`FULL=1`** — also measures `data/tehuti/pdf-library/` and `openclaw/node_modules` (can be **slow**).
- **`SHOW_PG_DATA=1`** — also `du` on `/var/lib/postgresql` when present (can be **slow**).
- **`DISK_WARN_PCT=90`** — override default **85** for the SUMMARY `action:` line.

Optional:

```bash
LAB_ROOT=/path/to/.n8n ./scripts/lab-storage-audit.sh
```

The script prints **per-path sizes** for major trees, **`df`** for filesystem use, and notes **Ollama** / **Postgres** if tools are available. It ends with a **`=== SUMMARY (paste / gitMaat / memory) ===`** block: **machine**, **date**, **sum of measured paths (hot total)**, **metric_note** (logical DB size vs PGDATA on disk), **values_note** (see below), **top 5 paths** (labels distinguish **pg_database_size** vs **du** on PGDATA), **`postgres_db_logical:`** (pretty size or **`unavailable`**), **`postgres_pgdata_disk:`** (**`skipped`** unless **`SHOW_PG_DATA=1`**, then human **`du`** or **`unavailable`**), **filesystem use %**, and an **action** line (warn if use ≥ **`DISK_WARN_PCT`**, default **85**). Re-run after big changes (new model, new corpus, RAG ingest).

**`skipped` vs `unavailable` in pasted SUMMARYs:** **`skipped`** = that measurement was **not requested** (e.g. default run without **`SHOW_PG_DATA=1`**). **`unavailable`** = it was **requested or applicable** but the value **was not obtained** (missing **`psql`**, bad URL, timeout, missing directory, **`du`** failure).

**Durable snapshots:** Append that SUMMARY block to `memory/YYYY-MM-DD.md`, gitMaat `log_learning`, or a ticket — terminal-only output rots; **dated + machine + path summary** is what you can compare next quarter.

**`FULL=1`** and **`SHOW_PG_DATA=1`** stay optional and can be slow; the default run stays **fast enough for routine checks**.

### Postgres logical size (same DB gitMaat uses)

If `psql` can connect with `PGVECTOR_DB_URL`:

```bash
set -a && source .env && set +a
psql "$PGVECTOR_DB_URL" -c "SELECT pg_size_pretty(pg_database_size(current_database())) AS db_size;"
```

Document the output in your operator log or a dated note in `memory/` (not secrets).

### Why document it

- **Other machines** need to know **what to sync** vs **what to generate locally** (models, venvs).
- **Agents** should not assume “infinite disk”; large writes (RAG, exports) belong behind **Guard** and **retention** policy ([`MAAT-GOVERNANCE-RETENTION.md`](MAAT-GOVERNANCE-RETENTION.md)).

---

## 3. Best practices (local memory at what cost?)

1. **Single Postgres for gitMaat** — one URL for all workstations ([`GITMAAT-CONNECT.md`](GITMAAT-CONNECT.md)); avoid N duplicate `maat_memory` DBs on every laptop unless you have a **sync story**.
2. **Keep corpora out of Git** when huge — `.gitignore` already excludes large trees (see [`PUSH-SAFETY.md`](PUSH-SAFETY.md) / [`data/tehuti/README.txt`](../data/tehuti/README.txt)); **transfer via USB/rsync**, not commits.
3. **Models on GPU host** — pull Ollama models **where they run**; laptops can use **remote** Ollama or smaller quants; document **which host** holds which tags.
4. **One venv per role** where possible — duplicate `tehuti-lab-webui-venv`-style trees multiply disk; prefer **one** maintained env per major app.
5. **Prune** — old `logs/`, `__pycache__`, abandoned `chroma_*` experiments; **governance retention** for PG ([`MAAT-GOVERNANCE-RETENTION.md`](MAAT-GOVERNANCE-RETENTION.md)).
6. **gitMaat for tasks, not for blobs** — store **pointers** (paths, hashes, URLs) in tasks/learnings; store **multi‑GB** data on disk/object store, not in DB BLOBs by default.

---

## 4. Backup plan (tiers)

| Tier | What | How often | Notes |
|------|------|-----------|--------|
| **A — Postgres** | `maat_memory` (and related DBs) | Daily / weekly logical dumps | `pg_dump` / your existing backup; **test restore** yearly |
| **B — Lab config** | `.env` (host-only copy), `~/.openclaw/openclaw.json`, systemd units | On change | Secrets **not** in Git; encrypted backup or password manager |
| **C — Repo** | Git remotes | Every push | Doctrine + code; **not** large data |
| **D — Large data** | `data/tehuti/pdf-library/`, `models/`, `fine-tuned-models/` | Weekly/monthly | `rsync` to NAS/second disk; Tehuti layout: [`data/tehuti/README.txt`](../data/tehuti/README.txt) |
| **E — Cold archive** | USB / `archives/` provenance | Per snapshot | Keep **one** canonical zip story to avoid silent duplicates |

**Restore drill (real, not ceremonial):** At least once per major backup change: restore **Postgres** to a scratch instance and verify `maat_memory` queries; restore **config** to a test host and run [`scripts/lab-runtime-check.sh`](../scripts/lab-runtime-check.sh). Then run [`scripts/lab-storage-audit.sh`](../scripts/lab-storage-audit.sh) and confirm the **SUMMARY** block matches expectations. If you only ever *measure* and never *restore*, you do not have a backup — you have a hope.

---

## 5. Cross-machine “build list” (gitMaat)

Durable **work queues** for new laptops belong in **gitMaat** (tasks in Postgres), not only in this repo’s markdown. When a machine **connects** with valid **`PGVECTOR_DB_URL`**, agents run **`get_tasks`** / update status — see [`KA2-RESEARCH-AGENT-AND-GITMAAT-PROGRESS.md`](KA2-RESEARCH-AGENT-AND-GITMAAT-PROGRESS.md) and [`.cursorrules`](../.cursorrules).

Optional operator tasks to seed:

- Run `lab-storage-audit.sh` and record sizes.
- Confirm `df` headroom on **Ollama host** and **Postgres host**.
- Align backup tier A + B for that machine.

---

## See also

- [`GITMAAT-CONNECT.md`](GITMAAT-CONNECT.md) — DB URL, LAN vs localhost.
- [`RUNTIME-HOOKUP.md`](RUNTIME-HOOKUP.md) — spine check.
- [`ROOT-INVENTORY.md`](ROOT-INVENTORY.md) — top-level folders.
- [`LAB-CANONICAL-TREE-AND-STACK.md`](LAB-CANONICAL-TREE-AND-STACK.md) — disk vs runtime.
