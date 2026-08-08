#!/usr/bin/env bash
# Apply longer request timeout and keep_alive for Ollama (e.g. 20B on CPU).
# Run once with: sudo bash /home/suspect/.n8n/scripts/ollama-increase-timeout.sh

set -e
OVERRIDE="/etc/systemd/system/ollama.service.d/override.conf"
mkdir -p "$(dirname "$OVERRIDE")"
cat > "$OVERRIDE" << 'EOF'
[Service]
Environment="OLLAMA_HOST=0.0.0.0"
Environment="OLLAMA_CONTEXT_LENGTH=64000"
# Allow long-running completions (20B on CPU can exceed 5 min)
Environment="OLLAMA_REQUEST_TIMEOUT=900"
# Keep model loaded 24h to avoid slow cold starts
Environment="OLLAMA_KEEP_ALIVE=24h"
EOF
systemctl daemon-reload
systemctl restart ollama.service
echo "Ollama override applied and service restarted."
