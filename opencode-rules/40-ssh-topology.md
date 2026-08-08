# SSH Topology & File Sharing — Tehuti Lab

**Status (this machine: `staydangerous`, 2026-08-08):**
- Tailscale: `Running`, tailnet `psnpropershare@`
- This box: `staydangerous` / `100.77.143.8` / online
- Peer: `desktop-ccitn8l` / `100.116.101.98` / Windows / **offline (last seen 9h)**

## Lab inventory

| Host | Tailscale IP | OS | User | Key alias | Status |
|------|--------------|----|------|-----------|--------|
| staydangerous | 100.77.143.8 | linux (Ubuntu 22) | suspect | `~/.ssh/id_ed25519` (this box) | online |
| desktop-ccitn8l | 100.116.101.98 | Windows 11 | suspect | TBD — generate on the box | offline |

**Add a row per peer as you onboard.** Keep the key alias column honest — it's the public half's filename on that machine.

## Trust model

1. **Tailscale handles identity.** SSH is gated to the tailnet's `100.64.0.0/10`; nothing in the lab is internet-facing.
2. **One ed25519 keypair per machine.** No shared "deploy key". Lost a key? Regenerate on that box, push the new pub half to every peer's `~/.ssh/authorized_keys`.
3. **No password auth, ever.** Drop-in: `/etc/ssh/sshd_config.d/99-tehuti-lab.conf` (in this dir's `sshd/`).
4. **No root ssh.** Period.

## File sharing

**Decision (per user, 2026-08-08):** keep per-machine dirs, sync via `opencode-rules pull`. No NFS, no Syncthing.

| What | Where | How |
|------|-------|-----|
| Lab doctrine (this dir) | `~/.opencode-rules/` | Git or rsync, scripted via `opencode-rules pull` |
| SSH config | `~/.ssh/config` | Hand-edit per machine; identical entries after onboarding a peer |
| sshd drop-in | `/etc/ssh/sshd_config.d/99-tehuti-lab.conf` | `sudo cp sshd/99-tehuti-lab.conf /etc/ssh/sshd_config.d/` + `sudo systemctl reload ssh` |
| MAAT memory (Postgres) | `localhost:5432/maat_memory` | Per-machine; not shared. Each agent writes its own agent_id. |

## Onboarding a new box

```bash
# 1. Install Tailscale, log in to the same tailnet
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up

# 2. Generate the box's keypair (no passphrase for unattended sync)
ssh-keygen -t ed25519 -a 100 -C "$(hostname)@tehuti-lab-$(date +%F)" -f ~/.ssh/id_ed25519 -N ""

# 3. Install the hardened sshd drop-in
sudo cp ~/.opencode-rules/sshd/99-tehuti-lab.conf /etc/ssh/sshd_config.d/
sudo cp ~/.opencode-rules/sshd/tehuti-lab-banner /etc/ssh/
sudo sshd -t && sudo systemctl reload ssh

# 4. Append this box's pub key to the PEER's authorized_keys (manual, one-time per peer pair)
#    From this box:
cat ~/.ssh/id_ed25519.pub
#    Paste into the peer's ~/.ssh/authorized_keys on a single new line.

# 5. Sync the opencode rules
git clone <lab-rules-repo> ~/.opencode-rules   # or rsync / curl|tar

# 6. Add a Host entry to ~/.ssh/config and a row to the inventory above.
```

## Recovery — locked out

If you lose your key (or the only trusted key leaves the box):

```bash
# On the LOCKED-OUT box, with console access:
sudo systemctl stop ssh
sudo cp ~/.opencode-rules/sshd/99-tehuti-lab.conf /etc/ssh/sshd_config.d/
sudo sshd -t
sudo systemctl start ssh

# Then add your fresh key from another box:
# 1. ssh-keygen -t ed25519 -C "recovery@$(date +%F)" -f ~/.ssh/id_ed25519_recovery -N "<passphrase>"
# 2. cat ~/.ssh/id_ed25519_recovery.pub | ssh suspect@<locked-out-box> 'cat >> ~/.ssh/authorized_keys'
```

If you can't console in, take the box offline and use a live USB. Do NOT re-enable password auth as a shortcut.
