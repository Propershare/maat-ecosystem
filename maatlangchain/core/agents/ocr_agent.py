"""
Autonomous OCR Processing Agent with Quality Validation
Maat: Truth, Order - Autonomous task execution with quality gates
"""

import logging
import os
from typing import Dict, Any, Optional, List, TypedDict
from pathlib import Path
from datetime import datetime

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from core.chains.quality_validator import QualityValidator, ValidationStatus

# Import Maat Memory
import sys
from pathlib import Path
maatlangchain_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(maatlangchain_root))
from maat_memory.memory_postgres import MaatMemoryPostgres as MaatMemory
try:
    from maat_memory.machine_info import get_unique_agent_id
except ImportError:
    import socket
    def get_unique_agent_id(prefix: str) -> str:
        return f"{prefix}_{socket.gethostname()}"

log = logging.getLogger(__name__)


class OCRState(TypedDict):
    """State for OCR processing workflow."""
    image_path: str
    image_type: Optional[str]
    ocr_result: Optional[Dict[str, Any]]
    extracted_text: Optional[str]
    validation_results: Optional[List[Any]]
    status: str
    error: Optional[str]
    rejection_reason: Optional[str]
    review_reason: Optional[str]
    metadata: Dict[str, Any]


class OCRAgent:
    """
    Autonomous OCR processing agent with quality validation.
    
    Executes OCR tasks with multi-stage quality checking to prevent
    garbage content from entering the RAG system.
    """
    
    def __init__(
        self,
        ocr_engine: Optional[Any] = None,
        quality_validator: Optional[QualityValidator] = None,
        memory: Optional[MaatMemory] = None
    ):
        """
        Initialize OCR agent.
        
        Args:
            ocr_engine: OCR engine (rapidocr, tesseract, etc.)
            quality_validator: Quality validator instance
            memory: Maat Memory instance for logging (optional)
        """
        self.ocr_engine = ocr_engine
        self.quality_validator = quality_validator or QualityValidator()
        
        # Make memory optional (for testing without DB)
        try:
            self.memory = memory or MaatMemory()
            self.memory_available = True
        except Exception as e:
            log.warning(f"Maat Memory not available: {e}. Continuing without logging.")
            self.memory = None
            self.memory_available = False
        
        self.agent_id = get_unique_agent_id("ocr_agent")
        
        # Build workflow
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build LangGraph workflow for OCR processing."""
        workflow = StateGraph(OCRState)
        
        # Add nodes
        workflow.add_node("extract_ocr", self._extract_ocr)
        workflow.add_node("check_confidence", self._check_confidence)
        workflow.add_node("check_readability", self._check_readability)
        workflow.add_node("check_content", self._check_content)
        workflow.add_node("check_structure", self._check_structure)
        workflow.add_node("process_and_store", self._process_and_store)
        workflow.add_node("reject", self._reject)
        workflow.add_node("review", self._flag_for_review)
        
        # Set entry point
        workflow.set_entry_point("extract_ocr")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "extract_ocr",
            self._route_after_extract,
            {
                "check_confidence": "check_confidence",
                "reject": "reject",
                "error": END
            }
        )
        
        workflow.add_conditional_edges(
            "check_confidence",
            self._route_after_confidence,
            {
                "check_readability": "check_readability",
                "reject": "reject",
                "review": "review"
            }
        )
        
        workflow.add_conditional_edges(
            "check_readability",
            self._route_after_readability,
            {
                "check_content": "check_content",
                "reject": "reject"
            }
        )
        
        workflow.add_conditional_edges(
            "check_content",
            self._route_after_content,
            {
                "check_structure": "check_structure",
                "reject": "reject"
            }
        )
        
        workflow.add_conditional_edges(
            "check_structure",
            self._route_after_structure,
            {
                "process": "process_and_store",
                "review": "review",
                "reject": "reject"
            }
        )
        
        # Terminal nodes
        workflow.add_edge("process_and_store", END)
        workflow.add_edge("reject", END)
        workflow.add_edge("review", END)
        
        return workflow.compile(checkpointer=MemorySaver())
    
    def _extract_ocr(self, state: OCRState) -> OCRState:
        """Extract text using OCR."""
        try:
            image_path = state["image_path"]
            
            if not os.path.exists(image_path):
                return {
                    **state,
                    "status": "error",
                    "error": f"Image not found: {image_path}"
                }
            
            # TODO: Integrate with actual OCR engine
            # For now, simulate OCR extraction
            # In production, use rapidocr, tesseract, or Datalab Marker
            
            log.info(f"Extracting OCR from {image_path}")
            
            # Simulated OCR result (replace with actual OCR)
            ocr_result = {
                "avg_confidence": 0.85,  # Would come from OCR engine
                "min_confidence": 0.65,
                "confidence_scores": [0.85, 0.90, 0.80, 0.65, 0.88],
                "text": "Extracted text would go here"  # Placeholder
            }
            
            return {
                **state,
                "ocr_result": ocr_result,
                "extracted_text": ocr_result.get("text", ""),
                "status": "extracted"
            }
            
        except Exception as e:
            log.error(f"OCR extraction failed: {e}")
            return {
                **state,
                "status": "error",
                "error": str(e)
            }
    
    def _check_confidence(self, state: OCRState) -> OCRState:
        """Check OCR confidence scores."""
        ocr_result = state.get("ocr_result")
        if not ocr_result:
            return {
                **state,
                "status": "reject",
                "rejection_reason": "No OCR result to validate"
            }
        
        result = self.quality_validator.validate_ocr_confidence(ocr_result)
        
        validation_results = state.get("validation_results") or []
        validation_results.append(result)
        
        return {
            **state,
            "validation_results": validation_results,
            "status": result.status.value
        }
    
    def _check_readability(self, state: OCRState) -> OCRState:
        """Check text readability."""
        text = state.get("extracted_text", "")
        if not text:
            return {
                **state,
                "status": "reject",
                "rejection_reason": "No text extracted"
            }
        
        result = self.quality_validator.validate_readability(text)
        
        validation_results = state.get("validation_results") or []
        validation_results.append(result)
        
        return {
            **state,
            "validation_results": validation_results,
            "status": result.status.value
        }
    
    def _check_content(self, state: OCRState) -> OCRState:
        """Check content quality."""
        text = state.get("extracted_text", "")
        if not text:
            return {
                **state,
                "status": "reject",
                "rejection_reason": "No text to validate"
            }
        
        result = self.quality_validator.validate_content_quality(text)
        
        validation_results = state.get("validation_results") or []
        validation_results.append(result)
        
        return {
            **state,
            "validation_results": validation_results,
            "status": result.status.value
        }
    
    def _check_structure(self, state: OCRState) -> OCRState:
        """Check structure for tables/flowcharts."""
        text = state.get("extracted_text", "")
        image_type = state.get("image_type")
        
        result = self.quality_validator.validate_structure(text, image_type)
        
        validation_results = state.get("validation_results") or []
        validation_results.append(result)
        
        return {
            **state,
            "validation_results": validation_results,
            "status": result.status.value
        }
    
    def _process_and_store(self, state: OCRState) -> OCRState:
        """Process and store validated content."""
        try:
            text = state.get("extracted_text", "")
            image_path = state["image_path"]
            
            log.info(f"Processing and storing validated OCR content from {image_path}")
            
            # TODO: Integrate with RAG system to store content
            # For now, log success
            
            # Log to Maat Memory (if available)
            if self.memory_available and self.memory:
                try:
                    self.memory.log_change(
                        agent=self.agent_id,
                        file_path=image_path,
                        change_type="created",
                        summary=f"OCR processed and validated: {os.path.basename(image_path)}",
                        reason="Autonomous OCR agent processing"
                    )
                except Exception as e:
                    log.warning(f"Failed to log to Maat Memory: {e}")
            
            return {
                **state,
                "status": "completed",
                "metadata": {
                    **state.get("metadata", {}),
                    "processed_at": datetime.now().isoformat(),
                    "text_length": len(text)
                }
            }
            
        except Exception as e:
            log.error(f"Failed to process and store: {e}")
            return {
                **state,
                "status": "error",
                "error": str(e)
            }
    
    def _reject(self, state: OCRState) -> OCRState:
        """Reject low-quality content."""
        validation_results = state.get("validation_results", [])
        rejection_reason = state.get("rejection_reason")
        
        # Find rejection reason from validation results
        if not rejection_reason:
            for result in validation_results:
                if result.status == ValidationStatus.REJECT:
                    rejection_reason = result.reason
                    break
        
        log.warning(f"Rejecting OCR content: {rejection_reason}")
        
        # Log rejection to Maat Memory (if available)
        if self.memory_available and self.memory:
            try:
                self.memory.log_error(
                    agent=self.agent_id,
                    error_type="OCRQualityRejection",
                    message=rejection_reason or "Quality validation failed",
                    context={
                        "image_path": state["image_path"],
                        "validation_results": [
                            {
                                "status": r.status.value,
                                "reason": r.reason,
                                "confidence": r.confidence
                            }
                            for r in validation_results
                        ]
                    }
                )
            except Exception as e:
                log.warning(f"Failed to log rejection to Maat Memory: {e}")
        
        return {
            **state,
            "status": "rejected",
            "rejection_reason": rejection_reason
        }
    
    def _flag_for_review(self, state: OCRState) -> OCRState:
        """Flag content for human review."""
        validation_results = state.get("validation_results", [])
        review_reason = state.get("review_reason")
        
        # Find review reason from validation results
        if not review_reason:
            for result in validation_results:
                if result.status == ValidationStatus.REVIEW:
                    review_reason = result.reason
                    break
        
        log.info(f"Flagging OCR content for review: {review_reason}")
        
        # Log to Maat Memory (if available)
        if self.memory_available and self.memory:
            try:
                self.memory.log_change(
                    agent=self.agent_id,
                    file_path=state["image_path"],
                    change_type="review",
                    summary=f"OCR flagged for review: {os.path.basename(state['image_path'])}",
                    reason=review_reason or "Quality validation requires review"
                )
            except Exception as e:
                log.warning(f"Failed to log review to Maat Memory: {e}")
        
        return {
            **state,
            "status": "review",
            "review_reason": review_reason
        }
    
    # Routing functions
    def _route_after_extract(self, state: OCRState) -> str:
        """Route after OCR extraction."""
        if state.get("status") == "error":
            return "error"
        if not state.get("ocr_result"):
            return "reject"
        return "check_confidence"
    
    def _route_after_confidence(self, state: OCRState) -> str:
        """Route after confidence check."""
        status = state.get("status", "")
        if status == "reject":
            return "reject"
        if status == "review":
            return "review"
        return "check_readability"
    
    def _route_after_readability(self, state: OCRState) -> str:
        """Route after readability check."""
        status = state.get("status", "")
        if status == "reject":
            return "reject"
        return "check_content"
    
    def _route_after_content(self, state: OCRState) -> str:
        """Route after content check."""
        status = state.get("status", "")
        if status == "reject":
            return "reject"
        return "check_structure"
    
    def _route_after_structure(self, state: OCRState) -> str:
        """Route after structure check."""
        status = state.get("status", "")
        if status == "reject":
            return "reject"
        if status == "review":
            return "review"
        return "process"
    
    def process(self, image_path: str, image_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Process image with OCR and quality validation.
        
        Args:
            image_path: Path to image file
            image_type: Type of image (table, flowchart, diagram, etc.)
            
        Returns:
            Processing result dictionary
        """
        initial_state: OCRState = {
            "image_path": image_path,
            "image_type": image_type,
            "ocr_result": None,
            "extracted_text": None,
            "validation_results": None,
            "status": "pending",
            "error": None,
            "rejection_reason": None,
            "review_reason": None,
            "metadata": {}
        }
        
        # Run workflow
        config = {"configurable": {"thread_id": f"ocr_{os.path.basename(image_path)}"}}
        final_state = self.workflow.invoke(initial_state, config)
        
        return {
            "status": final_state.get("status"),
            "extracted_text": final_state.get("extracted_text"),
            "error": final_state.get("error"),
            "rejection_reason": final_state.get("rejection_reason"),
            "review_reason": final_state.get("review_reason"),
            "validation_results": [
                {
                    "status": r.status.value,
                    "reason": r.reason,
                    "confidence": r.confidence
                }
                for r in (final_state.get("validation_results") or [])
            ],
            "metadata": final_state.get("metadata", {})
        }

