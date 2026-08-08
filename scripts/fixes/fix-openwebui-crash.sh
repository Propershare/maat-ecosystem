#!/bin/bash
# Fix OpenWebUI crash loop by checking and fixing common issues

echo "=== Diagnosing OpenWebUI Crash ==="
echo ""

# Check if OpenWebUI is running
if systemctl is-active --quiet open-webui.service; then
    echo "✓ OpenWebUI is running"
else
    echo "✗ OpenWebUI is not running"
    echo ""
    echo "Checking recent logs..."
    journalctl -u open-webui.service -n 20 --no-pager | tail -10
    echo ""
fi

# Check database
echo "Checking database..."
if [ -f /home/suspect/.n8n/open-webui/data/webui.db ]; then
    echo "✓ Database exists"
    DB_SIZE=$(stat -c%s /home/suspect/.n8n/open-webui/data/webui.db)
    echo "  Size: $DB_SIZE bytes"
    
    # Check integrity
    INTEGRITY=$(sqlite3 /home/suspect/.n8n/open-webui/data/webui.db "PRAGMA integrity_check;" | head -1)
    if [ "$INTEGRITY" = "ok" ]; then
        echo "✓ Database integrity: OK"
    else
        echo "✗ Database integrity: FAILED"
        echo "  $INTEGRITY"
    fi
else
    echo "✗ Database not found!"
fi

echo ""
echo "Checking tool configurations..."
TOOL_COUNT=$(sqlite3 /home/suspect/.n8n/open-webui/data/webui.db "SELECT COUNT(*) FROM tool;" 2>/dev/null)
echo "  Tools in database: $TOOL_COUNT"

echo ""
echo "Checking permissions..."
if [ -d /home/suspect/.n8n/open-webui/data/vector_db ]; then
    VECTOR_OWNER=$(stat -c '%U:%G' /home/suspect/.n8n/open-webui/data/vector_db)
    if [ "$VECTOR_OWNER" = "suspect:suspect" ]; then
        echo "✓ vector_db ownership: $VECTOR_OWNER"
    else
        echo "✗ vector_db ownership: $VECTOR_OWNER (should be suspect:suspect)"
        echo "  Fix with: sudo chown -R suspect:suspect /home/suspect/.n8n/open-webui/data/vector_db"
    fi
fi

DB_OWNER=$(stat -c '%U:%G' /home/suspect/.n8n/open-webui/data/webui.db)
if [ "$DB_OWNER" = "suspect:suspect" ]; then
    echo "✓ webui.db ownership: $DB_OWNER"
else
    echo "✗ webui.db ownership: $DB_OWNER (should be suspect:suspect)"
    echo "  Fix with: sudo chown suspect:suspect /home/suspect/.n8n/open-webui/data/webui.db"
fi

echo ""
echo "=== Recommendations ==="
echo ""
echo "If OpenWebUI is crashing:"
echo "1. Check full logs: sudo journalctl -u open-webui.service -n 100"
echo "2. Try manual start: /home/suspect/.n8n/open-webui-venv/bin/open-webui serve --host 0.0.0.0 --port 3000"
echo "3. Check for port conflicts: ss -ltnp | grep 3000"
echo "4. Verify environment: cat /etc/systemd/system/open-webui.service.d/override.conf"
echo ""
echo "To restart after fixing:"
echo "  sudo systemctl restart open-webui.service"

