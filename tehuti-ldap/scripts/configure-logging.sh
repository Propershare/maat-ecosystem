#!/bin/bash
# Configure LDAP logging with log rotation
# Maat-Aligned Logging Configuration

set -e

LOG_DIR="/var/log/ldap"
LOG_FILE="$LOG_DIR/tehuti-ldap.log"

echo "📋 Configuring LDAP logging..."

# Create log directory
sudo mkdir -p "$LOG_DIR"
sudo chown openldap:openldap "$LOG_DIR"
sudo chmod 755 "$LOG_DIR"

# Configure syslog for LDAP
echo "Configuring syslog for LDAP..."
if [ -d "/etc/rsyslog.d" ]; then
    sudo tee /etc/rsyslog.d/30-ldap.conf > /dev/null <<EOF
# Tehuti Lab LDAP Server Logging
local4.*    $LOG_FILE
EOF
    sudo systemctl restart rsyslog
elif [ -d "/etc/syslog-ng" ]; then
    sudo tee /etc/syslog-ng/conf.d/ldap.conf > /dev/null <<EOF
# Tehuti Lab LDAP Server Logging
filter f_ldap { facility(local4); };
destination d_ldap { file("$LOG_FILE"); };
log { source(s_src); filter(f_ldap); destination(d_ldap); };
EOF
    sudo systemctl restart syslog-ng
fi

# Configure logrotate
echo "Configuring log rotation..."
sudo tee /etc/logrotate.d/tehuti-ldap > /dev/null <<EOF
$LOG_FILE {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0640 openldap openldap
    sharedscripts
    postrotate
        systemctl reload tehuti-ldap.service > /dev/null 2>&1 || true
    endscript
}
EOF

# Update slapd.conf to use local4 facility
echo "Updating slapd.conf log level..."
# Log level 256 = stats (connections, operations, results)
# This is already configured in slapd.conf

echo "✅ Logging configured:"
echo "   Log file: $LOG_FILE"
echo "   Rotation: Daily, keep 30 days"
echo "   Log level: 256 (stats)"
echo ""
echo "📋 To view logs:"
echo "   tail -f $LOG_FILE"
echo ""
echo "🔄 Restart LDAP server to apply logging:"
echo "   sudo systemctl restart tehuti-ldap"

