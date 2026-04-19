# Push safety — keep the lab local and Git clean

**Problem:** A large monorepo + secrets + personal continuity files → easy to `git add .` and push the wrong thing.

**Principles:**

1. **Secrets never in Git** — real `.env`, keys, and host-only JSON live outside the repo or are gitignored.
2. **Personal continuity** — `MEMORY.md`, daily `memory/`, and root `USER.md` / `SOUL.md` are **default-ignored** at the lab root so a public remote does not get your private context. Use committed **`.example`** files as templates.
3. **Review before push** — `git status` and `git diff --cached` every time; avoid blind `git add .` until `.gitignore` is trusted.
4. **Private GitHub** until you have run a clean pass and are comfortable with what would be public.

## What belongs in Git (law)

**Commit** source, contracts, manifests, and reproducible configuration. **Do not commit** local environments, caches, generated artifacts, bulky datasets/models, or machine-local backups unless explicitly designated as versioned deliverables.

**Hygiene vs law:** [`.gitignore`](../.gitignore) answers what Git should stop nagging about day to day. **This section** states what must stay **reviewable and reproducible** in version control for a governed lab. They are not the same: do not use `.gitignore` to hide something that is actually part of the product surface—fix policy or split the artifact instead.

### Where large or local-only artifacts live instead

- **Bulky datasets, full model weights, scratch exports:** keep on host paths outside Git, object storage, or under `data/` only as documented; commit **manifests**, **checksums**, and **small fixtures** when they prove a contract or test.
- **Machine-local backups and tarballs:** default under **`backups/`** at the lab root (gitignored); not the constitutional record unless you intentionally add a **named, reviewed** artifact elsewhere in the tree.

If **`USER.md` / `SOUL.md` / `MEMORY.md` were committed before** adding these rules, stop tracking them without deleting your working copies:

`git rm --cached -- USER.md SOUL.md MEMORY.md 2>/dev/null || true`

Then commit the `.gitignore` change.

## What is gitignored (lab root)

See [`.gitignore`](../.gitignore). Highlights:

- `.env` and common env variants (`.env.local`, etc.); **`.env.example`** stays committable as a template.
- Root **`MEMORY.md`**, **`memory/`**, **`SSH-CREDENTIALS.md`**, **`.webui_secret_key`**, **`.ka-auth`**.
- Root **`USER.md`** and **`SOUL.md`** — copy from **`USER.md.example`** and **`SOUL.md.example`** locally; do not rely on Git for your real identity files if the remote is public.
- Extra venv trees (e.g. `tehuti-lab-webui-venv/`, **`.venvs/`**) and usual Python/OS noise.
- **Caches and tooling noise:** `node_modules/`, `.pnpm-store/`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`, `.ipynb_checkpoints/`, `unsloth_compiled_cache/`, coverage output — see `.gitignore` for the current list.
- **Root `backups/`** — machine-local bundles/snapshots; not a substitute for versioned docs (see *What belongs in Git* above).

Sanitize **[`.env.example`](../.env.example)** so it contains **placeholders only** (no real hosts, passwords, or keys). Example files are committed on purpose; they must not be a copy-paste of production.

## Before you push

```bash
./scripts/git-push-safety-check.sh
```

Exits **non-zero** if **staged** files look dangerous (e.g. `.env`, private key names, ignored paths accidentally forced with `-f`). Run after `git add`, before `git commit` / `git push`.

## If you already committed a secret

1. **Rotate** the secret (API key, password, token) at the provider — removing from Git history does not undo exposure.
2. Use `git filter-repo` or GitHub guidance to purge history if needed; treat the secret as compromised until rotated.

## Relation to Maat

- **gitMaat** can log decisions and audits; it does not replace `.gitignore` or hooks.
- **Tehuti Guard** governs runtime writes; **Git** hygiene is a separate, human + script layer.

## See also

- [`README.md`](../README.md) — repo entry points and governance context (public on GitHub).
- Local operator guidance may also exist in **`AGENTS.md`** at the lab root when present on disk; it is not required to exist in the remote.
