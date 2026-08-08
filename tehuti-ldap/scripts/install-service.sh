#!/bin/bash
# Install Tehuti Lab LDAP systemd service
# Maat-Aligned Service Installation

set -e

SERVICE_FILE="/etc/systemd/system/tehuti-ldap.service"
SOURCE_FILE="/home/suspect/.n8n/tehuti-ldap/systemd/tehuti-ldap.service"

echo "🔧 Installing Tehuti Lab LDAP service..."

# Check if service file exists
if [ ! -f "$SOURCE_FILE" ]; then
    echo "❌ Error: Service file not found: $SOURCE_FILE"
    exit 1
fi

# Copy service file
sudo cp "$SOURCE_FILE" "$SERVICE_FILE"
echo "✅ Service file copied"

# Reload systemd
sudo systemctl daemon-reload
echo "✅ Systemd daemon reloaded"

# Enable service (but don't start yet - need to configure first)
sudo systemctl enable tehuti-ldap.service
echo "✅ Service enabled"

echo ""
echo "📋 Next steps:"
echo "1. Configure LDAP (run setup-ldap.sh)"
echo "2. Start service: sudo systemctl start tehuti-ldap"
echo "3. Check status: sudo systemctl status tehuti-ldap"

