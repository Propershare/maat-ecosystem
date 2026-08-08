"""
MaatLangChain FastAPI Server - Updated Version
Exposes RAG functionality as OpenAPI tool server for OpenWebUI
"""

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
import os
import sys
import time
from pathlib import Path
import psycopg2
import json

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

# Maat Memory system for cross-session tracking
try:
    from maat_memory_integration import get_maat_memory_logger

    MAAT_MEMORY_AVAILABLE = True
except ImportError:
    MAAT_MEMORY_AVAILABLE = False
    get_maat_memory_logger = None

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

# Global instances (lazy loaded)
_rag_instance: Optional[MaatRAG] = None
_vector_store = None
_embeddings = None
_maat_memory: Optional[Any] = None


def get_pgvector_url():
    """Get PostgreSQL connection string."""
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
    return PGVECTOR_DB_URL


def get_vector_store():
    """Get PostgreSQL vector store connection."""
    global _vector_store, _embeddings

    if _vector_store is not None:
        return _vector_store, _embeddings

    PGVECTOR_DB_URL = get_pgvector_url()
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


def get_maat_memory():
    """Get or create Maat memory instance."""
    global _maat_memory

    if not MAAT_MEMORY_AVAILABLE:
        return None

    if _maat_memory is None:
        try:
            from maat_memory import MaatMemory

            _maat_memory = MaatMemory()
            # Ensure "api" agent memory exists
            if "api" not in _maat_memory._data["agent_memory"]:
                _maat_memory._data["agent_memory"]["api"] = {
                    "session_id": None,
                    "last_updated": None,
                    "context": [],
                    "preferences": {},
                    "work_history": [],
                }
            # Start API session if not already started
            if _maat_memory._data["agent_memory"]["api"].get("session_id") is None:
                _maat_memory.start_session("api", "MaatLangChain API session")
            log.info("Maat memory initialized for API logging")
        except Exception as e:
            log.warning(f"Failed to initialize Maat memory: {e}")
            return None

    return _maat_memory


# Pydantic Models
class RAGQueryRequest(BaseModel):
    question: str
    top_k: Optional[int] = 5
    collection_name: Optional[str] = "maat_knowledge"
    min_score: Optional[float] = 0.0


class DocumentSource(BaseModel):
    file_name: str
    page: int
    preview: str
    score: Optional[float] = None


class RAGQueryResponse(BaseModel):
    answer: str
    sources: List[DocumentSource]
    metadata: Dict[str, Any]
    query_time: Optional[float] = None


class ChunkFilter(BaseModel):
    pdf_name: Optional[str] = None
    limit: int = 10
    skip_toc: bool = True


class ChunkInfo(BaseModel):
    chunk_id: str
    content: str
    pdf_name: str
    page: int
    metadata: Dict[str, Any]
    preview: str


class ChunksResponse(BaseModel):
    chunks: List[ChunkInfo]
    total_count: int
    filtered_count: int
    metadata: Dict[str, Any]


class PDFIngestRequest(BaseModel):
    pdf_path: str
    collection_name: Optional[str] = None
    chunk_size: Optional[int] = 1000
    chunk_overlap: Optional[int] = 200
    skip_front_pages: Optional[int] = 5


class IngestStatus(BaseModel):
    status: str
    message: str
    pdf_name: str
    chunks_created: Optional[int] = None
    processing_time: Optional[float] = None
    error_details: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    database_connected: bool
    embeddings_ready: bool
    timestamp: str
    version: str = "1.0.0"


# Health Check
@app.get("/")
async def root():
    return {"name": "MaatLangChain RAG API", "version": "1.0.0", "status": "running"}


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint."""
    try:
        vector_store, embeddings = get_vector_store()
        return HealthResponse(
            status="healthy",
            database_connected=True,
            embeddings_ready=True,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
        )
    except Exception as e:
        return HealthResponse(
            status="unhealthy",
            database_connected=False,
            embeddings_ready=False,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
        )


# RAG Query Endpoint
@app.post("/rag/query", response_model=RAGQueryResponse)
async def query_rag(request: RAGQueryRequest):
    """
    Query the RAG system.

    This is the main endpoint for asking questions to the RAG system.
    Returns answers with source citations following Maat principles.
    """
    start_time = time.time()

    # Log to Maat Memory
    maat_memory = get_maat_memory()

    try:
        rag = get_rag_instance()
        collection_name = request.collection_name or "maat_knowledge"
        top_k = request.top_k or 5

        # Use similarity search directly
        docs = rag.search_similar(
            query=request.question, collection_name=collection_name, top_k=top_k
        )

        # For now, return first document as answer
        # TODO: Integrate with LLM for full RAG chain
        if docs:
            answer = (
                docs[0].page_content[:500] + "..."
                if len(docs[0].page_content) > 500
                else docs[0].page_content
            )
            sources = []
            for doc in docs[:top_k]:
                page_val = doc.metadata.get("page", 0)
                try:
                    page_int = int(page_val) if str(page_val).isdigit() else 0
                except (ValueError, TypeError):
                    page_int = 0

                source = DocumentSource(
                    file_name=doc.metadata.get("file_name", "unknown"),
                    page=page_int,
                    preview=doc.page_content[:200],
                )
                sources.append(source)
        else:
            answer = "No relevant documents found."
            sources = []

        query_time = time.time() - start_time

        response = RAGQueryResponse(
            answer=answer,
            sources=sources,
            metadata={
                "question": request.question,
                "top_k": top_k,
                "sources_found": len(docs),
                "collection_name": collection_name,
            },
            query_time=query_time,
        )

        # Log to Maat memory
        if maat_memory:
            try:
                maat_memory.log_conversation(
                    agent="api",
                    user_query=request.question,
                    agent_response=answer[:500] + "..."
                    if len(answer) > 500
                    else answer,
                    tools_used=["rag_query"],
                    files_accessed=[s.get("file", "unknown") for s in sources],
                    decisions_made=[
                        f"Retrieved {len(docs)} documents from {collection_name}"
                    ],
                )
                maat_memory.log_audit(
                    agent="api",
                    action="rag_query",
                    resource=f"collection:{collection_name}",
                    reason=f"User query: {request.question[:100]}",
                    maat_compliance={
                        "truth": True,
                        "balance": True,
                        "order": True,
                        "self_reflection": True,
                    },
                )
            except Exception as e:
                log.warning(f"Failed to log to Maat memory: {e}")

        return response
    except Exception as e:
        log.error(f"RAG query failed: {e}")

        # Log error to Maat memory
        if maat_memory:
            try:
                maat_memory.log_error(
                    agent="api",
                    error_type="RAGQueryError",
                    message=str(e),
                    context={
                        "question": request.question,
                        "collection": request.collection_name,
                    },
                )
            except:
                pass

        raise HTTPException(status_code=500, detail=str(e))


# Chunk Viewing Endpoint
@app.post("/rag/chunks", response_model=ChunksResponse)
async def view_chunks(filter: ChunkFilter):
    """View chunks from the vector store."""
    try:
        PGVECTOR_DB_URL = get_pgvector_url()
        if not PGVECTOR_DB_URL:
            raise HTTPException(
                status_code=500, detail="PGVECTOR_DB_URL not configured"
            )

        conn = psycopg2.connect(PGVECTOR_DB_URL)
        cur = conn.cursor()

        # Build query
        where_parts = []
        params = []

        if filter.pdf_name:
            where_parts.append("cmetadata->>'file_name' = %s")
            params.append(filter.pdf_name)

        if filter.skip_toc:
            where_parts.append("""
                document NOT ILIKE '%%CONTENTS%%' 
                AND document NOT ILIKE '%%C ONTENTS%%'
                AND document NOT ILIKE '%%ONTENTS%%'
            """)

        where_clause = "WHERE " + " AND ".join(where_parts) if where_parts else ""
        params.append(filter.limit)

        query = f"""
            SELECT document, cmetadata
            FROM langchain_pg_embedding 
            {where_clause}
            ORDER BY (cmetadata->>'page')::int NULLS LAST
            LIMIT %s;
        """

        cur.execute(query, params)

        chunks = []
        for i, (doc, meta) in enumerate(cur.fetchall()):
            page_num = meta.get("page", meta.get("page_number", 0))
            if isinstance(page_num, str) and page_num.isdigit():
                page_num = int(page_num)

            chunk_info = ChunkInfo(
                chunk_id=f"chunk_{i}",
                content=doc,
                pdf_name=meta.get("file_name", "unknown"),
                page=page_num,
                metadata=meta,
                preview=doc[:200] + "..." if len(doc) > 200 else doc,
            )
            chunks.append(chunk_info)

        conn.close()

        return ChunksResponse(
            chunks=chunks,
            total_count=len(chunks),
            filtered_count=len(chunks),
            metadata={
                "filters": filter.dict(),
                "query_executed": query.replace("  ", " ").strip(),
            },
        )
    except Exception as e:
        log.error(f"Error viewing chunks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# PDF Ingestion Endpoint
@app.post("/rag/ingest_pdf", response_model=IngestStatus)
async def ingest_pdf(request: PDFIngestRequest):
    """Ingest a PDF document into the RAG system."""
    start_time = time.time()

    # Log to Maat Memory
    maat_memory = get_maat_memory()

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
            max_chunk_size=request.chunk_size or 1000,
            min_chunk_size=200,
            skip_front_pages=request.skip_front_pages or 5,
        )

        # Load and process PDF
        documents = processor.load_pdf(request.pdf_path)
        if not documents:
            raise HTTPException(
                status_code=400, detail=f"Failed to load PDF: {request.pdf_path}"
            )

        # Process documents
        collection_name = request.collection_name or Path(request.pdf_path).stem
        success = processor.process_documents(documents, collection_name)

        processing_time = time.time() - start_time

        if success:
            status_response = IngestStatus(
                status="success",
                message=f"PDF {request.pdf_path} ingested successfully",
                pdf_name=os.path.basename(request.pdf_path),
                chunks_created=len(documents),
                processing_time=processing_time,
            )

            # Log to Maat memory
            if maat_memory:
                try:
                    maat_memory.log_change(
                        agent="api",
                        file_path=request.pdf_path,
                        change_type="created",
                        summary=f"Ingested PDF: {os.path.basename(request.pdf_path)} with {len(documents)} chunks",
                        reason=f"User requested PDF ingestion via API",
                    )
                    maat_memory.log_audit(
                        agent="api",
                        action="pdf_ingestion",
                        resource=request.pdf_path,
                        reason=f"Ingested {len(documents)} chunks into {request.collection_name or 'default'}",
                        maat_compliance={
                            "truth": True,
                            "balance": True,
                            "order": True,
                            "self_reflection": True,
                        },
                    )
                except Exception as e:
                    log.warning(f"Failed to log to Maat memory: {e}")

            return status_response
        else:
            status_response = IngestStatus(
                status="error",
                message=f"Failed to process PDF: {request.pdf_path}",
                pdf_name=os.path.basename(request.pdf_path),
                processing_time=processing_time,
                error_details="Processing failed during document processing",
            )

            # Log error to Maat memory
            if maat_memory:
                try:
                    maat_memory.log_error(
                        agent="api",
                        error_type="PDFIngestionError",
                        message="Processing failed during document processing",
                        context={"pdf_path": request.pdf_path},
                    )
                except:
                    pass

            return status_response
    except Exception as e:
        processing_time = time.time() - start_time
        log.error(f"Error ingesting PDF: {e}")

        status_response = IngestStatus(
            status="error",
            message=f"Error ingesting PDF: {request.pdf_path}",
            pdf_name=os.path.basename(request.pdf_path),
            processing_time=processing_time,
            error_details=str(e),
        )

        # Log error to Maat Memory
        if maat_memory:
            try:
                maat_memory.log_error(
                    agent="api",
                    error_type="PDFIngestionException",
                    message=str(e),
                    context={"pdf_path": request.pdf_path},
                    stack_trace=None,
                )
            except:
                pass

        return status_response


# Statistics Endpoint
@app.get("/rag/stats")
async def get_stats(collection_name: str = "maat_knowledge"):
    """Get statistics about the RAG system."""
    try:
        PGVECTOR_DB_URL = get_pgvector_url()
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
        PGVECTOR_DB_URL = get_pgvector_url()
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
            chunk_count = cur.fetchone()[0] if cur.fetchone() else 0

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
