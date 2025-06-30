#!/usr/bin/env python3
"""
Test character creation with OpenAI
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

def test_character_creation_openai():
    """Test character creation with OpenAI."""
    print("=== Testing Character Creation with OpenAI ===")
    
    try:
        from character_creation import CharacterCreator, CreationConfig
        from llm_services import create_llm_service
        
        print("Creating OpenAI service...")
        llm_service = create_llm_service(provider="openai")
        
        print("Creating character creator...")
        config = CreationConfig()
        config.base_timeout = 60  # OpenAI is much faster than Ollama
        
        creator = CharacterCreator(llm_service, config)
        
        print("Creating character...")
        result = creator.create_character(
            description="A brave human fighter with a strong sense of justice",
            level=1,
            generate_backstory=False,  # Keep it simple for testing
            include_custom_content=False
        )
        
        print(f"Creation successful: {result.success}")
        if result.success:
            character = result.data
            print(f"Character name: {character.get('name', 'No name')}")
            print(f"Species: {character.get('species', 'No species')}")
            print(f"Classes: {character.get('classes', 'No classes')}")
            print(f"Level: {character.get('level', 'No level')}")
            print(f"Background: {character.get('background', 'No background')}")
            print(f"Creation time: {result.creation_time:.2f} seconds")
            print("✅ Character creation with OpenAI successful!")
            
            # Quick validation
            from validation import CharacterValidator
            validator = CharacterValidator()
            validation = validator.validate_character_data(character)
            print(f"Validation score: {validation.score:.2f}")
            print(f"Valid: {validation.valid}")
            
            return True
        else:
            print(f"❌ Character creation failed: {result.error}")
            return False
            
    except Exception as e:
        print(f"❌ Character creation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_character_creation_openai()
