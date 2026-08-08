"""
Extract text from 5 graphs/images and show quality validation results
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.agents.ocr_agent import OCRAgent
from core.chains.quality_validator import QualityValidator, ValidationStatus

def extract_from_image(image_path: str, image_type: str = None):
    """Extract text from an image and show full results."""
    print("=" * 70)
    print(f"EXTRACTING FROM: {os.path.basename(image_path)}")
    print("=" * 70)
    print()
    
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        print()
        return None
    
    # Initialize agent
    agent = OCRAgent(memory=None)
    validator = QualityValidator()
    
    # Process image
    print("Processing image...")
    result = agent.process(image_path, image_type=image_type)
    
    print()
    print("EXTRACTION RESULT:")
    print("-" * 70)
    print(f"Status: {result['status'].upper()}")
    print()
    
    if result.get('extracted_text'):
        print("EXTRACTED TEXT:")
        print("-" * 70)
        print(result['extracted_text'])
        print()
    else:
        print("No text extracted")
        print()
    
    if result.get('validation_results'):
        print("VALIDATION RESULTS:")
        print("-" * 70)
        for i, val_result in enumerate(result['validation_results'], 1):
            print(f"{i}. {val_result['status'].upper()}")
            print(f"   Reason: {val_result['reason']}")
            if 'confidence' in val_result:
                print(f"   Confidence: {val_result['confidence']:.2f}")
            print()
    
    if result.get('rejection_reason'):
        print("REJECTION REASON:")
        print("-" * 70)
        print(result['rejection_reason'])
        print()
    
    if result.get('review_reason'):
        print("REVIEW REASON:")
        print("-" * 70)
        print(result['review_reason'])
        print()
    
    if result.get('error'):
        print("ERROR:")
        print("-" * 70)
        print(result['error'])
        print()
    
    return result


def main():
    """Extract from 5 graphs/images."""
    print("\n" + "=" * 70)
    print("GRAPH/IMAGE OCR EXTRACTION TEST - 5 IMAGES")
    print("=" * 70)
    print()
    
    # Try to find images in common locations
    search_paths = [
        "/home/suspect/.n8n",
        "/home/suspect/Downloads",
        "/home/suspect/Pictures",
        "/tmp"
    ]
    
    images_found = []
    for search_path in search_paths:
        if os.path.exists(search_path):
            for ext in ['*.png', '*.jpg', '*.jpeg', '*.gif', '*.bmp', '*.tiff']:
                for img_path in Path(search_path).rglob(ext):
                    if img_path.is_file():
                        images_found.append(str(img_path))
                        if len(images_found) >= 5:
                            break
                if len(images_found) >= 5:
                    break
        if len(images_found) >= 5:
            break
    
    if not images_found:
        print("⚠️  No images found. Creating test scenario with simulated extractions...")
        print()
        
        # Simulate 5 different graph extractions
        test_cases = [
            {
                "name": "Graph 1: Table with Data",
                "image_path": "/tmp/graph1_table.png",
                "image_type": "table",
                "extracted_text": "Column1 | Column2 | Column3\nValue1 | Value2 | Value3\nData1 | Data2 | Data3\nResult1 | Result2 | Result3",
                "ocr_result": {
                    "avg_confidence": 0.92,
                    "min_confidence": 0.88,
                    "confidence_scores": [0.92, 0.90, 0.88, 0.95, 0.91]
                }
            },
            {
                "name": "Graph 2: Flowchart",
                "image_path": "/tmp/graph2_flowchart.png",
                "image_type": "flowchart",
                "extracted_text": "Start → Process A → Decision: Yes/No → Process B → End",
                "ocr_result": {
                    "avg_confidence": 0.85,
                    "min_confidence": 0.75,
                    "confidence_scores": [0.85, 0.80, 0.75, 0.90, 0.88]
                }
            },
            {
                "name": "Graph 3: Bar Chart Labels",
                "image_path": "/tmp/graph3_barchart.png",
                "image_type": "diagram",
                "extracted_text": "Q1: 100 units\nQ2: 150 units\nQ3: 120 units\nQ4: 180 units",
                "ocr_result": {
                    "avg_confidence": 0.78,
                    "min_confidence": 0.65,
                    "confidence_scores": [0.78, 0.75, 0.65, 0.80, 0.82]
                }
            },
            {
                "name": "Graph 4: Garbage/Noise",
                "image_path": "/tmp/graph4_garbage.png",
                "image_type": None,
                "extracted_text": "!!!!!@@@@@#####$$$$$%%%%%",
                "ocr_result": {
                    "avg_confidence": 0.9,
                    "min_confidence": 0.8,
                    "confidence_scores": [0.9, 0.85, 0.88]
                }
            },
            {
                "name": "Graph 5: Complex Diagram",
                "image_path": "/tmp/graph5_diagram.png",
                "image_type": "diagram",
                "extracted_text": "System Architecture:\nInput Layer → Processing Layer → Output Layer\nData flows through multiple stages with validation at each step.",
                "ocr_result": {
                    "avg_confidence": 0.88,
                    "min_confidence": 0.82,
                    "confidence_scores": [0.88, 0.85, 0.82, 0.90, 0.87]
                }
            }
        ]
        
        validator = QualityValidator()
        
        for i, test_case in enumerate(test_cases, 1):
            print("=" * 70)
            print(f"GRAPH {i}: {test_case['name']}")
            print("=" * 70)
            print()
            print(f"Image: {test_case['image_path']}")
            print(f"Type: {test_case['image_type'] or 'Unknown'}")
            print()
            
            print("EXTRACTED TEXT:")
            print("-" * 70)
            print(test_case['extracted_text'])
            print()
            
            print("OCR CONFIDENCE:")
            print("-" * 70)
            print(f"Average: {test_case['ocr_result']['avg_confidence']:.2f}")
            print(f"Minimum: {test_case['ocr_result']['min_confidence']:.2f}")
            print()
            
            # Run validation
            print("VALIDATION RESULTS:")
            print("-" * 70)
            
            # Confidence check
            conf_result = validator.validate_ocr_confidence(test_case['ocr_result'])
            print(f"1. Confidence Check: {conf_result.status.value.upper()}")
            print(f"   → {conf_result.reason}")
            print()
            
            # Readability check
            read_result = validator.validate_readability(test_case['extracted_text'])
            print(f"2. Readability Check: {read_result.status.value.upper()}")
            print(f"   → {read_result.reason}")
            print()
            
            # Content check
            content_result = validator.validate_content_quality(test_case['extracted_text'])
            print(f"3. Content Check: {content_result.status.value.upper()}")
            print(f"   → {content_result.reason}")
            print()
            
            # Structure check
            struct_result = validator.validate_structure(
                test_case['extracted_text'],
                test_case['image_type']
            )
            print(f"4. Structure Check: {struct_result.status.value.upper()}")
            print(f"   → {struct_result.reason}")
            print()
            
            # Final decision
            all_results = [conf_result, read_result, content_result, struct_result]
            should_reject, reject_reason = validator.should_reject(all_results)
            should_review, review_reason = validator.should_review(all_results)
            
            print("FINAL DECISION:")
            print("-" * 70)
            if should_reject:
                print(f"❌ REJECTED: {reject_reason}")
            elif should_review:
                print(f"⚠️  REVIEW NEEDED: {review_reason}")
            else:
                print("✅ ACCEPTED: All validation checks passed")
            print()
            print()
        
        print("=" * 70)
        print("EXTRACTION COMPLETE - 5 GRAPHS PROCESSED")
        print("=" * 70)
        
    else:
        print(f"Found {len(images_found)} images. Processing first 5...")
        print()
        
        for i, img_path in enumerate(images_found[:5], 1):
            image_type = "table" if "table" in img_path.lower() else \
                        "flowchart" if "flow" in img_path.lower() else \
                        "diagram" if "diagram" in img_path.lower() else None
            
            extract_from_image(img_path, image_type)
            print()


if __name__ == "__main__":
    main()

