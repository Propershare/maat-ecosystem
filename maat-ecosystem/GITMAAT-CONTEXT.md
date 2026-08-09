# gitMaat context (all workstations)

**Refreshed from shared gitMaat.** Read this first so you know what other PCs/agents are doing.

## Pending / in-progress tasks

Count: 20
- [pending] ROOT PLAN P4 — move .n8n/models + fine-tuned to model_home (agent: cursor_staydangerous_data_drive)
- [pending] ROOT PLAN P3 — retarget OLLAMA_MODELS to /mnt/ai_models (agent: cursor_staydangerous_data_drive)
- [pending] ROOT PLAN P2 — prune unused Ollama tags on cockpit (agent: cursor_staydangerous_data_drive)
- [pending] ROOT PLAN P1 — move safe .n8n backup debt to /mnt/ai_backup (agent: cursor_staydangerous_data_drive)
- [in_progress] ROOT PLAN P0 — receipts + Write Gate Ask for Evidence (agent: cursor_staydangerous_data_drive)
- [pending] Implement Tehuti Maat Host RPC (protocol handshake + terminals) (agent: cursor_staydangerous_data_drive)
- [in_progress] Gut Traycer → Tehuti Nerve Center (Phase 0–1) (agent: cursor_staydangerous_data_drive)
- [pending] Cut over TCC daily board to modern React shell (agent: cursor_staydangerous_data_drive)
- [pending] Clean imhotepjr join plane (smoke dup + cursor_imhotepjr) (agent: cursor_staydangerous_data_drive)
- [in_progress] Wire Host Body / write-check into TCC pulse + NO_GO (agent: cursor_staydangerous_n8n)
- [pending] Persist TCC join plane: reclaim :8040 or systemd join@8041 + JOIN_PLANE_URL (agent: cursor_staydangerous_n8n)
- [pending] Migrate cockpit storage debt to organ mounts (ollama/models/comfyui/backups) (agent: cursor_staydangerous_n8n)
- [pending] EDGE TEST — connect gemma4 workers to Maat LLM Router :9140 (agent: cursor_staydangerous_data_drive)
- [in_progress] Connect edge PCs to Maat LLM router (agent: cursor_staydangerous_data_drive)
- [pending] SUDO finish after secrets quarantine pass 1 (agent: cursor_staydangerous_data_drive)

## Recent changes (by workstation/agent)

Count: 20
- opencode_staydangerous: /mnt/data_drive/maatlangchain/tests/unit/test_artifact_bank_fetch_routing.py | New regression test file for ArtifactBank.fetch() routing: 1
- opencode_staydangerous: /mnt/data_drive/maatlangchain/maat_memory/memory_plane/artifact_bank.py | Fixed ArtifactBank.fetch() routing: bare slugs (no URL schem
- opencode_staydangerous: /home/suspect/.opencode-rules/refs/maat-audit-agentic-engineering-doctrine.md | Re-audit v2: 21/21 CANON MAX (all pillars STRONG). No outsta
- opencode_staydangerous: /home/suspect/.opencode-rules/refs/agentic-engineering-doctrine.md | Applied 4 v1 remediation items: §7 provenance tables, §11.5 
- opencode_staydangerous: /home/suspect/.opencode-rules/refs/maat-scoring-canon.md | Authored Tehuti Lab Ma'at scoring canon v1 (3 layers, codifi
- opencode_staydangerous: /home/suspect/.opencode-rules/refs/maat-audit-agentic-engineering-doctrine.md | Ma'at audit of the doctrine against 7-pillar lab canon (7902
- opencode_staydangerous: /home/suspect/.opencode-rules/refs/agentic-engineering-doctrine.md | Authored Tehuti Lab canonization of the agentic engineering 
- opencode_staydangerous: /home/suspect/.opencode-rules/refs/horthy-2026-08-08.html | Saved the Horthy breakdown HTML (29495 bytes) as a ref artif
- opencode_staydangerous: /home/suspect/.config/opencode/opencode.json | Added ~/.opencode-rules/30-lab-powerup.md to the instruction
- opencode_staydangerous: /home/suspect/.opencode-rules/30-lab-powerup.md | Canonical cross-machine reference for opencode lab power-up 
- opencode_staydangerous_data_drive_3764637: /home/suspect/.opencode-rules/sshd/99-tehuti-lab.conf | New file: sshd hardening drop-in (password off, root off, X1
- opencode_staydangerous_data_drive_3764637: /home/suspect/.opencode-rules/40-ssh-topology.md | New file: lab inventory, trust model, file sharing, onboardi
- opencode_staydangerous_data_drive_3764637: /home/suspect/.ssh/authorized_keys | Appended staydangerous@tehuti-lab-2026-08-08 ed25519 pubkey 
- opencode_staydangerous_data_drive_3764637: /home/suspect/.ssh/config | Wrote ~/.ssh/config with Host aliases for staydangerous + de
- opencode_staydangerous_data_drive_3764637: /home/suspect/.ssh/id_ed25519 | Generated staydangerous ed25519 keypair (no passphrase, comm

## Learnings

- When fixing a routing bug in fetch()/resolve()/dispatch()-style functions, the r
- ArtifactBank.fetch() in memory_plane/artifact_bank.py had a routing bug: bare sl
- The Tehuti Lab Ma'at scoring canon is 3 layers, by purpose: (1) Runtime 4-key st
- When canonizing an external framework: (a) preserve the raw source as refs/<sour
- The Tehuti Lab constitutional canon is 7 pillars (Truth, Balance, Order, Justice

## Decisions

- 1. Authored refs/maat-scoring-canon-2026-08-08 (3-layer canon: runtime 4-key sta
- 1. Preserve the raw synthesis source as refs/horthy-2026-08-08 (not canon). 2. A
- Treat the doc as a reference artifact, not a TODO. Promote to object store so an
- Publish a single canonical reference artifact (slug opencode/lab-powerup-2026-08
- Use Tailscale for identity/auth (already deployed, psnpropershare tailnet) and p

---
*To refresh: run `python maatlangchain/scripts/query_gitmaat.py --out GITMAAT-CONTEXT.md` from workspace root.*