"""
MaatLangChain FastAPI Server
Exposes RAG functionality as OpenAPI tool server for OpenWebUI
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.chains.maat_rag import MaatRAG
from core.chains.document_processor import DocumentProcessor

# Try langchain_huggingface first, fallback to langchain_community
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings

from langchain_community.vectorstores import PGVector
import psycopg2

log = logging.getLogger(__name__)

app = FastAPI(
    title="MaatLangChain RAG API",
    description="Retrieval-Augmented Generation with Maat Governance",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global RAG instance (lazy loaded)
_rag_instance: Optional[MaatRAG] = None
_vector_store = None
_embeddings = None


def get_vector_store():
    """Get PostgreSQL vector store connection."""
    global _vector_store, _embeddings

    if _vector_store is not None:
        return _vector_store, _embeddings

    # Get PostgreSQL connection string
    PGVECTOR_DB_URL = os.environ.get("PGVECTOR_DB_URL")
    if not PGVECTOR_DB_URL:
        env_file = "/home/suspect/.n8n/open-webui/.env"
        if os.path.exists(env_file):
            with open(env_file, "r") as f:
                for line in f:
                    if line.startswith("PGVECTOR_DB_URL="):
                        PGVECTOR_DB_URL = (
                            line.split("=", 1)[1].strip().strip('"').strip("'")
                        )
                        break

    if not PGVECTOR_DB_URL:
        raise HTTPException(status_code=500, detail="PGVECTOR_DB_URL not configured")

    # Verify pgvector extension
    try:
        conn = psycopg2.connect(PGVECTOR_DB_URL)
        cur = conn.cursor()
        cur.execute("SELECT extname FROM pg_extension WHERE extname = 'vector';")
        if not cur.fetchone():
            conn.close()
            raise HTTPException(status_code=500, detail="pgvector extension not found")
        conn.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {e}")

    # Create embeddings
    _embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},  # Use CPU to avoid GPU conflicts
    )

    # Create vector store
    _vector_store = PGVector(
        connection_string=PGVECTOR_DB_URL,
        embedding_function=_embeddings,
        collection_name="maat_knowledge",
        use_jsonb=True,
    )

    return _vector_store, _embeddings


def get_rag_instance():
    """Get or create RAG instance."""
    global _rag_instance

    if _rag_instance is None:
        vector_store, embeddings = get_vector_store()
        _rag_instance = MaatRAG(vector_store=vector_store, embeddings=embeddings)

    return _rag_instance


# Import Pydantic models
try:
    from .models import (
        RAGQueryRequest,
        RAGQueryResponse,
        DocumentSource,
        ChunkFilter,
        ChunksResponse,
        ChunkInfo,
        PDFIngestRequest,
        IngestStatus,
        CollectionStats,
        SystemStats,
        HealthResponse,
        ErrorResponse,
    )
except ImportError:
    # Fallback if models not available
    class RAGQueryRequest(BaseModel):
        question: str
        top_k: Optional[int] = 5
        collection_name: Optional[str] = "maat_knowledge"

    class RAGQueryResponse(BaseModel):
        answer: str
        sources: List[Dict[str, Any]]
        metadata: Dict[str, Any]

    class PDFIngestRequest(BaseModel):
        pdf_path: str
        collection_name: Optional[str] = "maat_knowledge"
        min_chunk_size: Optional[int] = 200
        skip_front_pages: Optional[int] = 5


# Health Check
@app.get("/")
async def root():
    return {"name": "MaatLangChain RAG API", "version": "1.0.0", "status": "running"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    try:
        vector_store, _ = get_vector_store()
        return {"status": "healthy", "vector_store": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


# RAG Query Endpoint
@app.post("/rag/query", response_model=RAGQueryResponse)
async def query_rag(request: RAGQueryRequest):
    """
    Query the RAG system.

    This is the main endpoint for asking questions to the RAG system.
    Returns answers with source citations following Maat principles.
    """
    try:
        rag = get_rag_instance()

        # Query the RAG system
        # Note: MaatRAG.query() needs to be implemented or we use retriever directly
        retriever = rag.get_retriever(
            collection_name=request.collection_name, top_k=request.top_k
        )

        # Get relevant documents
        docs = retriever.get_relevant_documents(request.question)

        # For now, return first document as answer
        # TODO: Integrate with LLM for full RAG chain
        if docs:
            answer = (
                docs[0].page_content[:500] + "..."
                if len(docs[0].page_content) > 500
                else docs[0].page_content
            )
            sources = [
                {
                    "file": doc.metadata.get("file_name", "unknown"),
                    "page": doc.metadata.get("page", "unknown"),
                    "preview": doc.page_content[:200],
                }
                for doc in docs[: request.top_k]
            ]
        else:
            answer = "No relevant documents found."
            sources = []

        return RAGQueryResponse(
            answer=answer,
            sources=sources,
            metadata={
                "question": request.question,
                "top_k": request.top_k,
                "sources_found": len(docs),
            },
        )
    except Exception as e:
        log.error(f"RAG query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Chunk Viewing Endpoint
@app.get("/rag/chunks")
async def view_chunks(
    pdf_name: Optional[str] = None,
    limit: int = 10,
    skip_toc: bool = True,
    main_content_only: bool = False,
):
    """View chunks from the vector store in JSON format."""
    try:
        PGVECTOR_DB_URL = os.environ.get("PGVECTOR_DB_URL")
        if not PGVECTOR_DB_URL:
            env_file = "/home/suspect/.n8n/open-webui/.env"
            if os.path.exists(env_file):
                with open(env_file, "r") as f:
                    for line in f:
                        if line.startswith("PGVECTOR_DB_URL="):
                            PGVECTOR_DB_URL = (
                                line.split("=", 1)[1].strip().strip('"').strip("'")
                            )
                            break

        if not PGVECTOR_DB_URL:
            raise HTTPException(
                status_code=500, detail="PGVECTOR_DB_URL not configured"
            )

        conn = psycopg2.connect(PGVECTOR_DB_URL)
        cur = conn.cursor()

        # Build query
        where_parts = []
        params = []

        if pdf_name:
            where_parts.append("cmetadata->>'file_name' = %s")
            params.append(pdf_name)

        if skip_toc:
            where_parts.append("""
                document NOT ILIKE '%%CONTENTS%%' 
                AND document NOT ILIKE '%%C ONTENTS%%'
                AND document NOT ILIKE '%%ONTENTS%%'
            """)

        if main_content_only:
            where_parts.append("(cmetadata->>'page')::int > 19")

        where_clause = "WHERE " + " AND ".join(where_parts) if where_parts else ""
        params.append(limit)

        query = f"""
            SELECT document, cmetadata
            FROM langchain_pg_embedding 
            {where_clause}
            ORDER BY (cmetadata->>'page')::int NULLS LAST
            LIMIT %s;
        """

        cur.execute(query, params)

        chunks = []
        for doc, meta in cur.fetchall():
            page_num = meta.get("page", meta.get("page_number", "unknown"))
            is_front_matter = False
            if isinstance(page_num, int) and page_num <= 19:
                is_front_matter = True

            chunks.append(
                {
                    "text": doc[:500] + "..." if len(doc) > 500 else doc,
                    "full_length": len(doc),
                    "file": meta.get("file_name", "unknown"),
                    "page_number": page_num,
                    "page_label": meta.get("page_label", ""),
                    "is_front_matter": is_front_matter,
                }
            )

        conn.close()

        return {
            "chunks": chunks,
            "count": len(chunks),
            "filters": {
                "pdf_name": pdf_name,
                "skip_toc": skip_toc,
                "main_content_only": main_content_only,
            },
        }
    except Exception as e:
        log.error(f"Error viewing chunks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# PDF Ingestion Endpoint
@app.post("/rag/ingest_pdf")
async def ingest_pdf(request: IngestPDFRequest):
    """Ingest a PDF document into the RAG system."""
    try:
        if not os.path.exists(request.pdf_path):
            raise HTTPException(
                status_code=404, detail=f"PDF file not found: {request.pdf_path}"
            )

        vector_store, embeddings = get_vector_store()

        # Create document processor
        processor = DocumentProcessor(
            embeddings=embeddings,
            vector_store=vector_store,
            max_chunk_size=2500,
            min_chunk_size=request.min_chunk_size,
            skip_front_pages=request.skip_front_pages,
        )

        # Process PDF
        success = processor.process_rbg_pdf(request.pdf_path, request.collection_name)

        if success:
            return {
                "status": "success",
                "message": f"PDF {request.pdf_path} ingested successfully",
                "collection": request.collection_name,
            }
        else:
            raise HTTPException(
                status_code=500, detail=f"Failed to ingest PDF: {request.pdf_path}"
            )
    except Exception as e:
        log.error(f"Error ingesting PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Statistics Endpoint
@app.get("/rag/stats")
async def get_stats(collection_name: str = "maat_knowledge"):
    """Get statistics about the RAG system."""
    try:
        PGVECTOR_DB_URL = os.environ.get("PGVECTOR_DB_URL")
        if not PGVECTOR_DB_URL:
            env_file = "/home/suspect/.n8n/open-webui/.env"
            if os.path.exists(env_file):
                with open(env_file, "r") as f:
                    for line in f:
                        if line.startswith("PGVECTOR_DB_URL="):
                            PGVECTOR_DB_URL = (
                                line.split("=", 1)[1].strip().strip('"').strip("'")
                            )
                            break

        if not PGVECTOR_DB_URL:
            raise HTTPException(
                status_code=500, detail="PGVECTOR_DB_URL not configured"
            )

        conn = psycopg2.connect(PGVECTOR_DB_URL)
        cur = conn.cursor()

        # Get collection ID
        cur.execute(
            "SELECT uuid FROM langchain_pg_collection WHERE name = %s",
            (collection_name,),
        )
        collection_result = cur.fetchone()

        if not collection_result:
            conn.close()
            return {
                "collection": collection_name,
                "status": "not_found",
                "total_chunks": 0,
                "total_pdfs": 0,
            }

        collection_id = collection_result[0]

        # Get total chunks
        cur.execute(
            """
            SELECT COUNT(*) 
            FROM langchain_pg_embedding 
            WHERE collection_id = %s
        """,
            (collection_id,),
        )
        total_chunks = cur.fetchone()[0]

        # Get total PDFs
        cur.execute(
            """
            SELECT COUNT(DISTINCT cmetadata->>'file_name')
            FROM langchain_pg_embedding
            WHERE collection_id = %s
        """,
            (collection_id,),
        )
        total_pdfs = cur.fetchone()[0]

        # Get chunk size stats
        cur.execute(
            """
            SELECT 
                AVG(LENGTH(document)) as avg_length,
                MIN(LENGTH(document)) as min_length,
                MAX(LENGTH(document)) as max_length
            FROM langchain_pg_embedding
            WHERE collection_id = %s
        """,
            (collection_id,),
        )
        size_stats = cur.fetchone()

        # Get PDF list
        cur.execute(
            """
            SELECT 
                cmetadata->>'file_name' as name,
                COUNT(*) as chunks
            FROM langchain_pg_embedding
            WHERE collection_id = %s
            GROUP BY name
            ORDER BY chunks DESC
            LIMIT 10
        """,
            (collection_id,),
        )
        pdfs = [{"name": row[0], "chunks": row[1]} for row in cur.fetchall()]

        conn.close()

        return {
            "collection": collection_name,
            "status": "active",
            "total_chunks": total_chunks,
            "total_pdfs": total_pdfs,
            "chunk_stats": {
                "avg_length": int(size_stats[0]) if size_stats[0] else 0,
                "min_length": int(size_stats[1]) if size_stats[1] else 0,
                "max_length": int(size_stats[2]) if size_stats[2] else 0,
            },
            "top_pdfs": pdfs,
        }
    except Exception as e:
        log.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Collections Endpoint
@app.get("/rag/collections")
async def list_collections():
    """List all available collections."""
    try:
        PGVECTOR_DB_URL = os.environ.get("PGVECTOR_DB_URL")
        if not PGVECTOR_DB_URL:
            env_file = "/home/suspect/.n8n/open-webui/.env"
            if os.path.exists(env_file):
                with open(env_file, "r") as f:
                    for line in f:
                        if line.startswith("PGVECTOR_DB_URL="):
                            PGVECTOR_DB_URL = (
                                line.split("=", 1)[1].strip().strip('"').strip("'")
                            )
                            break

        if not PGVECTOR_DB_URL:
            raise HTTPException(
                status_code=500, detail="PGVECTOR_DB_URL not configured"
            )

        conn = psycopg2.connect(PGVECTOR_DB_URL)
        cur = conn.cursor()

        cur.execute("""
            SELECT 
                name,
                uuid,
                cmetadata
            FROM langchain_pg_collection
            ORDER BY name
        """)

        collections = []
        for name, uuid, metadata in cur.fetchall():
            # Get chunk count for this collection
            cur.execute(
                """
                SELECT COUNT(*) 
                FROM langchain_pg_embedding 
                WHERE collection_id = %s
            """,
                (uuid,),
            )
            chunk_count = cur.fetchone()[0]

            collections.append(
                {
                    "name": name,
                    "uuid": str(uuid),
                    "chunk_count": chunk_count,
                    "metadata": metadata,
                }
            )

        conn.close()

        return {"collections": collections, "count": len(collections)}
    except Exception as e:
        log.error(f"Error listing collections: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# OpenAPI Spec Endpoint (for OpenWebUI)
@app.get("/openapi.json")
async def openapi_spec():
    """Return OpenAPI spec for tool server integration."""
    from fastapi.openapi.utils import get_openapi

    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="MaatLangChain RAG API",
        version="1.0.0",
        description="Retrieval-Augmented Generation with Maat Governance",
        routes=app.routes,
    )

    # Add tool definitions for OpenWebUI
    openapi_schema["info"]["x-openai"] = {
        "name": "maatlangchain_rag",
        "description": "Query the MaatLangChain RAG system with Maat governance",
    }

    app.openapi_schema = openapi_schema
    return openapi_schema


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8019)
