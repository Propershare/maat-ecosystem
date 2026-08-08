#!/usr/bin/env python3
"""
Enhanced re-extraction of problematic files from source PDFs
Uses improved OCR settings and quality validation
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List
import logging

# Setup paths
maatlangchain_root = Path(__file__).parent
sys.path.insert(0, str(maatlangchain_root))
os.chdir(maatlangchain_root)

# Try to load .env file first (for database connection)
env_file = Path("/home/suspect/.n8n/tehuti-lab-webui/.env")
if env_file.exists():
    with open(env_file, 'r') as f:
        for line in f:
            if line.startswith("PGVECTOR_DB_URL=") or line.startswith("PGVECTOR_DB_URL ="):
                value = line.split("=", 1)[1].strip().strip('"').strip("'")
                if value:
                    os.environ["PGVECTOR_DB_URL"] = value
                    break

from core.chains.document_processor import DocumentProcessor
from api.main import get_vector_store

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(maatlangchain_root / "re_extraction.log")
    ]
)
log = logging.getLogger(__name__)

# Paths
mapping_file = maatlangchain_root / "txt_to_pdf_mapping.json"
review_folder = maatlangchain_root / "extracted_files_review"
output_folder = maatlangchain_root / "re_extracted_files"
output_folder.mkdir(exist_ok=True)

def load_mapping() -> Dict:
    """Load the txt to PDF mapping."""
    if not mapping_file.exists():
        log.error(f"Mapping file not found: {mapping_file}")
        return {}
    
    with open(mapping_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def re_extract_pdf(pdf_path: Path, txt_filename: str, category: str) -> Dict:
    """
    Re-extract text from PDF with enhanced OCR settings.
    Includes memory cleanup to prevent GPU memory issues.
    """
    """
    Re-extract text from PDF with enhanced OCR settings.
    
    Returns:
        Dict with status, file_path, chunks_created, processing_time
    """
    import time
    start_time = time.time()
    
    try:
        log.info(f"Re-extracting: {pdf_path.name} -> {txt_filename}")
        
        # Initialize vector store and embeddings
        vector_store, embeddings = get_vector_store()
        
        # Create processor with enhanced OCR settings
        processor = DocumentProcessor(
            embeddings=embeddings,
            vector_store=vector_store,
            max_chunk_size=2500,
            min_chunk_size=200,
            skip_front_pages=0,
            use_ocr=True,  # Enable OCR for better extraction
        )
        
        # Load PDF with enhanced OCR
        documents = processor.load_pdf(str(pdf_path))
        
        if not documents:
            return {
                'status': 'error',
                'file': txt_filename,
                'pdf': str(pdf_path),
                'error': 'Failed to load PDF',
                'processing_time': time.time() - start_time
            }
        
        # Combine all document content
        extracted_text = "\n\n".join([doc.page_content for doc in documents])
        
        # Clear documents from memory
        del documents
        
        # Force garbage collection to free memory
        import gc
        gc.collect()
        
        # Try to clear PyTorch cache if available
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except ImportError:
            pass
        
        # Save to output folder
        output_path = output_folder / txt_filename
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(extracted_text)
        
        processing_time = time.time() - start_time
        
        log.info(f"  ✓ Success: {len(extracted_text)} chars extracted in {processing_time:.2f}s")
        
        return {
            'status': 'success',
            'file': txt_filename,
            'pdf': str(pdf_path),
            'output_path': str(output_path),
            'size': len(extracted_text),
            'words': len(extracted_text.split()),
            'processing_time': processing_time
        }
        
    except Exception as e:
        processing_time = time.time() - start_time
        log.error(f"  ✗ Error re-extracting {pdf_path.name}: {e}")
        import traceback
        log.error(traceback.format_exc())
        return {
            'status': 'error',
            'file': txt_filename,
            'pdf': str(pdf_path),
            'error': str(e),
            'processing_time': processing_time
        }

def main():
    """Main re-extraction function."""
    log.info("=" * 80)
    log.info("ENHANCED RE-EXTRACTION FROM SOURCE PDFs")
    log.info("=" * 80)
    log.info("")
    
    # Load mapping
    mapping = load_mapping()
    if not mapping:
        log.error("No mapping data found!")
        return
    
    # Get files with PDFs
    files_with_pdfs = [
        (txt_file, info['pdf_path'], info['category'])
        for txt_file, info in mapping.items()
        if info.get('pdf_exists') and info.get('pdf_path')
    ]
    
    log.info(f"Found {len(files_with_pdfs)} files with source PDFs to re-extract")
    log.info("")
    
    results = []
    success_count = 0
    error_count = 0
    
    for i, (txt_file, pdf_path_str, category) in enumerate(files_with_pdfs, 1):
        pdf_path = Path(pdf_path_str)
        
        if not pdf_path.exists():
            log.warning(f"  PDF not found: {pdf_path}")
            results.append({
                'status': 'error',
                'file': txt_file,
                'pdf': pdf_path_str,
                'error': 'PDF file not found'
            })
            error_count += 1
            continue
        
        log.info(f"[{i}/{len(files_with_pdfs)}] Processing: {txt_file}")
        result = re_extract_pdf(pdf_path, txt_file, category)
        results.append(result)
        
        if result['status'] == 'success':
            success_count += 1
        else:
            error_count += 1
    
    # Save results
    results_file = maatlangchain_root / "re_extraction_results.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    log.info("")
    log.info("=" * 80)
    log.info("RE-EXTRACTION SUMMARY")
    log.info("=" * 80)
    log.info(f"Total files: {len(files_with_pdfs)}")
    log.info(f"Success: {success_count}")
    log.info(f"Errors: {error_count}")
    log.info(f"Output folder: {output_folder}")
    log.info(f"Results saved to: {results_file}")
    log.info("")
    log.info("NEXT STEPS:")
    log.info("1. Review re-extracted files in: " + str(output_folder))
    log.info("2. Run quality check on re-extracted files")
    log.info("3. Replace originals if quality improved")
    log.info("=" * 80)

if __name__ == "__main__":
    main()

