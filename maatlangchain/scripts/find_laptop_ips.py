#!/usr/bin/env python3
"""
Find IP addresses of laptops on the network
"""

import subprocess
import socket
from pathlib import Path

LAPTOPS = ["imhotep", "macdaddy", "imhotepjr"]

def find_ips():
    """Find IPs for all laptops."""
    print("🔍 Finding laptop IPs...")
    print()
    
    # Get current network
    try:
        result = subprocess.run(["hostname", "-I"], capture_output=True, text=True)
        current_ip = result.stdout.strip().split()[0]
        network_base = ".".join(current_ip.split(".")[:-1])
        print(f"Network: {network_base}.x")
        print(f"Current machine: {current_ip}")
        print()
    except:
        print("Could not determine network")
        return
    
    found = {}
    
    # Try hostnames
    print("Trying hostnames...")
    for laptop in LAPTOPS:
        try:
            ip = socket.gethostbyname(laptop)
            print(f"  ✅ {laptop}: {ip}")
            found[laptop] = ip
        except:
            print(f"  ❌ {laptop}: Not found")
    
    print()
    print("="*60)
    print("Found IPs:")
    print("="*60)
    
    if found:
        for laptop, ip in found.items():
            print(f"{laptop}={ip}")
        print()
        print("Copy these to scripts/laptop_ips.txt")
    else:
        print("No laptops found via hostname.")
        print()
        print("Try these common IPs on your network:")
        for i in [22, 23, 24, 25, 26]:
            ip = f"{network_base}.{i}"
            print(f"  {ip} - Test with: ping {ip}")

if __name__ == "__main__":
    find_ips()

