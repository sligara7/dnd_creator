#!/usr/bin/env python3
"""
Interactive testing script for D&D Character Creator Backend
Run this script to manually test different components
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from main import CharacterCreationBackend

def test_backend_functionality():
    """Test the main backend functionality interactively."""
    
    print("=== D&D Character Creator Backend Testing ===\n")
    
    # Initialize the backend
    print("1. Initializing backend...")
    backend = CharacterCreationBackend()
    
    # Test health status
    print("\n2. Testing health status...")
    health = backend.get_health_status()
    print(f"Status: {health['status']}")
    print(f"Services: {health['services']}")
    
    # Test character creation
    print("\n3. Testing character creation...")
    test_descriptions = [
        "A brave human fighter with a mysterious past",
        "An elven wizard who loves books",
        "A sneaky halfling rogue"
    ]
    
    for i, desc in enumerate(test_descriptions, 1):
        print(f"\n   Test {i}: {desc}")
        result = backend.create_character(desc, level=2, generate_backstory=True)
        
        if result["success"]:
            print(f"   ✅ Success! Character: {result['character']['name'] if result['character'] else 'No name'}")
            print(f"   ⏱️  Creation time: {result['creation_time']:.2f}s")
            
            # Test validation
            if result['character']:
                print("   🔍 Testing validation...")
                validation = backend.validate_character(result['character'])
                print(f"   📊 Validation score: {validation['score']:.2f}")
                print(f"   ✅ Valid: {validation['valid']}")
                
                # Test formatting
                print("   📝 Testing formatting...")
                formatted = backend.format_character(result['character'], "summary")
                if formatted['success']:
                    print("   ✅ Formatting successful")
                    print(f"   📄 Preview: {formatted['formatted_text'][:100]}...")
                else:
                    print("   ❌ Formatting failed")
        else:
            print(f"   ❌ Failed: {result['error']}")
        
        print("-" * 60)
    
    print("\n=== Testing Complete ===")

def test_individual_components():
    """Test individual components separately."""
    
    print("=== Individual Component Testing ===\n")
    
    try:
        # Test character creation component
        print("1. Testing CharacterCreator...")
        from character_creation import CharacterCreator, CreationConfig
        from llm_services import create_llm_service
        
        config = CreationConfig()
        llm_service = create_llm_service()
        creator = CharacterCreator(llm_service, config)
        
        result = creator.create_character("A test character", 1, False, False)
        print(f"   Result: {result.success}")
        
    except Exception as e:
        print(f"   ❌ CharacterCreator error: {e}")
    
    try:
        # Test validation component
        print("\n2. Testing CharacterValidator...")
        from validation import CharacterValidator
        
        validator = CharacterValidator()
        test_data = {
            "name": "Test Character",
            "level": 1,
            "species": "Human"
        }
        
        result = validator.validate_character_data(test_data)
        print(f"   Validation result: {result.valid}")
        
    except Exception as e:
        print(f"   ❌ CharacterValidator error: {e}")
    
    try:
        # Test formatting component
        print("\n3. Testing CharacterFormatter...")
        from formatting import CharacterFormatter, format_creation_result
        from character_creation import CreationResult
        
        formatter = CharacterFormatter()
        test_result = CreationResult(True, {"name": "Test", "level": 1})
        
        formatted = format_creation_result(test_result, "summary")
        print(f"   Formatting successful: {len(formatted) > 0}")
        
    except Exception as e:
        print(f"   ❌ CharacterFormatter error: {e}")

if __name__ == "__main__":
    print("Choose testing mode:")
    print("1. Full backend testing")
    print("2. Individual component testing")
    print("3. Both")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice in ["1", "3"]:
        test_backend_functionality()
    
    if choice in ["2", "3"]:
        test_individual_components()
