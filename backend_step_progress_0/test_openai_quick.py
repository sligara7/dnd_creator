#!/usr/bin/env python3
"""
Quick OpenAI test to verify API key and model work
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

def test_openai_direct():
    """Test OpenAI directly with the API key."""
    print("=== Testing OpenAI Integration ===")
    
    try:
        from llm_services import create_llm_service
        
        # Force OpenAI
        print("Creating OpenAI service...")
        llm_service = create_llm_service(provider="openai")
        
        print(f"Service type: {type(llm_service)}")
        
        # Test connection
        print("Testing connection...")
        if llm_service.test_connection():
            print("✅ OpenAI connection successful")
        else:
            print("❌ OpenAI connection failed")
            return False
        
        # Test generation
        print("Testing text generation...")
        result = llm_service.generate("Say hello and return a JSON object with 'message': 'hello'", timeout_seconds=30)
        
        print(f"Result: {result}")
        
        if result and len(result.strip()) > 0:
            print("✅ OpenAI generation working!")
            return True
        else:
            print("❌ OpenAI generation failed")
            return False
            
    except Exception as e:
        print(f"❌ OpenAI test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_openai_direct()
