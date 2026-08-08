#!/usr/bin/env bash
# Upgrade system Ollama from ~/.local/ollama-0.20.0 (downloaded from GitHub v0.20.0).
# Run: sudo bash /home/suspect/.n8n/scripts/upgrade-ollama-to-0.20.sh
# Override bundle path: sudo OLLAMA_SRC=/path/to/ollama-0.20.0 bash ...

set -euo pipefail

# Under `sudo`, HOME is /root — use the real user who invoked sudo.
if [[ -n "${SUDO_USER:-}" ]]; then
  REAL_HOME="$(getent passwd "$SUDO_USER" | cut -d: -f6)"
else
  REAL_HOME="$HOME"
fi
SRC="${OLLAMA_SRC:-$REAL_HOME/.local/ollama-0.20.0}"
if [[ ! -x "$SRC/bin/ollama" ]]; then
  echo "Missing $SRC/bin/ollama — download/extract v0.20.0 first."
  exit 1
fi

TS="$(date +%Y%m%d-%H%M%S)"

systemctl stop ollama

if [[ -f /usr/local/bin/ollama ]]; then
  cp -a /usr/local/bin/ollama "/usr/local/bin/ollama.bak.${TS}"
fi
install -m 0755 "$SRC/bin/ollama" /usr/local/bin/ollama

if [[ -d /usr/local/lib/ollama ]]; then
  mv /usr/local/lib/ollama "/usr/local/lib/ollama.bak.${TS}"
fi
cp -a "$SRC/lib/ollama" /usr/local/lib/ollama

systemctl start ollama
sleep 2

echo "---"
/usr/local/bin/ollama --version
systemctl is-active ollama
