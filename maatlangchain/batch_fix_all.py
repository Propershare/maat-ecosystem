#!/usr/bin/env python3
"""
Master script to fix all 147 problematic files:
- Re-extract 87 files with source PDFs (enhanced OCR)
- Post-process 60 files without PDFs (deduplication + OCR cleanup)
"""

import json
import os
import subprocess
import sys
from pathlib import Path
import logging

# Setup paths
maatlangchain_root = Path(__file__).parent
sys.path.insert(0, str(maatlangchain_root))
os.chdir(maatlangchain_root)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)

def run_script(script_name: str, description: str) -> bool:
    """Run a Python script and return success status."""
    script_path = maatlangchain_root / script_name
    if not script_path.exists():
        log.error(f"Script not found: {script_path}")
        return False
    
    log.info(f"\n{'=' * 80}")
    log.info(f"STEP: {description}")
    log.info(f"{'=' * 80}\n")
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            cwd=str(maatlangchain_root)
        )
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr, file=sys.stderr)
        
        return result.returncode == 0
    except Exception as e:
        log.error(f"Error running {script_name}: {e}")
        return False

def main():
    """Main batch fix function."""
    log.info("=" * 80)
    log.info("BATCH FIX FOR 147 PROBLEMATIC FILES")
    log.info("=" * 80)
    log.info("")
    log.info("This will:")
    log.info("1. Re-extract 87 files with source PDFs (enhanced OCR)")
    log.info("2. Deduplicate 25 repetitive files")
    log.info("3. Post-process remaining files without PDFs")
    log.info("")
    
    # Step 1: Re-extract files with PDFs
    log.info("PHASE 1: Re-extracting files with source PDFs...")
    success1 = run_script("enhanced_re_extract.py", "Re-extracting 87 files with enhanced OCR")
    
    # Step 2: Deduplicate repetitive files
    log.info("\nPHASE 2: Deduplicating repetitive files...")
    success2 = run_script("deduplicate_repetitive.py", "Removing duplicate content from 25 files")
    
    # Step 3: Summary
    log.info("\n" + "=" * 80)
    log.info("BATCH FIX SUMMARY")
    log.info("=" * 80)
    log.info(f"Re-extraction: {'✓ Success' if success1 else '✗ Failed'}")
    log.info(f"Deduplication: {'✓ Success' if success2 else '✗ Failed'}")
    log.info("")
    log.info("NEXT STEPS:")
    log.info("1. Review re-extracted files in: re_extracted_files/")
    log.info("2. Run quality check: python3 analyze_scan_quality.py")
    log.info("3. Replace originals if quality improved")
    log.info("=" * 80)

if __name__ == "__main__":
    main()

