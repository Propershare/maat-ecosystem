#!/bin/bash
# Complete Docling installation and re-extraction

set -e  # Exit on error

cd /home/suspect/.n8n/maatlangchain

echo "=========================================="
echo "DOCLING INTEGRATION - COMPLETE RUN"
echo "=========================================="
echo ""

# Step 1: Install Docling
echo "Step 1: Installing Docling..."
pip install docling || {
    echo "⚠️  pip install failed, trying python3 -m pip..."
    python3 -m pip install docling
}

echo ""
echo "Step 2: Testing Docling extraction..."
python3 install_and_test_docling.py

echo ""
read -p "Test successful? Continue with full re-extraction? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Step 3: Re-extracting all 87 files..."
    python3 enhanced_re_extract.py
    
    echo ""
    echo "=========================================="
    echo "RE-EXTRACTION COMPLETE!"
    echo "=========================================="
    echo ""
    echo "Check results in: re_extracted_files/"
    echo "Review summary: re_extraction_results.json"
else
    echo "Skipping full re-extraction."
fi

