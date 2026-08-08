"""
MaatLangChain Document Processor

Optimized document processing for RBG library with batch embedding generation,
adaptive chunk sizing, progress tracking, and quality filtering.

Updated for LangChain 0.2.x compatibility.
"""

import logging
import os
import json
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

# Import tqdm for progress tracking
try:
    from tqdm import tqdm
except ImportError:
    tqdm = None

# Updated LangChain imports (no deprecation warnings)
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

log = logging.getLogger(__name__)

# Import Docling for OCR support
try:
    from docling.document_converter import DocumentConverter
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.document_converter import PdfFormatOption
    DOCLING_AVAILABLE = True
    log.info("Docling available for OCR (GPU mode)")
except ImportError:
    # Try adding user site-packages to path (for --user installs)
    try:
        import site
        import sys
        user_site = site.getusersitepackages()
        if user_site not in sys.path:
            sys.path.insert(0, user_site)
        from docling.document_converter import DocumentConverter
        from docling.datamodel.pipeline_options import PdfPipelineOptions
        from docling.document_converter import PdfFormatOption
        DOCLING_AVAILABLE = True
        log.info("Docling available for OCR (from user site-packages, GPU mode)")
    except ImportError:
        DOCLING_AVAILABLE = False
        log.warning("Docling not available - OCR disabled. Install with: pip install --user docling")

# Legacy DatalabMarkerLoader support (deprecated, use Docling instead)
try:
    import sys
    # Try to import from tehuti-lab-webui
    webui_backend = Path(__file__).parent.parent.parent.parent / "tehuti-lab-webui" / "backend"
    if webui_backend.exists():
        sys.path.insert(0, str(webui_backend))
        try:
            from open_webui.retrieval.loaders.datalab_marker import DatalabMarkerLoader
            DATALAB_AVAILABLE = True
        except ImportError:
            DATALAB_AVAILABLE = False
    else:
        DATALAB_AVAILABLE = False
except Exception:
    DATALAB_AVAILABLE = False


class DocumentProcessor:
    """
    Optimized document processor for RBG library PDFs.

    Features:
    - Adaptive chunk sizing based on document size
    - Batch embedding generation for 10-50x speedup
    - Progress tracking with tqdm
    - Quality filtering (removes small/low-quality chunks)
    - Front matter filtering (skips title pages, copyright, TOC)
    """

    def __init__(self, embeddings, vector_store, max_chunk_size=2500, min_chunk_size=200, skip_front_pages=5, 
                 use_ocr=False, datalab_api_key=None, datalab_api_url=None):
        self.embeddings = embeddings
        self.vector_store = vector_store
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size  # Minimum chunk size to keep
        self.skip_front_pages = skip_front_pages  # Skip first N pages (title, copyright, TOC)
        # Prefer Docling over DatalabMarkerLoader
        self.use_ocr = use_ocr and (DOCLING_AVAILABLE or DATALAB_AVAILABLE)
        self.datalab_api_key = datalab_api_key or os.environ.get("DATALAB_MARKER_API_KEY")
        self.datalab_api_url = datalab_api_url or os.environ.get("DATALAB_MARKER_API_URL", "https://api.datalab.marker.io/v1")

    def get_adaptive_chunk_config(
        self, total_pages: int, total_chars: int
    ) -> tuple[int, int]:
        """
        Determine optimal chunk size and overlap based on document characteristics.

        Args:
            total_pages: Number of pages in the document
            total_chars: Total character count

        Returns:
            Tuple of (chunk_size, chunk_overlap)
        """
        if total_pages > 500 or total_chars > 1000000:  # Large PDFs
            chunk_size = min(2500, self.max_chunk_size)
            chunk_overlap = 400
        elif total_pages > 100 or total_chars > 200000:  # Medium PDFs
            chunk_size = min(2000, self.max_chunk_size)
            chunk_overlap = 300
        else:  # Small PDFs
            chunk_size = min(1000, self.max_chunk_size)
            chunk_overlap = 200

        log.info(
            f"Adaptive chunking: {total_pages} pages, {total_chars:,} chars -> chunk_size={chunk_size}, overlap={chunk_overlap}"
        )
        return chunk_size, chunk_overlap

    def is_low_quality_chunk(self, text: str) -> bool:
        """
        Check if chunk is low quality (too short, mostly copyright, etc.).

        Args:
            text: Chunk text content

        Returns:
            True if chunk should be filtered out
        """
        # Too short
        if len(text.strip()) < self.min_chunk_size:
            return True
        
        # Mostly whitespace
        if len(text.strip()) / len(text) < 0.5 if text else True:
            return True
        
        # Mostly copyright/legal text
        copyright_keywords = ['copyright', 'all rights reserved', 'no part of this publication', 
                             'reproduced', 'stored in a retrieval system', 'transmitted']
        text_lower = text.lower()
        copyright_count = sum(1 for keyword in copyright_keywords if keyword in text_lower)
        if copyright_count >= 3:  # 3+ copyright phrases = likely copyright page
            return True
        
        # Mostly page numbers or headers
        if re.match(r'^\d+\s*$', text.strip()) or len(text.strip().split()) < 5:
            return True
        
        return False

    def filter_front_matter(self, documents: List[Document]) -> List[Document]:
        """
        Filter out front matter (title pages, copyright, TOC).

        Args:
            documents: List of documents

        Returns:
            Filtered list without front matter
        """
        if self.skip_front_pages <= 0:
            return documents
        
        filtered = []
        skipped = 0
        
        for doc in documents:
            page_num = doc.metadata.get('page', 0)
            if isinstance(page_num, str):
                try:
                    page_num = int(page_num)
                except ValueError:
                    page_num = 0
            
            if page_num < self.skip_front_pages:
                skipped += 1
                continue
            
            filtered.append(doc)
        
        if skipped > 0:
            log.info(f"Skipped {skipped} front matter pages (first {self.skip_front_pages} pages)")
        
        return filtered

    def load_pdf(self, pdf_path: str, force_ocr: Optional[bool] = None) -> List[Document]:
        """
        Load PDF and return documents with metadata.
        
        Args:
            pdf_path: Path to PDF file
            force_ocr: Force OCR extraction (overrides use_ocr setting)
            
        Returns:
            List of Document objects
        """
        try:
            use_ocr = force_ocr if force_ocr is not None else self.use_ocr
            
            # Prefer Docling for OCR (local, no API keys needed) - GPU MODE
            if use_ocr and DOCLING_AVAILABLE:
                log.info(f"Loading PDF with Docling OCR (GPU): {pdf_path}")
                
                # Clear GPU cache before processing to prevent OOM
                try:
                    import torch
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
                        log.info("GPU cache cleared before Docling processing")
                except ImportError:
                    pass
                
                try:
                    # Configure Docling - disable table structure to reduce GPU memory usage
                    # But keep GPU enabled for OCR and layout models
                    pipeline_options = PdfPipelineOptions()
                    pipeline_options.do_ocr = True
                    pipeline_options.do_table_structure = False  # Disable to save GPU memory
                    
                    converter = DocumentConverter(
                        format_options={
                            PdfFormatOption.TEXT_MARKDOWN: True,
                        },
                        pipeline_options=pipeline_options
                    )
                    log.info("Docling configured: OCR enabled (GPU), table structure disabled")
                except (ImportError, AttributeError) as e:
                    # Fallback if pipeline options not available
                    log.warning(f"Using default Docling configuration: {e}")
                    converter = DocumentConverter()
                
                result = converter.convert(pdf_path)
                
                # Clear GPU cache after processing
                try:
                    import torch
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
                        log.info("GPU cache cleared after Docling processing")
                except ImportError:
                    pass
                
                # Convert DoclingDocument to LangChain Documents
                markdown_content = result.document.export_to_markdown()
                
                # Better splitting: Use larger chunks (by sections/paragraphs) instead of tiny splits
                # Split by double newlines but combine small chunks
                paragraphs = markdown_content.split('\n\n')
                documents = []
                current_chunk = []
                chunk_size = 0
                chunk_index = 0
                
                for para in paragraphs:
                    para = para.strip()
                    if not para or para.startswith('<!--'):  # Skip empty or image markers
                        continue
                    
                    # Combine paragraphs until we have a reasonable chunk size
                    if chunk_size + len(para) < 5000 and len(current_chunk) < 10:
                        current_chunk.append(para)
                        chunk_size += len(para)
                    else:
                        # Save current chunk
                        if current_chunk:
                            doc = Document(
                                page_content='\n\n'.join(current_chunk),
                                metadata={
                                    "page": chunk_index,
                                    "file_path": pdf_path,
                                    "file_name": os.path.basename(pdf_path),
                                    "processed_date": datetime.now().isoformat(),
                                    "extraction_method": "docling_ocr",
                                    "ocr_used": True,
                                }
                            )
                            documents.append(doc)
                            chunk_index += 1
                        
                        # Start new chunk
                        current_chunk = [para]
                        chunk_size = len(para)
                
                # Add final chunk
                if current_chunk:
                    doc = Document(
                        page_content='\n\n'.join(current_chunk),
                        metadata={
                            "page": chunk_index,
                            "file_path": pdf_path,
                            "file_name": os.path.basename(pdf_path),
                            "processed_date": datetime.now().isoformat(),
                            "extraction_method": "docling_ocr",
                            "ocr_used": True,
                        }
                    )
                    documents.append(doc)
                
                extraction_method = "docling_ocr"
                ocr_used = True
                
            elif use_ocr and DATALAB_AVAILABLE and self.datalab_api_key:
                # Fallback to DatalabMarkerLoader if Docling not available
                log.info(f"Loading PDF with DatalabMarkerLoader OCR: {pdf_path}")
                loader = DatalabMarkerLoader(
                    file_path=pdf_path,
                    api_key=self.datalab_api_key,
                    api_base_url=self.datalab_api_url,
                    force_ocr=True,
                    use_llm=False,
                    paginate=True,
                    format_lines=True,
                )
                documents = loader.load()
                extraction_method = "datalab_ocr"
                ocr_used = True
            else:
                # Use PyPDFLoader for text-based PDFs
                log.info(f"Loading PDF with PyPDFLoader: {pdf_path}")
                loader = PyPDFLoader(pdf_path)
                documents = loader.load()
                extraction_method = "pypdf"
                ocr_used = False

            # Add additional metadata
            file_stats = os.stat(pdf_path)
            
            for doc in documents:
                doc.metadata.update(
                    {
                        "file_path": pdf_path,
                        "file_name": os.path.basename(pdf_path),
                        "file_size": file_stats.st_size,
                        "processed_date": datetime.now().isoformat(),
                        "extraction_method": extraction_method,
                        "ocr_used": ocr_used,
                    }
                )

            log.info(f"Loaded {len(documents)} pages from {pdf_path} using {extraction_method}")
            return documents
        except Exception as e:
            log.error(f"Error loading PDF {pdf_path}: {e}")
            import traceback
            log.error(traceback.format_exc())
            return []

    def load_markdown(self, md_path: str) -> List[Document]:
        """
        Load markdown file and return documents with metadata.
        
        Args:
            md_path: Path to markdown file
            
        Returns:
            List of Document objects
        """
        try:
            log.info(f"Loading markdown file: {md_path}")
            loader = TextLoader(md_path, encoding='utf-8')
            documents = loader.load()
            
            if not documents:
                log.warning(f"No content loaded from {md_path}")
                return []
            
            # Extract title from first heading if available
            title = None
            content = documents[0].page_content if documents else ""
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            if title_match:
                title = title_match.group(1).strip()
            else:
                # Fallback to filename without extension
                title = Path(md_path).stem.replace('_', ' ').replace('-', ' ')
            
            # Add additional metadata
            file_stats = os.stat(md_path)
            
            for doc in documents:
                doc.metadata.update(
                    {
                        "file_path": md_path,
                        "file_name": os.path.basename(md_path),
                        "file_type": "markdown",
                        "source": "canon",
                        "file_size": file_stats.st_size,
                        "processed_date": datetime.now().isoformat(),
                        "title": title,
                        "extraction_method": "text_loader",
                    }
                )
            
            log.info(f"Loaded {len(documents)} document(s) from {md_path} (title: {title})")
            return documents
        except Exception as e:
            log.error(f"Error loading markdown {md_path}: {e}")
            import traceback
            log.error(traceback.format_exc())
            return []

    def process_documents(
        self, documents: List[Document], collection_name: str
    ) -> bool:
        """
        Process documents with optimized batch embedding generation and quality filtering.

        Args:
            documents: List of LangChain documents
            collection_name: Name for the vector collection

        Returns:
            True if successful, False otherwise
        """
        if not documents:
            log.warning("No documents to process")
            return False

        # Filter front matter
        documents = self.filter_front_matter(documents)
        
        if not documents:
            log.warning("No documents remaining after front matter filtering")
            return False

        # Calculate document statistics for adaptive sizing
        total_pages = len(documents)
        total_chars = sum(len(doc.page_content) for doc in documents)

        # Get adaptive chunk configuration
        chunk_size, chunk_overlap = self.get_adaptive_chunk_config(
            total_pages, total_chars
        )

        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            add_start_index=True,
        )

        log.info(f"Splitting {len(documents)} documents into chunks...")
        chunks = text_splitter.split_documents(documents)
        log.info(f"Created {len(chunks)} chunks before filtering")

        # Filter low-quality chunks
        original_count = len(chunks)
        chunks = [chunk for chunk in chunks if not self.is_low_quality_chunk(chunk.page_content)]
        filtered_count = original_count - len(chunks)
        
        if filtered_count > 0:
            log.info(f"Filtered out {filtered_count} low-quality chunks ({filtered_count/original_count*100:.1f}%)")
        
        log.info(f"Final chunk count: {len(chunks)}")

        if not chunks:
            log.warning("No chunks remaining after quality filtering")
            return False

        # Process embeddings in batch (MAJOR OPTIMIZATION)
        return self._process_embeddings_batch(chunks, collection_name)

    def _process_embeddings_batch(
        self, chunks: List[Document], collection_name: str
    ) -> bool:
        """
        Process embeddings using batch generation for 10-50x speedup.

        Args:
            chunks: List of document chunks
            collection_name: Name for the vector collection

        Returns:
            True if successful, False otherwise
        """
        if not chunks:
            log.warning("No chunks to process")
            return False

        try:
            # Extract texts for batch processing
            texts = [chunk.page_content for chunk in chunks]
            metadatas = [chunk.metadata for chunk in chunks]

            log.info(f"Generating embeddings for {len(texts)} chunks in batch...")
            
            # Batch embed all texts at once (10-50x faster)
            if tqdm:
                embeddings = list(tqdm(
                    self.embeddings.embed_documents(texts),
                    desc="Generating embeddings",
                    total=len(texts),
                    unit="chunk"
                ))
            else:
                embeddings = self.embeddings.embed_documents(texts)

            log.info(f"Generated {len(embeddings)} embeddings")

            # Store in batches
            return self._store_chunks_batch(texts, embeddings, metadatas, collection_name)

        except Exception as e:
            log.error(f"Batch embedding generation failed: {e}")
            return False

    def _store_chunks_batch(
        self,
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict],
        collection_name: str,
    ) -> bool:
        """
        Store chunks in vector store in batches.

        Args:
            texts: List of chunk texts
            embeddings: List of embeddings
            metadatas: List of metadata dicts
            collection_name: Name for the collection

        Returns:
            True if successful, False otherwise
        """
        if not self.vector_store:
            log.error("Vector store not available")
            return False

        try:
            batch_size = 500
            total_batches = (len(texts) + batch_size - 1) // batch_size

            log.info(f"Storing {len(texts)} chunks in {total_batches} batches...")

            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                batch_embeddings = embeddings[i:i + batch_size]
                batch_metadatas = metadatas[i:i + batch_size]

                batch_num = (i // batch_size) + 1
                
                if tqdm:
                    tqdm.write(f"Storing batch {batch_num}/{total_batches} ({len(batch_texts)} chunks)")
                
                # Store batch with pre-computed embeddings
                # Use add_embeddings for PGVector (not add_texts with embeddings param)
                self.vector_store.add_embeddings(
                    texts=batch_texts,
                    embeddings=batch_embeddings,
                    metadatas=batch_metadatas,
                )

            log.info(f"Successfully stored all {len(texts)} chunks in collection '{collection_name}'")
            return True

        except Exception as e:
            log.error(f"Failed to store chunks: {e}")
            return False

    def _store_processed_chunks(
        self, processed_chunks: List[Dict], collection_name: str
    ) -> bool:
        """
        Store processed chunks in vector store.

        Args:
            processed_chunks: List of processed chunk dicts
            collection_name: Name for the collection

        Returns:
            True if successful, False otherwise
        """
        if not self.vector_store:
            log.error("Vector store not available")
            return False

        try:
            # Extract data for batch storage
            texts = [chunk["content"] for chunk in processed_chunks]
            embeddings = [chunk["embedding"] for chunk in processed_chunks if chunk.get("embedding")]
            metadatas = [chunk["metadata"] for chunk in processed_chunks]

            if not embeddings:
                log.warning("No embeddings to store")
                return False

            return self._store_chunks_batch(texts, embeddings, metadatas, collection_name)

        except Exception as e:
            log.error(f"Failed to store processed chunks: {e}")
            return False

    def process_pdf(
        self, pdf_path: str, collection_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a single PDF file.

        Args:
            pdf_path: Path to PDF file
            collection_name: Optional collection name (defaults to filename)

        Returns:
            Processing result dictionary
        """
        if collection_name is None:
            collection_name = Path(pdf_path).stem

        # Load PDF
        documents = self.load_pdf(pdf_path)
        if not documents:
            return {"status": "error", "error": "Failed to load PDF"}

        # Process documents
        success = self.process_documents(documents, collection_name)

        return {
            "status": "success" if success else "error",
            "pdf_path": pdf_path,
            "collection_name": collection_name,
            "documents_loaded": len(documents),
        }
