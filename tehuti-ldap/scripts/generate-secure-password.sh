#!/bin/bash
# Generate secure LDAP password
# Maat-Aligned Password Generation

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <password>"
    echo ""
    echo "This script generates an SSHA hashed password for LDAP."
    echo "Example: $0 'MySecurePassword123!'"
    exit 1
fi

PASSWORD="$1"

# Check if slappasswd is available
if ! command -v slappasswd &> /dev/null; then
    echo "❌ Error: slappasswd not found. Install OpenLDAP utilities:"
    echo "   sudo apt-get install -y ldap-utils"
    exit 1
fi

# Generate SSHA hash
HASHED=$(slappasswd -s "$PASSWORD")

echo "✅ Generated SSHA hash:"
echo "$HASHED"
echo ""
echo "📋 Use this hash in:"
echo "   - slapd.conf: rootpw $HASHED"
echo "   - base.ldif: userPassword: $HASHED"
echo ""
echo "🔒 Store the plaintext password securely (password manager)"

