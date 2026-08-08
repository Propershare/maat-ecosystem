# Tehuti Lab LDAP Server

Maat-aligned LDAP server for centralized authentication across Tehuti Lab ecosystem.

## Architecture

- **Base DN:** `dc=tehuti,dc=lab`
- **Port:** 389 (LDAP), 636 (LDAPS)
- **Backend:** MDB (Memory-Mapped Database)
- **Schema:** Custom Maat schema with three-ring governance

## Directory Structure

```
tehuti-ldap/
├── schema/          # LDAP schema files
├── ldif/            # LDIF data files
├── ssl/             # SSL certificates
├── config/          # Configuration files
├── systemd/          # Systemd service files
├── scripts/         # Utility scripts
├── docs/            # Documentation
└── tests/           # Test files
```

## Quick Start

### 1. Install OpenLDAP

```bash
sudo apt-get update
sudo apt-get install -y slapd ldap-utils
```

### 2. Generate SSL Certificates

```bash
cd /home/suspect/.n8n/tehuti-ldap/ssl
./generate-certs.sh
```

### 3. Initialize LDAP Database

```bash
# Load base structure
ldapadd -x -H ldap://127.0.0.1:389 -D "cn=admin,dc=tehuti,dc=lab" -w <password> -f ldif/base.ldif

# Load groups
ldapadd -x -H ldap://127.0.0.1:389 -D "cn=admin,dc=tehuti,dc=lab" -w <password> -f ldif/groups.ldif

# Load users
ldapadd -x -H ldap://127.0.0.1:389 -D "cn=admin,dc=tehuti,dc=lab" -w <password> -f ldif/users.ldif
```

### 4. Install Systemd Service

```bash
cd /home/suspect/.n8n/tehuti-ldap
sudo ./scripts/install-service.sh
sudo systemctl start tehuti-ldap
```

### 5. Configure Open WebUI

See [docs/LDAP_ENV_CONFIG.md](docs/LDAP_ENV_CONFIG.md) for environment variables.

## Documentation

- [User Management](docs/USER_MANAGEMENT.md) - Adding, modifying, deleting users
- [Group Management](docs/GROUP_MANAGEMENT.md) - Managing three-ring groups
- [Integration Guide](docs/INTEGRATION.md) - Integrating with Open WebUI, gitMaat, TehutiGuard
- [Cross-Workstation Setup](docs/cross-workstation-setup.md) - Setting up remote workstations

## Maat Principles

- **Truth:** Single source of truth for user identity
- **Balance:** Unified access across all services
- **Order:** Structured hierarchy
- **Justice:** Three-ring governance
- **Self-Reflection:** Complete audit trail

## Three-Ring Governance

- **Inner Ring (Canon):** Read-only access
- **Middle Ring (Scholarship):** Can propose changes
- **Outer Ring (Monetized):** Full access

## Backup and Restore

```bash
# Backup
./scripts/backup.sh

# Restore
./scripts/restore.sh backups/ldap_backup_YYYYMMDD_HHMMSS.ldif.gz
```

## Testing

```bash
# Test local connection
./scripts/test-ldap-connection.sh

# Test remote connection
LDAP_ADMIN_PASSWORD=<password> ./scripts/test-ldap-connection.sh 47.200.181.85
```
