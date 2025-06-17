"""
Essential D&D Naming Validator Utilities

Streamlined naming validation utilities following backend7 architecture.
Based on crude_functional.py patterns and essential-only philosophy.
Maintains overarching functionality of crude_functional.py approach.

Naming validation supports creative freedom - all names are valid, validation provides suggestions only.
Naming enhances character creation with cultural context while preserving player choice.
"""

from typing import Dict, List, Tuple, Optional, Any, Union
from enum import Enum, auto
from core.enums import CultureType, CreativityLevel

# ============ NAMING ENUMS ============

class NameCreativity(Enum):
    """Naming creativity levels."""
    TRADITIONAL = auto()  # Classic fantasy names
    CREATIVE = auto()     # Unique and imaginative names
    RANDOM = auto()       # Randomly generated names

class CustomizationScope(Enum):
    """Character customization scope."""
    COSMETIC = auto()     # Visual and aesthetic changes
    MECHANICAL = auto()   # Gameplay-affecting modifications
    FULL = auto()         # Comprehensive customization options

class NameType(Enum):
    """Name component types."""
    GIVEN = auto()        # First/personal name
    FAMILY = auto()       # Last/family name
    CLAN = auto()         # Clan or tribal name
    TITLE = auto()        # Honorific or title
    NICKNAME = auto()     # Informal name or epithet

# ============ CORE NAMING VALIDATION ============

def validate_character_name(
    character_name: str,
    race: str = None,
    culture: str = None,
    creativity_level: NameCreativity = NameCreativity.CREATIVE
) -> Tuple[bool, List[str], List[str]]:
    """Validate character name - crude_functional.py supportive validation."""
    if not character_name:
        return True, [], ["Name is optional - unnamed characters are welcome"]
    
    # Always valid - provide enhancement suggestions only
    is_valid = True
    suggestions = []
    notes = []
    
    name_length = len(character_name.strip())
    
    # Length suggestions (not restrictions)
    if name_length < 2:
        suggestions.append("Consider a longer name for easier recognition")
    elif name_length > 50:
        suggestions.append("Very long names might be shortened by other players")
    
    # Character suggestions
    if has_special_characters(character_name):
        suggestions.append("Special characters add uniqueness but may be hard to type")
    
    # Cultural enhancement suggestions
    if race and culture:
        cultural_suggestions = get_cultural_name_suggestions(race, culture)
        if cultural_suggestions:
            suggestions.extend(cultural_suggestions)
    
    # Creativity level suggestions
    creativity_suggestions = get_creativity_suggestions(character_name, creativity_level)
    if creativity_suggestions:
        suggestions.extend(creativity_suggestions)
    
    # Always encourage creativity
    notes.append("All names are valid - choose what feels right for your character")
    notes.append("Names can evolve during play through roleplay")
    
    return is_valid, suggestions, notes

def validate_name_components(
    name_components: Dict[str, str],
    race: str = None,
    culture: str = None
) -> Tuple[bool, List[str], List[str]]:
    """Validate name components - crude_functional.py flexible validation."""
    if not name_components:
        return True, [], ["Name components are optional - simple names work great"]
    
    is_valid = True
    suggestions = []
    notes = []
    
    # Validate each component
    for name_type, name_value in name_components.items():
        if name_value:
            component_suggestions = validate_name_component(name_type, name_value, race, culture)
            suggestions.extend(component_suggestions)
    
    # Cultural harmony suggestions
    if race and culture:
        harmony_suggestions = check_name_cultural_harmony(name_components, race, culture)
        suggestions.extend(harmony_suggestions)
    
    notes.append("Name components add depth but are entirely optional")
    notes.append("Mix and match from different cultures as desired")
    
    return is_valid, suggestions, notes

def validate_name_component(
    component_type: str,
    component_value: str,
    race: str = None,
    culture: str = None
) -> List[str]:
    """Validate individual name component - crude_functional.py component validation."""
    if not component_value:
        return []
    
    suggestions = []
    
    # Type-specific suggestions
    if component_type.lower() == "title":
        suggestions.extend(get_title_suggestions(component_value, race, culture))
    elif component_type.lower() == "clan":
        suggestions.extend(get_clan_name_suggestions(component_value, race, culture))
    elif component_type.lower() == "nickname":
        suggestions.extend(get_nickname_suggestions(component_value))
    
    return suggestions

# ============ CULTURAL NAME UTILITIES ============

def get_cultural_name_suggestions(race: str, culture: str) -> List[str]:
    """Get cultural name suggestions - crude_functional.py cultural enhancement."""
    if not race or not culture:
        return []
    
    suggestions = []
    
    # Race-specific naming suggestions
    race_suggestions = {
        "elf": ["consider_melodic_flowing_sounds", "explore_nature_inspired_elements"],
        "dwarf": ["consider_strong_consonants", "explore_craft_or_stone_references"],
        "human": ["embrace_cultural_diversity", "draw_from_real_world_inspirations"],
        "halfling": ["consider_cozy_comfortable_sounds", "explore_food_or_comfort_themes"],
        "dragonborn": ["consider_draconic_elements", "explore_strong_powerful_sounds"],
        "tiefling": ["embrace_unique_combinations", "consider_virtue_or_concept_names"],
        "gnome": ["explore_whimsical_elements", "consider_invention_or_nature_themes"],
        "half-elf": ["blend_different_traditions", "create_unique_combinations"],
        "half-orc": ["embrace_cultural_duality", "consider_strength_based_elements"]
    }
    
    race_lower = race.lower()
    if race_lower in race_suggestions:
        suggestions.extend(race_suggestions[race_lower])
    
    # Culture-specific naming suggestions
    culture_suggestions = {
        "urban": ["consider_sophisticated_elements", "explore_cosmopolitan_influences"],
        "rural": ["embrace_simple_traditional_sounds", "consider_nature_connections"],
        "nomadic": ["explore_travel_inspired_elements", "consider_star_or_journey_themes"],
        "coastal": ["consider_sea_or_tide_elements", "explore_maritime_influences"],
        "mountain": ["embrace_strong_sturdy_sounds", "consider_stone_or_peak_references"],
        "forest": ["explore_woodland_elements", "consider_tree_or_animal_inspirations"],
        "desert": ["consider_sun_or_sand_elements", "explore_oasis_or_star_themes"]
    }
    
    culture_lower = culture.lower()
    if culture_lower in culture_suggestions:
        suggestions.extend(culture_suggestions[culture_lower])
    
    return suggestions

def check_name_cultural_harmony(
    name_components: Dict[str, str],
    race: str,
    culture: str
) -> List[str]:
    """Check name cultural harmony - crude_functional.py harmony suggestions."""
    suggestions = []
    
    if not name_components or not race or not culture:
        return suggestions
    
    # Suggest cultural elements that could enhance the name
    given_name = name_components.get("given", "")
    family_name = name_components.get("family", "")
    
    if given_name and family_name:
        suggestions.append("Consider how given and family names work together")
        
        # Cultural harmony suggestions
        if culture.lower() == "clan" and "clan" not in name_components:
            suggestions.append("Consider adding clan name for clan-based culture")
        elif culture.lower() in ["noble", "aristocratic"] and "title" not in name_components:
            suggestions.append("Consider adding title for high-status culture")
    
    return suggestions

# ============ CREATIVITY ENHANCEMENT ============

def get_creativity_suggestions(
    character_name: str,
    creativity_level: NameCreativity
) -> List[str]:
    """Get creativity-based suggestions - crude_functional.py creativity support."""
    if not character_name:
        return []
    
    suggestions = []
    
    if creativity_level == NameCreativity.TRADITIONAL:
        suggestions.extend([
            "explore_classic_fantasy_name_sources",
            "consider_established_naming_conventions",
            "draw_inspiration_from_literature"
        ])
    elif creativity_level == NameCreativity.CREATIVE:
        suggestions.extend([
            "blend_different_cultural_elements",
            "create_unique_sound_combinations",
            "consider_meaningful_name_elements"
        ])
    elif creativity_level == NameCreativity.RANDOM:
        suggestions.extend([
            "embrace_unexpected_combinations",
            "let_sound_guide_meaning",
            "consider_generated_name_variations"
        ])
    
    return suggestions

def suggest_name_variations(
    base_name: str,
    creativity_level: NameCreativity = NameCreativity.CREATIVE
) -> List[str]:
    """Suggest name variations - crude_functional.py variation generation."""
    if not base_name:
        return []
    
    variations = []
    base_clean = base_name.strip()
    
    # Simple variations based on creativity level
    if creativity_level == NameCreativity.TRADITIONAL:
        # Conservative variations
        variations.extend([
            f"{base_clean}son",  # Traditional patronymic
            f"{base_clean}daughter",
            base_clean.title(),  # Proper capitalization
        ])
    elif creativity_level == NameCreativity.CREATIVE:
        # Creative variations
        variations.extend([
            f"{base_clean[:3]}ara" if len(base_clean) > 3 else f"{base_clean}ara",
            f"{base_clean}wyn",
            f"{base_clean[:4]}iel" if len(base_clean) > 4 else f"{base_clean}iel",
        ])
    elif creativity_level == NameCreativity.RANDOM:
        # More random variations
        variations.extend([
            reverse_syllables(base_clean),
            f"{base_clean[-2:]}{base_clean[:-2]}" if len(base_clean) > 4 else base_clean,
            f"Z{base_clean[1:]}" if base_clean else "Zara"
        ])
    
    # Remove duplicates and empty strings
    variations = list(set([v for v in variations if v and v != base_clean]))
    
    return variations[:5]  # Limit to 5 variations

# ============ SPECIALIZED NAME VALIDATION ============

def get_title_suggestions(title: str, race: str = None, culture: str = None) -> List[str]:
    """Get title suggestions - crude_functional.py title enhancement."""
    suggestions = []
    
    if not title:
        return suggestions
    
    title_lower = title.lower()
    
    # Generic title suggestions
    if any(word in title_lower for word in ["lord", "lady", "sir", "dame"]):
        suggestions.append("Noble titles work well with aristocratic cultures")
    elif any(word in title_lower for word in ["chief", "elder", "shaman"]):
        suggestions.append("Tribal titles complement nomadic or clan cultures")
    elif any(word in title_lower for word in ["master", "scholar", "sage"]):
        suggestions.append("Academic titles suit urban or scholarly cultures")
    
    # Race-specific title suggestions
    if race:
        race_lower = race.lower()
        if race_lower == "dwarf" and "forge" not in title_lower:
            suggestions.append("Consider craft-related titles for dwarven characters")
        elif race_lower == "elf" and title_lower not in ["lord", "lady"]:
            suggestions.append("Elven titles often reflect long lifespans and wisdom")
    
    return suggestions

def get_clan_name_suggestions(clan_name: str, race: str = None, culture: str = None) -> List[str]:
    """Get clan name suggestions - crude_functional.py clan enhancement."""
    suggestions = []
    
    if not clan_name:
        return suggestions
    
    # General clan name suggestions
    suggestions.append("Clan names often reflect values, deeds, or origins")
    
    if race:
        race_lower = race.lower()
        if race_lower == "dwarf":
            suggestions.append("Dwarven clans often reference crafts, gems, or mountain features")
        elif race_lower == "dragonborn":
            suggestions.append("Dragonborn clans may reference draconic heritage or breath weapons")
        elif race_lower in ["half-orc", "orc"]:
            suggestions.append("Orcish clans often reference strength, weapons, or fierce animals")
    
    return suggestions

def get_nickname_suggestions(nickname: str) -> List[str]:
    """Get nickname suggestions - crude_functional.py nickname enhancement."""
    suggestions = []
    
    if not nickname:
        return suggestions
    
    suggestions.extend([
        "Nicknames often come from personality traits or memorable deeds",
        "Consider how the nickname was earned or given",
        "Nicknames can evolve during gameplay"
    ])
    
    return suggestions

# ============ UTILITY FUNCTIONS ============

def has_special_characters(name: str) -> bool:
    """Check if name has special characters - crude_functional.py character check."""
    if not name:
        return False
    
    special_chars = set("''-_.")
    return any(char in special_chars for char in name)

def reverse_syllables(name: str) -> str:
    """Reverse syllables in name - crude_functional.py simple reversal."""
    if not name or len(name) < 4:
        return name
    
    # Simple syllable reversal (very basic)
    mid = len(name) // 2
    return name[mid:] + name[:mid]

def is_pronounceable(name: str) -> bool:
    """Check if name is reasonably pronounceable - crude_functional.py pronunciation check."""
    if not name:
        return True  # Empty names are "pronounceable"
    
    # Simple heuristic: not too many consecutive consonants
    consonants = "bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ"
    consecutive_consonants = 0
    
    for char in name:
        if char in consonants:
            consecutive_consonants += 1
            if consecutive_consonants > 4:  # Very lenient
                return False
        else:
            consecutive_consonants = 0
    
    return True

def suggest_pronunciation_guide(name: str) -> str:
    """Suggest pronunciation guide - crude_functional.py pronunciation help."""
    if not name or len(name) < 4:
        return name
    
    # Very simple pronunciation guide
    # This is intentionally basic - real pronunciation is complex
    guide = name.lower()
    
    # Simple substitutions for common patterns
    guide = guide.replace("ph", "f")
    guide = guide.replace("gh", "g")
    guide = guide.replace("th", "th")
    
    return f"{name} (pronounced: {guide})"

def validate_name_length(name: str, min_length: int = 1, max_length: int = 50) -> Tuple[bool, List[str]]:
    """Validate name length - crude_functional.py length validation."""
    if not name:
        return True, ["Names are optional"]
    
    suggestions = []
    name_length = len(name.strip())
    
    if name_length < min_length:
        suggestions.append(f"Name is quite short - consider expanding if desired")
    elif name_length > max_length:
        suggestions.append(f"Very long name might be abbreviated by others")
    
    # Always valid - just suggestions
    return True, suggestions

# ============ COMPREHENSIVE NAME VALIDATION ============

def comprehensive_name_validation(
    character_name: str,
    name_components: Dict[str, str] = None,
    race: str = None,
    culture: str = None,
    creativity_level: NameCreativity = NameCreativity.CREATIVE
) -> Dict[str, Any]:
    """Comprehensive name validation - crude_functional.py complete assessment."""
    if not character_name and not name_components:
        return {
            "is_valid": True,
            "validation_level": "info",
            "suggestions": ["Names are optional but add character depth"],
            "notes": ["Unnamed characters can discover their name through play"],
            "variations": [],
            "cultural_harmony": True,
            "creative_freedom_preserved": True
        }
    
    # Run all validations
    name_valid, name_suggestions, name_notes = validate_character_name(
        character_name or "", race, culture, creativity_level
    )
    
    component_suggestions = []
    component_notes = []
    if name_components:
        _, component_suggestions, component_notes = validate_name_components(
            name_components, race, culture
        )
    
    # Generate variations
    variations = []
    if character_name:
        variations = suggest_name_variations(character_name, creativity_level)
    
    # Combine all feedback
    all_suggestions = list(set(name_suggestions + component_suggestions))
    all_notes = list(set(name_notes + component_notes))
    
    return {
        "is_valid": True,  # Names are always valid
        "validation_level": "suggestion",
        "suggestions": all_suggestions,
        "notes": all_notes,
        "variations": variations,
        "cultural_harmony": True,  # Cultural suggestions, not requirements
        "creative_freedom_preserved": True,  # Always preserved
        "pronunciation_guide": suggest_pronunciation_guide(character_name) if character_name else "",
        "is_pronounceable": is_pronounceable(character_name) if character_name else True
    }

# ============ ESSENTIAL EXPORTS ============

__all__ = [
    # Enums
    'NameCreativity',
    'CustomizationScope',
    'NameType',
    
    # Core validation
    'validate_character_name',
    'validate_name_components',
    'validate_name_component',
    
    # Cultural utilities
    'get_cultural_name_suggestions',
    'check_name_cultural_harmony',
    
    # Creativity utilities
    'get_creativity_suggestions',
    'suggest_name_variations',
    
    # Specialized validation
    'get_title_suggestions',
    'get_clan_name_suggestions',
    'get_nickname_suggestions',
    
    # Utility functions
    'has_special_characters',
    'reverse_syllables',
    'is_pronounceable',
    'suggest_pronunciation_guide',
    'validate_name_length',
    
    # Comprehensive validation
    'comprehensive_name_validation',
]

# ============ MODULE METADATA ============

__version__ = '1.0.0'
__description__ = 'Essential D&D naming validation utilities'
__author__ = 'D&D Character Creator Backend7'

# Backend7 architecture compliance
BACKEND7_COMPLIANCE = {
    "layer": "core/utils",
    "focus": "naming_validation_utilities",
    "line_target": 200,
    "dependencies": ["core.enums"],
    "philosophy": "crude_functional_inspired_creative_freedom_preserving",
    "maintains_crude_functional_approach": True,
    "naming_philosophy": "suggest_and_enhance_never_restrict"
}

# Naming Validation Philosophy
NAMING_PRINCIPLES = {
    "always_valid": "All names are valid - validation provides suggestions only",
    "creative_freedom": "Players can use any name they want",
    "cultural_enhancement": "Cultural suggestions enhance but never restrict",
    "supportive_feedback": "All feedback is positive and constructive",
    "optional_depth": "Name components add depth but are entirely optional"
}