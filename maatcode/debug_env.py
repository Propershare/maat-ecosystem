#!/usr/bin/env python3
"""Quick debug script to check .env file loading"""

import os
from pathlib import Path

workspace_root = Path("/home/suspect/.n8n")

print("=" * 60)
print("Debug: Checking .env files")
print("=" * 60)

# Check environment
pg_url = os.environ.get("PGVECTOR_DB_URL")
print(f"\n1. Environment variable PGVECTOR_DB_URL: {'SET' if pg_url else 'NOT SET'}")
if pg_url:
    if "@" in pg_url:
        parts = pg_url.split("@")
        if len(parts) == 2:
            masked = parts[0].split(":")[0] + ":****@" + parts[1]
            print(f"   Value: {masked}")
        else:
            print(f"   Value: {pg_url[:50]}...")
    else:
        print(f"   Value: {pg_url[:50]}...")

# Check .env files
env_files = [
    workspace_root / "tehuti-lab-webui" / ".env",
    workspace_root / "open-webui" / ".env",
    workspace_root / ".env",
]

print(f"\n2. Checking .env files:")
for env_file in env_files:
    exists = env_file.exists()
    print(f"   {env_file}: {'EXISTS' if exists else 'NOT FOUND'}")
    
    if exists:
        try:
            with open(env_file, "r") as f:
                found = False
                for line_num, line in enumerate(f, 1):
                    if line.startswith("PGVECTOR_DB_URL"):
                        found = True
                        db_url = line.split("=", 1)[1].strip().strip('"').strip("'") if "=" in line else ""
                        if "@" in db_url:
                            parts = db_url.split("@")
                            if len(parts) == 2:
                                masked = parts[0].split(":")[0] + ":****@" + parts[1]
                                print(f"      Line {line_num}: PGVECTOR_DB_URL={masked}")
                            else:
                                print(f"      Line {line_num}: PGVECTOR_DB_URL={db_url[:50]}...")
                        else:
                            print(f"      Line {line_num}: PGVECTOR_DB_URL={db_url[:50]}...")
                        break
                if not found:
                    print(f"      PGVECTOR_DB_URL not found in file")
        except Exception as e:
            print(f"      ERROR reading file: {e}")

print("\n" + "=" * 60)

