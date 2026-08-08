#!/usr/bin/env python3
"""
Remove 'extracted_' prefix from all files in extracted_files_review folder
"""

import os
from pathlib import Path

# Setup paths
maatlangchain_root = Path(__file__).parent
review_folder = maatlangchain_root / "extracted_files_review"

if not review_folder.exists():
    print(f"Error: Folder {review_folder} does not exist!")
    print("Please run RUN_ORGANIZE.py first to organize the files.")
    exit(1)

# Find all files in the review folder
files = list(review_folder.glob("extracted_*"))

if not files:
    print(f"No files with 'extracted_' prefix found in {review_folder}")
    exit(0)

print(f"Found {len(files)} files with 'extracted_' prefix")
print(f"Removing prefix from files in: {review_folder}")
print()

renamed_count = 0
errors = []

for file_path in files:
    try:
        # Skip if it's a directory
        if file_path.is_dir():
            continue
        
        # Get the filename
        filename = file_path.name
        
        # Check if it starts with 'extracted_'
        if not filename.startswith("extracted_"):
            continue
        
        # Remove the prefix
        new_filename = filename.replace("extracted_", "", 1)  # Only replace first occurrence
        
        # Skip if new name would be empty
        if not new_filename:
            errors.append((filename, "New filename would be empty"))
            continue
        
        # New path
        new_path = review_folder / new_filename
        
        # Check if target already exists
        if new_path.exists():
            errors.append((filename, f"Target file already exists: {new_filename}"))
            continue
        
        # Rename the file
        file_path.rename(new_path)
        renamed_count += 1
        
        if renamed_count % 50 == 0:
            print(f"  Renamed {renamed_count} files...")
            
    except Exception as e:
        errors.append((str(file_path), str(e)))

print()
print("=" * 60)
print(f"SUMMARY")
print("=" * 60)
print(f"Total files found: {len(files)}")
print(f"Successfully renamed: {renamed_count}")
print(f"Errors: {len(errors)}")
print()

if errors:
    print("Errors encountered:")
    for file_path, error in errors[:20]:  # Show first 20 errors
        print(f"  {file_path}: {error}")
    if len(errors) > 20:
        print(f"  ... and {len(errors) - 20} more errors")

print()
print(f"✓ Prefix removed from {renamed_count} files in {review_folder}")

