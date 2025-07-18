#!/usr/bin/env python3
"""
Test Google Drive Service Directly
"""

import asyncio
import json
from services.google_docs_service import GoogleDocsService

async def test_google_drive():
    """Test Google Drive service with dummy data"""
    
    print("🧪 Testing Google Drive Service")
    print("=" * 40)
    
    # Create dummy research result
    dummy_research = {
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
    
    # Create dummy GTM context
    dummy_context = {
        "company_name": "Test Company",
        "industry": "Technology",
        "annualrevenue": 1000000
    }
    
    try:
        # Initialize Google Docs service
        google_service = GoogleDocsService()
        print("✅ Google Docs service initialized")
        
        # Test creating a document
        print("\n📄 Creating test document...")
        doc_url, revision_id = await google_service.create_doc_from_template(
            research_result=dummy_research,
            gtm_context=dummy_context,
            company_id="99999",
            company_domain="testcompany.com"
        )
        
        print(f"✅ Document created successfully!")
        print(f"   URL: {doc_url}")
        print(f"   Revision ID: {revision_id}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"   Error type: {type(e).__name__}")
        
        # If it's a Google API error, show more details
        if hasattr(e, 'resp') and hasattr(e, 'content'):
            print(f"   HTTP Status: {e.resp.status}")
            print(f"   Error Content: {e.content.decode()}")

if __name__ == "__main__":
    asyncio.run(test_google_drive()) 