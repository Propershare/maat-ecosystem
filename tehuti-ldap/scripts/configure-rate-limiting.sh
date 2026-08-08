#!/bin/bash
# Configure rate limiting and fail2ban for LDAP
# Maat-Aligned Rate Limiting Configuration

set -e

echo "🔒 Configuring rate limiting for LDAP..."

# Password policy already includes lockout settings
# Verify password policy is loaded
echo "Verifying password policy is loaded..."
POLICY_DN="cn=passwordPolicy,ou=policies,dc=tehuti,dc=lab"

# Get password from secure file
PASSWORD_FILE="/home/suspect/.n8n/tehuti-ldap/.ldap_admin_password"
if [ -z "$LDAP_ADMIN_PASSWORD" ]; then
    if [ -f "$PASSWORD_FILE" ]; then
        export LDAP_ADMIN_PASSWORD=$(cat "$PASSWORD_FILE")
    else
        echo "❌ Error: Password file not found: $PASSWORD_FILE"
        exit 1
    fi
fi

# Check if password policy exists
if ldapsearch -x -H ldap://127.0.0.1:389 \
    -D "cn=admin,dc=tehuti,dc=lab" \
    -w "$LDAP_ADMIN_PASSWORD" \
    -b "$POLICY_DN" \
    -s base "(objectClass=pwdPolicy)" cn 2>/dev/null | grep -q "cn: passwordPolicy"; then
    echo "✅ Password policy is loaded"
else
    echo "⚠️  Password policy not found. Loading it now..."
    /home/suspect/.n8n/tehuti-ldap/scripts/load-password-policy.sh
fi

# Configure fail2ban for LDAP
echo ""
echo "Configuring fail2ban for LDAP..."

if ! command -v fail2ban-client &> /dev/null; then
    echo "⚠️  fail2ban not installed. Installing..."
    sudo apt-get update
    sudo apt-get install -y fail2ban
fi

# Create fail2ban filter for LDAP
sudo tee /etc/fail2ban/filter.d/ldap.conf > /dev/null <<'EOF'
[Definition]
# Fail2ban filter for OpenLDAP
# Matches failed authentication attempts

failregex = ^.*\s+ldap.*\s+.*authentication\s+failed.*$
            ^.*\s+ldap.*\s+.*invalid\s+credentials.*$
            ^.*\s+ldap.*\s+.*bind\s+failed.*$

ignoreregex =
EOF

# Create fail2ban jail for LDAP
sudo tee /etc/fail2ban/jail.d/ldap.conf > /dev/null <<EOF
[ldap]
enabled = true
port = 389,636
filter = ldap
logpath = /var/log/ldap/tehuti-ldap.log
maxretry = 5
bantime = 3600
findtime = 600
action = iptables[name=LDAP, port=389,636, protocol=tcp]
EOF

# Restart fail2ban
sudo systemctl restart fail2ban

echo "✅ Rate limiting configured:"
echo "   Password lockout: 5 failed attempts (from password policy)"
echo "   Lockout duration: 300 seconds (5 minutes)"
echo "   fail2ban: Enabled"
echo "   Max retries: 5"
echo "   Ban time: 3600 seconds (1 hour)"
echo "   Find time: 600 seconds (10 minutes)"
echo ""
echo "📋 Check fail2ban status:"
echo "   sudo fail2ban-client status ldap"
echo ""
echo "📋 View banned IPs:"
echo "   sudo fail2ban-client get ldap banned"

