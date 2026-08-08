"""
Three-Ring Classification System
Maat: Order - Structured access control and content classification
"""

import logging
from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

log = logging.getLogger(__name__)


class RingClassification(str, Enum):
    """Three-ring classification levels."""
    INNER = "inner"  # Canon - verified, immutable
    MIDDLE = "middle"  # Scholarship - interpreted, curated
    OUTER = "outer"  # Monetized - remixed, commercial


@dataclass
class ClassificationResult:
    """Result of three-ring classification."""
    ring: RingClassification
    confidence: float  # 0.0 to 1.0
    reasoning: str
    metadata: Dict[str, Any]


class ThreeRingClassifier:
    """
    Classifies content into three rings based on Maat principles.
    
    Inner Ring (Canon):
    - Verified methodologies
    - Immutable truths
    - Core principles
    - Source: Maat graphs, UKMT texts, verified claims
    
    Middle Ring (Scholarship):
    - Interpretations
    - Curated knowledge
    - Research notes
    - Source: RBG Library, methodology templates
    
    Outer Ring (Monetized):
    - Remixed content
    - Commercial applications
    - User-generated content
    - Source: Content jobs, workflows, scripts
    """
    
    def __init__(self):
        self.inner_keywords = [
            "canon", "verified", "immutable", "truth", "principle",
            "maat graph", "ukmt", "sacred", "foundational"
        ]
        self.middle_keywords = [
            "interpretation", "curated", "research", "scholarship",
            "rbg library", "methodology", "template", "analysis"
        ]
        self.outer_keywords = [
            "remix", "commercial", "monetized", "workflow", "script",
            "content job", "user-generated", "application"
        ]
    
    def classify(
        self,
        content: str,
        source: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ClassificationResult:
        """
        Classify content into three rings.
        
        Args:
            content: Content text to classify
            source: Source identifier (file path, URL, etc.)
            metadata: Additional metadata for classification
        
        Returns:
            ClassificationResult with ring, confidence, and reasoning
        """
        content_lower = content.lower()
        source_lower = (source or "").lower()
        
        # Check source path patterns
        if self._is_inner_source(source_lower):
            return ClassificationResult(
                ring=RingClassification.INNER,
                confidence=0.9,
                reasoning=f"Source path indicates Inner Ring: {source}",
                metadata=metadata or {}
            )
        
        if self._is_middle_source(source_lower):
            return ClassificationResult(
                ring=RingClassification.MIDDLE,
                confidence=0.85,
                reasoning=f"Source path indicates Middle Ring: {source}",
                metadata=metadata or {}
            )
        
        if self._is_outer_source(source_lower):
            return ClassificationResult(
                ring=RingClassification.OUTER,
                confidence=0.85,
                reasoning=f"Source path indicates Outer Ring: {source}",
                metadata=metadata or {}
            )
        
        # Check content keywords
        inner_score = sum(1 for kw in self.inner_keywords if kw in content_lower)
        middle_score = sum(1 for kw in self.middle_keywords if kw in content_lower)
        outer_score = sum(1 for kw in self.outer_keywords if kw in content_lower)
        
        total_score = inner_score + middle_score + outer_score
        
        if total_score == 0:
            # Default to middle ring if no indicators
            return ClassificationResult(
                ring=RingClassification.MIDDLE,
                confidence=0.5,
                reasoning="No clear indicators, defaulting to Middle Ring",
                metadata=metadata or {}
            )
        
        # Determine ring based on highest score
        if inner_score >= middle_score and inner_score >= outer_score:
            confidence = min(0.9, 0.5 + (inner_score / max(total_score, 1)) * 0.4)
            return ClassificationResult(
                ring=RingClassification.INNER,
                confidence=confidence,
                reasoning=f"Inner Ring indicators found (score: {inner_score})",
                metadata=metadata or {}
            )
        elif middle_score >= outer_score:
            confidence = min(0.85, 0.5 + (middle_score / max(total_score, 1)) * 0.35)
            return ClassificationResult(
                ring=RingClassification.MIDDLE,
                confidence=confidence,
                reasoning=f"Middle Ring indicators found (score: {middle_score})",
                metadata=metadata or {}
            )
        else:
            confidence = min(0.85, 0.5 + (outer_score / max(total_score, 1)) * 0.35)
            return ClassificationResult(
                ring=RingClassification.OUTER,
                confidence=confidence,
                reasoning=f"Outer Ring indicators found (score: {outer_score})",
                metadata=metadata or {}
            )
    
    def _is_inner_source(self, source: str) -> bool:
        """Check if source indicates Inner Ring."""
        inner_patterns = [
            "maat-graph", "maat_graph", "ukmt", "canon", "sacred",
            "verified", "foundational", "immutable"
        ]
        return any(pattern in source for pattern in inner_patterns)
    
    def _is_middle_source(self, source: str) -> bool:
        """Check if source indicates Middle Ring."""
        middle_patterns = [
            "rbg-library", "rbg_library", "methodology", "research",
            "scholarship", "curated", "template"
        ]
        return any(pattern in source for pattern in middle_patterns)
    
    def _is_outer_source(self, source: str) -> bool:
        """Check if source indicates Outer Ring."""
        outer_patterns = [
            "monetization", "workflow", "script", "content-job",
            "commercial", "remix", "user-generated"
        ]
        return any(pattern in source for pattern in outer_patterns)
    
    def can_access(
        self,
        user_ring: RingClassification,
        content_ring: RingClassification
    ) -> bool:
        """
        Check if user can access content based on ring classification.
        
        Rules:
        - Inner Ring: Only Inner Ring users
        - Middle Ring: Inner and Middle Ring users
        - Outer Ring: All users
        """
        if content_ring == RingClassification.INNER:
            return user_ring == RingClassification.INNER
        elif content_ring == RingClassification.MIDDLE:
            return user_ring in [RingClassification.INNER, RingClassification.MIDDLE]
        else:  # OUTER
            return True  # All users can access Outer Ring

