"""
Culture Generation Prompt Templates - Creative Character Generation Focus.

Creative prompt engineering for character background generation.
Follows Clean Architecture principles and CREATIVE_VALIDATION_APPROACH philosophy:
- Enable creativity rather than restrict it
- Focus on character generation support and enhancement  
- Constructive suggestions over rigid requirements
- Almost all cultures are usable for character generation

This module provides:
- Character-focused culture generation templates
- Creative freedom with optional authenticity levels
- Gaming-optimized prompt structures
- Pure functional template composition
- Flexible cultural inspiration without restrictions
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import re

# Import core types (inward dependencies only)
from ...enums.culture_types import (
    CultureAuthenticityLevel,
    CultureCreativityLevel,
    CultureComplexityLevel,
    CultureSourceType,
    CultureNamingStructure,
    CultureGenderSystem,
    CultureLinguisticFamily,
    CultureTemporalPeriod
)
from ...exceptions.culture import (
    CultureTemplateError,
    CultureValidationError
)


class PromptType(Enum):
    """Types of culture generation prompts."""
    BASE_GENERATION = "base_generation"
    ENHANCEMENT = "enhancement"
    VALIDATION = "validation"
    EXPANSION = "expansion"
    REFINEMENT = "refinement"
    CONTEXTUAL = "contextual"
    EDUCATIONAL = "educational"


class PromptStyle(Enum):
    """Prompt communication styles."""
    ACADEMIC = "academic"
    CONVERSATIONAL = "conversational"
    INSTRUCTIONAL = "instructional"
    CREATIVE = "creative"
    ANALYTICAL = "analytical"


@dataclass(frozen=True)
class PromptTemplate:
    """
    Immutable prompt template structure.
    
    Represents a complete prompt template with metadata
    for culturally sensitive AI generation.
    """
    name: str
    template: str
    prompt_type: PromptType
    style: PromptStyle
    required_variables: List[str]
    optional_variables: List[str] = field(default_factory=list)
    authenticity_focus: CultureAuthenticityLevel = CultureAuthenticityLevel.MODERATE
    cultural_sensitivity_notes: List[str] = field(default_factory=list)
    educational_objectives: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate template structure on creation."""
        if not self.name or not self.name.strip():
            raise CultureTemplateError("Template name cannot be empty")
        
        if not self.template or not self.template.strip():
            raise CultureTemplateError("Template content cannot be empty")
        
        # Validate that required variables are present in template
        for var in self.required_variables:
            if f"{{{var}}}" not in self.template:
                raise CultureTemplateError(f"Required variable '{var}' not found in template")


class CulturePromptTemplates:
    """
    Creative culture prompt template system for character generation.
    
    Provides static methods and immutable templates optimized for
    character background creation and creative storytelling.
    
    Philosophy: Enable creativity, support character generation,
    provide constructive enhancement rather than restrictive validation.
    """
    
    # ============================================================================
    # CHARACTER GENERATION FOCUSED TEMPLATES
    # ============================================================================
    
    CHARACTER_CULTURE_PROMPT = PromptTemplate(
        name="character_culture_generation",
        template="""You are a creative worldbuilding assistant specializing in character background cultures.
Your task is to generate inspiring cultural material for tabletop gaming character creation.

**Cultural Inspiration:** {cultural_reference}
**Creative Freedom Level:** {creativity_level}
**Character Focus:** {character_focus}

**Creative Guidelines:**
- Prioritize character generation potential over historical accuracy
- Create names and elements that inspire diverse character concepts
- Focus on gaming utility and creative storytelling
- Embrace creative interpretation and fantasy adaptation
- Make everything usable for character backgrounds

**Character-Focused Output:**
Please provide the following sections optimized for character creation:

**Culture Name:** [An inspiring name that sparks character ideas]

**Character Background Hook:** [2-3 sentences describing how characters from this culture might be motivated, what drives them, or what makes them interesting]

**Male Names:** [Provide {min_male_names} creative male names that work well for various character archetypes]

**Female Names:** [Provide {min_female_names} creative female names that work well for various character archetypes]

**Family Names:** [Provide {min_family_names} family/clan names that suggest character history]

**Titles and Epithets:** [Provide {min_titles} titles, ranks, or epithets that characters might earn or inherit]

**Character Inspiration Elements:** [Cultural traits, values, or practices that create interesting character motivations and backgrounds]

**Gaming Notes:** [Practical tips for players creating characters from this culture]

Remember: This is for creative character generation. Prioritize inspiration, playability, and character potential over rigid authenticity. Make it fun and usable!""",
        prompt_type=PromptType.BASE_GENERATION,
        style=PromptStyle.CREATIVE,
        required_variables=[
            "cultural_reference", "creativity_level", "character_focus",
            "min_male_names", "min_female_names", "min_family_names", "min_titles"
        ],
        authenticity_focus=CultureAuthenticityLevel.CREATIVE,
        cultural_sensitivity_notes=[
            "Focuses on creative character potential",
            "Balances inspiration with respectful representation",
            "Prioritizes gaming utility over academic accuracy"
        ],
        educational_objectives=[
            "Character background development",
            "Creative storytelling inspiration",
            "Gaming table usability",
            "Diverse character concept support"
        ]
    )
    
    FANTASY_CULTURE_PROMPT = PromptTemplate(
        name="fantasy_culture_generation", 
        template="""Create an imaginative fantasy culture for character generation in tabletop gaming.

**Fantasy Concept:** {cultural_reference}
**Creative Approach:** Maximum creative freedom - this can be completely original!

**Fantasy Culture Creation:**
Feel free to:
- Invent entirely new cultural concepts
- Blend multiple inspirations creatively
- Create unique naming patterns and sounds
- Design culture specifically for interesting characters
- Ignore real-world limitations - this is fantasy!

**Output for Character Creation:**
**Culture Name:** [Something evocative and memorable]

**Core Character Traits:** [What makes characters from this culture unique and interesting?]

**Male Names:** [Generate {min_male_names} names that sound cool and are easy to pronounce at the gaming table]

**Female Names:** [Generate {min_female_names} names that sound cool and are easy to pronounce at the gaming table]

**Family/Clan Names:** [Generate {min_family_names} names that suggest character history and connections]

**Titles and Honors:** [Generate {min_titles} titles that characters might aspire to or inherit]

**Character Background Elements:** [Cultural practices, beliefs, or traditions that create character motivations and story hooks]

**Player Character Ideas:** [3-5 example character concepts that would fit this culture]

Focus on making everything usable, inspiring, and fun for character creation!""",
        prompt_type=PromptType.BASE_GENERATION,
        style=PromptStyle.CREATIVE,
        required_variables=[
            "cultural_reference", "min_male_names", "min_female_names", 
            "min_family_names", "min_titles"
        ],
        authenticity_focus=CultureAuthenticityLevel.FANTASY,
        cultural_sensitivity_notes=[
            "Maximum creative freedom for fantasy settings",
            "Focuses entirely on character generation utility",
            "No authenticity constraints - pure creativity"
        ],
        educational_objectives=[
            "Creative worldbuilding skills",
            "Character concept development", 
            "Fantasy gaming enhancement",
            "Storytelling inspiration"
        ]
    )
    
    QUICK_CULTURE_PROMPT = PromptTemplate(
        name="quick_character_culture",
        template="""Quick culture generation for immediate character creation needs.

**Culture Concept:** {cultural_reference}

Generate a simple but usable culture for character backgrounds:

**Culture Name:** [Keep it simple and memorable]

**Character Hook:** [One sentence: what makes characters from this culture interesting?]

**Names:**
- **Male:** {min_male_names} names (easy to pronounce, good for characters)
- **Female:** {min_female_names} names (easy to pronounce, good for characters)  
- **Family:** {min_family_names} surnames/clan names
- **Titles:** {min_titles} ranks/titles characters might have

**Quick Background:** [2-3 bullet points about the culture that help with character creation]

Keep it simple, usable, and character-focused!""",
        prompt_type=PromptType.BASE_GENERATION,
        style=PromptStyle.CONVERSATIONAL,
        required_variables=[
            "cultural_reference", "min_male_names", "min_female_names",
            "min_family_names", "min_titles"
        ],
        authenticity_focus=CultureAuthenticityLevel.MODERATE,
        cultural_sensitivity_notes=[
            "Streamlined for immediate use",
            "Balances simplicity with creativity"
        ],
        educational_objectives=[
            "Rapid character creation support",
            "Gaming table efficiency"
        ]
    )
    
    # ============================================================================
    # CHARACTER ENHANCEMENT TEMPLATES
    # ============================================================================
    
    CHARACTER_ENHANCEMENT_PROMPTS = {
        "expand_character_names": PromptTemplate(
            name="expand_character_names",
            template="""Expand the name options for this culture to support more diverse character creation.

**Existing Culture:**
{existing_culture_data}

**Enhancement Goal:** Add {additional_count} more names to {target_categories} that:
- Work well for different character archetypes
- Are memorable and pronounceable at the gaming table
- Maintain consistency with existing naming style
- Inspire diverse character personalities

**Character Archetype Considerations:**
- Strong warrior types
- Clever rogues/scouts  
- Wise magic users
- Charismatic leaders
- Mysterious outsiders

Generate names that support these and other character concepts while fitting the culture's established style.

Format as clear lists, ready for character creation use.""",
            prompt_type=PromptType.ENHANCEMENT,
            style=PromptStyle.CREATIVE,
            required_variables=[
                "existing_culture_data", "additional_count", "target_categories"
            ],
            authenticity_focus=CultureAuthenticityLevel.CREATIVE,
            cultural_sensitivity_notes=[
                "Focuses on character archetype support",
                "Prioritizes gaming utility over linguistic accuracy"
            ],
            educational_objectives=[
                "Character diversity support",
                "Gaming table usability",
                "Creative name generation"
            ]
        ),
        
        "add_character_hooks": PromptTemplate(
            name="add_character_background_hooks",
            template="""Enhance this culture with additional character background elements.

**Current Culture:**
{existing_culture_data}

**Enhancement Focus:** Add character-generation elements:

1. **Character Motivations:** What drives characters from this culture?
2. **Background Professions:** What jobs/roles do people have?
3. **Cultural Conflicts:** What tensions create character story hooks?
4. **Coming of Age:** How do young people prove themselves?
5. **Cultural Secrets:** What mysteries might characters uncover?
6. **Character Relationships:** How do family/clan ties affect characters?

**Goal:** Give players rich material for creating interesting character backgrounds and motivations.

Focus on elements that create story opportunities and character development rather than academic cultural details.""",
            prompt_type=PromptType.ENHANCEMENT,
            style=PromptStyle.CREATIVE,
            required_variables=["existing_culture_data"],
            authenticity_focus=CultureAuthenticityLevel.CREATIVE,
            cultural_sensitivity_notes=[
                "Emphasizes character story potential",
                "Focuses on gaming narrative utility"
            ],
            educational_objectives=[
                "Character background development",
                "Storytelling enhancement",
                "Gaming narrative support"
            ]
        )
    }
    
    # ============================================================================
    # CREATIVE OPTIMIZATION TEMPLATES
    # ============================================================================
    
    CREATIVE_OPTIMIZATION_PROMPTS = {
        "optimize_for_gaming": PromptTemplate(
            name="optimize_culture_for_gaming",
            template="""Optimize this culture for better tabletop gaming use while maintaining its character.

**Culture to Optimize:**
{culture_data}

**Gaming Optimization Goals:**
1. **Name Accessibility:** Ensure names are pronounceable and memorable
2. **Character Variety:** Support diverse character concepts
3. **Quick Reference:** Make information easy to use during play
4. **Story Integration:** Enhance plot hook potential
5. **Player Inspiration:** Maximize character creation appeal

**Provide:**
- **Gaming-Friendly Names:** Improved versions of complex names
- **Character Archetypes:** Types of characters this culture supports well
- **Quick Reference Summary:** Key culture points for easy table use
- **Story Hook Ideas:** Plot elements characters might be involved in
- **Player Tips:** Advice for creating characters from this culture

Focus on practical gaming utility while keeping the culture's inspirational core.""",
            prompt_type=PromptType.REFINEMENT,
            style=PromptStyle.INSTRUCTIONAL,
            required_variables=["culture_data"],
            authenticity_focus=CultureAuthenticityLevel.MODERATE,
            cultural_sensitivity_notes=[
                "Balances authenticity with gaming practicality",
                "Maintains cultural inspiration while improving usability"
            ],
            educational_objectives=[
                "Gaming table optimization",
                "Player experience enhancement",
                "Practical culture application"
            ]
        )
    }

# Update utility functions to match creative approach
def build_character_culture_prompt(
    cultural_inspiration: str,
    creativity_level: CultureCreativityLevel = CultureCreativityLevel.CREATIVE,
    character_focus: str = "diverse archetypes",
    min_names_per_category: int = 15
) -> str:
    """
    Build a character-focused culture generation prompt.
    
    Optimized for character creation rather than cultural authenticity.
    
    Args:
        cultural_inspiration: Loose inspiration for the culture (can be anything!)
        creativity_level: How creative/original to be
        character_focus: What types of characters to support
        min_names_per_category: Minimum names per category
        
    Returns:
        Character-optimized prompt string
    """
    # Always use character-focused template
    template = CulturePromptTemplates.CHARACTER_CULTURE_PROMPT
    
    variables = {
        'cultural_reference': cultural_inspiration,
        'creativity_level': creativity_level.name.replace('_', ' ').title(),
        'character_focus': character_focus,
        'min_male_names': min_names_per_category,
        'min_female_names': min_names_per_category,
        'min_family_names': max(10, min_names_per_category - 5),
        'min_titles': max(8, min_names_per_category // 2)
    }
    
    return CulturePromptTemplates.build_prompt(template, variables)

def build_fantasy_culture_prompt(
    fantasy_concept: str,
    min_names_per_category: int = 12
) -> str:
    """
    Build a fantasy culture prompt with maximum creative freedom.
    
    No authenticity constraints - pure creative character support.
    """
    template = CulturePromptTemplates.FANTASY_CULTURE_PROMPT
    
    variables = {
        'cultural_reference': fantasy_concept,
        'min_male_names': min_names_per_category,
        'min_female_names': min_names_per_category,
        'min_family_names': max(8, min_names_per_category - 4),
        'min_titles': max(6, min_names_per_category // 2)
    }
    
    return CulturePromptTemplates.build_prompt(template, variables)

def build_quick_culture_prompt(
    culture_concept: str,
    min_names_per_category: int = 8
) -> str:
    """
    Build a quick culture prompt for immediate character creation.
    
    Streamlined for rapid use at the gaming table.
    """
    template = CulturePromptTemplates.QUICK_CULTURE_PROMPT
    
    variables = {
        'cultural_reference': culture_concept,
        'min_male_names': min_names_per_category,
        'min_female_names': min_names_per_category,
        'min_family_names': max(6, min_names_per_category - 2),
        'min_titles': max(4, min_names_per_category // 2)
    }
    
    return CulturePromptTemplates.build_prompt(template, variables)

# Updated philosophy alignment
CREATIVE_VALIDATION_ALIGNMENT = {
    "philosophy": "Enable creativity rather than restrict it",
    "implementation": "Character-focused templates with creative freedom",
    "focus": "Character generation support and enhancement", 
    "template_approach": "Inspiration over authenticity",
    "validation_style": "Constructive suggestions over rigid requirements",
    "enhancement_focus": "Gaming utility and character potential",
    "usability_threshold": "Almost all cultures are usable for character generation",
    "template_compliance": "All templates prioritize character creation needs"
}