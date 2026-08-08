"""
Semantic Code Search
Maat: Truth - Find relevant code using semantic understanding
"""

import logging
from typing import List, Dict, Any, Optional
import json

from langchain_huggingface import HuggingFaceEmbeddings

from core.integrations.postgres import get_postgres_connection
from config.shared_config import get_shared_config

log = logging.getLogger(__name__)


class SemanticCodeSearch:
    """
    Semantic search for code using vector embeddings.
    
    Finds relevant code snippets based on semantic similarity.
    """
    
    def __init__(self, embedding_model: Optional[str] = None):
        config = get_shared_config()
        self.embedding_model = embedding_model or config.embedding_model
        
        # Initialize embeddings (same model as embedder)
        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.embedding_model,
            encode_kwargs={
                "batch_size": config.embedding_batch_size,
                "normalize_embeddings": True,
            },
        )
    
    def search(
        self,
        query: str,
        top_k: int = 10,
        language: Optional[str] = None,
        file_path: Optional[str] = None,
        min_similarity: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant code snippets.
        
        Args:
            query: Search query
            top_k: Number of results to return
            language: Filter by programming language
            file_path: Filter by file path pattern
            min_similarity: Minimum similarity score (0-1)
        
        Returns:
            List of code snippets with similarity scores
        """
        try:
            # Generate query embedding
            query_embedding = self.embeddings.embed_query(query)
            
            # Build query
            conditions = []
            params = []
            
            if language:
                conditions.append("language = %s")
                params.append(language)
            
            if file_path:
                conditions.append("file_path LIKE %s")
                params.append(f"%{file_path}%")
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            # Vector similarity search
            with get_postgres_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(f"""
                        SELECT 
                            id, file_path, code_snippet, language,
                            function_name, class_name, line_start, line_end,
                            metadata,
                            1 - (embedding <=> %s::vector) as similarity
                        FROM maat_code_embeddings
                        WHERE {where_clause}
                        ORDER BY embedding <=> %s::vector
                        LIMIT %s
                    """, params + [str(query_embedding), str(query_embedding), top_k])
                    
                    results = []
                    for row in cur.fetchall():
                        similarity = float(row[9])
                        if similarity >= min_similarity:
                            results.append({
                                "id": str(row[0]),
                                "file_path": row[1],
                                "code": row[2],
                                "language": row[3],
                                "function_name": row[4],
                                "class_name": row[5],
                                "line_start": row[6],
                                "line_end": row[7],
                                "metadata": row[8] if row[8] else {},
                                "similarity": similarity
                            })
                    
                    log.info(f"Found {len(results)} code snippets for query: {query[:50]}")
                    return results
        except Exception as e:
            log.error(f"Failed to search code: {e}")
            return []
    
    def find_similar_code(
        self,
        code: str,
        top_k: int = 10,
        language: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find code similar to given code snippet.
        
        Args:
            code: Code snippet to find similar code for
            top_k: Number of results
            language: Filter by language
        
        Returns:
            List of similar code snippets
        """
        return self.search(
            query=code,
            top_k=top_k,
            language=language,
            min_similarity=0.7  # Higher threshold for code similarity
        )
    
    def find_functions(
        self,
        function_description: str,
        language: Optional[str] = None,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find functions matching description.
        
        Args:
            function_description: Description of function to find
            language: Filter by language
            top_k: Number of results
        
        Returns:
            List of matching functions
        """
        results = self.search(
            query=function_description,
            top_k=top_k * 2,  # Get more, filter to functions
            language=language
        )
        
        # Filter to only functions
        functions = [
            r for r in results
            if r.get("function_name") or "def " in r.get("code", "").lower()
        ]
        
        return functions[:top_k]

