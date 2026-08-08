# LDAP Integration Guide

## Open WebUI Integration

### Configuration

Add to `/home/suspect/.n8n/tehuti-lab-webui/.env`:

```env
ENABLE_LDAP=true
LDAP_SERVER_LABEL="Tehuti Lab LDAP"
LDAP_SERVER_HOST=127.0.0.1
LDAP_SERVER_PORT=389
LDAP_USE_TLS=false
LDAP_VALIDATE_CERT=false
LDAP_SEARCH_BASE="ou=users,dc=tehuti,dc=lab"
LDAP_SEARCH_FILTERS="(objectClass=maatUser)"
LDAP_ATTRIBUTE_FOR_USERNAME=uid
LDAP_ATTRIBUTE_FOR_MAIL=mail
LDAP_APP_DN="cn=admin,dc=tehuti,dc=lab"
LDAP_APP_PASSWORD=<admin_password>
ENABLE_LDAP_GROUP_MANAGEMENT=true
ENABLE_LDAP_GROUP_CREATION=false
LDAP_ATTRIBUTE_FOR_GROUPS=memberOf
```

### Testing

1. Restart Open WebUI service
2. Navigate to login page
3. Select "LDAP" authentication option
4. Enter LDAP username and password
5. Verify successful login

## gitMaat Integration

### Automatic Logging

LDAP authentication events are automatically logged to gitMaat when users authenticate via Open WebUI.

### Manual Logging

```python
from maat_memory import MaatMemory, get_unique_agent_id
from maat_memory.ldap_integration import LDAPIntegration

memory = MaatMemory()
agent_id = get_unique_agent_id("cursor")
ldap_integration = LDAPIntegration(memory)

# Log authentication event
ldap_integration.log_ldap_auth(
    agent=agent_id,
    ldap_user="username",
    success=True,
    groups=["outer-ring", "admins"],
    metadata={"source": "manual"}
)

# Map LDAP user to agent
ldap_integration.map_ldap_to_agent(
    ldap_user="username",
    agent_id=agent_id
)
```

### Querying LDAP Data

```python
# Get user's groups from gitMaat
groups = ldap_integration.get_ldap_user_groups("username")

# Get LDAP user mapped to agent
ldap_user = ldap_integration.get_ldap_user_from_agent(agent_id)
```

## TehutiGuard Integration

### Policy Enforcement

TehutiGuard uses LDAP groups to enforce three-ring governance:

```typescript
import { enforceLDAPPolicy, queryLDAPUserGroups } from './ldap-policy';

// Query user's LDAP groups
const groups = await queryLDAPUserGroups('username');

// Enforce policy
const decision = enforceLDAPPolicy(
  {
    action: 'write',
    resource: 'maatlangchain/',
    user: 'username'
  },
  {
    uid: 'username',
    groups: groups
  }
);

if (decision.allowed) {
  // Allow action
} else {
  // Deny action
}
```

### Three-Ring Mapping

- `inner-ring` → Read-only (Canon)
- `middle-ring` → Propose (Scholarship)
- `outer-ring` → Full access (Monetized)

## Cross-Workstation Integration

### Server Configuration

LDAP server runs on `staydangerous` (47.200.181.85).

### Client Configuration

Each workstation connects to the central LDAP server:

1. Install LDAP client tools
2. Configure `/etc/ldap/ldap.conf`
3. Test connection using `test-ldap-connection.sh`
4. Configure Open WebUI (if installed) to use remote LDAP server

See [cross-workstation-setup.md](cross-workstation-setup.md) for detailed instructions.

## Troubleshooting

### Authentication Fails

1. Check LDAP server is running: `sudo systemctl status tehuti-ldap`
2. Verify user exists: `ldapsearch -x -b "ou=users,dc=tehuti,dc=lab" "(uid=username)"`
3. Check password: `ldapwhoami -x -D "uid=username,ou=users,dc=tehuti,dc=lab" -w <password>`
4. Check Open WebUI logs: `tail -f /tmp/tehuti-webui.log`

### gitMaat Logging Fails

1. Verify gitMaat connection: Check `PGVECTOR_DB_URL` in `.env`
2. Check Python path: Ensure `maatlangchain` is in Python path
3. Check logs: Look for gitMaat errors in Open WebUI logs

### TehutiGuard Policy Issues

1. Verify LDAP groups are correct
2. Check three-ring mapping in `ldap-policy.ts`
3. Verify permissions match expected role

