# Secrets Directory

**⚠️ SECURITY**: This directory contains sensitive credentials. Never commit to git.

## Files

- `api-keys.json` - API keys and credentials for all services
- `contextguard-alerts.env` - Context guard alert configuration

## File Permissions

All files in this directory should have restrictive permissions:
```bash
chmod 600 /home/suspect/.n8n/config/secrets/*
```

## Usage

### Reading API Keys

```python
import json

with open('/home/suspect/.n8n/config/secrets/api-keys.json', 'r') as f:
    secrets = json.load(f)
    
nginx_key = secrets['nginx']['tool_api_key']
n8n_key = secrets['n8n']['api_key']
```

### Updating API Keys

1. Edit the JSON file
2. Update the relevant service
3. Restart services if needed

## Git Ignore

This directory should be in `.gitignore`:
```
config/secrets/
```

