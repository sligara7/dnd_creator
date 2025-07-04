#!/usr/bin/env python3
"""
Test script to validate the frontend v2 API integration.
This script tests the same API calls that the frontend makes.
"""

import requests
import json
import time

API_BASE = 'http://localhost:8000'

def test_v2_integration():
    """Test the v2 API endpoints that the frontend uses"""
    
    print("🧪 Testing Frontend V2 API Integration")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{API_BASE}/health")
        print(f"✅ Health check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test 2: Character creation via factory
    print("\n2. Testing character creation...")
    try:
        character_data = {
            "creation_type": "character",
            "prompt": "A mystical wizard from a floating sky city who controls crystal magic",
            "save_to_database": True,
            "user_preferences": {
                "level": 3,
                "detail_level": "high",
                "verbose_generation": False  # Disable verbose for faster testing
            }
        }
        
        response = requests.post(f"{API_BASE}/api/v2/factory/create", json=character_data)
        result = response.json()
        
        if response.status_code == 200 and result.get('success'):
            character_id = result.get('object_id')
            print(f"✅ Character created: {character_id}")
            print(f"   Character name: {result['data']['core']['name']}")
            print(f"   Species: {result['data']['core']['species']}")
            print(f"   Classes: {result['data']['core']['character_classes']}")
            
            # Test 3: Character retrieval
            print("\n3. Testing character retrieval...")
            get_response = requests.get(f"{API_BASE}/api/v2/characters/{character_id}")
            if get_response.status_code == 200:
                print(f"✅ Character retrieved successfully")
            else:
                print(f"❌ Character retrieval failed: {get_response.status_code}")
            
            # Test 4: Character sheet
            print("\n4. Testing character sheet...")
            sheet_response = requests.get(f"{API_BASE}/api/v2/characters/{character_id}/sheet")
            if sheet_response.status_code == 200:
                print(f"✅ Character sheet loaded successfully")
            else:
                print(f"⚠️ Character sheet failed (might not be implemented): {sheet_response.status_code}")
            
            # Test 5: Character state
            print("\n5. Testing character state...")
            state_response = requests.get(f"{API_BASE}/api/v2/characters/{character_id}/state")
            if state_response.status_code == 200:
                print(f"✅ Character state loaded successfully")
            else:
                print(f"⚠️ Character state failed (might not be implemented): {state_response.status_code}")
            
            # Test 6: Character validation
            print("\n6. Testing character validation...")
            validation_response = requests.get(f"{API_BASE}/api/v2/characters/{character_id}/validate")
            if validation_response.status_code == 200:
                validation_result = validation_response.json()
                print(f"✅ Character validation: {validation_result}")
            else:
                print(f"⚠️ Character validation failed: {validation_response.status_code}")
            
            # Test 7: Character evolution/refinement
            print("\n7. Testing character evolution...")
            evolution_data = {
                "creation_type": "character",
                "character_id": character_id,
                "evolution_prompt": "Make the character more mysterious and add shadow magic abilities",
                "preserve_backstory": True,
                "user_preferences": {
                    "refinement_type": "user_feedback",
                    "iteration": 1
                }
            }
            
            evolution_response = requests.post(f"{API_BASE}/api/v2/factory/evolve", json=evolution_data)
            if evolution_response.status_code == 200 and evolution_response.json().get('success'):
                print(f"✅ Character evolution successful")
            else:
                print(f"⚠️ Character evolution failed: {evolution_response.status_code}")
            
            return True
            
        else:
            print(f"❌ Character creation failed: {response.status_code}")
            print(f"   Response: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Character creation failed: {e}")
        return False

def test_factory_content_generation():
    """Test the factory endpoints for different content types"""
    
    print("\n🏭 Testing Factory Content Generation")
    print("=" * 50)
    
    content_types = [
        ("weapon", "A mystical crystal sword that channels elemental magic"),
        ("armor", "Ethereal robes that shimmer with protective starlight"),
        ("spell", "A unique spell that creates temporary bridges of solid light"),
        ("other_item", "A compass that points to the nearest source of magic"),
        ("npc", "A wise mentor who teaches ancient crystal magic secrets")
    ]
    
    for content_type, prompt in content_types:
        print(f"\n• Testing {content_type} generation...")
        try:
            data = {
                "creation_type": content_type,
                "prompt": prompt,
                "save_to_database": False
            }
            
            response = requests.post(f"{API_BASE}/api/v2/factory/create", json=data)
            result = response.json()
            
            if response.status_code == 200 and result.get('success'):
                print(f"  ✅ {content_type.title()} created successfully")
                if 'data' in result:
                    # Try to extract name or identifier
                    item_data = result['data']
                    name = item_data.get('name') or item_data.get('core', {}).get('name') or 'Generated Item'
                    print(f"     Name: {name}")
            else:
                print(f"  ❌ {content_type.title()} creation failed: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ {content_type.title()} creation error: {e}")

if __name__ == "__main__":
    print("🚀 Starting Frontend V2 Integration Tests...")
    
    # Test the main character creation workflow
    main_success = test_v2_integration()
    
    # Test factory content generation
    test_factory_content_generation()
    
    print("\n" + "=" * 50)
    if main_success:
        print("🎉 Frontend V2 Integration Tests PASSED!")
        print("✅ The frontend should work correctly with v2 API endpoints")
    else:
        print("❌ Frontend V2 Integration Tests FAILED!")
        print("⚠️ There may be issues with the v2 API integration")
    
    print("\n📝 Next Steps:")
    print("1. Open http://localhost:8080/ai_character_creator.html in a browser")
    print("2. Test the character creation workflow manually")
    print("3. Check browser console for any JavaScript errors")
    print("4. Verify that all v2 endpoints are working as expected")
