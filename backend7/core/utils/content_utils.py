"""
Essential D&D Content Utilities

Streamlined content utilities following backend7 architecture.
Based on crude_functional.py patterns and essential-only philosophy.
Maintains overarching functionality of crude_functional.py approach.

SUPPORTS UNLIMITED CREATIVE CONTENT - No restrictions on classes, species, feats, spells, weapons.
"""

from typing import Dict, List, Tuple, Optional, Any, Union
from core.enums import (
    CharacterElement, SourceType, ContentRarity, MechanicType,
    SpellSchool, EquipmentCategory, CultureType, CreativityLevel
)

# ============ MISSING CORE FUNCTIONS (REQUIRED BY __init__.py) ============

def analyze_character_content(character_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze character content - crude_functional.py content analysis. UNLIMITED CREATIVITY."""
    if not character_data:
        return {
            "content_score": 0.0,
            "completeness": 0.0,
            "richness": 0.0,
            "consistency": 0.0,
            "themes": [],
            "missing_elements": ["basic_character_data"]
        }
    
    # Basic content analysis - no restrictions on content types
    content_elements = {
        "basic_info": bool(character_data.get("name") and 
                          (character_data.get("race") or character_data.get("species")) and 
                          character_data.get("class")),
        "background": bool(character_data.get("background")),
        "personality": bool(character_data.get("personality_traits") or character_data.get("traits")),
        "backstory": bool(character_data.get("backstory") or character_data.get("history")),
        "goals": bool(character_data.get("goals") or character_data.get("motivations")),
        "connections": bool(character_data.get("allies") or character_data.get("contacts")),
        "flaws": bool(character_data.get("flaws") or character_data.get("weaknesses")),
        "ideals": bool(character_data.get("ideals") or character_data.get("beliefs"))
    }
    
    # Calculate scores
    present_elements = sum(content_elements.values())
    total_elements = len(content_elements)
    completeness = present_elements / total_elements
    
    # Content richness based on detail level
    richness = calculate_content_richness(character_data)
    
    # Content consistency - flexible for any content
    consistency = check_content_consistency(character_data)[0]
    
    # Overall content score
    content_score = (completeness * 0.4) + (richness * 0.3) + (consistency * 0.3)
    
    # Extract themes - works with any content
    themes = extract_character_themes(character_data)
    
    # Missing elements
    missing_elements = [element for element, present in content_elements.items() if not present]
    
    return {
        "content_score": content_score,
        "completeness": completeness,
        "richness": richness,
        "consistency": consistency,
        "themes": themes,
        "missing_elements": missing_elements,
        "present_elements": list(element for element, present in content_elements.items() if present),
        "supports_unlimited_creativity": True
    }

def validate_content_completeness(character_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate content completeness - crude_functional.py completeness check. NO CONTENT RESTRICTIONS."""
    if not character_data:
        return False, ["No character data provided"]
    
    suggestions = []
    
    # Essential elements - accept any values, no predefined lists
    essential_missing = []
    if not character_data.get("name"):
        essential_missing.append("character name")
    if not (character_data.get("race") or character_data.get("species")):
        essential_missing.append("character race/species")
    if not character_data.get("class"):
        essential_missing.append("character class")
    
    if essential_missing:
        suggestions.extend([f"Add {element}" for element in essential_missing])
        return False, suggestions
    
    # Recommended elements - flexible suggestions
    recommended_elements = {
        "background": "Add character background for depth",
        "personality_traits": "Add personality traits for roleplay",
        "backstory": "Add backstory for character motivation",
        "goals": "Add character goals and motivations",
        "flaws": "Add character flaws for interesting roleplay",
        "ideals": "Add character ideals and beliefs"
    }
    
    for element, suggestion in recommended_elements.items():
        if not character_data.get(element):
            suggestions.append(suggestion)
    
    # Consider complete if has essentials + at least 2 recommended
    has_recommended = sum(1 for element in recommended_elements if character_data.get(element))
    is_complete = len(essential_missing) == 0 and has_recommended >= 2
    
    return is_complete, suggestions

def generate_content_suggestions(character_data: Dict[str, Any]) -> List[str]:
    """Generate content suggestions - crude_functional.py suggestion engine. UNLIMITED CREATIVITY."""
    if not character_data:
        return [
            "Start with basic character information: name, race/species, class",
            "Add a background that fits your character concept",
            "Define personality traits that make your character unique",
            "Create any custom classes, species, or abilities you envision"
        ]
    
    suggestions = []
    
    # Content completeness suggestions
    _, completeness_suggestions = validate_content_completeness(character_data)
    suggestions.extend(completeness_suggestions)
    
    # Flexible content suggestions based on what exists
    character_class = character_data.get("class", "")
    if character_class:
        class_suggestions = get_flexible_class_suggestions(character_class)
        suggestions.extend(class_suggestions)
    
    # Species/race suggestions - flexible
    race = character_data.get("race") or character_data.get("species", "")
    if race:
        species_suggestions = get_flexible_species_suggestions(race)
        suggestions.extend(species_suggestions)
    
    # Background suggestions - flexible
    background = character_data.get("background", "")
    if background:
        background_suggestions = get_flexible_background_suggestions(background)
        suggestions.extend(background_suggestions)
    
    # Theme-based suggestions - works with any themes
    themes = extract_character_themes(character_data)
    if themes:
        theme_suggestions = get_theme_content_suggestions(themes)
        suggestions.extend(theme_suggestions)
    
    # Creative freedom suggestions
    suggestions.extend([
        "Feel free to create completely new classes, species, or abilities",
        "Custom content is encouraged and supported",
        "Build unique character concepts without traditional limitations"
    ])
    
    # Remove duplicates and limit to reasonable number
    unique_suggestions = list(set(suggestions))
    return unique_suggestions[:12]  # Allow a few more suggestions for creative freedom

def check_content_consistency(character_data: Dict[str, Any]) -> Tuple[float, List[str]]:
    """Check content consistency - crude_functional.py consistency validation. FLEXIBLE FOR ANY CONTENT."""
    if not character_data:
        return 0.0, ["No character data to check"]
    
    consistency_score = 1.0
    inconsistencies = []
    
    # Flexible consistency checks - look for logical conflicts, not predefined restrictions
    character_class = character_data.get("class", "")
    background = character_data.get("background", "")
    
    if character_class and background:
        # Only flag obvious logical conflicts, not traditional combinations
        logical_conflicts = check_logical_conflicts(character_class, background)
        if logical_conflicts:
            consistency_score -= 0.1  # Reduced penalty for creative freedom
            inconsistencies.extend(logical_conflicts)
    
    # Check for internal contradictions in personality/goals
    personality = character_data.get("personality_traits", [])
    goals = character_data.get("goals", [])
    
    if personality and goals:
        internal_conflicts = check_internal_contradictions(personality, goals)
        if internal_conflicts:
            consistency_score -= 0.1
            inconsistencies.extend(internal_conflicts)
    
    # Always maintain high consistency for creative content
    return max(0.8, consistency_score), inconsistencies

def extract_character_themes(character_data: Dict[str, Any]) -> List[str]:
    """Extract character themes - crude_functional.py theme extraction. WORKS WITH ANY CONTENT."""
    if not character_data:
        return []
    
    themes = []
    
    # Extract themes from any class name
    character_class = character_data.get("class", "")
    if character_class:
        class_themes = extract_themes_from_name(character_class)
        themes.extend(class_themes)
    
    # Extract themes from any background
    background = character_data.get("background", "")
    if background:
        background_themes = extract_themes_from_name(background)
        themes.extend(background_themes)
    
    # Extract themes from race/species name
    race = character_data.get("race") or character_data.get("species", "")
    if race:
        race_themes = extract_themes_from_name(race)
        themes.extend(race_themes)
    
    # Extract themes from backstory/personality/goals
    backstory = character_data.get("backstory", "")
    personality = character_data.get("personality_traits", [])
    goals = character_data.get("goals", [])
    
    text_themes = extract_themes_from_text(backstory, personality, goals)
    themes.extend(text_themes)
    
    # Remove duplicates and return
    return list(set(themes))

def summarize_character_concept(character_data: Dict[str, Any]) -> str:
    """Summarize character concept - crude_functional.py concept summary. SUPPORTS ANY CONTENT."""
    if not character_data:
        return "Incomplete character concept"
    
    # Basic character info - flexible field names
    name = character_data.get("name", "Unnamed Character")
    race = character_data.get("race") or character_data.get("species", "Unknown Species")
    character_class = character_data.get("class", "Unknown Class")
    level = character_data.get("level", 1)
    background = character_data.get("background", "")
    
    # Build summary
    summary_parts = []
    
    # Basic description
    basic_desc = f"{name} is a level {level} {race} {character_class}"
    if background:
        basic_desc += f" with a {background} background"
    summary_parts.append(basic_desc)
    
    # Add personality if available
    personality = character_data.get("personality_traits", [])
    if personality:
        if isinstance(personality, list) and personality:
            personality_desc = f"Known for being {', '.join(personality[:2])}"
            summary_parts.append(personality_desc)
        elif isinstance(personality, str):
            personality_desc = f"Characterized by {personality}"
            summary_parts.append(personality_desc)
    
    # Add goals if available
    goals = character_data.get("goals", [])
    if goals:
        if isinstance(goals, list) and goals:
            goal_desc = f"Seeks to {goals[0]}"
            summary_parts.append(goal_desc)
        elif isinstance(goals, str):
            goal_desc = f"Motivated by {goals}"
            summary_parts.append(goal_desc)
    
    # Add primary theme
    themes = extract_character_themes(character_data)
    if themes:
        theme_desc = f"Embodies themes of {themes[0]}"
        summary_parts.append(theme_desc)
    
    return ". ".join(summary_parts) + "."

# ============ FLEXIBLE CONTENT FUNCTIONS ============

def get_flexible_class_suggestions(character_class: str) -> List[str]:
    """Get flexible class suggestions - crude_functional.py adaptive suggestions."""
    suggestions = []
    
    # Generic suggestions that work for any class
    suggestions.extend([
        f"Explore what makes your {character_class} unique",
        f"Define your {character_class}'s abilities and powers",
        f"Consider your {character_class}'s role in the world",
        f"Create meaningful connections for your {character_class}"
    ])
    
    # Keyword-based suggestions for known patterns
    class_lower = character_class.lower()
    
    if any(word in class_lower for word in ["magic", "spell", "wizard", "sorcerer", "mage"]):
        suggestions.append("Define your magical abilities and their source")
    
    if any(word in class_lower for word in ["fight", "warrior", "soldier", "guard"]):
        suggestions.append("Define your combat training and experience")
    
    if any(word in class_lower for word in ["divine", "holy", "priest", "cleric"]):
        suggestions.append("Define your divine connection or beliefs")
    
    if any(word in class_lower for word in ["nature", "wild", "druid", "ranger"]):
        suggestions.append("Define your connection to nature")
    
    if any(word in class_lower for word in ["rogue", "thief", "spy", "assassin"]):
        suggestions.append("Define your stealth abilities and contacts")
    
    return suggestions

def get_flexible_species_suggestions(species: str) -> List[str]:
    """Get flexible species suggestions - crude_functional.py adaptive suggestions."""
    suggestions = []
    
    # Generic suggestions that work for any species
    suggestions.extend([
        f"Explore what makes {species} unique in your world",
        f"Define {species} cultural connections and traditions",
        f"Consider how {species} interacts with other species",
        f"Create {species} physical and mental characteristics"
    ])
    
    # Keyword-based suggestions
    species_lower = species.lower()
    
    if any(word in species_lower for word in ["dragon", "draconic", "wyrm"]):
        suggestions.append("Define your draconic heritage and powers")
    
    if any(word in species_lower for word in ["elf", "fae", "fairy"]):
        suggestions.append("Consider long-lived perspective and grace")
    
    if any(word in species_lower for word in ["dwarf", "stone", "mountain"]):
        suggestions.append("Explore craftsmanship and tradition themes")
    
    if any(word in species_lower for word in ["demon", "devil", "infernal"]):
        suggestions.append("Define relationship with infernal heritage")
    
    if any(word in species_lower for word in ["celestial", "angel", "divine"]):
        suggestions.append("Explore divine nature and moral purpose")
    
    return suggestions

def get_flexible_background_suggestions(background: str) -> List[str]:
    """Get flexible background suggestions - crude_functional.py adaptive suggestions."""
    suggestions = []
    
    # Generic suggestions
    suggestions.extend([
        f"Define key experiences from your {background} background",
        f"Create connections from your {background} past",
        f"Consider how {background} shaped your personality",
        f"Explore opportunities from your {background} experience"
    ])
    
    # Keyword-based suggestions
    background_lower = background.lower()
    
    if any(word in background_lower for word in ["noble", "royal", "aristocrat"]):
        suggestions.append("Define noble obligations and political connections")
    
    if any(word in background_lower for word in ["criminal", "thief", "outlaw"]):
        suggestions.append("Create criminal contacts and past consequences")
    
    if any(word in background_lower for word in ["scholar", "sage", "academic"]):
        suggestions.append("Define area of expertise and research goals")
    
    if any(word in background_lower for word in ["soldier", "military", "guard"]):
        suggestions.append("Create military connections and combat experience")
    
    if any(word in background_lower for word in ["merchant", "trader", "guild"]):
        suggestions.append("Define trade connections and economic interests")
    
    return suggestions

def extract_themes_from_name(name: str) -> List[str]:
    """Extract themes from any name - crude_functional.py theme extraction."""
    if not name:
        return []
    
    themes = []
    name_lower = name.lower()
    
    # Flexible theme extraction based on keywords
    theme_keywords = {
        "power": ["power", "might", "strong", "force"],
        "magic": ["magic", "spell", "arcane", "mystic", "enchant"],
        "nature": ["nature", "wild", "forest", "earth", "green"],
        "divine": ["divine", "holy", "sacred", "blessed", "celestial"],
        "shadow": ["shadow", "dark", "night", "stealth", "hidden"],
        "fire": ["fire", "flame", "burn", "inferno", "heat"],
        "ice": ["ice", "frost", "cold", "winter", "freeze"],
        "storm": ["storm", "lightning", "thunder", "tempest", "wind"],
        "death": ["death", "undead", "necro", "grave", "bone"],
        "life": ["life", "heal", "growth", "renewal", "vitality"],
        "war": ["war", "battle", "combat", "fight", "warrior"],
        "peace": ["peace", "harmony", "balance", "tranquil", "serene"],
        "wisdom": ["wise", "knowledge", "sage", "scholar", "learned"],
        "chaos": ["chaos", "random", "wild", "unpredictable", "mad"],
        "order": ["order", "law", "structure", "discipline", "organized"],
        "freedom": ["free", "liberty", "independent", "rebel", "wild"],
        "honor": ["honor", "noble", "chivalry", "virtue", "righteous"],
        "trickery": ["trick", "deceit", "cunning", "clever", "sly"],
        "travel": ["travel", "journey", "wander", "explore", "nomad"],
        "forge": ["forge", "craft", "smith", "create", "build"],
        "hunt": ["hunt", "track", "predator", "stalker", "prey"]
    }
    
    for theme, keywords in theme_keywords.items():
        if any(keyword in name_lower for keyword in keywords):
            themes.append(theme)
    
    return themes

def check_logical_conflicts(character_class: str, background: str) -> List[str]:
    """Check for logical conflicts - crude_functional.py flexible conflict detection."""
    conflicts = []
    
    if not character_class or not background:
        return conflicts
    
    class_lower = character_class.lower()
    background_lower = background.lower()
    
    # Only flag truly illogical combinations, not just unusual ones
    logical_conflicts = [
        # These are logical impossibilities, not creative restrictions
        ("pacifist", "assassin"),
        ("mute", "bard"),  # Only if bard specifically requires speech
        ("blind", "archer")  # Only if archer requires sight
    ]
    
    for class_word, bg_word in logical_conflicts:
        if class_word in class_lower and bg_word in background_lower:
            conflicts.append(f"Potential logical conflict: {character_class} with {background} - consider how this works")
    
    return conflicts

def check_internal_contradictions(personality: List[str], goals: List[str]) -> List[str]:
    """Check internal contradictions - crude_functional.py contradiction detection."""
    contradictions = []
    
    if not personality or not goals:
        return contradictions
    
    # Convert to strings for analysis
    personality_str = " ".join(personality).lower() if isinstance(personality, list) else str(personality).lower()
    goals_str = " ".join(goals).lower() if isinstance(goals, list) else str(goals).lower()
    
    # Check for obvious contradictions
    contradiction_pairs = [
        ("pacifist", "destroy"),
        ("hermit", "social"),
        ("honest", "deceive"),
        ("coward", "brave")
    ]
    
    for trait, goal in contradiction_pairs:
        if trait in personality_str and goal in goals_str:
            contradictions.append(f"Potential contradiction between personality and goals - consider character growth arc")
    
    return contradictions

def extract_themes_from_text(backstory: str, personality: List[str], goals: List[str]) -> List[str]:
    """Extract themes from text - crude_functional.py text theme extraction. UNLIMITED."""
    themes = []
    
    # Combine all text
    all_text = ""
    if backstory:
        all_text += backstory.lower() + " "
    if personality:
        if isinstance(personality, list):
            all_text += " ".join(personality).lower() + " "
        else:
            all_text += str(personality).lower() + " "
    if goals:
        if isinstance(goals, list):
            all_text += " ".join(goals).lower() + " "
        else:
            all_text += str(goals).lower() + " "
    
    # Expanded theme extraction - supports any themes
    theme_keywords = {
        "revenge": ["revenge", "vengeance", "avenge", "payback"],
        "redemption": ["redeem", "atone", "forgive", "salvation"],
        "family": ["family", "parent", "sibling", "child", "relative"],
        "power": ["power", "strength", "control", "dominate", "rule"],
        "knowledge": ["learn", "study", "discover", "research", "wisdom"],
        "love": ["love", "romance", "beloved", "heart", "passion"],
        "loss": ["lost", "death", "grief", "mourn", "sorrow"],
        "freedom": ["freedom", "liberty", "escape", "chains", "bound"],
        "justice": ["justice", "right", "fair", "law", "order"],
        "discovery": ["explore", "find", "search", "quest", "journey"],
        "survival": ["survive", "endure", "live", "struggle", "fight"],
        "protection": ["protect", "defend", "guard", "shield", "safe"],
        "creation": ["create", "build", "make", "craft", "forge"],
        "destruction": ["destroy", "ruin", "end", "collapse", "break"],
        "transformation": ["change", "transform", "evolve", "become", "grow"],
        "mystery": ["mystery", "secret", "hidden", "unknown", "puzzle"],
        "friendship": ["friend", "companion", "ally", "bond", "together"],
        "rivalry": ["rival", "enemy", "compete", "oppose", "challenge"],
        "identity": ["identity", "self", "who", "am", "become"],
        "destiny": ["destiny", "fate", "chosen", "purpose", "calling"],
        "sacrifice": ["sacrifice", "give", "cost", "price", "loss"],
        "hope": ["hope", "dream", "wish", "aspire", "believe"],
        "fear": ["fear", "afraid", "terror", "dread", "scary"],
        "courage": ["brave", "courage", "bold", "fearless", "hero"],
        "betrayal": ["betray", "trust", "deceive", "lie", "false"],
        "legacy": ["legacy", "inheritance", "ancestor", "tradition", "heritage"]
    }
    
    for theme, keywords in theme_keywords.items():
        if any(keyword in all_text for keyword in keywords):
            themes.append(theme)
    
    return themes

def get_theme_content_suggestions(themes: List[str]) -> List[str]:
    """Get theme-based suggestions - crude_functional.py theme suggestions. FLEXIBLE."""
    suggestions = []
    
    theme_advice = {
        "revenge": "Add past wrongs that need addressing",
        "redemption": "Create past mistakes to overcome",
        "discovery": "Add mysteries to solve or places to explore",
        "protection": "Define what or who needs protecting",
        "family": "Develop family connections and obligations",
        "honor": "Create codes and principles to uphold",
        "power": "Define what power means to your character",
        "knowledge": "Add learning goals and intellectual pursuits",
        "love": "Develop romantic interests or deep friendships",
        "freedom": "Create constraints your character wants to escape",
        "justice": "Define moral wrongs that need righting",
        "survival": "Add challenges that test endurance",
        "transformation": "Show how your character grows and changes",
        "mystery": "Add unknown elements to uncover",
        "identity": "Explore questions of self-discovery",
        "destiny": "Create a greater purpose or calling",
        "legacy": "Connect to ancestral traditions or inheritance"
    }
    
    for theme in themes:
        if theme in theme_advice:
            suggestions.append(theme_advice[theme])
        else:
            # Generic suggestion for any theme
            suggestions.append(f"Explore how {theme} shapes your character's story")
    
    return suggestions

# ============ EXISTING FLEXIBLE CONTENT VALIDATION ============

def validate_content_source(content_type: str, source: str) -> Tuple[bool, str]:
    """Validate content source - crude_functional.py style simple validation. ACCEPTS ALL SOURCES."""
    if not content_type or not source:
        return False, "Missing content type or source"
    
    # Accept all sources - no restrictions on creativity
    official_sources = ["phb", "xgte", "tce", "mm", "dmg", "phb2024"]
    if source.lower() in official_sources:
        return True, "official"
    elif source.startswith("ua_"):
        return True, "unearthed_arcana"
    elif source.startswith("homebrew_"):
        return True, "homebrew"
    elif source.startswith("custom_"):
        return True, "custom"
    elif source.startswith("original_"):
        return True, "original"
    else:
        return True, "custom"  # Accept any source as custom

def get_content_rarity(content_item: Dict[str, Any]) -> ContentRarity:
    """Get content rarity - crude_functional.py style direct mapping. FLEXIBLE RARITY."""
    rarity_str = content_item.get("rarity", "common").lower()
    
    rarity_map = {
        "common": ContentRarity.COMMON,
        "uncommon": ContentRarity.UNCOMMON,
        "rare": ContentRarity.RARE,
        "very_rare": ContentRarity.VERY_RARE,
        "legendary": ContentRarity.LEGENDARY,
        "artifact": ContentRarity.ARTIFACT,
        "unique": ContentRarity.LEGENDARY,  # Treat unique as legendary
        "custom": ContentRarity.UNCOMMON,   # Default custom rarity
        "original": ContentRarity.RARE      # Default original rarity
    }
    
    return rarity_map.get(rarity_str, ContentRarity.COMMON)

def is_content_appropriate(content: Dict[str, Any], character_level: int) -> bool:
    """Check if content is appropriate for character level - crude_functional.py simplicity. FLEXIBLE."""
    if not content or character_level < 1:
        return True  # Default to allowing content
    
    content_level = content.get("level", 1)
    content_rarity = get_content_rarity(content)
    
    # Very flexible level-based appropriateness
    if content_level > character_level + 3:  # Allow some flexibility
        return False
    
    # Flexible rarity-based suggestions, not restrictions
    rarity_level_suggestions = {
        ContentRarity.COMMON: 1,
        ContentRarity.UNCOMMON: 2,  # More lenient
        ContentRarity.RARE: 4,      # More lenient
        ContentRarity.VERY_RARE: 8, # More lenient
        ContentRarity.LEGENDARY: 12, # More lenient
        ContentRarity.ARTIFACT: 15   # More lenient
    }
    
    suggested_level = rarity_level_suggestions.get(content_rarity, 1)
    return character_level >= suggested_level - 2  # Allow some leeway

# ============ ESSENTIAL EXPORTS ============

__all__ = [
    # Core missing functions (required by __init__.py)
    'analyze_character_content',
    'validate_content_completeness',
    'generate_content_suggestions',
    'check_content_consistency',
    'extract_character_themes',
    'summarize_character_concept',
    
    # Core validation - flexible
    'validate_content_source',
    'get_content_rarity',
    'is_content_appropriate',
    
    # Flexible supporting functions
    'calculate_content_richness',
    'get_flexible_class_suggestions',
    'get_flexible_species_suggestions',
    'get_flexible_background_suggestions',
    'get_theme_content_suggestions',
    
    # Flexible consistency checks
    'check_logical_conflicts',
    'check_internal_contradictions',
    
    # Flexible theme extraction
    'extract_themes_from_name',
    'extract_themes_from_text',
]

# Calculate content richness - same as before but included for completeness
def calculate_content_richness(character_data: Dict[str, Any]) -> float:
    """Calculate content richness - crude_functional.py richness assessment."""
    if not character_data:
        return 0.0
    
    richness_score = 0.0
    
    # Text-based richness
    text_fields = ["backstory", "personality_traits", "goals", "flaws", "ideals"]
    for field in text_fields:
        value = character_data.get(field, "")
        if value:
            if isinstance(value, str):
                richness_score += min(0.2, len(value) / 500)  # Longer descriptions = richer
            elif isinstance(value, list):
                richness_score += min(0.2, len(value) * 0.1)  # More elements = richer
    
    # Detail richness
    detail_fields = ["allies", "enemies", "connections", "equipment", "spells", "abilities", "features"]
    for field in detail_fields:
        value = character_data.get(field, [])
        if value:
            richness_score += min(0.1, len(value) * 0.02)
    
    return min(1.0, richness_score)

# ============ MODULE METADATA ============

__version__ = '1.0.0'
__description__ = 'Essential D&D content utilities - UNLIMITED CREATIVITY'
__author__ = 'D&D Character Creator Backend7'

# Backend7 architecture compliance
BACKEND7_COMPLIANCE = {
    "layer": "core/utils",
    "focus": "unlimited_content_analysis_and_validation",
    "line_target": 200,
    "dependencies": ["core.enums"],
    "philosophy": "crude_functional_inspired_unlimited_creative_content",
    "maintains_crude_functional_approach": True,
    "supports_unlimited_creativity": True
}

# Unlimited Content Philosophy
UNLIMITED_CONTENT_PRINCIPLES = {
    "no_content_restrictions": "No limits on classes, species, feats, spells, weapons, or any content",
    "creative_freedom_paramount": "All content is valid and supported",
    "flexible_validation": "Validation guides without restricting creativity",
    "adaptive_suggestions": "Suggestions work with any content type",
    "unlimited_support": "System adapts to any creative content",
    "traditional_and_new": "Supports both traditional D&D and completely new content"
}

# Supported Content Types
UNLIMITED_CONTENT_SUPPORT = {
    "classes": "Any class - traditional, homebrew, or completely original",
    "species": "Any species/race - traditional fantasy or completely unique",
    "backgrounds": "Any background concept - predefined or custom",
    "abilities": "Any abilities - magical, supernatural, or mundane",
    "equipment": "Any equipment - traditional weapons or innovative items",
    "spells": "Any spells - traditional schools or new magical systems",
    "feats": "Any feats - traditional or custom character features",
    "cultures": "Any cultural concepts - Earth-based or fantastical",
    "themes": "Any narrative themes - classic or innovative"
}