"""
Code Embedding Generator
Layer 2: Embed all code for semantic search
Maat: Truth - Accurate code representation
"""

import logging
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
import hashlib

from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

from core.integrations.postgres import get_postgres_connection
from config.shared_config import get_shared_config

log = logging.getLogger(__name__)


class CodeEmbedder:
    """
    Generates embeddings for codebase files.
    
    Stores embeddings in PostgreSQL/pgvector for semantic search.
    """
    
    def __init__(self, embedding_model: Optional[str] = None):
        config = get_shared_config()
        self.embedding_model = embedding_model or config.embedding_model
        
        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.embedding_model,
            encode_kwargs={
                "batch_size": config.embedding_batch_size,
                "normalize_embeddings": True,
            },
        )
        
        self.embedding_dim = 384  # all-MiniLM-L6-v2 dimension
        self._ensure_table()
    
    def _ensure_table(self):
        """Ensure code embeddings table exists."""
        try:
            with get_postgres_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        CREATE EXTENSION IF NOT EXISTS vector;
                        
                        CREATE TABLE IF NOT EXISTS maat_code_embeddings (
                            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                            file_path VARCHAR(1000) NOT NULL,
                            code_hash VARCHAR(64) NOT NULL,
                            code_snippet TEXT NOT NULL,
                            language VARCHAR(50),
                            function_name VARCHAR(255),
                            class_name VARCHAR(255),
                            line_start INTEGER,
                            line_end INTEGER,
                            embedding vector(384),
                            metadata JSONB DEFAULT '{}'::jsonb,
                            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                            UNIQUE(file_path, code_hash)
                        );
                        
                        CREATE INDEX IF NOT EXISTS maat_code_embeddings_file_path_idx 
                        ON maat_code_embeddings(file_path);
                        
                        CREATE INDEX IF NOT EXISTS maat_code_embeddings_language_idx 
                        ON maat_code_embeddings(language);
                        
                        CREATE INDEX IF NOT EXISTS maat_code_embeddings_embedding_idx 
                        ON maat_code_embeddings USING ivfflat (embedding vector_cosine_ops);
                    """)
                    conn.commit()
                    log.info("Code embeddings table ensured")
        except Exception as e:
            log.error(f"Failed to ensure code embeddings table: {e}")
    
    def _hash_code(self, code: str) -> str:
        """Generate hash for code snippet."""
        return hashlib.sha256(code.encode("utf-8")).hexdigest()
    
    def embed_file(
        self,
        file_path: str,
        code: str,
        language: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Embed a file's code.
        
        Args:
            file_path: Path to the file
            code: Code content
            language: Programming language
            metadata: Additional metadata
        
        Returns:
            List of embedding IDs
        """
        # Split code into chunks (functions, classes, or by size)
        chunks = self._chunk_code(code, language)
        
        embedding_ids = []
        
        for chunk in chunks:
            embedding_id = self.embed_chunk(
                file_path=file_path,
                code=chunk["code"],
                language=language or chunk.get("language"),
                function_name=chunk.get("function_name"),
                class_name=chunk.get("class_name"),
                line_start=chunk.get("line_start"),
                line_end=chunk.get("line_end"),
                metadata={**(metadata or {}), **chunk.get("metadata", {})}
            )
            if embedding_id:
                embedding_ids.append(embedding_id)
        
        return embedding_ids
    
    def _chunk_code(
        self,
        code: str,
        language: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Chunk code into embeddable units.
        
        For now, chunks by functions/classes or by size.
        """
        chunks = []
        lines = code.split("\n")
        
        # Simple chunking: by function/class boundaries or by size
        current_chunk = []
        current_start = 1
        chunk_size = 50  # lines per chunk
        
        for i, line in enumerate(lines, 1):
            current_chunk.append(line)
            
            # Check if we hit a function/class boundary
            is_boundary = (
                line.strip().startswith("def ") or
                line.strip().startswith("class ") or
                line.strip().startswith("async def ") or
                len(current_chunk) >= chunk_size
            )
            
            if is_boundary and len(current_chunk) > 1:
                chunk_code = "\n".join(current_chunk[:-1])  # Exclude boundary line
                if chunk_code.strip():
                    chunks.append({
                        "code": chunk_code,
                        "language": language,
                        "line_start": current_start,
                        "line_end": i - 1,
                        "metadata": {}
                    })
                current_chunk = [line]  # Start new chunk with boundary line
                current_start = i
        
        # Add remaining chunk
        if current_chunk:
            chunk_code = "\n".join(current_chunk)
            if chunk_code.strip():
                chunks.append({
                    "code": chunk_code,
                    "language": language,
                    "line_start": current_start,
                    "line_end": len(lines),
                    "metadata": {}
                })
        
        return chunks
    
    def embed_chunk(
        self,
        file_path: str,
        code: str,
        language: Optional[str] = None,
        function_name: Optional[str] = None,
        class_name: Optional[str] = None,
        line_start: Optional[int] = None,
        line_end: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Embed a code chunk.
        
        Args:
            file_path: Path to the file
            code: Code snippet
            language: Programming language
            function_name: Function name if applicable
            class_name: Class name if applicable
            line_start: Starting line number
            line_end: Ending line number
            metadata: Additional metadata
        
        Returns:
            Embedding ID if successful, None otherwise
        """
        code_hash = self._hash_code(code)
        
        try:
            # Generate embedding
            embedding_vector = self.embeddings.embed_query(code)
            
            # Store in database
            with get_postgres_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO maat_code_embeddings (
                            file_path, code_hash, code_snippet, language,
                            function_name, class_name, line_start, line_end,
                            embedding, metadata
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (file_path, code_hash) 
                        DO UPDATE SET
                            code_snippet = EXCLUDED.code_snippet,
                            embedding = EXCLUDED.embedding,
                            metadata = EXCLUDED.metadata,
                            updated_at = NOW()
                        RETURNING id
                    """, (
                        file_path,
                        code_hash,
                        code,
                        language,
                        function_name,
                        class_name,
                        line_start,
                        line_end,
                        str(embedding_vector),  # Convert to PostgreSQL vector format
                        json.dumps(metadata or {})
                    ))
                    embedding_id = str(cur.fetchone()[0])
                    conn.commit()
                    log.debug(f"Embedded code chunk: {file_path}:{line_start}-{line_end}")
                    return embedding_id
        except Exception as e:
            log.error(f"Failed to embed code chunk: {e}")
            return None
    
    def embed_codebase(
        self,
        codebase_path: str,
        file_extensions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Embed entire codebase.
        
        Args:
            codebase_path: Path to codebase root
            file_extensions: List of file extensions to process
        
        Returns:
            Summary of embedding process
        """
        if file_extensions is None:
            file_extensions = [".py", ".js", ".ts", ".jsx", ".tsx"]
        
        codebase = Path(codebase_path)
        if not codebase.exists():
            raise ValueError(f"Codebase path does not exist: {codebase_path}")
        
        files_processed = 0
        chunks_embedded = 0
        errors = []
        
        for file_path in codebase.rglob("*"):
            if file_path.is_file() and file_path.suffix in file_extensions:
                try:
                    code = file_path.read_text(encoding="utf-8")
                    language = self._detect_language(file_path.suffix)
                    
                    embedding_ids = self.embed_file(
                        file_path=str(file_path.relative_to(codebase)),
                        code=code,
                        language=language
                    )
                    
                    files_processed += 1
                    chunks_embedded += len(embedding_ids)
                    log.info(f"Embedded {file_path}: {len(embedding_ids)} chunks")
                except Exception as e:
                    error_msg = f"Failed to embed {file_path}: {e}"
                    log.error(error_msg)
                    errors.append(error_msg)
        
        return {
            "files_processed": files_processed,
            "chunks_embedded": chunks_embedded,
            "errors": errors
        }
    
    def _detect_language(self, extension: str) -> str:
        """Detect programming language from file extension."""
        lang_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".jsx": "javascript",
            ".tsx": "typescript",
            ".java": "java",
            ".go": "go",
            ".rs": "rust",
            ".cpp": "cpp",
            ".c": "c",
        }
        return lang_map.get(extension, "unknown")

