# Host Body Awareness — staydangerous

**Date:** 2026-08-03  
**Reporter:** `cursor_staydangerous_n8n` (Tehuti Cursor seat on `.n8n` cockpit)  
**Law:** [`MAAT_STORAGE_ROOTS_v0.1.yaml`](./MAAT_STORAGE_ROOTS_v0.1.yaml)  
**Doctrine:** Root is the cockpit, not the warehouse. Before the fleet debates, the body must know its organs.

---

## 1. Identity

| Field | Value |
|-------|-------|
| Hostname | `staydangerous` |
| Role | Tehuti Lab Ka spine / brain (not a client laptop) |
| LAN | `192.168.4.21` (+ Tailscale `100.77.143.8`) |
| Discovery | `http://192.168.4.21:8010` |
| Seat | Cursor SSH into `/home/suspect/.n8n` |
| CPU | Intel i9-12900K (24 threads) |
| RAM | 125 GiB total (~90 GiB available at report) |
| Kernel | Linux 5.15.0-185-generic |
| Uptime (at report) | ~3 weeks |
| Load (at report) | **~81** — body under heavy load; treat as WARN |

**This workspace is the cockpit on the brain.** Agents here are already *inside* the host. Other drives on the same machine are organs, not “another computer.”

---

## 2. Organs (storage mounts)

| Mount class | Path | Device | Size | Used (report) | Status |
|-------------|------|--------|------|---------------|--------|
| **cockpit** | `/` (+ `/home`) | LVM `ubuntu-vg-myRoots` on nvme1n1 | 1.8T | **~93%** (~134G free) | **WARN → near NO_GO** |
| **live_bulk** | `/mnt/data_drive` | Samsung 980 PRO 1TB (`nvme0n1`) | 916G | ~49% | OK |
| **model_home** | `/mnt/ai_models` | CT2000T500 (`nvme2n1`) | 1.8T | ~12% | OK |
| **backup** | `/mnt/ai_backup` | CT2000T500 (`nvme3n1`) | 1.8T | ~26% | OK |

Also present (not primary law roots): `/mnt/ai_backup` siblings history, `/mnt/t7`, `/mnt/usb_sda1`, `/mnt/imhotep_ai_images` (often empty/root-owned).

---

## 3. Trees and fruits (where weight lives)

### Cockpit fruit (WRONG organ — existing debt)

`/home/suspect` ≈ **800G** on root. Heaviest:

| Path | ~Size | Should be |
|------|------:|-----------|
| `/home/suspect/.ollama` | 218G | model_home |
| `/home/suspect/.n8n` | 237G | cockpit (repos OK) — but see children |
| `/home/suspect/comfyui` | 142G | live_bulk |
| `/home/suspect/.local` | 47G | review |
| `/home/suspect/.cache` | 43G | ephemeral / live_bulk |
| `/home/suspect/models` | 26G | model_home |
| `/home/suspect/.openclaw` | 21G | review |
| `/usr/share/ollama/.ollama/models` | 145G | model_home (2nd blob store on root vol) |

Inside `.n8n` (cockpit workspace):

| Path | ~Size | Class debt |
|------|------:|------------|
| `models/` | 106G | model_home |
| `fine-tuned-models/` | 22G | model_home |
| `.reorg-backup-20251217-222805/` | 21G | backup |
| `.git/` | 20G | cockpit (OK but heavy) |
| `maatlangchain/` | 11G | coordination (OK) |
| `tehuti-lab-webui-venv*` | ~19G | live_bulk / prune |
| `.venvs/` | 7.8G | review |
| `openclaw` + old openclaw | ~8.5G | review |

### live_bulk fruit (`/mnt/data_drive` ≈ 425G)

| Path | ~Size |
|------|------:|
| `unsloth-studio/` | 342G |
| `models/` | 32G |
| `tehuti-lab-webui/` | 14G |
| `tehuti-control-center/` | 6.9G |
| `hermes/` | ~0.9G |
| `ka-education` deploys / related | (under various) |

### model_home fruit (`/mnt/ai_models` ≈ 208G)

| Path | ~Size |
|------|------:|
| `huggingface/` | 207G |
| `ollama/` | tiny (not the live blob home yet) |

### backup fruit (`/mnt/ai_backup` ≈ 437G)

| Path | ~Size |
|------|------:|
| `staydangerous_test/` | 206G |
| `staydangerous1/` | 147G |
| `smokyo_drift/` | 85G |

---

## 4. Living organs (services / ports)

| Organ | Port | Notes |
|-------|------|-------|
| Ka Discovery | `:8010` | body manifest |
| Tehuti Guard | `:8013` | policy |
| Tehuti Core / brain | `:8014` | |
| Maat Memory MCP | `:8022` | gitMaat |
| Write broker | `:8023` | localhost |
| OpenClaw gateway | `:18790` | senses |
| Ollama | `:11434` | 33 tags ≈ 239.5G catalog |
| Maat LLM Router | `:9140` | hub big model; edges small |
| Postgres | `:5432` | maat_memory |
| Ka Education | `:3008` | |
| n8n (legacy listen) | `:5678` | retired doctrine elsewhere |
| Buzz / Control surfaces | `:3000` etc. | |

User systemd units of note: `ka-discovery`, `tehuti-guard`, `mcpo-maat-memory`, `openclaw-gateway`, `maat-llm-router`, `maat-ollama-pin`, `tehuti-ka-education`, Hermes data_drive gateway, Raku TTS/STT, VisionClaw→Hermes bridge.

---

## 5. Limits (hard truth)

1. **Cockpit at ~93%** — soft-full law fires; large writes to `/` or `/home` must **DENY_EVENT / NO_GO**.
2. **Dual Ollama stores on root volume** (~218G home + ~145G `/usr/share`) — primary migration debt.
3. **NVIDIA NVML driver/library mismatch** at report time — GPU tooling unstable until driver/userspace aligned.
4. **Load ~81** — do not start more always-on heavy workers without Head Operator weigh-in.
5. **Fleet join without write gate** would accelerate root death — gate now exists (`write-check`).

---

## 6. Runtime gate (shipped)

```bash
# Organ pressure
python3 ~/.hermes/scripts/maat_memory_plane.py body

# Before a write
python3 ~/.hermes/scripts/maat_memory_plane.py write-check \
  --path /home/suspect/.n8n/models/new.gguf --size-mb 4000 --type model_weight
# → NO_GO (cockpit + model_weight)

python3 ~/.hermes/scripts/maat_memory_plane.py write-check \
  --path /mnt/ai_models/huggingface/new --size-mb 4000 --type model_weight
# → ALLOW (model_home)
```

Code: `maatlangchain/maat_memory/memory_plane/write_preflight.py`  
Law: `docs/MAAT_STORAGE_ROOTS_v0.1.yaml`

---

## 7. Agent loop under this law

```
chore claimed
  → preflight (identity + presence + host_body)
  → write-check(path, size, type)
  → Guard / allow|deny
  → work
  → did + receipt
  → report to Head Operator
```

**Clean line:** Before the fleet debates, the body must know its organs. Before an agent writes, it must know the mount.

---

## 8. Recommended follow-on chores (not done in this report)

1. Migrate `.ollama` / `/usr/share/ollama` blobs → `/mnt/ai_models` (single model_home).
2. Move `.n8n/models` + `fine-tuned-models` → model_home; leave symlinks if needed.
3. Relocate `.reorg-backup-*` → `/mnt/ai_backup`.
4. Relocate or slim `~/comfyui` toward data_drive.
5. Only then: Fleet Pilot / join token scale-up.

---

*Receipt of awareness for Head Operator Imhotep — Truth before autonomy.*
