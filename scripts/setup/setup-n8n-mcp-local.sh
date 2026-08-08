#!/bin/bash
# Setup n8n-mcp from local build (not Docker)

echo "=== Setting up n8n-mcp from local build ==="
echo ""

N8N_MCP_PATH="/home/suspect/.n8n/n8n-mcp"
MCP_INDEX="$N8N_MCP_PATH/dist/mcp/index.js"

# Check if built
if [ ! -f "$MCP_INDEX" ]; then
    echo "Error: n8n-mcp not built. Run:"
    echo "  cd $N8N_MCP_PATH"
    echo "  npm install"
    echo "  npm run build"
    echo "  npm run rebuild"
    exit 1
fi

echo "✓ Found n8n-mcp at: $MCP_INDEX"
echo ""

# Create systemd service
echo "=== Creating systemd service ==="
sudo tee /etc/systemd/system/mcpo-n8n-mcp.service > /dev/null <<EOF
[Unit]
Description=mcpo bridge for n8n-mcp MCP server (local build)
After=network.target

[Service]
Type=simple
User=suspect
WorkingDirectory=/home/suspect/.n8n
Environment="PATH=/usr/local/bin:/usr/bin:/bin:/home/suspect/.nvm/versions/node/v20.19.4/bin"
Environment="NODE_ENV=production"
Environment="MCP_MODE=stdio"
Environment="LOG_LEVEL=error"
Environment="DISABLE_CONSOLE_OUTPUT=true"
Environment="N8N_API_URL=http://127.0.0.1:5678"
ExecStart=/home/suspect/.local/bin/uvx mcpo --host 127.0.0.1 --port 8015 -- node $MCP_INDEX
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "✓ Systemd service created"
echo ""

# Reload systemd
echo "=== Reloading systemd ==="
sudo systemctl daemon-reload
echo "✓ Systemd reloaded"
echo ""

# Start service
echo "=== Starting n8n-mcp service ==="
sudo systemctl enable --now mcpo-n8n-mcp.service
sleep 3

echo ""
echo "=== Checking service status ==="
systemctl status mcpo-n8n-mcp.service --no-pager | head -15

echo ""
echo "=== Checking port 8015 ==="
ss -ltnp | grep 8015

echo ""
echo "=== Testing OpenAPI endpoint ==="
curl -s http://127.0.0.1:8015/openapi.json | python3 -m json.tool | head -20

echo ""
echo "✅ n8n-mcp setup complete!"
echo ""
echo "To test:"
echo "  curl http://127.0.0.1:8015/openapi.json | jq .info.title"

