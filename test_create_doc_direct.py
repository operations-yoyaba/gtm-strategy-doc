#!/usr/bin/env python3
"""
Test Creating Document Directly (Without Template)
"""

import requests
import json

SERVICE_URL = "https://gtm-strategy-doc-areezn3awa-uc.a.run.app"

def test_create_doc_direct():
    """Test creating a document directly without copying template"""
    
    print("🧪 Testing Direct Document Creation")
    print("=" * 40)
    
    # Test payload for direct document creation
    test_payload = {
        "test_mode": "direct_create",
        "companyId": 99999,
        "company": {
            "id": 99999,
            "name": "Direct Create Test Company",
            "domain": "directcreatetest.com",
            "industry": "Technology"
        },
        "dummy_research": {
            "DOC_TITLE": "Test Document Created Directly",
            "INTRO": "This is a test document created directly without template."
        }
    }
    
    try:
        print("📤 Testing direct document creation...")
        response = requests.post(
            f"{SERVICE_URL}/test-create-direct",
            json=test_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Direct document creation successful!")
            print(f"   Doc URL: {result.get('doc_url')}")
            print(f"   Doc ID: {result.get('doc_id')}")
            print(f"   Status: {result.get('status')}")
        else:
            print(f"❌ Direct document creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_create_doc_direct() 