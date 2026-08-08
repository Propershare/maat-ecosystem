#!/bin/bash
# Fix stuck apt process

echo "Checking for stuck apt processes..."
ps aux | grep -E "apt|dpkg" | grep -v grep

echo ""
echo "Process 2905121 has been running for 44+ minutes (likely stuck)"
echo ""
echo "To fix, run these commands:"
echo ""
echo "1. Kill the stuck process:"
echo "   sudo kill -9 2905121"
echo ""
echo "2. Remove lock files:"
echo "   sudo rm /var/lib/dpkg/lock-frontend"
echo "   sudo rm /var/lib/dpkg/lock"
echo "   sudo rm /var/cache/apt/archives/lock"
echo ""
echo "3. Reconfigure dpkg if needed:"
echo "   sudo dpkg --configure -a"
echo ""
echo "4. Then retry the installation:"
echo "   sudo apt install -y python3.12 python3.12-venv python3.12-dev"

