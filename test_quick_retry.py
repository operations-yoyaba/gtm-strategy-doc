#!/usr/bin/env python3
"""
Quick Retry Test - Test the system again after fixing permissions
"""

import requests
from datetime import datetime

SERVICE_URL = "https://gtm-strategy-doc-areezn3awa-uc.a.run.app"

def test_quick_retry():
    """Quick test to see if the system works after permission fix"""
    
    # Simple test payload
    test_payload = {
        "companyId": 99999,
        "stageTs": datetime.utcnow().isoformat(),
        "company": {
            "id": 99999,
            "name": "Test Company",
            "domain": "testcompany.com",
            "industry": "Technology",
            "annualrevenue": 1000000,
            "numberofemployees": 10
        },
        "enriched_data": {
            "funding_rounds": [],
            "total_funding": 0,
            "investors": [],
            "competitors": [],
            "technologies": [],
            "market_position": "Startup",
            "growth_metrics": {
                "annual_growth_rate": 50,
                "avg_deal_size": 10000,
                "customer_count": 100
            }
        }
    }
    
    print("🧪 Quick Retry Test")
    print("=" * 30)
    
    try:
        response = requests.post(
            f"{SERVICE_URL}/generate",
            json=test_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Job submitted successfully!")
            print(f"   Response ID: {result.get('response_id')}")
            print(f"   Status: {result.get('status')}")
            print(f"   Message: {result.get('message')}")
            print(f"\n💡 Check status in 15 minutes:")
            print(f"   curl '{SERVICE_URL}/job-status/{result.get('response_id')}'")
        else:
            print(f"❌ Job submission failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_quick_retry() 