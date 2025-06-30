#!/usr/bin/env python3
"""
Test script to debug character creation workflow
"""

import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, '/home/ajs7/dnd_tools/dnd_char_creator/backend')

from character_creation import CharacterCreator
from llm_service import create_llm_service

async def test_basic_creation():
    """Test basic character creation without complex LLM calls."""
    print("Testing basic character creation...")
    
    try:
        # Create a simple LLM service
        llm_service = create_llm_service("ollama", model="tinyllama:latest", timeout=30)
        print("LLM service created")
        
        # Create character creator
        creator = CharacterCreator(llm_service)
        print("Character creator initialized")
        
        # Simple prompt
        prompt = "A human fighter"
        
        print(f"Creating character with prompt: {prompt}")
        result = await creator.create_character(prompt)
        
        if result.success:
            print("Character creation successful!")
            print(f"Character data keys: {list(result.data.keys()) if result.data else 'None'}")
            return True
        else:
            print(f"Character creation failed: {result.error}")
            print(f"Warnings: {result.warnings}")
            return False
            
    except Exception as e:
        print(f"Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_basic_creation())
