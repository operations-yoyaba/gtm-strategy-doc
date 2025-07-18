#!/usr/bin/env python3
"""
Test Google Drive Service Only - No OpenAI
"""

import requests
import json

SERVICE_URL = "https://gtm-strategy-doc-areezn3awa-uc.a.run.app"

def test_google_drive_only():
    """Test Google Drive service directly without OpenAI"""
    
    print("🧪 Testing Google Drive Service Only")
    print("=" * 40)
    
    # Test payload with dummy research result (bypassing OpenAI)
    test_payload = {
        "test_mode": True,  # Flag to indicate this is a test
        "companyId": 99999,
        "company": {
            "id": 99999,
            "name": "Google Drive Test Company",
            "domain": "googledrivetest.com",
            "industry": "Technology"
        },
        "dummy_research_result": {
            "DOC_TITLE": "Test GTM Strategy Document",
            "INTRO": "This is a test introduction for the GTM strategy document.",
            "PRICING_PACKAGING": "Test pricing and packaging information.",
            "GTM_MOTION": "Test GTM motion details.",
            "TOUCH_MODEL": "Test touch model information.",
            "ICP": "Test ICP details.",
            "METRICS": "Test metrics information.",
            "FINANCIALS": "Test financial information.",
            "FINANCING": "Test financing details.",
            "MARKET_MATURITY": "Test market maturity analysis.",
            "STAKEHOLDERS": "Test stakeholder information.",
            "SUMMARY_TABLE": "Test summary table."
        }
    }
    
    try:
        print("📤 Testing Google Drive creation...")
        response = requests.post(
            f"{SERVICE_URL}/test-google-drive",
            json=test_payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Google Drive test successful!")
            print(f"   Doc URL: {result.get('doc_url')}")
            print(f"   Folder: {result.get('folder_name')}")
            print(f"   Status: {result.get('status')}")
        else:
            print(f"❌ Google Drive test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_google_drive_only() 