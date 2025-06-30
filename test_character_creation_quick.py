#!/usr/bin/env python3
"""
Quick test script for character creation API
"""
import asyncio
import aiohttp
import json

async def test_character_creation():
    """Test the character creation endpoint with a simple character."""
    
    character_data = {
        "name": "Test Fighter",
        "species": "Human", 
        "character_class": "Fighter",
        "level": 1,
        "background": "Soldier",
        "concept": "A simple human fighter with military training"
    }
    
    print("Testing character creation...")
    print(f"Request data: {json.dumps(character_data, indent=2)}")
    
    try:
        timeout = aiohttp.ClientTimeout(total=120)  # 2 minute timeout
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                "http://localhost:8000/api/v1/characters",
                json=character_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                print(f"Response status: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    print("SUCCESS! Character created:")
                    print(f"Character ID: {result.get('character_id', 'Unknown')}")
                    print(f"Name: {result.get('name', 'Unknown')}")
                    print(f"Species: {result.get('species', 'Unknown')}")
                    print(f"Class: {result.get('character_class', 'Unknown')}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"ERROR: {response.status}")
                    print(f"Response: {error_text}")
                    return False
                    
    except asyncio.TimeoutError:
        print("ERROR: Request timed out")
        return False
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_character_creation())
    if success:
        print("\n✅ Character creation test PASSED")
    else:
        print("\n❌ Character creation test FAILED")
