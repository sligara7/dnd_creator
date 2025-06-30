#!/usr/bin/env python3
"""
Test script for the refactored LLM service with Ollama default.
This script tests both Ollama (local) and OpenAI (if configured) services.
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from llm_service_new import create_llm_service, create_ollama_service

async def test_ollama_service():
    """Test Ollama service (default)."""
    print("🦙 Testing Ollama LLM Service")
    print("=" * 50)
    
    try:
        # Create Ollama service (default)
        llm_service = create_llm_service()  # Defaults to Ollama
        
        # Test connection
        print("Testing connection to Ollama...")
        is_available = await llm_service.test_connection()
        
        if not is_available:
            print("❌ Ollama not available. Please ensure:")
            print("1. Ollama is installed: https://ollama.ai/")
            print("2. Ollama is running: ollama serve")
            print("3. Llama3 model is pulled: ollama pull llama3")
            return False
        
        print("✅ Ollama connection successful!")
        
        # Test content generation
        print("\nTesting content generation...")
        prompt = "Create a brief D&D character description for a level 1 human fighter named Marcus."
        
        print(f"Prompt: {prompt}")
        print("\nGenerating response...")
        
        response = await llm_service.generate_content(prompt, temperature=0.7, max_tokens=150)
        
        print(f"✅ Response generated ({len(response)} characters):")
        print("-" * 30)
        print(response)
        print("-" * 30)
        
        # Check rate limit status
        status = llm_service.get_rate_limit_status()
        print(f"\n📊 Status: {status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ollama test failed: {str(e)}")
        return False

async def test_openai_service():
    """Test OpenAI service (if configured)."""
    print("\n🤖 Testing OpenAI LLM Service")
    print("=" * 50)
    
    try:
        # Check if API key is available
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("⚠️  OpenAI API key not found in environment.")
            print("   To test OpenAI, create .env file with OPENAI_API_KEY=your_key")
            return False
        
        # Create OpenAI service
        llm_service = create_llm_service("openai")
        
        # Test connection
        print("Testing connection to OpenAI...")
        is_available = await llm_service.test_connection()
        
        if not is_available:
            print("❌ OpenAI not available. Check your API key.")
            return False
        
        print("✅ OpenAI connection successful!")
        
        # Test content generation (shorter prompt to save tokens)
        print("\nTesting content generation...")
        prompt = "Create a brief D&D character name and class."
        
        print(f"Prompt: {prompt}")
        print("\nGenerating response...")
        
        response = await llm_service.generate_content(prompt, temperature=0.7, max_tokens=50)
        
        print(f"✅ Response generated ({len(response)} characters):")
        print("-" * 30)
        print(response)
        print("-" * 30)
        
        # Check rate limit status
        status = llm_service.get_rate_limit_status()
        print(f"\n📊 Status: Requests this minute: {status.get('requests_per_minute', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ OpenAI test failed: {str(e)}")
        return False

async def test_service_switching():
    """Test switching between services."""
    print("\n🔄 Testing Service Switching")
    print("=" * 50)
    
    try:
        # Test default (Ollama)
        default_service = create_llm_service()
        print(f"Default service: {type(default_service).__name__}")
        
        # Test explicit Ollama
        ollama_service = create_llm_service("ollama")
        print(f"Explicit Ollama: {type(ollama_service).__name__}")
        
        # Test convenience function
        convenience_service = create_ollama_service(model="llama3")
        print(f"Convenience function: {type(convenience_service).__name__}")
        
        # Test different models
        if await default_service.test_connection():
            print("✅ Can create and switch between different LLM services")
            return True
        else:
            print("⚠️  Ollama not available for switching test")
            return False
            
    except Exception as e:
        print(f"❌ Service switching test failed: {str(e)}")
        return False

async def main():
    """Run all tests."""
    print("🧪 LLM Service Test Suite")
    print("=" * 60)
    
    results = []
    
    # Test Ollama (primary)
    ollama_result = await test_ollama_service()
    results.append(("Ollama", ollama_result))
    
    # Test OpenAI (if available)
    openai_result = await test_openai_service()
    results.append(("OpenAI", openai_result))
    
    # Test service switching
    switching_result = await test_service_switching()
    results.append(("Service Switching", switching_result))
    
    # Summary
    print("\n📋 Test Results Summary")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} | {status}")
    
    # Overall result
    passed_tests = sum(1 for _, result in results if result)
    total_tests = len(results)
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if ollama_result:
        print("\n🎉 Ollama is working! You can now use the LLM service for D&D character creation.")
        print("   Usage: llm_service = create_llm_service()  # Defaults to Ollama")
    else:
        print("\n⚠️  Ollama setup needed. Follow the instructions above.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n🛑 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {str(e)}")
        sys.exit(1)
