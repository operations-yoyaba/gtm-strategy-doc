#!/usr/bin/env python3
"""
Simple Document Creation Test
"""

import requests
import json

SERVICE_URL = "https://gtm-strategy-doc-areezn3awa-uc.a.run.app"

def test_simple_doc():
    """Test creating a simple document without template"""
    
    print("🧪 Testing Simple Document Creation")
    print("=" * 40)
    
    # Simple test payload
    test_payload = {
        "test_mode": "simple_doc",
        "companyId": 99999,
        "company": {
            "id": 99999,
            "name": "Simple Test Company",
            "domain": "simpletest.com",
            "industry": "Technology"
        }
    }
    
    try:
        print("📤 Testing simple document creation...")
        response = requests.post(
            f"{SERVICE_URL}/test-simple-doc",
            json=test_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Simple document creation successful!")
            print(f"   Doc URL: {result.get('doc_url')}")
            print(f"   Doc ID: {result.get('doc_id')}")
            print(f"   Status: {result.get('status')}")
        else:
            print(f"❌ Simple document creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_simple_doc() 