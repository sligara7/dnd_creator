#!/usr/bin/env python3
"""
LLM Service Diagnostic Test for D&D Character Creator
Tests the LLM service with Ollama to diagnose any issues
"""

import sys
import json
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

def test_raw_ollama_api():
    """Test the raw Ollama API directly."""
    print("=== Testing Raw Ollama API ===")
    
    try:
        import requests
        
        url = "http://localhost:11434/api/generate"
        data = {
            "model": "llama3",
            "prompt": "Create a simple JSON object with name and age",
            "stream": False
        }
        
        print(f"Making request to: {url}")
        print(f"Request data: {json.dumps(data, indent=2)}")
        
        response = requests.post(url, json=data, timeout=30)
        
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {result.get('response', 'No response field')}")
            print("✅ Raw Ollama API working!")
            return True
        else:
            print(f"❌ Raw API failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Raw API test failed: {e}")
        return False

def test_ollama_python_client():
    """Test the Ollama Python client."""
    print("\n=== Testing Ollama Python Client ===")
    
    try:
        import ollama
        
        print("Creating Ollama client...")
        client = ollama.Client(host='http://localhost:11434')
        
        print("Testing connection...")
        # Try to list models first
        models = client.list()
        print(f"Available models: {[m.get('name', m.get('model', 'unknown')) for m in models.get('models', [])]}")
        
        print("Making chat request...")
        response = client.chat(
            model='llama3',
            messages=[{
                'role': 'user',
                'content': 'Create a simple JSON object with name and age. Return only the JSON, no explanation.'
            }]
        )
        
        print(f"Response type: {type(response)}")
        print(f"Response keys: {list(response.keys()) if isinstance(response, dict) else 'Not a dict'}")
        
        if isinstance(response, dict) and 'message' in response:
            content = response['message']['content']
            print(f"Content: {content}")
            print("✅ Ollama Python client working!")
            return True
        else:
            print(f"❌ Unexpected response format: {response}")
            return False
            
    except Exception as e:
        print(f"❌ Ollama Python client test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_llm_service():
    """Test our LLM service implementation."""
    print("\n=== Testing Our LLM Service ===")
    
    try:
        from llm_services import create_llm_service
        
        print("Creating LLM service...")
        llm_service = create_llm_service(provider="auto")  # Will auto-detect OpenAI or Ollama
        
        if llm_service is None:
            print("❌ LLM service creation returned None")
            return False
        
        print(f"LLM service type: {type(llm_service)}")
        
        # Test connection
        print("Testing connection...")
        if hasattr(llm_service, 'test_connection'):
            connection_ok = llm_service.test_connection()
            print(f"Connection test: {'✅ OK' if connection_ok else '❌ Failed'}")
        
        # Test generation with shorter timeout for faster testing
        print("Testing text generation...")
        prompt = "Create a simple JSON object with name and age. Return only the JSON."
        result = llm_service.generate(prompt, timeout_seconds=60)  # Shorter timeout for testing
        
        print(f"Generation result: {result}")
        
        if result and len(result.strip()) > 0:
            print("✅ LLM service working!")
            return True
        else:
            print("❌ LLM service returned empty result")
            return False
            
    except Exception as e:
        print(f"❌ LLM service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_character_creation():
    """Test character creation with the LLM service."""
    print("\n=== Testing Character Creation ===")
    
    try:
        from character_creation import CharacterCreator, CreationConfig
        from llm_services import create_llm_service
        
        print("Creating services...")
        llm_service = create_llm_service(provider="auto")  # Auto-detect OpenAI or Ollama
        config = CreationConfig()
        config.base_timeout = 120  # Reasonable timeout for testing
        
        creator = CharacterCreator(llm_service, config)
        
        print("Creating character...")
        result = creator.create_character(
            description="A brave human fighter",
            level=1,
            generate_backstory=False,  # Disable backstory for faster testing
            include_custom_content=False
        )
        
        print(f"Creation result: {result.success}")
        if result.success:
            print(f"Character name: {result.data.get('name', 'No name')}")
            print(f"Character class: {result.data.get('classes', 'No classes')}")
            print("✅ Character creation working!")
            return True
        else:
            print(f"❌ Character creation failed: {result.error}")
            return False
            
    except Exception as e:
        print(f"❌ Character creation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all diagnostic tests."""
    print("D&D Character Creator - LLM Diagnostic Tests")
    print("=" * 50)
    
    tests = [
        ("Raw Ollama API", test_raw_ollama_api),
        ("Ollama Python Client", test_ollama_python_client),
        ("LLM Service", test_llm_service),
        ("Character Creation", test_character_creation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("DIAGNOSTIC SUMMARY")
    print("="*60)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:30} {status}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your backend is ready for testing.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()
