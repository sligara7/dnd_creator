"""
LLM Prompt Templates for D&D Creative Content Generation.

This module contains all prompt templates used for generating D&D content through
Large Language Models. These prompts enforce D&D 5e/2024 rule compliance while
enabling creative freedom in character and content generation.

Following Clean Architecture principles, these prompts are:
- Infrastructure-independent (work with any LLM provider)
- Focused on D&D business rules and creative requirements
- Modular and reusable across different generation contexts
- Aligned with the interactive character creation workflow
"""

from typing import Dict, List, Any, Optional
from ..enums.creativity_levels import CreativityLevel, GenerationMethod, ContentComplexity
from ..enums.content_types import ContentType, ThemeCategory
from ..enums.balance_levels import BalanceLevel
from ..enums.progression_types import ProgressionType, ThematicTier


# ============ CHARACTER CONCEPT GENERATION PROMPTS ============

# Initial character concept prompts for different creativity levels
CHARACTER_CONCEPT_PROMPTS: Dict[CreativityLevel, str] = {
    CreativityLevel.LOW: """
You are a D&D 5e/2024 character creation assistant. Create a character concept based on this user input: "{user_input}"

REQUIREMENTS:
- Use only official D&D 5e/2024 content (PHB, DMG, MM, Xanathar's, Tasha's)
- Follow standard class/species combinations
- Maintain traditional D&D themes and archetypes
- Ensure mechanical optimization and viability
- No homebrew or experimental content

RESPONSE FORMAT (JSON):
{{
    "name": "Character name",
    "species": "Official species name",
    "character_class": "Official class name", 
    "background": "Official background name",
    "concept_summary": "2-3 sentence character concept",
    "mechanical_theme": "Combat role and party function",
    "personality_hooks": ["3-4 personality traits"],
    "story_connections": ["2-3 background story elements"],
    "optimization_notes": "Why this build is mechanically sound"
}}

Focus on proven, effective combinations that new players can easily understand and play.
""",

    CreativityLevel.MEDIUM: """
You are a D&D 5e/2024 creative character designer. Develop an interesting character concept from: "{user_input}"

REQUIREMENTS:
- Blend official content with creative interpretations
- Consider unusual but viable class/species combinations  
- Balance mechanical effectiveness with thematic uniqueness
- Allow minor reflavoring of official content
- Maintain D&D 5e/2024 rule compatibility

RESPONSE FORMAT (JSON):
{{
    "name": "Character name with thematic significance",
    "species": "Species name (with potential reflavoring notes)",
    "character_class": "Class name (with potential subclass suggestion)",
    "background": "Background (possibly customized)",
    "concept_summary": "Compelling 3-4 sentence character concept",
    "unique_angle": "What makes this character distinctive", 
    "mechanical_synergies": ["2-3 mechanical synergies to explore"],
    "thematic_elements": ["3-4 thematic hooks and connections"],
    "potential_story_arcs": ["2-3 character development directions"],
    "reflavoring_suggestions": ["Optional content reflavoring ideas"]
}}

Create something memorable while maintaining mechanical viability and D&D authenticity.
""",

    CreativityLevel.HIGH: """
You are a master D&D content creator specializing in innovative character concepts. Transform this input into something extraordinary: "{user_input}"

REQUIREMENTS:
- Push creative boundaries while respecting D&D 5e/2024 framework
- Consider custom content that enhances rather than breaks the game
- Blend multiple themes and archetypes in unique ways
- Suggest minor homebrew elements if they serve the concept
- Maintain game balance and table compatibility

RESPONSE FORMAT (JSON):
{{
    "name": "Evocative name that captures the concept's essence",
    "species": "Species (official or well-balanced custom)",
    "character_class": "Class (possibly multiclass or variant)",
    "background": "Background (customized or newly designed)",
    "concept_summary": "Rich, detailed character concept (4-5 sentences)",
    "innovative_elements": ["What makes this concept groundbreaking"],
    "custom_content_needed": ["Required homebrew elements with balance notes"],
    "mechanical_complexity": "How complex this build is to play",
    "thematic_layers": ["Multiple thematic elements woven together"],
    "narrative_potential": ["Rich storytelling opportunities"],
    "table_integration": "How this fits with typical D&D campaigns",
    "evolution_path": "How the character grows and changes"
}}

Create something that inspires both player and DM while remaining fundamentally D&D.
""",

    CreativityLevel.EXPERIMENTAL: """
You are an experimental D&D designer pushing the absolute boundaries of creative character design. Revolutionize this concept: "{user_input}"

REQUIREMENTS:
- Explore uncharted territory in D&D character creation
- Suggest bold homebrew elements that expand the game
- Challenge traditional assumptions while maintaining core D&D DNA
- Create something that could inspire official content
- Balance innovation with playability

⚠️ EXPERIMENTAL CONTENT WARNING: This will include untested homebrew elements.

RESPONSE FORMAT (JSON):
{{
    "name": "Name that embodies revolutionary concept",
    "core_identity": "What fundamentally defines this character",
    "species_design": "Species (extensively modified or entirely new)",
    "class_framework": "Class structure (hybrid, variant, or new)",
    "background_narrative": "Rich background that supports the concept",
    "concept_manifesto": "Detailed explanation of the revolutionary concept",
    "experimental_mechanics": ["Cutting-edge homebrew mechanics"],
    "balance_considerations": ["How experimental elements stay balanced"],
    "implementation_challenges": ["What makes this difficult to realize"],
    "inspiration_sources": ["What inspired this boundary-pushing design"],
    "playtesting_priorities": ["Key areas that need testing"],
    "dm_guidance": "How DMs can implement this safely",
    "player_expectations": "What players should know before playing this"
}}

Break new ground while honoring what makes D&D special.
"""
}

# ============ CONTENT GENERATION PROMPTS ============

# Prompts for generating specific types of custom content
CONTENT_GENERATION_PROMPTS: Dict[ContentType, Dict[str, str]] = {
    ContentType.SPECIES: {
        "base_prompt": """
Generate a custom D&D 5e/2024 species based on these requirements:

CONCEPT: {concept_description}
THEME CATEGORIES: {theme_categories}
BALANCE LEVEL: {balance_level}
POWER TIER: {power_tier}

DESIGN REQUIREMENTS:
- Follow D&D 2024 species structure (no more ASI, flexible ability scores)
- 2-4 meaningful species traits (including at least 1 "ribbon" flavor trait)
- Appropriate for {power_tier} tier play
- Thematically consistent with: {theme_categories}
- Balance level: {balance_level}

RESPONSE FORMAT (JSON):
{{
    "name": "Species name",
    "creature_type": "Humanoid/Fey/etc.",
    "size": "Size category", 
    "speed": "Base speed and type",
    "life_span": "Typical lifespan",
    "alignment_tendency": "Typical alignment (not restrictive)",
    "languages": ["Known languages"],
    "traits": [
        {{
            "name": "Trait name",
            "description": "What the trait does",
            "mechanics": "Specific mechanical effects",
            "trait_type": "combat/utility/ribbon"
        }}
    ],
    "physical_description": "Appearance and physical characteristics",
    "cultural_notes": "Society, customs, and behavior",
    "naming_conventions": "How they name themselves",
    "balance_analysis": "Power level assessment and justification"
}}
""",
        
        "refinement_prompt": """Based on this feedback: "{user_feedback}", refine the species design while maintaining D&D 5e/2024 compliance and balance."""
    },
    
    ContentType.CHARACTER_CLASS: {
        "base_prompt": """
Design a custom D&D 5e/2024 character class with these specifications:

CONCEPT: {concept_description}
THEME: {primary_theme}
ROLE: {intended_role}
COMPLEXITY: {complexity_level}
BALANCE TARGET: {balance_level}

DESIGN FRAMEWORK:
- Hit die appropriate for role (d6/d8/d10/d12)
- 2 saving throw proficiencies (one strong, one weak)
- Appropriate armor/weapon/tool/skill proficiencies
- 20 levels of progression with meaningful choices
- Subclass selection at level 3 (unless concept requires different level)
- ASI at levels 4, 8, 12, 16, 19
- Capstone feature at level 20

RESPONSE FORMAT (JSON):
{{
    "class_name": "Class name",
    "hit_die": "Hit die type",
    "primary_ability": ["Primary ability scores"],
    "saving_throws": ["Two saving throw proficiencies"],
    "proficiencies": {{
        "armor": ["Armor proficiencies"],
        "weapons": ["Weapon proficiencies"], 
        "tools": ["Tool proficiency options"],
        "skills": ["Skill options and count"]
    }},
    "class_features": [
        {{
            "level": 1,
            "feature_name": "Feature name",
            "description": "What it does",
            "mechanics": "Specific rules"
        }}
    ],
    "subclass_framework": {{
        "selection_level": 3,
        "feature_levels": [3, 7, 15, 18],
        "design_space": "What subclasses can explore"
    }},
    "design_philosophy": "Core design principles",
    "balance_notes": "Power level analysis and justification"
}}
""",
        
        "subclass_prompt": """
Design a subclass for the {parent_class} class:

SUBCLASS CONCEPT: {subclass_concept}
THEME: {theme_focus}
PARENT CLASS: {parent_class}

Provide features for levels {feature_levels} that enhance the base class while maintaining thematic focus.
"""
    },
    
    ContentType.SPELL: {
        "base_prompt": """
Create a custom D&D 5e/2024 spell with these parameters:

CONCEPT: {spell_concept}
SPELL LEVEL: {spell_level} 
SCHOOL: {magic_school}
THEME: {thematic_focus}
BALANCE TARGET: {balance_level}

DESIGN REQUIREMENTS:
- Follow D&D 2024 spell formatting
- Appropriate power level for spell level
- Clear, unambiguous mechanics
- Interesting tactical applications
- Fits thematically with {magic_school} school

RESPONSE FORMAT (JSON):
{{
    "name": "Spell name",
    "level": {spell_level},
    "school": "{magic_school}",
    "casting_time": "Action type required",
    "range": "Range in feet or special",
    "duration": "Duration or instantaneous", 
    "components": "V, S, M components",
    "material_component": "Specific material if needed",
    "description": "Full spell description with mechanics",
    "at_higher_levels": "Upcast effects if applicable",
    "spell_lists": ["Which classes can learn this"],
    "design_notes": "Why this spell is interesting and balanced"
}}

Compare power level to similar level spells like {comparison_spells}.
""",
        
        "cantrip_prompt": """Create a cantrip (0-level spell) that scales with character level but remains balanced for unlimited use."""
    },
    
    ContentType.FEAT: {
        "base_prompt": """
Design a custom D&D 5e/2024 feat with this concept:

CONCEPT: {feat_concept}
FEAT TYPE: {feat_type}
THEME: {thematic_focus}
POWER LEVEL: {power_target}

DESIGN PRINCIPLES:
- Clear mechanical benefit worth a feat selection
- Interesting tactical decisions
- Scales appropriately across levels
- Maintains bounded accuracy principles
- Offers meaningful choice

RESPONSE FORMAT (JSON):
{{
    "name": "Feat name",
    "feat_type": "General/Fighting Style/etc.",
    "prerequisites": ["Requirements if any"],
    "benefits": [
        {{
            "type": "mechanical/asi/utility",
            "description": "What this benefit provides",
            "mechanics": "Specific rules and limitations"
        }}
    ],
    "design_rationale": "Why this feat is interesting and balanced",
    "power_comparison": "How it compares to similar feats",
    "tactical_applications": ["How players might use this strategically"]
}}
""",
        
        "fighting_style_prompt": """Create a new Fighting Style option that provides a distinct combat approach without overshadowing existing styles."""
    }
}

# ============ CHARACTER REFINEMENT PROMPTS ============

CHARACTER_REFINEMENT_PROMPTS: Dict[str, str] = {
    "general_refinement": """
The user wants to refine their character based on this feedback: "{user_feedback}"

CURRENT CHARACTER:
{current_character_json}

REFINEMENT SCOPE: {refinement_areas}

Modify the character while:
- Maintaining D&D 5e/2024 rule compliance
- Preserving the core concept identity
- Addressing the specific feedback
- Keeping mechanical balance
- Improving thematic consistency

Focus changes on: {refinement_areas}
""",
    
    "mechanical_adjustment": """
Adjust the mechanical aspects of this character based on feedback: "{user_feedback}"

Focus on:
- Combat effectiveness and optimization
- Ability score allocation
- Skill and proficiency selections
- Equipment and starting gear
- Multiclass considerations if applicable

Maintain thematic integrity while improving mechanical function.
""",
    
    "thematic_refinement": """
Enhance the thematic and narrative aspects based on: "{user_feedback}"

Focus on:
- Character personality and motivations
- Background story and connections
- Roleplaying hooks and character voice
- Visual description and mannerisms
- Character arc and development potential

Keep mechanical elements stable while enriching the character's story.
""",
    
    "balance_adjustment": """
The character has balance concerns that need addressing: {balance_issues}

User feedback: "{user_feedback}"

Adjust the character to:
- Reduce overpowered elements
- Strengthen underpowered aspects
- Maintain fun and interesting gameplay
- Preserve character concept
- Meet {balance_target} balance standards
"""
}

# ============ PROGRESSION GENERATION PROMPTS ============

PROGRESSION_PROMPTS: Dict[ProgressionType, str] = {
    ProgressionType.SINGLE_CLASS: """
Generate level progression for this single-class character:

CHARACTER: {character_summary}
CLASS: {character_class}
SUBCLASS: {subclass}
LEVELS: {level_range}

For each level, provide:
- Hit points (average)
- New class features gained
- ASI/feat decisions with reasoning
- Spell progression if applicable
- Key tactical changes
- Thematic evolution notes

Focus on natural character growth and mechanical optimization.
""",
    
    ProgressionType.MULTICLASS: """
Design a multiclass progression for this character:

PRIMARY CLASS: {primary_class} (levels {primary_levels})
SECONDARY CLASS: {secondary_class} (levels {secondary_levels})
CONCEPT: {multiclass_concept}
OPTIMIZATION GOAL: {optimization_focus}

Ensure:
- Multiclass requirements are met
- Synergies between classes are utilized
- Progression feels natural and thematic
- No major dead levels or awkward transitions
- Final build achieves the intended concept
""",
    
    ProgressionType.VARIANT: """
Create a variant progression using these rules:

BASE CHARACTER: {character_base}
VARIANT RULES: {variant_rules_used}
SPECIAL CONSIDERATIONS: {special_rules}

Apply variant rules while maintaining:
- Character concept integrity
- Mechanical balance
- Table compatibility
- Clear progression path
"""
}

# ============ THEMATIC EVOLUTION PROMPTS ============

THEMATIC_TIER_PROMPTS: Dict[ThematicTier, str] = {
    ThematicTier.LOCAL_HERO: """
Develop the character's identity as a LOCAL HERO (levels 1-4):

CHARACTER: {character_concept}

Focus on:
- Small-scale adventures and local problems
- Learning basic abilities and finding their place
- Establishing relationships in a community
- Personal growth and skill development
- Simple but meaningful heroic acts

Create progression narrative showing growth from novice to local champion.
""",
    
    ThematicTier.REGIONAL_CHAMPION: """
Evolve the character into a REGIONAL CHAMPION (levels 5-10):

CHARACTER: {character_concept}
PREVIOUS TIER: {local_hero_summary}

Focus on:
- Regional threats and wider influence
- Mastery of signature abilities
- Leadership and reputation building
- Complex moral decisions
- Meaningful impact on larger communities

Show the transition from local hero to regional figure of importance.
""",
    
    ThematicTier.WORLD_SHAPER: """
Transform the character into a WORLD SHAPER (levels 11-16):

CHARACTER: {character_concept}
PREVIOUS DEVELOPMENT: {previous_tier_summary}

Focus on:
- World-spanning adventures and threats
- Legendary abilities and recognition
- Political influence and major decisions
- Shaping the fate of nations or planes
- Becoming a figure of myth and legend

Demonstrate how they've grown to affect the world itself.
""",
    
    ThematicTier.COSMIC_FORCE: """
Ascend the character to COSMIC FORCE status (levels 17-20):

CHARACTER: {character_concept}
JOURNEY SO FAR: {complete_progression_summary}

Focus on:
- Cosmic threats and divine intervention
- Reality-altering powers and influence
- Decisions affecting multiple planes of existence
- Becoming a force of nature or divine champion
- Legacy that will endure beyond mortal life

Show their final evolution into a truly legendary figure.
"""
}

# ============ CONVERSATION FLOW PROMPTS ============

# Prompts for managing the interactive character creation conversation
CONVERSATION_PROMPTS: Dict[str, str] = {
    "welcome": """
Welcome to the D&D Character Creator! I'm here to help you bring your perfect D&D character to life.

Tell me about the character you'd like to create - feel free to include any details from name to species to background, or just share a cool concept you have in mind. I'll help fill in the rest, and then we'll refine it together until it's exactly what you want.

Don't worry about knowing all the rules - I'll handle the mechanical details while keeping your vision at the center. Let's create something amazing!

What kind of character are you imagining?
""",
    
    "concept_clarification": """
I love the direction you're going with "{user_input}"! Let me ask a few questions to make sure I capture your vision perfectly:

{clarifying_questions}

These details will help me create something that really matches what you have in mind.
""",
    
    "presenting_concept": """
Based on your input, I've created this character concept:

{character_concept}

What do you think? Is this capturing what you had in mind, or would you like me to adjust anything? I can modify:
- The mechanical build and optimization
- Thematic elements and personality
- Background story and connections
- Combat role and party function
- Overall power level or complexity

Just let me know what feels right and what you'd like to change!
""",
    
    "refinement_options": """
Great! I can help refine your character. What would you like to focus on?

1. **Mechanical Optimization** - Improve combat effectiveness, ability scores, and build synergy
2. **Thematic Development** - Enhance personality, backstory, and roleplaying elements  
3. **Balance Adjustment** - Fine-tune power level and ensure fair play
4. **Progression Planning** - Map out how the character grows through levels
5. **Custom Content** - Add unique homebrew elements to make them special

Or just tell me specifically what you'd like to change - I'm here to make this character perfect for you!
""",
    
    "ready_for_generation": """
Perfect! Your character concept is ready. Now I can generate:

🎭 **Full Character Sheets** - Complete character for levels 1-20
📊 **Progression Guide** - How they develop and grow
⚔️ **Combat Tactics** - How to play them effectively  
📝 **Roleplay Guide** - Personality, voice, and story hooks
🎲 **Custom Content** - Any homebrew elements they need
📋 **Export Options** - Character sheets for your VTT of choice

What would you like me to create first?
""",
    
    "export_ready": """
Your character is complete! Here are your export options:

📋 **Character Sheets**: D&D Beyond, Roll20, Fantasy Grounds, PDF
📊 **Progression Charts**: Level-by-level advancement guide
⚔️ **Quick Reference**: Combat actions and key abilities
🎭 **Roleplay Guide**: Personality, voice, and story hooks
🏠 **Homebrew Content**: Custom elements for your DM

Which format would be most helpful for your game?
"""
}

# ============ BALANCE ANALYSIS PROMPTS ============

BALANCE_ANALYSIS_PROMPTS: Dict[BalanceLevel, str] = {
    BalanceLevel.CONSERVATIVE: """
Analyze this content for CONSERVATIVE balance standards:

CONTENT: {content_data}
TYPE: {content_type}

Apply strict balance criteria:
- Must not exceed official content power levels
- No edge cases or complex interactions
- Straightforward, predictable mechanics
- Suitable for new players and DMs
- Errs on the side of underpowered rather than overpowered

Provide detailed power level analysis and adjustment recommendations.
""",
    
    BalanceLevel.STANDARD: """
Evaluate this content using STANDARD balance guidelines:

CONTENT: {content_data}
TYPE: {content_type}

Apply typical D&D balance standards:
- Comparable to official content in power level
- Reasonable complexity and interaction
- Fair for most table environments
- Interesting without being disruptive
- Balances power with appropriate limitations

Compare to similar official content and assess overall balance.
""",
    
    BalanceLevel.AGGRESSIVE: """
Assess this content for AGGRESSIVE balance standards:

CONTENT: {content_data}
TYPE: {content_type}

Push power level boundaries while maintaining game integrity:
- Can exceed typical power levels if justified
- Complex interactions allowed
- Requires experienced players/DMs
- Innovative mechanics encouraged
- Higher risk/reward ratios acceptable

Ensure it's powerful but not game-breaking.
"""
}

# ============ ERROR HANDLING PROMPTS ============

ERROR_HANDLING_PROMPTS: Dict[str, str] = {
    "invalid_concept": """
I'm having trouble understanding that character concept. Could you help me by providing:

- A basic idea of what you want (fighter, wizard, sneaky type, etc.)
- Any specific D&D elements you're interested in
- The general feel or theme you're going for
- What role you want them to play in a party

Even something simple like "I want a tough warrior" or "sneaky magic user" gives me a great starting point!
""",
    
    "balance_concerns": """
I've created your character, but there are some balance concerns that might cause issues at most tables:

{balance_issues}

I can:
1. **Auto-adjust** - Let me tone it down to standard power levels
2. **Explain the issues** - Help you understand what might be problematic  
3. **Provide alternatives** - Suggest different approaches to the concept
4. **Keep as-is** - Mark it as high-power content with warnings

What would you prefer?
""",
    
    "generation_failed": """
I encountered an issue generating that content. This might be because:

- The concept conflicts with D&D rules in complex ways
- The requirements are contradictory
- The request is outside my design capabilities

Could you try:
- Simplifying the concept
- Focusing on one specific aspect
- Providing more context about what you want

I'm here to help work through any creative challenges!
"""
}

# ============ HELPER FUNCTIONS FOR PROMPT MANAGEMENT ============

def get_character_concept_prompt(creativity_level: CreativityLevel, user_input: str) -> str:
    """Get character concept generation prompt for specified creativity level."""
    template = CHARACTER_CONCEPT_PROMPTS.get(creativity_level, CHARACTER_CONCEPT_PROMPTS[CreativityLevel.MEDIUM])
    return template.format(user_input=user_input)

def get_content_generation_prompt(content_type: ContentType, 
                                 prompt_type: str = "base_prompt",
                                 **kwargs) -> str:
    """Get content generation prompt for specified content type."""
    prompts = CONTENT_GENERATION_PROMPTS.get(content_type, {})
    template = prompts.get(prompt_type, "")
    
    if template:
        return template.format(**kwargs)
    return f"Generate {content_type.value} content based on: {kwargs}"

def get_refinement_prompt(refinement_type: str, **kwargs) -> str:
    """Get character refinement prompt for specified refinement type."""
    template = CHARACTER_REFINEMENT_PROMPTS.get(refinement_type, CHARACTER_REFINEMENT_PROMPTS["general_refinement"])
    return template.format(**kwargs)

def get_progression_prompt(progression_type: ProgressionType, **kwargs) -> str:
    """Get progression generation prompt for specified progression type."""
    template = PROGRESSION_PROMPTS.get(progression_type, PROGRESSION_PROMPTS[ProgressionType.SINGLE_CLASS])
    return template.format(**kwargs)

def get_thematic_tier_prompt(tier: ThematicTier, **kwargs) -> str:
    """Get thematic development prompt for specified tier."""
    template = THEMATIC_TIER_PROMPTS.get(tier, "")
    return template.format(**kwargs) if template else ""

def get_conversation_prompt(conversation_type: str, **kwargs) -> str:
    """Get conversation flow prompt for specified interaction type."""
    template = CONVERSATION_PROMPTS.get(conversation_type, "")
    return template.format(**kwargs) if template else ""

def get_balance_analysis_prompt(balance_level: BalanceLevel, **kwargs) -> str:
    """Get balance analysis prompt for specified balance level."""
    template = BALANCE_ANALYSIS_PROMPTS.get(balance_level, BALANCE_ANALYSIS_PROMPTS[BalanceLevel.STANDARD])
    return template.format(**kwargs)

def get_error_handling_prompt(error_type: str, **kwargs) -> str:
    """Get error handling prompt for specified error type."""
    template = ERROR_HANDLING_PROMPTS.get(error_type, "I encountered an issue. Could you please clarify your request?")
    return template.format(**kwargs)

# ============ PROMPT VALIDATION HELPERS ============

def validate_prompt_parameters(prompt_template: str, provided_params: Dict[str, Any]) -> List[str]:
    """
    Validate that all required parameters are provided for a prompt template.
    
    Args:
        prompt_template: The prompt template string
        provided_params: Dictionary of provided parameters
        
    Returns:
        List of missing required parameters
    """
    import re
    
    # Find all parameters in the template (format: {parameter_name})
    required_params = set(re.findall(r'\{([^}]+)\}', prompt_template))
    provided_param_names = set(provided_params.keys())
    
    missing_params = required_params - provided_param_names
    return list(missing_params)

def get_prompt_metadata() -> Dict[str, Dict[str, Any]]:
    """Get metadata about all available prompts."""
    return {
        "character_concept": {
            "creativity_levels": list(CHARACTER_CONCEPT_PROMPTS.keys()),
            "required_params": ["user_input"],
            "description": "Generate initial character concepts"
        },
        "content_generation": {
            "content_types": list(CONTENT_GENERATION_PROMPTS.keys()),
            "prompt_types": ["base_prompt", "refinement_prompt"],
            "description": "Generate custom D&D content"
        },
        "character_refinement": {
            "refinement_types": list(CHARACTER_REFINEMENT_PROMPTS.keys()),
            "description": "Refine existing characters based on feedback"
        },
        "progression": {
            "progression_types": list(PROGRESSION_PROMPTS.keys()),
            "description": "Generate character level progressions"
        },
        "thematic_tiers": {
            "tier_types": list(THEMATIC_TIER_PROMPTS.keys()),
            "description": "Develop character themes across tiers"
        },
        "conversation_flow": {
            "conversation_types": list(CONVERSATION_PROMPTS.keys()),
            "description": "Interactive character creation conversation"
        },
        "balance_analysis": {
            "balance_levels": list(BALANCE_ANALYSIS_PROMPTS.keys()),
            "description": "Analyze content balance and power levels"
        },
        "error_handling": {
            "error_types": list(ERROR_HANDLING_PROMPTS.keys()),
            "description": "Handle errors and edge cases gracefully"
        }
    }

# ============ MODULE METADATA ============

__version__ = '2.0.0'
__description__ = 'LLM prompt templates for D&D Creative Content Framework'
__author__ = 'D&D Character Creator Backend6'

# Clean Architecture compliance metadata
CLEAN_ARCHITECTURE_COMPLIANCE = {
    "layer": "core/constants",
    "dependencies": ["core/enums"],
    "dependents": ["domain/services", "infrastructure/llm_providers"],
    "infrastructure_independent": True,
    "focuses_on": "D&D business rules and creative requirements"
}

# Prompt template statistics
PROMPT_STATISTICS = {
    "total_templates": (
        len(CHARACTER_CONCEPT_PROMPTS) +
        sum(len(prompts) for prompts in CONTENT_GENERATION_PROMPTS.values()) +
        len(CHARACTER_REFINEMENT_PROMPTS) +
        len(PROGRESSION_PROMPTS) +
        len(THEMATIC_TIER_PROMPTS) +
        len(CONVERSATION_PROMPTS) +
        len(BALANCE_ANALYSIS_PROMPTS) +
        len(ERROR_HANDLING_PROMPTS)
    ),
    "creativity_levels_supported": len(CHARACTER_CONCEPT_PROMPTS),
    "content_types_supported": len(CONTENT_GENERATION_PROMPTS),
    "conversation_states_handled": len(CONVERSATION_PROMPTS)
}