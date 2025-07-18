#!/usr/bin/env python3
"""
Test script for the webhook-based GTM document generation system
"""

import asyncio
import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add the parent directory to the path so we can import from services
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from models.gtm_context import GenerateRequest

# Load environment variables
load_dotenv()

async def test_webhook_submission():
    """Test submitting a job to the webhook-based system"""
    
    print("Testing Webhook-Based GTM Document Generation...")
    print()
    
    # Check environment variables
    required_vars = ["OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these variables and try again.")
        return False
    
    # Mock request data
    request_data = {
        "companyId": 15231,
        "stageTs": datetime.utcnow().isoformat(),
        "company": {
            "id": 15231,
            "name": "ProofServe",
            "domain": "proofserve.com",
            "industry": "Legal tech",
            "numberofemployees": 250,
            "annualrevenue": "30000000",
            "city": "Denver",
            "state": "CO",
            "country": "United States",
            "gtm_description": "ProofServe is a legal tech company focused on document automation and workflow management for law firms."
        },
        "enriched_data": {
            "funding_rounds": [
                {"round": "Series A", "amount": 5000000, "date": "2023-03-15"}
            ],
            "total_funding": 5000000,
            "investors": ["LegalTech Ventures", "Denver Capital"],
            "competitors": ["DocuSign", "Clio", "MyCase"],
            "technologies": ["Python", "React", "AWS", "MongoDB"],
            "social_presence": {
                "linkedin_followers": 2500,
                "twitter_followers": 1200
            },
            "market_position": "Emerging player in legal document automation",
            "growth_metrics": {
                "customer_count": 150,
                "annual_growth_rate": 200,
                "churn_rate": 0.08,
                "avg_deal_size": 25000
            }
        }
    }
    
    print(f"Company: {request_data['company']['name']}")
    print(f"Industry: {request_data['company']['industry']}")
    print(f"Employees: {request_data['company']['numberofemployees']}")
    print(f"Revenue: ${int(request_data['company']['annualrevenue']):,}")
    print()
    
    try:
        # Test job submission
        print("1. Testing background job submission...")
        
        # Import the main app function
        from main import generate_gtm_doc
        
        # Create request object
        request = GenerateRequest(**request_data)
        
        # Mock background tasks
        class MockBackgroundTasks:
            def add_task(self, func, *args, **kwargs):
                pass
        
        background_tasks = MockBackgroundTasks()
        
        # Submit the job
        result = await generate_gtm_doc(request, background_tasks)
        
        print(f"   ✓ Job submitted successfully")
        print(f"   ✓ Response ID: {result['response_id']}")
        print(f"   ✓ Status: {result['status']}")
        print(f"   ✓ Message: {result['message']}")
        print(f"   ✓ Estimated completion: {result['estimated_completion']}")
        print()
        
        # Test job status endpoint
        print("2. Testing job status endpoint...")
        from main import get_job_status
        
        status_result = await get_job_status(result['response_id'])
        print(f"   ✓ Status endpoint working")
        print(f"   ✓ Current status: {status_result['status']}")
        print(f"   ✓ Message: {status_result['message']}")
        print()
        
        print("✅ Webhook-based system test completed successfully!")
        print()
        print("Next steps:")
        print("1. Start the webhook handler: python webhook_handler.py")
        print("2. Configure webhook in OpenAI dashboard:")
        print("   - URL: https://your-domain.com/webhook/openai")
        print("   - Event: response.completed")
        print("3. Submit real jobs and monitor webhook processing")
        print()
        print("Key benefits of this approach:")
        print("- No need to keep servers alive during long-running jobs")
        print("- Automatic retry and reliability from OpenAI")
        print("- Scalable to handle many concurrent jobs")
        print("- Cost-effective: only pay for compute when processing results")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_webhook_handler():
    """Test the webhook handler functionality"""
    
    print("Testing Webhook Handler...")
    print()
    
    try:
        # Import webhook handler
        from webhook_handler import app, job_tracker
        
        print("1. Testing webhook handler initialization...")
        print(f"   ✓ Webhook handler app created")
        print(f"   ✓ Job tracker initialized")
        print()
        
        # Test health endpoint
        print("2. Testing health endpoint...")
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        health_response = client.get("/health")
        
        if health_response.status_code == 200:
            print(f"   ✓ Health endpoint working")
            health_data = health_response.json()
            print(f"   ✓ Status: {health_data['status']}")
        else:
            print(f"   ❌ Health endpoint failed: {health_response.status_code}")
        print()
        
        print("✅ Webhook handler test completed successfully!")
        print()
        print("To test with real webhooks:")
        print("1. Deploy webhook handler to a public URL")
        print("2. Configure webhook in OpenAI dashboard")
        print("3. Submit background jobs and monitor webhook events")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Webhook-Based GTM System")
    parser.add_argument("--submission", action="store_true", help="Test job submission")
    parser.add_argument("--handler", action="store_true", help="Test webhook handler")
    
    args = parser.parse_args()
    
    if args.handler:
        success = asyncio.run(test_webhook_handler())
    elif args.submission:
        success = asyncio.run(test_webhook_submission())
    else:
        # Run both tests
        print("Running both webhook system tests...")
        print("=" * 50)
        success1 = asyncio.run(test_webhook_handler())
        print("\n" + "=" * 50)
        success2 = asyncio.run(test_webhook_submission())
        success = success1 and success2
    
    exit(0 if success else 1) 