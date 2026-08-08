# LDAP User Management Guide

## Adding a User

### Using LDIF File

1. Create user entry in LDIF format:

```ldif
dn: uid=newuser,ou=users,dc=tehuti,dc=lab
objectClass: top
objectClass: maatUser
objectClass: inetOrgPerson
uid: newuser
cn: New User
sn: User
mail: newuser@tehuti.lab
userPassword: {SSHA}encrypted_password
maatRole: outer-ring
maatAgentId: cursor_newuser
workstationId: staydangerous
maatPermissions: {"read": true, "write": true, "execute": true}
```

2. Add user to LDAP:

```bash
ldapadd -x -H ldap://127.0.0.1:389 \
  -D "cn=admin,dc=tehuti,dc=lab" \
  -w <admin_password> \
  -f newuser.ldif
```

### Using ldapmodify

```bash
ldapmodify -x -H ldap://127.0.0.1:389 \
  -D "cn=admin,dc=tehuti,dc=lab" \
  -w <admin_password>
```

Then enter:
```
dn: uid=newuser,ou=users,dc=tehuti,dc=lab
changetype: add
objectClass: top
objectClass: maatUser
objectClass: inetOrgPerson
uid: newuser
cn: New User
sn: User
mail: newuser@tehuti.lab
userPassword: {SSHA}encrypted_password
```

## Modifying a User

### Change Password

```bash
ldappasswd -x -H ldap://127.0.0.1:389 \
  -D "cn=admin,dc=tehuti,dc=lab" \
  -w <admin_password> \
  -s <new_password> \
  "uid=username,ou=users,dc=tehuti,dc=lab"
```

### Update Attributes

```bash
ldapmodify -x -H ldap://127.0.0.1:389 \
  -D "cn=admin,dc=tehuti,dc=lab" \
  -w <admin_password>
```

Then enter:
```
dn: uid=username,ou=users,dc=tehuti,dc=lab
changetype: modify
replace: maatRole
maatRole: middle-ring
```

## Deleting a User

```bash
ldapdelete -x -H ldap://127.0.0.1:389 \
  -D "cn=admin,dc=tehuti,dc=lab" \
  -w <admin_password> \
  "uid=username,ou=users,dc=tehuti,dc=lab"
```

## Searching Users

### List All Users

```bash
ldapsearch -x -H ldap://127.0.0.1:389 \
  -D "cn=admin,dc=tehuti,dc=lab" \
  -w <admin_password> \
  -b "ou=users,dc=tehuti,dc=lab" \
  "(objectClass=maatUser)"
```

### Search by Username

```bash
ldapsearch -x -H ldap://127.0.0.1:389 \
  -D "cn=admin,dc=tehuti,dc=lab" \
  -w <admin_password> \
  -b "ou=users,dc=tehuti,dc=lab" \
  "(uid=username)"
```

### Search by Email

```bash
ldapsearch -x -H ldap://127.0.0.1:389 \
  -D "cn=admin,dc=tehuti,dc=lab" \
  -w <admin_password> \
  -b "ou=users,dc=tehuti,dc=lab" \
  "(mail=user@tehuti.lab)"
```

## Adding User to Group

```bash
ldapmodify -x -H ldap://127.0.0.1:389 \
  -D "cn=admin,dc=tehuti,dc=lab" \
  -w <admin_password>
```

Then enter:
```
dn: cn=outer-ring,ou=groups,dc=tehuti,dc=lab
changetype: modify
add: member
member: uid=username,ou=users,dc=tehuti,dc=lab
```

## Maat Attributes

### maatRole

- `inner-ring`: Read-only access (Canon)
- `middle-ring`: Can propose changes (Scholarship)
- `outer-ring`: Full access (Monetized)

### maatAgentId

Agent identifier for gitMaat coordination (e.g., `cursor_imhotep`)

### workstationId

Associated workstation (e.g., `imhotep`, `macdaddy`, `staydangerous`)

### maatPermissions

JSON permissions object:
```json
{
  "read": true,
  "write": true,
  "execute": true
}
```

