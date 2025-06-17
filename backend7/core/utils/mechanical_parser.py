"""
Essential D&D Mechanical Parser Utilities

Streamlined mechanical parsing utilities following backend7 architecture.
Based on crude_functional.py patterns and essential-only philosophy.
Maintains overarching functionality of crude_functional.py approach.

Mechanical parsing focuses on D&D rules, stats, and game mechanics with simple, direct processing.
"""

from typing import Dict, List, Tuple, Optional, Any, Union
from core.enums import (
    AbilityScore, Skill, SavingThrow, DamageType, ConditionType,
    SpellSchool, MagicSchool, ActionType, DurationUnit
)

# ============ CORE MECHANICAL PARSING ============

def parse_ability_scores(ability_input: Union[Dict[str, int], List[int], str]) -> Dict[str, int]:
    """Parse ability scores - crude_functional.py simple parsing."""
    if not ability_input:
        return get_default_ability_scores()
    
    if isinstance(ability_input, dict):
        return normalize_ability_dict(ability_input)
    elif isinstance(ability_input, list):
        return list_to_ability_dict(ability_input)
    elif isinstance(ability_input, str):
        return parse_ability_string(ability_input)
    else:
        return get_default_ability_scores()

def normalize_ability_dict(ability_dict: Dict[str, int]) -> Dict[str, int]:
    """Normalize ability score dictionary - crude_functional.py standardization."""
    if not ability_dict:
        return get_default_ability_scores()
    
    # Standard ability score names
    standard_abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
    
    normalized = {}
    for ability in standard_abilities:
        # Try various name formats
        value = None
        for key in ability_dict:
            key_lower = key.lower().strip()
            if key_lower == ability or key_lower == ability[:3]:  # STR, DEX, etc.
                value = ability_dict[key]
                break
        
        # Default to 10 if not found
        normalized[ability] = max(1, min(20, int(value) if value is not None else 10))
    
    return normalized

def list_to_ability_dict(ability_list: List[int]) -> Dict[str, int]:
    """Convert ability list to dictionary - crude_functional.py direct conversion."""
    if not ability_list or len(ability_list) != 6:
        return get_default_ability_scores()
    
    ability_names = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
    
    return {
        ability_names[i]: max(1, min(20, int(ability_list[i])))
        for i in range(6)
    }

def parse_ability_string(ability_string: str) -> Dict[str, int]:
    """Parse ability scores from string - crude_functional.py string parsing."""
    if not ability_string:
        return get_default_ability_scores()
    
    # Simple formats: "15,14,13,12,10,8" or "STR:15,DEX:14,..."
    ability_string = ability_string.strip()
    
    if ":" in ability_string:
        return parse_named_ability_string(ability_string)
    else:
        return parse_numeric_ability_string(ability_string)

def parse_named_ability_string(ability_string: str) -> Dict[str, int]:
    """Parse named ability string - crude_functional.py named parsing."""
    abilities = get_default_ability_scores()
    
    parts = ability_string.split(",")
    for part in parts:
        if ":" in part:
            name, value = part.split(":", 1)
            name = name.strip().lower()
            
            # Map common abbreviations
            name_mapping = {
                "str": "strength", "dex": "dexterity", "con": "constitution",
                "int": "intelligence", "wis": "wisdom", "cha": "charisma"
            }
            
            full_name = name_mapping.get(name, name)
            if full_name in abilities:
                try:
                    abilities[full_name] = max(1, min(20, int(value.strip())))
                except ValueError:
                    pass  # Keep default value
    
    return abilities

def parse_numeric_ability_string(ability_string: str) -> Dict[str, int]:
    """Parse numeric ability string - crude_functional.py numeric parsing."""
    try:
        values = [int(x.strip()) for x in ability_string.split(",")]
        if len(values) == 6:
            return list_to_ability_dict(values)
    except ValueError:
        pass
    
    return get_default_ability_scores()

def get_default_ability_scores() -> Dict[str, int]:
    """Get default ability scores - crude_functional.py safe defaults."""
    return {
        "strength": 10,
        "dexterity": 10,
        "constitution": 10,
        "intelligence": 10,
        "wisdom": 10,
        "charisma": 10
    }

# ============ SKILL AND PROFICIENCY PARSING ============

def parse_skills(skill_input: Union[List[str], Dict[str, Any], str]) -> Dict[str, Any]:
    """Parse skill proficiencies - crude_functional.py skill processing."""
    if not skill_input:
        return {}
    
    if isinstance(skill_input, list):
        return list_to_skill_dict(skill_input)
    elif isinstance(skill_input, dict):
        return normalize_skill_dict(skill_input)
    elif isinstance(skill_input, str):
        return parse_skill_string(skill_input)
    else:
        return {}

def list_to_skill_dict(skill_list: List[str]) -> Dict[str, Any]:
    """Convert skill list to dictionary - crude_functional.py list conversion."""
    skill_dict = {}
    
    for skill in skill_list:
        if skill:
            skill_name = skill.strip().lower().replace(" ", "_")
            skill_dict[skill_name] = {"proficient": True, "expertise": False}
    
    return skill_dict

def normalize_skill_dict(skill_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize skill dictionary - crude_functional.py normalization."""
    normalized = {}
    
    for skill, value in skill_dict.items():
        skill_name = skill.strip().lower().replace(" ", "_")
        
        if isinstance(value, bool):
            normalized[skill_name] = {"proficient": value, "expertise": False}
        elif isinstance(value, dict):
            normalized[skill_name] = {
                "proficient": value.get("proficient", False),
                "expertise": value.get("expertise", False)
            }
        else:
            normalized[skill_name] = {"proficient": True, "expertise": False}
    
    return normalized

def parse_skill_string(skill_string: str) -> Dict[str, Any]:
    """Parse skills from string - crude_functional.py string parsing."""
    if not skill_string:
        return {}
    
    skills = {}
    skill_parts = skill_string.split(",")
    
    for part in skill_parts:
        part = part.strip()
        if not part:
            continue
        
        # Check for expertise marker
        has_expertise = part.endswith("*") or "(expertise)" in part.lower()
        skill_name = part.replace("*", "").replace("(expertise)", "").strip().lower().replace(" ", "_")
        
        skills[skill_name] = {
            "proficient": True,
            "expertise": has_expertise
        }
    
    return skills

# ============ SPELL PARSING ============

def parse_spell_data(spell_input: Union[Dict[str, Any], str]) -> Dict[str, Any]:
    """Parse spell data - crude_functional.py spell processing."""
    if not spell_input:
        return {}
    
    if isinstance(spell_input, dict):
        return normalize_spell_dict(spell_input)
    elif isinstance(spell_input, str):
        return parse_spell_string(spell_input)
    else:
        return {}

def normalize_spell_dict(spell_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize spell dictionary - crude_functional.py spell normalization."""
    if not spell_dict:
        return {}
    
    normalized = {
        "name": spell_dict.get("name", "Unknown Spell"),
        "level": max(0, min(9, int(spell_dict.get("level", 0)))),
        "school": spell_dict.get("school", "universal").lower(),
        "casting_time": spell_dict.get("casting_time", "1 action"),
        "range": spell_dict.get("range", "Self"),
        "components": parse_spell_components(spell_dict.get("components", [])),
        "duration": spell_dict.get("duration", "Instantaneous"),
        "description": spell_dict.get("description", ""),
        "damage_type": spell_dict.get("damage_type", "").lower(),
        "save": spell_dict.get("save", "").lower(),
        "ritual": bool(spell_dict.get("ritual", False)),
        "concentration": bool(spell_dict.get("concentration", False))
    }
    
    return normalized

def parse_spell_string(spell_string: str) -> Dict[str, Any]:
    """Parse spell from string - crude_functional.py basic spell parsing."""
    if not spell_string:
        return {}
    
    # Simple format: "Fireball (3rd level, Evocation)"
    parts = spell_string.split("(")
    spell_name = parts[0].strip()
    
    spell_data = {
        "name": spell_name,
        "level": 0,
        "school": "universal",
        "casting_time": "1 action",
        "range": "Self",
        "components": [],
        "duration": "Instantaneous",
        "description": "",
        "ritual": False,
        "concentration": False
    }
    
    if len(parts) > 1:
        details = parts[1].replace(")", "").lower()
        
        # Extract level
        if "cantrip" in details:
            spell_data["level"] = 0
        else:
            for i in range(1, 10):
                if f"{i}" in details and ("level" in details or "st" in details or "nd" in details or "rd" in details or "th" in details):
                    spell_data["level"] = i
                    break
        
        # Extract school
        schools = ["abjuration", "conjuration", "divination", "enchantment", "evocation", "illusion", "necromancy", "transmutation"]
        for school in schools:
            if school in details:
                spell_data["school"] = school
                break
        
        # Check for ritual/concentration
        if "ritual" in details:
            spell_data["ritual"] = True
        if "concentration" in details:
            spell_data["concentration"] = True
    
    return spell_data

def parse_spell_components(component_input: Union[List[str], str]) -> List[str]:
    """Parse spell components - crude_functional.py component parsing."""
    if not component_input:
        return []
    
    if isinstance(component_input, list):
        return [comp.strip().upper() for comp in component_input if comp.strip()]
    elif isinstance(component_input, str):
        # Format: "V, S, M" or "Verbal, Somatic, Material"
        components = []
        comp_string = component_input.upper()
        
        if "V" in comp_string or "VERBAL" in comp_string:
            components.append("V")
        if "S" in comp_string or "SOMATIC" in comp_string:
            components.append("S")
        if "M" in comp_string or "MATERIAL" in comp_string:
            components.append("M")
        
        return components
    else:
        return []

# ============ EQUIPMENT PARSING ============

def parse_equipment_data(equipment_input: Union[Dict[str, Any], str]) -> Dict[str, Any]:
    """Parse equipment data - crude_functional.py equipment processing."""
    if not equipment_input:
        return {}
    
    if isinstance(equipment_input, dict):
        return normalize_equipment_dict(equipment_input)
    elif isinstance(equipment_input, str):
        return parse_equipment_string(equipment_input)
    else:
        return {}

def normalize_equipment_dict(equipment_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize equipment dictionary - crude_functional.py equipment normalization."""
    if not equipment_dict:
        return {}
    
    normalized = {
        "name": equipment_dict.get("name", "Unknown Item"),
        "type": equipment_dict.get("type", "item").lower(),
        "cost": parse_cost(equipment_dict.get("cost", 0)),
        "weight": max(0, float(equipment_dict.get("weight", 0))),
        "rarity": equipment_dict.get("rarity", "common").lower(),
        "magical": bool(equipment_dict.get("magical", False)),
        "attunement": bool(equipment_dict.get("attunement", False)),
        "description": equipment_dict.get("description", ""),
        "properties": equipment_dict.get("properties", [])
    }
    
    # Weapon-specific fields
    if normalized["type"] in ["weapon", "sword", "bow", "staff"]:
        normalized.update({
            "damage": equipment_dict.get("damage", "1d4"),
            "damage_type": equipment_dict.get("damage_type", "bludgeoning").lower(),
            "weapon_type": equipment_dict.get("weapon_type", "simple").lower(),
            "range": equipment_dict.get("range", "5 ft")
        })
    
    # Armor-specific fields
    if normalized["type"] in ["armor", "shield"]:
        normalized.update({
            "ac": max(0, int(equipment_dict.get("ac", 10))),
            "armor_type": equipment_dict.get("armor_type", "light").lower(),
            "stealth_disadvantage": bool(equipment_dict.get("stealth_disadvantage", False))
        })
    
    return normalized

def parse_equipment_string(equipment_string: str) -> Dict[str, Any]:
    """Parse equipment from string - crude_functional.py basic equipment parsing."""
    if not equipment_string:
        return {}
    
    # Simple format: "Longsword +1 (magic weapon)"
    equipment_data = {
        "name": equipment_string.strip(),
        "type": "item",
        "cost": 0,
        "weight": 0,
        "rarity": "common",
        "magical": False,
        "description": "",
        "properties": []
    }
    
    name_lower = equipment_string.lower()
    
    # Determine type from name
    if any(weapon in name_lower for weapon in ["sword", "bow", "axe", "hammer", "dagger", "spear"]):
        equipment_data["type"] = "weapon"
    elif any(armor in name_lower for armor in ["armor", "mail", "plate", "leather", "shield"]):
        equipment_data["type"] = "armor"
    elif any(tool in name_lower for tool in ["kit", "tools", "pouch", "pack"]):
        equipment_data["type"] = "tool"
    
    # Check for magical properties
    if any(magic in name_lower for magic in ["+1", "+2", "+3", "magic", "enchanted"]):
        equipment_data["magical"] = True
        equipment_data["rarity"] = "uncommon"
    
    return equipment_data

def parse_cost(cost_input: Union[int, float, str]) -> Dict[str, int]:
    """Parse cost data - crude_functional.py cost parsing."""
    if not cost_input:
        return {"gp": 0}
    
    if isinstance(cost_input, (int, float)):
        return {"gp": int(cost_input)}
    elif isinstance(cost_input, str):
        cost_string = cost_input.lower().strip()
        
        # Parse formats like "15 gp", "2 sp", "100 cp"
        cost_dict = {"cp": 0, "sp": 0, "gp": 0, "pp": 0}
        
        import re
        matches = re.findall(r'(\d+)\s*(cp|sp|gp|pp)', cost_string)
        for amount, currency in matches:
            cost_dict[currency] = int(amount)
        
        return cost_dict
    else:
        return {"gp": 0}

# ============ MODIFIER CALCULATION ============

def calculate_ability_modifier(ability_score: int) -> int:
    """Calculate ability modifier - crude_functional.py standard calculation."""
    if not isinstance(ability_score, int):
        ability_score = 10
    
    return (max(1, min(30, ability_score)) - 10) // 2

def calculate_proficiency_bonus(character_level: int) -> int:
    """Calculate proficiency bonus - crude_functional.py level-based calculation."""
    if not isinstance(character_level, int) or character_level < 1:
        character_level = 1
    
    return ((min(20, character_level) - 1) // 4) + 2

def calculate_skill_bonus(
    ability_score: int,
    proficient: bool = False,
    expertise: bool = False,
    character_level: int = 1
) -> int:
    """Calculate skill bonus - crude_functional.py skill calculation."""
    modifier = calculate_ability_modifier(ability_score)
    
    if proficient:
        proficiency = calculate_proficiency_bonus(character_level)
        if expertise:
            proficiency *= 2
        modifier += proficiency
    
    return modifier

def calculate_save_bonus(
    ability_score: int,
    proficient: bool = False,
    character_level: int = 1
) -> int:
    """Calculate saving throw bonus - crude_functional.py save calculation."""
    modifier = calculate_ability_modifier(ability_score)
    
    if proficient:
        modifier += calculate_proficiency_bonus(character_level)
    
    return modifier

# ============ UTILITY FUNCTIONS ============

def parse_dice_expression(dice_string: str) -> Dict[str, Any]:
    """Parse dice expression - crude_functional.py dice parsing."""
    if not dice_string:
        return {"count": 1, "sides": 4, "modifier": 0}
    
    # Simple format: "2d6+3" or "1d8"
    dice_string = dice_string.strip().lower().replace(" ", "")
    
    import re
    match = re.match(r'(\d*)d(\d+)([+-]\d+)?', dice_string)
    
    if match:
        count = int(match.group(1)) if match.group(1) else 1
        sides = int(match.group(2))
        modifier = int(match.group(3)) if match.group(3) else 0
        
        return {
            "count": max(1, count),
            "sides": max(2, sides),
            "modifier": modifier,
            "expression": dice_string
        }
    else:
        # Try to parse as just a number
        try:
            modifier = int(dice_string)
            return {"count": 0, "sides": 0, "modifier": modifier, "expression": dice_string}
        except ValueError:
            return {"count": 1, "sides": 4, "modifier": 0, "expression": "1d4"}

def format_modifier(modifier: int) -> str:
    """Format modifier for display - crude_functional.py formatting."""
    if modifier >= 0:
        return f"+{modifier}"
    else:
        return str(modifier)

def validate_mechanical_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate mechanical data - crude_functional.py validation."""
    if not data:
        return False, ["No mechanical data provided"]
    
    warnings = []
    
    # Check ability scores
    if "ability_scores" in data:
        abilities = data["ability_scores"]
        for ability, score in abilities.items():
            if not isinstance(score, int) or score < 3 or score > 20:
                warnings.append(f"Unusual {ability} score: {score}")
    
    # Check level
    if "level" in data:
        level = data["level"]
        if not isinstance(level, int) or level < 1 or level > 20:
            warnings.append(f"Invalid character level: {level}")
    
    # Data is always valid, just warn about unusual values
    return True, warnings

# ============ ESSENTIAL EXPORTS ============

__all__ = [
    # Ability score parsing
    'parse_ability_scores',
    'normalize_ability_dict',
    'list_to_ability_dict',
    'parse_ability_string',
    'get_default_ability_scores',
    
    # Skill parsing
    'parse_skills',
    'list_to_skill_dict',
    'normalize_skill_dict',
    'parse_skill_string',
    
    # Spell parsing
    'parse_spell_data',
    'normalize_spell_dict',
    'parse_spell_string',
    'parse_spell_components',
    
    # Equipment parsing
    'parse_equipment_data',
    'normalize_equipment_dict',
    'parse_equipment_string',
    'parse_cost',
    
    # Modifier calculations
    'calculate_ability_modifier',
    'calculate_proficiency_bonus',
    'calculate_skill_bonus',
    'calculate_save_bonus',
    
    # Utility functions
    'parse_dice_expression',
    'format_modifier',
    'validate_mechanical_data',
]

# ============ MODULE METADATA ============

__version__ = '1.0.0'
__description__ = 'Essential D&D mechanical parsing utilities'
__author__ = 'D&D Character Creator Backend7'

# Backend7 architecture compliance
BACKEND7_COMPLIANCE = {
    "layer": "core/utils",
    "focus": "mechanical_parsing_utilities",
    "line_target": 200,
    "dependencies": ["core.enums"],
    "philosophy": "crude_functional_inspired_essential_mechanics",
    "maintains_crude_functional_approach": True
}