#!/bin/bash
# Distribute CA certificate to client workstations
# Maat-Aligned Certificate Distribution

set -e

CA_CERT="/home/suspect/.n8n/tehuti-ldap/ssl/ca.crt"
DIST_DIR="/tmp/tehuti-ldap-cert-dist"

echo "📋 Distributing CA certificate to client workstations..."

if [ ! -f "$CA_CERT" ]; then
    echo "❌ Error: CA certificate not found: $CA_CERT"
    exit 1
fi

# Create distribution directory
mkdir -p "$DIST_DIR"

# Copy CA certificate
cp "$CA_CERT" "$DIST_DIR/tehuti-ldap-ca.crt"
chmod 644 "$DIST_DIR/tehuti-ldap-ca.crt"

echo "✅ CA certificate prepared: $DIST_DIR/tehuti-ldap-ca.crt"
echo ""
echo "📋 Distribution instructions:"
echo ""
echo "1. Copy certificate to client workstations:"
echo "   scp $DIST_DIR/tehuti-ldap-ca.crt user@workstation:/tmp/"
echo ""
echo "2. On client workstation, install certificate:"
echo "   sudo cp /tmp/tehuti-ldap-ca.crt /etc/ldap/ssl/tehuti-ldap-ca.crt"
echo "   sudo chmod 644 /etc/ldap/ssl/tehuti-ldap-ca.crt"
echo "   sudo update-ca-certificates"
echo ""
echo "3. Test LDAPS connection:"
echo "   ldapsearch -x -H ldaps://47.200.181.85:636 \\"
echo "       -b \"dc=tehuti,dc=lab\" \\"
echo "       -s base \"(objectClass=*)\""
echo ""
echo "📋 Client workstations:"
echo "   - imhotep (192.168.4.x)"
echo "   - macdaddy (192.168.4.x)"
echo "   - imhotepjr (192.168.4.x)"

