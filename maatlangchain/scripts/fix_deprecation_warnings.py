#!/usr/bin/env python3
"""
Fix LangChain deprecation warnings in MaatLangChain codebase.

This script updates deprecated imports to use the new LangChain packages.
"""

import os
import re
import sys
from pathlib import Path

# Get the maatlangchain root directory
MAATLANGCHAIN_ROOT = Path(__file__).parent.parent

# Files to fix
FILES_TO_FIX = [
    'core/chains/document_processor.py',
    'core/integrations/tehuti_lab.py',
    'core/chains/maat_rag.py',
]

# Fix patterns: (pattern, replacement, description)
FIXES = [
    # Document loaders
    (
        r'from langchain\.document_loaders import',
        'from langchain_community.document_loaders import',
        'Update document loaders import'
    ),
    # Embeddings - prefer langchain_huggingface
    (
        r'from langchain\.embeddings import HuggingFaceEmbeddings',
        'from langchain_huggingface import HuggingFaceEmbeddings',
        'Update HuggingFaceEmbeddings import (langchain.embeddings)'
    ),
    (
        r'from langchain_community\.embeddings import HuggingFaceEmbeddings',
        'from langchain_huggingface import HuggingFaceEmbeddings',
        'Update HuggingFaceEmbeddings import (langchain_community.embeddings)'
    ),
    # Ollama LLM
    (
        r'from langchain_community\.llms import Ollama',
        'from langchain_ollama import OllamaLLM',
        'Update Ollama import'
    ),
    (
        r'\bOllama\(',
        'OllamaLLM(',
        'Update Ollama() calls to OllamaLLM()'
    ),
]


def fix_file(filepath: Path, dry_run: bool = False) -> bool:
    """Fix deprecation warnings in a single file."""
    if not filepath.exists():
        print(f"❌ File not found: {filepath}")
        return False
    
    print(f"\n📄 Processing: {filepath}")
    
    # Read file
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"   ❌ Error reading file: {e}")
        return False
    
    original_content = content
    changes_made = []
    
    # Apply fixes
    for pattern, replacement, description in FIXES:
        matches = re.findall(pattern, content)
        if matches:
            content = re.sub(pattern, replacement, content)
            changes_made.append(f"   ✅ {description}: {len(matches)} occurrence(s)")
    
    # Write back if changes were made
    if content != original_content:
        if not dry_run:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"   ✅ File updated successfully")
                for change in changes_made:
                    print(change)
                return True
            except Exception as e:
                print(f"   ❌ Error writing file: {e}")
                return False
        else:
            print(f"   🔍 DRY RUN - Would update:")
            for change in changes_made:
                print(change)
            return True
    else:
        print(f"   ℹ️  No changes needed")
        return False


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Fix LangChain deprecation warnings'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without making changes'
    )
    parser.add_argument(
        '--file',
        type=str,
        help='Fix a specific file (relative to maatlangchain root)'
    )
    args = parser.parse_args()
    
    # Change to maatlangchain root
    os.chdir(MAATLANGCHAIN_ROOT)
    
    print(f"🔧 Fixing LangChain deprecation warnings")
    print(f"📁 Working directory: {MAATLANGCHAIN_ROOT}")
    if args.dry_run:
        print("🔍 DRY RUN MODE - No files will be modified")
    print()
    
    # Determine files to process
    if args.file:
        files_to_process = [Path(args.file)]
    else:
        files_to_process = [MAATLANGCHAIN_ROOT / f for f in FILES_TO_FIX]
    
    # Process files
    fixed_count = 0
    for filepath in files_to_process:
        if fix_file(filepath, dry_run=args.dry_run):
            fixed_count += 1
    
    # Summary
    print(f"\n{'='*60}")
    if args.dry_run:
        print(f"🔍 DRY RUN: Would fix {fixed_count} file(s)")
        print("Run without --dry-run to apply changes")
    else:
        print(f"✅ Fixed {fixed_count} file(s)")
    
    # Check if packages need to be installed
    print("\n📦 Required packages:")
    print("   pip install langchain-ollama langchain-huggingface")
    
    return 0 if fixed_count > 0 or args.dry_run else 1


if __name__ == '__main__':
    sys.exit(main())

