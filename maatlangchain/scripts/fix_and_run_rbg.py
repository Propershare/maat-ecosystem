#!/usr/bin/env python3
"""
Fix database connection and run RBG processing
Attempts to fix common database connection issues
"""

import os
import sys
from pathlib import Path

maatlangchain_root = Path(__file__).parent.parent
sys.path.insert(0, str(maatlangchain_root))
os.chdir(maatlangchain_root)

from api.main import get_pgvector_url

print("=" * 80)
print("Database Connection Check & Fix")
print("=" * 80)
print()

# Check current connection string
pg_url = get_pgvector_url()
if not pg_url:
    print("✗ No PGVECTOR_DB_URL found")
    print("\nTrying to find it in .env file...")
    
    env_file = Path("/home/suspect/.n8n/tehuti-lab-webui/.env")
    if env_file.exists():
        print(f"✓ Found .env file: {env_file}")
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith("PGVECTOR_DB_URL="):
                    value = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if value:
                        print(f"✓ Found PGVECTOR_DB_URL in .env")
                        # Set it as environment variable
                        os.environ["PGVECTOR_DB_URL"] = value
                        print("✓ Set as environment variable")
                        break
    else:
        print(f"✗ .env file not found: {env_file}")
        print("\nPlease set PGVECTOR_DB_URL environment variable or add it to .env file")
        sys.exit(1)
else:
    print("✓ PGVECTOR_DB_URL found")
    # Check if password is missing
    if "@" in pg_url:
        parts = pg_url.split("@")
        if len(parts) == 2:
            user_part = parts[0]
            # Check if password is in connection string
            if ":" in user_part:
                user_pass = user_part.split("://")[-1] if "://" in user_part else user_part
                if ":" in user_pass:
                    user, pwd = user_pass.rsplit(":", 1)
                    if not pwd or pwd == "":
                        print("⚠️  Warning: Password appears to be empty in connection string")
                    else:
                        print("✓ Password found in connection string")
                else:
                    print("⚠️  Warning: No password separator found")
            else:
                print("⚠️  Warning: Connection string format may be incorrect")
        else:
            print("⚠️  Warning: Connection string format may be incorrect")
    else:
        print("⚠️  Warning: No @ symbol found in connection string")

print()
print("=" * 80)
print("Running RBG Processing...")
print("=" * 80)
print()

# Now run the processing
from scripts.run_rbg_processing_direct import main
main()

