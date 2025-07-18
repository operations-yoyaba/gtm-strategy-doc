#!/usr/bin/env python3
"""
Full System Test - End-to-End GTM Strategy Document Generation
Tests the complete flow from HubSpot webhook to Google Doc creation
"""

import os
import json
import asyncio
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
SERVICE_URL = "https://gtm-strategy-doc-areezn3awa-uc.a.run.app"
WEBHOOK_URL = f"{SERVICE_URL}/webhook/openai"

def test_health_check():
    """Test if the service is healthy"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{SERVICE_URL}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health check passed: {health_data}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def create_test_payload():
    """Create a realistic test payload for ProofServe"""
    return {
        "companyId": 12345,
        "stageTs": datetime.utcnow().isoformat(),
        "company": {
            "id": 12345,
            "name": "ProofServe",
            "domain": "proofserve.com",
            "industry": "Legal Technology",
            "annualrevenue": 5000000,
            "numberofemployees": 50,
            "city": "Denver",
            "state": "Colorado",
            "country": "United States",
            "gtm_description": "ProofServe is a legal technology platform revolutionizing how legal documents are served and filed. They operate a nationwide network of process servers and provide electronic court filing services."
        },
        "enriched_data": {
            "funding_rounds": [
                {"round": "Series B", "amount": 30400000, "date": "2024-01"},
                {"round": "Series A", "amount": 7000000, "date": "2022-03"}
            ],
            "total_funding": 37400000,
            "investors": ["Long Ridge Equity Partners", "Blue Heron Capital", "The LegalTech Fund", "Clio Ventures"],
            "competitors": ["ABC Legal", "One Legal", "ServeManager"],
            "technologies": ["Mobile Apps", "GPS Tracking", "Real-time Updates", "API Integrations"],
            "social_presence": {
                "linkedin_followers": 2500,
                "twitter_followers": 1200
            },
            "market_position": "Market leader in on-demand process serving",
            "growth_metrics": {
                "annual_growth_rate": 100,
                "avg_deal_size": 75,
                "customer_count": 5000
            }
        }
    }

def test_job_submission():
    """Test submitting a deep research job"""
    print("\n🚀 Testing job submission...")
    
    payload = create_test_payload()
    
    try:
        response = requests.post(
            f"{SERVICE_URL}/generate",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Job submitted successfully!")
            print(f"   Response ID: {result.get('response_id')}")
            print(f"   Status: {result.get('status')}")
            print(f"   Message: {result.get('message')}")
            return result.get('response_id')
        else:
            print(f"❌ Job submission failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Job submission error: {e}")
        return None

def test_job_status(response_id):
    """Test checking job status"""
    print(f"\n📊 Testing job status for {response_id}...")
    
    try:
        response = requests.get(f"{SERVICE_URL}/job-status/{response_id}", timeout=10)
        
        if response.status_code == 200:
            status_data = response.json()
            print(f"✅ Job status retrieved:")
            print(f"   Company: {status_data.get('company_name')}")
            print(f"   Status: {status_data.get('status')}")
            print(f"   Submitted: {status_data.get('submitted_at')}")
            
            if status_data.get('completion'):
                print(f"   ✅ Job completed!")
                print(f"   Doc URL: {status_data.get('completion', {}).get('doc_url')}")
                print(f"   Token Usage: {status_data.get('completion', {}).get('token_usage', {})}")
            else:
                print(f"   ⏳ Job still processing...")
                
            return status_data
        else:
            print(f"❌ Status check failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Status check error: {e}")
        return None

def test_webhook_simulation():
    """Simulate a webhook call (for testing purposes)"""
    print("\n🔗 Testing webhook simulation...")
    
    # This would normally come from OpenAI, but we'll simulate it
    webhook_payload = {
        "type": "response.completed",
        "data": {
            "id": "test-response-123",
            "status": "completed",
            "output_text": json.dumps({
                "DOC_TITLE": "ProofServe.com Go-To-Market Strategy Overview",
                "INTRO": "ProofServe (Proof Technology, Inc.) is a legal technology platform revolutionizing how legal documents are served and filed...",
                "PRICING_PACKAGING": "Consumption-Based Pricing: Proofserve employs a straightforward pay-per-use pricing model...",
                "GTM_MOTION": "Proofserve utilizes a hybrid Go-to-Market motion that blends product-led growth with targeted sales...",
                "TOUCH_MODEL": "Proofserve serves a diverse customer base with varying needs, so it employs different engagement 'touch' models...",
                "ICP": "Proofserve's Ideal Customer Profile is defined primarily by industry vertical and use case...",
                "METRICS": "Proofserve has demonstrated strong growth since its launch...",
                "FINANCIALS": "As a private VC-backed company, detailed financial figures for Proofserve are not publicly disclosed...",
                "FINANCING": "Proofserve is venture-backed, with a financing history that has enabled its rapid growth...",
                "MARKET_MATURITY": "Proofserve operates at the intersection of the LegalTech market and the traditional process serving industry...",
                "STAKEHOLDERS": "Proofserve's leadership and stakeholders provide insight into the company's direction...",
                "SUMMARY_TABLE": "Aspect | Proofserve's Current Approach\nPricing Model | Consumption-based, pay-per-use..."
            })
        }
    }
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=webhook_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Webhook simulation successful")
            return True
        else:
            print(f"❌ Webhook simulation failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Webhook simulation error: {e}")
        return False

def main():
    """Run the full system test"""
    print("🧪 Starting Full System Test")
    print("=" * 50)
    
    # Test 1: Health Check
    if not test_health_check():
        print("❌ Health check failed. Stopping test.")
        return
    
    # Test 2: Job Submission
    response_id = test_job_submission()
    if not response_id:
        print("❌ Job submission failed. Stopping test.")
        return
    
    # Test 3: Job Status Check
    print("\n⏳ Waiting 5 seconds before checking status...")
    import time
    time.sleep(5)
    
    status_data = test_job_status(response_id)
    if not status_data:
        print("❌ Status check failed.")
        return
    
    # Test 4: Webhook Simulation (optional)
    print("\n🔗 Testing webhook simulation...")
    test_webhook_simulation()
    
    print("\n" + "=" * 50)
    print("🎉 Full System Test Complete!")
    print("\n📋 Summary:")
    print(f"   Service URL: {SERVICE_URL}")
    print(f"   Response ID: {response_id}")
    print(f"   Job Status: {status_data.get('status', 'unknown')}")
    
    if status_data.get('completion'):
        print(f"   ✅ Document created: {status_data.get('completion', {}).get('doc_url')}")
    else:
        print("   ⏳ Job is still processing (this is normal for background jobs)")
        print("   💡 Check the webhook logs for completion status")

if __name__ == "__main__":
    main() 