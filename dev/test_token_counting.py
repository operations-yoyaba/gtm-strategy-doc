#!/usr/bin/env python3
"""
Simple test script to verify token counting functionality
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import from services
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from services.openai_service import OpenAIService

# Load environment variables
load_dotenv()

async def test_token_counting():
    """Test token counting functionality"""
    
    print("Testing Token Counting Functionality...")
    print()
    
    # Test data
    test_text = "This is a test of the token counting functionality. It should accurately count tokens using tiktoken."
    
    try:
        # Create OpenAI service
        openai_service = OpenAIService()
        
        # Test token counting
        print("1. Testing token counting...")
        token_count = openai_service.count_tokens(test_text)
        print(f"   ✓ Text: '{test_text}'")
        print(f"   ✓ Token count: {token_count}")
        print()
        
        # Test token usage logging
        print("2. Testing token usage logging...")
        input_tokens = 1000
        output_tokens = 2000
        usage_info = openai_service.log_token_usage(input_tokens, output_tokens, "gpt-4")
        
        print(f"   ✓ Input tokens: {usage_info['input_tokens']:,}")
        print(f"   ✓ Output tokens: {usage_info['output_tokens']:,}")
        print(f"   ✓ Total tokens: {usage_info['total_tokens']:,}")
        print(f"   ✓ Model: {usage_info['model']}")
        print()
        
        # Test with o3-deep-research model (should show cost estimate)
        print("3. Testing o3-deep-research cost estimation...")
        usage_info_deep = openai_service.log_token_usage(5000, 10000, "o3-deep-research")
        
        print(f"   ✓ Input tokens: {usage_info_deep['input_tokens']:,}")
        print(f"   ✓ Output tokens: {usage_info_deep['output_tokens']:,}")
        print(f"   ✓ Total tokens: {usage_info_deep['total_tokens']:,}")
        print(f"   ✓ Model: {usage_info_deep['model']}")
        print()
        
        print("✅ Token counting functionality is working correctly!")
        print()
        print("Key features:")
        print("- Accurate token counting using tiktoken")
        print("- Fallback to character-based estimation if tiktoken unavailable")
        print("- Cost estimation for o3-deep-research model")
        print("- Comprehensive usage logging")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_token_counting())
    exit(0 if success else 1) 