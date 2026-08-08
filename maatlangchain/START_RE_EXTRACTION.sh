#!/bin/bash
# Start full re-extraction with Docling

cd /home/suspect/.n8n/maatlangchain

echo "=========================================="
echo "STARTING FULL RE-EXTRACTION WITH DOCLING"
echo "=========================================="
echo ""
echo "This will process 87 files with source PDFs"
echo "Estimated time: 3-5 hours (3-4 min per file)"
echo ""
echo "Starting now..."
echo ""

python3 enhanced_re_extract.py

echo ""
echo "=========================================="
echo "RE-EXTRACTION COMPLETE!"
echo "=========================================="
echo ""
echo "Check results in: re_extracted_files/"
echo "Review summary: re_extraction_results.json"

