#!/usr/bin/env python3
"""
Push Maat Memory Scripts to All Laptops Automatically
Super simple - just run it!
"""

import subprocess
import socket
import sys
from pathlib import Path

# Configuration
USERNAME = "suspect"
SCRIPTS = ["setup_maat_memory.py", "verify_sync.py"]
LAPTOPS = ["imhotep", "macdaddy", "imhotepjr"]

def load_ips():
    """Load IPs from config file or try to find them."""
    config_file = Path(__file__).parent / "laptop_ips.txt"
    ips = {}
    
    # Try to load from config file
    if config_file.exists():
        with open(config_file, 'r') as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    name, ip = line.split('=', 1)
                    name = name.strip()
                    ip = ip.strip()
                    if ip:
                        ips[name] = ip
    
    # Try to find by hostname
    for laptop in LAPTOPS:
        if laptop not in ips:
            try:
                ip = socket.gethostbyname(laptop)
                ips[laptop] = ip
                print(f"✅ Found {laptop} at {ip} (via hostname)")
            except:
                pass
    
    return ips

def push_scripts():
    """Push scripts to all laptops."""
    project_root = Path(__file__).parent.parent
    scripts_dir = project_root / "scripts"
    
    print("="*60)
    print("🚀 Pushing Maat Memory Scripts to All Laptops")
    print("="*60)
    print()
    
    # Load IPs
    laptops = load_ips()
    
    # Show what we found
    if laptops:
        print("📱 Found laptops:")
        for name, ip in laptops.items():
            print(f"   {name}: {ip}")
        print()
    else:
        print("⚠️  No laptop IPs found!")
        print()
        print("Please edit: scripts/laptop_ips.txt")
        print("Add IPs like:")
        print("  imhotep=192.168.4.22")
        print("  macdaddy=192.168.4.23")
        print("  imhotepjr=192.168.4.24")
        print()
        return
    
    # Copy scripts
    success_count = 0
    for laptop_name, laptop_ip in laptops.items():
        print(f"📤 Copying to {laptop_name} ({laptop_ip})...")
        
        for script in SCRIPTS:
            script_path = scripts_dir / script
            if not script_path.exists():
                print(f"   ❌ {script} not found!")
                continue
            
            dest = f"{USERNAME}@{laptop_ip}:/home/{USERNAME}/.n8n/maatlangchain/scripts/"
            
            try:
                # Allow password prompts by not capturing output
                result = subprocess.run(
                    ["scp", "-o", "ConnectTimeout=10", "-o", "StrictHostKeyChecking=no",
                     str(script_path), dest],
                    timeout=30
                )
                
                if result.returncode == 0:
                    print(f"   ✅ {script}")
                else:
                    print(f"   ❌ {script} - Failed (check password/connection)")
            except subprocess.TimeoutExpired:
                print(f"   ❌ {script} - Connection timeout")
            except Exception as e:
                print(f"   ❌ {script} - {str(e)[:50]}")
        
        # Make executable
        try:
            subprocess.run(
                ["ssh", "-o", "ConnectTimeout=10", "-o", "StrictHostKeyChecking=no",
                 f"{USERNAME}@{laptop_ip}", 
                 "chmod +x /home/suspect/.n8n/maatlangchain/scripts/*.py 2>/dev/null"],
                timeout=15
            )
            print(f"   ✅ Made scripts executable")
        except:
            print(f"   ⚠️  Could not make scripts executable (run manually if needed)")
        
        success_count += 1
        print()
    
    print("="*60)
    if success_count > 0:
        print(f"✅ Scripts pushed to {len(laptops)} laptop(s)!")
        print()
        print("📋 Next steps on each laptop:")
        print("   python3 /home/suspect/.n8n/maatlangchain/scripts/setup_maat_memory.py")
        print()
        print("💡 Use the SAME database URL on all laptops for sync!")
    else:
        print("❌ No laptops updated. Check IPs in scripts/laptop_ips.txt")
    print("="*60)

if __name__ == "__main__":
    push_scripts()
