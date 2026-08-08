"""
PostgreSQL Connection Pool
Shared infrastructure for MaatLangChain and MaatCode
Maat: Order - Centralized connection management
"""

import logging
from typing import Optional
import psycopg2
from psycopg2 import pool
from psycopg2.extensions import connection
from contextlib import contextmanager

from config.shared_config import get_shared_config

log = logging.getLogger(__name__)

# Global connection pool
_postgres_pool: Optional[pool.ThreadedConnectionPool] = None


def get_postgres_pool() -> pool.ThreadedConnectionPool:
    """Get or create PostgreSQL connection pool."""
    global _postgres_pool
    
    if _postgres_pool is None:
        config = get_shared_config()
        
        # Parse connection string
        # Format: postgresql://user:password@host:port/database
        import urllib.parse
        parsed = urllib.parse.urlparse(config.postgres_url)
        
        pool_config = {
            "minconn": 1,
            "maxconn": config.postgres_pool_size + config.postgres_max_overflow,
            "host": parsed.hostname,
            "port": parsed.port or 5432,
            "database": parsed.path.lstrip("/"),
            "user": parsed.username,
            "password": parsed.password,
        }
        
        try:
            _postgres_pool = pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=pool_config["maxconn"],
                host=pool_config["host"],
                port=pool_config["port"],
                database=pool_config["database"],
                user=pool_config["user"],
                password=pool_config["password"],
            )
            log.info(
                f"PostgreSQL connection pool created: "
                f"{pool_config['minconn']}-{pool_config['maxconn']} connections"
            )
        except Exception as e:
            log.error(f"Failed to create PostgreSQL connection pool: {e}")
            raise
    
    return _postgres_pool


@contextmanager
def get_postgres_connection():
    """Get a connection from the pool (context manager)."""
    pool = get_postgres_pool()
    conn = None
    try:
        conn = pool.getconn()
        yield conn
    except Exception as e:
        if conn:
            conn.rollback()
        log.error(f"PostgreSQL connection error: {e}")
        raise
    finally:
        if conn:
            pool.putconn(conn)


def close_postgres_pool():
    """Close the PostgreSQL connection pool."""
    global _postgres_pool
    if _postgres_pool:
        _postgres_pool.closeall()
        _postgres_pool = None
        log.info("PostgreSQL connection pool closed")

