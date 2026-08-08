#!/usr/bin/env python3
"""
Maat Audit: Diagnose Tool Loading Issue
Trace through the entire tool loading flow to find where tools are lost
"""

import json
import requests
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "tehuti-lab-webui" / "backend"
sys.path.insert(0, str(backend_path))

print("=" * 80)
print("MAAT AUDIT: Tool Loading Diagnosis")
print("=" * 80)

# Step 1: Check OpenAPI endpoint
print("\n[STEP 1] Checking OpenAPI Endpoint")
print("-" * 80)
try:
    resp = requests.get('http://127.0.0.1:8014/openapi.json', timeout=5)
    spec = resp.json()
    paths = spec.get('paths', {})
    print(f"✓ OpenAPI endpoint accessible")
    print(f"✓ Total paths in OpenAPI spec: {len(paths)}")
    
    operation_ids = []
    for path, methods in paths.items():
        for method, op in methods.items():
            if isinstance(op, dict) and op.get('operationId'):
                operation_ids.append(op['operationId'])
    
    print(f"✓ Total operationIds: {len(operation_ids)}")
    print(f"\nOperationIds:")
    for i, op_id in enumerate(sorted(operation_ids), 1):
        print(f"  {i:2d}. {op_id}")
        
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

# Step 2: Check Redis cache
print("\n[STEP 2] Checking Redis Cache")
print("-" * 80)
try:
    import redis
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=False)
    cached = r.get('tool_servers')
    
    if cached:
        data = json.loads(cached)
        tc = [s for s in data if isinstance(s, dict) and s.get('id') == 'tehuti-core']
        if tc:
            specs = tc[0].get('specs', [])
            print(f"✓ Cache exists")
            print(f"✓ tehuti-core in cache: YES")
            print(f"✓ Number of specs in cache: {len(specs)}")
            print(f"\nCached tool names (first 10):")
            for i, spec in enumerate(specs[:10], 1):
                print(f"  {i:2d}. {spec.get('name', 'NO NAME')}")
        else:
            print(f"✓ Cache exists but tehuti-core not found")
    else:
        print(f"✓ No cache (cache is empty)")
except Exception as e:
    print(f"⚠ Redis not accessible or error: {e}")

# Step 3: Simulate conversion
print("\n[STEP 3] Simulating OpenAPI to Tool Conversion")
print("-" * 80)
try:
    # Simple conversion simulation (without full imports)
    tool_payload = []
    for path, methods in paths.items():
        for method, operation in methods.items():
            if operation.get("operationId"):
                tool_payload.append({
                    "name": operation.get("operationId"),
                    "description": operation.get("description", operation.get("summary", "")),
                })
    
    print(f"✓ Conversion simulation: {len(tool_payload)} tools")
    print(f"\nConverted tool names (first 10):")
    for i, tool in enumerate(tool_payload[:10], 1):
        print(f"  {i:2d}. {tool['name']}")
        
except Exception as e:
    print(f"✗ Error: {e}")

# Step 4: Simulate name stripping
print("\n[STEP 4] Simulating Name Stripping Logic")
print("-" * 80)
server_id = "tehuti-core"
server_id_underscore = server_id.replace("-", "_")

stripped_names = []
for op_id in operation_ids:
    if op_id.startswith("tool_") and op_id.endswith("_post"):
        native_name = op_id[5:-5]
        if native_name.startswith(server_id_underscore + "_"):
            native_name = native_name[len(server_id_underscore) + 1:]
        stripped_names.append(native_name)
    else:
        stripped_names.append(op_id)

print(f"✓ After stripping: {len(stripped_names)} tool names")
print(f"\nStripped tool names (first 10):")
for i, name in enumerate(stripped_names[:10], 1):
    print(f"  {i:2d}. {name}")

# Step 5: Check for collisions
print("\n[STEP 5] Checking for Name Collisions")
print("-" * 80)
from collections import Counter
name_counts = Counter(stripped_names)
collisions = {name: count for name, count in name_counts.items() if count > 1}

if collisions:
    print(f"⚠ Found {len(collisions)} name collisions:")
    for name, count in collisions.items():
        print(f"  - {name}: appears {count} times")
else:
    print(f"✓ No name collisions")

# Step 6: Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"OpenAPI paths: {len(paths)}")
print(f"OperationIds: {len(operation_ids)}")
print(f"After conversion: {len(tool_payload) if 'tool_payload' in locals() else 'N/A'}")
print(f"After stripping: {len(stripped_names)}")
print(f"Collisions: {len(collisions) if collisions else 0}")
print("\nExpected: 18 tools")
print("Actual showing: 6 tools")
print("\nPossible causes:")
print("  1. Only 6 tools enabled in UI (check tool_ids in request)")
print("  2. Filtering applied (check function_name_filter_list)")
print("  3. Tools not being loaded (check get_tool_servers response)")
print("  4. Tools overwritten by collisions (unlikely - no collisions found)")

