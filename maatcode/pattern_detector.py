"""
Pattern Detection for Code
Maat: Order - Identify patterns and anti-patterns
"""

import logging
from typing import List, Dict, Any, Optional
import re

from core.maatcode.semantic_search import SemanticCodeSearch

log = logging.getLogger(__name__)


class PatternDetector:
    """
    Detects patterns and anti-patterns in codebase.
    
    Uses semantic search to find similar code patterns.
    """
    
    def __init__(self):
        self.search = SemanticCodeSearch()
        
        # Common patterns to detect
        self.patterns = {
            "security": [
                "sql injection",
                "xss",
                "csrf",
                "authentication",
                "authorization",
                "password",
                "secret",
                "api key"
            ],
            "performance": [
                "n+1 query",
                "slow query",
                "inefficient loop",
                "memory leak",
                "bottleneck"
            ],
            "maat_compliance": [
                "truth",
                "balance",
                "order",
                "justice",
                "self-reflection",
                "three-ring",
                "governance"
            ],
            "anti_patterns": [
                "god object",
                "spaghetti code",
                "code smell",
                "technical debt"
            ]
        }
    
    def detect_patterns(
        self,
        codebase_path: str,
        pattern_types: Optional[List[str]] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Detect patterns in codebase.
        
        Args:
            codebase_path: Path to codebase
            pattern_types: Types of patterns to detect (security, performance, etc.)
        
        Returns:
            Dictionary of pattern types to detected instances
        """
        if pattern_types is None:
            pattern_types = list(self.patterns.keys())
        
        detected = {}
        
        for pattern_type in pattern_types:
            if pattern_type not in self.patterns:
                continue
            
            detected[pattern_type] = []
            
            for pattern_query in self.patterns[pattern_type]:
                results = self.search.search(
                    query=pattern_query,
                    top_k=5
                )
                
                for result in results:
                    detected[pattern_type].append({
                        "pattern": pattern_query,
                        "file": result["file_path"],
                        "code": result["code"],
                        "similarity": result["similarity"],
                        "line_start": result.get("line_start"),
                        "line_end": result.get("line_end")
                    })
        
        return detected
    
    def find_duplicate_code(
        self,
        code: str,
        language: Optional[str] = None,
        threshold: float = 0.85
    ) -> List[Dict[str, Any]]:
        """
        Find duplicate or very similar code.
        
        Args:
            code: Code snippet to check
            language: Programming language
            threshold: Similarity threshold
        
        Returns:
            List of similar code snippets
        """
        results = self.search.find_similar_code(
            code=code,
            language=language,
            top_k=20
        )
        
        # Filter by threshold
        duplicates = [
            r for r in results
            if r["similarity"] >= threshold
        ]
        
        return duplicates
    
    def detect_security_issues(
        self,
        codebase_path: str
    ) -> List[Dict[str, Any]]:
        """
        Detect potential security issues.
        
        Args:
            codebase_path: Path to codebase
        
        Returns:
            List of security issues found
        """
        patterns = self.detect_patterns(codebase_path, ["security"])
        return patterns.get("security", [])
    
    def detect_maat_compliance(
        self,
        codebase_path: str
    ) -> List[Dict[str, Any]]:
        """
        Detect Maat compliance patterns.
        
        Args:
            codebase_path: Path to codebase
        
        Returns:
            List of Maat compliance instances
        """
        patterns = self.detect_patterns(codebase_path, ["maat_compliance"])
        return patterns.get("maat_compliance", [])

