#!/usr/bin/env python3
"""
Test script for MaatLangChain FastAPI endpoints
"""

import requests
import json
import time
from typing import Dict, Any

API_BASE = "http://localhost:8019"


def test_endpoint(
    method: str, path: str, data: Dict[str, Any] = None, params: Dict[str, Any] = None
):
    """Test an API endpoint."""
    url = f"{API_BASE}{path}"

    try:
        if method == "GET":
            response = requests.get(url, params=params, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        else:
            return {"status": "error", "message": f"Unsupported method: {method}"}

        return {
            "status": "success" if response.status_code < 400 else "error",
            "status_code": response.status_code,
            "data": response.json()
            if response.headers.get("content-type", "").startswith("application/json")
            else response.text,
        }
    except requests.exceptions.ConnectionError:
        return {"status": "error", "message": "Could not connect to API server"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def main():
    """Run all endpoint tests."""
    print("🧪 Testing MaatLangChain FastAPI Endpoints")
    print("=" * 50)

    tests = [
        {"name": "Health Check", "method": "GET", "path": "/health"},
        {"name": "Root Endpoint", "method": "GET", "path": "/"},
        {
            "name": "RAG Query",
            "method": "POST",
            "path": "/rag/query",
            "data": {
                "question": "What is Maat?",
                "top_k": 3,
                "collection_name": "maat_knowledge",
            },
        },
        {
            "name": "View Chunks",
            "method": "POST",
            "path": "/rag/chunks",
            "data": {"pdf_name": None, "limit": 5, "skip_toc": True},
        },
        {
            "name": "Get Stats",
            "method": "GET",
            "path": "/rag/stats",
            "params": {"collection_name": "maat_knowledge"},
        },
        {"name": "List Collections", "method": "GET", "path": "/rag/collections"},
    ]

    results = []

    for test in tests:
        print(f"\n🔍 Testing: {test['name']}")
        result = test_endpoint(
            method=test["method"],
            path=test["path"],
            data=test.get("data"),
            params=test.get("params"),
        )

        results.append({"name": test["name"], "result": result})

        if result["status"] == "success":
            print(f"✅ {test['name']}: {result['status_code']}")
            # Show brief data preview
            if isinstance(result.get("data"), dict):
                keys = list(result["data"].keys())[:3]
                print(f"   Data keys: {keys}")
            else:
                preview = str(result["data"])[:100]
                print(f"   Data: {preview}...")
        else:
            print(f"❌ {test['name']}: {result.get('message', 'Unknown error')}")

    print("\n" + "=" * 50)
    print("📊 Test Summary:")

    success_count = sum(1 for r in results if r["result"]["status"] == "success")
    total_count = len(results)

    print(f"   Successful: {success_count}/{total_count}")
    print(f"   Failed: {total_count - success_count}/{total_count}")

    if success_count == total_count:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Check the API server is running on port 8019.")
        print("\nTo start the API server:")
        print("   cd /home/suspect/.n8n/maatlangchain")
        print("   python3 api/main.py")


if __name__ == "__main__":
    main()
