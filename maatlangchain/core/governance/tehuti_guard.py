"""
TehutiGuard - Policy Enforcement Engine
Maat: Justice - Enforce policies and protect system integrity
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from .three_ring import RingClassification, ThreeRingClassifier

log = logging.getLogger(__name__)


class PolicyViolationType(str, Enum):
    """Types of policy violations."""
    ACCESS_DENIED = "access_denied"
    RING_VIOLATION = "ring_violation"
    UNAUTHORIZED_ACTION = "unauthorized_action"
    INVALID_CLASSIFICATION = "invalid_classification"
    RESOURCE_LIMIT = "resource_limit"
    SECURITY_VIOLATION = "security_violation"


@dataclass
class PolicyViolation:
    """Represents a policy violation."""
    violation_type: PolicyViolationType
    message: str
    severity: str  # "low", "medium", "high", "critical"
    context: Dict[str, Any]
    timestamp: datetime


class TehutiGuard:
    """
    Policy enforcement engine for Maat-aligned systems.
    
    Enforces:
    - Three-ring access control
    - Resource limits
    - Security policies
    - Maat compliance
    """
    
    def __init__(self):
        self.classifier = ThreeRingClassifier()
        self.violations: List[PolicyViolation] = []
        self.policies = {
            "max_queries_per_minute": 60,
            "max_documents_per_query": 100,
            "require_citations": True,
            "require_uncertainty_acknowledgment": True,
        }
    
    def check_access(
        self,
        user_ring: RingClassification,
        content_ring: RingClassification,
        action: str = "read"
    ) -> tuple[bool, Optional[PolicyViolation]]:
        """
        Check if user can access content.
        
        Args:
            user_ring: User's ring classification
            content_ring: Content's ring classification
            action: Action being performed (read, write, delete)
        
        Returns:
            Tuple of (allowed, violation)
        """
        allowed = self.classifier.can_access(user_ring, content_ring)
        
        if not allowed:
            violation = PolicyViolation(
                violation_type=PolicyViolationType.ACCESS_DENIED,
                message=f"User with {user_ring.value} ring cannot {action} {content_ring.value} ring content",
                severity="high",
                context={
                    "user_ring": user_ring.value,
                    "content_ring": content_ring.value,
                    "action": action
                },
                timestamp=datetime.now()
            )
            self.violations.append(violation)
            log.warning(f"Access denied: {violation.message}")
            return False, violation
        
        return True, None
    
    def check_action(
        self,
        user_ring: RingClassification,
        action: str,
        resource: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> tuple[bool, Optional[PolicyViolation]]:
        """
        Check if user can perform action.
        
        Args:
            user_ring: User's ring classification
            action: Action being performed
            resource: Resource being accessed
            metadata: Additional metadata
        
        Returns:
            Tuple of (allowed, violation)
        """
        # Inner Ring actions require Inner Ring access
        if action in ["modify_canon", "create_canon", "delete_canon"]:
            if user_ring != RingClassification.INNER:
                violation = PolicyViolation(
                    violation_type=PolicyViolationType.UNAUTHORIZED_ACTION,
                    message=f"Only Inner Ring users can {action}",
                    severity="critical",
                    context={
                        "user_ring": user_ring.value,
                        "action": action,
                        "resource": resource
                    },
                    timestamp=datetime.now()
                )
                self.violations.append(violation)
                log.warning(f"Unauthorized action: {violation.message}")
                return False, violation
        
        # Middle Ring actions require at least Middle Ring access
        if action in ["modify_scholarship", "create_scholarship"]:
            if user_ring == RingClassification.OUTER:
                violation = PolicyViolation(
                    violation_type=PolicyViolationType.UNAUTHORIZED_ACTION,
                    message=f"Outer Ring users cannot {action}",
                    severity="high",
                    context={
                        "user_ring": user_ring.value,
                        "action": action,
                        "resource": resource
                    },
                    timestamp=datetime.now()
                )
                self.violations.append(violation)
                log.warning(f"Unauthorized action: {violation.message}")
                return False, violation
        
        return True, None
    
    def validate_classification(
        self,
        content: str,
        source: Optional[str] = None,
        claimed_ring: Optional[RingClassification] = None
    ) -> tuple[bool, Optional[PolicyViolation], RingClassification]:
        """
        Validate content classification.
        
        Args:
            content: Content text
            source: Source identifier
            claimed_ring: Claimed ring classification
        
        Returns:
            Tuple of (valid, violation, actual_ring)
        """
        actual_result = self.classifier.classify(content, source)
        actual_ring = actual_result.ring
        
        if claimed_ring and claimed_ring != actual_ring:
            violation = PolicyViolation(
                violation_type=PolicyViolationType.INVALID_CLASSIFICATION,
                message=f"Claimed ring {claimed_ring.value} does not match actual ring {actual_ring.value}",
                severity="medium",
                context={
                    "claimed_ring": claimed_ring.value,
                    "actual_ring": actual_ring.value,
                    "source": source,
                    "confidence": actual_result.confidence
                },
                timestamp=datetime.now()
            )
            self.violations.append(violation)
            log.warning(f"Invalid classification: {violation.message}")
            return False, violation, actual_ring
        
        return True, None, actual_ring
    
    def check_resource_limit(
        self,
        resource_type: str,
        current_usage: int,
        limit: Optional[int] = None
    ) -> tuple[bool, Optional[PolicyViolation]]:
        """
        Check if resource usage is within limits.
        
        Args:
            resource_type: Type of resource (queries, documents, etc.)
            current_usage: Current usage count
            limit: Custom limit (uses policy default if None)
        
        Returns:
            Tuple of (within_limit, violation)
        """
        policy_key = f"max_{resource_type}_per_minute"
        limit = limit or self.policies.get(policy_key, 100)
        
        if current_usage >= limit:
            violation = PolicyViolation(
                violation_type=PolicyViolationType.RESOURCE_LIMIT,
                message=f"Resource limit exceeded: {resource_type} ({current_usage}/{limit})",
                severity="medium",
                context={
                    "resource_type": resource_type,
                    "current_usage": current_usage,
                    "limit": limit
                },
                timestamp=datetime.now()
            )
            self.violations.append(violation)
            log.warning(f"Resource limit: {violation.message}")
            return False, violation
        
        return True, None
    
    def get_violations(
        self,
        severity: Optional[str] = None,
        violation_type: Optional[PolicyViolationType] = None
    ) -> List[PolicyViolation]:
        """Get policy violations, optionally filtered."""
        violations = self.violations
        
        if severity:
            violations = [v for v in violations if v.severity == severity]
        
        if violation_type:
            violations = [v for v in violations if v.violation_type == violation_type]
        
        return violations
    
    def clear_violations(self):
        """Clear all violations."""
        self.violations.clear()

