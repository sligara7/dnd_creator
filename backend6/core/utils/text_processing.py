"""
Enhanced Text Processing Utilities for D&D Character Creation.

MINIMAL VERSION: Focused on creative character generation with optional cultural enhancement.
Culture features are supportive only - they enhance but never restrict creative freedom.

Core Philosophy:
- Character creation comes first
- Culture enhances but never restricts
- Simple, clean functions for creative freedom
- Gaming table optimization
"""

import re
import unicodedata
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from collections import Counter

# ============================================================================
# MINIMAL IMPORTS - Only what we need
# ============================================================================

from ..enums.text_types import (
    EnhancedTextStyle,
    EnhancedContentType,
    TextAnalysisCategory
)

from ..exceptions.culture import CultureError

# Optional culture utilities - fallback gracefully if not available
try:
    from ..enums.culture_types import CultureAuthenticityLevel
    CULTURE_SUPPORT_AVAILABLE = True
except ImportError:
    class CultureAuthenticityLevel:
        GAMING = "gaming"
    CULTURE_SUPPORT_AVAILABLE = False

# ============================================================================
# MINIMAL DATACLASSES - Character focused
# ============================================================================

@dataclass(frozen=True)
class CharacterName:
    """Simple character name components for creative generation."""
    first_name: str
    last_name: Optional[str] = None
    nickname: Optional[str] = None
    title: Optional[str] = None
    full_name: Optional[str] = None
    pronunciation_hint: Optional[str] = None  # Optional gaming table help
    
    def __post_init__(self):
        """Build full name if not provided."""
        if not self.full_name and self.first_name:
            parts = []
            if self.title:
                parts.append(self.title)
            parts.append(self.first_name)
            if self.last_name:
                parts.append(self.last_name)
            object.__setattr__(self, 'full_name', ' '.join(parts))


@dataclass(frozen=True)
class TextAnalysis:
    """Simple text analysis for character content."""
    word_count: int
    readability_score: float  # 0-100, higher = easier to read
    gaming_friendly: bool     # Good for table use?
    character_elements: List[str] = field(default_factory=list)  # Found character elements
    suggestions: List[str] = field(default_factory=list)        # Optional improvements


# ============================================================================
# CORE TEXT FORMATTING - Simple and Gaming Friendly
# ============================================================================

def format_text_for_character(text: str, style: EnhancedTextStyle = EnhancedTextStyle.GAMING_FRIENDLY) -> str:
    """
    Format text for character creation with gaming table optimization.
    
    Args:
        text: Text to format
        style: How to format (defaults to gaming-friendly)
        
    Returns:
        Formatted text optimized for character sheets and gaming tables
    """
    if not text:
        return text
    
    text = text.strip()
    if not text:
        return text
    
    # Apply simple, effective formatting
    if style == EnhancedTextStyle.GAMING_FRIENDLY:
        return _make_gaming_friendly(text)
    elif style == EnhancedTextStyle.TITLE_CASE:
        return _smart_title_case(text)
    elif style == EnhancedTextStyle.UPPER_CASE:
        return text.upper()
    elif style == EnhancedTextStyle.LOWER_CASE:
        return text.lower()
    else:
        # Default to gaming-friendly for any unknown styles
        return _make_gaming_friendly(text)


def _make_gaming_friendly(text: str) -> str:
    """Make text friendly for gaming tables - easy to read and pronounce."""
    # Clean up separators
    text = text.replace('_', ' ').replace('-', ' ')
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Simple title case
    words = text.split()
    if not words:
        return text
    
    # Keep small words lowercase (except first word)
    small_words = {'a', 'an', 'and', 'as', 'at', 'but', 'by', 'for', 'if', 'in', 
                  'nor', 'of', 'on', 'or', 'so', 'the', 'to', 'up', 'yet', 'with'}
    
    result = []
    for i, word in enumerate(words):
        clean_word = re.sub(r'[^a-zA-Z0-9\']', '', word)
        if i == 0 or clean_word.lower() not in small_words:
            result.append(word.capitalize())
        else:
            result.append(word.lower())
    
    formatted = ' '.join(result)
    
    # Optional: Simplify very difficult pronunciations
    formatted = _simplify_pronunciation(formatted)
    
    return formatted


def _smart_title_case(text: str) -> str:
    """Smart title case that handles names well."""
    text = text.replace('_', ' ').replace('-', ' ')
    words = text.split()
    
    small_words = {'a', 'an', 'and', 'as', 'at', 'but', 'by', 'for', 'if', 'in', 
                  'nor', 'of', 'on', 'or', 'so', 'the', 'to', 'up', 'yet', 'with'}
    
    result = []
    for i, word in enumerate(words):
        if i == 0 or word.lower() not in small_words:
            result.append(word.capitalize())
        else:
            result.append(word.lower())
    
    return ' '.join(result)


def _simplify_pronunciation(text: str) -> str:
    """Optional pronunciation simplification for gaming tables."""
    # Only apply if it significantly helps without changing meaning
    
    # Simple replacements that help pronunciation
    replacements = {
        r'sch\b': 'sh',    # "sch" at end of word -> "sh"
        r'tch\b': 'ch',    # "tch" at end of word -> "ch"  
        r"'{2,}": "'",     # Multiple apostrophes -> single
        r'-{2,}': '-',     # Multiple hyphens -> single
    }
    
    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    return text


# ============================================================================
# CHARACTER NAME UTILITIES - Creative Freedom Focus
# ============================================================================

def create_character_name(first_name: str, last_name: Optional[str] = None,
                         culture_hint: Optional[str] = None) -> CharacterName:
    """
    Create a character name with optional cultural flavor.
    
    Args:
        first_name: Character's first name
        last_name: Optional last name
        culture_hint: Optional cultural inspiration (enhances, doesn't restrict)
        
    Returns:
        CharacterName object with gaming-friendly formatting
    """
    # Format names for gaming use
    formatted_first = format_text_for_character(first_name)
    formatted_last = format_text_for_character(last_name) if last_name else None
    
    # Optional cultural enhancement (supportive only)
    title = None
    pronunciation_hint = None
    
    if culture_hint and CULTURE_SUPPORT_AVAILABLE:
        title, pronunciation_hint = _get_cultural_enhancements(
            formatted_first, formatted_last, culture_hint
        )
    
    return CharacterName(
        first_name=formatted_first,
        last_name=formatted_last,
        title=title,
        pronunciation_hint=pronunciation_hint
    )


def _get_cultural_enhancements(first_name: str, last_name: Optional[str], 
                              culture_hint: str) -> Tuple[Optional[str], Optional[str]]:
    """Get optional cultural enhancements - never required, always helpful."""
    title = None
    pronunciation = None
    
    culture_lower = culture_hint.lower()
    
    # Optional titles that might fit (suggestions only)
    if 'norse' in culture_lower or 'viking' in culture_lower:
        # Optional Norse-style enhancements
        if first_name.endswith('son'):
            pronunciation = f"{first_name} (SON ending)"
        
    elif 'celtic' in culture_lower or 'irish' in culture_lower:
        # Optional Celtic-style enhancements  
        if first_name.startswith('Mac') or first_name.startswith("O'"):
            pronunciation = f"{first_name} (Celtic name)"
    
    # These are just helpful hints, never requirements
    return title, pronunciation


# ============================================================================
# TEXT VALIDATION - Supportive, Not Restrictive
# ============================================================================

def validate_character_text(text: str, content_type: EnhancedContentType,
                           max_length: Optional[int] = None) -> Tuple[bool, List[str]]:
    """
    Simple validation that supports creativity rather than restricting it.
    
    Args:
        text: Text to validate  
        content_type: What type of content this is
        max_length: Optional length limit
        
    Returns:
        (is_valid, suggestions) - suggestions are helpful, not required
    """
    if not text or not text.strip():
        return False, ["Content cannot be empty"]
    
    suggestions = []
    
    # Reasonable length limits (generous for creativity)
    length_limits = {
        EnhancedContentType.CHARACTER_NAME: 100,
        EnhancedContentType.CHARACTER_NICKNAME: 50, 
        EnhancedContentType.PERSONALITY_TRAIT: 500,
        EnhancedContentType.BACKGROUND_STORY: 3000,
        EnhancedContentType.PHYSICAL_DESCRIPTION: 1000
    }
    
    limit = max_length or length_limits.get(content_type, 1000)
    
    if len(text) > limit:
        return False, [f"Content too long (max {limit} characters)"]
    
    # Gaming-friendly suggestions (optional)
    if content_type == EnhancedContentType.CHARACTER_NAME:
        if len(text) > 30:
            suggestions.append("Shorter names are easier at gaming tables")
        if re.search(r'[^a-zA-Z\s\'-\.\u00C0-\u017F]', text):
            suggestions.append("Consider simpler characters for easier use")
    
    elif content_type == EnhancedContentType.BACKGROUND_STORY:
        if len(text.split()) > 300:
            suggestions.append("Consider a shorter summary for table reference")
    
    # Always return True for creativity - suggestions are just helpful
    return True, suggestions


# ============================================================================
# TEXT ANALYSIS - Simple and Helpful
# ============================================================================

def analyze_character_text(text: str) -> TextAnalysis:
    """
    Simple analysis focused on character creation utility.
    
    Args:
        text: Text to analyze
        
    Returns:
        TextAnalysis with helpful insights for character creation
    """
    if not text:
        return TextAnalysis(
            word_count=0,
            readability_score=0.0,
            gaming_friendly=True,
            character_elements=[],
            suggestions=[]
        )
    
    word_count = len(text.split())
    readability_score = _calculate_simple_readability(text)
    gaming_friendly = _is_gaming_friendly(text)
    character_elements = _find_character_elements(text)
    suggestions = _generate_helpful_suggestions(text, character_elements)
    
    return TextAnalysis(
        word_count=word_count,
        readability_score=readability_score,
        gaming_friendly=gaming_friendly,
        character_elements=character_elements,
        suggestions=suggestions
    )


def _calculate_simple_readability(text: str) -> float:
    """Simple readability score - higher = easier to read at tables."""
    words = text.split()
    if not words:
        return 100.0
    
    # Simple metrics
    avg_word_length = sum(len(word) for word in words) / len(words)
    sentences = len(re.findall(r'[.!?]+', text))
    avg_sentence_length = len(words) / max(sentences, 1)
    
    # Simple formula - penalize long words and sentences
    score = 100 - (avg_word_length * 5) - (avg_sentence_length * 0.5)
    return max(0.0, min(100.0, score))


def _is_gaming_friendly(text: str) -> bool:
    """Check if text is friendly for gaming table use."""
    # Simple checks
    if len(text) > 1000:  # Very long
        return False
    
    words = text.split()
    if not words:
        return True
    
    # Check for overly complex words
    complex_words = sum(1 for word in words if len(word) > 12)
    if complex_words > len(words) * 0.1:  # More than 10% complex
        return False
    
    return True


def _find_character_elements(text: str) -> List[str]:
    """Find elements useful for character creation."""
    elements = []
    text_lower = text.lower()
    
    # Character creation elements
    character_terms = {
        'personality': ['brave', 'kind', 'cunning', 'wise', 'strong', 'gentle', 'bold', 'shy'],
        'background': ['family', 'childhood', 'past', 'history', 'experience', 'training'],
        'motivation': ['goal', 'desire', 'quest', 'mission', 'purpose', 'dream'],
        'relationships': ['friend', 'enemy', 'ally', 'mentor', 'rival', 'companion'],
        'conflict': ['conflict', 'struggle', 'challenge', 'problem', 'obstacle']
    }
    
    for category, terms in character_terms.items():
        if any(term in text_lower for term in terms):
            elements.append(category)
    
    return elements


def _generate_helpful_suggestions(text: str, character_elements: List[str]) -> List[str]:
    """Generate helpful suggestions to enhance character creation."""
    suggestions = []
    
    # Positive, supportive suggestions
    if not character_elements:
        suggestions.append("Consider adding personality traits or background elements")
    
    if 'personality' not in character_elements:
        suggestions.append("Adding personality traits can make the character more memorable")
    
    if 'motivation' not in character_elements:
        suggestions.append("Character goals or motivations can drive interesting roleplay")
    
    if len(text.split()) > 200:
        suggestions.append("A shorter summary might be helpful for quick table reference")
    
    return suggestions


# ============================================================================
# UTILITY FUNCTIONS - Simple and Clean
# ============================================================================

def clean_text_for_character_sheet(text: str) -> str:
    """Clean text for character sheet use - preserves creativity."""
    if not text:
        return ""
    
    # Basic cleaning that preserves creative content
    text = text.strip()
    
    # Remove only truly problematic characters
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def get_pronunciation_hint(name: str) -> Optional[str]:
    """Get optional pronunciation hint for difficult names."""
    if not name or len(name) <= 4:
        return None
    
    # Only provide hints for potentially difficult names
    difficult_patterns = ['sch', 'tch', 'pht', 'xhr', 'gn', 'ps']
    
    if any(pattern in name.lower() for pattern in difficult_patterns):
        # Simple phonetic breakdown
        simplified = name.lower()
        for pattern in ['sch', 'tch', 'pht']:
            if pattern in simplified:
                return f"Pronunciation tip: '{pattern}' sounds like '{pattern[:-1]}'"
    
    return None


def extract_character_names(text: str) -> List[str]:
    """Extract potential character names from text."""
    # Find capitalized words that might be names
    potential_names = re.findall(r'\b[A-Z][a-z]{2,}\b', text)
    
    # Filter out common words that aren't names
    common_words = {
        'The', 'This', 'That', 'They', 'There', 'Then', 'When', 'Where',
        'What', 'Who', 'Why', 'How', 'And', 'But', 'Or', 'So', 'If',
        'Character', 'Person', 'People', 'Name', 'Story', 'Tale'
    }
    
    names = [name for name in potential_names if name not in common_words]
    
    # Remove duplicates while preserving order
    seen = set()
    unique_names = []
    for name in names:
        if name not in seen:
            seen.add(name)
            unique_names.append(name)
    
    return unique_names


# ============================================================================
# CULTURAL SUPPORT - Optional and Enhancing Only
# ============================================================================

def add_cultural_flavor(text: str, culture_hint: Optional[str] = None) -> str:
    """
    Optionally add cultural flavor to enhance creativity.
    
    This function ONLY adds helpful elements - it never restricts or changes
    the original creative content.
    
    Args:
        text: Original creative text
        culture_hint: Optional cultural inspiration
        
    Returns: 
        Enhanced text (original + optional cultural elements)
    """
    if not culture_hint or not CULTURE_SUPPORT_AVAILABLE:
        return text  # Return unchanged if no culture support
    
    # Culture only adds flavor, never changes original content
    enhanced_text = text
    
    culture_lower = culture_hint.lower()
    
    # Optional enhancements (additive only)
    if 'norse' in culture_lower and 'honor' not in text.lower():
        enhanced_text += "\n\n[Cultural note: Norse-inspired elements could include themes of honor, courage, and family legacy]"
    
    elif 'celtic' in culture_lower and 'nature' not in text.lower():
        enhanced_text += "\n\n[Cultural note: Celtic-inspired elements could include connections to nature, music, and ancient wisdom]"
    
    # These are just optional suggestions appended to original content
    return enhanced_text


# ============================================================================
# EXPORTS - Keep it Simple
# ============================================================================

__all__ = [
    # Core types
    "CharacterName",
    "TextAnalysis",
    
    # Main functions  
    "format_text_for_character",
    "create_character_name", 
    "validate_character_text",
    "analyze_character_text",
    
    # Utilities
    "clean_text_for_character_sheet",
    "get_pronunciation_hint",
    "extract_character_names",
    "add_cultural_flavor"
]

# ============================================================================
# MODULE INFO
# ============================================================================

__version__ = "1.0.0"
__description__ = "Minimal Text Processing for D&D Character Creation - Culture Enhances, Never Restricts"