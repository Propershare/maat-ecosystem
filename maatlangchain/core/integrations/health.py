"""
Health Check Endpoints
Maat: Truth - Honest system status reporting
"""

import logging
from typing import Dict, Any
from datetime import datetime

from .postgres import get_postgres_pool, get_postgres_connection
from .redis import get_redis_client
from .ollama import get_ollama_client

log = logging.getLogger(__name__)


def check_postgres_health() -> Dict[str, Any]:
    """Check PostgreSQL connection health."""
    try:
        with get_postgres_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
        
        pool = get_postgres_pool()
        return {
            "status": "healthy",
            "pool_size": pool.maxconn if pool else 0,
            "checked_at": datetime.now().isoformat(),
        }
    except Exception as e:
        log.error(f"PostgreSQL health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "checked_at": datetime.now().isoformat(),
        }


def check_redis_health() -> Dict[str, Any]:
    """Check Redis connection health."""
    client = get_redis_client()
    if not client:
        return {
            "status": "disabled",
            "checked_at": datetime.now().isoformat(),
        }
    
    try:
        client.ping()
        return {
            "status": "healthy",
            "checked_at": datetime.now().isoformat(),
        }
    except Exception as e:
        log.error(f"Redis health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "checked_at": datetime.now().isoformat(),
        }


def check_ollama_health() -> Dict[str, Any]:
    """Check Ollama service health."""
    client = get_ollama_client()
    try:
        is_healthy = client.health_check()
        if is_healthy:
            models = client.list_models()
            return {
                "status": "healthy",
                "models_available": len(models),
                "models": models[:5],  # First 5 models
                "checked_at": datetime.now().isoformat(),
            }
        else:
            return {
                "status": "unhealthy",
                "checked_at": datetime.now().isoformat(),
            }
    except Exception as e:
        log.error(f"Ollama health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "checked_at": datetime.now().isoformat(),
        }


def check_all_health() -> Dict[str, Any]:
    """Check health of all shared infrastructure."""
    return {
        "postgres": check_postgres_health(),
        "redis": check_redis_health(),
        "ollama": check_ollama_health(),
        "checked_at": datetime.now().isoformat(),
    }

