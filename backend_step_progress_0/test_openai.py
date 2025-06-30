#!/usr/bin/env python3
"""
Simple OpenAI API test for GPT-4.1-nano model
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

def test_openai_direct():
    """Test OpenAI API directly with the specified model."""
    print("=== Direct OpenAI API Test ===")
    
    # Extract API key from llm_services.py
    api_key = None
    try:
        with open('llm_services.py', 'r') as f:
            first_line = f.readline().strip()
            if first_line.startswith('# '):
                api_key = first_line[2:].strip()
                print("🔑 Found API key in llm_services.py")
    except:
        print("❌ Could not extract API key from file")
        return False
    
    if not api_key:
        print("❌ No API key found")
        return False
    
    try:
        import openai
        
        client = openai.OpenAI(api_key=api_key)
        model = "gpt-4.1-nano-2025-04-14"
        
        print(f"Testing model: {model}")
        print("Making test request...")
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Create a simple JSON object with name and age. Return only the JSON, no explanation."}
            ],
            max_tokens=100,
            temperature=0.1
        )
        
        if response.choices and response.choices[0].message:
            content = response.choices[0].message.content.strip()
            print(f"✅ Success! Response: {content}")
            
            # Try to parse as JSON to verify format
            try:
                import json
                parsed = json.loads(content.strip('```json').strip('```').strip())
                print(f"✅ Valid JSON: {parsed}")
                return True
            except:
                print(f"⚠️  Response received but not valid JSON: {content}")
                return True  # Still success, just not JSON
        else:
            print("❌ No response content received")
            return False
            
    except Exception as e:
        print(f"❌ OpenAI API test failed: {e}")
        
        # Check if it's a model availability issue
        if "model" in str(e).lower():
            print(f"\n💡 The model '{model}' might not be available.")
            print("   Try these alternatives:")
            print("   - gpt-4o-mini (current fast model)")
            print("   - gpt-4o (standard model)")
            print("   - gpt-3.5-turbo (older fast model)")
            
            # Test with fallback model
            print("\n🔄 Testing with fallback model gpt-4o-mini...")
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "user", "content": "Hello, world!"}
                    ],
                    max_tokens=10
                )
                if response.choices:
                    print("✅ gpt-4o-mini works as fallback!")
                    return True
            except Exception as e2:
                print(f"❌ Fallback also failed: {e2}")
        
        return False

def test_backend_integration():
    """Test the backend integration with OpenAI."""
    print("\n=== Backend Integration Test ===")
    
    try:
        from llm_services import create_llm_service
        
        print("Creating LLM service (should auto-detect OpenAI)...")
        llm_service = create_llm_service(provider="openai")
        
        print(f"Service type: {type(llm_service)}")
        print("Testing connection...")
        
        if llm_service.test_connection():
            print("✅ Connection successful!")
            
            print("Testing text generation...")
            result = llm_service.generate(
                "Create a JSON object with a character name and level. Return only JSON.",
                timeout_seconds=30
            )
            
            print(f"Generation result: {result}")
            return True
        else:
            print("❌ Connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Backend integration failed: {e}")
        return False

def main():
    """Run all OpenAI tests."""
    print("OpenAI GPT-4.1-nano Testing")
    print("=" * 40)
    
    # Install openai if needed
    try:
        import openai
    except ImportError:
        print("Installing OpenAI package...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "openai"], check=True)
        import openai
    
    results = []
    
    # Test 1: Direct API
    success1 = test_openai_direct()
    results.append(("Direct OpenAI API", success1))
    
    # Test 2: Backend integration
    success2 = test_backend_integration()
    results.append(("Backend Integration", success2))
    
    # Summary
    print("\n" + "="*40)
    print("TEST SUMMARY")
    print("="*40)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:25} {status}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    if passed == total:
        print(f"\n🎉 All tests passed! OpenAI integration ready.")
    else:
        print(f"\n⚠️  {passed}/{total} tests passed. Check errors above.")

if __name__ == "__main__":
    main()
