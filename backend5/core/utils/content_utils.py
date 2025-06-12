"""
Pure content manipulation utilities for the D&D Creative Content Framework.

This module provides utility functions for processing, transforming, and
analyzing generated content across all content types.
"""

from typing import Dict, List, Optional, Any, Set, Tuple
import re
from datetime import datetime
from ..entities.character import Character
from ..entities.generated_content import GeneratedContent
from ..entities.character_concept import CharacterConcept
from ..enums.content_types import ContentType


# === CHARACTER UTILITIES ===

class CharacterFormatter:
    """Utility class for formatting character data."""
    
    @staticmethod
    def format_character_summary(character: Character) -> str:
        """Format character as a readable summary."""
        summary = character.get_character_summary()
        
        return f"""
=== {summary['name']} ===
Level {summary['level']} {summary['species']} {summary['class']}
Hit Points: {summary['hit_points']}
Armor Class: {summary['armor_class']}
Proficiency Bonus: +{summary['proficiency_bonus']}

Ability Scores:
  STR: {character.strength} ({character.get_ability_modifier('strength'):+d})
  DEX: {character.dexterity} ({character.get_ability_modifier('dexterity'):+d})
  CON: {character.constitution} ({character.get_ability_modifier('constitution'):+d})
  INT: {character.intelligence} ({character.get_ability_modifier('intelligence'):+d})
  WIS: {character.wisdom} ({character.get_ability_modifier('wisdom'):+d})
  CHA: {character.charisma} ({character.get_ability_modifier('charisma'):+d})
        """.strip()
    
    @staticmethod
    def format_character_sheet(character: Character) -> str:
        """Format character as a complete character sheet."""
        summary = CharacterFormatter.format_character_summary(character)
        
        # Add equipment, spells, features, etc.
        equipment_section = ""
        if character.equipment:
            equipment_section = "\nEquipment:\n" + "\n".join(f"  - {item}" for item in character.equipment)
        
        spell_section = ""
        if character.spells:
            spell_section = "\nSpells:\n" + "\n".join(f"  - {spell}" for spell in character.spells)
        
        return f"{summary}{equipment_section}{spell_section}"
    
    @staticmethod
    def format_level_progression(character: Character) -> str:
        """Format character level progression summary."""
        if not character.is_multiclass:
            return f"Level {character.total_level} {character.primary_class}"
        
        class_levels = [f"{cls} {lvl}" for cls, lvl in character.character_classes.items()]
        return f"Level {character.total_level} ({'/'.join(class_levels)})"


class CharacterValidator:
    """Utility class for basic character validation."""
    
    @staticmethod
    def validate_character_data(data: Dict[str, Any]) -> List[str]:
        """Validate basic character data structure."""
        errors = []
        
        # Required fields
        required_fields = ["name", "species"]
        for field in required_fields:
            if field not in data or not data[field]:
                errors.append(f"Missing required field: {field}")
        
        # Ability scores
        if "ability_scores" in data:
            for ability, score in data["ability_scores"].items():
                if not isinstance(score, int) or score < 1 or score > 30:
                    errors.append(f"Invalid {ability} score: {score}")
        
        return errors
    
    @staticmethod
    def validate_level_data(classes: Dict[str, int]) -> List[str]:
        """Validate character class levels."""
        errors = []
        
        if not classes:
            errors.append("Character must have at least one class level")
            return errors
        
        total_level = sum(classes.values())
        if total_level > 20:
            errors.append(f"Total level ({total_level}) exceeds maximum (20)")
        
        for class_name, level in classes.items():
            if level < 1 or level > 20:
                errors.append(f"Invalid level for {class_name}: {level}")
        
        return errors


# === CONTENT MANIPULATION ===

def extract_themes_from_content(content: GeneratedContent) -> List[str]:
    """Extract thematic keywords from generated content."""
    themes = []
    
    # From explicit themes
    if hasattr(content, 'themes') and content.themes:
        themes.extend(content.themes)
    
    # From description text
    if content.description:
        themes.extend(_extract_keywords_from_text(content.description))
    
    # From mechanical text
    if hasattr(content, 'mechanical_description') and content.mechanical_description:
        themes.extend(_extract_keywords_from_text(content.mechanical_description))
    
    # Remove duplicates and return
    return list(set(themes))


def merge_content_themes(content_list: List[GeneratedContent]) -> Dict[str, int]:
    """Merge themes from multiple content pieces, counting frequency."""
    theme_counts = {}
    
    for content in content_list:
        themes = extract_themes_from_content(content)
        for theme in themes:
            theme_counts[theme] = theme_counts.get(theme, 0) + 1
    
    return theme_counts


def filter_content_by_theme(
    content_list: List[GeneratedContent], 
    required_themes: List[str],
    forbidden_themes: List[str] = None
) -> List[GeneratedContent]:
    """Filter content by thematic requirements."""
    if forbidden_themes is None:
        forbidden_themes = []
    
    filtered = []
    
    for content in content_list:
        content_themes = [theme.lower() for theme in extract_themes_from_content(content)]
        
        # Check required themes
        has_required = all(
            any(req.lower() in theme for theme in content_themes)
            for req in required_themes
        )
        
        # Check forbidden themes
        has_forbidden = any(
            any(forbidden.lower() in theme for theme in content_themes)
            for forbidden in forbidden_themes
        )
        
        if has_required and not has_forbidden:
            filtered.append(content)
    
    return filtered


def calculate_thematic_compatibility(
    content1: GeneratedContent,
    content2: GeneratedContent
) -> float:
    """Calculate thematic compatibility between two content pieces (0.0-1.0)."""
    themes1 = set(theme.lower() for theme in extract_themes_from_content(content1))
    themes2 = set(theme.lower() for theme in extract_themes_from_content(content2))
    
    if not themes1 and not themes2:
        return 0.5  # Neutral if no themes
    
    if not themes1 or not themes2:
        return 0.3  # Low compatibility if one has no themes
    
    # Jaccard similarity
    intersection = themes1 & themes2
    union = themes1 | themes2
    
    return len(intersection) / len(union) if union else 0.0


def group_content_by_theme(content_list: List[GeneratedContent]) -> Dict[str, List[GeneratedContent]]:
    """Group content by dominant themes."""
    theme_groups = {}
    
    for content in content_list:
        themes = extract_themes_from_content(content)
        
        # Use first theme as primary grouping
        primary_theme = themes[0] if themes else "unthemed"
        
        if primary_theme not in theme_groups:
            theme_groups[primary_theme] = []
        
        theme_groups[primary_theme].append(content)
    
    return theme_groups


# === CONTENT ANALYSIS ===

def analyze_content_complexity(content: GeneratedContent) -> Dict[str, Any]:
    """Analyze the complexity of generated content."""
    complexity_factors = {
        "text_length": len(content.description) if content.description else 0,
        "mechanical_complexity": 0,
        "choice_points": 0,
        "conditional_effects": 0
    }
    
    # Analyze mechanical text for complexity indicators
    if hasattr(content, 'mechanical_description') and content.mechanical_description:
        mech_text = content.mechanical_description.lower()
        
        # Count complexity indicators
        complexity_factors["choice_points"] = mech_text.count("choose") + mech_text.count("select")
        complexity_factors["conditional_effects"] = mech_text.count("if") + mech_text.count("when")
        
        # Simple mechanical complexity based on keywords
        complex_keywords = ["advantage", "disadvantage", "resistance", "immunity", "spell", "ability"]
        complexity_factors["mechanical_complexity"] = sum(
            mech_text.count(keyword) for keyword in complex_keywords
        )
    
    # Calculate overall complexity score
    max_text_length = 1000  # Arbitrary threshold
    normalized_length = min(1.0, complexity_factors["text_length"] / max_text_length)
    
    mechanical_score = min(1.0, complexity_factors["mechanical_complexity"] / 10)
    choice_score = min(1.0, complexity_factors["choice_points"] / 5)
    conditional_score = min(1.0, complexity_factors["conditional_effects"] / 3)
    
    overall_complexity = (normalized_length + mechanical_score + choice_score + conditional_score) / 4
    
    return {
        **complexity_factors,
        "overall_complexity_score": overall_complexity,
        "complexity_rating": _get_complexity_rating(overall_complexity)
    }


def find_content_dependencies(content: GeneratedContent) -> List[str]:
    """Find what other content this piece depends on."""
    dependencies = []
    
    if not content.mechanical_description:
        return dependencies
    
    text = content.mechanical_description.lower()
    
    # Look for references to other content
    dependency_patterns = [
        r"requires? (\w+)",
        r"must have (\w+)",
        r"prerequisite[s]?:? (\w+)",
        r"only if you have (\w+)"
    ]
    
    for pattern in dependency_patterns:
        matches = re.findall(pattern, text)
        dependencies.extend(matches)
    
    return list(set(dependencies))  # Remove duplicates


def suggest_complementary_content(
    base_content: GeneratedContent,
    available_content: List[GeneratedContent],
    max_suggestions: int = 5
) -> List[Tuple[GeneratedContent, float]]:
    """Suggest content that complements the base content."""
    suggestions = []
    
    base_themes = extract_themes_from_content(base_content)
    
    for content in available_content:
        if content.id == base_content.id:
            continue  # Skip self
        
        # Calculate compatibility
        compatibility = calculate_thematic_compatibility(base_content, content)
        
        # Boost score for different content types (synergy)
        if content.content_type != base_content.content_type:
            compatibility *= 1.2
        
        # Boost for complementary mechanics
        if _has_complementary_mechanics(base_content, content):
            compatibility *= 1.3
        
        suggestions.append((content, compatibility))
    
    # Sort by compatibility and return top suggestions
    suggestions.sort(key=lambda x: x[1], reverse=True)
    return suggestions[:max_suggestions]


# === HELPER FUNCTIONS ===

def _extract_keywords_from_text(text: str) -> List[str]:
    """Extract meaningful keywords from descriptive text."""
    if not text:
        return []
    
    # Simple keyword extraction
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())  # Words 4+ characters
    
    # Filter out common words
    stop_words = {
        "this", "that", "with", "from", "they", "them", "their", "have", "been",
        "will", "would", "could", "should", "might", "must", "shall", "were",
        "when", "where", "what", "which", "while", "until", "since", "after",
        "before", "during", "through", "over", "under", "above", "below"
    }
    
    keywords = [word for word in words if word not in stop_words and len(word) > 3]
    
    # Remove duplicates while preserving order
    seen = set()
    unique_keywords = []
    for keyword in keywords:
        if keyword not in seen:
            seen.add(keyword)
            unique_keywords.append(keyword)
    
    return unique_keywords[:10]  # Limit to top 10 keywords


def _get_complexity_rating(score: float) -> str:
    """Convert complexity score to rating."""
    if score < 0.2:
        return "Very Simple"
    elif score < 0.4:
        return "Simple"
    elif score < 0.6:
        return "Moderate"
    elif score < 0.8:
        return "Complex"
    else:
        return "Very Complex"


def _has_complementary_mechanics(content1: GeneratedContent, content2: GeneratedContent) -> bool:
    """Check if two content pieces have complementary mechanics."""
    if not (content1.mechanical_description and content2.mechanical_description):
        return False
    
    text1 = content1.mechanical_description.lower()
    text2 = content2.mechanical_description.lower()
    
    # Look for complementary patterns
    complementary_pairs = [
        ("attack", "damage"),
        ("defense", "armor"),
        ("spell", "magic"),
        ("heal", "support"),
        ("buff", "enhance"),
        ("stealth", "sneak"),
        ("social", "charisma")
    ]
    
    for word1, word2 in complementary_pairs:
        if (word1 in text1 and word2 in text2) or (word2 in text1 and word1 in text2):
            return True
    
    return False


# === CONTENT SERIALIZATION ===

def serialize_content_collection(content_list: List[GeneratedContent]) -> Dict[str, Any]:
    """Serialize a collection of content to a structured format."""
    return {
        "content_count": len(content_list),
        "content_by_type": {
            content_type.value: [
                content.to_dict() for content in content_list
                if content.content_type == content_type
            ]
            for content_type in ContentType
        },
        "themes": merge_content_themes(content_list),
        "created_at": datetime.now().isoformat()
    }


def deserialize_content_collection(data: Dict[str, Any]) -> List[GeneratedContent]:
    """Deserialize a content collection from structured format."""
    content_list = []
    
    for content_type_str, content_data_list in data.get("content_by_type", {}).items():
        for content_data in content_data_list:
            content = GeneratedContent.from_dict(content_data)
            content_list.append(content)
    
    return content_list

"""
Content manipulation and utility functions.

This module provides pure functions for manipulating and analyzing D&D content,
supporting the Creative Content Framework's content generation and validation.
"""

from typing import Dict, List, Optional, Any, Set, Tuple
import re
from ..enums.content_types import ContentType
from ..enums.dnd_constants import Ability, Skill


def normalize_content_name(name: str) -> str:
    """
    Normalize content name to standard format.
    
    Args:
        name: Raw content name
        
    Returns:
        Normalized name in Title Case
    """
    if not name:
        return ""
    
    # Remove extra whitespace and convert to title case
    normalized = re.sub(r'\s+', ' ', name.strip()).title()
    
    # Handle common D&D naming conventions
    normalized = re.sub(r'\bOf\b', 'of', normalized)
    normalized = re.sub(r'\bThe\b', 'the', normalized)
    normalized = re.sub(r'\bAnd\b', 'and', normalized)
    
    return normalized


def extract_content_themes(content_data: Dict[str, Any]) -> List[str]:
    """
    Extract thematic keywords from content data.
    
    Args:
        content_data: Content dictionary
        
    Returns:
        List of extracted themes
    """
    themes = []
    
    # Common fields that contain thematic information
    thematic_fields = ["description", "flavor_text", "background", "lore", "origin"]
    
    for field in thematic_fields:
        if field in content_data and isinstance(content_data[field], str):
            text = content_data[field].lower()
            
            # Extract adjectives and descriptive words
            words = re.findall(r'\b[a-z]{4,}\b', text)
            
            # Filter for thematic words (simple heuristic)
            thematic_words = [
                word for word in words 
                if word not in _get_common_words() and len(word) > 3
            ]
            
            themes.extend(thematic_words[:5])  # Limit per field
    
    # Deduplicate and return
    return list(set(themes))


def calculate_content_similarity(content1: Dict[str, Any], content2: Dict[str, Any]) -> float:
    """
    Calculate similarity between two pieces of content.
    
    Args:
        content1: First content dictionary
        content2: Second content dictionary
        
    Returns:
        Similarity score (0.0 to 1.0)
    """
    # Extract comparable features
    features1 = _extract_comparable_features(content1)
    features2 = _extract_comparable_features(content2)
    
    # Calculate Jaccard similarity
    intersection = len(features1 & features2)
    union = len(features1 | features2)
    
    if union == 0:
        return 0.0
    
    return intersection / union


def merge_content_attributes(base_content: Dict[str, Any], additional_content: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge two content dictionaries, combining compatible attributes.
    
    Args:
        base_content: Base content dictionary
        additional_content: Additional content to merge
        
    Returns:
        Merged content dictionary
    """
    merged = base_content.copy()
    
    for key, value in additional_content.items():
        if key not in merged:
            merged[key] = value
        elif isinstance(value, list) and isinstance(merged[key], list):
            # Merge lists, avoiding duplicates
            merged[key] = list(set(merged[key] + value))
        elif isinstance(value, dict) and isinstance(merged[key], dict):
            # Recursively merge dictionaries
            merged[key] = merge_content_attributes(merged[key], value)
        # For other types, keep the base value (no overwrite)
    
    return merged


def validate_content_structure(content_data: Dict[str, Any], content_type: ContentType) -> List[str]:
    """
    Validate content structure matches expected format for content type.
    
    Args:
        content_data: Content dictionary to validate
        content_type: Expected content type
        
    Returns:
        List of structural validation issues
    """
    issues = []
    
    # Required fields by content type
    required_fields = _get_required_fields(content_type)
    
    for field in required_fields:
        if field not in content_data:
            issues.append(f"Missing required field: {field}")
        elif not content_data[field]:
            issues.append(f"Empty required field: {field}")
    
    # Type-specific validations
    if content_type == ContentType.SPECIES:
        issues.extend(_validate_species_structure(content_data))
    elif content_type == ContentType.CHARACTER_CLASS:
        issues.extend(_validate_class_structure(content_data))
    elif content_type == ContentType.SPELL:
        issues.extend(_validate_spell_structure(content_data))
    
    return issues


def generate_content_summary(content_data: Dict[str, Any], content_type: ContentType) -> str:
    """
    Generate a concise summary of content for display.
    
    Args:
        content_data: Content dictionary
        content_type: Content type
        
    Returns:
        Summary string
    """
    name = content_data.get("name", "Unnamed Content")
    
    if content_type == ContentType.SPECIES:
        traits = content_data.get("racial_features", [])
        return f"{name}: {len(traits)} racial features"
    
    elif content_type == ContentType.CHARACTER_CLASS:
        hit_die = content_data.get("hit_die", "?")
        return f"{name}: d{hit_die} hit die, {_get_class_role(content_data)}"
    
    elif content_type == ContentType.SPELL:
        level = content_data.get("level", 0)
        school = content_data.get("school", "Unknown")
        return f"{name}: Level {level} {school} spell"
    
    elif content_type == ContentType.EQUIPMENT:
        item_type = content_data.get("type", "Item")
        return f"{name}: {item_type}"
    
    else:
        return f"{name}: {content_type.value}"


def extract_mechanical_keywords(content_data: Dict[str, Any]) -> Set[str]:
    """
    Extract mechanical keywords that affect balance or gameplay.
    
    Args:
        content_data: Content dictionary
        
    Returns:
        Set of mechanical keywords
    """
    keywords = set()
    
    # Text fields to analyze
    text_fields = ["description", "effect", "features", "abilities"]
    
    for field in text_fields:
        if field in content_data:
            text = str(content_data[field]).lower()
            
            # Extract mechanical terms
            mechanical_terms = [
                "advantage", "disadvantage", "resistance", "immunity", "vulnerability",
                "proficiency", "expertise", "critical", "damage", "healing", "temporary",
                "bonus action", "reaction", "concentration", "ritual", "spell slot"
            ]
            
            for term in mechanical_terms:
                if term in text:
                    keywords.add(term)
    
    return keywords


# Helper functions
def _get_common_words() -> Set[str]:
    """Get set of common English words to filter out of themes."""
    return {
        "the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by",
        "from", "up", "about", "into", "over", "after", "this", "that", "these", "those",
        "can", "could", "will", "would", "should", "may", "might", "must", "have", "has",
        "had", "is", "are", "was", "were", "be", "been", "being", "do", "does", "did"
    }


def _extract_comparable_features(content: Dict[str, Any]) -> Set[str]:
    """Extract features that can be compared between content."""
    features = set()
    
    # Add mechanical keywords
    features.update(extract_mechanical_keywords(content))
    
    # Add themes
    features.update(extract_content_themes(content))
    
    # Add specific attributes
    if "damage_type" in content:
        features.add(f"damage_type:{content['damage_type']}")
    
    if "school" in content:  # For spells
        features.add(f"school:{content['school']}")
    
    return features


def _get_required_fields(content_type: ContentType) -> List[str]:
    """Get required fields for each content type."""
    base_fields = ["name", "description"]
    
    if content_type == ContentType.SPECIES:
        return base_fields + ["ability_score_increases", "size", "speed"]
    elif content_type == ContentType.CHARACTER_CLASS:
        return base_fields + ["hit_die", "primary_ability", "saving_throw_proficiencies"]
    elif content_type == ContentType.SPELL:
        return base_fields + ["level", "school", "casting_time", "range", "duration"]
    elif content_type == ContentType.EQUIPMENT:
        return base_fields + ["type", "rarity"]
    else:
        return base_fields


def _validate_species_structure(content_data: Dict[str, Any]) -> List[str]:
    """Validate species-specific structure."""
    issues = []
    
    # Check ability score increases
    asi = content_data.get("ability_score_increases", {})
    if asi:
        total_asi = sum(asi.values())
        if total_asi > 3:
            issues.append("Total ability score increases exceed recommended maximum (3)")
    
    return issues


def _validate_class_structure(content_data: Dict[str, Any]) -> List[str]:
    """Validate class-specific structure."""
    issues = []
    
    # Check hit die
    hit_die = content_data.get("hit_die")
    if hit_die and hit_die not in [6, 8, 10, 12]:
        issues.append(f"Unusual hit die size: d{hit_die}")
    
    return issues


def _validate_spell_structure(content_data: Dict[str, Any]) -> List[str]:
    """Validate spell-specific structure."""
    issues = []
    
    # Check spell level
    level = content_data.get("level", 0)
    if not (0 <= level <= 9):
        issues.append(f"Invalid spell level: {level} (must be 0-9)")
    
    return issues


def _get_class_role(class_data: Dict[str, Any]) -> str:
    """Determine class role from class data."""
    hit_die = class_data.get("hit_die", 8)
    
    if hit_die >= 10:
        return "Tank/Defender"
    elif "spellcasting" in class_data:
        return "Spellcaster"
    else:
        return "Martial"