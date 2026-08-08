#!/bin/bash
# Diagnose and fix OpenWebUI tool connection errors

DB="/home/suspect/.n8n/open-webui/data/webui.db"

echo "=== OpenWebUI Tool Configuration Diagnostic ==="
echo ""

echo "1. Checking all tools in database:"
sqlite3 "$DB" "SELECT id, name, json_extract(content, '$.url') as url FROM tool ORDER BY id;" | column -t -s '|'
echo ""

echo "2. Checking for tools pointing to port 8000 (old config):"
sqlite3 "$DB" "SELECT id, name FROM tool WHERE content LIKE '%8000%';" || echo "  ✓ None found (good!)"
echo ""

echo "3. Checking mcpo services status:"
systemctl status mcpo-postgres.service --no-pager | grep -E "Active:|Main PID:" | head -2
echo ""

echo "4. Checking if port 8017 is listening:"
ss -ltnp | grep 8017 || echo "  ✗ Port 8017 not listening!"
echo ""

echo "5. Testing postgres OpenAPI endpoint:"
curl -s http://127.0.0.1:8017/openapi.json | python3 -m json.tool | head -5 || echo "  ✗ Cannot reach OpenAPI endpoint!"
echo ""

echo "=== Recommendations ==="
echo ""
echo "If postgres-tools shows port 8017 but OpenWebUI still tries 8000:"
echo "  1. Restart OpenWebUI: sudo systemctl restart open-webui"
echo "  2. Clear browser cache or hard refresh (Ctrl+Shift+R)"
echo "  3. Check if any models reference old tool IDs"
echo ""
echo "If port 8017 is not listening:"
echo "  1. Start mcpo-postgres: sudo systemctl start mcpo-postgres.service"
echo "  2. Check logs: sudo journalctl -u mcpo-postgres.service -n 20"
echo ""

