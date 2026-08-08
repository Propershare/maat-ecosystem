"""
Redis Connection Pool
Shared infrastructure for caching
Maat: Balance - Efficient resource usage through caching
"""

import logging
from typing import Optional
import redis
from redis.connection import ConnectionPool

from config.shared_config import get_shared_config

log = logging.getLogger(__name__)

# Global Redis connection pool
_redis_pool: Optional[ConnectionPool] = None
_redis_client: Optional[redis.Redis] = None


def get_redis_pool() -> Optional[ConnectionPool]:
    """Get or create Redis connection pool."""
    global _redis_pool
    
    config = get_shared_config()
    
    if not config.redis_enabled:
        log.debug("Redis not enabled in configuration")
        return None
    
    if _redis_pool is None:
        try:
            # Parse Redis URL if provided, otherwise use defaults
            if config.redis_url:
                _redis_pool = ConnectionPool.from_url(
                    config.redis_url,
                    max_connections=50,
                    decode_responses=True,
                )
            else:
                # Default to localhost
                _redis_pool = ConnectionPool(
                    host="localhost",
                    port=6379,
                    db=0,
                    max_connections=50,
                    decode_responses=True,
                )
            
            log.info("Redis connection pool created")
        except Exception as e:
            log.warning(f"Failed to create Redis connection pool: {e}")
            log.warning("Continuing without Redis cache")
            return None
    
    return _redis_pool


def get_redis_client() -> Optional[redis.Redis]:
    """Get Redis client instance."""
    global _redis_client
    
    config = get_shared_config()
    
    if not config.redis_enabled:
        return None
    
    if _redis_client is None:
        pool = get_redis_pool()
        if pool:
            _redis_client = redis.Redis(connection_pool=pool)
            # Test connection
            try:
                _redis_client.ping()
                log.info("Redis client connected")
            except Exception as e:
                log.warning(f"Redis connection test failed: {e}")
                _redis_client = None
                return None
    
    return _redis_client


def cache_get(key: str) -> Optional[str]:
    """Get value from Redis cache."""
    client = get_redis_client()
    if not client:
        return None
    
    try:
        return client.get(key)
    except Exception as e:
        log.debug(f"Redis cache get failed: {e}")
        return None


def cache_set(key: str, value: str, ttl: Optional[int] = None) -> bool:
    """Set value in Redis cache."""
    client = get_redis_client()
    if not client:
        return False
    
    config = get_shared_config()
    ttl = ttl or config.redis_cache_ttl
    
    try:
        client.setex(key, ttl, value)
        return True
    except Exception as e:
        log.debug(f"Redis cache set failed: {e}")
        return False


def cache_delete(key: str) -> bool:
    """Delete key from Redis cache."""
    client = get_redis_client()
    if not client:
        return False
    
    try:
        client.delete(key)
        return True
    except Exception as e:
        log.debug(f"Redis cache delete failed: {e}")
        return False

