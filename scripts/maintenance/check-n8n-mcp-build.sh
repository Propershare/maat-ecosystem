#!/bin/bash
# Check n8n-mcp build status

echo "=== n8n-mcp Build Status ==="
echo ""

cd /home/suspect/.n8n/n8n-mcp 2>/dev/null || {
    echo "❌ n8n-mcp directory not found"
    exit 1
}

# Check installation
if [ -d "node_modules" ]; then
    echo "✅ npm install: Complete"
else
    echo "⏳ npm install: In progress..."
fi

# Check build
if [ -f "dist/mcp/index.js" ]; then
    echo "✅ npm run build: Complete"
    echo "   File: dist/mcp/index.js"
    ls -lh dist/mcp/index.js
else
    echo "⏳ npm run build: In progress or not started..."
    if [ -d "dist" ]; then
        echo "   dist/ directory exists but index.js not found"
        ls -la dist/ 2>/dev/null | head -5
    fi
fi

# Check rebuild
if [ -f "data/nodes.db" ] || [ -d "data" ]; then
    echo "✅ npm run rebuild: Complete (database exists)"
else
    echo "⏳ npm run rebuild: In progress or not started..."
fi

echo ""
echo "=== Next Steps ==="
if [ -f "dist/mcp/index.js" ]; then
    echo "✅ Build complete! You can now:"
    echo "   1. Run: /home/suspect/.n8n/setup-n8n-mcp-local.sh"
    echo "   2. Or manually setup systemd service"
else
    echo "⏳ Wait for build to complete, then run this script again"
fi

