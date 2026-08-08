#!/bin/bash
# Test Docling, then run full re-extraction

cd /home/suspect/.n8n/maatlangchain

echo "Step 1: Testing Docling extraction..."
python3 install_and_test_docling.py

echo ""
echo "Step 2: Running full re-extraction of 87 files..."
python3 enhanced_re_extract.py

echo ""
echo "Done! Check results in: re_extracted_files/"

