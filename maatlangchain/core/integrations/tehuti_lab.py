"""
Tehuti Lab Integration for MaatLangChain

Integration with Tehuti Lab for optimized vector stores and embeddings.
Includes GPU optimization and batch processing capabilities.

Updated for LangChain 0.2.x compatibility.
"""

import logging
import os
from typing import Optional, Dict, Any, Union
from pathlib import Path

# Updated LangChain imports (no deprecation warnings)
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

# For vector stores, use conditional imports to avoid missing dependencies
try:
    from langchain_chroma import Chroma

    CHROMA_AVAILABLE = True
except ImportError:
    try:
        from langchain_community.vectorstores import Chroma

        CHROMA_AVAILABLE = True
    except ImportError:
        CHROMA_AVAILABLE = False
        Chroma = None

try:
    from langchain_community.vectorstores import FAISS

    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    FAISS = None

log = logging.getLogger(__name__)


def get_vector_store(
    vector_store_type: str = "chroma",
    persist_directory: str = "./chroma_db_maat",
    collection_name: str = "maat_rbg",
    **kwargs,
) -> Optional[Union[Chroma, FAISS]]:
    """
    Get optimized vector store instance.

    Args:
        vector_store_type: Type of vector store ('chroma', 'faiss')
        persist_directory: Directory for persistent storage
        collection_name: Name of the collection
        **kwargs: Additional vector store parameters

    Returns:
        Configured vector store instance
    """
    try:
        if vector_store_type.lower() == "chroma":
            if not CHROMA_AVAILABLE:
                log.error(
                    "Chroma not available. Install with: pip install langchain-chroma"
                )
                return None

            # Filter kwargs to remove invalid parameters
            valid_kwargs = {
                k: v
                for k, v in kwargs.items()
                if k not in ["batch_size", "embedding_function"]
            }

            vector_store = Chroma(
                collection_name=collection_name,
                persist_directory=persist_directory,
                **valid_kwargs,
            )
        elif vector_store_type.lower() == "faiss":
            if not FAISS_AVAILABLE:
                log.error("FAISS not available. Install with: pip install faiss-cpu")
                return None

            # For FAISS, we need an existing index or create new one
            index_path = Path(persist_directory) / f"{collection_name}.faiss"
            if index_path.exists():
                embeddings = kwargs.get("embeddings")
                vector_store = FAISS.load_local(
                    str(index_path.parent),
                    embeddings=embeddings,
                    index_name=index_path.stem,
                )
            else:
                # Create new FAISS index (will need embeddings later)
                vector_store = None
                log.warning(
                    "FAISS index not found, will be created when adding documents"
                )
        else:
            raise ValueError(f"Unsupported vector store type: {vector_store_type}")

        log.info(f"Created {vector_store_type} vector store: {collection_name}")
        return vector_store

    except Exception as e:
        log.error(f"Failed to create vector store: {e}")
        return None


def get_optimized_embeddings(
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
    device: str = "cpu",  # Changed to CPU for safety
    batch_size: int = 32,
    normalize_embeddings: bool = True,
    **kwargs,
) -> HuggingFaceEmbeddings:
    """
    Get optimized embeddings with GPU support and batch processing.

    Args:
        embedding_model: Name of embedding model
        device: Device to use ('cpu', 'cuda', 'auto') - defaults to CPU for safety
        batch_size: Batch size for embedding generation
        normalize_embeddings: Whether to normalize embeddings
        **kwargs: Additional embedding parameters

    Returns:
        Optimized embeddings instance
    """
    try:
        # Auto-detect device if set to 'auto'
        if device == "auto":
            try:
                import torch

                device = "cuda" if torch.cuda.is_available() else "cpu"
                log.info(f"Auto-detected device: {device}")
            except ImportError:
                device = "cpu"
                log.info("PyTorch not available, using CPU")

        # Use langchain_huggingface for updated compatibility
        # Note: New HuggingFaceEmbeddings doesn't accept 'device' in model_kwargs
        # It uses separate 'model_kwargs' and 'encode_kwargs'

        # For GPU/CPU selection, we need to set device differently now
        if device == "cuda":
            # Set device environment variable for sentence-transformers
            import os

            os.environ["CUDA_VISIBLE_DEVICES"] = "0"
            log.info("GPU optimization enabled for embeddings")
        else:
            log.info("Using CPU for embeddings (safer for development)")

        # Create embeddings with correct parameters
        embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            encode_kwargs={
                "batch_size": batch_size,
                "normalize_embeddings": normalize_embeddings,
            },
        )

        log.info(f"Created HuggingFace embeddings: {embedding_model}")
        log.info(f"  Device: {device}")
        log.info(f"  Batch size: {batch_size}")
        log.info(f"  Normalize: {normalize_embeddings}")

        return embeddings

    except Exception as e:
        log.error(f"Failed to create embeddings: {e}")
        # Fallback to basic embeddings
        return HuggingFaceEmbeddings(model_name=embedding_model)


def create_tehuti_vector_store(
    vector_store_type: str = "chroma",
    persist_directory: str = "./chroma_db_maat",
    collection_name: str = "maat_rbg",
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
    device: str = "cpu",  # Default to CPU for safety
    **kwargs,
):
    """
    Create Tehuti-optimized vector store with embeddings.

    Args:
        vector_store_type: Type of vector store ('chroma', 'faiss')
        persist_directory: Directory for persistent storage
        collection_name: Name for the collection
        embedding_model: Name of embedding model
        device: Device to use for embeddings (defaults to CPU)
        **kwargs: Additional parameters

    Returns:
        Tuple of (vector_store, embeddings)
    """
    # Get optimized embeddings
    embeddings = get_optimized_embeddings(
        embedding_model=embedding_model, device=device, **kwargs
    )

    # Get vector store
    vector_store = get_vector_store(
        vector_store_type=vector_store_type,
        persist_directory=persist_directory,
        collection_name=collection_name,
        embedding_function=embeddings,
        **kwargs,
    )

    log.info(f"Created Tehuti-optimized vector store: {collection_name}")
    return vector_store, embeddings


def optimize_vector_store_for_gpu(vector_store, device: str = "cpu"):
    """
    Optimize vector store for GPU usage.

    Args:
        vector_store: Vector store instance
        device: Target device

    Returns:
        Optimized vector store
    """
    try:
        if hasattr(vector_store, "_collection") and device == "cuda":
            # Chroma optimizations for GPU
            log.info("Optimizing Chroma vector store for GPU")
            # Chroma doesn't have direct GPU support, but we can optimize the embeddings

        elif hasattr(vector_store, "index") and device == "cuda":
            # FAISS GPU optimizations
            log.info("Optimizing FAISS vector store for GPU")
            try:
                import faiss

                if hasattr(vector_store.index, "to_gpu"):
                    vector_store.index = vector_store.index.to_gpu()
                    log.info("FAISS index moved to GPU")
            except ImportError:
                log.warning("FAISS GPU not available")

        return vector_store

    except Exception as e:
        log.error(f"Failed to optimize vector store: {e}")
        return vector_store


def get_tehuti_config() -> Dict[str, Any]:
    """
    Get Tehuti Lab configuration.

    Returns:
        Dictionary containing Tehuti configuration
    """
    config = {
        "embedding_model": os.getenv(
            "TEHUTI_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
        ),
        "device": os.getenv("TEHUTI_DEVICE", "cpu"),  # Default to CPU for safety
        "batch_size": int(os.getenv("TEHUTI_BATCH_SIZE", "32")),
        "vector_store_type": os.getenv("TEHUTI_VECTOR_STORE", "chroma"),
        "persist_directory": os.getenv("TEHUTI_PERSIST_DIR", "./chroma_db_maat"),
        "collection_name": os.getenv("TEHUTI_COLLECTION", "maat_rbg"),
        "normalize_embeddings": os.getenv("TEHUTI_NORMALIZE", "true").lower() == "true",
        "gpu_optimization": os.getenv("TEHUTI_GPU_OPT", "false").lower()
        == "true",  # Default to False
    }

    log.info(f"Tehuti config: {config}")
    return config


def setup_tehuti_environment():
    """
    Setup Tehuti Lab environment with optimizations.
    """
    try:
        # Set environment variables for optimal performance
        os.environ["TOKENIZERS_PARALLELISM"] = "false"  # Avoid tokenizer warnings

        # Optimize for PyTorch if available
        try:
            import torch

            if torch.cuda.is_available():
                torch.cuda.empty_cache()  # Clear GPU cache
                os.environ["CUDA_VISIBLE_DEVICES"] = "0"  # Use first GPU
                log.info("GPU environment optimized for Tehuti")
        except ImportError:
            log.info("PyTorch not available, using CPU optimizations")

        log.info("Tehuti environment setup complete")

    except Exception as e:
        log.error(f"Failed to setup Tehuti environment: {e}")


# Auto-setup Tehuti environment when imported
setup_tehuti_environment()
