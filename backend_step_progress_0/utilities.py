"""
D&D Character Creator Utilities - Refactored and Enhanced

This module provides utility functions that support the character creation system.
These utilities handle common tasks like level determination, text processing,
and D&D-specific calculations that are used across multiple modules.
"""

import re
import random
import logging
from typing import Dict, Any, List, Optional, Union, Tuple
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# LEVEL DETERMINATION UTILITIES
# ============================================================================

def determine_level_from_description(description: str) -> int:
    """Determine appropriate character level from description text."""
    
    if not description or not description.strip():
        return 1
    
    description_lower = description.lower()
    
    # Look for explicit level mentions first
    level_match = re.search(r'level\s*(\d+)', description_lower)
    if level_match:
        level = int(level_match.group(1))
        return max(1, min(20, level))
    
    # Look for tier mentions
    if any(tier in description_lower for tier in ["tier 4", "epic", "legendary campaign"]):
        return random.randint(17, 20)
    elif any(tier in description_lower for tier in ["tier 3", "high level"]):
        return random.randint(11, 16)
    elif any(tier in description_lower for tier in ["tier 2", "mid level"]):
        return random.randint(5, 10)
    elif any(tier in description_lower for tier in ["tier 1", "low level", "starting"]):
        return random.randint(1, 4)
    
    # Analyze experience indicators
    experience_score = _calculate_experience_score(description_lower)
    
    if experience_score >= 3:
        return random.randint(11, 20)  # High level
    elif experience_score >= 1:
        return random.randint(5, 10)   # Mid level
    elif experience_score <= -1:
        return random.randint(1, 4)    # Low level
    else:
        # Analyze role complexity
        complexity_score = _calculate_role_complexity(description_lower)
        
        if complexity_score >= 2:
            return random.randint(8, 15)  # Complex roles
        elif complexity_score >= 1:
            return random.randint(4, 10)  # Moderate complexity
        else:
            return random.randint(1, 6)   # Simple roles

def _calculate_experience_score(description: str) -> int:
    """Calculate experience level score from description."""
    
    high_experience = [
        "veteran", "master", "legendary", "ancient", "experienced", "seasoned",
        "elite", "renowned", "famous", "powerful", "mighty", "epic",
        "years of experience", "decades", "long career", "many battles",
        "grizzled", "battle-hardened", "wise", "elder", "senior"
    ]
    
    mid_experience = [
        "skilled", "trained", "competent", "capable", "proven", "established",
        "journeyman", "professional", "accomplished", "some experience",
        "practiced", "adept", "proficient"
    ]
    
    low_experience = [
        "young", "new", "novice", "beginning", "fresh", "inexperienced",
        "rookie", "apprentice", "student", "learning", "starting out",
        "untested", "green", "fledgling", "aspiring"
    ]
    
    high_count = sum(1 for indicator in high_experience if indicator in description)
    mid_count = sum(1 for indicator in mid_experience if indicator in description)
    low_count = sum(1 for indicator in low_experience if indicator in description)
    
    return high_count * 2 + mid_count - low_count * 2

def _calculate_role_complexity(description: str) -> int:
    """Calculate role complexity score from description."""
    
    very_complex = [
        "archmage", "lich", "dragon slayer", "planar traveler", "time mage",
        "demon hunter", "divine champion", "artifact wielder"
    ]
    
    complex_roles = [
        "assassin", "warlock", "sorcerer", "paladin", "high priest", 
        "master thief", "spymaster", "court wizard", "battle commander",
        "druid circle leader", "guild master"
    ]
    
    moderate_roles = [
        "cleric", "ranger", "bard", "monk", "artificer", "investigator",
        "merchant", "scholar", "healer", "tracker", "diplomat"
    ]
    
    very_complex_count = sum(1 for role in very_complex if role in description)
    complex_count = sum(1 for role in complex_roles if role in description)
    moderate_count = sum(1 for role in moderate_roles if role in description)
    
    return very_complex_count * 3 + complex_count * 2 + moderate_count

# ============================================================================
# D&D RULES UTILITIES
# ============================================================================

def get_mastery_description(mastery_property: str) -> str:
    """Get description of weapon mastery property (2024 D&D rules)."""
    
    mastery_descriptions = {
        "cleave": "When you hit a creature with a melee attack, you can make an attack against a second creature within 5 feet of the first that is also within your reach.",
        "graze": "If your attack roll misses, you can deal damage equal to your ability modifier to the target.",
        "nick": "When you make the Attack action with this weapon, you can make one additional attack as part of the same action with a different Light weapon you're holding.",
        "push": "If you hit a creature, you can push it up to 10 feet away from you if it is Large or smaller.",
        "sap": "If you hit a creature, it has disadvantage on its next attack roll before the start of your next turn.",
        "slow": "If you hit a creature, its speed is reduced by 10 feet until the start of your next turn.",
        "topple": "If you hit a creature, you can force it to make a Constitution saving throw. If it fails, it has the Prone condition.",
        "vex": "If you hit a creature, the next attack roll made by another creature against the target before the start of your next turn has advantage."
    }
    
    return mastery_descriptions.get(mastery_property.lower(), f"Unknown mastery property: {mastery_property}")

def calculate_modifier(ability_score: int) -> int:
    """Calculate ability modifier from ability score."""
    return (ability_score - 10) // 2

def format_modifier(modifier: int) -> str:
    """Format modifier as +X or -X string."""
    return f"+{modifier}" if modifier >= 0 else str(modifier)

def calculate_proficiency_bonus(level: int) -> int:
    """Calculate proficiency bonus based on character level."""
    return 2 + ((level - 1) // 4)

def get_spell_slots(class_name: str, level: int) -> Dict[int, int]:
    """Get spell slots for a class at given level (simplified)."""
    
    # This is a simplified version - would need full spell slot tables
    full_casters = ["bard", "cleric", "druid", "sorcerer", "wizard"]
    half_casters = ["paladin", "ranger", "artificer"]
    third_casters = ["eldritch knight", "arcane trickster"]
    
    if class_name.lower() in full_casters:
        return _get_full_caster_slots(level)
    elif class_name.lower() in half_casters:
        return _get_half_caster_slots(level)
    elif class_name.lower() in third_casters:
        return _get_third_caster_slots(level)
    else:
        return {}

def _get_full_caster_slots(level: int) -> Dict[int, int]:
    """Get full caster spell slots (simplified)."""
    slots = {}
    if level >= 1: slots[1] = min(4, 2 + (level - 1) // 2)
    if level >= 3: slots[2] = min(3, 1 + (level - 3) // 2)
    if level >= 5: slots[3] = min(3, 1 + (level - 5) // 2)
    if level >= 7: slots[4] = min(3, 1 + (level - 7) // 4)
    if level >= 9: slots[5] = min(3, 1 + (level - 9) // 4)
    if level >= 11: slots[6] = min(2, 1 + (level - 11) // 8)
    if level >= 13: slots[7] = min(2, 1 + (level - 13) // 6)
    if level >= 15: slots[8] = min(1, 1)
    if level >= 17: slots[9] = min(1, 1)
    return slots

def _get_half_caster_slots(level: int) -> Dict[int, int]:
    """Get half caster spell slots (simplified)."""
    if level < 2:
        return {}
    effective_level = level // 2
    return _get_full_caster_slots(effective_level)

def _get_third_caster_slots(level: int) -> Dict[int, int]:
    """Get 1/3 caster spell slots (simplified)."""
    if level < 3:
        return {}
    effective_level = level // 3
    return _get_full_caster_slots(effective_level)

# ============================================================================
# TEXT PROCESSING UTILITIES
# ============================================================================

def clean_description_text(text: str) -> str:
    """Clean and normalize description text."""
    
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove common formatting artifacts
    text = text.replace('\\n', ' ').replace('\\t', ' ')
    
    # Normalize quotes
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")
    
    return text

def extract_keywords(text: str) -> List[str]:
    """Extract relevant keywords from description text."""
    
    if not text:
        return []
    
    # Convert to lowercase for analysis
    text_lower = text.lower()
    
    # D&D-relevant keywords
    classes = ["artificer", "barbarian", "bard", "cleric", "druid", "fighter", "monk", "paladin", "ranger", "rogue", "sorcerer", "warlock", "wizard"]
    races = ["human", "elf", "dwarf", "halfling", "dragonborn", "gnome", "half-elf", "half-orc", "tiefling", "aasimar", "genasi", "goliath", "tabaxi"]
    backgrounds = ["acolyte", "criminal", "folk hero", "noble", "sage", "soldier", "charlatan", "entertainer", "hermit", "outlander"]
    
    keywords = []
    
    # Find class keywords
    for cls in classes:
        if cls in text_lower:
            keywords.append(f"class:{cls}")
    
    # Find race keywords
    for race in races:
        if race in text_lower:
            keywords.append(f"race:{race}")
    
    # Find background keywords
    for bg in backgrounds:
        if bg in text_lower:
            keywords.append(f"background:{bg}")
    
    return keywords

def wrap_text(text: str, width: int = 80) -> List[str]:
    """Wrap text to specified width, preserving words."""
    
    if not text:
        return []
    
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        if len(current_line + " " + word) <= width:
            current_line += (" " + word) if current_line else word
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)
    
    return lines

# ============================================================================
# VALIDATION UTILITIES
# ============================================================================

def is_valid_ability_score(score: Union[int, str]) -> bool:
    """Check if an ability score is valid (1-30)."""
    try:
        score_int = int(score)
        return 1 <= score_int <= 30
    except (ValueError, TypeError):
        return False

def is_valid_level(level: Union[int, str]) -> bool:
    """Check if a character level is valid (1-20)."""
    try:
        level_int = int(level)
        return 1 <= level_int <= 20
    except (ValueError, TypeError):
        return False

def validate_character_name(name: str) -> Tuple[bool, str]:
    """Validate character name and return (is_valid, error_message)."""
    
    if not name or not name.strip():
        return False, "Character name cannot be empty"
    
    name = name.strip()
    
    if len(name) < 2:
        return False, "Character name must be at least 2 characters long"
    
    if len(name) > 50:
        return False, "Character name cannot exceed 50 characters"
    
    # Check for reasonable characters (letters, spaces, hyphens, apostrophes)
    if not re.match(r"^[a-zA-Z\s\-'\.]+$", name):
        return False, "Character name contains invalid characters"
    
    return True, ""

# ============================================================================
# RANDOM GENERATION UTILITIES
# ============================================================================

def roll_dice(dice_string: str) -> int:
    """Roll dice from string like '1d6', '2d8+3', etc."""
    
    try:
        # Parse dice notation
        match = re.match(r'(\d+)d(\d+)([+-]\d+)?', dice_string.lower())
        if not match:
            return 0
        
        num_dice = int(match.group(1))
        die_size = int(match.group(2))
        modifier = int(match.group(3)) if match.group(3) else 0
        
        # Roll the dice
        total = sum(random.randint(1, die_size) for _ in range(num_dice))
        return total + modifier
        
    except (ValueError, AttributeError):
        return 0

def generate_stats_array(method: str = "standard") -> List[int]:
    """Generate ability score array using specified method."""
    
    if method == "standard":
        return [15, 14, 13, 12, 10, 8]
    elif method == "point_buy":
        # Default point buy distribution
        return [15, 14, 13, 12, 10, 8]
    elif method == "4d6_drop_lowest":
        stats = []
        for _ in range(6):
            rolls = [random.randint(1, 6) for _ in range(4)]
            rolls.sort(reverse=True)
            stats.append(sum(rolls[:3]))
        return sorted(stats, reverse=True)
    else:
        return [15, 14, 13, 12, 10, 8]

# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def get_default_equipment(character_class: str, level: int = 1) -> Dict[str, Any]:
    """Get default starting equipment for a class."""
    
    # Simplified starting equipment
    equipment_by_class = {
        "fighter": {
            "armor": "Chain Mail",
            "weapons": [{"name": "Longsword", "damage": "1d8", "properties": ["versatile"]}],
            "equipment": [{"name": "Adventurer's Pack", "quantity": 1}]
        },
        "wizard": {
            "armor": "None",
            "weapons": [{"name": "Dagger", "damage": "1d4", "properties": ["finesse", "light", "thrown"]}],
            "equipment": [{"name": "Spellbook", "quantity": 1}, {"name": "Component Pouch", "quantity": 1}]
        },
        "rogue": {
            "armor": "Leather Armor",
            "weapons": [{"name": "Rapier", "damage": "1d8", "properties": ["finesse"]}, {"name": "Dagger", "damage": "1d4", "properties": ["finesse", "light", "thrown"]}],
            "equipment": [{"name": "Thieves' Tools", "quantity": 1}]
        }
    }
    
    return equipment_by_class.get(character_class.lower(), {
        "armor": "Leather Armor",
        "weapons": [{"name": "Club", "damage": "1d4", "properties": ["light"]}],
        "equipment": [{"name": "Adventurer's Pack", "quantity": 1}]
    })

def get_class_hit_die(character_class: str) -> int:
    """Get hit die size for a class."""
    
    hit_dice = {
        "barbarian": 12, "fighter": 10, "paladin": 10, "ranger": 10,
        "bard": 8, "cleric": 8, "druid": 8, "monk": 8, "rogue": 8, "warlock": 8,
        "artificer": 8, "sorcerer": 6, "wizard": 6
    }
    
    return hit_dice.get(character_class.lower(), 8)

# ============================================================================
# MODULE SUMMARY
# ============================================================================
"""
REFACTORED UTILITIES MODULE

This module provides essential utility functions for the D&D character creation system:

LEVEL DETERMINATION:
- determine_level_from_description(): Smart level detection from text
- Experience and complexity scoring algorithms

D&D RULES UTILITIES:
- get_mastery_description(): 2024 D&D weapon mastery properties
- calculate_modifier(): Ability score to modifier conversion
- calculate_proficiency_bonus(): Level-based proficiency bonus
- get_spell_slots(): Spell slot calculations by class/level

TEXT PROCESSING:
- clean_description_text(): Text normalization
- extract_keywords(): D&D-relevant keyword extraction
- wrap_text(): Text formatting utilities

VALIDATION:
- is_valid_ability_score(): Score validation
- is_valid_level(): Level validation  
- validate_character_name(): Name validation with error messages

RANDOM GENERATION:
- roll_dice(): Dice notation parser and roller
- generate_stats_array(): Multiple stat generation methods

CONVENIENCE FUNCTIONS:
- get_default_equipment(): Starting equipment by class
- get_class_hit_die(): Hit die sizes by class

These utilities support the character creation workflow and can be used
across all modules for common D&D calculations and validations.
"""
