#!/usr/bin/env python3
"""
Safe Model Import Script for OpenWebUI

This script properly imports models into OpenWebUI database with:
- Valid JSON validation
- Proper timestamp handling
- Data type validation
- Error handling

Prevents the JSON corruption issues we've been experiencing.
"""

import sqlite3
import json
import sys
import time
from pathlib import Path


def validate_json(value, field_name):
    """Validate JSON and return cleaned value."""
    if value is None or value == '':
        return None
    
    if isinstance(value, str):
        try:
            # Try to parse as JSON
            parsed = json.loads(value)
            # Return as properly formatted JSON string
            return json.dumps(parsed)
        except json.JSONDecodeError as e:
            print(f"⚠️  {field_name}: Invalid JSON - {e}")
            print(f"   Raw value: {repr(value[:100])}")
            return None
    elif isinstance(value, dict):
        return json.dumps(value)
    else:
        return None


def validate_timestamp(value, field_name):
    """Validate timestamp and return integer."""
    if value is None or value == '':
        return int(time.time())
    
    if isinstance(value, int):
        return value
    
    if isinstance(value, str):
        # Try to parse as integer
        try:
            return int(value)
        except ValueError:
            print(f"⚠️  {field_name}: Invalid timestamp - {repr(value)}")
            return int(time.time())
    
    return int(time.time())


def import_model(db_path, model_data):
    """
    Safely import a model into OpenWebUI database.
    
    Args:
        db_path: Path to webui.db
        model_data: Dict with model fields (id, user_id, base_model_id, name, meta, params, etc.)
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    try:
        # Validate and clean all fields
        model_id = model_data.get('id')
        if not model_id:
            raise ValueError("Model ID is required")
        
        user_id = model_data.get('user_id')
        if not user_id:
            raise ValueError("User ID is required")
        
        name = model_data.get('name', 'Unnamed Model')
        base_model_id = model_data.get('base_model_id')
        
        # Validate JSON fields
        meta = validate_json(model_data.get('meta'), 'meta')
        params = validate_json(model_data.get('params'), 'params')
        access_control = validate_json(model_data.get('access_control'), 'access_control')
        
        # Validate timestamps
        created_at = validate_timestamp(model_data.get('created_at'), 'created_at')
        updated_at = validate_timestamp(model_data.get('updated_at'), 'updated_at')
        
        # Default values
        is_active = model_data.get('is_active', 1)
        if not isinstance(is_active, (int, bool)):
            is_active = 1
        
        # Insert or update
        cur.execute("""
            INSERT OR REPLACE INTO model 
            (id, user_id, base_model_id, name, meta, params, created_at, updated_at, access_control, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (model_id, user_id, base_model_id, name, meta, params, created_at, updated_at, access_control, is_active))
        
        conn.commit()
        
        # Verify
        cur.execute("SELECT id, name FROM model WHERE id = ?", (model_id,))
        result = cur.fetchone()
        
        if result:
            print(f"✅ Successfully imported: {result[1]} ({result[0]})")
            
            # Final validation
            cur.execute("SELECT meta, params, access_control FROM model WHERE id = ?", (model_id,))
            meta_val, params_val, ac_val = cur.fetchone()
            
            errors = []
            if meta_val:
                try:
                    json.loads(meta_val)
                except:
                    errors.append("meta")
            if params_val:
                try:
                    json.loads(params_val)
                except:
                    errors.append("params")
            if ac_val:
                try:
                    json.loads(ac_val)
                except:
                    errors.append("access_control")
            
            if errors:
                print(f"⚠️  Warning: Invalid JSON in fields: {', '.join(errors)}")
            else:
                print("✅ All JSON fields validated")
        else:
            print(f"❌ Failed to import model {model_id}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error importing model: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 fix_model_import.py <db_path>")
        print("Example: python3 fix_model_import.py /home/suspect/.n8n/open-webui/data/webui.db")
        sys.exit(1)
    
    db_path = sys.argv[1]
    
    if not Path(db_path).exists():
        print(f"❌ Database not found: {db_path}")
        sys.exit(1)
    
    # Example model data
    example_model = {
        "id": "test-model",
        "user_id": "b9937d92-97c1-42fb-90ea-ffa53f394a31",
        "base_model_id": "llama3.2:3b",
        "name": "Test Model",
        "meta": {"description": "Test"},
        "params": {"system": "You are a test model"},
        "created_at": int(time.time()),
        "updated_at": int(time.time()),
        "access_control": None,
        "is_active": 1
    }
    
    print("Safe Model Import Script")
    print("=" * 50)
    print(f"Database: {db_path}")
    print("\nThis script validates all fields before importing.")
    print("Use this when importing models to prevent JSON corruption.")
    print("\nExample usage in code:")
    print("  from fix_model_import import import_model")
    print("  import_model(db_path, model_data)")

