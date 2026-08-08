#!/usr/bin/env python3
"""Run RBG processing with improved database connection handling"""

import os
import sys
from pathlib import Path

# Change to maatlangchain root
os.chdir(Path(__file__).parent)
sys.path.insert(0, str(Path(__file__).parent))

# Try to load .env file first
env_file = Path("/home/suspect/.n8n/tehuti-lab-webui/.env")
if env_file.exists():
    with open(env_file, 'r') as f:
        for line in f:
            if line.startswith("PGVECTOR_DB_URL=") or line.startswith("PGVECTOR_DB_URL ="):
                value = line.split("=", 1)[1].strip().strip('"').strip("'")
                if value:
                    os.environ["PGVECTOR_DB_URL"] = value
                    break

# Import and execute main
from scripts.run_rbg_processing_direct import main

if __name__ == "__main__":
    main()

