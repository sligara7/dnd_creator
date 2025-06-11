import json
import os
from typing import Dict, Any

# filepath: /home/ajs7/dnd_tools/dnd_char_creator/backend4/character_utils.py
def format_character_summary(character_data: Dict[str, Any]) -> str:
    """Format character data into readable text with enhanced details."""
    output = []
    
    # Basic identity
    output.append("=== CHARACTER IDENTITY ===")
    output.append(f"Name: {character_data.get('name', 'Unknown')}")
    output.append(f"Species: {character_data.get('species', 'Unknown')}")
    output.append(f"Level: {character_data.get('level', 1)}")
    output.append(f"Classes: {', '.join([f'{cls} ({lvl})' for cls, lvl in character_data.get('classes', {}).items()])}")
    
    # Subclasses
    if character_data.get('subclasses'):
        subclass_str = ', '.join([f"{cls}: {subcls}" for cls, subcls in character_data.get('subclasses', {}).items()])
        output.append(f"Subclasses: {subclass_str}")
    
    output.append(f"Background: {character_data.get('background', 'Unknown')}")
    output.append(f"Alignment: {character_data.get('alignment', 'Unknown')}")
    output.append("")
    
    # Ability scores
    output.append("=== ABILITY SCORES ===")
    abilities = character_data.get('ability_scores', {})
    mods = character_data.get('ability_modifiers', {})
    
    for ability in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
        score = abilities.get(ability, 10)
        mod = mods.get(ability, 0)
        mod_str = f"+{mod}" if mod >= 0 else f"{mod}"
        output.append(f"{ability.capitalize():12} {score:2} ({mod_str})")
    output.append("")
    
    # Combat stats
    output.append("=== COMBAT ===")
    output.append(f"AC: {character_data.get('ac', 10)}")
    hp = character_data.get('hp', {})
    output.append(f"HP: {hp.get('current', 0)}/{hp.get('max', 0)}")
    output.append(f"Initiative: {character_data.get('initiative', 0)}")
    output.append(f"Proficiency Bonus: +{character_data.get('proficiency_bonus', 2)}")
    output.append("")
    
    # Enhanced Equipment Section
    output.append("=== EQUIPMENT ===")
    
    # Armor
    armor = character_data.get('armor', {})
    if isinstance(armor, dict) and armor.get('name'):
        output.append(f"Armor: {armor['name']} (AC {armor.get('ac_base', 10)})")
        if armor.get('special_properties'):
            output.append(f"  Properties: {', '.join(armor['special_properties'])}")
        if armor.get('description'):
            output.append(f"  Description: {armor['description']}")
    elif isinstance(armor, str) and armor:
        output.append(f"Armor: {armor}")
    
    # Weapons
    output.append("\nWeapons:")
    for weapon in character_data.get('weapons', []):
        if isinstance(weapon, dict):
            magical_indicator = " (Magical)" if weapon.get('magical', False) else ""
            output.append(f"- {weapon.get('name', 'Unknown')}{magical_indicator}")
            output.append(f"  Damage: {weapon.get('damage', '1d4')} {weapon.get('damage_type', 'piercing')}")
            if weapon.get('special_abilities'):
                output.append(f"  Special: {', '.join(weapon['special_abilities'])}")
            if weapon.get('description'):
                output.append(f"  Description: {weapon['description']}")
        elif isinstance(weapon, str):
            output.append(f"- {weapon}")
    
    # Magical Items
    magical_items = character_data.get('magical_items', [])
    if magical_items:
        output.append("\nMagical Items:")
        for item in magical_items:
            if isinstance(item, dict):
                attune_text = " (Requires Attunement)" if item.get('attunement', False) else ""
                output.append(f"- {item.get('name', 'Unknown')} ({item.get('rarity', 'common')}){attune_text}")
                if item.get('properties'):
                    output.append(f"  Properties: {', '.join(item['properties'])}")
                if item.get('description'):
                    output.append(f"  Description: {item['description']}")
    
    # Regular Equipment
    equipment = character_data.get('equipment', [])
    if equipment:
        output.append("\nOther Equipment:")
        for item in equipment:
            if isinstance(item, dict):
                qty_text = f" x{item['quantity']}" if item.get('quantity', 1) > 1 else ""
                output.append(f"- {item.get('name', 'Unknown')}{qty_text}")
            elif isinstance(item, str):
                output.append(f"- {item}")
    
    output.append("")
    
    # Special Abilities
    special_abilities = character_data.get('special_abilities', [])
    if special_abilities:
        output.append("=== SPECIAL ABILITIES ===")
        for ability in special_abilities:
            if isinstance(ability, dict):
                output.append(f"- {ability.get('name', 'Unknown')} ({ability.get('uses', 'at will')})")
                if ability.get('description'):
                    output.append(f"  {ability['description']}")
        output.append("")
    
    # Spellcasting
    if character_data.get('spellcasting_ability'):
        output.append("=== SPELLCASTING ===")
        output.append(f"Spellcasting Ability: {character_data['spellcasting_ability'].capitalize()}")
        output.append(f"Spell Save DC: {character_data.get('spell_save_dc', 10)}")
        output.append(f"Spell Attack Bonus: +{character_data.get('spell_attack_bonus', 0)}")
        
        # Spell slots
        spell_slots = character_data.get('spell_slots', {})
        if spell_slots:
            slots_text = ", ".join([f"Level {level}: {slots}" for level, slots in spell_slots.items()])
            output.append(f"Spell Slots: {slots_text}")
        
        # Spells known
        spells_known = character_data.get('spells_known', {})
        if spells_known:
            output.append("\nSpells Known:")
            for level, spells in sorted(spells_known.items(), key=lambda x: int(x[0])):
                level_name = "Cantrips" if level == "0" else f"Level {level}"
                output.append(f"  {level_name}: {', '.join(spells)}")
        output.append("")
    
    # Skills and features
    output.append("=== PROFICIENT SKILLS ===")
    for skill in character_data.get('proficient_skills', []):
        output.append(f"- {skill}")
    output.append("")
    
    # Character details
    output.append("=== CHARACTER DETAILS ===")
    if character_data.get('personality_traits'):
        output.append("Personality Traits:")
        for trait in character_data.get('personality_traits', []):
            output.append(f"- {trait}")
    
    if character_data.get('ideals'):
        output.append("Ideals:")
        for ideal in character_data.get('ideals', []):
            output.append(f"- {ideal}")
            
    if character_data.get('bonds'):
        output.append("Bonds:")
        for bond in character_data.get('bonds', []):
            output.append(f"- {bond}")
            
    if character_data.get('flaws'):
        output.append("Flaws:")
        for flaw in character_data.get('flaws', []):
            output.append(f"- {flaw}")
    
    # Enhanced personality details
    personality_details = character_data.get('personality_details', {})
    if personality_details:
        output.append("\n=== PERSONALITY DETAILS ===")
        if personality_details.get('appearance'):
            output.append(f"Appearance: {personality_details['appearance']}")
        if personality_details.get('mannerisms'):
            output.append(f"Mannerisms: {', '.join(personality_details['mannerisms'])}")
        if personality_details.get('voice_and_speech'):
            output.append(f"Voice: {personality_details['voice_and_speech']}")
    
    # Enhanced backstory
    if character_data.get('backstory'):
        output.append("\n=== BACKSTORY ===")
        output.append(character_data.get('backstory', ''))
    
    return "\n".join(output)


def save_character(character_data: Dict[str, Any], save_dir: str = None) -> str:
    """Save character data to a JSON file."""
    if save_dir is None:
        save_dir = os.path.join(os.path.dirname(__file__), 'saved_characters')
    
    # Create characters directory if it doesn't exist
    os.makedirs(save_dir, exist_ok=True)
    
    # Generate filename from character name
    char_name = character_data.get('name', 'unnamed_character')
    safe_name = ''.join(c if c.isalnum() else '_' for c in char_name.lower())
    filename = os.path.join(save_dir, f"{safe_name}.json")
    
    # Save the character data
    with open(filename, 'w') as f:
        json.dump(character_data, f, indent=2)
    
    return filename