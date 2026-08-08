# RBG Library PDF Processing Guide

## Overview

The RBG library PDF processing system extracts content from PDFs and ingests them into the RAG system with automatic OCR detection.

## Features

- **Automatic PDF Type Detection**: Detects text-based vs scanned PDFs
- **OCR Support**: Uses DatalabMarkerLoader for scanned PDFs
- **Text Extraction**: Uses PyPDFLoader for text-based PDFs
- **Batch Processing**: Process all PDFs in RBG library
- **Monitoring Output**: Detailed results saved for testing

## Tools Used

### 1. PyPDFLoader (Text PDFs)
- **Best for**: PDFs with native text
- **Fast**: Direct text extraction
- **No API required**: Works offline

### 2. DatalabMarkerLoader (Scanned PDFs)
- **Best for**: Scanned PDFs, images, complex layouts
- **Features**: OCR, table extraction, image extraction
- **Requires**: Datalab Marker API key

## Setup

### Environment Variables (Optional - for OCR)

```bash
export DATALAB_MARKER_API_KEY="your-api-key"
export DATALAB_MARKER_API_URL="https://api.datalab.marker.io/v1"
```

If not set, system will use PyPDFLoader only (no OCR).

## Usage

### Batch Process All PDFs

```bash
cd /home/suspect/.n8n/maatlangchain
python3 scripts/process_rbg_library.py
```

### Process Single PDF via API

```bash
curl -X POST "http://localhost:8000/rag/ingest_pdf" \
  -H "Content-Type: application/json" \
  -d '{
    "pdf_path": "/path/to/file.pdf",
    "use_ocr": false,
    "collection_name": "rbg_collection"
  }'
```

## Output Monitoring

All processing results are saved to:
```
/home/suspect/.n8n/maatlangchain/rbg_processing_output/
```

### Files Generated

1. **`processing_results_YYYYMMDD_HHMMSS.json`**
   - Detailed results for each PDF
   - Includes: status, pages, chunks, processing time, errors

2. **`latest_summary.json`**
   - Latest processing summary
   - Quick overview: total, success, errors, OCR usage

### View Results

```bash
# View latest summary
cat rbg_processing_output/latest_summary.json | jq

# View detailed results
cat rbg_processing_output/processing_results_*.json | jq '.results[0]'
```

## PDF Detection Logic

The system automatically detects PDF type:

1. **Try PyPDFLoader first**
2. **Check average text per page**
   - If < 100 chars/page → Likely scanned → Use OCR
   - If ≥ 100 chars/page → Text-based → Use PyPDFLoader

## Processing Flow

```
PDF File
  ↓
Detect Type (text vs scanned)
  ↓
Extract Content
  ├─ Text PDF → PyPDFLoader
  └─ Scanned PDF → DatalabMarkerLoader (OCR)
  ↓
Filter Front Matter (skip first 5 pages)
  ↓
Chunk Documents (adaptive sizing)
  ↓
Filter Low-Quality Chunks
  ↓
Generate Embeddings (batch)
  ↓
Store in Vector DB
  ↓
Save Results to Output Folder
```

## Collection Naming

PDFs are stored in collections named:
- Format: `rbg_{filename_without_extension}`
- Example: `RBG-Tools-for-Analysis.pdf` → `rbg_rbg-tools-for-analysis`

## Error Handling

- **No text extracted**: PDF marked as error, logged
- **OCR failure**: Falls back to PyPDFLoader if possible
- **Processing errors**: Detailed error messages in output JSON

## Integration with RAG

Processed PDFs are immediately available for RAG queries:

```python
# Query processed PDFs
result = rag.query(
    question="What is the RBG methodology?",
    collection_name="rbg_rbg-tools-for-analysis",
    top_k=5
)
```

## Next Steps

1. Run batch processing: `python3 scripts/process_rbg_library.py`
2. Monitor output folder for results
3. Test RAG queries on processed PDFs
4. Review and adjust chunk sizes if needed

