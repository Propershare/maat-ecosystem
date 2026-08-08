#!/bin/bash
# Fix external mobile access for ai.suspecttv.com

echo "=== Fixing Firewall for External Access ==="
echo ""

# Check current firewall status
echo "Current firewall status:"
sudo ufw status verbose | head -10

echo ""
echo "Allowing HTTPS (443) and HTTP (80)..."
sudo ufw allow 443/tcp comment 'HTTPS for ai.suspecttv.com'
sudo ufw allow 80/tcp comment 'HTTP for ai.suspecttv.com'

echo ""
echo "Reloading firewall..."
sudo ufw reload

echo ""
echo "New firewall status:"
sudo ufw status | grep -E "443|80|Status"

echo ""
echo "✅ Firewall configured!"
echo ""
echo "Test from mobile: https://ai.suspecttv.com"
