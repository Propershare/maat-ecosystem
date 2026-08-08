# Fix Docling Installation Permission Error

## Problem
Installation failed with:
```
ERROR: Could not install packages due to an OSError: [Errno 13] Permission denied
```

## Solution

Install Docling to user site-packages (avoids permission issues):

```bash
cd /home/suspect/.n8n/maatlangchain
python3 install_docling_user.py
```

Or manually:
```bash
pip install --user docling
```

## What Changed

1. **Updated `document_processor.py`** - Now checks user site-packages if Docling not found in regular path
2. **Created `install_docling_user.py`** - Installs with `--user` flag automatically

## After Installation

Run the test:
```bash
python3 install_and_test_docling.py
```

Then re-extract:
```bash
python3 enhanced_re_extract.py
```

## Why This Works

- `--user` flag installs to `~/.local/lib/python3.12/site-packages/`
- No permission issues (user owns their home directory)
- DocumentProcessor automatically finds it in user site-packages

