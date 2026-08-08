#!/usr/bin/env python3
"""
Install Docling to user site-packages (avoids permission issues)
"""

import subprocess
import sys
import os
from pathlib import Path

# Setup paths
maatlangchain_root = Path(__file__).parent
os.chdir(maatlangchain_root)

print("=" * 80)
print("INSTALLING DOCLING (USER MODE)")
print("=" * 80)

# Install to user site-packages to avoid permission issues
try:
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "--user", "docling"],
        capture_output=True,
        text=True,
        cwd=str(maatlangchain_root)
    )
    
    if result.returncode == 0:
        print("✅ Docling installed successfully to user site-packages!")
        print(result.stdout[-300:] if result.stdout else "")
    else:
        print("⚠️  Installation had issues:")
        print(result.stderr[-500:] if result.stderr else "")
        print("\nTrying alternative method...")
        
        # Try with --break-system-packages if on newer Python
        result2 = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--user", "--break-system-packages", "docling"],
            capture_output=True,
            text=True
        )
        if result2.returncode == 0:
            print("✅ Docling installed with --break-system-packages flag")
        else:
            print("❌ Installation failed. Please install manually:")
            print("   pip install --user docling")
            sys.exit(1)
            
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nPlease install manually:")
    print("   pip install --user docling")
    sys.exit(1)

# Verify installation
print("\n" + "=" * 80)
print("VERIFYING INSTALLATION")
print("=" * 80)

try:
    import docling
    print("✅ Docling imported successfully!")
    print(f"   Version: {docling.__version__ if hasattr(docling, '__version__') else 'unknown'}")
except ImportError as e:
    print(f"⚠️  Could not import docling: {e}")
    print("\nYou may need to add user site-packages to PYTHONPATH:")
    import site
    user_site = site.getusersitepackages()
    print(f"   export PYTHONPATH={user_site}:$PYTHONPATH")
    print("\nOr restart your Python session after installation.")

print("\n" + "=" * 80)
print("NEXT STEP: Run test script")
print("=" * 80)
print("python3 install_and_test_docling.py")

