"""
D&D naming convention validation utilities.

This module provides pure functions to validate names follow D&D conventions,
supporting the Creative Content Framework's consistency and authenticity requirements.
"""

import re
from typing import List, Dict, Set, Optional, Tuple
from ..enums.content_types import ContentType


# === NAMING PATTERN DEFINITIONS ===

# D&D naming patterns by content type
SPECIES_NAME_PATTERNS = [
    r"^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?$",  # "Human", "Half Elf"
    r"^[A-Z][a-z]+-[A-Z][a-z]+$",         # "Half-Orc"
]

CLASS_NAME_PATTERNS = [
    r"^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$",  # "Fighter", "Eldritch Knight"
]

SPELL_NAME_PATTERNS = [
    r"^[A-Z][a-z]+(?:\s+[a-z]+)*(?:\s+[A-Z][a-z]+)*$",  # "Magic Missile", "Bigby's Hand"
    r"^[A-Z][a-z]+(?:'s\s+[A-Z][a-z]+)+$",               # "Tasha's Hideous Laughter"
]

EQUIPMENT_NAME_PATTERNS = [
    r"^[A-Z][a-z]+(?:\s+[a-z]+)*(?:\s+[A-Z][a-z]+)*$",  # "Longsword", "Plate Armor"
    r"^[A-Z][a-z]+(?:\s+[a-z]+)*\s+\+\d+$",             # "Sword +1"
]

FEAT_NAME_PATTERNS = [
    r"^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$",  # "Great Weapon Master"
]

# Common D&D naming elements
FANTASY_PREFIXES = {
    "Arch", "Elder", "Great", "High", "Lesser", "Ancient", "Divine", "Infernal",
    "Celestial", "Shadow", "Storm", "Fire", "Ice", "Earth", "Air", "Dark", "Light",
    "Master", "Grand", "Prime", "Superior", "Enhanced", "Blessed", "Cursed"
}

FANTASY_SUFFIXES = {
    "bane", "ward", "guard", "keeper", "slayer", "sworn", "touched", "born",
    "heart", "soul", "mind", "blade", "fist", "eye", "wing", "scale", "caller",
    "walker", "speaker", "seeker", "finder", "bearer", "wielder", "master"
}

# Problematic patterns to avoid
FORBIDDEN_PATTERNS = [
    r".*\d.*",  # Numbers in names (except enhancement bonuses)
    r"^[a-z].*",  # Lowercase start
    r".*[XxQq]{2,}.*",  # Too many X's or Q's (looks artificial)
    r".*[aeiou]{4,}.*",  # Too many consecutive vowels
    r".*[bcdfghjklmnpqrstvwxyz]{4,}.*",  # Too many consecutive consonants
]

# Terms that should be flagged for review (family-friendly content)
INAPPROPRIATE_TERMS = {
    "damn", "hell", "ass", "bitch", "bastard", "whore", "slut", "shit", "fuck",
    "piss", "crap", "bloody", "goddamn"
}

# D&D official terminology for reference
OFFICIAL_DAMAGE_TYPES = {
    "acid", "bludgeoning", "cold", "fire", "force", "lightning", "necrotic",
    "piercing", "poison", "psychic", "radiant", "slashing", "thunder"
}

OFFICIAL_CONDITIONS = {
    "blinded", "charmed", "deafened", "frightened", "grappled", "incapacitated",
    "invisible", "paralyzed", "petrified", "poisoned", "prone", "restrained",
    "stunned", "unconscious"
}


# === CORE VALIDATION FUNCTIONS ===

def validate_content_name(name: str, content_type: ContentType) -> List[str]:
    """
    Validate a content name follows D&D naming conventions.
    
    Args:
        name: Name to validate
        content_type: Type of content being named
        
    Returns:
        List of validation issues (empty if valid)
    """
    issues = []
    
    if not name or not name.strip():
        issues.append("Name cannot be empty")
        return issues
    
    name = name.strip()
    
    # Basic validation
    issues.extend(_validate_basic_format(name))
    issues.extend(_validate_length(name, content_type))
    issues.extend(_validate_characters(name))
    issues.extend(_validate_appropriateness(name))
    
    # Content-type specific validation
    if content_type == ContentType.SPECIES:
        issues.extend(_validate_species_name(name))
    elif content_type == ContentType.CHARACTER_CLASS:
        issues.extend(_validate_class_name(name))
    elif content_type == ContentType.SPELL:
        issues.extend(_validate_spell_name(name))
    elif content_type == ContentType.EQUIPMENT:
        issues.extend(_validate_equipment_name(name))
    elif content_type == ContentType.FEAT:
        issues.extend(_validate_feat_name(name))
    
    # Common naming issues
    issues.extend(_check_common_naming_issues(name))
    
    return issues


def suggest_name_improvements(name: str, content_type: ContentType) -> List[str]:
    """
    Suggest improvements for a content name.
    
    Args:
        name: Original name
        content_type: Type of content
        
    Returns:
        List of suggested improvements
    """
    suggestions = []
    
    if not name or not name.strip():
        return ["Provide a name for the content"]
    
    name = name.strip()
    
    # Capitalization suggestions
    if not name[0].isupper():
        suggestions.append(f"Capitalize first letter: '{name.capitalize()}'")
    
    # Title case for multi-word names
    words = name.split()
    if len(words) > 1:
        title_case = ' '.join(_capitalize_word(word, i) for i, word in enumerate(words))
        if title_case != name:
            suggestions.append(f"Consider title case: '{title_case}'")
    
    # Fantasy element suggestions
    if _is_mundane_name(name):
        suggestions.extend(_suggest_fantasy_elements(name, content_type))
    
    # Pattern-specific suggestions
    patterns = _get_patterns_for_content_type(content_type)
    if patterns and not any(re.match(pattern, name) for pattern in patterns):
        suggestions.append(f"Consider following {content_type.value} naming patterns")
    
    return suggestions


def generate_name_variations(base_name: str, content_type: ContentType, count: int = 5) -> List[str]:
    """
    Generate variations of a base name.
    
    Args:
        base_name: Base name to vary
        content_type: Type of content
        count: Number of variations to generate
        
    Returns:
        List of name variations
    """
    if not base_name or not base_name.strip():
        return []
    
    variations = []
    base_name = base_name.strip()
    words = base_name.split()
    base_word = words[0]
    
    # Prefix variations
    prefix_count = min(count // 3, len(FANTASY_PREFIXES))
    for prefix in list(FANTASY_PREFIXES)[:prefix_count]:
        variation = f"{prefix} {base_name}"
        if len(variation) <= 50:  # Respect length limits
            variations.append(variation)
    
    # Suffix variations
    suffix_count = min(count // 3, len(FANTASY_SUFFIXES))
    for suffix in list(FANTASY_SUFFIXES)[:suffix_count]:
        if len(words) == 1:
            variation = f"{base_word}{suffix}"
        else:
            variation = f"{base_name} {suffix.capitalize()}"
        
        if len(variation) <= 50:
            variations.append(variation)
    
    # Structural variations
    if len(words) > 1:
        variations.append(f"{words[0]} of {words[1]}")
        variations.append(f"Greater {base_name}")
        if len(words) == 2:
            variations.append(f"{words[1]} {words[0]}")
    
    # Enhancement variations for equipment
    if content_type == ContentType.EQUIPMENT:
        for bonus in ["+1", "+2", "+3"]:
            variation = f"{base_name} {bonus}"
            if len(variation) <= 50:
                variations.append(variation)
    
    return variations[:count]


def validate_name_uniqueness(name: str, existing_names: Set[str]) -> List[str]:
    """
    Check if name conflicts with existing content names.
    
    Args:
        name: Name to check
        existing_names: Set of existing names
        
    Returns:
        List of uniqueness issues
    """
    issues = []
    
    if not name or not name.strip():
        return issues
    
    name = name.strip()
    
    # Exact match
    if name in existing_names:
        issues.append("Name already exists")
        return issues
    
    # Similar name check
    name_lower = name.lower()
    for existing in existing_names:
        if _names_too_similar(name_lower, existing.lower()):
            issues.append(f"Name too similar to existing: '{existing}'")
    
    return issues


def check_name_authenticity(name: str, content_type: ContentType) -> Dict[str, any]:
    """
    Analyze how authentic a name sounds for D&D fantasy setting.
    
    Args:
        name: Name to analyze
        content_type: Type of content
        
    Returns:
        Dictionary with authenticity analysis
    """
    if not name or not name.strip():
        return {
            "authenticity_score": 0.0,
            "issues": ["Name is empty"],
            "suggestions": ["Provide a name"]
        }
    
    name = name.strip()
    score = 0.5  # Start with neutral
    issues = []
    suggestions = []
    
    # Pattern matching
    patterns = _get_patterns_for_content_type(content_type)
    if patterns:
        if any(re.match(pattern, name) for pattern in patterns):
            score += 0.3
        else:
            issues.append(f"Doesn't follow {content_type.value} naming patterns")
            suggestions.append(f"Consider {content_type.value} naming conventions")
    
    # Fantasy element check
    if _has_fantasy_elements(name):
        score += 0.2
    else:
        issues.append("Lacks fantasy elements")
        suggestions.extend(_suggest_fantasy_elements(name, content_type))
    
    # Length appropriateness
    if 3 <= len(name) <= 25:
        score += 0.1
    elif len(name) < 3:
        issues.append("Name too short")
        suggestions.append("Make name longer")
    elif len(name) > 25:
        issues.append("Name too long")
        suggestions.append("Shorten name")
    
    # Forbidden patterns
    for pattern in FORBIDDEN_PATTERNS:
        if re.match(pattern, name, re.IGNORECASE):
            score -= 0.2
            issues.append("Contains problematic patterns")
            break
    
    # Normalize score
    score = max(0.0, min(1.0, score))
    
    return {
        "authenticity_score": score,
        "issues": issues,
        "suggestions": suggestions,
        "pattern_match": any(re.match(pattern, name) for pattern in patterns) if patterns else False,
        "has_fantasy_elements": _has_fantasy_elements(name)
    }


# === HELPER FUNCTIONS ===

def _validate_basic_format(name: str) -> List[str]:
    """Validate basic name formatting."""
    issues = []
    
    # Check forbidden patterns
    for pattern in FORBIDDEN_PATTERNS:
        if re.match(pattern, name, re.IGNORECASE):
            if r"\d" in pattern:
                issues.append("Name should not contain numbers")
            elif r"^[a-z]" in pattern:
                issues.append("Name should start with capital letter")
            else:
                issues.append("Name contains problematic patterns")
            break
    
    return issues


def _validate_length(name: str, content_type: ContentType) -> List[str]:
    """Validate name length based on content type."""
    issues = []
    
    # Content-type specific length limits
    limits = {
        ContentType.SPECIES: (2, 30),
        ContentType.CHARACTER_CLASS: (3, 40),
        ContentType.SPELL: (3, 50),
        ContentType.EQUIPMENT: (3, 60),
        ContentType.FEAT: (3, 40),
    }
    
    min_len, max_len = limits.get(content_type, (2, 50))
    
    if len(name) < min_len:
        issues.append(f"Name too short (minimum {min_len} characters for {content_type.value})")
    elif len(name) > max_len:
        issues.append(f"Name too long (maximum {max_len} characters for {content_type.value})")
    
    return issues


def _validate_characters(name: str) -> List[str]:
    """Validate allowed characters in name."""
    issues = []
    
    # Basic character validation
    if not re.match(r"^[A-Za-z\s\-'\.]*$", name):
        issues.append("Name contains invalid characters (only letters, spaces, hyphens, apostrophes, and periods allowed)")
    
    # Check for excessive punctuation
    if name.count("'") > 2:
        issues.append("Too many apostrophes (maximum 2)")
    if name.count("-") > 2:
        issues.append("Too many hyphens (maximum 2)")
    if name.count(".") > 1:
        issues.append("Too many periods (maximum 1)")
    
    return issues


def _validate_appropriateness(name: str) -> List[str]:
    """Check for inappropriate content."""
    issues = []
    
    name_lower = name.lower()
    for term in INAPPROPRIATE_TERMS:
        if term in name_lower:
            issues.append("Name contains inappropriate language")
            break
    
    return issues


def _validate_species_name(name: str) -> List[str]:
    """Validate species-specific naming rules."""
    issues = []
    
    # Species names should be concise
    if len(name.split()) > 3:
        issues.append("Species names should be concise (3 words or fewer)")
    
    # Check patterns
    if not any(re.match(pattern, name) for pattern in SPECIES_NAME_PATTERNS):
        issues.append("Name doesn't follow typical species naming patterns")
    
    return issues


def _validate_class_name(name: str) -> List[str]:
    """Validate class-specific naming rules."""
    issues = []
    
    if len(name.split()) > 4:
        issues.append("Class names should be reasonably concise (4 words or fewer)")
    
    if not any(re.match(pattern, name) for pattern in CLASS_NAME_PATTERNS):
        issues.append("Name doesn't follow typical class naming patterns")
    
    return issues


def _validate_spell_name(name: str) -> List[str]:
    """Validate spell-specific naming rules."""
    issues = []
    
    # Check possessive format
    if "'" in name and not re.search(r"'s\s", name):
        issues.append("Possessive spell names should use \"'s\" format (e.g., \"Bigby's Hand\")")
    
    if not any(re.match(pattern, name) for pattern in SPELL_NAME_PATTERNS):
        issues.append("Name doesn't follow typical spell naming patterns")
    
    return issues


def _validate_equipment_name(name: str) -> List[str]:
    """Validate equipment-specific naming rules."""
    issues = []
    
    # Check enhancement bonus format
    if re.search(r"\+\d+", name):
        if not re.search(r"\s\+\d+$", name):
            issues.append("Enhancement bonuses should be at the end (e.g., 'Sword +1')")
    
    if not any(re.match(pattern, name) for pattern in EQUIPMENT_NAME_PATTERNS):
        issues.append("Name doesn't follow typical equipment naming patterns")
    
    return issues


def _validate_feat_name(name: str) -> List[str]:
    """Validate feat-specific naming rules."""
    issues = []
    
    if len(name.split()) > 5:
        issues.append("Feat names should be reasonably concise (5 words or fewer)")
    
    if not any(re.match(pattern, name) for pattern in FEAT_NAME_PATTERNS):
        issues.append("Name doesn't follow typical feat naming patterns")
    
    return issues


def _check_common_naming_issues(name: str) -> List[str]:
    """Check for common naming problems."""
    issues = []
    
    words = name.lower().split()
    
    # Check for repeated words
    if len(words) != len(set(words)):
        issues.append("Name contains repeated words")
    
    # Check for awkward vowel/consonant combinations
    if re.search(r"[aeiou]{3,}", name.lower()):
        issues.append("Name has too many consecutive vowels")
    
    if re.search(r"[bcdfghjklmnpqrstvwxyz]{3,}", name.lower()):
        issues.append("Name has too many consecutive consonants")
    
    return issues


def _get_patterns_for_content_type(content_type: ContentType) -> List[str]:
    """Get naming patterns for a specific content type."""
    pattern_map = {
        ContentType.SPECIES: SPECIES_NAME_PATTERNS,
        ContentType.CHARACTER_CLASS: CLASS_NAME_PATTERNS,
        ContentType.SPELL: SPELL_NAME_PATTERNS,
        ContentType.EQUIPMENT: EQUIPMENT_NAME_PATTERNS,
        ContentType.FEAT: FEAT_NAME_PATTERNS,
    }
    return pattern_map.get(content_type, [])


def _capitalize_word(word: str, position: int) -> str:
    """Capitalize word appropriately based on position."""
    # Don't capitalize articles, prepositions, etc. unless they're first
    small_words = {"of", "the", "and", "or", "but", "in", "on", "at", "to", "for", "with", "by"}
    
    if position == 0 or word.lower() not in small_words:
        return word.capitalize()
    return word.lower()


def _is_mundane_name(name: str) -> bool:
    """Check if a name lacks fantasy elements."""
    return not _has_fantasy_elements(name)


def _has_fantasy_elements(name: str) -> bool:
    """Check if name contains fantasy elements."""
    name_lower = name.lower()
    
    # Check for fantasy prefixes/suffixes
    for prefix in FANTASY_PREFIXES:
        if name_lower.startswith(prefix.lower()):
            return True
    
    for suffix in FANTASY_SUFFIXES:
        if name_lower.endswith(suffix.lower()):
            return True
    
    # Check for fantasy patterns (apostrophes, hyphens)
    if "'" in name or "-" in name:
        return True
    
    # Check for D&D terminology
    for term in OFFICIAL_DAMAGE_TYPES | OFFICIAL_CONDITIONS:
        if term in name_lower:
            return True
    
    return False


def _suggest_fantasy_elements(name: str, content_type: ContentType) -> List[str]:
    """Suggest fantasy elements to add to a mundane name."""
    suggestions = []
    
    # Suggest prefixes
    prefix_suggestions = list(FANTASY_PREFIXES)[:3]
    for prefix in prefix_suggestions:
        suggestions.append(f"Add fantasy prefix: '{prefix} {name}'")
    
    # Suggest suffixes based on content type
    if content_type == ContentType.EQUIPMENT:
        relevant_suffixes = ["bane", "ward", "blade", "fist"]
    elif content_type == ContentType.SPELL:
        relevant_suffixes = ["caller", "speaker", "seeker"]
    else:
        relevant_suffixes = ["born", "touched", "sworn"]
    
    for suffix in relevant_suffixes[:2]:
        if len(name.split()) == 1:
            suggestions.append(f"Add fantasy suffix: '{name}{suffix}'")
        else:
            suggestions.append(f"Add fantasy suffix: '{name} {suffix.capitalize()}'")
    
    return suggestions


def _names_too_similar(name1: str, name2: str) -> bool:
    """Check if two names are too similar."""
    # Simple similarity check
    if len(name1) != len(name2):
        return False
    
    # Check if they differ by only 1-2 characters
    differences = sum(c1 != c2 for c1, c2 in zip(name1, name2))
    return differences <= 2 and len(name1) > 3