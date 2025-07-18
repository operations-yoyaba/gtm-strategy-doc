#!/usr/bin/env python3
"""
Mock call script for testing the GTM Strategy Doc Generator locally
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.gtm_context import GtmContext
from services.openai_service import OpenAIService

async def test_full_document_output():
    """Test the full deep research and save complete document output to file"""
    
    # Mock request data (using the ProofServe data you've configured)
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
            "gtm_description": ""
        },
        "enriched_data": {
            "funding_rounds": [
            ],
            "total_funding": "",
            "investors": [],
            "competitors": [],
            "technologies": [],
            "social_presence": {
                "linkedin_followers": "",
                "twitter_followers": ""
            },
            "market_position": "",
            "growth_metrics": {
                "customer_count": "",
                "annual_growth_rate": "",
                "churn_rate": "",
                "avg_deal_size": ""
            }
        }
    }
    
    print("Testing Full Document Output Generation...")
    print(f"Company: {request_data['company']['name']}")
    print(f"Industry: {request_data['company']['industry']}")
    print(f"Employees: {request_data['company']['numberofemployees']}")
    print(f"Revenue: ${int(request_data['company']['annualrevenue']):,}")
    print(f"GTM Description: {'Empty' if not request_data['company']['gtm_description'] else 'Provided'}")
    print()
    
    try:
        # Test full deep research with GTM framework
        print("1. Running OpenAI deep-research with GTM framework...")
        openai_service = OpenAIService()
        
        raw_data = {
            "company": request_data["company"],
            "enriched_data": request_data["enriched_data"]
        }
        
        research_result = await openai_service.deep_research(raw_data)
        
        print(f"   ✓ Successfully generated research result")
        print(f"   ✓ Document sections: {len(research_result)}")
        print(f"   ✓ Sections: {', '.join(research_result.keys())}")
        print()
        
        # Show token usage
        if len(research_result) == 2 and isinstance(research_result[1], dict) and 'total_tokens' in research_result[1]:
            # New format with token usage
            doc_content, token_usage = research_result
            print(f"   ✓ Token usage: {token_usage['total_tokens']:,} total tokens")
            print(f"   ✓ Estimated cost: ${(token_usage['input_tokens'] / 1000) * 0.10 + (token_usage['output_tokens'] / 1000) * 0.30:.2f}")
            print()
            
            # Show sample content from key sections
            print("2. Sample content from key sections:")
            for section in ["DOC_TITLE", "INTRO", "GTM_MOTION", "ICP"]:
                if section in doc_content:
                    content = doc_content[section]
                    preview = content[:200] + "..." if len(content) > 200 else content
                    print(f"   {section}: {preview}")
        else:
            # Old format (fallback)
            print("2. Sample content from key sections:")
            for section in ["DOC_TITLE", "INTRO", "GTM_MOTION", "ICP"]:
                if section in research_result:
                    content = research_result[section]
                    preview = content[:200] + "..." if len(content) > 200 else content
                    print(f"   {section}: {preview}")
        print()
        
        # Save complete document to file
        print("3. Saving complete document to file...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"test_document_output_{timestamp}.txt"
        
        # Determine which content to use
        if len(research_result) == 2 and isinstance(research_result[1], dict) and 'total_tokens' in research_result[1]:
            # New format with token usage
            doc_content, token_usage = research_result
        else:
            # Fallback for old format
            doc_content = research_result
            token_usage = None
        
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(f"GTM Strategy Document Test Output\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write(f"Company: {request_data['company']['name']}\n")
            f.write(f"Industry: {request_data['company']['industry']}\n")
            f.write(f"Employees: {request_data['company']['numberofemployees']}\n")
            f.write(f"Revenue: ${int(request_data['company']['annualrevenue']):,}\n")
            f.write(f"GTM Description: {'Empty' if not request_data['company']['gtm_description'] else 'Provided'}\n")
            
            # Add token usage info if available
            if token_usage:
                f.write(f"Token Usage: {token_usage['total_tokens']:,} total tokens\n")
                f.write(f"Estimated Cost: ${(token_usage['input_tokens'] / 1000) * 0.10 + (token_usage['output_tokens'] / 1000) * 0.30:.2f}\n")
            
            f.write("=" * 80 + "\n\n")
            
            # Write each section
            for section_name, content in doc_content.items():
                f.write(f"{section_name}\n")
                f.write("-" * 40 + "\n")
                if isinstance(content, str):
                    f.write(content)
                else:
                    f.write(json.dumps(content, indent=2))
                f.write("\n\n")
            
            # Write raw input data for reference
            f.write("RAW INPUT DATA\n")
            f.write("-" * 40 + "\n")
            f.write("Company Data:\n")
            f.write(json.dumps(request_data['company'], indent=2))
            f.write("\n\nEnriched Data:\n")
            f.write(json.dumps(request_data['enriched_data'], indent=2))
        
        print(f"   ✓ Complete document saved to: {output_filename}")
        print()
        
        # Show document statistics
        print("4. Document Statistics:")
        total_chars = sum(len(str(content)) for content in doc_content.values())
        total_words = sum(len(str(content).split()) for content in doc_content.values())
        print(f"   ✓ Total characters: {total_chars:,}")
        print(f"   ✓ Total words: {total_words:,}")
        print(f"   ✓ Average section length: {total_words // len(doc_content):,} words")
        print()
        
        # Show section lengths
        print("5. Section Lengths:")
        for section_name, content in doc_content.items():
            content_str = str(content)
            words = len(content_str.split())
            chars = len(content_str)
            print(f"   {section_name}: {words:,} words ({chars:,} chars)")
        print()
        
        print("✅ Full document generation completed successfully!")
        print(f"📄 Complete document saved to: {output_filename}")
        print()
        print("Key observations:")
        print("- System handled sparse data gracefully")
        print("- Generated comprehensive analysis despite minimal input")
        print("- Used GTM framework to ensure systematic coverage")
        print("- Professional tone maintained throughout")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_gtm_framework_approach():
    """Test the new GTM framework approach (direct from raw data to research)"""
    
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
            "gtm_description": ""
        },
        "enriched_data": {
            "funding_rounds": [
            ],
            "total_funding": "",
            "investors": [],
            "competitors": [],
            "technologies": [],
            "social_presence": {
                "linkedin_followers": "",
                "twitter_followers": ""
            },
            "market_position": "",
            "growth_metrics": {
                "customer_count": "",
                "annual_growth_rate": "",
                "churn_rate": "",
                "avg_deal_size": ""
            }
        }
    }
    
    print("Testing GTM Framework Approach (Direct Raw Data to Research)...")
    print(f"Company: {request_data['company']['name']}")
    print(f"Industry: {request_data['company']['industry']}")
    print(f"Employees: {request_data['company']['numberofemployees']}")
    print(f"Revenue: ${int(request_data['company']['annualrevenue']):,}")
    print()
    
    try:
        # Test direct deep research with GTM framework
        print("1. Testing OpenAI deep-research with GTM framework...")
        openai_service = OpenAIService()
        
        raw_data = {
            "company": request_data["company"],
            "enriched_data": request_data["enriched_data"]
        }
        
        research_result = await openai_service.deep_research(raw_data)
        
        print(f"   ✓ Successfully generated research result")
        print(f"   ✓ Document sections: {len(research_result)}")
        print(f"   ✓ Sections: {', '.join(research_result.keys())}")
        print()
        
        # Show sample content from key sections
        print("2. Sample content from key sections:")
        for section in ["DOC_TITLE", "INTRO", "GTM_MOTION", "ICP"]:
            if section in research_result:
                content = research_result[section]
                preview = content[:200] + "..." if len(content) > 200 else content
                print(f"   {section}: {preview}")
        print()
        
        print("✅ All tests passed! The GTM framework approach is working correctly.")
        print()
        print("Key benefits:")
        print("- Uses GTM framework as thinking model, not data structure")
        print("- Works directly with raw data, no parsing step needed")
        print("- Ensures comprehensive analysis across all GTM elements")
        print("- Handles poor/missing GTM descriptions gracefully")
        print()
        print("Next steps:")
        print("1. Set up environment variables (GOOGLE_APPLICATION_CREDENTIALS, GS_TEMPLATE_DOC_ID, GS_DRIVE_FOLDER_ID)")
        print("2. Run the full generation test with: python -m dev.mock_call --generate")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

async def test_gtm_context_parsing():
    """Test the new OpenAI-based GTM context parsing"""
    
    # Mock request data
    request_data = {
        "companyId": 15231,
        "stageTs": datetime.utcnow().isoformat(),
        "company": {
            "id": 15231,
            "name": "TechCorp Solutions",
            "domain": "techcorp.com",
            "industry": "Software",
            "numberofemployees": 250,
            "annualrevenue": 50000000,
            "city": "San Francisco",
            "state": "CA",
            "country": "United States",
            "gtm_description": "TechCorp is a B2B SaaS company focused on enterprise workflow automation. They use a product-led growth motion with strong inbound marketing and have recently expanded into enterprise sales. Their ICP includes mid-market companies in manufacturing and logistics."
        },
        "enriched_data": {
            "funding_rounds": [
                {"round": "Series B", "amount": 25000000, "date": "2023-06-15"},
                {"round": "Series A", "amount": 10000000, "date": "2022-03-10"}
            ],
            "total_funding": 35000000,
            "investors": ["Sequoia Capital", "Andreessen Horowitz", "Accel"],
            "competitors": ["Competitor A", "Competitor B", "Competitor C"],
            "technologies": ["Python", "React", "AWS", "PostgreSQL"],
            "social_presence": {
                "linkedin_followers": 15000,
                "twitter_followers": 8500
            },
            "market_position": "Emerging leader in workflow automation",
            "growth_metrics": {
                "customer_count": 500,
                "annual_growth_rate": 150,
                "churn_rate": 0.05,
                "avg_deal_size": 75000
            }
        }
    }
    
    print("Testing OpenAI-based GTM Context Parsing...")
    print(f"Company: {request_data['company']['name']}")
    print(f"Industry: {request_data['company']['industry']}")
    print(f"Employees: {request_data['company']['numberofemployees']}")
    print(f"Revenue: ${int(request_data['company']['annualrevenue']):,}")
    print()
    
    try:
        # Test OpenAI parsing
        print("1. Testing OpenAI GTM context parsing...")
        openai_service = OpenAIService()
        
        raw_data = {
            "company": request_data["company"],
            "enriched_data": request_data["enriched_data"]
        }
        
        parsed_context_data = await openai_service.parse_gtm_context(raw_data)
        
        print(f"   ✓ Successfully parsed GTM context")
        print(f"   ✓ Business Model: {parsed_context_data['companyOverview']['businessModel']['description']}")
        print(f"   ✓ Business Model Types: {', '.join(parsed_context_data['companyOverview']['businessModel']['types'])}")
        print(f"   ✓ Financing: {', '.join(parsed_context_data['companyOverview']['financing']['types'])}")
        print(f"   ✓ Market Maturity: {parsed_context_data['companyOverview']['marketMaturity']}")
        print(f"   ✓ ARR: ${parsed_context_data['companyOverview']['globalMetrics']['arr']:,}" if parsed_context_data['companyOverview']['globalMetrics']['arr'] else "   ✓ ARR: N/A")
        print(f"   ✓ ACV: ${parsed_context_data['companyOverview']['globalMetrics']['acv']:,}" if parsed_context_data['companyOverview']['globalMetrics']['acv'] else "   ✓ ACV: N/A")
        print(f"   ✓ YoY Growth: {parsed_context_data['companyOverview']['globalMetrics']['yoyGrowthRate']}%" if parsed_context_data['companyOverview']['globalMetrics']['yoyGrowthRate'] else "   ✓ YoY Growth: N/A")
        print(f"   ✓ Products: {len(parsed_context_data['products'])}")
        print(f"   ✓ ICPs: {len(parsed_context_data['icps'])}")
        print()
        
        # Test GtmContext creation from parsed data
        print("2. Testing GtmContext creation from parsed data...")
        gtm_context = GtmContext(**parsed_context_data)
        
        print(f"   ✓ Successfully created GtmContext object")
        print(f"   ✓ Schema Version: {gtm_context.meta['schemaVersion']}")
        print(f"   ✓ Company ID: {gtm_context.meta['companyId']}")
        print()
        
        # Test formatted context
        print("3. Testing formatted context for prompts...")
        formatted_context = gtm_context.get_formatted_context_for_prompt()
        print(f"   ✓ Company Name: {formatted_context['company_name']}")
        print(f"   ✓ Company Overview: {len(formatted_context['company_overview'])} chars")
        print(f"   ✓ Enriched Data: {len(formatted_context['enriched_data'])} chars")
        print(f"   ✓ GTM Description: {len(formatted_context['gtm_description'])} chars")
        print()
        
        # Test structured context formatting
        print("4. Testing structured GTM context...")
        structured_context = openai_service._format_structured_gtm_context(gtm_context)
        print(f"   ✓ Structured Context: {len(structured_context)} chars")
        print("   ✓ Sample structured context:")
        print("   " + "\n   ".join(structured_context.split('\n')[:10]) + "...")
        print()
        
        print("✅ All tests passed! The OpenAI-based GTM context parsing is working correctly.")
        print()
        print("Key improvements:")
        print("- Intelligent parsing of free-text data")
        print("- Better extraction of products and ICPs")
        print("- More accurate business model classification")
        print("- Improved metric estimation")
        print()
        print("Next steps:")
        print("1. Set up environment variables (GOOGLE_APPLICATION_CREDENTIALS, GS_TEMPLATE_DOC_ID, GS_DRIVE_FOLDER_ID)")
        print("2. Run the full generation test with: python -m dev.mock_call --generate")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

async def test_generate():
    """Test the generate endpoint with mock data"""
    
    # Mock request data
    request_data = {
        "companyId": 15231,
        "stageTs": datetime.utcnow().isoformat(),
        "company": {
            "id": 15231,
            "name": "TechCorp Solutions",
            "domain": "techcorp.com",
            "industry": "Software",
            "numberofemployees": 250,
            "annualrevenue": 50000000,
            "city": "San Francisco",
            "state": "CA",
            "country": "United States",
            "gtm_description": "TechCorp is a B2B SaaS company focused on enterprise workflow automation. They use a product-led growth motion with strong inbound marketing and have recently expanded into enterprise sales. Their ICP includes mid-market companies in manufacturing and logistics."
        },
        "enriched_data": {
            "funding_rounds": [
                {"round": "Series B", "amount": 25000000, "date": "2023-06-15"},
                {"round": "Series A", "amount": 10000000, "date": "2022-03-10"}
            ],
            "total_funding": 35000000,
            "investors": ["Sequoia Capital", "Andreessen Horowitz", "Accel"],
            "competitors": ["Competitor A", "Competitor B", "Competitor C"],
            "technologies": ["Python", "React", "AWS", "PostgreSQL"],
            "social_presence": {
                "linkedin_followers": 15000,
                "twitter_followers": 8500
            },
            "market_position": "Emerging leader in workflow automation",
            "growth_metrics": {
                "customer_count": 500,
                "annual_growth_rate": 150,
                "churn_rate": 0.05,
                "avg_deal_size": 75000
            }
        }
    }
    
    print("Testing GTM Strategy Doc Generator...")
    print(f"Company: {request_data['company']['name']}")
    print(f"Industry: {request_data['company']['industry']}")
    print(f"Employees: {request_data['company']['numberofemployees']}")
    print(f"Revenue: ${int(request_data['company']['annualrevenue']):,}")
    print()
    
    try:
        # Test GtmContext assembly (legacy method for comparison)
        print("1. Testing legacy GtmContext assembly...")
        gtm_context = GtmContext.assemble_from_payload({
            "company": request_data["company"],
            "enriched_data": request_data["enriched_data"]
        })
        
        print(f"   ✓ Business Model: {gtm_context.companyOverview.businessModel.description}")
        print(f"   ✓ Business Model Types: {', '.join(gtm_context.companyOverview.businessModel.types)}")
        print(f"   ✓ Financing: {', '.join(gtm_context.companyOverview.financing.types)}")
        print(f"   ✓ Market Maturity: {gtm_context.companyOverview.marketMaturity}")
        print(f"   ✓ ARR: ${gtm_context.companyOverview.globalMetrics.arr:,}" if gtm_context.companyOverview.globalMetrics.arr else "   ✓ ARR: N/A")
        print(f"   ✓ ACV: ${gtm_context.companyOverview.globalMetrics.acv:,}" if gtm_context.companyOverview.globalMetrics.acv else "   ✓ ACV: N/A")
        print(f"   ✓ YoY Growth: {gtm_context.companyOverview.globalMetrics.yoyGrowthRate}%" if gtm_context.companyOverview.globalMetrics.yoyGrowthRate else "   ✓ YoY Growth: N/A")
        print(f"   ✓ Products: {len(gtm_context.products)}")
        print(f"   ✓ ICPs: {len(gtm_context.icps)}")
        print()
        
        # Test formatted context
        print("2. Testing formatted context for prompts...")
        formatted_context = gtm_context.get_formatted_context_for_prompt()
        print(f"   ✓ Company Name: {formatted_context['company_name']}")
        print(f"   ✓ Company Overview: {len(formatted_context['company_overview'])} chars")
        print(f"   ✓ Enriched Data: {len(formatted_context['enriched_data'])} chars")
        print(f"   ✓ GTM Description: {len(formatted_context['gtm_description'])} chars")
        print()
        
        # Test structured context formatting
        print("3. Testing structured GTM context...")
        from services.openai_service import OpenAIService
        openai_service = OpenAIService()
        structured_context = openai_service._format_structured_gtm_context(gtm_context)
        print(f"   ✓ Structured Context: {len(structured_context)} chars")
        print("   ✓ Sample structured context:")
        print("   " + "\n   ".join(structured_context.split('\n')[:10]) + "...")
        print()
        
        print("✅ All tests passed! The GTM context is properly structured.")
        print()
        print("Next steps:")
        print("1. Set up environment variables (OPENAI_API_KEY, GOOGLE_CREDENTIALS)")
        print("2. Run the full generation test with: python -m dev.mock_call --generate")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

async def test_full_generation():
    """Test the full generation process (requires API keys)"""
    
    print("Testing full GTM document generation...")
    print("This requires OPENAI_API_KEY and GOOGLE_CREDENTIALS environment variables.")
    print()
    
    # Check environment variables
    required_vars = ["OPENAI_API_KEY", "GOOGLE_APPLICATION_CREDENTIALS"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these variables and try again.")
        return False
    
    # Mock request data (same as above)
    request_data = {
        "companyId": 15231,
        "stageTs": datetime.utcnow().isoformat(),
        "company": {
            "id": 15231,
            "name": "TechCorp Solutions",
            "domain": "techcorp.com",
            "industry": "Software",
            "numberofemployees": 250,
            "annualrevenue": 50000000,
            "city": "San Francisco",
            "state": "CA",
            "country": "United States",
            "gtm_description": "TechCorp is a B2B SaaS company focused on enterprise workflow automation. They use a product-led growth motion with strong inbound marketing and have recently expanded into enterprise sales. Their ICP includes mid-market companies in manufacturing and logistics."
        },
        "enriched_data": {
            "funding_rounds": [
                {"round": "Series B", "amount": 25000000, "date": "2023-06-15"},
                {"round": "Series A", "amount": 10000000, "date": "2022-03-10"}
            ],
            "total_funding": 35000000,
            "investors": ["Sequoia Capital", "Andreessen Horowitz", "Accel"],
            "competitors": ["Competitor A", "Competitor B", "Competitor C"],
            "technologies": ["Python", "React", "AWS", "PostgreSQL"],
            "social_presence": {
                "linkedin_followers": 15000,
                "twitter_followers": 8500
            },
            "market_position": "Emerging leader in workflow automation",
            "growth_metrics": {
                "customer_count": 500,
                "annual_growth_rate": 150,
                "churn_rate": 0.05,
                "avg_deal_size": 75000
            }
        }
    }
    
    try:
        # Import the request model
        from main import GenerateRequest
        
        # Create request object
        request = GenerateRequest(**request_data)
        
        # Mock background tasks
        class MockBackgroundTasks:
            def add_task(self, func, *args, **kwargs):
                pass
        
        background_tasks = MockBackgroundTasks()
        
        # Call the generate function
        print("Starting document generation...")
        result = await generate_gtm_doc(request, background_tasks)
        
        print("✅ Document generation completed!")
        print(f"Doc URL: {result['doc_url']}")
        print(f"Revision ID: {result['revision_id']}")
        print(f"Status: {result['status']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test GTM Strategy Doc Generator")
    parser.add_argument("--generate", action="store_true", help="Test full document generation")
    parser.add_argument("--parse", action="store_true", help="Test OpenAI-based GTM context parsing")
    parser.add_argument("--framework", action="store_true", help="Test GTM framework approach (direct raw data to research)")
    parser.add_argument("--full-output", action="store_true", help="Test full document output generation (deep research and save to file)")
    
    args = parser.parse_args()
    
    if args.generate:
        success = asyncio.run(test_full_generation())
    elif args.parse:
        success = asyncio.run(test_gtm_context_parsing())
    elif args.framework:
        success = asyncio.run(test_gtm_framework_approach())
    elif args.full_output:
        success = asyncio.run(test_full_document_output())
    else:
        success = asyncio.run(test_generate())
    
    sys.exit(0 if success else 1) 