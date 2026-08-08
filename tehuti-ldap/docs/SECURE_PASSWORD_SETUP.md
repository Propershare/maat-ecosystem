# Secure Password Setup Guide

## Overview

This guide explains how to set up secure passwords for the LDAP server. **Default passwords MUST be changed before production use.**

## Step 1: Generate Admin Password Hash

```bash
cd /home/suspect/.n8n/tehuti-ldap
./scripts/generate-secure-password.sh "YourSecurePassword123!"
```

This will output an SSHA hash like:
```
{SSHA}abc123def456...
```

## Step 2: Update slapd.conf

Edit `config/slapd.conf` and replace:
```
rootpw          {SSHA}CHANGE_ME_USE_GENERATE_SECURE_PASSWORD_SCRIPT
```

With:
```
rootpw          {SSHA}abc123def456...
```

## Step 3: Update base.ldif

Edit `ldif/base.ldif` and replace:
```
userPassword: {SSHA}CHANGE_ME_USE_GENERATE_SECURE_PASSWORD_SCRIPT
```

With:
```
userPassword: {SSHA}abc123def456...
```

## Step 4: Store Password Securely

- Store plaintext password in password manager
- Do NOT commit passwords to git
- Document password location securely
- Share with authorized personnel only

## Step 5: Create User Passwords

When creating users, generate password hash:

```bash
./scripts/generate-secure-password.sh "UserPassword123!"
```

Then add to user LDIF:
```
userPassword: {SSHA}generated_hash_here
```

## Security Notes

- Use strong passwords (min 16 characters, mixed case, numbers, symbols)
- Never use default passwords
- Rotate passwords regularly
- Use different passwords for admin and users
- Store passwords in secure password manager

