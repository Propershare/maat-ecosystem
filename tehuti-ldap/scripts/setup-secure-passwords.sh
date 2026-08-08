#!/bin/bash
# Setup secure passwords for LDAP
# Maat-Aligned Password Setup

set -e

echo "🔒 Setting up secure LDAP passwords..."
echo ""
echo "⚠️  IMPORTANT: This will generate new passwords for LDAP."
echo "   You will need to update configurations manually."
echo ""

# Check if slappasswd is available
if ! command -v slappasswd &> /dev/null; then
    echo "❌ Error: slappasswd not found. Install OpenLDAP utilities:"
    echo "   sudo apt-get install -y ldap-utils"
    exit 1
fi

# Generate admin password
echo "Generating admin password..."
read -sp "Enter admin password: " ADMIN_PASSWORD
echo ""
read -sp "Confirm admin password: " ADMIN_PASSWORD_CONFIRM
echo ""

if [ "$ADMIN_PASSWORD" != "$ADMIN_PASSWORD_CONFIRM" ]; then
    echo "❌ Passwords do not match"
    exit 1
fi

if [ -z "$ADMIN_PASSWORD" ]; then
    echo "❌ Password cannot be empty"
    exit 1
fi

# Generate SSHA hash
ADMIN_HASH=$(slappasswd -s "$ADMIN_PASSWORD")

echo ""
echo "✅ Generated admin password hash:"
echo "$ADMIN_HASH"
echo ""
echo "📋 Next steps:"
echo "1. Update slapd.conf: rootpw $ADMIN_HASH"
echo "2. Update base.ldif: userPassword: $ADMIN_HASH"
echo "3. Store password securely (password manager)"
echo ""
echo "🔒 Password hash saved. Update configuration files now."

