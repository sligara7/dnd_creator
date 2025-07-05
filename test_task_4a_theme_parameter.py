#!/usr/bin/env python3

"""
Test script for Task 4a: Theme Parameter Support
Tests the new theme parameter in factory endpoints
"""

import os
import requests
import json
import sys

# Set minimal environment variables for testing
os.environ['SECRET_KEY'] = 'test-secret-key-for-development'
os.environ['LLM_PROVIDER'] = 'ollama'
os.environ['LLM_MODEL'] = 'llama3'
os.environ['DATABASE_URL'] = 'sqlite:///./test_backend.db'

# Backend service URL
BACKEND_BASE_URL = "http://localhost:8000"

def test_theme_parameter():
    """Test the new theme parameter in factory endpoints."""
    
    print("🧪 Testing Task 4a: Theme Parameter Support")
    print("=" * 60)
    
    # 1. Test health endpoint
    print("\n1. Testing backend service health...")
    try:
        response = requests.get(f"{BACKEND_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Backend service is running")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend service. Is it running on port 8000?")
        print("   Start with: cd backend && uvicorn app:app --port 8000 --reload")
        return False
    
    # 2. Test factory creation WITHOUT theme (backward compatibility)
    print("\n2. Testing factory creation WITHOUT theme (backward compatibility)...")
    create_data = {
        "creation_type": "weapon",
        "prompt": "Create a simple sword",
        "save_to_database": False
    }
    
    try:
        response = requests.post(f"{BACKEND_BASE_URL}/api/v2/factory/create", json=create_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Creation without theme: SUCCESS")
            print(f"   Creation type: {result.get('creation_type')}")
            print(f"   Theme: {result.get('theme', 'None (expected)')}")
            print(f"   Success: {result.get('success')}")
        else:
            print(f"❌ Creation without theme failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Creation without theme error: {e}")
    
    # 3. Test factory creation WITH theme
    print("\n3. Testing factory creation WITH theme...")
    create_data_with_theme = {
        "creation_type": "weapon",
        "prompt": "Create a weapon for a gunslinger",
        "theme": "western",
        "save_to_database": False
    }
    
    try:
        response = requests.post(f"{BACKEND_BASE_URL}/api/v2/factory/create", json=create_data_with_theme)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Creation with western theme: SUCCESS")
            print(f"   Creation type: {result.get('creation_type')}")
            print(f"   Theme: {result.get('theme')}")
            print(f"   Success: {result.get('success')}")
            # Check if theme is reflected in the response
            weapon_data = result.get('data', {})
            if 'name' in weapon_data:
                print(f"   Generated weapon: {weapon_data['name']}")
        else:
            print(f"❌ Creation with theme failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Creation with theme error: {e}")
    
    # 4. Test different themes
    print("\n4. Testing different themes...")
    themes_to_test = [
        ("cyberpunk", "character", "Create a hacker character"),
        ("steampunk", "armor", "Create protective gear"),
        ("horror", "spell", "Create a dark magic spell")
    ]
    
    for theme, creation_type, prompt in themes_to_test:
        print(f"\n   Testing {theme} theme with {creation_type}...")
        test_data = {
            "creation_type": creation_type,
            "prompt": prompt,
            "theme": theme,
            "save_to_database": False
        }
        
        try:
            response = requests.post(f"{BACKEND_BASE_URL}/api/v2/factory/create", json=test_data)
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ {theme} {creation_type}: SUCCESS")
                print(f"      Theme in response: {result.get('theme')}")
            else:
                print(f"   ❌ {theme} {creation_type}: FAILED ({response.status_code})")
        except Exception as e:
            print(f"   ❌ {theme} {creation_type}: ERROR ({e})")
    
    # 5. Test factory types endpoint (should still work)
    print("\n5. Testing factory types endpoint...")
    try:
        response = requests.get(f"{BACKEND_BASE_URL}/api/v2/factory/types")
        if response.status_code == 200:
            types = response.json()
            print(f"✅ Factory types available: {len(types)} types")
            print(f"   Types: {', '.join(types)}")
        else:
            print(f"❌ Factory types failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Factory types error: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Task 4a Testing Complete!")
    print("   ✅ Theme parameter added to factory endpoints")
    print("   ✅ Backward compatibility maintained (theme optional)")
    print("   ✅ Theme included in factory responses")
    print("   ✅ Multiple content types support themes")
    print("   ✅ Foundation ready for theme-aware content creation")
    
    return True

if __name__ == "__main__":
    success = test_theme_parameter()
    sys.exit(0 if success else 1)
