#!/bin/bash
# Install and start ALL mcpo services (Python + npx + Docker)

echo "=== Creating systemd services for ALL MCP servers ==="

# Python MCP servers
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
ExecStart=/home/suspect/.local/bin/uvx mcpo --host 127.0.0.1 --port 8011 -- python3 /home/suspect/.n8n/mcp-servers/ImhotepMCP/pythonMCP/imhotep_curriculum_server.py
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
ExecStart=/home/suspect/.local/bin/uvx mcpo --host 127.0.0.1 --port 8012 -- python3 /home/suspect/.n8n/mcp-servers/ImhotepMCP/pythonMCP/imhotep_research_server.py
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
ExecStart=/home/suspect/.local/bin/uvx mcpo --host 127.0.0.1 --port 8013 -- python3 /home/suspect/.n8n/mcp-servers/ImhotepMCP/pythonMCP/imhotep_integration_server.py
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
ExecStart=/home/suspect/.local/bin/uvx mcpo --host 127.0.0.1 --port 8014 -- python3 /home/suspect/.n8n/mcp-servers/ImhotepMCP/pythonMCP/mhotep_server.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# npx-based MCP servers
sudo tee /etc/systemd/system/mcpo-filesystem.service > /dev/null <<EOF
[Unit]
Description=mcpo bridge for filesystem MCP server
After=network.target

[Service]
Type=simple
User=suspect
WorkingDirectory=/home/suspect/.n8n
Environment="PATH=/usr/local/bin:/usr/bin:/bin:/home/suspect/.local/bin"
ExecStart=/home/suspect/.local/bin/uvx mcpo --host 127.0.0.1 --port 8016 -- npx -y @modelcontextprotocol/server-filesystem /home/suspect/.n8n
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo tee /etc/systemd/system/mcpo-postgres.service > /dev/null <<EOF
[Unit]
Description=mcpo bridge for postgres MCP server
After=network.target postgresql.service

[Service]
Type=simple
User=suspect
WorkingDirectory=/home/suspect/.n8n
Environment="PATH=/usr/local/bin:/usr/bin:/bin:/home/suspect/.local/bin"
ExecStart=/home/suspect/.local/bin/uvx mcpo --host 127.0.0.1 --port 8017 -- npx -y @modelcontextprotocol/server-postgres postgresql://suspect:suspect@localhost:5432/jarvis
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo tee /etc/systemd/system/mcpo-memory.service > /dev/null <<EOF
[Unit]
Description=mcpo bridge for memory MCP server
After=network.target

[Service]
Type=simple
User=suspect
WorkingDirectory=/home/suspect/.n8n
Environment="PATH=/usr/local/bin:/usr/bin:/bin:/home/suspect/.local/bin"
ExecStart=/home/suspect/.local/bin/uvx mcpo --host 127.0.0.1 --port 8018 -- npx -y @modelcontextprotocol/server-memory
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Docker-based n8n-mcp (requires Docker)
sudo tee /etc/systemd/system/mcpo-n8n-mcp.service > /dev/null <<EOF
[Unit]
Description=mcpo bridge for n8n-mcp MCP server
After=network.target docker.service

[Service]
Type=simple
User=suspect
WorkingDirectory=/home/suspect/.n8n
Environment="PATH=/usr/local/bin:/usr/bin:/bin:/home/suspect/.local/bin"
ExecStart=/home/suspect/.local/bin/uvx mcpo --host 127.0.0.1 --port 8015 -- docker run -i --rm -e MCP_MODE=stdio -e LOG_LEVEL=error -e DISABLE_CONSOLE_OUTPUT=true ghcr.io/czlonkowski/n8n-mcp:latest
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo ""
echo "=== Reloading systemd ==="
sudo systemctl daemon-reload

echo ""
echo "=== Starting all mcpo services ==="
sudo systemctl enable --now mcpo-tehuti-curriculum.service
sudo systemctl enable --now mcpo-tehuti-research.service
sudo systemctl enable --now mcpo-tehuti-integration.service
sudo systemctl enable --now mcpo-tehuti-core.service
sudo systemctl enable --now mcpo-n8n-mcp.service
sudo systemctl enable --now mcpo-filesystem.service
sudo systemctl enable --now mcpo-postgres.service
sudo systemctl enable --now mcpo-memory.service

echo ""
echo "=== Waiting for services to start ==="
sleep 8

echo ""
echo "=== Checking service status ==="
systemctl status mcpo-* --no-pager | head -60

echo ""
echo "=== Checking ports ==="
ss -ltnp | grep -E '8011|8012|8013|8014|8015|8016|8017|8018'

echo ""
echo "✅ All mcpo services should now be running!"
echo ""
echo "UPDATE YOUR EXTERNAL TOOLS IN OPENWEBUI:"
echo "Settings → External Tools → Add Server"
echo ""
echo "For MCP (Streamable HTTP) type:"
echo "  - http://127.0.0.1:8011 (curriculum)"
echo "  - http://127.0.0.1:8012 (research)"
echo "  - http://127.0.0.1:8013 (integration)"
echo "  - http://127.0.0.1:8014 (core)"
echo "  - http://127.0.0.1:8015 (n8n-mcp)"
echo "  - http://127.0.0.1:8016 (filesystem)"
echo "  - http://127.0.0.1:8017 (postgres)"
echo "  - http://127.0.0.1:8018 (memory)"
echo ""
echo "OR for OpenAPI type (use /openapi.json URLs):"
echo "  - http://127.0.0.1:8011/openapi.json"
echo "  - etc."

