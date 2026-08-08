# Quick Fix for Docling Installation

## Problem
Virtual environments don't allow `--user` installs, and regular install has permission errors.

## Solution

**Option 1: Fix permissions and install (Recommended)**
```bash
cd /home/suspect/.n8n/maatlangchain
python3 fix_venv_and_install.py
```

**Option 2: Manual fix**
```bash
# Fix permissions
sudo chmod -R u+w /home/suspect/.n8n/tehuti-lab-webui-venv/lib/python3.12/site-packages/

# Install Docling
pip install docling
```

**Option 3: If you own the venv directory**
```bash
# Make sure you own the venv
sudo chown -R $USER:$USER /home/suspect/.n8n/tehuti-lab-webui-venv/

# Then install
pip install docling
```

## After Installation

Test it:
```bash
python3 install_and_test_docling.py
```

Then re-extract:
```bash
python3 enhanced_re_extract.py
```

