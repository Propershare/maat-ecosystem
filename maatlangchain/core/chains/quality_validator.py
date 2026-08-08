"""
Quality Validation System for OCR and Document Processing
Maat: Truth - Ensure only high-quality content enters the system
"""

import logging
import re
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

log = logging.getLogger(__name__)


class ValidationStatus(str, Enum):
    """Validation status."""
    PASS = "pass"
    REJECT = "reject"
    REVIEW = "review"
    WARN = "warn"


@dataclass
class ValidationResult:
    """Result of quality validation."""
    status: ValidationStatus
    reason: str
    confidence: float = 1.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class QualityValidator:
    """
    Multi-stage quality validation for OCR and document extraction.
    
    Prevents garbage content from entering the RAG system.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize quality validator with configurable thresholds.
        
        Args:
            config: Configuration dictionary with quality thresholds
        """
        self.config = config or self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Default quality thresholds - PRODUCTION-READY."""
        return {
            "ocr_confidence_min": 0.65,         # 65% average confidence (production-tuned)
            "ocr_confidence_min_single": 0.3,   # 30% minimum for any word (allows some noise)
            "readability_letter_ratio": 0.5,    # 50% letters minimum
            "content_min_words": 5,             # Minimum 5 words
            "content_meaningful_words": 3,      # Minimum 3 meaningful words (>3 chars)
            "structure_check_enabled": True,    # Enable structure validation
            "reject_repeated_chars": True,      # Reject repeated character patterns
            "reject_only_symbols": True,        # Reject text with only symbols
            "low_confidence_ratio_threshold": 0.4,  # Flag for review if >40% low confidence
        }
    
    def validate_ocr_confidence(
        self, 
        ocr_result: Dict[str, Any]
    ) -> ValidationResult:
        """
        Validate OCR confidence scores.
        
        Args:
            ocr_result: OCR result with confidence scores
            
        Returns:
            ValidationResult
        """
        avg_confidence = ocr_result.get("avg_confidence", 0.0)
        min_confidence = ocr_result.get("min_confidence", 0.0)
        confidence_scores = ocr_result.get("confidence_scores", [])
        
        # Check average confidence
        if avg_confidence < self.config["ocr_confidence_min"]:
            return ValidationResult(
                status=ValidationStatus.REJECT,
                reason=f"Low OCR confidence: {avg_confidence:.2f} < {self.config['ocr_confidence_min']}",
                confidence=avg_confidence,
                metadata={"avg_confidence": avg_confidence, "threshold": self.config["ocr_confidence_min"]}
            )
        
        # Check minimum confidence (only reject if VERY low AND average is also low)
        if min_confidence < 0.1 and avg_confidence < 0.5:  # Only reject if both are very low
            return ValidationResult(
                status=ValidationStatus.REJECT,
                reason=f"Very low confidence: min {min_confidence:.2f}, avg {avg_confidence:.2f}",
                confidence=min_confidence,
                metadata={"min_confidence": min_confidence, "avg_confidence": avg_confidence}
            )
        elif min_confidence < self.config["ocr_confidence_min_single"] and avg_confidence < self.config["ocr_confidence_min"]:
            # If min is low but avg is acceptable, flag for review
            return ValidationResult(
                status=ValidationStatus.REVIEW,
                reason=f"Some text has low confidence ({min_confidence:.2f}) but average is {avg_confidence:.2f}",
                confidence=avg_confidence,
                metadata={"min_confidence": min_confidence, "avg_confidence": avg_confidence}
            )
        
        # Check if too many low-confidence words (flag for review, not reject)
        if confidence_scores:
            low_confidence_count = sum(1 for score in confidence_scores if score < self.config["ocr_confidence_min_single"])
            low_confidence_ratio = low_confidence_count / len(confidence_scores)
            threshold = self.config.get("low_confidence_ratio_threshold", 0.4)
            if low_confidence_ratio > threshold:  # More than threshold% low confidence
                return ValidationResult(
                    status=ValidationStatus.REVIEW,
                    reason=f"High ratio of low-confidence words: {low_confidence_ratio:.2%}",
                    confidence=avg_confidence,
                    metadata={"low_confidence_ratio": low_confidence_ratio}
                )
        
        return ValidationResult(
            status=ValidationStatus.PASS,
            reason="OCR confidence acceptable",
            confidence=avg_confidence,
            metadata={"avg_confidence": avg_confidence, "min_confidence": min_confidence}
        )
    
    def validate_readability(self, text: str) -> ValidationResult:
        """
        Validate if extracted text is readable.
        
        Args:
            text: Extracted text to validate
            
        Returns:
            ValidationResult
        """
        if not text or not text.strip():
            return ValidationResult(
                status=ValidationStatus.REJECT,
                reason="Empty or whitespace-only text",
                confidence=0.0
            )
        
        text_stripped = text.strip()
        
        # Check for garbage patterns
        garbage_patterns = []
        
        if self.config.get("reject_only_symbols", True):
            # Only symbols, no letters/numbers
            if re.match(r'^[^\w\s]+$', text_stripped):
                garbage_patterns.append("Only symbols, no alphanumeric characters")
        
        # Too short
        if len(text_stripped) < 10:
            garbage_patterns.append(f"Too short: {len(text_stripped)} characters")
        
        # Only numbers
        if re.match(r'^\d+$', text_stripped):
            garbage_patterns.append("Only numbers, no text")
        
        # All caps (likely OCR error for long strings)
        if len(text_stripped) > 20 and text_stripped.isupper() and not re.match(r'^[A-Z\s]+$', text_stripped):
            # Check if it's actually acronyms or if it's an error
            words = text_stripped.split()
            if len(words) > 5:  # Long all-caps text is suspicious
                garbage_patterns.append("Suspicious all-caps pattern (possible OCR error)")
        
        if garbage_patterns:
            return ValidationResult(
                status=ValidationStatus.REJECT,
                reason=f"Unreadable text: {'; '.join(garbage_patterns)}",
                confidence=0.0,
                metadata={"patterns": garbage_patterns}
            )
        
        # Check character ratio (letters vs symbols)
        total_chars = len(text)
        letter_chars = sum(c.isalnum() for c in text)
        letter_ratio = letter_chars / total_chars if total_chars > 0 else 0
        
        if letter_ratio < self.config["readability_letter_ratio"]:
            return ValidationResult(
                status=ValidationStatus.REJECT,
                reason=f"Too many non-letter characters: {letter_ratio:.2%} < {self.config['readability_letter_ratio']:.2%}",
                confidence=letter_ratio,
                metadata={"letter_ratio": letter_ratio, "threshold": self.config["readability_letter_ratio"]}
            )
        
        return ValidationResult(
            status=ValidationStatus.PASS,
            reason="Text is readable",
            confidence=letter_ratio,
            metadata={"letter_ratio": letter_ratio}
        )
    
    def validate_content_quality(self, text: str) -> ValidationResult:
        """
        Validate content quality and meaningfulness.
        
        Args:
            text: Text to validate
            
        Returns:
            ValidationResult
        """
        if not text:
            return ValidationResult(
                status=ValidationStatus.REJECT,
                reason="Empty text",
                confidence=0.0
            )
        
        words = text.split()
        
        # Check word count
        if len(words) < self.config["content_min_words"]:
            return ValidationResult(
                status=ValidationStatus.REJECT,
                reason=f"Too few words: {len(words)} < {self.config['content_min_words']}",
                confidence=len(words) / self.config["content_min_words"],
                metadata={"word_count": len(words), "threshold": self.config["content_min_words"]}
            )
        
        # Check for meaningful words (not just stopwords or very short words)
        meaningful_words = [w for w in words if len(w) > 3 and w.isalnum()]
        
        if len(meaningful_words) < self.config["content_meaningful_words"]:
            return ValidationResult(
                status=ValidationStatus.REJECT,
                reason=f"Not enough meaningful words: {len(meaningful_words)} < {self.config['content_meaningful_words']}",
                confidence=len(meaningful_words) / self.config["content_meaningful_words"],
                metadata={"meaningful_words": len(meaningful_words), "threshold": self.config["content_meaningful_words"]}
            )
        
        # Check for repeated characters (OCR error pattern)
        if self.config.get("reject_repeated_chars", True):
            if re.search(r'(.)\1{5,}', text):  # Same char 6+ times
                return ValidationResult(
                    status=ValidationStatus.REJECT,
                    reason="Repeated character pattern detected (likely OCR error)",
                    confidence=0.0,
                    metadata={"pattern": "repeated_chars"}
                )
        
        # Check for excessive whitespace (likely OCR error)
        if re.search(r'\s{10,}', text):  # 10+ consecutive spaces
            return ValidationResult(
                status=ValidationStatus.REVIEW,
                reason="Excessive whitespace detected (possible OCR error)",
                confidence=0.7,
                metadata={"pattern": "excessive_whitespace"}
            )
        
        return ValidationResult(
            status=ValidationStatus.PASS,
            reason="Content quality acceptable",
            confidence=min(1.0, len(meaningful_words) / max(10, len(words))),
            metadata={"word_count": len(words), "meaningful_words": len(meaningful_words)}
        )
    
    def validate_structure(
        self, 
        text: str, 
        image_type: Optional[str] = None
    ) -> ValidationResult:
        """
        Validate structure for tables/flowcharts.
        
        Args:
            text: Extracted text
            image_type: Type of image (table, flowchart, diagram, etc.)
            
        Returns:
            ValidationResult
        """
        if not self.config.get("structure_check_enabled", True):
            return ValidationResult(
                status=ValidationStatus.PASS,
                reason="Structure check disabled",
                confidence=1.0
            )
        
        if not image_type or image_type == "unknown":
            return ValidationResult(
                status=ValidationStatus.PASS,
                reason="No specific structure to validate",
                confidence=1.0
            )
        
        lines = text.split('\n')
        
        if image_type == "table":
            # Check for table structure
            if len(lines) < 2:
                return ValidationResult(
                    status=ValidationStatus.REJECT,
                    reason="Table has no structure (less than 2 lines)",
                    confidence=0.0,
                    metadata={"lines": len(lines)}
                )
            
            # Check for column separators or alignment
            has_structure = any('|' in line or '\t' in line for line in lines[:10])  # Check first 10 lines
            if not has_structure:
                return ValidationResult(
                    status=ValidationStatus.WARN,
                    reason="Table structure may be lost (no separators detected)",
                    confidence=0.6,
                    metadata={"lines": len(lines), "has_separators": False}
                )
        
        elif image_type == "flowchart":
            # Check for flowchart structure (decision points, arrows, etc.)
            has_flowchart_indicators = any(
                keyword in text.lower() 
                for keyword in ['yes', 'no', 'if', 'then', 'else', 'decision', 'process']
            )
            if not has_flowchart_indicators and len(lines) < 5:
                return ValidationResult(
                    status=ValidationStatus.WARN,
                    reason="Flowchart structure may be incomplete",
                    confidence=0.7,
                    metadata={"lines": len(lines), "has_indicators": has_flowchart_indicators}
                )
        
        return ValidationResult(
            status=ValidationStatus.PASS,
            reason="Structure validation passed",
            confidence=0.9,
            metadata={"image_type": image_type, "lines": len(lines)}
        )
    
    def validate_all(
        self,
        text: str,
        ocr_result: Optional[Dict[str, Any]] = None,
        image_type: Optional[str] = None
    ) -> List[ValidationResult]:
        """
        Run all validation checks.
        
        Args:
            text: Extracted text
            ocr_result: OCR result with confidence scores
            image_type: Type of image
            
        Returns:
            List of ValidationResults
        """
        results = []
        
        # OCR confidence check (if OCR result provided)
        if ocr_result:
            results.append(self.validate_ocr_confidence(ocr_result))
        
        # Readability check
        results.append(self.validate_readability(text))
        
        # Content quality check
        results.append(self.validate_content_quality(text))
        
        # Structure check
        results.append(self.validate_structure(text, image_type))
        
        return results
    
    def should_reject(self, validation_results: List[ValidationResult]) -> tuple[bool, Optional[str]]:
        """
        Determine if content should be rejected based on validation results.
        
        Args:
            validation_results: List of validation results
            
        Returns:
            Tuple of (should_reject, reason)
        """
        for result in validation_results:
            if result.status == ValidationStatus.REJECT:
                return True, result.reason
        
        return False, None
    
    def should_review(self, validation_results: List[ValidationResult]) -> tuple[bool, Optional[str]]:
        """
        Determine if content should be flagged for review.
        
        Args:
            validation_results: List of validation results
            
        Returns:
            Tuple of (should_review, reason)
        """
        for result in validation_results:
            if result.status == ValidationStatus.REVIEW:
                return True, result.reason
        
        # Check for multiple warnings
        warnings = [r for r in validation_results if r.status == ValidationStatus.WARN]
        if len(warnings) >= 2:
            return True, f"Multiple warnings: {', '.join(w.reason for w in warnings)}"
        
        return False, None

