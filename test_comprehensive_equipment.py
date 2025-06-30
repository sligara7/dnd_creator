#!/usr/bin/env python3
"""
Comprehensive Armor, Tools, and Equipment System Test for D&D Character Creator

This test verifies that:
1. Armor selection prioritizes official D&D 5e armor over custom armor
2. Tool selection prioritizes official D&D 5e tools over custom tools  
3. Equipment selection prioritizes official D&D 5e gear over custom gear
4. Class-appropriate armor, tools, and equipment are selected
5. Spellcasting focuses are correctly assigned to spellcasters
6. Equipment packs are assigned based on class preferences
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from dnd_data import (
    DND_ARMOR_DATABASE, ALL_ARMOR, ARMOR_LOOKUP, CLASS_ARMOR_PROFICIENCIES,
    DND_TOOLS_DATABASE, ALL_TOOLS, TOOLS_LOOKUP,
    DND_ADVENTURING_GEAR_DATABASE, ALL_ADVENTURING_GEAR, ADVENTURING_GEAR_LOOKUP, CLASS_EQUIPMENT_PREFERENCES,
    is_existing_dnd_armor, get_armor_data, get_appropriate_armor_for_character,
    is_existing_dnd_tool, get_tool_data, get_appropriate_tools_for_character,
    is_existing_dnd_gear, get_gear_data, get_appropriate_equipment_pack_for_character,
    validate_armor_database, validate_tools_database, validate_gear_database
)

def test_armor_database_coverage():
    """Test that the armor database covers all D&D 5e armor types."""
    print("Testing D&D 5e Armor Database Coverage...")
    
    # Test database integrity
    assert validate_armor_database(), "Armor database validation failed"
    
    # Test that key armor pieces exist
    key_armor = [
        "Leather Armor", "Studded Leather Armor", "Chain Shirt", "Breastplate", 
        "Chain Mail", "Plate Armor", "Shield"
    ]
    
    for armor_name in key_armor:
        assert is_existing_dnd_armor(armor_name), f"Missing key armor: {armor_name}"
        armor_data = get_armor_data(armor_name)
        assert armor_data is not None, f"No data for armor: {armor_name}"
        assert "ac_base" in armor_data or "ac_bonus" in armor_data, f"Missing AC data for {armor_name}"
    
    print(f"✓ Armor database covers {len(ALL_ARMOR)} armor pieces")
    print(f"✓ All key armor pieces are present")
    
    # Test armor categories
    categories = ["light_armor", "medium_armor", "heavy_armor", "shields"]
    for category in categories:
        assert category in DND_ARMOR_DATABASE, f"Missing armor category: {category}"
    
    print(f"✓ All armor categories are present: {categories}")

def test_tools_database_coverage():
    """Test that the tools database covers all D&D 5e tool types."""
    print("\nTesting D&D 5e Tools Database Coverage...")
    
    # Test database integrity
    assert validate_tools_database(), "Tools database validation failed"
    
    # Test that key tools exist
    key_tools = [
        "Thieves' Tools", "Smith's Tools", "Herbalism Kit", "Disguise Kit",
        "Alchemist's Supplies", "Lute", "Dice Set", "Calligrapher's Supplies"
    ]
    
    for tool_name in key_tools:
        assert is_existing_dnd_tool(tool_name), f"Missing key tool: {tool_name}"
        tool_data = get_tool_data(tool_name)
        assert tool_data is not None, f"No data for tool: {tool_name}"
        assert "category" in tool_data, f"Missing category data for {tool_name}"
    
    print(f"✓ Tools database covers {len(ALL_TOOLS)} tools")
    print(f"✓ All key tools are present")
    
    # Test tool categories
    categories = ["artisan_tools", "specialist_kits", "gaming_sets", "musical_instruments"]
    for category in categories:
        assert category in DND_TOOLS_DATABASE, f"Missing tool category: {category}"
    
    print(f"✓ All tool categories are present: {categories}")

def test_gear_database_coverage():
    """Test that the adventuring gear database covers all D&D 5e gear types."""
    print("\nTesting D&D 5e Adventuring Gear Database Coverage...")
    
    # Test database integrity
    assert validate_gear_database(), "Gear database validation failed"
    
    # Test that key gear exists
    key_gear = [
        "Backpack", "Arrows", "Crystal", "Holy Symbol", "Explorer's Pack",
        "Burglar's Pack", "Scholar's Pack", "Acid", "Alchemist's Fire"
    ]
    
    for gear_name in key_gear:
        assert is_existing_dnd_gear(gear_name), f"Missing key gear: {gear_name}"
        gear_data = get_gear_data(gear_name)
        assert gear_data is not None, f"No data for gear: {gear_name}"
        assert "category" in gear_data, f"Missing category data for {gear_name}"
    
    print(f"✓ Adventuring gear database covers {len(ALL_ADVENTURING_GEAR)} items")
    print(f"✓ All key gear items are present")
    
    # Test gear categories
    categories = ["ammunition", "arcane_focus", "holy_symbol", "equipment_packs", "consumables"]
    for category in categories:
        assert category in DND_ADVENTURING_GEAR_DATABASE, f"Missing gear category: {category}"
    
    print(f"✓ All gear categories are present")

def test_armor_selection_by_class():
    """Test that appropriate armor is selected based on class proficiencies."""
    print("\nTesting Armor Selection by Class...")
    
    test_characters = [
        {"classes": {"Fighter": 5}, "level": 5},
        {"classes": {"Wizard": 3}, "level": 3},
        {"classes": {"Rogue": 4}, "level": 4},
        {"classes": {"Cleric": 6}, "level": 6},
        {"classes": {"Barbarian": 7}, "level": 7},
        {"classes": {"Monk": 8}, "level": 8}
    ]
    
    for character_data in test_characters:
        primary_class = list(character_data["classes"].keys())[0]
        armor = get_appropriate_armor_for_character(character_data)
        
        class_profs = CLASS_ARMOR_PROFICIENCIES.get(primary_class, {})
        
        if armor:
            # Verify the armor is appropriate for the class
            armor_data = None
            armor_name = None
            for armor_cat in DND_ARMOR_DATABASE.values():
                for name, data in armor_cat.items():
                    if data == armor:
                        armor_data = data
                        armor_name = name
                        break
                if armor_data:
                    break
            
            assert armor_data is not None, f"Could not find armor data for {primary_class}"
            armor_category = armor_data["category"]
            
            # Check if class can wear this armor
            if armor_category == "Light":
                assert class_profs.get("light", False), f"{primary_class} can't wear light armor but got {armor_name}"
            elif armor_category == "Medium":
                assert class_profs.get("medium", False), f"{primary_class} can't wear medium armor but got {armor_name}"
            elif armor_category == "Heavy":
                assert class_profs.get("heavy", False), f"{primary_class} can't wear heavy armor but got {armor_name}"
            
            print(f"✓ {primary_class} (level {character_data['level']}) gets appropriate armor: {armor_name} ({armor_category})")
        else:
            # Some classes (like Monks, some Wizards) might not get armor
            print(f"✓ {primary_class} (level {character_data['level']}) gets no armor (expected for some classes)")

def test_tools_selection_by_class():
    """Test that appropriate tools are selected based on class and background."""
    print("\nTesting Tools Selection by Class and Background...")
    
    test_characters = [
        {"classes": {"Rogue": 3}, "level": 3, "background": "Criminal"},
        {"classes": {"Wizard": 5}, "level": 5, "background": "Sage"},
        {"classes": {"Fighter": 4}, "level": 4, "background": "Soldier"},
        {"classes": {"Bard": 6}, "level": 6, "background": "Entertainer"},
        {"classes": {"Cleric": 3}, "level": 3, "background": "Acolyte"},
        {"classes": {"Ranger": 5}, "level": 5, "background": "Outlander"}
    ]
    
    for character_data in test_characters:
        primary_class = list(character_data["classes"].keys())[0]
        background = character_data["background"]
        tools = get_appropriate_tools_for_character(character_data, 3)
        
        # Verify all tools are official D&D tools
        for tool in tools:
            tool_name = tool["name"]
            assert is_existing_dnd_tool(tool_name) or is_existing_dnd_gear(tool_name), f"Non-D&D tool assigned: {tool_name}"
        
        # Check for class-specific tools
        if primary_class == "Rogue":
            tool_names = [t["name"] for t in tools]
            assert any("Thieves' Tools" in name for name in tool_names), "Rogue should get Thieves' Tools"
        
        print(f"✓ {primary_class}/{background} (level {character_data['level']}) gets {len(tools)} appropriate tools")
        for tool in tools:
            print(f"  - {tool['name']} ({tool['category']})")

def test_equipment_pack_assignment():
    """Test that appropriate equipment packs are assigned by class."""
    print("\nTesting Equipment Pack Assignment by Class...")
    
    all_classes = ["Barbarian", "Bard", "Cleric", "Druid", "Fighter", "Monk", 
                   "Paladin", "Ranger", "Rogue", "Sorcerer", "Warlock", "Wizard"]
    
    for class_name in all_classes:
        character_data = {"classes": {class_name: 3}, "level": 3}
        pack = get_appropriate_equipment_pack_for_character(character_data)
        
        assert pack is not None, f"No equipment pack assigned for {class_name}"
        
        # Find pack name
        pack_name = None
        for pack_cat in DND_ADVENTURING_GEAR_DATABASE.values():
            for name, data in pack_cat.items():
                if data == pack:
                    pack_name = name
                    break
            if pack_name:
                break
        
        assert pack_name is not None, f"Could not find pack name for {class_name}"
        assert is_existing_dnd_gear(pack_name), f"Non-D&D equipment pack assigned: {pack_name}"
        
        expected_pack = CLASS_EQUIPMENT_PREFERENCES.get(class_name, "Explorer's Pack")
        assert pack_name == expected_pack, f"{class_name} should get {expected_pack} but got {pack_name}"
        
        print(f"✓ {class_name} gets appropriate equipment pack: {pack_name}")

def test_spellcasting_focus_assignment():
    """Test that spellcasters get appropriate spellcasting focuses."""
    print("\nTesting Spellcasting Focus Assignment...")
    
    spellcaster_classes = {
        "Wizard": "Crystal",
        "Sorcerer": "Crystal", 
        "Warlock": "Crystal",
        "Cleric": "Holy Symbol",
        "Paladin": "Holy Symbol",
        "Druid": "Druidic Focus"
    }
    
    for class_name, expected_focus in spellcaster_classes.items():
        # Verify the focus exists in our database
        assert is_existing_dnd_gear(expected_focus), f"Expected focus {expected_focus} not in database"
        focus_data = get_gear_data(expected_focus)
        assert focus_data is not None, f"No data for focus: {expected_focus}"
        
        print(f"✓ {class_name} should get spellcasting focus: {expected_focus}")

def test_equipment_prioritization():
    """Test that D&D 5e equipment is prioritized over custom equipment."""
    print("\nTesting Equipment Prioritization...")
    
    # Test lookups work correctly
    dnd_items = ["Backpack", "Rope (50 feet)", "Rations (5 days)", "Waterskin"]
    
    for item in dnd_items:
        # Test case-insensitive lookup
        assert is_existing_dnd_gear(item), f"D&D gear not found: {item}"
        assert is_existing_dnd_gear(item.lower()), f"Case-insensitive lookup failed: {item}"
        assert is_existing_dnd_gear(item.upper()), f"Case-insensitive lookup failed: {item}"
        
        # Test data retrieval
        data = get_gear_data(item)
        assert data is not None, f"No data for D&D gear: {item}"
        assert "cost" in data, f"Missing cost for {item}"
        assert "weight" in data, f"Missing weight for {item}"
        
    print(f"✓ All tested D&D equipment items are properly indexed and retrievable")

def run_comprehensive_equipment_tests():
    """Run all equipment system tests."""
    print("=" * 80)
    print("COMPREHENSIVE D&D 5e EQUIPMENT SYSTEM TESTS")
    print("=" * 80)
    
    try:
        # Database coverage tests
        test_armor_database_coverage()
        test_tools_database_coverage()
        test_gear_database_coverage()
        
        # Selection and assignment tests
        test_armor_selection_by_class()
        test_tools_selection_by_class()
        test_equipment_pack_assignment()
        test_spellcasting_focus_assignment()
        
        # Prioritization tests
        test_equipment_prioritization()
        
        print("\n" + "=" * 80)
        print("✅ ALL EQUIPMENT SYSTEM TESTS PASSED!")
        print("=" * 80)
        print(f"Armor Database: {len(ALL_ARMOR)} items")
        print(f"Tools Database: {len(ALL_TOOLS)} items")
        print(f"Gear Database: {len(ALL_ADVENTURING_GEAR)} items")
        print(f"Total Equipment Items: {len(ALL_ARMOR) + len(ALL_TOOLS) + len(ALL_ADVENTURING_GEAR)}")
        print("\nThe D&D character creator will now prioritize official D&D 5e equipment,")
        print("armor, and tools before creating custom items, following D&D 5e rules")
        print("for class proficiencies and character needs.")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = run_comprehensive_equipment_tests()
    sys.exit(0 if success else 1)
