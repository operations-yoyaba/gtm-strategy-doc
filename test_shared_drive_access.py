#!/usr/bin/env python3
"""
Test Shared Drive Access
"""

import requests
import json

SERVICE_URL = "https://gtm-strategy-doc-areezn3awa-uc.a.run.app"

def test_shared_drive_access():
    """Test access to Shared Drive and template document"""
    
    print("🧪 Testing Shared Drive Access")
    print("=" * 40)
    
    # Test payload
    test_payload = {
        "test_mode": "shared_drive_access",
        "shared_drive_id": "0AC3eBtdW1kwVUk9PVA",
        "template_doc_id": "1hhBU5pwfPGiuE0X5fokhhkmLBF1Lwz7_j2aRKPzWrQU"
    }
    
    try:
        print("📤 Testing Shared Drive access...")
        response = requests.post(
            f"{SERVICE_URL}/test-shared-drive-access",
            json=test_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Shared Drive access test successful!")
            print(f"   Shared Drive ID: {result.get('shared_drive_id')}")
            print(f"   Template Access: {result.get('template_access')}")
            print(f"   Service Account: {result.get('service_account')}")
            print(f"   Permissions: {result.get('permissions')}")
        else:
            print(f"❌ Shared Drive access test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_shared_drive_access() 