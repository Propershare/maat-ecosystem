# LDAP Environment Configuration for Open WebUI

Add these environment variables to `/home/suspect/.n8n/tehuti-lab-webui/.env`:

```env
# LDAP Configuration - Tehuti Lab
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
LDAP_APP_PASSWORD=changeme
ENABLE_LDAP_GROUP_MANAGEMENT=true
ENABLE_LDAP_GROUP_CREATION=false
LDAP_ATTRIBUTE_FOR_GROUPS=memberOf
```

**Note:** Change `LDAP_APP_PASSWORD` to the actual admin password after LDAP setup.

