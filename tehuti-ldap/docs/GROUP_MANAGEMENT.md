# LDAP Group Management Guide

## Three-Ring Governance Groups

### Inner Ring (Canon)

- **Purpose:** Read-only access to protected resources
- **DN:** `cn=inner-ring,ou=groups,dc=tehuti,dc=lab`
- **Permissions:** Read only

### Middle Ring (Scholarship)

- **Purpose:** Can propose changes, read-only access
- **DN:** `cn=middle-ring,ou=groups,dc=tehuti,dc=lab`
- **Permissions:** Read, propose

### Outer Ring (Monetized)

- **Purpose:** Full access to monetized resources
- **DN:** `cn=outer-ring,ou=groups,dc=tehuti,dc=lab`
- **Permissions:** Read, write, execute, propose

## Adding a Group

```bash
ldapadd -x -H ldap://127.0.0.1:389 \
  -D "cn=admin,dc=tehuti,dc=lab" \
  -w <admin_password>
```

Then enter:
```
dn: cn=newgroup,ou=groups,dc=tehuti,dc=lab
objectClass: top
objectClass: maatGroup
cn: newgroup
description: New group description
maatRole: outer-ring
member: cn=admin,dc=tehuti,dc=lab
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

## Removing User from Group

```bash
ldapmodify -x -H ldap://127.0.0.1:389 \
  -D "cn=admin,dc=tehuti,dc=lab" \
  -w <admin_password>
```

Then enter:
```
dn: cn=outer-ring,ou=groups,dc=tehuti,dc=lab
changetype: modify
delete: member
member: uid=username,ou=users,dc=tehuti,dc=lab
```

## Listing Group Members

```bash
ldapsearch -x -H ldap://127.0.0.1:389 \
  -D "cn=admin,dc=tehuti,dc=lab" \
  -w <admin_password> \
  -b "cn=outer-ring,ou=groups,dc=tehuti,dc=lab" \
  "(objectClass=maatGroup)"
```

## Listing User's Groups

```bash
ldapsearch -x -H ldap://127.0.0.1:389 \
  -D "cn=admin,dc=tehuti,dc=lab" \
  -w <admin_password> \
  -b "ou=groups,dc=tehuti,dc=lab" \
  "(member=uid=username,ou=users,dc=tehuti,dc=lab)"
```

## Deleting a Group

```bash
ldapdelete -x -H ldap://127.0.0.1:389 \
  -D "cn=admin,dc=tehuti,dc=lab" \
  -w <admin_password> \
  "cn=groupname,ou=groups,dc=tehuti,dc=lab"
```

## Group Hierarchy

Groups follow three-ring governance:

1. **inner-ring** - Most restrictive (read-only)
2. **middle-ring** - Can propose (read + propose)
3. **outer-ring** - Full access (read + write + execute + propose)

Users can belong to multiple groups, but permissions are determined by the highest-level group.

