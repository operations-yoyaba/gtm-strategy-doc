#!/usr/bin/env python3
"""
Test Shared Drive Write Access
"""

import requests
import json

SERVICE_URL = "https://gtm-strategy-doc-areezn3awa-uc.a.run.app"

def test_shared_drive_write():
    """Test if service account can write to Shared Drive"""
    
    print("🧪 Testing Shared Drive Write Access")
    print("=" * 40)
    
    # Test payload
    test_payload = {
        "test_mode": "shared_drive_write",
        "shared_drive_id": "0AC3eBtdW1kwVUk9PVA"
    }
    
    try:
        print("📤 Testing Shared Drive write access...")
        response = requests.post(
            f"{SERVICE_URL}/test-shared-drive-write",
            json=test_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Shared Drive write test successful!")
            print(f"   Document URL: {result.get('doc_url')}")
            print(f"   Document ID: {result.get('doc_id')}")
            print(f"   Status: {result.get('status')}")
        else:
            print(f"❌ Shared Drive write test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_shared_drive_write() 