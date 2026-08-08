"""
Extract ACTUAL text from the 5 graph images found
"""

import sys
import os
from pathlib import Path

# Graph images we found
GRAPH_IMAGES = [
    "/home/suspect/.n8n/weknora-analysis/docs/images/graph1.png",
    "/home/suspect/.n8n/weknora-analysis/docs/images/graph2.png",
    "/home/suspect/.n8n/weknora-analysis/docs/images/graph3.png",
    "/home/suspect/.n8n/jarvis/maat-graphs/evolution-of-enslavement/Evolution_Slavery.jpg",
    "/home/suspect/.n8n/weknora-analysis/docs/images/pipeline.jpg"
]

def try_ocr_extraction(image_path):
    """Try multiple OCR methods."""
    results = {}
    
    # Method 1: Tesseract
    try:
        import pytesseract
        from PIL import Image
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        results['tesseract'] = text.strip()
    except Exception as e:
        results['tesseract_error'] = str(e)
    
    # Method 2: Datalab Marker
    try:
        sys.path.insert(0, '/home/suspect/.n8n/tehuti-lab-webui/backend')
        from open_webui.retrieval.loaders.datalab_marker import DatalabMarkerLoader
        api_key = os.getenv("DATALAB_MARKER_API_KEY", "")
        api_url = os.getenv("DATALAB_MARKER_API_BASE_URL", "https://api.datalab.marker.com")
        if api_key:
            loader = DatalabMarkerLoader(
                file_path=image_path,
                api_key=api_key,
                api_base_url=api_url,
                force_ocr=True
            )
            docs = loader.load()
            if docs:
                results['datalab'] = "\n".join([doc.page_content for doc in docs])
    except Exception as e:
        results['datalab_error'] = str(e)
    
    return results

def main():
    """Extract and show EXACT text from 5 graph images."""
    print("=" * 80)
    print("EXTRACTING ACTUAL TEXT FROM 5 GRAPH IMAGES")
    print("=" * 80)
    print()
    
    for i, img_path in enumerate(GRAPH_IMAGES, 1):
        if not os.path.exists(img_path):
            print(f"SKIPPING IMAGE {i}: {os.path.basename(img_path)} (not found)")
            print()
            continue
        
        print("=" * 80)
        print(f"GRAPH {i}: {os.path.basename(img_path)}")
        print("=" * 80)
        print()
        print(f"Full path: {img_path}")
        print(f"File size: {os.path.getsize(img_path):,} bytes")
        print()
        
        print("ATTEMPTING OCR EXTRACTION...")
        print()
        
        results = try_ocr_extraction(img_path)
        
        # Show extracted text
        if 'tesseract' in results:
            print("EXTRACTED TEXT (TESSERACT OCR):")
            print("-" * 80)
            print(results['tesseract'])
            print()
            print(f"Character count: {len(results['tesseract'])}")
            print(f"Word count: {len(results['tesseract'].split())}")
        elif 'datalab' in results:
            print("EXTRACTED TEXT (DATALAB MARKER OCR):")
            print("-" * 80)
            print(results['datalab'])
            print()
            print(f"Character count: {len(results['datalab'])}")
            print(f"Word count: {len(results['datalab'].split())}")
        else:
            print("COULD NOT EXTRACT TEXT")
            print("-" * 80)
            if 'tesseract_error' in results:
                print(f"Tesseract error: {results['tesseract_error']}")
            if 'datalab_error' in results:
                print(f"Datalab error: {results['datalab_error']}")
            print()
            print("To extract text, install tesseract:")
            print("  sudo apt-get install tesseract-ocr")
        
        print()
        print()
    
    print("=" * 80)
    print("EXTRACTION COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()

