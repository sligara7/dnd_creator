"""
Essential D&D Culture Parser Utilities

Streamlined culture parsing utilities following backend7 architecture.
Based on crude_functional.py patterns and essential-only philosophy.
Maintains overarching functionality of crude_functional.py approach.

Culture augments character creation with deep backgrounds while preserving creative freedom.
Culture provides context and depth, never restricts player choice.
"""

from typing import Dict, List, Tuple, Optional, Any, Union
from core.enums import (
    CultureType, LanguageFamily, SocialStructure, ReligiousTradition,
    ArtisticTradition, SettlementType, CreativityLevel
)

# ============ CORE CULTURE PARSING ============

def parse_culture_data(culture_input: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Parse culture data - crude_functional.py style simple parsing."""
    if not culture_input:
        return get_default_culture()
    
    if isinstance(culture_input, str):
        return parse_culture_from_string(culture_input)
    elif isinstance(culture_input, dict):
        return normalize_culture_dict(culture_input)
    else:
        return get_default_culture()

def parse_culture_from_string(culture_string: str) -> Dict[str, Any]:
    """Parse culture from string - crude_functional.py direct approach."""
    if not culture_string:
        return get_default_culture()
    
    culture_string = culture_string.lower().strip()
    
    # Simple string-to-culture mapping
    culture_mappings = {
        "urban": {"type": "urban", "structure": "hierarchical", "settlement": "city"},
        "rural": {"type": "rural", "structure": "communal", "settlement": "village"},
        "nomadic": {"type": "nomadic", "structure": "tribal", "settlement": "camp"},
        "coastal": {"type": "coastal", "structure": "trading", "settlement": "port"},
        "mountain": {"type": "mountain", "structure": "clan", "settlement": "stronghold"},
        "forest": {"type": "forest", "structure": "druidic", "settlement": "grove"},
        "desert": {"type": "desert", "structure": "tribal", "settlement": "oasis"},
        "underground": {"type": "underground", "structure": "clan", "settlement": "delve"}
    }
    
    base_culture = culture_mappings.get(culture_string, {"type": "mixed", "structure": "varied", "settlement": "town"})
    return expand_culture_data(base_culture)

def normalize_culture_dict(culture_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize culture dictionary - crude_functional.py simple normalization."""
    if not culture_dict:
        return get_default_culture()
    
    # Ensure required fields exist
    normalized = {
        "type": culture_dict.get("type", "mixed"),
        "structure": culture_dict.get("structure", "varied"),
        "settlement": culture_dict.get("settlement", "town"),
        "languages": culture_dict.get("languages", ["common"]),
        "traditions": culture_dict.get("traditions", []),
        "values": culture_dict.get("values", []),
        "customs": culture_dict.get("customs", []),
        "restrictions": culture_dict.get("restrictions", []),  # Kept minimal for creative freedom
        "suggestions": culture_dict.get("suggestions", []),
        "flexibility": culture_dict.get("flexibility", "high")  # Default to high flexibility
    }
    
    return normalized

def get_default_culture() -> Dict[str, Any]:
    """Get default culture - crude_functional.py safe default."""
    return {
        "type": "mixed",
        "structure": "varied",
        "settlement": "town",
        "languages": ["common"],
        "traditions": ["storytelling", "craftsmanship"],
        "values": ["community", "tradition", "adaptability"],
        "customs": ["seasonal_festivals", "coming_of_age_ceremonies"],
        "restrictions": [],  # No restrictions by default
        "suggestions": ["consider_local_customs", "embrace_cultural_diversity"],
        "flexibility": "high"
    }

# ============ CULTURE ENHANCEMENT UTILITIES ============

def expand_culture_data(base_culture: Dict[str, Any]) -> Dict[str, Any]:
    """Expand culture data with rich details - crude_functional.py enhancement."""
    if not base_culture:
        return get_default_culture()
    
    culture_type = base_culture.get("type", "mixed")
    
    # Enhance based on culture type
    enhancements = {
        "urban": {
            "languages": ["common", "trade_tongue", "guild_cant"],
            "traditions": ["guild_craftsmanship", "formal_education", "political_discourse"],
            "values": ["progress", "efficiency", "social_mobility"],
            "customs": ["market_days", "guild_ceremonies", "formal_greetings"],
            "opportunities": ["merchant_connections", "guild_membership", "formal_education"],
            "art_forms": ["theater", "sculpture", "architecture"]
        },
        "rural": {
            "languages": ["common", "local_dialect"],
            "traditions": ["agricultural_cycles", "folk_medicine", "oral_history"],
            "values": ["hard_work", "community_support", "connection_to_land"],
            "customs": ["harvest_festivals", "barn_raisings", "storytelling_evenings"],
            "opportunities": ["deep_nature_knowledge", "practical_skills", "tight_community"],
            "art_forms": ["folk_music", "woodcarving", "quilting"]
        },
        "nomadic": {
            "languages": ["common", "trade_pidgin", "ancient_tongue"],
            "traditions": ["seasonal_migration", "oral_traditions", "star_navigation"],
            "values": ["freedom", "adaptability", "ancestral_wisdom"],
            "customs": ["seasonal_gatherings", "storytelling_competitions", "blessing_ceremonies"],
            "opportunities": ["extensive_travel_knowledge", "survival_skills", "cultural_exchange"],
            "art_forms": ["epic_poetry", "textile_work", "music"]
        }
    }
    
    enhancement = enhancements.get(culture_type, {})
    
    # Merge enhancements with base culture
    enhanced_culture = base_culture.copy()
    for key, value in enhancement.items():
        if key in enhanced_culture:
            if isinstance(value, list):
                enhanced_culture[key] = list(set(enhanced_culture[key] + value))
            else:
                enhanced_culture[key] = value
        else:
            enhanced_culture[key] = value
    
    return enhanced_culture

def get_cultural_suggestions(culture_data: Dict[str, Any], character_data: Dict[str, Any] = None) -> List[str]:
    """Get cultural suggestions for character - crude_functional.py helpful guidance."""
    if not culture_data:
        return []
    
    suggestions = []
    culture_type = culture_data.get("type", "mixed")
    character_class = character_data.get("class", "") if character_data else ""
    character_background = character_data.get("background", "") if character_data else ""
    
    # Base cultural suggestions
    base_suggestions = culture_data.get("suggestions", [])
    suggestions.extend(base_suggestions)
    
    # Class-specific cultural suggestions
    if character_class:
        class_culture_suggestions = {
            "barbarian": ["consider_tribal_heritage", "embrace_natural_connection"],
            "bard": ["explore_artistic_traditions", "value_storytelling_culture"],
            "cleric": ["align_with_religious_traditions", "serve_community_needs"],
            "druid": ["connect_with_nature_traditions", "respect_natural_cycles"],
            "fighter": ["honor_warrior_traditions", "value_martial_heritage"],
            "monk": ["embrace_monastic_traditions", "seek_inner_harmony"],
            "paladin": ["uphold_cultural_virtues", "serve_as_moral_example"],
            "ranger": ["bridge_civilization_wilderness", "protect_cultural_borders"],
            "rogue": ["navigate_cultural_underworld", "understand_social_dynamics"],
            "sorcerer": ["explore_magical_heritage", "embrace_unique_cultural_role"],
            "warlock": ["consider_cultural_taboos", "explore_forbidden_knowledge"],
            "wizard": ["value_educational_traditions", "seek_cultural_knowledge"]
        }
        
        class_suggestions = class_culture_suggestions.get(character_class.lower(), [])
        suggestions.extend(class_suggestions)
    
    # Background-specific cultural suggestions
    if character_background:
        background_culture_suggestions = {
            "acolyte": ["explore_religious_culture", "understand_sacred_traditions"],
            "criminal": ["understand_underground_culture", "navigate_social_margins"],
            "folk_hero": ["embrace_common_culture", "serve_community_needs"],
            "noble": ["understand_aristocratic_culture", "navigate_social_hierarchy"],
            "sage": ["value_intellectual_culture", "seek_ancient_knowledge"],
            "soldier": ["honor_military_culture", "understand_chain_of_command"]
        }
        
        background_suggestions = background_culture_suggestions.get(character_background.lower(), [])
        suggestions.extend(background_suggestions)
    
    # Always add creative freedom reminder
    suggestions.append("remember_culture_enhances_not_restricts")
    suggestions.append("adapt_culture_to_your_vision")
    
    return list(set(suggestions))  # Remove duplicates

# ============ CULTURAL COMPATIBILITY UTILITIES ============

def check_cultural_compatibility(
    race: str,
    culture_data: Dict[str, Any],
    character_data: Dict[str, Any] = None
) -> Tuple[bool, List[str], List[str]]:
    """Check cultural compatibility - crude_functional.py flexible validation."""
    if not race or not culture_data:
        return True, [], ["Missing race or culture data"]
    
    suggestions = []
    notes = []
    
    # Always compatible - culture enhances, never restricts
    is_compatible = True
    
    # Provide enhancement suggestions based on race-culture combination
    race_culture_enhancements = {
        ("elf", "urban"): ["consider_elven_districts", "explore_long_lived_perspective"],
        ("dwarf", "mountain"): ["embrace_clan_traditions", "honor_ancestral_crafts"],
        ("human", "nomadic"): ["adapt_quickly_to_change", "bridge_cultural_differences"],
        ("halfling", "rural"): ["value_comfort_and_community", "celebrate_simple_pleasures"],
        ("dragonborn", "any"): ["explore_draconic_heritage", "navigate_cultural_prejudices"],
        ("tiefling", "any"): ["overcome_cultural_suspicion", "prove_individual_worth"]
    }
    
    # Check for specific enhancements
    race_lower = race.lower()
    culture_type = culture_data.get("type", "mixed")
    
    enhancement_key = (race_lower, culture_type)
    if enhancement_key in race_culture_enhancements:
        suggestions.extend(race_culture_enhancements[enhancement_key])
    
    # Generic race-culture enhancement
    generic_key = (race_lower, "any")
    if generic_key in race_culture_enhancements:
        suggestions.extend(race_culture_enhancements[generic_key])
    
    # Add general notes about cultural integration
    notes.append(f"{race.title()} characters can thrive in {culture_type} culture")
    notes.append("Cultural background provides opportunities for rich roleplay")
    notes.append("Feel free to adapt cultural elements to your character concept")
    
    return is_compatible, suggestions, notes

def generate_cultural_background(
    culture_data: Dict[str, Any],
    creativity_level: CreativityLevel = CreativityLevel.BALANCED
) -> Dict[str, Any]:
    """Generate cultural background details - crude_functional.py creative generation."""
    if not culture_data:
        return {}
    
    culture_type = culture_data.get("type", "mixed")
    
    # Generate background elements based on culture
    background_elements = {
        "family_structure": get_family_structure(culture_type),
        "coming_of_age": get_coming_of_age_tradition(culture_type),
        "daily_life": get_daily_life_elements(culture_type),
        "festivals": get_cultural_festivals(culture_type),
        "conflicts": get_cultural_conflicts(culture_type),
        "opportunities": get_cultural_opportunities(culture_type),
        "mysteries": get_cultural_mysteries(culture_type),
        "connections": get_cultural_connections(culture_type)
    }
    
    # Adjust based on creativity level
    if creativity_level == CreativityLevel.CONSERVATIVE:
        # Stick to well-established tropes
        background_elements = filter_conservative_elements(background_elements)
    elif creativity_level == CreativityLevel.CREATIVE:
        # Add more unique elements
        background_elements = enhance_creative_elements(background_elements)
    
    return background_elements

# ============ BACKGROUND ELEMENT GENERATORS ============

def get_family_structure(culture_type: str) -> List[str]:
    """Get family structure options - crude_functional.py simple options."""
    family_structures = {
        "urban": ["nuclear_family", "extended_family", "chosen_family", "guild_family"],
        "rural": ["extended_family", "clan_structure", "farming_community", "village_elders"],
        "nomadic": ["tribal_family", "traveling_band", "seasonal_groups", "ancestral_lines"],
        "coastal": ["maritime_family", "trading_house", "fishing_community", "port_family"],
        "mountain": ["clan_structure", "forge_family", "mining_community", "stone_kindred"],
        "forest": ["grove_family", "ranger_band", "druid_circle", "nature_clan"],
        "desert": ["oasis_family", "caravan_group", "tribal_structure", "nomad_kinship"]
    }
    
    return family_structures.get(culture_type, ["varied_family_structure"])

def get_coming_of_age_tradition(culture_type: str) -> List[str]:
    """Get coming of age traditions - crude_functional.py cultural depth."""
    traditions = {
        "urban": ["guild_apprenticeship", "formal_education", "social_debut", "skill_mastery"],
        "rural": ["harvest_participation", "craft_learning", "community_service", "land_blessing"],
        "nomadic": ["vision_quest", "survival_trial", "star_reading", "ancestor_communion"],
        "coastal": ["first_voyage", "storm_weathering", "tide_reading", "sea_blessing"],
        "mountain": ["stone_trial", "forge_mastery", "clan_acceptance", "mountain_pilgrimage"],
        "forest": ["nature_communion", "tracking_mastery", "grove_acceptance", "animal_bond"],
        "desert": ["sun_trial", "oasis_finding", "survival_test", "star_navigation"]
    }
    
    return traditions.get(culture_type, ["personal_achievement"])

def get_daily_life_elements(culture_type: str) -> List[str]:
    """Get daily life elements - crude_functional.py cultural texture."""
    daily_life = {
        "urban": ["market_visits", "guild_meetings", "social_gatherings", "formal_meals"],
        "rural": ["dawn_chores", "seasonal_work", "community_meals", "evening_stories"],
        "nomadic": ["camp_breaking", "travel_preparation", "star_navigation", "tribal_councils"],
        "coastal": ["tide_watching", "net_mending", "weather_reading", "sea_prayers"],
        "mountain": ["forge_work", "mining_duties", "clan_meetings", "stone_carving"],
        "forest": ["nature_tending", "grove_maintenance", "animal_care", "herb_gathering"],
        "desert": ["water_conservation", "heat_avoidance", "caravan_preparation", "star_study"]
    }
    
    return daily_life.get(culture_type, ["varied_daily_routine"])

def get_cultural_festivals(culture_type: str) -> List[str]:
    """Get cultural festivals - crude_functional.py celebration options."""
    festivals = {
        "urban": ["guild_festivals", "market_celebrations", "political_ceremonies", "artistic_showcases"],
        "rural": ["harvest_festivals", "planting_ceremonies", "seasonal_celebrations", "community_fairs"],
        "nomadic": ["migration_ceremonies", "star_festivals", "ancestor_honoring", "tribal_gatherings"],
        "coastal": ["tide_festivals", "storm_celebrations", "fishing_ceremonies", "maritime_holidays"],
        "mountain": ["forge_festivals", "clan_gatherings", "stone_ceremonies", "mining_celebrations"],
        "forest": ["seasonal_rites", "grove_ceremonies", "nature_festivals", "harmony_celebrations"],
        "desert": ["oasis_festivals", "star_ceremonies", "survival_celebrations", "caravan_festivals"]
    }
    
    return festivals.get(culture_type, ["seasonal_celebrations"])

def get_cultural_conflicts(culture_type: str) -> List[str]:
    """Get cultural conflicts - crude_functional.py story hooks."""
    conflicts = {
        "urban": ["guild_rivalries", "class_tensions", "political_disputes", "resource_competition"],
        "rural": ["land_disputes", "weather_hardships", "tradition_vs_change", "resource_scarcity"],
        "nomadic": ["territory_conflicts", "resource_competition", "tradition_preservation", "external_pressure"],
        "coastal": ["maritime_disputes", "weather_challenges", "trade_conflicts", "territorial_waters"],
        "mountain": ["clan_feuds", "mining_rights", "forge_competition", "territory_disputes"],
        "forest": ["nature_preservation", "external_encroachment", "grove_protection", "balance_maintenance"],
        "desert": ["water_rights", "oasis_control", "caravan_conflicts", "survival_competition"]
    }
    
    return conflicts.get(culture_type, ["general_challenges"])

def get_cultural_opportunities(culture_type: str) -> List[str]:
    """Get cultural opportunities - crude_functional.py positive aspects."""
    opportunities = {
        "urban": ["networking", "education", "cultural_exchange", "economic_advancement"],
        "rural": ["deep_community_bonds", "nature_connection", "traditional_knowledge", "simple_pleasures"],
        "nomadic": ["travel_experience", "cultural_diversity", "survival_skills", "freedom"],
        "coastal": ["maritime_knowledge", "trade_connections", "weather_wisdom", "sea_mysteries"],
        "mountain": ["crafting_mastery", "clan_loyalty", "mineral_knowledge", "fortress_security"],
        "forest": ["nature_wisdom", "druidic_knowledge", "animal_companionship", "natural_magic"],
        "desert": ["survival_expertise", "star_knowledge", "caravan_connections", "heat_adaptation"]
    }
    
    return opportunities.get(culture_type, ["diverse_experiences"])

def get_cultural_mysteries(culture_type: str) -> List[str]:
    """Get cultural mysteries - crude_functional.py intrigue hooks."""
    mysteries = {
        "urban": ["hidden_guild_secrets", "political_conspiracies", "underground_networks", "ancient_architecture"],
        "rural": ["old_standing_stones", "forest_spirits", "ancestral_burial_grounds", "weather_omens"],
        "nomadic": ["star_prophecies", "ancient_migration_routes", "sacred_sites", "ancestral_visions"],
        "coastal": ["sea_legends", "hidden_coves", "storm_omens", "deep_sea_mysteries"],
        "mountain": ["ancient_forges", "deep_tunnels", "clan_secrets", "stone_magic"],
        "forest": ["grove_mysteries", "ancient_trees", "spirit_communication", "natural_portals"],
        "desert": ["buried_cities", "oasis_magic", "star_portents", "ancient_ruins"]
    }
    
    return mysteries.get(culture_type, ["local_legends"])

def get_cultural_connections(culture_type: str) -> List[str]:
    """Get cultural connections - crude_functional.py network building."""
    connections = {
        "urban": ["guild_members", "political_contacts", "merchant_networks", "cultural_patrons"],
        "rural": ["village_elders", "farming_families", "local_crafters", "traveling_merchants"],
        "nomadic": ["tribal_leaders", "fellow_travelers", "trading_partners", "spiritual_guides"],
        "coastal": ["ship_captains", "dock_workers", "maritime_traders", "weather_watchers"],
        "mountain": ["clan_elders", "master_crafters", "mining_foremen", "stone_speakers"],
        "forest": ["grove_keepers", "ranger_networks", "druid_circles", "nature_spirits"],
        "desert": ["caravan_leaders", "oasis_keepers", "star_readers", "survival_guides"]
    }
    
    return connections.get(culture_type, ["community_members"])

# ============ CREATIVE FREEDOM UTILITIES ============

def filter_conservative_elements(background_elements: Dict[str, Any]) -> Dict[str, Any]:
    """Filter for conservative creativity - crude_functional.py safety."""
    # Keep traditional, well-established elements
    filtered = {}
    for key, value in background_elements.items():
        if isinstance(value, list):
            # Keep first few traditional options
            filtered[key] = value[:2]
        else:
            filtered[key] = value
    
    return filtered

def enhance_creative_elements(background_elements: Dict[str, Any]) -> Dict[str, Any]:
    """Enhance for creative freedom - crude_functional.py expansion."""
    # Add more unique and creative options
    enhanced = background_elements.copy()
    
    # Add creative variants
    creative_additions = {
        "unique_traditions": ["secret_societies", "mystical_practices", "unusual_crafts"],
        "cultural_innovations": ["new_technologies", "social_experiments", "artistic_movements"],
        "cross_cultural_elements": ["foreign_influences", "cultural_fusion", "immigrant_communities"]
    }
    
    enhanced.update(creative_additions)
    return enhanced

def validate_creative_freedom(culture_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate creative freedom preservation - crude_functional.py freedom check."""
    if not culture_data:
        return True, []
    
    freedom_violations = []
    
    # Check for overly restrictive elements
    restrictions = culture_data.get("restrictions", [])
    if len(restrictions) > 3:
        freedom_violations.append("Too many cultural restrictions may limit creativity")
    
    # Check flexibility setting
    flexibility = culture_data.get("flexibility", "high")
    if flexibility.lower() in ["none", "low"]:
        freedom_violations.append("Low flexibility may restrict character development")
    
    # Always encourage creative adaptation
    freedom_preserving = len(freedom_violations) == 0
    
    return freedom_preserving, freedom_violations

# ============ ESSENTIAL EXPORTS ============

__all__ = [
    # Core parsing
    'parse_culture_data',
    'parse_culture_from_string',
    'normalize_culture_dict',
    'get_default_culture',
    
    # Enhancement utilities
    'expand_culture_data',
    'get_cultural_suggestions',
    
    # Compatibility utilities
    'check_cultural_compatibility',
    'generate_cultural_background',
    
    # Background element generators
    'get_family_structure',
    'get_coming_of_age_tradition',
    'get_daily_life_elements',
    'get_cultural_festivals',
    'get_cultural_conflicts',
    'get_cultural_opportunities',
    'get_cultural_mysteries',
    'get_cultural_connections',
    
    # Creative freedom utilities
    'filter_conservative_elements',
    'enhance_creative_elements',
    'validate_creative_freedom',
]

# ============ MODULE METADATA ============

__version__ = '1.0.0'
__description__ = 'Essential D&D culture parsing utilities'
__author__ = 'D&D Character Creator Backend7'

# Backend7 architecture compliance
BACKEND7_COMPLIANCE = {
    "layer": "core/utils",
    "focus": "culture_parsing_utilities",
    "line_target": 200,
    "dependencies": ["core.enums"],
    "philosophy": "crude_functional_inspired_creative_freedom_preserving",
    "maintains_crude_functional_approach": True,
    "cultural_philosophy": "enhance_not_restrict_creative_freedom"
}

# Cultural Design Philosophy
CULTURAL_DESIGN_PRINCIPLES = {
    "enhancement_over_restriction": "Culture adds depth, never limits choice",
    "creative_freedom_paramount": "Players can adapt any cultural element",
    "suggestions_not_requirements": "Cultural elements are options, not mandates",
    "flexibility_default": "All cultures default to high flexibility",
    "positive_focus": "Emphasize opportunities and richness over limitations"
}