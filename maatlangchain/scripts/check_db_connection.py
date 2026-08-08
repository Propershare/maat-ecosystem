#!/usr/bin/env python3
"""Check database connection configuration"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.main import get_pgvector_url

print("=" * 80)
print("Database Connection Check")
print("=" * 80)
print()

# Check environment variable
pg_url_env = os.environ.get("PGVECTOR_DB_URL")
if pg_url_env:
    print("✓ PGVECTOR_DB_URL found in environment")
    # Mask password for security
    if "@" in pg_url_env:
        parts = pg_url_env.split("@")
        if len(parts) == 2:
            user_part = parts[0]
            if ":" in user_part:
                user, pwd = user_part.rsplit(":", 1)
                masked = f"{user}:{'*' * len(pwd)}@{parts[1]}"
                print(f"  Connection string: {masked}")
            else:
                print(f"  Connection string: {pg_url_env[:50]}...")
        else:
            print(f"  Connection string: {pg_url_env[:50]}...")
    else:
        print(f"  Connection string: {pg_url_env[:50]}...")
else:
    print("✗ PGVECTOR_DB_URL not in environment")

print()

# Check .env file
env_file = Path("/home/suspect/.n8n/tehuti-lab-webui/.env")
if env_file.exists():
    print(f"✓ .env file found: {env_file}")
    with open(env_file, 'r') as f:
        for line in f:
            if line.startswith("PGVECTOR_DB_URL="):
                value = line.split("=", 1)[1].strip().strip('"').strip("'")
                # Mask password
                if "@" in value:
                    parts = value.split("@")
                    if len(parts) == 2:
                        user_part = parts[0]
                        if ":" in user_part:
                            user, pwd = user_part.rsplit(":", 1)
                            masked = f"{user}:{'*' * len(pwd)}@{parts[1]}"
                            print(f"  Connection string: {masked}")
                        else:
                            print(f"  Connection string: {value[:50]}...")
                    else:
                        print(f"  Connection string: {value[:50]}...")
                else:
                    print(f"  Connection string: {value[:50]}...")
                break
        else:
            print("  ✗ PGVECTOR_DB_URL not found in .env file")
else:
    print(f"✗ .env file not found: {env_file}")

print()

# Try to get connection URL
try:
    pg_url = get_pgvector_url()
    if pg_url:
        print("✓ get_pgvector_url() returned a connection string")
        # Mask password
        if "@" in pg_url:
            parts = pg_url.split("@")
            if len(parts) == 2:
                user_part = parts[0]
                if ":" in user_part:
                    user, pwd = user_part.rsplit(":", 1)
                    masked = f"{user}:{'*' * len(pwd)}@{parts[1]}"
                    print(f"  Connection string: {masked}")
                else:
                    print(f"  Connection string: {pg_url[:50]}...")
            else:
                print(f"  Connection string: {pg_url[:50]}...")
        else:
            print(f"  Connection string: {pg_url[:50]}...")
        
        # Check if password is in connection string
        if "password=" in pg_url.lower() or ":" in pg_url.split("@")[0] if "@" in pg_url else False:
            print("  ✓ Password appears to be in connection string")
        else:
            print("  ⚠️  Warning: Password may be missing from connection string")
    else:
        print("✗ get_pgvector_url() returned None")
except Exception as e:
    print(f"✗ Error calling get_pgvector_url(): {e}")

print()
print("=" * 80)

