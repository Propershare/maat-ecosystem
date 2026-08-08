#!/usr/bin/env python3
"""
Ingest Canon Markdown Files into RAG System
Processes all markdown files from docs/canon/ and stores them in canon_kmt collection
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Setup paths
maatlangchain_root = Path(__file__).parent.parent
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

# Import after path setup
try:
    from api.main import get_vector_store
    from core.chains.document_processor import DocumentProcessor
except Exception as e:
    print(f"Import error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(maatlangchain_root / "canon_ingestion.log")
    ]
)
log = logging.getLogger(__name__)

# Canon directory
CANON_DIR = maatlangchain_root / "docs" / "canon"
OUTPUT_DIR = maatlangchain_root
OUTPUT_DIR.mkdir(exist_ok=True)

# Collection name for canon files
COLLECTION_NAME = "canon_kmt"


def find_markdown_files(base_path: Path) -> List[Path]:
    """Find all markdown files recursively."""
    md_files = []
    if base_path.exists() and base_path.is_dir():
        md_files = list(base_path.rglob("*.md"))
        md_files.extend(list(base_path.rglob("*.MD")))
    return sorted(md_files)


def process_markdown_file(
    md_path: Path, 
    processor: DocumentProcessor,
    vector_store,
    embeddings
) -> Dict[str, Any]:
    """Process a single markdown file."""
    result = {
        "file_path": str(md_path),
        "file_name": md_path.name,
        "status": "pending",
        "documents_loaded": 0,
        "chunks_created": 0,
        "processing_time": 0.0,
        "error": None,
        "timestamp": datetime.now().isoformat(),
    }
    
    start_time = datetime.now()
    
    try:
        # Load markdown file
        documents = processor.load_markdown(str(md_path))
        
        if not documents:
            result["status"] = "error"
            result["error"] = "No documents loaded"
            return result
        
        result["documents_loaded"] = len(documents)
        
        # Process and store in database
        try:
            success = processor.process_documents(documents, COLLECTION_NAME)
            if success:
                # Estimate chunks (actual count would require tracking during processing)
                # For now, we'll use document count as approximation
                result["chunks_created"] = len(documents)
                result["status"] = "success"
                result["collection_name"] = COLLECTION_NAME
            else:
                result["status"] = "error"
                result["error"] = "Failed to process documents"
        except Exception as db_error:
            result["status"] = "error"
            result["error"] = str(db_error)
            log.error(f"Database error processing {md_path.name}: {db_error}")
        
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        log.error(f"Error processing {md_path.name}: {e}")
        import traceback
        log.error(traceback.format_exc())
    
    finally:
        result["processing_time"] = (datetime.now() - start_time).total_seconds()
    
    return result


def main():
    """Main processing function."""
    log.info("=" * 80)
    log.info("Canon Markdown Ingestion to RAG")
    log.info("=" * 80)
    log.info("")
    
    # Find markdown files
    if not CANON_DIR.exists():
        log.error(f"Canon directory not found: {CANON_DIR}")
        return
    
    md_files = find_markdown_files(CANON_DIR)
    
    if not md_files:
        log.warning("No markdown files found in canon directory")
        log.info(f"Searched: {CANON_DIR}")
        summary = {
            "total_files": 0,
            "processed": 0,
            "success": 0,
            "errors": 0,
            "start_time": datetime.now().isoformat(),
            "end_time": datetime.now().isoformat(),
            "total_processing_time": 0.0,
        }
        with open(OUTPUT_DIR / "canon_ingestion_summary.json", 'w') as f:
            json.dump(summary, f, indent=2)
        return
    
    log.info(f"Found {len(md_files)} markdown files in {CANON_DIR}")
    log.info("")
    
    # Initialize vector store once (reuse for all files)
    log.info("Initializing vector store and embeddings...")
    vector_store, embeddings = None, None
    try:
        vector_store, embeddings = get_vector_store()
        log.info("✓ Vector store initialized successfully")
    except Exception as e:
        log.error(f"✗ Failed to initialize vector store: {e}")
        log.error("Cannot proceed with database storage.")
        log.error("Please check PGVECTOR_DB_URL in /home/suspect/.n8n/tehuti-lab-webui/.env")
        return
    
    # Create processor
    processor = DocumentProcessor(
        embeddings=embeddings,
        vector_store=vector_store,
        max_chunk_size=2500,
        min_chunk_size=200,
        skip_front_pages=0,  # Don't skip for markdown files
        use_ocr=False,  # Markdown doesn't need OCR
    )
    
    # Process files
    results = []
    summary = {
        "total_files": len(md_files),
        "processed": 0,
        "success": 0,
        "errors": 0,
        "start_time": datetime.now().isoformat(),
        "collection_name": COLLECTION_NAME,
    }
    
    for i, md_path in enumerate(md_files, 1):
        log.info(f"\n[{i}/{len(md_files)}] Processing: {md_path.name}")
        
        result = process_markdown_file(md_path, processor, vector_store, embeddings)
        results.append(result)
        summary["processed"] += 1
        
        if result["status"] == "success":
            summary["success"] += 1
            log.info(f"  ✓ Success: {result['documents_loaded']} document(s), ~{result['chunks_created']} chunks")
        else:
            summary["errors"] += 1
            log.error(f"  ✗ Error: {result.get('error', 'Unknown error')}")
    
    # Finalize summary
    summary["end_time"] = datetime.now().isoformat()
    summary["total_processing_time"] = (
        datetime.fromisoformat(summary["end_time"]) - 
        datetime.fromisoformat(summary["start_time"])
    ).total_seconds()
    
    # Save results
    output_file = OUTPUT_DIR / f"canon_ingestion_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump({
            "summary": summary,
            "results": results
        }, f, indent=2)
    
    summary_file = OUTPUT_DIR / "canon_ingestion_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    # Print summary
    log.info("\n" + "=" * 80)
    log.info("INGESTION SUMMARY")
    log.info("=" * 80)
    log.info(f"Total Files: {summary['total_files']}")
    log.info(f"Processed: {summary['processed']}")
    log.info(f"Success: {summary['success']}")
    log.info(f"Errors: {summary['errors']}")
    log.info(f"Collection: {COLLECTION_NAME}")
    log.info(f"Total Time: {summary['total_processing_time']:.2f} seconds")
    log.info(f"\nResults saved to: {output_file.name}")
    log.info(f"Summary saved to: {summary_file.name}")
    log.info("=" * 80)


if __name__ == "__main__":
    main()

