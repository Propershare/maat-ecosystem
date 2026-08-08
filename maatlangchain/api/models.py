"""
Pydantic models for MaatLangChain FastAPI endpoints
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime


class RAGQueryRequest(BaseModel):
    """Request model for RAG queries."""

    question: str = Field(
        ..., description="Question to ask the RAG system", min_length=1
    )
    top_k: Optional[int] = Field(
        5, description="Number of top results to retrieve", ge=1, le=50
    )
    collection_name: Optional[str] = Field(
        "maat_knowledge", description="Collection name to search"
    )
    min_score: Optional[float] = Field(
        0.0, description="Minimum similarity score", ge=0.0, le=1.0
    )


class DocumentSource(BaseModel):
    """Source document information."""

    file_name: str = Field(..., description="Source PDF file name")
    page: Union[int, str] = Field(..., description="Page number")
    file_path: Optional[str] = Field(None, description="Full path to source file")
    preview: str = Field(..., description="Preview of the content")
    score: Optional[float] = Field(None, description="Similarity score")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class RAGQueryResponse(BaseModel):
    """Response model for RAG queries."""

    answer: str = Field(..., description="Answer to the question")
    sources: List[DocumentSource] = Field(..., description="Source documents used")
    metadata: Dict[str, Any] = Field(
        ..., description="Additional metadata about the query"
    )
    query_time: Optional[float] = Field(
        None, description="Time taken for query in seconds"
    )


class ChunkFilter(BaseModel):
    """Filter options for viewing chunks."""

    pdf_name: Optional[str] = Field(None, description="Filter by specific PDF name")
    page_numbers: Optional[List[Union[int, str]]] = Field(
        None, description="Filter by page numbers"
    )
    min_length: Optional[int] = Field(50, description="Minimum chunk length", ge=1)
    skip_toc: Optional[bool] = Field(True, description="Skip table of contents chunks")
    limit: Optional[int] = Field(
        10, description="Maximum number of chunks to return", ge=1, le=1000
    )


class ChunkInfo(BaseModel):
    """Information about a document chunk."""

    chunk_id: str = Field(..., description="Unique chunk identifier")
    content: str = Field(..., description="Chunk content")
    pdf_name: str = Field(..., description="Source PDF file name")
    page: Union[int, str] = Field(..., description="Page number")
    metadata: Dict[str, Any] = Field(..., description="Chunk metadata")
    preview: str = Field(..., description="Short preview of content")


class ChunksResponse(BaseModel):
    """Response model for chunks endpoint."""

    chunks: List[ChunkInfo] = Field(..., description="List of chunks")
    total_count: int = Field(
        ..., description="Total number of chunks matching criteria"
    )
    filtered_count: int = Field(..., description="Number of chunks after filtering")
    metadata: Dict[str, Any] = Field(..., description="Additional metadata")


class PDFIngestRequest(BaseModel):
    """Request model for PDF ingestion."""

    pdf_path: str = Field(..., description="Path to PDF file to ingest")
    collection_name: Optional[str] = Field(
        None, description="Collection name (defaults to filename)"
    )
    chunk_size: Optional[int] = Field(
        1000, description="Chunk size for processing", ge=100, le=5000
    )
    chunk_overlap: Optional[int] = Field(
        200, description="Chunk overlap", ge=0, le=1000
    )
    skip_front_pages: Optional[int] = Field(
        5, description="Skip first N pages", ge=0, le=20
    )


class IngestStatus(BaseModel):
    """Status of PDF ingestion process."""

    status: str = Field(..., description="Status: success, error, processing")
    message: str = Field(..., description="Status message")
    pdf_name: str = Field(..., description="PDF file name")
    chunks_created: Optional[int] = Field(None, description="Number of chunks created")
    processing_time: Optional[float] = Field(
        None, description="Processing time in seconds"
    )
    error_details: Optional[str] = Field(
        None, description="Error details if status is error"
    )


class CollectionStats(BaseModel):
    """Statistics for a collection."""

    name: str = Field(..., description="Collection name")
    chunk_count: int = Field(..., description="Number of chunks in collection")
    last_updated: Optional[datetime] = Field(None, description="Last update timestamp")
    pdf_count: int = Field(..., description="Number of PDFs in collection")
    avg_chunk_size: Optional[float] = Field(
        None, description="Average chunk size in characters"
    )


class SystemStats(BaseModel):
    """System-wide statistics."""

    total_chunks: int = Field(..., description="Total chunks across all collections")
    total_pdfs: int = Field(..., description="Total PDFs processed")
    collections: List[CollectionStats] = Field(
        ..., description="Statistics per collection"
    )
    database_status: str = Field(..., description="Database connection status")
    last_ingestion: Optional[datetime] = Field(
        None, description="Last PDF ingestion timestamp"
    )


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Health status: healthy, unhealthy")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Health check timestamp"
    )
    database_connected: bool = Field(..., description="Database connection status")
    embeddings_ready: bool = Field(..., description="Embeddings model status")
    uptime_seconds: Optional[float] = Field(
        None, description="Server uptime in seconds"
    )
    version: str = Field("1.0.0", description="API version")


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(
        None, description="Additional error details"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Error timestamp"
    )
