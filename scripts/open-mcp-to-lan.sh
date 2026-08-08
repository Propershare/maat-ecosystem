#!/usr/bin/env bash
# Run on the SERVER with: sudo bash open-mcp-to-lan.sh
# Opens MCP ports 8011-8021 to the LAN so Clawd (and other workstations) can connect.
# Does NOT change mcpo bind address; see CLAWD-MCP-ACCESS.md for binding to 0.0.0.0.

set -e
LAN_CIDR="${LAN_CIDR:-192.168.4.0/24}"

echo "=== Opening MCP ports to LAN (Clawd) ==="
echo "LAN: $LAN_CIDR"
echo "Ports: 8011-8021 (Tehuti, n8n MCP, ComfyUI Intelligent, etc.)"
echo ""

if command -v ufw >/dev/null 2>&1 && ufw status 2>/dev/null | grep -q "Status: active"; then
    ufw allow from "$LAN_CIDR" to any port 8011:8021 proto tcp comment "MCP for Clawd"
    echo "UFW: allowed 8011-8021/tcp from $LAN_CIDR"
else
    echo "UFW not active; ensure your firewall allows 8011-8021 from $LAN_CIDR"
fi

echo ""
echo "Next: bind mcpo to 0.0.0.0 so Clawd can connect (see CLAWD-MCP-ACCESS.md)."
