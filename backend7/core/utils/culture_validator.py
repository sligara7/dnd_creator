"""
Essential D&D Culture Validator Utilities

Streamlined culture validation utilities following backend7 architecture.
Based on crude_functional.py patterns and essential-only philosophy.
Maintains overarching functionality of crude_functional.py approach.

Culture validation augments character creation with helpful guidance while preserving creative freedom.
Validation provides suggestions and warnings, never prevents character choices.
"""

from typing import Dict, List, Tuple, Optional, Any, Union
from core.enums import (
    CultureType, LanguageFamily, SocialStructure, ReligiousTradition,
    ArtisticTradition, SettlementType, CreativityLevel
)

# ============ CORE CULTURE VALIDATION ============

def validate_culture_choice(
    culture_data: Dict[str, Any],
    character_data: Dict[str, Any] = None
) -> Tuple[bool, List[str], List[str]]:
    """Validate culture choice - crude_functional.py style helpful validation."""
    if not culture_data:
        return True, [], ["No culture data provided - using flexible defaults"]
    
    # Always valid - culture never restricts, only suggests
    is_valid = True
    suggestions = []
    notes = []
    
    # Basic structure validation
    required_fields = ["type", "structure", "settlement"]
    missing_fields = [field for field in required_fields if field not in culture_data]
    
    if missing_fields:
        notes.append(f"Consider adding: {', '.join(missing_fields)} for richer culture")
    
    # Get enhancement suggestions
    culture_type = culture_data.get("type", "mixed")
    suggestions.extend(get_culture_enhancement_suggestions(culture_type))
    
    # Character-specific suggestions
    if character_data:
        suggestions.extend(get_character_culture_suggestions(culture_data, character_data))
    
    # Always remind about creative freedom
    notes.append("Culture elements are suggestions - adapt freely to your vision")
    
    return is_valid, suggestions, notes

def validate_cultural_compatibility(
    race: str,
    culture_type: str,
    background: str = None,
    character_class: str = None
) -> Tuple[bool, List[str], List[str]]:
    """Validate cultural compatibility - crude_functional.py flexible validation."""
    if not race or not culture_type:
        return True, [], ["Missing race or culture - all combinations welcome"]
    
    # Always compatible - provide enhancement suggestions instead
    is_compatible = True
    enhancements = []
    notes = []
    
    # Race-culture enhancement opportunities
    race_culture_synergies = get_race_culture_synergies(race.lower(), culture_type.lower())
    if race_culture_synergies:
        enhancements.extend(race_culture_synergies)
    
    # Background-culture synergies
    if background:
        background_synergies = get_background_culture_synergies(background.lower(), culture_type.lower())
        if background_synergies:
            enhancements.extend(background_synergies)
    
    # Class-culture synergies
    if character_class:
        class_synergies = get_class_culture_synergies(character_class.lower(), culture_type.lower())
        if class_synergies:
            enhancements.extend(class_synergies)
    
    # General compatibility notes
    notes.append(f"{race.title()} characters can thrive in {culture_type} culture")
    notes.append("Every race-culture combination offers unique roleplay opportunities")
    
    return is_compatible, enhancements, notes

def validate_language_choices(
    culture_data: Dict[str, Any],
    chosen_languages: List[str]
) -> Tuple[bool, List[str], List[str]]:
    """Validate language choices - crude_functional.py supportive validation."""
    if not culture_data or not chosen_languages:
        return True, [], ["Language choices are flexible - choose what fits your character"]
    
    is_valid = True
    suggestions = []
    notes = []
    
    cultural_languages = culture_data.get("languages", ["common"])
    culture_type = culture_data.get("type", "mixed")
    
    # Suggest cultural languages as enhancements, not requirements
    for lang in cultural_languages:
        if lang not in chosen_languages:
            suggestions.append(f"Consider {lang} to connect with {culture_type} culture")
    
    # Validate chosen languages are reasonable
    for lang in chosen_languages:
        if lang.lower() == "common":
            notes.append("Common language enables broad communication")
        elif is_exotic_language(lang):
            suggestions.append(f"Consider how you learned {lang} - adds character depth")
    
    # Always supportive
    notes.append("Language choices reflect your character's background and travels")
    
    return is_valid, suggestions, notes

# ============ ENHANCEMENT SUGGESTION UTILITIES ============

def get_culture_enhancement_suggestions(culture_type: str) -> List[str]:
    """Get culture enhancement suggestions - crude_functional.py helpful guidance."""
    if not culture_type:
        return []
    
    enhancement_suggestions = {
        "urban": [
            "explore_guild_connections",
            "consider_district_specializations",
            "develop_political_awareness",
            "embrace_cultural_diversity"
        ],
        "rural": [
            "connect_with_natural_cycles",
            "develop_community_relationships",
            "explore_folk_traditions",
            "appreciate_simple_pleasures"
        ],
        "nomadic": [
            "embrace_freedom_of_movement",
            "develop_survival_instincts",
            "preserve_oral_traditions",
            "navigate_cultural_exchanges"
        ],
        "coastal": [
            "understand_maritime_culture",
            "respect_sea_and_storm",
            "develop_trading_relationships",
            "appreciate_tidal_rhythms"
        ],
        "mountain": [
            "honor_clan_traditions",
            "respect_ancient_stonework",
            "develop_underground_knowledge",
            "value_craftsmanship"
        ],
        "forest": [
            "connect_with_nature_spirits",
            "understand_woodland_cycles",
            "preserve_natural_balance",
            "develop_tracking_awareness"
        ]
    }
    
    return enhancement_suggestions.get(culture_type.lower(), ["explore_unique_cultural_aspects"])

def get_race_culture_synergies(race: str, culture_type: str) -> List[str]:
    """Get race-culture synergies - crude_functional.py positive combinations."""
    synergies = {
        ("elf", "forest"): ["embrace_fey_connections", "extend_natural_lifespans", "perfect_woodland_skills"],
        ("elf", "urban"): ["bring_long_perspective", "bridge_old_and_new", "add_artistic_refinement"],
        ("dwarf", "mountain"): ["honor_ancestral_halls", "master_stone_and_metal", "preserve_clan_history"],
        ("dwarf", "urban"): ["establish_craft_guilds", "build_lasting_structures", "create_quality_goods"],
        ("human", "any"): ["adapt_quickly", "bridge_cultural_gaps", "lead_through_versatility"],
        ("halfling", "rural"): ["create_cozy_communities", "celebrate_comfort_and_food", "maintain_peaceful_relations"],
        ("halfling", "urban"): ["build_neighborhood_networks", "create_homey_spaces", "bridge_social_classes"],
        ("dragonborn", "any"): ["overcome_prejudice_with_honor", "bring_draconic_wisdom", "command_respect"],
        ("tiefling", "any"): ["prove_individual_worth", "overcome_suspicion", "bring_unique_perspective"],
        ("gnome", "urban"): ["innovate_with_technology", "bring_curiosity_and_wonder", "create_magical_solutions"],
        ("half-elf", "any"): ["bridge_two_worlds", "adapt_to_any_culture", "bring_diplomatic_skills"],
        ("half-orc", "any"): ["prove_strength_through_community", "overcome_stereotypes", "bring_fierce_loyalty"]
    }
    
    # Try specific combination first, then race with any culture
    specific_key = (race, culture_type)
    general_key = (race, "any")
    
    if specific_key in synergies:
        return synergies[specific_key]
    elif general_key in synergies:
        return synergies[general_key]
    else:
        return [f"explore_unique_{race}_{culture_type}_combination"]

def get_background_culture_synergies(background: str, culture_type: str) -> List[str]:
    """Get background-culture synergies - crude_functional.py meaningful connections."""
    synergies = {
        ("acolyte", "urban"): ["serve_city_temple", "minister_to_diverse_population", "navigate_religious_politics"],
        ("acolyte", "rural"): ["be_village_spiritual_guide", "blend_faith_with_folk_wisdom", "comfort_simple_folk"],
        ("criminal", "urban"): ["navigate_underworld_networks", "understand_city_shadows", "exploit_urban_anonymity"],
        ("folk_hero", "rural"): ["champion_common_people", "defend_traditional_ways", "inspire_community_courage"],
        ("noble", "urban"): ["navigate_high_society", "influence_political_structures", "maintain_family_honor"],
        ("sage", "any"): ["preserve_cultural_knowledge", "bridge_ancient_and_modern", "teach_and_learn"],
        ("soldier", "any"): ["bring_military_discipline", "understand_chain_of_command", "protect_community"]
    }
    
    key = (background, culture_type)
    general_key = (background, "any")
    
    if key in synergies:
        return synergies[key]
    elif general_key in synergies:
        return synergies[general_key]
    else:
        return [f"integrate_{background}_experience_with_{culture_type}_culture"]

def get_class_culture_synergies(character_class: str, culture_type: str) -> List[str]:
    """Get class-culture synergies - crude_functional.py role integration."""
    synergies = {
        ("barbarian", "nomadic"): ["embrace_tribal_traditions", "be_cultural_warrior", "preserve_ancient_ways"],
        ("barbarian", "rural"): ["protect_simple_folk", "embody_primal_connection", "defend_traditional_lands"],
        ("bard", "any"): ["preserve_cultural_stories", "bridge_different_communities", "celebrate_local_traditions"],
        ("cleric", "any"): ["serve_community_spiritual_needs", "represent_divine_in_culture", "guide_moral_decisions"],
        ("druid", "rural"): ["protect_natural_balance", "guide_agricultural_cycles", "preserve_old_ways"],
        ("druid", "forest"): ["commune_with_nature_spirits", "maintain_woodland_balance", "teach_natural_wisdom"],
        ("fighter", "any"): ["protect_community", "uphold_cultural_values", "lead_through_strength"],
        ("monk", "mountain"): ["seek_enlightenment_in_isolation", "preserve_ancient_disciplines", "teach_inner_peace"],
        ("paladin", "any"): ["embody_cultural_ideals", "serve_as_moral_exemplar", "protect_the_innocent"],
        ("ranger", "any"): ["guard_cultural_borders", "bridge_civilization_and_wild", "track_threats"],
        ("rogue", "urban"): ["navigate_city_shadows", "understand_social_undercurrents", "gather_information"],
        ("sorcerer", "any"): ["explore_magical_heritage", "understand_power_within_culture", "bridge_mundane_and_magical"],
        ("warlock", "any"): ["explore_forbidden_knowledge", "navigate_cultural_taboos", "understand_power_costs"],
        ("wizard", "urban"): ["pursue_formal_education", "contribute_to_knowledge", "serve_as_cultural_scholar"]
    }
    
    key = (character_class, culture_type)
    general_key = (character_class, "any")
    
    if key in synergies:
        return synergies[key]
    elif general_key in synergies:
        return synergies[general_key]
    else:
        return [f"explore_{character_class}_role_in_{culture_type}_society"]

def get_character_culture_suggestions(
    culture_data: Dict[str, Any],
    character_data: Dict[str, Any]
) -> List[str]:
    """Get character-specific culture suggestions - crude_functional.py personalized guidance."""
    if not culture_data or not character_data:
        return []
    
    suggestions = []
    
    # Extract character elements
    character_race = character_data.get("race", "")
    character_class = character_data.get("class", "")
    character_background = character_data.get("background", "")
    character_level = character_data.get("level", 1)
    
    # Level-based cultural suggestions
    if character_level >= 5:
        suggestions.append("consider_how_adventures_changed_cultural_perspective")
    if character_level >= 10:
        suggestions.append("explore_leadership_role_in_cultural_community")
    
    # Ability score based suggestions (if available)
    ability_scores = character_data.get("ability_scores", {})
    if ability_scores:
        if ability_scores.get("charisma", 10) >= 14:
            suggestions.append("consider_cultural_leadership_or_diplomatic_roles")
        if ability_scores.get("wisdom", 10) >= 14:
            suggestions.append("explore_cultural_wisdom_keeper_or_advisor_role")
        if ability_scores.get("intelligence", 10) >= 14:
            suggestions.append("consider_cultural_scholar_or_historian_role")
    
    return suggestions

# ============ VALIDATION HELPER UTILITIES ============

def is_exotic_language(language: str) -> bool:
    """Check if language is exotic - crude_functional.py simple check."""
    if not language:
        return False
    
    exotic_languages = [
        "abyssal", "celestial", "draconic", "deep_speech", "infernal",
        "primordial", "sylvan", "undercommon", "thieves_cant"
    ]
    
    return language.lower() in exotic_languages

def get_cultural_warning_level(
    culture_data: Dict[str, Any],
    character_data: Dict[str, Any] = None
) -> str:
    """Get cultural validation warning level - crude_functional.py helpful categorization."""
    if not culture_data:
        return "info"
    
    # Always low-level warnings since culture is supportive
    restrictions = culture_data.get("restrictions", [])
    flexibility = culture_data.get("flexibility", "high")
    
    if len(restrictions) > 3 and flexibility.lower() == "low":
        return "caution"  # Still not an error
    elif len(restrictions) > 0:
        return "info"
    else:
        return "suggestion"

def validate_cultural_depth(culture_data: Dict[str, Any]) -> Tuple[int, List[str]]:
    """Validate cultural depth - crude_functional.py richness assessment."""
    if not culture_data:
        return 0, ["No culture data provided"]
    
    depth_score = 0
    suggestions_for_depth = []
    
    # Check for various cultural elements
    cultural_elements = [
        ("languages", "Add more languages for linguistic diversity"),
        ("traditions", "Include more traditions for cultural richness"),
        ("values", "Define cultural values for character motivation"),
        ("customs", "Add customs for daily life details"),
        ("festivals", "Include festivals for cultural celebration"),
        ("art_forms", "Add art forms for creative expression"),
        ("conflicts", "Consider cultural tensions for story hooks"),
        ("opportunities", "Define opportunities for character growth")
    ]
    
    for element, suggestion in cultural_elements:
        if element in culture_data and culture_data[element]:
            depth_score += 1
        else:
            suggestions_for_depth.append(suggestion)
    
    return depth_score, suggestions_for_depth

def suggest_cultural_improvements(
    culture_data: Dict[str, Any],
    depth_score: int
) -> List[str]:
    """Suggest cultural improvements - crude_functional.py constructive feedback."""
    if not culture_data:
        return ["Start with basic culture type and structure"]
    
    improvements = []
    
    if depth_score < 3:
        improvements.append("Add more basic cultural elements (languages, traditions, values)")
    elif depth_score < 5:
        improvements.append("Consider adding customs and festivals for daily life richness")
    elif depth_score < 7:
        improvements.append("Include art forms and cultural conflicts for storytelling depth")
    else:
        improvements.append("Your culture is richly detailed - great work!")
    
    # Always encourage creativity
    improvements.append("Remember: adapt any cultural element to fit your character concept")
    improvements.append("Culture should inspire, not constrain your roleplay")
    
    return improvements

# ============ COMPREHENSIVE VALIDATION ============

def comprehensive_culture_validation(
    culture_data: Dict[str, Any],
    character_data: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Comprehensive culture validation - crude_functional.py complete assessment."""
    if not culture_data:
        return {
            "is_valid": True,
            "validation_level": "info",
            "suggestions": ["Consider adding cultural elements for character depth"],
            "notes": ["Culture is optional but adds richness to roleplay"],
            "depth_score": 0,
            "improvements": ["Start with basic culture type"]
        }
    
    # Run all validations
    is_valid, suggestions, notes = validate_culture_choice(culture_data, character_data)
    warning_level = get_cultural_warning_level(culture_data, character_data)
    depth_score, depth_suggestions = validate_cultural_depth(culture_data)
    improvements = suggest_cultural_improvements(culture_data, depth_score)
    
    # Combine all feedback
    all_suggestions = list(set(suggestions + depth_suggestions))
    all_notes = list(set(notes))
    
    return {
        "is_valid": is_valid,  # Always true for culture
        "validation_level": warning_level,
        "suggestions": all_suggestions,
        "notes": all_notes,
        "depth_score": depth_score,
        "improvements": improvements,
        "creative_freedom_preserved": True  # Always true
    }

# ============ ESSENTIAL EXPORTS ============

__all__ = [
    # Core validation
    'validate_culture_choice',
    'validate_cultural_compatibility',
    'validate_language_choices',
    
    # Enhancement suggestions
    'get_culture_enhancement_suggestions',
    'get_race_culture_synergies',
    'get_background_culture_synergies',
    'get_class_culture_synergies',
    'get_character_culture_suggestions',
    
    # Helper utilities
    'is_exotic_language',
    'get_cultural_warning_level',
    'validate_cultural_depth',
    'suggest_cultural_improvements',
    
    # Comprehensive validation
    'comprehensive_culture_validation',
]

# ============ MODULE METADATA ============

__version__ = '1.0.0'
__description__ = 'Essential D&D culture validation utilities'
__author__ = 'D&D Character Creator Backend7'

# Backend7 architecture compliance
BACKEND7_COMPLIANCE = {
    "layer": "core/utils",
    "focus": "culture_validation_utilities",
    "line_target": 200,
    "dependencies": ["core.enums"],
    "philosophy": "crude_functional_inspired_supportive_validation",
    "maintains_crude_functional_approach": True,
    "validation_philosophy": "suggest_and_enhance_never_restrict"
}

# Cultural Validation Philosophy
VALIDATION_PRINCIPLES = {
    "always_valid": "Cultural choices are always valid - validation provides suggestions",
    "enhance_not_restrict": "Validation enhances creativity, never limits choice",
    "supportive_feedback": "All feedback is constructive and encouraging",
    "creative_freedom": "Players can adapt, modify, or ignore any cultural suggestion",
    "positive_reinforcement": "Focus on opportunities and synergies, not limitations"
}