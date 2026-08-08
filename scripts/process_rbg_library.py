#!/usr/bin/env python3
"""
RBG Library Processing Script with Optimizations

Script to process the RBG library PDFs with optimized embedding generation,
adaptive chunk sizing, and progress tracking.

Usage:
    python scripts/process_rbg_library.py --limit 10 --device cuda
    python scripts/process_rbg_library.py --pdf-path /path/to/file.pdf
"""

import os
import sys
import argparse
import logging
import time
from pathlib import Path
from typing import List, Optional

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Import optimized components
from core.chains.document_processor import create_optimized_document_processor
from core.chains.maat_rag import create_optimized_rag
from core.integrations.tehuti_lab import create_tehuti_vector_store, get_tehuti_config

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
log = logging.getLogger(__name__)


def get_rbg_pdfs(rbg_library_path: str, limit: Optional[int] = None) -> List[str]:
    """
    Get list of RBG PDF files to process.

    Args:
        rbg_library_path: Path to RBG library directory
        limit: Optional limit on number of PDFs to process

    Returns:
        List of PDF file paths
    """
    library_path = Path(rbg_library_path)
    if not library_path.exists():
        log.error(f"RBG library path not found: {rbg_library_path}")
        return []

    # Find all PDF files
    pdf_files = list(library_path.glob("*.pdf"))
    pdf_files.sort()

    if limit:
        pdf_files = pdf_files[:limit]

    log.info(f"Found {len(pdf_files)} PDF files to process")
    return [str(pdf) for pdf in pdf_files]


def process_single_pdf(pdf_path: str, processor, rag_instance) -> bool:
    """
    Process a single PDF file.

    Args:
        pdf_path: Path to PDF file
        processor: Document processor instance
        rag_instance: RAG instance

    Returns:
        True if successful, False otherwise
    """
    try:
        pdf_name = Path(pdf_path).stem
        log.info(f"Processing PDF: {pdf_name}")

        start_time = time.time()

        # Load and process document
        from langchain_community.document_loaders import PyPDFLoader

        loader = PyPDFLoader(pdf_path)
        documents = loader.load()

        if not documents:
            log.warning(f"No documents loaded from {pdf_name}")
            return False

        # Add metadata
        for doc in documents:
            doc.metadata.update(
                {
                    "source_pdf": pdf_name,
                    "file_path": pdf_path,
                }
            )

        # Process with optimizations
        success = processor.process_documents(documents, pdf_name)

        processing_time = time.time() - start_time
        log.info(
            f"Processed {pdf_name} in {processing_time:.2f}s - {'SUCCESS' if success else 'FAILED'}"
        )

        return success

    except Exception as e:
        log.error(f"Failed to process {pdf_path}: {e}")
        return False


def main():
    """Main processing function."""
    parser = argparse.ArgumentParser(
        description="Process RBG Library with optimizations"
    )
    parser.add_argument(
        "--rbg-library",
        default="/home/suspect/.n8n/jarvis/rbg-library",
        help="Path to RBG library directory",
    )
    parser.add_argument(
        "--limit", type=int, default=None, help="Limit number of PDFs to process"
    )
    parser.add_argument(
        "--pdf-path", type=str, default=None, help="Process single PDF file"
    )
    parser.add_argument(
        "--device",
        choices=["cpu", "cuda", "auto"],
        default="auto",
        help="Device for embedding generation",
    )
    parser.add_argument(
        "--batch-size", type=int, default=32, help="Batch size for embedding generation"
    )
    parser.add_argument(
        "--vector-store",
        choices=["chroma", "faiss"],
        default="chroma",
        help="Vector store type",
    )
    parser.add_argument(
        "--persist-dir",
        default="./chroma_db_maat",
        help="Vector store persistence directory",
    )
    parser.add_argument(
        "--collection", default="rbg_library", help="Collection name for vector store"
    )

    args = parser.parse_args()

    # Setup Tehuti environment
    config = get_tehuti_config()
    log.info(f"Using Tehuti config: {config}")

    try:
        # Create optimized vector store and embeddings
        log.info("Creating optimized vector store and embeddings...")
        vector_store, embeddings = create_tehuti_vector_store(
            vector_store_type=args.vector_store,
            persist_directory=args.persist_dir,
            collection_name=args.collection,
            embedding_model=config["embedding_model"],
            device=args.device,
            batch_size=args.batch_size,
        )

        # Create optimized processor and RAG
        processor = create_optimized_document_processor(
            embeddings=embeddings,
            vector_store=vector_store,
            max_chunk_size=2500,
        )

        rag_instance = create_optimized_rag(
            vector_store=vector_store,
            embeddings=embeddings,
        )

        # Process single PDF if specified
        if args.pdf_path:
            if not os.path.exists(args.pdf_path):
                log.error(f"PDF file not found: {args.pdf_path}")
                return 1

            log.info(f"Processing single PDF: {args.pdf_path}")
            success = process_single_pdf(args.pdf_path, processor, rag_instance)
            return 0 if success else 1

        # Process RBG library
        pdf_files = get_rbg_pdfs(args.rbg_library, args.limit)
        if not pdf_files:
            log.error("No PDF files found to process")
            return 1

        # Process with timing
        start_time = time.time()
        successful = 0
        failed = 0

        log.info(f"Starting batch processing of {len(pdf_files)} PDF files...")

        for i, pdf_path in enumerate(pdf_files, 1):
            log.info(f"Processing PDF {i}/{len(pdf_files)}")

            if process_single_pdf(pdf_path, processor, rag_instance):
                successful += 1
            else:
                failed += 1

        total_time = time.time() - start_time

        # Report results
        log.info("=" * 60)
        log.info("PROCESSING COMPLETE")
        log.info("=" * 60)
        log.info(f"Total PDFs processed: {len(pdf_files)}")
        log.info(f"Successful: {successful}")
        log.info(f"Failed: {failed}")
        log.info(f"Total time: {total_time:.2f}s")
        log.info(f"Average time per PDF: {total_time / len(pdf_files):.2f}s")
        log.info(f"Throughput: {len(pdf_files) / total_time * 60:.1f} PDFs/minute")

        # Performance stats
        if hasattr(rag_instance, "get_performance_stats"):
            stats = rag_instance.get_performance_stats()
            log.info(f"Performance stats: {stats}")

        return 0 if failed == 0 else 1

    except Exception as e:
        log.error(f"Processing failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
