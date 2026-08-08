#!/usr/bin/env bash
# Run on the SERVER with: sudo bash expose-mcp-bind-lan.sh
# Creates systemd drop-in overrides so mcpo MCP services bind to 0.0.0.0 (LAN)
# instead of 127.0.0.1, so Clawd (and other PCs) can connect.
#
# Only touches services that exist under /etc/systemd/system. If you have
# mcpo-comfyui-intelligent (8019) or others elsewhere, create overrides manually
# using the same pattern (see CLAWD-MCP-ACCESS.md).

set -e
SVC="mcpo-tehuti-core-fixed"
OVERRIDE_DIR="/etc/systemd/system/${SVC}.service.d"
OVERRIDE_CONF="${OVERRIDE_DIR}/override.conf"

echo "=== Expose MCP to LAN (bind 0.0.0.0) ==="
echo "Creating override for: $SVC (port 8014)"
echo ""

if [ ! -f "/etc/systemd/system/${SVC}.service" ]; then
    echo "Service ${SVC}.service not found in /etc/systemd/system."
    echo "Copy it from $(dirname "$0")/../systemd-services/ and install, or create overrides manually."
    exit 1
fi

mkdir -p "$OVERRIDE_DIR"
# Replace --host 127.0.0.1 with --host 0.0.0.0 in ExecStart
cat > "$OVERRIDE_CONF" << 'OVERRIDE'
[Service]
ExecStart=
ExecStart=/home/suspect/.local/bin/uvx mcpo --host 0.0.0.0 --port 8014 -- python3 /home/suspect/.n8n/mcp-servers/tehuti-core/tehuti_core_server.py
OVERRIDE

echo "Wrote $OVERRIDE_CONF"
systemctl daemon-reload
systemctl restart "${SVC}.service"
echo "Restarted $SVC"
echo ""
echo "For other MCPs (ComfyUI 8019, n8n 8015, etc.): create the same override"
echo "with the correct --port and command. See CLAWD-MCP-ACCESS.md."
echo "Then run: sudo bash open-mcp-to-lan.sh  # open firewall 8011-8021"
