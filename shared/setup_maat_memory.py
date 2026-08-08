#!/usr/bin/env python3
"""
Maat Memory Setup Script - Onboard Laptops to Unified PostgreSQL Memory

This script helps set up Maat Memory with PostgreSQL backend for cross-machine sync.
"""

import os
import sys
from pathlib import Path
import subprocess
import json

# Colors for output
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
RESET = "\033[0m"


def print_header(text):
    """Print formatted header."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text:^60}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")


def print_success(text):
    print(f"{GREEN}✅ {text}{RESET}")


def print_warning(text):
    print(f"{YELLOW}⚠️  {text}{RESET}")


def print_error(text):
    print(f"{RED}❌ {text}{RESET}")


def print_info(text):
    print(f"{BLUE}ℹ️  {text}{RESET}")


def check_dependencies():
    """Check if required dependencies are installed."""
    print_header("Checking Dependencies")
    
    required = {
        "psycopg2": "psycopg2-binary",
        "pgvector": "pgvector",
        "langchain_huggingface": "langchain-huggingface",
    }
    
    missing = []
    for module, package in required.items():
        try:
            __import__(module)
            print_success(f"{package} is installed")
        except ImportError:
            print_warning(f"{package} is missing")
            missing.append(package)
    
    if missing:
        print_info("Installing missing dependencies...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
            print_success("Dependencies installed")
        except subprocess.CalledProcessError:
            print_error("Failed to install dependencies")
            print_info(f"Please install manually: pip install {' '.join(missing)}")
            return False
    
    return True


def get_current_db_url():
    """Get current PGVECTOR_DB_URL from environment."""
    return os.environ.get("PGVECTOR_DB_URL")


def configure_database_url():
    """Configure PostgreSQL database URL."""
    print_header("Database Configuration")
    
    current = get_current_db_url()
    if current:
        print_success(f"Current PGVECTOR_DB_URL is set")
        print_info(f"URL: {current[:50]}..." if len(current) > 50 else f"URL: {current}")
        
        use_current = input("\nUse this database URL? (y/n): ").lower().strip()
        if use_current == 'y':
            return current
    
    print_info("Enter PostgreSQL connection details:")
    print_info("Format: postgresql://user:password@host:port/database")
    
    host = input("Database host [localhost]: ").strip() or "localhost"
    port = input("Database port [5434]: ").strip() or "5434"
    database = input("Database name [n8n_ai_starter]: ").strip() or "n8n_ai_starter"
    user = input("Database user [suspect]: ").strip() or "suspect"
    password = input("Database password: ").strip()
    
    if not password:
        print_warning("Password is required")
        return None
    
    db_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
    
    # Test connection
    print_info("Testing connection...")
    if test_connection(db_url):
        print_success("Connection successful!")
        
        # Save to environment
        save_to_env = input("\nSave to ~/.bashrc? (y/n): ").lower().strip()
        if save_to_env == 'y':
            save_env_var("PGVECTOR_DB_URL", db_url)
        
        return db_url
    else:
        print_error("Connection failed. Please check your credentials.")
        return None


def test_connection(db_url=None):
    """Test PostgreSQL connection."""
    if not db_url:
        db_url = get_current_db_url()
    
    if not db_url:
        return False
    
    try:
        import psycopg2
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # Check pgvector extension
        cur.execute("SELECT extname FROM pg_extension WHERE extname = 'vector';")
        has_pgvector = cur.fetchone() is not None
        
        if not has_pgvector:
            print_warning("pgvector extension not found. Creating...")
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            conn.commit()
            print_success("pgvector extension created")
        
        conn.close()
        return True
    except Exception as e:
        print_error(f"Connection test failed: {e}")
        return False


def save_env_var(name, value):
    """Save environment variable to ~/.bashrc."""
    bashrc = Path.home() / ".bashrc"
    
    # Check if already exists
    if bashrc.exists():
        with open(bashrc, 'r') as f:
            content = f.read()
            if f"export {name}=" in content:
                print_warning(f"{name} already exists in ~/.bashrc")
                return
    
    # Append to bashrc
    with open(bashrc, 'a') as f:
        f.write(f"\n# Maat Memory Configuration\n")
        f.write(f"export {name}='{value}'\n")
    
    print_success(f"Saved {name} to ~/.bashrc")
    print_info("Run: source ~/.bashrc or restart terminal")


def check_existing_json():
    """Check for existing maat_memory.json files."""
    print_header("Checking for Existing Data")
    
    json_paths = [
        Path("/home/suspect/.n8n/.maat_memory/maat_memory.json"),
        Path.home() / ".n8n" / ".maat_memory" / "maat_memory.json",
        Path.cwd() / "maat_memory.json",
    ]
    
    existing = []
    for path in json_paths:
        if path.exists():
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                    sessions = len(data.get("sessions", []))
                    conversations = len(data.get("conversations", []))
                    existing.append({
                        "path": str(path),
                        "sessions": sessions,
                        "conversations": conversations
                    })
            except:
                pass
    
    if existing:
        print_info(f"Found {len(existing)} existing JSON file(s):")
        for item in existing:
            print(f"  - {item['path']}")
            print(f"    Sessions: {item['sessions']}, Conversations: {item['conversations']}")
        
        migrate = input("\nMigrate existing data to PostgreSQL? (y/n): ").lower().strip()
        if migrate == 'y':
            return existing
    
    return []


def migrate_json_to_postgres(json_paths):
    """Migrate JSON data to PostgreSQL."""
    print_header("Migrating Data to PostgreSQL")
    
    # Set environment for migration
    db_url = get_current_db_url()
    if not db_url:
        print_error("PGVECTOR_DB_URL not set")
        return False
    
    os.environ["PGVECTOR_DB_URL"] = db_url
    
    # Add project root to path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    try:
        from maat_memory.migrate_to_postgres import main as migrate_main
        
        for json_path in json_paths:
            print_info(f"Migrating {json_path['path']}...")
            # Migration script will handle the actual migration
            # For now, we'll just indicate it should be run
            print_success(f"Migration queued for {json_path['path']}")
        
        print_info("Running migration...")
        # Actually run migration
        result = subprocess.run(
            [sys.executable, str(project_root / "maat_memory" / "migrate_to_postgres.py")],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print_success("Migration completed!")
            return True
        else:
            print_error(f"Migration failed: {result.stderr}")
            return False
            
    except Exception as e:
        print_error(f"Migration error: {e}")
        return False


def test_memory_system():
    """Test the memory system."""
    print_header("Testing Memory System")
    
    db_url = get_current_db_url()
    if not db_url:
        print_error("PGVECTOR_DB_URL not set")
        return False
    
    os.environ["PGVECTOR_DB_URL"] = db_url
    
    # Add project root to path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    try:
        from maat_memory import MaatMemory
        
        print_info("Initializing MaatMemory...")
        memory = MaatMemory()
        
        backend = memory.__class__.__name__
        print_success(f"Backend: {backend}")
        
        if "Postgres" in backend:
            print_success("Using PostgreSQL backend - cross-machine sync enabled!")
        else:
            print_warning("Using JSON backend - no cross-machine sync")
        
        # Test save
        print_info("Testing save operation...")
        session_id = memory.start_session("cursor", "setup-test-session")
        print_success(f"Session created: {session_id}")
        
        # Test retrieve
        print_info("Testing retrieve operation...")
        sessions = memory.get_sessions(agent="cursor", limit=1)
        if sessions:
            print_success(f"Retrieved {len(sessions)} session(s)")
        else:
            print_warning("No sessions found")
        
        return True
        
    except Exception as e:
        print_error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main setup function."""
    print_header("Maat Memory Setup - Cross-Machine Sync")
    print_info("This script will help you set up unified PostgreSQL memory")
    print_info("for cross-machine synchronization across all laptops.\n")
    
    # Step 1: Check dependencies
    if not check_dependencies():
        print_error("Please install dependencies and try again")
        sys.exit(1)
    
    # Step 2: Configure database
    db_url = configure_database_url()
    if not db_url:
        print_error("Database configuration failed")
        sys.exit(1)
    
    # Set environment for this session
    os.environ["PGVECTOR_DB_URL"] = db_url
    
    # Step 3: Check for existing data
    existing_json = check_existing_json()
    
    # Step 4: Migrate if needed
    if existing_json:
        migrate_json_to_postgres(existing_json)
    
    # Step 5: Test system
    if test_memory_system():
        print_header("Setup Complete!")
        print_success("Maat Memory is configured and working")
        print_info("All laptops using the same PGVECTOR_DB_URL will share memory")
        print_info("JSON files remain as local backup/fallback")
        print("\nNext steps:")
        print("1. Set PGVECTOR_DB_URL on other laptops to the same database")
        print("2. Run this script on each laptop")
        print("3. Verify: Save on one laptop, check on another")
    else:
        print_error("Setup incomplete - please check errors above")
        sys.exit(1)


if __name__ == "__main__":
    main()

