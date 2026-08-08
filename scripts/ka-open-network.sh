#!/bin/bash
# Ka Architecture — Open all organs to the network
# Run with: sudo bash /home/suspect/.n8n/scripts/ka-open-network.sh
#
# This script:
# 1. Rebinds all MCPs from 127.0.0.1 → 0.0.0.0
# 2. Adds API key auth to every endpoint
# 3. Creates maat-memory service (port 8022)
# 4. Creates ka-discovery service (port 8010)
# 5. Opens firewall ports

set -e

# Broker-only key load — never from agent-facing .ka-auth (quarantined).
# Do not print key material (full or partial).
API_KEY=$(grep -E '^(MCPO_API_KEY|KA_API_KEY)=' /home/suspect/.n8n/.env.broker | head -1 | cut -d= -f2-)
if [ -z "$API_KEY" ]; then
    echo "❌ No API key in ~/.n8n/.env.broker (organs only). .ka-auth is quarantined."
    exit 1
fi

echo "🪶 Ka Architecture — Opening the body to the network"
echo "   API key loaded from .env.broker (length ${#API_KEY}; value not printed)"
echo ""

# === Override existing services to bind 0.0.0.0 + add auth ===

declare -A OVERRIDES=(
    ["mcpo-n8n-mcp"]="/home/suspect/.local/bin/uvx --with 'mcp==1.9.4' mcpo --host 0.0.0.0 --port 8015 --api-key $API_KEY --strict-auth -- node /home/suspect/.n8n/n8n-mcp/dist/mcp/index.js"
    ["mcpo-filesystem"]="/home/suspect/.local/bin/uvx --with 'mcp==1.9.4' mcpo --host 0.0.0.0 --port 8016 --api-key $API_KEY --strict-auth -- npx -y @modelcontextprotocol/server-filesystem /home/suspect/.n8n"
    ["mcpo-postgres"]="/home/suspect/.local/bin/uvx --with 'mcp==1.9.4' mcpo --host 0.0.0.0 --port 8017 --api-key $API_KEY --strict-auth -- npx -y @modelcontextprotocol/server-postgres postgresql://suspect:suspect@localhost:5432/jarvis"
    ["mcpo-memory"]="/home/suspect/.local/bin/uvx --with 'mcp==1.9.4' mcpo --host 0.0.0.0 --port 8018 --api-key $API_KEY --strict-auth -- npx -y @modelcontextprotocol/server-memory"
    ["mcpo-comfyui-intelligent"]="/home/suspect/.local/bin/uvx --with 'mcp==1.9.4' mcpo --host 0.0.0.0 --port 8019 --api-key $API_KEY --strict-auth -- /home/suspect/comfyui/comfyui-mcp-intelligent/scripts/run_mcp_server.sh"
    ["mcpo-tehuti-core"]="/home/suspect/.local/bin/uvx --with 'mcp==1.9.4' mcpo --host 0.0.0.0 --port 8014 --api-key $API_KEY --strict-auth -- python3 /home/suspect/.n8n/mcp-servers/tehuti-core/tehuti_core_server.py"
)

for svc in "${!OVERRIDES[@]}"; do
    echo "📦 Override: $svc"
    mkdir -p /etc/systemd/system/${svc}.service.d
    cat > /etc/systemd/system/${svc}.service.d/ka-network.conf << CONF
[Service]
ExecStart=
ExecStart=${OVERRIDES[$svc]}
CONF
done

# === Create Maat Memory MCP service (port 8022) ===

echo "📦 New service: mcpo-maat-memory (port 8022)"
cat > /etc/systemd/system/mcpo-maat-memory.service << EOF
[Unit]
Description=Maat Memory MCP Server — Ka Architecture Memory Organ
After=network.target postgresql.service

[Service]
Type=simple
User=suspect
Group=suspect
WorkingDirectory=/home/suspect/.n8n/mcp-servers/maat-memory
Environment=PGVECTOR_DB_URL=postgresql://suspect:disdick@localhost:5432/maat_memory
ExecStart=/home/suspect/.local/bin/uvx --with 'mcp==1.9.4' mcpo --host 0.0.0.0 --port 8022 --api-key $API_KEY --strict-auth -- python3 /home/suspect/.n8n/mcp-servers/maat-memory/maat_memory_server.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# === Create Ka Discovery service (port 8010) ===

echo "📦 New service: ka-discovery (port 8010)"
cat > /etc/systemd/system/ka-discovery.service << EOF
[Unit]
Description=Ka Architecture Discovery — Body manifest over HTTP
After=network.target

[Service]
Type=simple
User=suspect
Group=suspect
WorkingDirectory=/home/suspect/.n8n/mcp-servers
ExecStart=/usr/bin/python3 /home/suspect/.n8n/mcp-servers/ka-discovery/ka_discovery_server.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# === Reload and restart everything ===

echo ""
echo "🔄 Reloading systemd..."
systemctl daemon-reload

echo "🔄 Restarting MCP services..."
for svc in mcpo-tehuti-core mcpo-n8n-mcp mcpo-filesystem mcpo-postgres mcpo-memory mcpo-comfyui-intelligent; do
    systemctl restart $svc.service 2>/dev/null && echo "  ✅ $svc" || echo "  ⚠️  $svc (may not exist)"
done

echo "🆕 Starting new services..."
systemctl enable --now mcpo-maat-memory.service 2>/dev/null && echo "  ✅ mcpo-maat-memory" || echo "  ⚠️  mcpo-maat-memory"
systemctl enable --now ka-discovery.service 2>/dev/null && echo "  ✅ ka-discovery" || echo "  ⚠️  ka-discovery"

# === Open firewall ports ===

echo ""
echo "🔥 Opening firewall ports..."
if command -v ufw &>/dev/null; then
    for port in 8010 8014 8015 8016 8017 8018 8019 8020 8022; do
        ufw allow $port/tcp comment "Ka Architecture organ" 2>/dev/null
    done
    ufw reload 2>/dev/null
    echo "  ✅ UFW rules added"
else
    echo "  ⚠️  No UFW found — ports may already be open or use iptables"
fi

echo ""
echo "═══════════════════════════════════════════════"
echo "🪶 Ka Architecture — Body is OPEN"
echo "═══════════════════════════════════════════════"
echo ""
echo "Discovery:  http://$(hostname):8010/manifest"
echo "API Key:    ${API_KEY:0:8}...${API_KEY: -8}  (full key NOT printed — use ~/.n8n/.env.broker)"
echo ""
echo "Agents connect with header:"
echo "  Authorization: Bearer <KA_API_KEY from ~/.n8n/.env.broker>"
echo ""
echo "Or discover the full body:"
echo "  curl http://$(hostname):8010/manifest"
echo "═══════════════════════════════════════════════"
