#!/bin/bash
# Generate SSL certificates for LDAPS
# Maat-Aligned Certificate Generation

set -e

SSL_DIR="/home/suspect/.n8n/tehuti-ldap/ssl"
DAYS_VALID=3650  # 10 years

echo "🔒 Generating SSL certificates for LDAPS..."

# Create SSL directory if it doesn't exist
mkdir -p "$SSL_DIR"
cd "$SSL_DIR"

# Generate CA private key
echo "Generating CA private key..."
openssl genrsa -out ca.key 4096

# Generate CA certificate
echo "Generating CA certificate..."
openssl req -new -x509 -days $DAYS_VALID -key ca.key -out ca.crt \
    -subj "/C=US/ST=State/L=City/O=Tehuti Lab/CN=Tehuti Lab CA"

# Generate server private key
echo "Generating server private key..."
openssl genrsa -out ldap.key 4096

# Generate server certificate signing request
echo "Generating server certificate signing request..."
openssl req -new -key ldap.key -out ldap.csr \
    -subj "/C=US/ST=State/L=City/O=Tehuti Lab/CN=localhost"

# Generate server certificate signed by CA
echo "Generating server certificate..."
openssl x509 -req -days $DAYS_VALID -in ldap.csr -CA ca.crt -CAkey ca.key \
    -CAcreateserial -out ldap.crt

# Set permissions
chmod 600 ca.key ldap.key
chmod 644 ca.crt ldap.crt

echo ""
echo "✅ SSL certificates generated:"
echo "   - CA Certificate: $SSL_DIR/ca.crt"
echo "   - CA Key: $SSL_DIR/ca.key"
echo "   - Server Certificate: $SSL_DIR/ldap.crt"
echo "   - Server Key: $SSL_DIR/ldap.key"
echo ""
echo "📋 Next: Update slapd.conf with certificate paths"

