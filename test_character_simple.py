#!/usr/bin/env python3
"""
Simple test script for character creation API
"""

import requests
import json
import time

def test_character_creation():
    """Test character creation with a simple concept."""
    url = "http://localhost:8000/api/v1/characters"
    
    payload = {
        "name": "Test Wizard",
        "species": "Human", 
        "character_class": "Wizard",
        "level": 1,
        "background": "Scholar",
        "concept": "A young wizard studying arcane magic"
    }
    
    print("Testing character creation...")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        start_time = time.time()
        response = requests.post(url, json=payload, timeout=60)
        end_time = time.time()
        
        print(f"Request completed in {end_time - start_time:.2f} seconds")
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Character creation successful!")
            print(f"Character ID: {result.get('id', 'N/A')}")
            print(f"Character Name: {result.get('name', 'N/A')}")
            return True
        else:
            print(f"Character creation failed:")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("Request timed out after 60 seconds")
        return False
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return False

if __name__ == "__main__":
    test_character_creation()
