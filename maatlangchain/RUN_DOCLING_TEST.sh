#!/bin/bash
# Run Docling installation and test

cd /home/suspect/.n8n/maatlangchain

echo "Installing Docling..."
python3 -m pip install docling

echo ""
echo "Running Docling test..."
python3 install_and_test_docling.py

