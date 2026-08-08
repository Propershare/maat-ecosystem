#!/bin/bash
# Configure firewall rules for LDAP
# Maat-Aligned Firewall Configuration

set -e

echo "🔥 Configuring firewall for LDAP..."

# Check if ufw is installed
if ! command -v ufw &> /dev/null; then
    echo "❌ Error: ufw not found. Install with: sudo apt-get install -y ufw"
    exit 1
fi

# Internal network (Tehuti Lab workstations)
INTERNAL_NETWORK="192.168.4.0/24"

echo "Configuring firewall rules..."
echo "  Internal network: $INTERNAL_NETWORK"
echo ""

# Allow LDAP (389) from internal network only
echo "Rule 1: Allow LDAP (389) from internal network..."
sudo ufw allow from $INTERNAL_NETWORK to any port 389 proto tcp comment "LDAP - Internal network only"

# Allow LDAPS (636) from internal network only
echo "Rule 2: Allow LDAPS (636) from internal network..."
sudo ufw allow from $INTERNAL_NETWORK to any port 636 proto tcp comment "LDAPS - Internal network only"

# Deny LDAP from anywhere else (explicit deny for clarity)
echo "Rule 3: Deny LDAP from external networks..."
# Note: ufw denies by default, but we can be explicit
sudo ufw deny 389/tcp comment "LDAP - External access denied"
sudo ufw deny 636/tcp comment "LDAPS - External access denied"

# Then re-allow for internal network (order matters)
sudo ufw allow from $INTERNAL_NETWORK to any port 389 proto tcp comment "LDAP - Internal network"
sudo ufw allow from $INTERNAL_NETWORK to any port 636 proto tcp comment "LDAPS - Internal network"

echo ""
echo "✅ Firewall rules configured"
echo ""
echo "📋 Current firewall status:"
sudo ufw status numbered | grep -E "(389|636)" || echo "No LDAP rules found (check ufw status)"

echo ""
echo "⚠️  Note: If firewall was not active, enable it with:"
echo "   sudo ufw enable"
echo ""
echo "📋 Test firewall rules:"
echo "   From internal network: ldapsearch -x -H ldap://47.200.181.85:389 -b \"dc=tehuti,dc=lab\""
echo "   From external: Should be blocked"

