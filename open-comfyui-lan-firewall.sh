#!/bin/bash
# Open UFW for ComfyUI (8188) and joenorton comfyui-mcp-server HTTP (9000) on the LAN.
# Run on the machine that hosts ComfyUI: bash /home/suspect/.n8n/open-comfyui-lan-firewall.sh

set -e

echo "=== UFW: allow ComfyUI + MCP (LAN) ==="
echo ""

if ! command -v ufw >/dev/null 2>&1; then
    echo "ufw not found. Install with: sudo apt install ufw"
    exit 1
fi

echo "Current status:"
sudo ufw status verbose | head -15 || true
echo ""

echo "Adding rules (idempotent if already present)..."
sudo ufw allow 8188/tcp comment 'ComfyUI web UI'
sudo ufw allow 9000/tcp comment 'comfyui-mcp-server streamable-http'

echo ""
echo "Reloading..."
sudo ufw reload

echo ""
echo "Rules (filtered):"
sudo ufw status numbered | grep -E 'Status|8188|9000' || sudo ufw status

echo ""
echo "Done. From another device: http://<this-host-ip>:8188/ and MCP http://<this-host-ip>:9000/mcp"
echo ""
echo "To restrict to LAN only later (example), remove these rules and use:"
echo "  sudo ufw allow from 192.168.0.0/16 to any port 8188 proto tcp comment 'ComfyUI LAN-only'"
echo "  sudo ufw allow from 192.168.0.0/16 to any port 9000 proto tcp comment 'MCP LAN-only'"
