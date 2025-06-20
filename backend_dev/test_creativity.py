#!/usr/bin/env python3
"""
Creative D&D Character Creation Stress Test
Tests the system's ability to generate completely custom content that pushes creativity to the max.
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

def test_ultra_creative_character():
    """Test creating a character with maximum creativity - custom everything."""
    print("=== ULTRA-CREATIVE CHARACTER CREATION STRESS TEST ===\n")
    
    try:
        from character_creation import CharacterCreator, CreationConfig
        from llm_services import create_llm_service
        
        print("🎨 Creating services for maximum creativity test...")
        llm_service = create_llm_service(provider="auto")
        
        # Configure for maximum creativity
        config = CreationConfig()
        config.base_timeout = 180  # 3 minutes for complex generation
        config.enable_progress_feedback = True
        
        creator = CharacterCreator(llm_service, config)
        
        # Ultra-creative character description that requires inventing everything
        creative_description = """
        Create a sentient crystalline entity from the Plane of Mirrors who has learned to shapeshift 
        into organic forms. They practice a unique form of magic called "Reflection Weaving" that 
        manipulates light, shadows, and reflections. 
        
        REQUIREMENTS - INVENT ALL OF THESE:
        - Custom Species: "Mirrorbeing" with unique racial traits
        - Custom Class: "Reflection Weaver" with custom abilities
        - Custom Background: "Dimensional Refugee" 
        - Custom Feat: "Prismatic Soul" (enhances reflection magic)
        - Custom Armor: "Crystalline Carapace" (made from their own essence)
        - Custom Weapon: "Shard of Infinite Reflections" (melee/ranged weapon)
        - Custom Spell: "Mirror Maze" (creates illusions and teleportation)
        
        Make this character Level 5 to showcase more abilities.
        Be creative with ability scores - maybe Constitution is called "Cohesion" 
        and Charisma is "Luminosity" for this species.
        """
        
        print("🌟 Creating ultra-creative character...")
        print("📝 Request: Sentient crystalline Mirrorbeing Reflection Weaver")
        print("🎯 Challenge: Invent new species, class, feat, armor, weapon, and spell")
        print("⏱️  Timeout: 3 minutes for complex generation")
        print("\n" + "="*60)
        
        result = creator.create_character(
            description=creative_description,
            level=5,  # Higher level to show more abilities
            generate_backstory=True,  # Include backstory for full creativity
            include_custom_content=True  # Enable all custom content
        )
        
        print("="*60)
        
        if result.success:
            print("🎉 ULTRA-CREATIVE CHARACTER GENERATION SUCCESSFUL!")
            print(f"⏱️  Generation time: {result.creation_time:.2f} seconds")
            
            character = result.data
            
            # Display the creative elements
            print("\n🎨 CREATIVE ELEMENTS GENERATED:")
            print("="*50)
            
            # Species
            species = character.get('species', 'Unknown')
            print(f"🧬 Species: {species}")
            
            # Class
            classes = character.get('classes', {})
            for class_name, level in classes.items():
                print(f"⚔️  Class: {class_name} (Level {level})")
            
            # Background
            background = character.get('background', 'Unknown')
            print(f"📚 Background: {background}")
            
            # Feats
            feats = character.get('feats', [])
            if feats:
                print("🌟 Custom Feats:")
                for feat in feats:
                    print(f"   • {feat}")
            
            # Equipment
            equipment = character.get('equipment', {})
            
            # Armor
            armor = equipment.get('armor', [])
            if armor:
                print("🛡️  Custom Armor:")
                for item in armor:
                    print(f"   • {item}")
            
            # Weapons
            weapons = equipment.get('weapons', [])
            if weapons:
                print("⚔️  Custom Weapons:")
                for weapon in weapons:
                    print(f"   • {weapon}")
            
            # Spells
            spells = character.get('spells', {})
            if spells:
                print("✨ Custom Spells:")
                for level, spell_list in spells.items():
                    if spell_list:
                        print(f"   Level {level}: {', '.join(spell_list)}")
            
            # Racial traits
            racial_traits = character.get('racial_traits', [])
            if racial_traits:
                print("🧬 Custom Racial Traits:")
                for trait in racial_traits:
                    print(f"   • {trait}")
            
            # Backstory snippet
            backstory = character.get('backstory', '')
            if backstory:
                print(f"\n📖 Backstory Preview:")
                preview = backstory[:200] + "..." if len(backstory) > 200 else backstory
                print(f"   {preview}")
            
            print("\n" + "="*60)
            print("✅ CREATIVITY STRESS TEST: PASSED")
            print("🎨 The AI successfully invented custom D&D content!")
            
            return True
            
        else:
            print("❌ ULTRA-CREATIVE CHARACTER GENERATION FAILED")
            print(f"Error: {result.error}")
            
            if result.error and "timeout" in result.error.lower():
                print("\n💡 TIMEOUT SUGGESTIONS:")
                print("- Increase config.base_timeout to 300+ seconds")
                print("- Break complex requests into smaller parts")
                print("- Use OpenAI (faster than Ollama for complex requests)")
            
            return False
            
    except Exception as e:
        print(f"❌ Creativity stress test crashed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multiple_creative_concepts():
    """Test multiple creative concepts in sequence."""
    print("\n=== MULTIPLE CREATIVE CONCEPTS TEST ===\n")
    
    creative_concepts = [
        {
            "name": "Quantum Mage",
            "description": "A scientist-wizard who manipulates probability and quantum mechanics through spellcasting. Create a custom 'Quantum Manipulation' class with probability-based spells.",
            "level": 3
        },
        {
            "name": "Dream Architect",
            "description": "A being from the Realm of Sleep who builds physical structures from crystallized dreams. Invent a 'Oneirokinetic' species and 'Dream Shaper' class.",
            "level": 4
        },
        {
            "name": "Symbiotic Warrior",
            "description": "A character bonded with an alien symbiotic organism that forms weapons and armor. Create custom equipment that's actually a living creature.",
            "level": 6
        }
    ]
    
    try:
        from character_creation import CharacterCreator, CreationConfig
        from llm_services import create_llm_service
        
        llm_service = create_llm_service(provider="auto")
        config = CreationConfig()
        config.base_timeout = 120
        
        creator = CharacterCreator(llm_service, config)
        
        successes = 0
        
        for i, concept in enumerate(creative_concepts, 1):
            print(f"🎨 Creative Concept {i}: {concept['name']}")
            print(f"📝 Description: {concept['description']}")
            
            result = creator.create_character(
                description=concept['description'],
                level=concept['level'],
                generate_backstory=False,  # Skip backstory for faster testing
                include_custom_content=True
            )
            
            if result.success:
                print(f"✅ {concept['name']}: SUCCESS")
                character_name = result.data.get('name', 'Unnamed')
                character_class = list(result.data.get('classes', {}).keys())[0] if result.data.get('classes') else 'Unknown'
                print(f"   Generated: {character_name} the {character_class}")
                successes += 1
            else:
                print(f"❌ {concept['name']}: FAILED - {result.error}")
            
            print("-" * 50)
        
        print(f"\n🎯 Multiple Concepts Result: {successes}/{len(creative_concepts)} successful")
        return successes == len(creative_concepts)
        
    except Exception as e:
        print(f"❌ Multiple concepts test failed: {e}")
        return False

def main():
    """Run all creativity stress tests."""
    print("D&D CHARACTER CREATOR - CREATIVITY STRESS TESTS")
    print("=" * 60)
    print("🎨 Testing maximum creativity and custom content generation")
    print("🚀 This will push the AI to its creative limits!")
    print("=" * 60)
    
    tests = [
        ("Ultra-Creative Character", test_ultra_creative_character),
        ("Multiple Creative Concepts", test_multiple_creative_concepts)
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
    
    # Final summary
    print("\n" + "="*70)
    print("CREATIVITY STRESS TEST SUMMARY")
    print("="*70)
    
    for test_name, success in results:
        status = "🎨 CREATIVE SUCCESS" if success else "❌ NEEDS WORK"
        print(f"{test_name:35} {status}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    if passed == total:
        print(f"\n🎉 ALL CREATIVITY TESTS PASSED!")
        print("🎨 Your D&D Character Creator is ready for maximum creativity!")
        print("🌟 It can invent custom species, classes, spells, and equipment!")
    else:
        print(f"\n⚠️  {passed}/{total} creativity tests passed.")
        print("💡 Consider tuning prompts or timeouts for better creative results.")

if __name__ == "__main__":
    main()
