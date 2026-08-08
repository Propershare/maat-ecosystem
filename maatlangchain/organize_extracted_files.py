#!/usr/bin/env python3
"""
Organize all extracted_* files into a single folder for review
"""

import os
import shutil
from pathlib import Path

# Setup paths
maatlangchain_root = Path(__file__).parent
review_folder = maatlangchain_root / "extracted_files_review"
review_folder.mkdir(exist_ok=True)

# Find all extracted_* files
extracted_files = list(maatlangchain_root.glob("extracted_*"))

print(f"Found {len(extracted_files)} files with 'extracted_' prefix")
print(f"Moving to: {review_folder}")
print()

moved_count = 0
errors = []

for file_path in extracted_files:
    try:
        # Skip if it's a directory
        if file_path.is_dir():
            continue
        
        # Get just the filename
        filename = file_path.name
        
        # Destination path
        dest_path = review_folder / filename
        
        # Move the file
        shutil.move(str(file_path), str(dest_path))
        moved_count += 1
        
        if moved_count % 50 == 0:
            print(f"  Moved {moved_count} files...")
            
    except Exception as e:
        errors.append((str(file_path), str(e)))

print()
print("=" * 60)
print(f"SUMMARY")
print("=" * 60)
print(f"Total files found: {len(extracted_files)}")
print(f"Successfully moved: {moved_count}")
print(f"Errors: {len(errors)}")
print(f"Review folder: {review_folder}")
print()

if errors:
    print("Errors encountered:")
    for file_path, error in errors[:10]:  # Show first 10 errors
        print(f"  {file_path}: {error}")
    if len(errors) > 10:
        print(f"  ... and {len(errors) - 10} more errors")

print()
print("All extracted files are now in:", review_folder)

