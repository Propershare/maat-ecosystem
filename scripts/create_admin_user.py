#!/usr/bin/env python3
"""Quick script to create admin user directly in database - bypasses signup issues"""

import sys
import os
from pathlib import Path

# Use venv's Python and add backend to path
venv_python = Path(__file__).parent.parent / "open-webui-venv" / "bin" / "python3"
if venv_python.exists():
    # If running with venv python, we're good
    pass

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "open-webui" / "backend"))

# Set PYTHONPATH
os.environ["PYTHONPATH"] = str(Path(__file__).parent.parent / "open-webui" / "backend")

from open_webui.utils.auth import get_password_hash
from open_webui.models.users import Users
from open_webui.internal.db import get_db
from open_webui.models.users import User

def create_admin():
    """Create admin user directly in database"""
    email = "propershare@gmail.com"
    name = "Imhotep"
    password = "Imhotep123!"  # Will be truncated to 72 bytes by get_password_hash
    
    # Check if user already exists
    existing = Users.get_user_by_email(email)
    if existing:
        print(f"❌ User {email} already exists!")
        return False
    
    # Hash password (get_password_hash handles truncation)
    hashed = get_password_hash(password)
    
    # Create user directly in database
    with get_db() as db:
        user = User(
            email=email.lower(),
            password_hash=hashed,
            name=name,
            role="admin"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print(f"✅ Admin user created successfully!")
        print(f"   Email: {email}")
        print(f"   Name: {name}")
        print(f"   Role: admin")
        print(f"   ID: {user.id}")
        return True

if __name__ == "__main__":
    create_admin()

