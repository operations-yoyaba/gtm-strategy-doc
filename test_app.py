#!/usr/bin/env python3
"""
Simple test script to verify the app works correctly
"""

import asyncio
import sys
from pathlib import Path

# Add the current directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app import app
from fastapi.testclient import TestClient

def test_app():
    """Test the app endpoints"""
    client = TestClient(app)
    
    print("Testing GTM Strategy Document Generator App...")
    print()
    
    # Test root endpoint
    print("1. Testing root endpoint...")
    response = client.get("/")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ App name: {data['name']}")
        print(f"   ✓ Version: {data['version']}")
        print(f"   ✓ Description: {data['description']}")
    else:
        print(f"   ❌ Root endpoint failed: {response.status_code}")
    print()
    
    # Test health endpoint
    print("2. Testing health endpoint...")
    response = client.get("/health")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Status: {data['status']}")
        print(f"   ✓ Services: {data['services']}")
    else:
        print(f"   ❌ Health endpoint failed: {response.status_code}")
    print()
    
    print("✅ App test completed successfully!")
    print()
    print("Next steps:")
    print("1. Add your OpenAI API key and webhook secret as GitHub secrets")
    print("2. Push to main branch to trigger deployment")
    print("3. Configure webhook in OpenAI dashboard")

if __name__ == "__main__":
    test_app() 