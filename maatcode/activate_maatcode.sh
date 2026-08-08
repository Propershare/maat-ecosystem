#!/bin/bash
# Maat Balance: MaatCode Activation Script
# Purpose: Activate MaatCode API and MCP servers

set -e

WORKSPACE_ROOT="/home/suspect/.n8n"
cd "$WORKSPACE_ROOT/maatcode"

echo "=== Maat Balance: MaatCode Activation ==="
echo ""

# Check if API server is running
echo "1. Checking MaatCode API server status..."
if pgrep -f "api_server.py" > /dev/null; then
    echo "   ✅ API server already running"
    API_RUNNING=true
else
    echo "   ⚠️  API server not running"
    API_RUNNING=false
fi

# Check if MCP server is running
echo ""
echo "2. Checking MaatCode MCP server status..."
if pgrep -f "mcp_server.py" > /dev/null; then
    echo "   ✅ MCP server already running"
    MCP_RUNNING=true
else
    echo "   ⚠️  MCP server not running"
    MCP_RUNNING=false
fi

# Create systemd service files if needed
echo ""
echo "3. Creating systemd service files..."

# API Server service
cat > /tmp/maatcode-api.service << 'EOF'
[Unit]
Description=MaatCode API Server
After=network.target

[Service]
Type=simple
User=suspect
WorkingDirectory=/home/suspect/.n8n/maatcode
Environment="PATH=/home/suspect/.n8n/tehuti-lab-webui-venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/home/suspect/.n8n/tehuti-lab-webui-venv/bin/python3 /home/suspect/.n8n/maatcode/api_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# MCP Server service
cat > /tmp/maatcode-mcp.service << 'EOF'
[Unit]
Description=MaatCode MCP Server
After=network.target

[Service]
Type=simple
User=suspect
WorkingDirectory=/home/suspect/.n8n/maatcode
Environment="PATH=/home/suspect/.n8n/tehuti-lab-webui-venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/home/suspect/.n8n/tehuti-lab-webui-venv/bin/python3 /home/suspect/.n8n/maatcode/mcp_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "   ✅ Service files created in /tmp/"
echo "   💡 To install: sudo cp /tmp/maatcode-*.service /etc/systemd/system/ && sudo systemctl daemon-reload"

# Integration instructions
echo ""
echo "4. Integration Instructions:"
echo ""
echo "   API Server:"
echo "   - Port: 8020 (default)"
echo "   - Endpoint: http://localhost:8020"
echo "   - Tools: /tools/get_tasks, /tools/log_change, etc."
echo ""
echo "   MCP Server:"
echo "   - Protocol: MCP (stdio)"
echo "   - Command: python3 /home/suspect/.n8n/maatcode/mcp_server.py"
echo "   - Tools: get_tasks, log_change, log_decision"
echo ""

# Summary
echo "=== Activation Summary ==="
if [ "$API_RUNNING" = true ] && [ "$MCP_RUNNING" = true ]; then
    echo "✅ MaatCode fully activated"
elif [ "$API_RUNNING" = true ]; then
    echo "⚠️  API server running, MCP server needs activation"
elif [ "$MCP_RUNNING" = true ]; then
    echo "⚠️  MCP server running, API server needs activation"
else
    echo "⚠️  MaatCode needs activation"
    echo "   Start API: python3 api_server.py"
    echo "   Start MCP: python3 mcp_server.py"
fi
echo ""
echo "📋 Next steps:"
echo "   1. Start API/MCP servers if not running"
echo "   2. Integrate with WebUI (add to TOOL_SERVER_CONNECTIONS)"
echo "   3. Test gitMaat integration"
echo ""
echo "=== Maat Balance: MaatCode activation complete ==="

