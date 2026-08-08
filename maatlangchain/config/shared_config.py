"""
Shared Configuration Management
Maat: Order - Centralized configuration for consistency
"""

import os
import logging
from typing import Optional, Dict, Any
from pathlib import Path
from dataclasses import dataclass

log = logging.getLogger(__name__)


@dataclass
class SharedConfig:
    """Shared configuration for MaatLangChain and Tehuti Lab."""
    
    # PostgreSQL Configuration
    postgres_url: str
    postgres_pool_size: int = 10
    postgres_max_overflow: int = 20
    postgres_pool_recycle: int = 3600
    
    # Redis Configuration
    redis_url: Optional[str] = None
    redis_enabled: bool = False
    redis_cache_ttl: int = 3600  # 1 hour default
    
    # Ollama Configuration
    ollama_base_url: str = "http://localhost:11434"
    ollama_default_model: str = "qwen2.5:14b"
    ollama_timeout: int = 120
    
    # Embedding Configuration
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_device: str = "cpu"
    embedding_batch_size: int = 32
    
    # MaatCode Configuration
    maatcode_cache_enabled: bool = True
    maatcode_max_context_size: int = 1000000  # 1M tokens
    
    @classmethod
    def from_env(cls) -> "SharedConfig":
        """Load configuration from environment variables."""
        # PostgreSQL
        postgres_url = os.getenv("PGVECTOR_DB_URL")
        if not postgres_url:
            # Try to find in common locations
            postgres_url = _find_postgres_url()
        
        if not postgres_url:
            raise ValueError(
                "PGVECTOR_DB_URL not set. Required for shared infrastructure."
            )
        
        # Redis
        redis_url = os.getenv("REDIS_URL")
        redis_enabled = redis_url is not None
        
        # Ollama
        ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        ollama_default_model = os.getenv("OLLAMA_DEFAULT_MODEL", "qwen2.5:14b")
        
        # Embeddings
        embedding_model = os.getenv(
            "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
        )
        embedding_device = os.getenv("EMBEDDING_DEVICE", "cpu")
        
        return cls(
            postgres_url=postgres_url,
            postgres_pool_size=int(os.getenv("POSTGRES_POOL_SIZE", "10")),
            postgres_max_overflow=int(os.getenv("POSTGRES_MAX_OVERFLOW", "20")),
            postgres_pool_recycle=int(os.getenv("POSTGRES_POOL_RECYCLE", "3600")),
            redis_url=redis_url,
            redis_enabled=redis_enabled,
            redis_cache_ttl=int(os.getenv("REDIS_CACHE_TTL", "3600")),
            ollama_base_url=ollama_base_url,
            ollama_default_model=ollama_default_model,
            ollama_timeout=int(os.getenv("OLLAMA_TIMEOUT", "120")),
            embedding_model=embedding_model,
            embedding_device=embedding_device,
            embedding_batch_size=int(os.getenv("EMBEDDING_BATCH_SIZE", "32")),
            maatcode_cache_enabled=os.getenv("MAATCODE_CACHE_ENABLED", "true").lower() == "true",
            maatcode_max_context_size=int(os.getenv("MAATCODE_MAX_CONTEXT_SIZE", "1000000")),
        )


def _find_postgres_url() -> Optional[str]:
    """Try to find PostgreSQL URL from common locations."""
    # Check environment
    url = os.getenv("PGVECTOR_DB_URL")
    if url:
        return url
    
    # Check .env files
    env_files = [
        Path.home() / ".n8n" / "open-webui" / ".env",
        Path.home() / ".n8n" / "maatlangchain" / ".env",
        Path.cwd() / ".env",
    ]
    
    for env_file in env_files:
        if env_file.exists():
            try:
                with open(env_file, "r") as f:
                    for line in f:
                        if line.startswith("PGVECTOR_DB_URL="):
                            url = line.split("=", 1)[1].strip().strip('"').strip("'")
                            if url:
                                return url
            except Exception:
                continue
    
    # Check .bashrc
    bashrc = Path.home() / ".bashrc"
    if bashrc.exists():
        try:
            with open(bashrc, "r") as f:
                for line in f:
                    if line.strip().startswith("export PGVECTOR_DB_URL="):
                        url = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if url:
                            return url
        except Exception:
            pass
    
    return None


# Global config instance
_shared_config: Optional[SharedConfig] = None


def get_shared_config() -> SharedConfig:
    """Get or create shared configuration instance."""
    global _shared_config
    if _shared_config is None:
        _shared_config = SharedConfig.from_env()
        log.info("Shared configuration loaded")
    return _shared_config

