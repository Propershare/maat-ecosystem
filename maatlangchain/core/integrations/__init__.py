"""
Shared Infrastructure Integrations
PostgreSQL, Redis, Ollama connection pools and clients
"""

from .postgres import (
    get_postgres_pool,
    get_postgres_connection,
    close_postgres_pool,
)
from .redis import (
    get_redis_pool,
    get_redis_client,
    cache_get,
    cache_set,
    cache_delete,
)
from .ollama import (
    OllamaClient,
    get_ollama_client,
)

__all__ = [
    # PostgreSQL
    "get_postgres_pool",
    "get_postgres_connection",
    "close_postgres_pool",
    # Redis
    "get_redis_pool",
    "get_redis_client",
    "cache_get",
    "cache_set",
    "cache_delete",
    # Ollama
    "OllamaClient",
    "get_ollama_client",
]

