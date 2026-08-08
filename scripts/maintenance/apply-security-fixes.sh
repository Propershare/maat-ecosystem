#!/bin/bash
# Apply security fixes: localhost binding and restart services

echo "=== Applying Security Fixes ==="
echo ""

echo "1. Updating systemd service files to use 127.0.0.1..."
# This will be done by re-running start-all-mcpo-services.sh after it's updated

echo "2. Restarting all mcpo services (requires sudo)..."
echo "   Run: sudo /home/suspect/.n8n/start-all-mcpo-services.sh"

echo ""
echo "3. After restarting, verify services are on localhost:"
echo "   ss -ltnp | grep -E '8011|8012|8013|8014|8015|8016|8017|8018'"
echo "   Should show 127.0.0.1, not 0.0.0.0"

echo ""
echo "4. High-risk tools now have authentication:"
echo "   - Port 8013 (integration) - bearer auth"
echo "   - Port 8014 (core/python) - bearer auth"
echo "   - Port 8016 (filesystem) - bearer auth"
echo "   - Port 8017 (postgres) - bearer auth"

echo ""
echo "5. Restart OpenWebUI to apply auth changes:"
echo "   sudo systemctl restart open-webui"

