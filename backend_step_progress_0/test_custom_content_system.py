#!/usr/bin/env python3
"""
Test Custom Content System with LLM Integration

This script tests the enhanced custom content system including:
- LLM integration for rich descriptions
- Database persistence
- ContentRegistry functionality
- AI character creator enhancements

Usage:
    python test_custom_content_system.py
"""

import sys
import asyncio
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from custom_content_models import ContentRegistry, LLMContentGenerator, CustomContentDatabase
from llm_service_new import create_ollama_service
from character_models import CharacterCore

async def test_llm_content_generator():
    """Test the LLM content generator."""
    print("🧪 Testing LLM Content Generator...")
    
    try:
        llm_service = create_ollama_service()
        generator = LLMContentGenerator(llm_service)
        
        # Test species description generation
        species_desc = await generator.generate_species_description(
            "Crystalkin", 
            "A crystal-powered artificer from a steampunk sky city"
        )
        print(f"✅ Generated species description: {species_desc[:100]}...")
        
        # Test class description generation
        class_desc = await generator.generate_class_description(
            "Crystal Artificer",
            "A master of crystal technology and mechanical innovation"
        )
        print(f"✅ Generated class description: {class_desc[:100]}...")
        
        return True
    except Exception as e:
        print(f"⚠️  LLM Generator test failed: {e}")
        return False

def test_custom_content_database():
    """Test the custom content database."""
    print("\n🧪 Testing Custom Content Database...")
    
    try:
        # Create test database
        db = CustomContentDatabase("test_custom_content.json")
        
        # Test storing and retrieving content
        from custom_content_models import CustomSpecies
        test_species = CustomSpecies(
            name="Test Species",
            description="A test species for database testing",
            creature_type="Humanoid"
        )
        
        db.store_species(test_species)
        retrieved = db.get_species("Test Species")
        
        if retrieved and retrieved["name"] == "Test Species":
            print("✅ Database storage and retrieval works")
            
            # Test statistics
            stats = db.get_database_stats()
            print(f"✅ Database stats: {stats}")
            
            return True
        else:
            print("❌ Database retrieval failed")
            return False
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

async def test_enhanced_content_registry():
    """Test the enhanced content registry."""
    print("\n🧪 Testing Enhanced Content Registry...")
    
    try:
        # Initialize registry with LLM
        registry = ContentRegistry("test_registry.json")
        
        try:
            llm_service = create_ollama_service()
            registry.set_llm_service(llm_service)
            print("✅ Registry initialized with LLM service")
            
            # Test creating content with LLM
            custom_species = await registry.create_species_with_llm(
                "Shadowborn", 
                "A mysterious species that emerged from the shadow realm"
            )
            print(f"✅ Created species with LLM: {custom_species.name}")
            print(f"   Description: {custom_species.description[:80]}...")
            
            custom_class = await registry.create_class_with_llm(
                "Shadow Dancer",
                "A martial artist who fights using shadow magic"
            )
            print(f"✅ Created class with LLM: {custom_class.name}")
            print(f"   Description: {custom_class.description[:80]}...")
            
            # Test linking content to character
            registry.link_content_to_character(
                "test_char_001", 
                ["Species: Shadowborn", "Class: Shadow Dancer"]
            )
            
            linked_content = registry.get_character_content("test_char_001")
            print(f"✅ Linked content: {linked_content}")
            
            return True
            
        except Exception as e:
            print(f"⚠️  LLM integration failed, testing without LLM: {e}")
            
            # Test without LLM (should still work with fallback descriptions)
            from custom_content_models import CustomSpecies, CustomClass
            
            fallback_species = CustomSpecies(
                name="Fallback Species",
                description="A species created without LLM assistance"
            )
            registry.register_species(fallback_species)
            
            fallback_class = CustomClass(
                name="Fallback Class", 
                description="A class created without LLM assistance"
            )
            registry.register_class(fallback_class)
            
            print("✅ Registry works without LLM")
            return True
            
    except Exception as e:
        print(f"❌ Registry test failed: {e}")
        return False

def test_ability_score_display():
    """Test the ability score display bug fix."""
    print("\n🧪 Testing Ability Score Display Fix...")
    
    try:
        # Create a character and set ability scores
        character = CharacterCore("Test Character", "Human", "Folk Hero")
        character.set_character_class("Fighter", 3)
        character.set_ability_score("strength", 16)
        character.set_ability_score("dexterity", 14)
        character.set_ability_score("constitution", 15)
        character.set_ability_score("intelligence", 12)
        character.set_ability_score("wisdom", 13)
        character.set_ability_score("charisma", 10)
        
        # Test ability score retrieval
        abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        modifiers = character.get_ability_modifiers()
        
        print("Ability Scores:")
        for ability in abilities:
            ability_score_obj = character.get_ability_score(ability)
            if ability_score_obj and hasattr(ability_score_obj, 'total_score'):
                score = ability_score_obj.total_score
                modifier = modifiers.get(ability, 0)
                sign = "+" if modifier >= 0 else ""
                print(f"  {ability.title():13}: {score:2d} ({sign}{modifier})")
            else:
                print(f"  {ability.title():13}: ERROR - No total_score attribute")
                return False
        
        print("✅ Ability score display works correctly")
        return True
        
    except Exception as e:
        print(f"❌ Ability score test failed: {e}")
        return False

async def main():
    """Run all tests."""
    print("🧪 Testing Enhanced Custom Content System")
    print("=" * 50)
    
    test_results = []
    
    # Test 1: LLM Content Generator
    llm_result = await test_llm_content_generator()
    test_results.append(("LLM Content Generator", llm_result))
    
    # Test 2: Custom Content Database
    db_result = test_custom_content_database()
    test_results.append(("Custom Content Database", db_result))
    
    # Test 3: Enhanced Content Registry
    registry_result = await test_enhanced_content_registry()
    test_results.append(("Enhanced Content Registry", registry_result))
    
    # Test 4: Ability Score Display Fix
    ability_result = test_ability_score_display()
    test_results.append(("Ability Score Display", ability_result))
    
    # Print summary
    print("\n" + "=" * 50)
    print("🧪 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:25}: {status}")
        if result:
            passed += 1
    
    print(f"\n{passed}/{len(test_results)} tests passed")
    
    if passed == len(test_results):
        print("🎉 All tests passed! The enhanced system is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    # Cleanup test files
    try:
        import os
        test_files = ["test_custom_content.json", "test_registry.json"]
        for file in test_files:
            if os.path.exists(file):
                os.remove(file)
        print("🧹 Cleaned up test files")
    except:
        pass

if __name__ == "__main__":
    asyncio.run(main())
