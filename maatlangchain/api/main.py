"""
Active FastAPI entrypoint for tooling that imports `api.main`.

`rag_query_helper` and scripts expect `from api.main import get_rag_instance`.
"""
from api.main_original import app, get_rag_instance

__all__ = ["app", "get_rag_instance"]
