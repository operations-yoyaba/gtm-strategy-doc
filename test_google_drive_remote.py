#!/usr/bin/env python3
"""
Test Google Drive Service via Cloud Run
"""

import requests
import json
from datetime import datetime

SERVICE_URL = "https://gtm-strategy-doc-areezn3awa-uc.a.run.app"

def test_google_drive_remote():
    """Test Google Drive service via Cloud Run with minimal payload"""
    
    print("🧪 Testing Google Drive Service via Cloud Run")
    print("=" * 50)
    
    # Minimal test payload that should trigger Google Drive creation
    test_payload = {
        "companyId": 99999,
        "stageTs": datetime.utcnow().isoformat(),
        "company": {
            "id": 99999,
            "name": "Google Drive Test Company",
            "domain": "googledrivetest.com",
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
    
    try:
        print("📤 Submitting job...")
        response = requests.post(
            f"{SERVICE_URL}/generate",
            json=test_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            response_id = result.get('response_id')
            print(f"✅ Job submitted successfully!")
            print(f"   Response ID: {response_id}")
            print(f"   Status: {result.get('status')}")
            print(f"   Message: {result.get('message')}")
            
            # Wait a bit and check status
            print(f"\n⏳ Waiting 30 seconds for processing...")
            import time
            time.sleep(30)
            
            # Check job status
            status_response = requests.get(f"{SERVICE_URL}/job-status/{response_id}")
            if status_response.status_code == 200:
                status_data = status_response.json()
                print(f"\n📊 Job Status:")
                print(f"   Status: {status_data.get('status')}")
                print(f"   Company: {status_data.get('company_name')}")
                
                if status_data.get('completion'):
                    completion = status_data['completion']
                    print(f"   ✅ Completed!")
                    print(f"   Doc URL: {completion.get('doc_url')}")
                    print(f"   Token Usage: {completion.get('token_usage', {}).get('total_tokens', 0):,} tokens")
                elif status_data.get('error'):
                    print(f"   ❌ Error: {status_data.get('error')}")
                else:
                    print(f"   ⏳ Still processing...")
            else:
                print(f"❌ Failed to get status: {status_response.status_code}")
                print(f"   Response: {status_response.text}")
        else:
            print(f"❌ Job submission failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_google_drive_remote() 