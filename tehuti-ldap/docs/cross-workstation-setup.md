# Cross-Workstation LDAP Setup
# Maat-Aligned Cross-Workstation Configuration

**IMPORTANT: Use LDAPS (port 636) for all cross-workstation connections for security.**

## Overview

This guide explains how to configure LDAP clients on other workstations (imhotep, macdaddy, imhotepjr) to connect to the central LDAP server on staydangerous.

## Prerequisites

- LDAP server running on staydangerous (47.200.181.85)
- LDAPS (port 636) configured with TLS certificates
- CA certificate distributed to all workstations
- Network connectivity between workstations (192.168.4.0/24)

## Step 1: Distribute CA Certificate

### On staydangerous (LDAP Server)

1. Copy CA certificate to shared location or distribute securely:
```bash
# Copy CA certificate
sudo cp /home/suspect/.n8n/tehuti-ldap/ssl/ca.crt /tmp/tehuti-ldap-ca.crt
sudo chmod 644 /tmp/tehuti-ldap-ca.crt
```

2. Transfer to client workstations using secure method (scp, USB, etc.)

### On Client Workstations

1. Install CA certificate:
```bash
# Ubuntu/Debian
sudo cp tehuti-ldap-ca.crt /usr/local/share/ca-certificates/tehuti-ldap-ca.crt
sudo update-ca-certificates

# Or place in LDAP client config directory
sudo mkdir -p /etc/ldap/ssl
sudo cp tehuti-ldap-ca.crt /etc/ldap/ssl/tehuti-ldap-ca.crt
sudo chmod 644 /etc/ldap/ssl/tehuti-ldap-ca.crt
```

## Step 2: Configure LDAP Client

### Install LDAP Client Tools

```bash
sudo apt-get update
sudo apt-get install -y ldap-utils libldap-common
```

### Configure LDAP Client (ldap.conf)

Create or edit `/etc/ldap/ldap.conf`:

```bash
sudo tee /etc/ldap/ldap.conf > /dev/null <<EOF
# Tehuti Lab LDAP Configuration
BASE    dc=tehuti,dc=lab
URI     ldaps://47.200.181.85:636

# TLS Configuration
TLS_CACERT      /etc/ldap/ssl/tehuti-ldap-ca.crt
TLS_REQCERT     demand
TLS_CACERTDIR   /etc/ldap/ssl

# Security
SASL_NOCANON    on
EOF
```

## Step 3: Test LDAPS Connection

### Test Connection

```bash
# Test LDAPS connection with certificate validation
ldapsearch -x -H ldaps://47.200.181.85:636 \
    -D "cn=admin,dc=tehuti,dc=lab" \
    -w "<admin_password>" \
    -b "dc=tehuti,dc=lab" \
    -s base "(objectClass=*)"

# Test anonymous bind (should fail if ACLs are enforced)
ldapsearch -x -H ldaps://47.200.181.85:636 \
    -b "dc=tehuti,dc=lab" \
    -s base "(objectClass=*)"
```

### Test User Authentication

```bash
# Test user authentication
ldapwhoami -x -H ldaps://47.200.181.85:636 \
    -D "uid=testuser,ou=users,dc=tehuti,dc=lab" \
    -w "<user_password>"
```

## Step 4: Configure Applications

### Open WebUI Integration

Update Open WebUI `.env` file:

```env
# LDAP Configuration (LDAPS)
ENABLE_LDAP=true
LDAP_SERVER_LABEL="Tehuti Lab LDAP"
LDAP_SERVER_HOST=47.200.181.85
LDAP_SERVER_PORT=636
LDAP_USE_TLS=true
LDAP_VALIDATE_CERT=true
LDAP_CA_CERT_FILE=/etc/ldap/ssl/tehuti-ldap-ca.crt

# LDAP Search Configuration
LDAP_SEARCH_BASE="ou=users,dc=tehuti,dc=lab"
LDAP_SEARCH_FILTERS="(objectClass=maatUser)"
LDAP_ATTRIBUTE_FOR_USERNAME=uid
LDAP_ATTRIBUTE_FOR_MAIL=mail

# LDAP App Credentials
LDAP_APP_DN="cn=admin,dc=tehuti,dc=lab"
LDAP_APP_PASSWORD=<secure_password>
```

### Python LDAP Client

Example Python code using `ldap3`:

```python
from ldap3 import Server, Connection, Tls, ALL
import ssl

# Configure TLS
tls = Tls(
    ca_certs_file='/etc/ldap/ssl/tehuti-ldap-ca.crt',
    validate=ssl.CERT_REQUIRED
)

# Connect via LDAPS
server = Server(
    'ldaps://47.200.181.85:636',
    use_ssl=True,
    tls=tls,
    get_info=ALL
)

# Bind
conn = Connection(
    server,
    user='cn=admin,dc=tehuti,dc=lab',
    password='<admin_password>',
    auto_bind=True
)

# Search
conn.search(
    'dc=tehuti,dc=lab',
    '(objectClass=*)',
    attributes=['uid', 'mail', 'memberOf']
)

conn.unbind()
```

## Step 5: Firewall Configuration

### On staydangerous (LDAP Server)

Ensure firewall allows LDAPS from internal network:

```bash
# Allow LDAPS from internal network
sudo ufw allow from 192.168.4.0/24 to any port 636 proto tcp comment "LDAPS - Internal network"
```

### On Client Workstations

No special firewall configuration needed (outbound connections).

## Step 6: Verify Configuration

### Connection Test Script

Create test script on client workstation:

```bash
#!/bin/bash
# Test LDAPS connection from client workstation

LDAP_SERVER="ldaps://47.200.181.85:636"
LDAP_BASE="dc=tehuti,dc=lab"
LDAP_ADMIN="cn=admin,dc=tehuti,dc=lab"

echo "Testing LDAPS connection to $LDAP_SERVER..."

# Test 1: Server reachability
echo "1. Testing server reachability..."
if ldapsearch -x -H "$LDAP_SERVER" \
    -b "$LDAP_BASE" \
    -s base "(objectClass=*)" > /dev/null 2>&1; then
    echo "   ✅ Server is reachable"
else
    echo "   ❌ Server is not reachable"
    exit 1
fi

# Test 2: Certificate validation
echo "2. Testing certificate validation..."
if ldapsearch -x -H "$LDAP_SERVER" \
    -D "$LDAP_ADMIN" \
    -w "<admin_password>" \
    -b "$LDAP_BASE" \
    -s base "(objectClass=*)" > /dev/null 2>&1; then
    echo "   ✅ Certificate validation passed"
else
    echo "   ❌ Certificate validation failed"
    exit 1
fi

# Test 3: Authentication
echo "3. Testing authentication..."
if ldapwhoami -x -H "$LDAP_SERVER" \
    -D "$LDAP_ADMIN" \
    -w "<admin_password>" > /dev/null 2>&1; then
    echo "   ✅ Authentication successful"
else
    echo "   ❌ Authentication failed"
    exit 1
fi

echo ""
echo "✅ All tests passed. LDAPS connection is working."
```

## Troubleshooting

### Certificate Errors

If you see certificate errors:

1. Verify CA certificate is installed:
```bash
ls -l /etc/ldap/ssl/tehuti-ldap-ca.crt
```

2. Verify certificate is valid:
```bash
openssl x509 -in /etc/ldap/ssl/tehuti-ldap-ca.crt -text -noout
```

3. Test with certificate:
```bash
ldapsearch -x -H ldaps://47.200.181.85:636 \
    -b "dc=tehuti,dc=lab" \
    -s base "(objectClass=*)" \
    -o ldif-wrap=no
```

### Connection Refused

If connection is refused:

1. Check firewall on server:
```bash
sudo ufw status | grep 636
```

2. Check LDAP server is running:
```bash
ssh staydangerous "sudo systemctl status tehuti-ldap"
```

3. Test network connectivity:
```bash
telnet 47.200.181.85 636
```

### Authentication Failures

If authentication fails:

1. Verify credentials:
```bash
ldapwhoami -x -H ldaps://47.200.181.85:636 \
    -D "cn=admin,dc=tehuti,dc=lab" \
    -w "<admin_password>"
```

2. Check ACLs on server:
```bash
# On server
sudo ldapsearch -Y EXTERNAL -H ldapi:/// \
    -b "olcDatabase={1}mdb,cn=config" \
    olcAccess
```

## Security Notes

- **Always use LDAPS (port 636)** for cross-workstation connections
- **Never use LDAP (port 389)** over untrusted networks
- **Validate certificates** to prevent man-in-the-middle attacks
- **Use strong passwords** for LDAP admin account
- **Restrict firewall** to internal network (192.168.4.0/24)
- **Monitor logs** for suspicious activity

## Next Steps

- Configure application-specific LDAP integration
- Set up monitoring and alerting
- Document user management procedures
- Test failover scenarios
