#!/usr/bin/env python3
"""
Simple Backend Test - Basic functionality check

This is a simplified version to test core functionality without complex imports.
"""

import sys
import tempfile
import os
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def test_imports():
    """Test that all modules can be imported."""
    print("🔍 Testing module imports...")
    
    try:
        from config_new import settings
        print("✅ Config imported successfully")
    except Exception as e:
        print(f"❌ Config import failed: {e}")
        return False
        
    try:
        from database_models_new import Base, CharacterRepository
        print("✅ Database models imported successfully")
    except Exception as e:
        print(f"❌ Database models import failed: {e}")
        return False
        
    try:
        from character_models import CharacterCore
        print("✅ Character models imported successfully")
    except Exception as e:
        print(f"❌ Character models import failed: {e}")
        return False
        
    try:
        from llm_service_new import create_llm_service
        print("✅ LLM service imported successfully")
    except Exception as e:
        print(f"❌ LLM service import failed: {e}")
        return False
        
    try:
        from fastapi_main_new import app
        print("✅ FastAPI app imported successfully")
        return True
    except Exception as e:
        print(f"❌ FastAPI app import failed: {e}")
        return False
        
    return True

def test_character_model():
    """Test basic character model functionality."""
    print("\n🎲 Testing character model...")
    
    try:
        from character_models import CharacterCore
        
        # Create a simple character
        character = CharacterCore(name="Test Hero")
        character.species = "Human"
        
        print(f"✅ Created character: {character.name}")
        
        # Test ability scores
        character.set_ability_score("strength", 15)
        str_score = character.get_ability_score("strength")
        print(f"✅ Set strength score object")
        
        # Test ability modifiers
        modifiers = character.get_ability_modifiers()
        str_mod = modifiers.get("strength", 0)
        print(f"✅ Strength modifier: +{str_mod}")
        
        return True
        
    except Exception as e:
        print(f"❌ Character model test failed: {e}")
        return False

def test_database_models():
    """Test database model creation."""
    print("\n🗃️ Testing database models...")
    
    try:
        from database_models_new import CharacterRepository, Base
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        # Create temporary in-memory database
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=engine)
        
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = SessionLocal()
        
        # Create a repository
        repo = CharacterRepository(
            name="Test Repository",
            description="Simple test repository",
            player_name="Test Player"
        )
        
        session.add(repo)
        session.commit()
        
        print(f"✅ Created repository: {repo.name} (ID: {repo.id})")
        
        session.close()
        return True
        
    except Exception as e:
        print(f"❌ Database models test failed: {e}")
        return False

def test_llm_service():
    """Test LLM service creation."""
    print("\n🤖 Testing LLM service...")
    
    try:
        from llm_service_new import create_llm_service, create_ollama_service
        
        # Test default service creation
        service = create_llm_service()
        print(f"✅ Created LLM service: {type(service).__name__}")
        
        # Test Ollama service creation
        ollama_service = create_ollama_service()
        print(f"✅ Created Ollama service: {type(ollama_service).__name__}")
        
        return True
        
    except Exception as e:
        print(f"❌ LLM service test failed: {e}")
        return False

def main():
    """Run simple backend tests."""
    print("🧪 D&D Character Creator - Simple Backend Test")
    print("=" * 50)
    
    tests = [
        ("Module Imports", test_imports),
        ("Character Model", test_character_model),
        ("Database Models", test_database_models),
        ("LLM Service", test_llm_service)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔬 Running {test_name} test...")
        if test_func():
            passed += 1
            
    print(f"\n{'='*50}")
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Backend is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
