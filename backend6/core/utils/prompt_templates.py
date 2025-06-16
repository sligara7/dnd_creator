"""
Simple Prompt Templates for D&D Character Creation.

MINIMAL VERSION: Focused on character creation with optional cultural enhancement.
Culture features are simple suggestions that enhance but never restrict creativity.

Philosophy:
- Character creation comes first
- Simple, clean templates
- Culture adds flavor, never requirements
- Creative freedom is paramount
"""

from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

# ============================================================================
# MINIMAL IMPORTS - Only what we need for character creation
# ============================================================================

# Optional culture support - graceful fallback if not available
try:
    from ..enums.culture_types import CultureAuthenticityLevel
    CULTURE_SUPPORT = True
except ImportError:
    class CultureAuthenticityLevel:
        CREATIVE = "creative"
        GAMING = "gaming"
    CULTURE_SUPPORT = False


# ============================================================================
# SIMPLE PROMPT TYPES - Character Focused
# ============================================================================

class PromptType(Enum):
    """Simple prompt types for character creation."""
    CHARACTER_NAME = "character_name"
    CHARACTER_BACKGROUND = "character_background" 
    CULTURAL_FLAVOR = "cultural_flavor"
    PERSONALITY_TRAITS = "personality_traits"
    CHARACTER_STORY = "character_story"


@dataclass
class SimplePrompt:
    """Simple prompt template for character creation."""
    template: str
    placeholder_count: int
    example: str
    purpose: str


# ============================================================================
# CHARACTER NAME PROMPTS - Simple and Effective
# ============================================================================

CHARACTER_NAME_PROMPTS = {
    "basic": SimplePrompt(
        template="Generate {count} names suitable for a {character_type} character. The names should be easy to pronounce at a gaming table.",
        placeholder_count=2,
        example="Generate 5 names suitable for a warrior character. The names should be easy to pronounce at a gaming table.",
        purpose="Basic character name generation"
    ),
    
    "with_culture": SimplePrompt(
        template="Generate {count} names for a {character_type} character with {culture_hint} inspiration. Keep names gaming-friendly and easy to pronounce.",
        placeholder_count=3,
        example="Generate 5 names for a ranger character with Celtic inspiration. Keep names gaming-friendly and easy to pronounce.",
        purpose="Character names with cultural flavor"
    ),
    
    "fantasy": SimplePrompt(
        template="Create {count} fantasy names for a {character_type}. Make them memorable but not too complex for gaming use.",
        placeholder_count=2,
        example="Create 5 fantasy names for a wizard. Make them memorable but not too complex for gaming use.",
        purpose="Fantasy character names"
    )
}


# ============================================================================
# CHARACTER BACKGROUND PROMPTS - Creative Support
# ============================================================================

CHARACTER_BACKGROUND_PROMPTS = {
    "simple_background": SimplePrompt(
        template="Create a brief background for a {character_type} character named {character_name}. Include personality traits, motivation, and one interesting detail for roleplay.",
        placeholder_count=2,
        example="Create a brief background for a rogue character named Zara. Include personality traits, motivation, and one interesting detail for roleplay.",
        purpose="Basic character background"
    ),
    
    "cultural_background": SimplePrompt(
        template="Create a background for {character_name}, a {character_type} from a culture inspired by {culture_hint}. Focus on character development and roleplay opportunities.",
        placeholder_count=3,
        example="Create a background for Erik, a fighter from a culture inspired by Norse traditions. Focus on character development and roleplay opportunities.",
        purpose="Background with cultural elements"
    ),
    
    "story_hooks": SimplePrompt(
        template="Generate 3 story hooks and background elements for {character_name}, a {character_type}. Make them suitable for any campaign setting.",
        placeholder_count=2,
        example="Generate 3 story hooks and background elements for Luna, a cleric. Make them suitable for any campaign setting.",
        purpose="Character story hooks"
    )
}


# ============================================================================
# CULTURAL FLAVOR PROMPTS - Enhancement Only
# ============================================================================

CULTURAL_FLAVOR_PROMPTS = {
    "light_flavor": SimplePrompt(
        template="Add some {culture_type} cultural flavor to enhance {character_name}'s background. Keep it optional and supportive of creative freedom.",
        placeholder_count=2,
        example="Add some elven cultural flavor to enhance Lyralei's background. Keep it optional and supportive of creative freedom.",
        purpose="Light cultural enhancement"
    ),
    
    "traditions": SimplePrompt(
        template="Suggest 2-3 cultural traditions or customs that could enhance {character_name}'s roleplay, inspired by {culture_hint}. Make them optional additions.",
        placeholder_count=2,
        example="Suggest 2-3 cultural traditions or customs that could enhance Bjorn's roleplay, inspired by Viking culture. Make them optional additions.",
        purpose="Optional cultural traditions"
    ),
    
    "naming_context": SimplePrompt(
        template="Provide context for the name {character_name} including meaning, pronunciation tip, and cultural significance if relevant.",
        placeholder_count=1,
        example="Provide context for the name Seamus including meaning, pronunciation tip, and cultural significance if relevant.",
        purpose="Name context and pronunciation"
    )
}


# ============================================================================
# PERSONALITY AND TRAITS PROMPTS - Character Development
# ============================================================================

PERSONALITY_PROMPTS = {
    "basic_traits": SimplePrompt(
        template="Generate personality traits, ideals, bonds, and flaws for {character_name}, a {character_type}. Make them interesting for roleplay.",
        placeholder_count=2,
        example="Generate personality traits, ideals, bonds, and flaws for Marcus, a paladin. Make them interesting for roleplay.",
        purpose="D&D personality traits"
    ),
    
    "cultural_personality": SimplePrompt(
        template="Create personality traits for {character_name} that blend their {character_type} nature with {culture_hint} cultural influences. Keep it flexible for player creativity.",
        placeholder_count=3,
        example="Create personality traits for Yuki that blend their monk nature with Japanese cultural influences. Keep it flexible for player creativity.",
        purpose="Culturally influenced personality"
    ),
    
    "quirks": SimplePrompt(
        template="Generate 3 interesting quirks or mannerisms for {character_name} that will make them memorable at the gaming table.",
        placeholder_count=1,
        example="Generate 3 interesting quirks or mannerisms for Pip that will make them memorable at the gaming table.",
        purpose="Character quirks and mannerisms"
    )
}


# ============================================================================
# SIMPLE PROMPT BUILDER FUNCTIONS
# ============================================================================

def build_character_name_prompt(character_type: str, count: int = 5, 
                               culture_hint: Optional[str] = None) -> str:
    """
    Build a simple prompt for character name generation.
    
    Args:
        character_type: Type of character (fighter, wizard, etc.)
        count: Number of names to generate
        culture_hint: Optional cultural inspiration
        
    Returns:
        Ready-to-use prompt string
    """
    if culture_hint:
        template = CHARACTER_NAME_PROMPTS["with_culture"].template
        return template.format(
            count=count,
            character_type=character_type,
            culture_hint=culture_hint
        )
    else:
        template = CHARACTER_NAME_PROMPTS["basic"].template
        return template.format(
            count=count,
            character_type=character_type
        )


def build_character_background_prompt(character_name: str, character_type: str,
                                    culture_hint: Optional[str] = None) -> str:
    """
    Build a simple prompt for character background generation.
    
    Args:
        character_name: Character's name
        character_type: Type of character
        culture_hint: Optional cultural inspiration
        
    Returns:
        Ready-to-use prompt string
    """
    if culture_hint:
        template = CHARACTER_BACKGROUND_PROMPTS["cultural_background"].template
        return template.format(
            character_name=character_name,
            character_type=character_type,
            culture_hint=culture_hint
        )
    else:
        template = CHARACTER_BACKGROUND_PROMPTS["simple_background"].template
        return template.format(
            character_name=character_name,
            character_type=character_type
        )


def build_personality_prompt(character_name: str, character_type: str,
                           culture_hint: Optional[str] = None) -> str:
    """
    Build a simple prompt for personality trait generation.
    
    Args:
        character_name: Character's name
        character_type: Type of character
        culture_hint: Optional cultural inspiration
        
    Returns:
        Ready-to-use prompt string
    """
    if culture_hint:
        template = PERSONALITY_PROMPTS["cultural_personality"].template
        return template.format(
            character_name=character_name,
            character_type=character_type,
            culture_hint=culture_hint
        )
    else:
        template = PERSONALITY_PROMPTS["basic_traits"].template
        return template.format(
            character_name=character_name,
            character_type=character_type
        )


def add_cultural_flavor_prompt(character_name: str, culture_hint: str) -> str:
    """
    Build a prompt to add optional cultural flavor to a character.
    
    Args:
        character_name: Character's name
        culture_hint: Cultural inspiration
        
    Returns:
        Prompt for cultural enhancement (optional)
    """
    template = CULTURAL_FLAVOR_PROMPTS["light_flavor"].template
    return template.format(
        character_name=character_name,
        culture_type=culture_hint
    )


# ============================================================================
# COMPLETE CHARACTER PROMPT - All-in-One
# ============================================================================

def build_complete_character_prompt(character_name: str, character_type: str,
                                  culture_hint: Optional[str] = None,
                                  include_names: bool = False) -> str:
    """
    Build a complete character generation prompt.
    
    Args:
        character_name: Character's name (or "generate" to create names)
        character_type: Type of character
        culture_hint: Optional cultural inspiration
        include_names: Whether to generate additional names
        
    Returns:
        Complete character generation prompt
    """
    sections = []
    
    # Names section (if requested)
    if include_names or character_name.lower() == "generate":
        name_prompt = build_character_name_prompt(character_type, 5, culture_hint)
        sections.append(f"NAMES:\n{name_prompt}")
        
        if character_name.lower() == "generate":
            character_name = "[Generated Name]"
    
    # Background section
    background_prompt = build_character_background_prompt(character_name, character_type, culture_hint)
    sections.append(f"BACKGROUND:\n{background_prompt}")
    
    # Personality section
    personality_prompt = build_personality_prompt(character_name, character_type, culture_hint)
    sections.append(f"PERSONALITY:\n{personality_prompt}")
    
    # Optional cultural flavor (if specified)
    if culture_hint:
        flavor_prompt = add_cultural_flavor_prompt(character_name, culture_hint)
        sections.append(f"CULTURAL NOTES (Optional):\n{flavor_prompt}")
    
    # Add instructions
    instructions = """
INSTRUCTIONS:
- Focus on character creation and roleplay potential
- Keep cultural elements as optional enhancements, not requirements
- Make names easy to pronounce at gaming tables
- Provide creative hooks that work in any campaign
- Support player creativity and freedom
"""
    sections.append(instructions)
    
    return "\n\n".join(sections)


# ============================================================================
# PROMPT VALIDATION - Simple and Supportive
# ============================================================================

def validate_prompt_inputs(character_type: str, character_name: Optional[str] = None,
                          culture_hint: Optional[str] = None) -> tuple[bool, List[str]]:
    """
    Simple validation for prompt inputs - supportive, not restrictive.
    
    Args:
        character_type: Type of character
        character_name: Optional character name
        culture_hint: Optional cultural inspiration
        
    Returns:
        (is_valid, suggestions) - always returns True with helpful suggestions
    """
    suggestions = []
    
    # Character type suggestions
    if not character_type:
        suggestions.append("Character type is required (fighter, wizard, rogue, etc.)")
        return False, suggestions
    
    if len(character_type) < 3:
        suggestions.append("Consider a more specific character type for better results")
    
    # Name suggestions
    if character_name and len(character_name) > 20:
        suggestions.append("Shorter names are easier to use at gaming tables")
    
    # Culture suggestions
    if culture_hint and len(culture_hint) > 50:
        suggestions.append("Simpler cultural hints often work better")
    
    # Always valid - suggestions are just helpful
    if not suggestions:
        suggestions.append("All inputs look good for character generation!")
    
    return True, suggestions


# ============================================================================
# TEMPLATE UTILITIES - Gaming Table Focused
# ============================================================================

def get_available_templates() -> Dict[str, List[str]]:
    """Get all available prompt templates organized by category."""
    return {
        "names": list(CHARACTER_NAME_PROMPTS.keys()),
        "backgrounds": list(CHARACTER_BACKGROUND_PROMPTS.keys()),
        "personality": list(PERSONALITY_PROMPTS.keys()),
        "cultural_flavor": list(CULTURAL_FLAVOR_PROMPTS.keys())
    }


def get_template_example(category: str, template_name: str) -> Optional[str]:
    """Get an example for a specific template."""
    templates = {
        "names": CHARACTER_NAME_PROMPTS,
        "backgrounds": CHARACTER_BACKGROUND_PROMPTS,
        "personality": PERSONALITY_PROMPTS,
        "cultural_flavor": CULTURAL_FLAVOR_PROMPTS
    }
    
    category_templates = templates.get(category, {})
    template = category_templates.get(template_name)
    
    return template.example if template else None


def get_gaming_friendly_suggestions() -> List[str]:
    """Get suggestions for making prompts more gaming-table friendly."""
    return [
        "Keep names short and pronounceable",
        "Focus on roleplay opportunities",
        "Make cultural elements optional",
        "Include personality hooks for the GM",
        "Provide backstory that works in any setting",
        "Add quirks that are memorable but not disruptive",
        "Keep complexity appropriate for the table"
    ]


# ============================================================================
# EXPORTS - Keep It Simple
# ============================================================================

__all__ = [
    # Core types
    "PromptType",
    "SimplePrompt",
    
    # Template collections
    "CHARACTER_NAME_PROMPTS",
    "CHARACTER_BACKGROUND_PROMPTS", 
    "PERSONALITY_PROMPTS",
    "CULTURAL_FLAVOR_PROMPTS",
    
    # Builder functions
    "build_character_name_prompt",
    "build_character_background_prompt",
    "build_personality_prompt",
    "add_cultural_flavor_prompt",
    "build_complete_character_prompt",
    
    # Utilities
    "validate_prompt_inputs",
    "get_available_templates",
    "get_template_example",
    "get_gaming_friendly_suggestions"
]

# ============================================================================
# MODULE INFO
# ============================================================================

__version__ = "1.0.0"
__description__ = "Simple Prompt Templates for D&D Character Creation - Culture Enhances, Never Restricts"