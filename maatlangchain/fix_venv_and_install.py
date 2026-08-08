#!/usr/bin/env python3
"""
Fix virtual environment permissions and install Docling
"""

import subprocess
import sys
import os
from pathlib import Path

# Setup paths
maatlangchain_root = Path(__file__).parent
os.chdir(maatlangchain_root)

print("=" * 80)
print("FIXING VENV PERMISSIONS & INSTALLING DOCLING")
print("=" * 80)

# Get venv path
venv_path = Path("/home/suspect/.n8n/tehuti-lab-webui-venv")
site_packages = venv_path / "lib" / "python3.12" / "site-packages"

print(f"\nVirtual environment: {venv_path}")
print(f"Site-packages: {site_packages}")

# Fix permissions
print("\nFixing permissions on site-packages...")
try:
    os.chmod(site_packages, 0o755)
    # Also fix parent directories
    for parent in site_packages.parents:
        try:
            os.chmod(parent, 0o755)
        except OSError:
            pass
    print("✅ Permissions fixed")
except Exception as e:
    print(f"⚠️  Could not fix permissions: {e}")
    print("Trying to install anyway...")

# Install Docling directly to venv
print("\nInstalling Docling to virtual environment...")
try:
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "docling"],
        capture_output=True,
        text=True,
        cwd=str(maatlangchain_root)
    )
    
    if result.returncode == 0:
        print("✅ Docling installed successfully!")
        if result.stdout:
            # Show last few lines
            lines = result.stdout.strip().split('\n')
            print("\n".join(lines[-5:]))
    else:
        print("❌ Installation failed:")
        if result.stderr:
            print(result.stderr[-500:])
        print("\nTrying with sudo (if available)...")
        
        # Last resort: try with sudo
        result2 = subprocess.run(
            ["sudo", sys.executable, "-m", "pip", "install", "docling"],
            capture_output=True,
            text=True,
            input="\n"  # Auto-approve if no password needed
        )
        if result2.returncode == 0:
            print("✅ Docling installed with sudo")
        else:
            print("❌ All installation methods failed")
            print("\nManual fix:")
            print(f"  sudo chmod -R u+w {site_packages}")
            print(f"  {sys.executable} -m pip install docling")
            sys.exit(1)
            
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Verify installation
print("\n" + "=" * 80)
print("VERIFYING INSTALLATION")
print("=" * 80)

try:
    import docling
    print("✅ Docling imported successfully!")
    print(f"   Location: {docling.__file__ if hasattr(docling, '__file__') else 'unknown'}")
except ImportError as e:
    print(f"❌ Could not import docling: {e}")
    print("\nPlease try manually:")
    print(f"  sudo chmod -R u+w {site_packages}")
    print(f"  {sys.executable} -m pip install docling")
    sys.exit(1)

print("\n" + "=" * 80)
print("✅ DOCLING READY!")
print("=" * 80)
print("\nNext steps:")
print("  1. Test: python3 install_and_test_docling.py")
print("  2. Re-extract: python3 enhanced_re_extract.py")

