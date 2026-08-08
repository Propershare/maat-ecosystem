#!/bin/bash
# Install and start all mcpo services

echo "=== Installing mcpo systemd services ==="

sudo cp /tmp/mcpo-tehuti-curriculum.service /etc/systemd/system/ 2>/dev/null || echo "Curriculum service file not found in /tmp"
sudo cp /tmp/mcpo-tehuti-research.service /etc/systemd/system/ 2>/dev/null || echo "Research service file not found in /tmp"
sudo cp /tmp/mcpo-tehuti-integration.service /etc/systemd/system/ 2>/dev/null || echo "Integration service file not found in /tmp"
sudo cp /tmp/mcpo-tehuti-core.service /etc/systemd/system/ 2>/dev/null || echo "Core service file not found in /tmp"

# If files aren't in /tmp, create them
if [ ! -f /tmp/mcpo-tehuti-curriculum.service ]; then
    echo "Creating service files..."
    sudo tee /etc/systemd/system/mcpo-tehuti-curriculum.service > /dev/null <<EOF
[Unit]
Description=mcpo bridge for tehuti-curriculum MCP server
After=network.target

[Service]
Type=simple
User=suspect
WorkingDirectory=/home/suspect/.n8n
Environment="PATH=/usr/local/bin:/usr/bin:/bin:/home/suspect/.local/bin"
Environment="PYTHONPATH=/home/suspect/.n8n/mcp-servers/ImhotepMCP/pythonMCP"
ExecStart=/home/suspect/.local/bin/uvx mcpo --host 0.0.0.0 --port 8011 -- python3 /home/suspect/.n8n/mcp-servers/ImhotepMCP/pythonMCP/imhotep_curriculum_server.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    sudo tee /etc/systemd/system/mcpo-tehuti-research.service > /dev/null <<EOF
[Unit]
Description=mcpo bridge for tehuti-research MCP server
After=network.target

[Service]
Type=simple
User=suspect
WorkingDirectory=/home/suspect/.n8n
Environment="PATH=/usr/local/bin:/usr/bin:/bin:/home/suspect/.local/bin"
Environment="PYTHONPATH=/home/suspect/.n8n/mcp-servers/ImhotepMCP/pythonMCP"
ExecStart=/home/suspect/.local/bin/uvx mcpo --host 0.0.0.0 --port 8012 -- python3 /home/suspect/.n8n/mcp-servers/ImhotepMCP/pythonMCP/imhotep_research_server.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    sudo tee /etc/systemd/system/mcpo-tehuti-integration.service > /dev/null <<EOF
[Unit]
Description=mcpo bridge for tehuti-integration MCP server
After=network.target

[Service]
Type=simple
User=suspect
WorkingDirectory=/home/suspect/.n8n
Environment="PATH=/usr/local/bin:/usr/bin:/bin:/home/suspect/.local/bin"
Environment="PYTHONPATH=/home/suspect/.n8n/mcp-servers/ImhotepMCP/pythonMCP"
ExecStart=/home/suspect/.local/bin/uvx mcpo --host 0.0.0.0 --port 8013 -- python3 /home/suspect/.n8n/mcp-servers/ImhotepMCP/pythonMCP/imhotep_integration_server.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    sudo tee /etc/systemd/system/mcpo-tehuti-core.service > /dev/null <<EOF
[Unit]
Description=mcpo bridge for tehuti-core MCP server
After=network.target

[Service]
Type=simple
User=suspect
WorkingDirectory=/home/suspect/.n8n
Environment="PATH=/usr/local/bin:/usr/bin:/bin:/home/suspect/.local/bin"
Environment="PYTHONPATH=/home/suspect/.n8n/mcp-servers/ImhotepMCP/pythonMCP"
ExecStart=/home/suspect/.local/bin/uvx mcpo --host 0.0.0.0 --port 8014 -- python3 /home/suspect/.n8n/mcp-servers/ImhotepMCP/pythonMCP/mhotep_server.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
fi

echo ""
echo "=== Reloading systemd ==="
sudo systemctl daemon-reload

echo ""
echo "=== Starting mcpo services ==="
sudo systemctl enable --now mcpo-tehuti-curriculum.service
sudo systemctl enable --now mcpo-tehuti-research.service
sudo systemctl enable --now mcpo-tehuti-integration.service
sudo systemctl enable --now mcpo-tehuti-core.service

echo ""
echo "=== Waiting for services to start ==="
sleep 5

echo ""
echo "=== Checking service status ==="
systemctl status mcpo-tehuti-* --no-pager | head -40

echo ""
echo "=== Checking ports ==="
ss -ltnp | grep -E '8011|8012|8013|8014'

echo ""
echo "✅ mcpo services should now be running!"
echo ""
echo "NOW UPDATE YOUR EXTERNAL TOOLS IN OPENWEBUI:"
echo "1. Go to Settings → External Tools"
echo "2. Delete the old entries pointing to port 8000"
echo "3. Add new entries:"
echo "   - Type: MCP (Streamable HTTP)"
echo "   - URL: http://127.0.0.1:8011 (for curriculum)"
echo "   - URL: http://127.0.0.1:8012 (for research)"
echo "   - URL: http://127.0.0.1:8013 (for integration)"
echo "   - URL: http://127.0.0.1:8014 (for core)"
echo ""
echo "OR if you want OpenAPI (mcpo also exposes OpenAPI):"
echo "   - Type: OpenAPI"
echo "   - URL: http://127.0.0.1:8011/openapi.json (for curriculum)"
echo "   - etc."

