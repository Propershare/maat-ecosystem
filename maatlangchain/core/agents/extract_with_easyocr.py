"""
Extract ACTUAL text from 5 graph images using EasyOCR
Shows the EXACT extracted words
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Graph images we found
GRAPH_IMAGES = [
    "/home/suspect/.n8n/weknora-analysis/docs/images/graph1.png",
    "/home/suspect/.n8n/weknora-analysis/docs/images/graph2.png",
    "/home/suspect/.n8n/weknora-analysis/docs/images/graph3.png",
    "/home/suspect/.n8n/jarvis/maat-graphs/evolution-of-enslavement/Evolution_Slavery.jpg",
    "/home/suspect/.n8n/weknora-analysis/docs/images/pipeline.jpg"
]

def extract_with_easyocr(image_path):
    """Extract text using EasyOCR."""
    try:
        import easyocr
        reader = easyocr.Reader(['en'], gpu=False)
        results = reader.readtext(image_path)
        
        # Combine all detected text
        extracted_text = []
        confidences = []
        
        for (bbox, text, confidence) in results:
            extracted_text.append(text)
            confidences.append(confidence)
        
        full_text = "\n".join(extracted_text)
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        min_confidence = min(confidences) if confidences else 0.0
        
        return {
            'text': full_text,
            'avg_confidence': avg_confidence,
            'min_confidence': min_confidence,
            'confidences': confidences,
            'detections': results
        }
    except Exception as e:
        return {'error': str(e)}

def main():
    """Extract and show EXACT text from 5 graph images."""
    print("=" * 80)
    print("EXTRACTING ACTUAL TEXT FROM 5 GRAPH IMAGES USING EasyOCR")
    print("=" * 80)
    print()
    
    for i, img_path in enumerate(GRAPH_IMAGES, 1):
        if not os.path.exists(img_path):
            print(f"SKIPPING GRAPH {i}: {os.path.basename(img_path)} (not found)")
            print()
            continue
        
        print("=" * 80)
        print(f"GRAPH {i}: {os.path.basename(img_path)}")
        print("=" * 80)
        print()
        print(f"Full path: {img_path}")
        print(f"File size: {os.path.getsize(img_path):,} bytes")
        print()
        
        print("Extracting text with EasyOCR...")
        print("(This may take a moment on first run)")
        print()
        
        result = extract_with_easyocr(img_path)
        
        if 'error' in result:
            print("ERROR:")
            print("-" * 80)
            print(result['error'])
        else:
            print("EXTRACTED TEXT (EXACT WORDS):")
            print("-" * 80)
            if result['text']:
                print(result['text'])
                print()
                print(f"Character count: {len(result['text'])}")
                print(f"Word count: {len(result['text'].split())}")
                print(f"Lines detected: {len(result['text'].split(chr(10)))}")
                print()
                print("OCR CONFIDENCE:")
                print("-" * 80)
                print(f"Average confidence: {result['avg_confidence']:.2%}")
                print(f"Minimum confidence: {result['min_confidence']:.2%}")
                print(f"Total detections: {len(result['detections'])}")
                print()
                print("DETAILED DETECTIONS:")
                print("-" * 80)
                for idx, (bbox, text, conf) in enumerate(result['detections'][:10], 1):  # Show first 10
                    print(f"{idx}. \"{text}\" (confidence: {conf:.2%})")
                if len(result['detections']) > 10:
                    print(f"... and {len(result['detections']) - 10} more detections")
            else:
                print("No text detected in this image")
        
        print()
        print()
    
    print("=" * 80)
    print("EXTRACTION COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()

