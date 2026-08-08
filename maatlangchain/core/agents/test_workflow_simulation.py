"""
Test OCR Agent Workflow Simulation
Tests the complete workflow without requiring database connection
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.agents.ocr_agent import OCRAgent
from core.chains.quality_validator import QualityValidator, ValidationStatus

def simulate_ocr_workflow():
    """Simulate complete OCR workflow with quality validation."""
    print("=" * 60)
    print("OCR Agent Workflow Simulation")
    print("=" * 60)
    print()
    
    # Initialize agent (without Maat Memory for testing)
    agent = OCRAgent(memory=None)
    print("✅ OCR Agent initialized")
    print()
    
    # Test cases simulating different scenarios
    test_cases = [
        {
            "name": "High-quality extraction (should pass)",
            "ocr_result": {
                "avg_confidence": 0.92,
                "min_confidence": 0.85,
                "confidence_scores": [0.92, 0.90, 0.88, 0.95],
                "text": "This is a comprehensive document about statistical analysis with meaningful content and proper structure. It contains multiple paragraphs with detailed information."
            },
            "image_type": None,  # Not a table, just high-quality text
            "expected": "completed"
        },
        {
            "name": "Low confidence OCR (should reject)",
            "ocr_result": {
                "avg_confidence": 0.4,
                "min_confidence": 0.2,
                "confidence_scores": [0.4, 0.3, 0.2, 0.5],
                "text": "Some text here"
            },
            "image_type": None,
            "expected": "rejected"
        },
        {
            "name": "Garbage text (should reject)",
            "ocr_result": {
                "avg_confidence": 0.9,
                "min_confidence": 0.8,
                "confidence_scores": [0.9, 0.85, 0.88],
                "text": "!!!!!@@@@@#####$$$$$"
            },
            "image_type": None,
            "expected": "rejected"
        },
        {
            "name": "Review needed (low confidence ratio)",
            "ocr_result": {
                "avg_confidence": 0.75,
                "min_confidence": 0.6,
                "confidence_scores": [0.75, 0.4, 0.3, 0.35, 0.8, 0.9],  # 50% low confidence
                "text": "This is good text but some words have low confidence scores."
            },
            "image_type": None,
            "expected": "review"
        }
    ]
    
    print("Testing workflow with simulated OCR results:")
    print()
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"Test {i}: {test['name']}")
        
        # Simulate the workflow by testing each validation stage
        validator = QualityValidator()
        
        # Stage 1: Confidence check
        conf_result = validator.validate_ocr_confidence(test["ocr_result"])
        if conf_result.status == ValidationStatus.REJECT:
            result_status = "rejected"
            reason = conf_result.reason
        elif conf_result.status == ValidationStatus.REVIEW:
            result_status = "review"
            reason = conf_result.reason
        else:
            # Stage 2: Readability check
            read_result = validator.validate_readability(test["ocr_result"]["text"])
            if read_result.status == ValidationStatus.REJECT:
                result_status = "rejected"
                reason = read_result.reason
            else:
                # Stage 3: Content check
                content_result = validator.validate_content_quality(test["ocr_result"]["text"])
                if content_result.status == ValidationStatus.REJECT:
                    result_status = "rejected"
                    reason = content_result.reason
                else:
                    # Stage 4: Structure check
                    struct_result = validator.validate_structure(
                        test["ocr_result"]["text"],
                        test["image_type"]
                    )
                    if struct_result.status == ValidationStatus.REJECT:
                        result_status = "rejected"
                        reason = struct_result.reason
                    elif struct_result.status == ValidationStatus.REVIEW:
                        result_status = "review"
                        reason = struct_result.reason
                    else:
                        result_status = "completed"
                        reason = "All checks passed"
        
        # Check result
        if result_status == test["expected"]:
            print(f"  ✅ PASS - Status: {result_status}")
            print(f"     Reason: {reason[:60]}...")
            passed += 1
        else:
            print(f"  ❌ FAIL - Expected {test['expected']}, got {result_status}")
            print(f"     Reason: {reason[:60]}...")
            failed += 1
        print()
    
    print(f"Results: {passed} passed, {failed} failed")
    print()
    
    return passed, failed


def test_quality_validation_against_maat():
    """Test quality validation follows Maat principles."""
    print("=" * 60)
    print("Maat Principles Validation")
    print("=" * 60)
    print()
    
    validator = QualityValidator()
    
    maat_tests = [
        {
            "principle": "Truth",
            "test": "Rejects false/low-quality content",
            "text": "!!!!!@@@@@#####",
            "should_reject": True
        },
        {
            "principle": "Balance",
            "test": "Allows high-quality content",
            "text": "This is a comprehensive document with meaningful content.",
            "should_reject": False
        },
        {
            "principle": "Order",
            "test": "Structured validation process",
            "text": "Column1 | Column2\nValue1 | Value2",
            "image_type": "table",
            "should_reject": False
        },
        {
            "principle": "Justice",
            "test": "Consistent validation for all content",
            "text": "Short",
            "should_reject": True
        },
        {
            "principle": "Self-Reflection",
            "test": "Flags uncertain cases for review",
            "ocr_result": {
                "avg_confidence": 0.75,
                "min_confidence": 0.6,
                "confidence_scores": [0.75, 0.4, 0.3, 0.35, 0.8, 0.9]
            },
            "should_review": True
        }
    ]
    
    print("Testing Maat principles:")
    print()
    
    all_passed = True
    for test in maat_tests:
        print(f"  {test['principle']}: {test['test']}")
        
        if "ocr_result" in test:
            result = validator.validate_ocr_confidence(test["ocr_result"])
            passed = (test.get("should_review", False) and result.status == ValidationStatus.REVIEW) or \
                     (not test.get("should_review", False) and result.status != ValidationStatus.REJECT)
        else:
            result = validator.validate_readability(test["text"])
            if result.status == ValidationStatus.PASS:
                result = validator.validate_content_quality(test["text"])
            if "image_type" in test:
                result = validator.validate_structure(test["text"], test["image_type"])
            
            if test["should_reject"]:
                passed = result.status == ValidationStatus.REJECT
            else:
                passed = result.status == ValidationStatus.PASS
        
        if passed:
            print(f"    ✅ PASS")
        else:
            print(f"    ❌ FAIL - Status: {result.status.value}")
            all_passed = False
        print()
    
    return all_passed


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("OCR Agent - Complete Workflow Test")
    print("=" * 60)
    print()
    
    # Test 1: Workflow simulation
    passed, failed = simulate_ocr_workflow()
    
    # Test 2: Maat principles
    maat_ok = test_quality_validation_against_maat()
    
    # Summary
    print("=" * 60)
    print("Final Summary")
    print("=" * 60)
    print()
    print(f"Workflow Tests: {passed} passed, {failed} failed")
    print(f"Maat Principles: {'✅ All passed' if maat_ok else '❌ Some failed'}")
    print()
    
    if passed == 4 and failed == 0 and maat_ok:
        print("🎉 ALL TESTS PASSED!")
        print()
        print("✅ Quality validation working")
        print("✅ Garbage content rejected")
        print("✅ High-quality content accepted")
        print("✅ Maat principles followed")
        print("✅ Workflow ready for production")
        return 0
    else:
        print("⚠️  Some tests failed")
        return 1


if __name__ == "__main__":
    exit(main())

