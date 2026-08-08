#!/bin/bash
# Run on the SERVER (this machine) with: sudo bash open-postgres-to-lan.sh
# Allows workstations on 192.168.4.0/24 to connect to PostgreSQL on port 5432 for gitMaat.

set -e
CONF_DIR="${CONF_DIR:-/etc/postgresql/14/main}"
LAN_CIDR="${LAN_CIDR:-192.168.4.0/24}"

echo "=== Opening PostgreSQL to LAN (gitMaat) ==="
echo "Config dir: $CONF_DIR"
echo "LAN: $LAN_CIDR"
echo ""

# 1. Set listen_addresses = '*'
if grep -q "^listen_addresses" "$CONF_DIR/postgresql.conf"; then
    sed -i "s/^listen_addresses.*/listen_addresses = '*'/" "$CONF_DIR/postgresql.conf"
else
    # Uncomment and set, or add new line after the commented default
    sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" "$CONF_DIR/postgresql.conf"
    if ! grep -q "^listen_addresses" "$CONF_DIR/postgresql.conf"; then
        echo "listen_addresses = '*'" >> "$CONF_DIR/postgresql.conf"
    fi
fi
echo "Set listen_addresses = '*' in postgresql.conf"

# 2. Allow LAN in pg_hba.conf (scram-sha-256 for PG 14)
if grep -q "maat_memory.*$LAN_CIDR" "$CONF_DIR/pg_hba.conf"; then
    echo "pg_hba.conf already has rule for maat_memory $LAN_CIDR"
else
    echo "host  maat_memory  all  $LAN_CIDR  scram-sha-256" >> "$CONF_DIR/pg_hba.conf"
    echo "Added pg_hba rule: host maat_memory all $LAN_CIDR scram-sha-256"
fi

# 3. Restart PostgreSQL
echo "Restarting PostgreSQL..."
systemctl restart postgresql
echo "PostgreSQL restarted."

# 4. Allow port in firewall if ufw is active
if command -v ufw >/dev/null 2>&1 && ufw status 2>/dev/null | grep -q "Status: active"; then
    ufw allow 5432/tcp comment "gitMaat PostgreSQL"
    echo "UFW: allowed 5432/tcp"
fi

echo ""
echo "Done. From a workstation, test: python3 test_gitmaat_connection.py (with .env pointing at this server:5432)"
