#!/usr/bin/env python3
"""
Quick check for database connection string
"""

import os
from pathlib import Path

workspace_root = Path(__file__).parent.parent

# Check environment variable
pg_url = os.environ.get("PGVECTOR_DB_URL")
print(f"PGVECTOR_DB_URL from env: {'SET' if pg_url else 'NOT SET'}")

# Check .env file
env_file = workspace_root / "tehuti-lab-webui" / ".env"
if env_file.exists():
    print(f"\n.env file exists: {env_file}")
    with open(env_file, "r") as f:
        for line in f:
            if line.startswith("PGVECTOR_DB_URL="):
                db_url = line.split("=", 1)[1].strip().strip('"').strip("'")
                # Mask password for security
                if "@" in db_url:
                    parts = db_url.split("@")
                    if len(parts) == 2:
                        masked = parts[0].split(":")[0] + ":****@" + parts[1]
                        print(f"Found in .env: {masked}")
                    else:
                        print(f"Found in .env: {db_url[:50]}...")
                else:
                    print(f"Found in .env: {db_url[:50]}...")
                break
        else:
            print("PGVECTOR_DB_URL not found in .env file")
else:
    print(f"\n.env file not found: {env_file}")

