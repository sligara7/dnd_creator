"""
Essential D&D Text Processing Utilities

Streamlined text processing utilities following backend7 architecture.
Based on crude_functional.py patterns and essential-only philosophy.
Maintains overarching functionality of crude_functional.py approach.

Text processing focuses on D&D-specific text manipulation with simple, direct functions.
"""

from typing import Dict, List, Tuple, Optional, Any, Union
import re

# ============ CORE TEXT PROCESSING ============

def clean_text(text: str) -> str:
    """Clean and normalize text - crude_functional.py simple cleaning."""
    if not text:
        return ""
    
    # Simple cleaning - remove extra whitespace and normalize
    cleaned = ' '.join(text.split()).strip()
    return cleaned

def normalize_dnd_text(text: str) -> str:
    """Normalize D&D text - crude_functional.py D&D-specific normalization."""
    if not text:
        return ""
    
    # D&D-specific text normalization
    normalized = text.strip()
    
    # Convert common D&D abbreviations to standard format
    dnd_replacements = {
        "str": "strength",
        "dex": "dexterity", 
        "con": "constitution",
        "int": "intelligence",
        "wis": "wisdom",
        "cha": "charisma",
        "ac": "armor_class",
        "hp": "hit_points",
        "sp": "spell_points"
    }
    
    normalized_lower = normalized.lower()
    for abbrev, full in dnd_replacements.items():
        if normalized_lower == abbrev:
            return full
    
    return normalized

def sanitize_name(name: str) -> str:
    """Sanitize character/item names - crude_functional.py name cleaning."""
    if not name:
        return ""
    
    # Keep letters, numbers, spaces, apostrophes, hyphens
    sanitized = re.sub(r"[^a-zA-Z0-9\s'\-]", "", name)
    
    # Clean up whitespace
    sanitized = ' '.join(sanitized.split()).strip()
    
    # Capitalize first letter of each word
    return sanitized.title()

def format_description(description: str, max_length: int = 500) -> str:
    """Format description text - crude_functional.py description formatting."""
    if not description:
        return ""
    
    # Clean and truncate if needed
    cleaned = clean_text(description)
    
    if len(cleaned) <= max_length:
        return cleaned
    
    # Truncate at word boundary
    truncated = cleaned[:max_length]
    last_space = truncated.rfind(' ')
    
    if last_space > max_length * 0.8:  # If space is reasonably close to end
        return truncated[:last_space] + "..."
    else:
        return truncated + "..."

# ============ D&D SPECIFIC TEXT UTILITIES ============

def parse_dice_notation(dice_text: str) -> Dict[str, Any]:
    """Parse dice notation - crude_functional.py dice parsing."""
    if not dice_text:
        return {"valid": False, "count": 0, "sides": 0, "modifier": 0}
    
    # Simple dice notation parsing: "2d6+3", "1d8", "d20"
    dice_text = dice_text.strip().lower().replace(" ", "")
    
    # Match pattern like "2d6+3" or "d20" or "1d8-1"
    match = re.match(r'(\d*)d(\d+)([+-]\d+)?', dice_text)
    
    if match:
        count = int(match.group(1)) if match.group(1) else 1
        sides = int(match.group(2))
        modifier = int(match.group(3)) if match.group(3) else 0
        
        return {
            "valid": True,
            "count": count,
            "sides": sides,
            "modifier": modifier,
            "notation": dice_text
        }
    
    # Try to parse as just a number (modifier only)
    try:
        modifier = int(dice_text)
        return {
            "valid": True,
            "count": 0,
            "sides": 0,
            "modifier": modifier,
            "notation": dice_text
        }
    except ValueError:
        return {"valid": False, "count": 0, "sides": 0, "modifier": 0}

def format_ability_score(score: int) -> str:
    """Format ability score with modifier - crude_functional.py score formatting."""
    if not isinstance(score, int):
        return "10 (+0)"
    
    # Clamp score to reasonable range
    score = max(1, min(30, score))
    
    # Calculate modifier
    modifier = (score - 10) // 2
    
    # Format with sign
    if modifier >= 0:
        return f"{score} (+{modifier})"
    else:
        return f"{score} ({modifier})"

def format_modifier(modifier: int) -> str:
    """Format modifier with proper sign - crude_functional.py modifier formatting."""
    if not isinstance(modifier, int):
        return "+0"
    
    if modifier >= 0:
        return f"+{modifier}"
    else:
        return str(modifier)

def parse_spell_components(components_text: str) -> List[str]:
    """Parse spell components - crude_functional.py component parsing."""
    if not components_text:
        return []
    
    # Parse "V, S, M" or "Verbal, Somatic, Material"
    components = []
    text_upper = components_text.upper()
    
    if 'V' in text_upper or 'VERBAL' in text_upper:
        components.append("V")
    if 'S' in text_upper or 'SOMATIC' in text_upper:
        components.append("S")  
    if 'M' in text_upper or 'MATERIAL' in text_upper:
        components.append("M")
    
    return components

def format_spell_components(components: List[str]) -> str:
    """Format spell components for display - crude_functional.py component formatting."""
    if not components:
        return "None"
    
    # Ensure proper ordering: V, S, M
    ordered_components = []
    if "V" in components:
        ordered_components.append("V")
    if "S" in components:
        ordered_components.append("S")
    if "M" in components:
        ordered_components.append("M")
    
    return ", ".join(ordered_components)

# ============ LIST AND ARRAY PROCESSING ============

def clean_text_list(text_list: List[str]) -> List[str]:
    """Clean list of text items - crude_functional.py list cleaning."""
    if not text_list:
        return []
    
    cleaned = []
    for text in text_list:
        if text and isinstance(text, str):
            clean = clean_text(text)
            if clean:  # Only add non-empty cleaned text
                cleaned.append(clean)
    
    return cleaned

def join_with_and(items: List[str]) -> str:
    """Join list with 'and' - crude_functional.py natural language joining."""
    if not items:
        return ""
    
    if len(items) == 1:
        return items[0]
    elif len(items) == 2:
        return f"{items[0]} and {items[1]}"
    else:
        return ", ".join(items[:-1]) + f", and {items[-1]}"

def split_camel_case(text: str) -> str:
    """Split camelCase text - crude_functional.py camel case splitting."""
    if not text:
        return ""
    
    # Insert space before uppercase letters (except first)
    spaced = re.sub(r'(?<!^)([A-Z])', r' \1', text)
    return spaced.title()

def snake_to_title(text: str) -> str:
    """Convert snake_case to Title Case - crude_functional.py case conversion."""
    if not text:
        return ""
    
    # Replace underscores with spaces and title case
    return text.replace('_', ' ').title()

# ============ VALIDATION AND CHECKING ============

def is_valid_identifier(text: str) -> bool:
    """Check if text is valid identifier - crude_functional.py identifier validation."""
    if not text:
        return False
    
    # Must start with letter or underscore, then letters/numbers/underscores
    return bool(re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', text))

def contains_profanity(text: str) -> bool:
    """Check for basic profanity - crude_functional.py simple profanity check."""
    if not text:
        return False
    
    # Very basic profanity list - extend as needed
    basic_profanity = [
        "damn", "hell", "crap"  # Very mild examples
    ]
    
    text_lower = text.lower()
    return any(word in text_lower for word in basic_profanity)

def validate_character_name(name: str) -> Tuple[bool, str]:
    """Validate character name - crude_functional.py name validation."""
    if not name:
        return True, ""  # Empty names are allowed
    
    # Basic validation
    if len(name.strip()) < 1:
        return False, "Name cannot be empty"
    
    if len(name) > 50:
        return False, "Name too long (max 50 characters)"
    
    # Check for reasonable characters
    if not re.match(r"^[a-zA-Z\s'\-\.]+$", name):
        return False, "Name contains invalid characters"
    
    # Very lenient profanity check
    if contains_profanity(name):
        return False, "Name contains inappropriate content"
    
    return True, ""

# ============ SEARCH AND MATCHING ============

def fuzzy_match(query: str, target: str, threshold: float = 0.6) -> bool:
    """Simple fuzzy matching - crude_functional.py fuzzy matching."""
    if not query or not target:
        return False
    
    query_clean = clean_text(query)
    target_clean = clean_text(target)
    
    # Simple substring matching
    if query_clean in target_clean:
        return True
    
    # Simple character overlap ratio
    query_chars = set(query_clean)
    target_chars = set(target_clean)
    
    if not query_chars:
        return False
    
    overlap = len(query_chars.intersection(target_chars))
    ratio = overlap / len(query_chars)
    
    return ratio >= threshold

def extract_keywords(text: str, min_length: int = 3) -> List[str]:
    """Extract keywords from text - crude_functional.py keyword extraction."""
    if not text:
        return []
    
    # Simple keyword extraction
    words = clean_text(text).split()
    
    # Filter by length and remove common words
    common_words = {"the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
    
    keywords = []
    for word in words:
        if len(word) >= min_length and word not in common_words:
            keywords.append(word)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_keywords = []
    for keyword in keywords:
        if keyword not in seen:
            seen.add(keyword)
            unique_keywords.append(keyword)
    
    return unique_keywords

# ============ FORMATTING UTILITIES ============

def wrap_text(text: str, width: int = 80) -> List[str]:
    """Wrap text to specified width - crude_functional.py text wrapping."""
    if not text:
        return []
    
    words = text.split()
    if not words:
        return []
    
    lines = []
    current_line = []
    current_length = 0
    
    for word in words:
        # If adding this word would exceed width, start new line
        if current_length + len(word) + len(current_line) > width and current_line:
            lines.append(' '.join(current_line))
            current_line = [word]
            current_length = len(word)
        else:
            current_line.append(word)
            current_length += len(word)
    
    # Add final line
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines

def truncate_with_ellipsis(text: str, max_length: int = 100) -> str:
    """Truncate text with ellipsis - crude_functional.py text truncation."""
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."

def pad_text(text: str, width: int, align: str = "left") -> str:
    """Pad text to specified width - crude_functional.py text padding."""
    if not text:
        text = ""
    
    if len(text) >= width:
        return text
    
    if align == "center":
        return text.center(width)
    elif align == "right":
        return text.rjust(width)
    else:  # left or default
        return text.ljust(width)

# ============ ESSENTIAL EXPORTS ============

__all__ = [
    # Core text processing
    'clean_text',
    'normalize_dnd_text',
    'sanitize_name',
    'format_description',
    
    # D&D specific utilities
    'parse_dice_notation',
    'format_ability_score',
    'format_modifier',
    'parse_spell_components',
    'format_spell_components',
    
    # List processing
    'clean_text_list',
    'join_with_and',
    'split_camel_case',
    'snake_to_title',
    
    # Validation
    'is_valid_identifier',
    'contains_profanity',
    'validate_character_name',
    
    # Search and matching
    'fuzzy_match',
    'extract_keywords',
    
    # Formatting utilities
    'wrap_text',
    'truncate_with_ellipsis',
    'pad_text',
]

# ============ MODULE METADATA ============

__version__ = '1.0.0'
__description__ = 'Essential D&D text processing utilities'
__author__ = 'D&D Character Creator Backend7'

# Backend7 architecture compliance
BACKEND7_COMPLIANCE = {
    "layer": "core/utils",
    "focus": "text_processing_utilities",
    "line_target": 200,
    "dependencies": [],
    "philosophy": "crude_functional_inspired_essential_text_processing",
    "maintains_crude_functional_approach": True
}