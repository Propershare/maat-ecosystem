"""
Test script for OCR Agent with Quality Validation
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.agents.ocr_agent import OCRAgent
from core.chains.quality_validator import QualityValidator

def test_quality_validator():
    """Test quality validator."""
    print("=== Testing Quality Validator ===\n")
    
    validator = QualityValidator()
    
    # Test 1: Good text
    print("Test 1: Good text")
    text = "This is a high-quality text extraction with meaningful content."
    result = validator.validate_readability(text)
    print(f"  Status: {result.status.value}")
    print(f"  Reason: {result.reason}\n")
    
    # Test 2: Garbage text
    print("Test 2: Garbage text")
    garbage = "!!!!!@@@@@#####$$$$$"
    result = validator.validate_readability(garbage)
    print(f"  Status: {result.status.value}")
    print(f"  Reason: {result.reason}\n")
    
    # Test 3: Low confidence OCR
    print("Test 3: Low confidence OCR")
    ocr_result = {
        "avg_confidence": 0.5,
        "min_confidence": 0.3,
        "confidence_scores": [0.5, 0.4, 0.3, 0.6]
    }
    result = validator.validate_ocr_confidence(ocr_result)
    print(f"  Status: {result.status.value}")
    print(f"  Reason: {result.reason}\n")
    
    # Test 4: High confidence OCR
    print("Test 4: High confidence OCR")
    ocr_result = {
        "avg_confidence": 0.9,
        "min_confidence": 0.8,
        "confidence_scores": [0.9, 0.85, 0.88, 0.92]
    }
    result = validator.validate_ocr_confidence(ocr_result)
    print(f"  Status: {result.status.value}")
    print(f"  Reason: {result.reason}\n")
    
    print("✅ Quality validator tests complete!\n")


def test_ocr_agent():
    """Test OCR agent workflow."""
    print("=== Testing OCR Agent ===\n")
    
    try:
        agent = OCRAgent()
        print("✅ OCR Agent initialized\n")
        
        # Test with a non-existent file (will test error handling)
        print("Test: Processing non-existent image")
        result = agent.process("/tmp/test_image.png", image_type="table")
        print(f"  Status: {result['status']}")
        if result.get('error'):
            print(f"  Error: {result['error']}")
        print()
        
        print("✅ OCR Agent workflow test complete!\n")
        
    except Exception as e:
        print(f"❌ Error: {e}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("=" * 60)
    print("OCR Agent Quality Validation System Test")
    print("=" * 60)
    print()
    
    test_quality_validator()
    test_ocr_agent()
    
    print("=" * 60)
    print("All tests complete!")
    print("=" * 60)

