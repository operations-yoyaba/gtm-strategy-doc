#!/usr/bin/env python3
"""
Test Template Document Access
"""

import requests
import json

SERVICE_URL = "https://gtm-strategy-doc-areezn3awa-uc.a.run.app"

def test_template_access():
    """Test if we can access the template document"""
    
    print("🧪 Testing Template Document Access")
    print("=" * 40)
    
    # Test payload that just tries to access the template
    test_payload = {
        "test_mode": "template_access",
        "companyId": 99999,
        "company": {
            "id": 99999,
            "name": "Template Test Company",
            "domain": "templatetest.com",
            "industry": "Technology"
        }
    }
    
    try:
        print("📤 Testing template access...")
        response = requests.post(
            f"{SERVICE_URL}/test-template-access",
            json=test_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Template access successful!")
            print(f"   Template ID: {result.get('template_id')}")
            print(f"   Template Name: {result.get('template_name')}")
            print(f"   Access: {result.get('access_status')}")
        else:
            print(f"❌ Template access failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_template_access() 