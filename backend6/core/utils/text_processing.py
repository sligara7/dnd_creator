
# refactor based on the following structure:
# ├── core/
# │   ├── utils/
# │   │   ├── text_processing.py                    # ✅ EXISTS - Consistent Interface & Validation
# │   │   ├── cultures/
# │   │   │   ├── culture_generator.py              # 🆕 CORE - LLM Culture Generation Logic
# │   │   │   ├── prompt_templates.py               # 🆕 CORE - Prompt Engineering Templates
# │   │   │   └── culture_parser.py                 # 🆕 CORE - Parse LLM Responses
# │   │   └── validation/
# │   │       └── culture_validator.py              # 🆕 CORE - Validate Generated Cultures

"""
Text Processing Utilities for D&D Creative Content Framework.

This module provides pure utility functions for:
- Text formatting and validation for character sheets
- Natural language processing for character descriptions
- Lore text analysis and generation
- String manipulation and sanitization
- Content generation using cultural naming systems
- Multi-language support for international D&D content

Following Clean Architecture principles, these utilities are:
- Infrastructure-independent (no external NLP dependencies)
- Pure functions with no side effects
- Focused on text processing and linguistic operations
- Used by domain services and application use cases
- Support character creation and content generation workflows

This module is culture-agnostic - specific cultural naming systems are handled
by the cultures module at /backend6/core/utils/cultures/
"""

import re
import random
import string
import unicodedata
from typing import Dict, List, Optional, Tuple, Union, Set, Any, Callable
from dataclasses import dataclass
from enum import Enum
import json
from collections import Counter, defaultdict
import math

# Import culture system
from .cultures import get_culture, list_cultures, CultureType


# ============================================================================
# TYPE DEFINITIONS AND ENUMS
# ============================================================================

class TextStyle(Enum):
    """Text formatting styles."""
    PLAIN = "plain"
    TITLE_CASE = "title"
    UPPER_CASE = "upper"
    LOWER_CASE = "lower"
    SENTENCE_CASE = "sentence"
    CAMEL_CASE = "camel"
    SNAKE_CASE = "snake"
    KEBAB_CASE = "kebab"


class ContentType(Enum):
    """Types of D&D content for processing."""
    CHARACTER_NAME = "character_name"
    PLACE_NAME = "place_name"
    ITEM_NAME = "item_name"
    SPELL_NAME = "spell_name"
    ABILITY_NAME = "ability_name"
    PERSONALITY_TRAIT = "personality_trait"
    IDEAL = "ideal"
    BOND = "bond"
    FLAW = "flaw"
    BACKGROUND_STORY = "background_story"
    PHYSICAL_DESCRIPTION = "physical_description"
    EQUIPMENT_DESCRIPTION = "equipment_description"
    SPELL_DESCRIPTION = "spell_description"


@dataclass(frozen=True)
class NameComponents:
    """Components of a generated name."""
    first_name: str
    last_name: Optional[str] = None
    title: Optional[str] = None
    epithet: Optional[str] = None
    clan_name: Optional[str] = None
    patronymic: Optional[str] = None
    matronymic: Optional[str] = None
    full_name: Optional[str] = None
    pronunciation: Optional[str] = None
    meaning: Optional[str] = None
    cultural_notes: Optional[str] = None
    historical_context: Optional[str] = None


@dataclass(frozen=True)
class TextAnalysis:
    """Analysis results for text content."""
    word_count: int
    character_count: int
    sentence_count: int
    paragraph_count: int
    reading_level: float
    complexity_score: float
    fantasy_terms: List[str]
    sentiment_score: float
    keywords: List[Tuple[str, int]]
    language_detected: Optional[str]
    cultural_references: List[str]


@dataclass(frozen=True)
class ValidationResult:
    """Text validation result."""
    is_valid: bool
    errors: List[str]
    warnings: List[str] = None

    def __post_init__(self):
        if self.warnings is None:
            object.__setattr__(self, 'warnings', [])


# ============================================================================
# CORE TEXT FORMATTING FUNCTIONS
# ============================================================================

def format_text(text: str, style: TextStyle) -> str:
    """
    Format text according to specified style.
    
    Args:
        text: Text to format
        style: Formatting style to apply
        
    Returns:
        Formatted text string
        
    Examples:
        >>> format_text("hello world", TextStyle.TITLE_CASE)
        "Hello World"
        >>> format_text("CamelCase", TextStyle.SNAKE_CASE)
        "camel_case"
    """
    if not text:
        return text
    
    if style == TextStyle.PLAIN:
        return text
    elif style == TextStyle.TITLE_CASE:
        return text.title()
    elif style == TextStyle.UPPER_CASE:
        return text.upper()
    elif style == TextStyle.LOWER_CASE:
        return text.lower()
    elif style == TextStyle.SENTENCE_CASE:
        return text.capitalize()
    elif style == TextStyle.CAMEL_CASE:
        words = re.split(r'[\s_-]+', text.lower())
        return words[0] + ''.join(word.capitalize() for word in words[1:])
    elif style == TextStyle.SNAKE_CASE:
        # Convert CamelCase and spaces to snake_case
        text = re.sub(r'([A-Z])', r'_\1', text)
        text = re.sub(r'[\s-]+', '_', text)
        return text.lower().strip('_')
    elif style == TextStyle.KEBAB_CASE:
        # Convert to kebab-case
        text = re.sub(r'([A-Z])', r'-\1', text)
        text = re.sub(r'[\s_]+', '-', text)
        return text.lower().strip('-')
    
    return text


def sanitize_text_input(text: str, max_length: int = 1000, allow_unicode: bool = True) -> str:
    """
    Sanitize user text input for safety and consistency.
    
    Args:
        text: Text to sanitize
        max_length: Maximum allowed length
        allow_unicode: Whether to allow Unicode characters
        
    Returns:
        Sanitized text string
    """
    if not text:
        return ""
    
    # Truncate to max length
    text = text[:max_length]
    
    # Remove or replace dangerous characters
    # Remove control characters except newlines and tabs
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
    
    # Handle Unicode
    if not allow_unicode:
        # Convert to ASCII, replacing non-ASCII characters
        text = unicodedata.normalize('NFKD', text)
        text = text.encode('ascii', 'ignore').decode('ascii')
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove potentially harmful patterns (basic XSS prevention)
    dangerous_patterns = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
        r'<iframe[^>]*>.*?</iframe>'
    ]
    
    for pattern in dangerous_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)
    
    return text


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace in text.
    
    Args:
        text: Text to normalize
        
    Returns:
        Text with normalized whitespace
    """
    if not text:
        return text
    
    # Replace multiple spaces with single space
    text = re.sub(r' +', ' ', text)
    
    # Replace multiple newlines with double newline (paragraph break)
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    
    # Remove trailing whitespace from lines
    text = '\n'.join(line.rstrip() for line in text.split('\n'))
    
    return text.strip()


def truncate_text(text: str, max_length: int, preserve_words: bool = True, 
                 ellipsis: str = "...") -> str:
    """
    Truncate text to specified length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        preserve_words: Whether to preserve word boundaries
        ellipsis: String to append if truncated
        
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    if not preserve_words:
        return text[:max_length - len(ellipsis)] + ellipsis
    
    # Find last space before max_length
    truncate_pos = max_length - len(ellipsis)
    if truncate_pos <= 0:
        return ellipsis
    
    # Look for word boundary
    while truncate_pos > 0 and not text[truncate_pos].isspace():
        truncate_pos -= 1
    
    if truncate_pos == 0:
        # No word boundary found, truncate at character level
        return text[:max_length - len(ellipsis)] + ellipsis
    
    return text[:truncate_pos].rstrip() + ellipsis


# ============================================================================
# TEXT VALIDATION FUNCTIONS
# ============================================================================

def validate_character_sheet_text(text: str, content_type: ContentType) -> ValidationResult:
    """
    Validate text content for character sheets based on content type.
    
    Args:
        text: Text to validate
        content_type: Type of content being validated
        
    Returns:
        ValidationResult with validation status and messages
    """
    errors = []
    warnings = []
    
    if not text:
        errors.append("Text cannot be empty")
        return ValidationResult(False, errors, warnings)
    
    # Content-specific validation
    if content_type == ContentType.CHARACTER_NAME:
        if len(text) > 50:
            errors.append("Character name too long (max 50 characters)")
        if not re.match(r'^[a-zA-Z\s\'-\.]+$', text):
            errors.append("Character name contains invalid characters")
        if len(text.strip()) < 2:
            errors.append("Character name too short")
        
    elif content_type == ContentType.PERSONALITY_TRAIT:
        if len(text) > 200:
            errors.append("Personality trait too long (max 200 characters)")
        if len(text.split()) < 3:
            warnings.append("Personality trait should be at least 3 words")
        if not text.strip().endswith('.'):
            warnings.append("Personality trait should end with a period")
            
    elif content_type == ContentType.BACKGROUND_STORY:
        if len(text) > 2000:
            errors.append("Background story too long (max 2000 characters)")
        word_count = len(text.split())
        if word_count < 10:
            warnings.append("Background story should be at least 10 words")
        if word_count > 500:
            warnings.append("Background story is quite long - consider condensing")
            
    elif content_type == ContentType.PHYSICAL_DESCRIPTION:
        if len(text) > 500:
            errors.append("Physical description too long (max 500 characters)")
        if len(text.split()) < 5:
            warnings.append("Physical description should be more detailed")
            
    elif content_type in [ContentType.IDEAL, ContentType.BOND, ContentType.FLAW]:
        if len(text) > 150:
            errors.append(f"{content_type.value.title()} too long (max 150 characters)")
        if not text.strip().endswith('.'):
            warnings.append(f"{content_type.value.title()} should end with a period")
    
    # General text quality checks
    if text.count('\n') > 10:
        warnings.append("Text has many line breaks - consider reformatting")
    
    # Check for reasonable character variety (not just repeated characters)
    unique_chars = len(set(text.lower().replace(' ', '')))
    if unique_chars < 3 and len(text) > 10:
        errors.append("Text lacks character variety")
    
    # Check for excessive punctuation
    punct_count = sum(1 for char in text if char in '!?')
    if punct_count > len(text) // 20:  # More than 5% punctuation
        warnings.append("Text contains excessive punctuation")
    
    return ValidationResult(len(errors) == 0, errors, warnings)


def validate_name_components(components: NameComponents) -> ValidationResult:
    """
    Validate name components for correctness.
    
    Args:
        components: Name components to validate
        
    Returns:
        ValidationResult with validation status and messages
    """
    errors = []
    warnings = []
    
    # Check first name
    if not components.first_name:
        errors.append("First name is required")
    elif len(components.first_name) > 50:
        errors.append("First name is too long (max 50 characters)")
    elif not re.match(r'^[a-zA-Z\s\'-\.]+$', components.first_name):
        errors.append("First name contains invalid characters")
    
    # Check last name if present
    if components.last_name:
        if len(components.last_name) > 50:
            errors.append("Last name is too long (max 50 characters)")
        elif not re.match(r'^[a-zA-Z\s\'-\.]+$', components.last_name):
            errors.append("Last name contains invalid characters")
    
    # Check full name construction
    if components.full_name:
        expected_parts = []
        if components.title:
            expected_parts.append(components.title)
        if components.first_name:
            expected_parts.append(components.first_name)
        if components.last_name:
            expected_parts.append(components.last_name)
        if components.epithet:
            expected_parts.append(components.epithet)
        
        expected_full = ' '.join(expected_parts)
        if components.full_name != expected_full:
            warnings.append("Full name doesn't match component parts")
    
    # Check pronunciation guide format
    if components.pronunciation and not re.match(r'^\[.*\]$', components.pronunciation):
        warnings.append("Pronunciation guide should be enclosed in brackets")
    
    return ValidationResult(len(errors) == 0, errors, warnings)


# ============================================================================
# TEXT ANALYSIS FUNCTIONS
# ============================================================================

def analyze_text_content(text: str) -> TextAnalysis:
    """
    Analyze text content for various metrics.
    
    Args:
        text: Text to analyze
        
    Returns:
        TextAnalysis with comprehensive metrics
    """
    if not text:
        return TextAnalysis(
            word_count=0, character_count=0, sentence_count=0, paragraph_count=0,
            reading_level=0.0, complexity_score=0.0, fantasy_terms=[],
            sentiment_score=0.0, keywords=[], language_detected=None, cultural_references=[]
        )
    
    # Basic counts
    word_count = len(text.split())
    character_count = len(text)
    sentence_count = len(re.findall(r'[.!?]+', text))
    paragraph_count = len([p for p in text.split('\n\n') if p.strip()])
    
    # Reading level (simplified Flesch Reading Ease)
    reading_level = calculate_reading_level(text)
    
    # Complexity score
    complexity_score = calculate_text_complexity(text)
    
    # Extract fantasy terms
    fantasy_terms = extract_fantasy_terms(text)
    
    # Sentiment analysis (basic)
    sentiment_score = detect_sentiment(text)
    
    # Keywords extraction
    keywords = extract_keywords(text)
    
    # Language detection (basic)
    language_detected = detect_language(text)
    
    # Cultural references
    cultural_references = extract_cultural_references(text)
    
    return TextAnalysis(
        word_count=word_count,
        character_count=character_count,
        sentence_count=sentence_count,
        paragraph_count=paragraph_count,
        reading_level=reading_level,
        complexity_score=complexity_score,
        fantasy_terms=fantasy_terms,
        sentiment_score=sentiment_score,
        keywords=keywords,
        language_detected=language_detected,
        cultural_references=cultural_references
    )


def calculate_reading_level(text: str) -> float:
    """
    Calculate text reading level using Flesch Reading Ease formula.
    
    Args:
        text: Text to analyze
        
    Returns:
        Reading level score (0-100, higher = easier)
    """
    if not text or not text.strip():
        return 0.0
    
    sentences = re.findall(r'[.!?]+', text)
    words = text.split()
    syllables = sum(count_syllables(word) for word in words)
    
    if len(sentences) == 0 or len(words) == 0:
        return 0.0
    
    avg_sentence_length = len(words) / len(sentences)
    avg_syllables_per_word = syllables / len(words)
    
    # Flesch Reading Ease formula
    reading_ease = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
    
    # Clamp to 0-100 range
    return max(0.0, min(100.0, reading_ease))


def count_syllables(word: str) -> int:
    """
    Count syllables in a word (simplified algorithm).
    
    Args:
        word: Word to count syllables for
        
    Returns:
        Number of syllables
    """
    word = word.lower().strip('.,!?";')
    if not word:
        return 0
    
    vowels = 'aeiouy'
    syllable_count = 0
    prev_was_vowel = False
    
    for char in word:
        is_vowel = char in vowels
        if is_vowel and not prev_was_vowel:
            syllable_count += 1
        prev_was_vowel = is_vowel
    
    # Handle silent e
    if word.endswith('e') and syllable_count > 1:
        syllable_count -= 1
    
    return max(1, syllable_count)


def calculate_text_complexity(text: str) -> float:
    """
    Calculate text complexity score.
    
    Args:
        text: Text to analyze
        
    Returns:
        Complexity score (0-20)
    """
    if not text:
        return 0.0
    
    words = text.split()
    if not words:
        return 0.0
    
    # Factors that increase complexity
    complexity = 0.0
    
    # Average word length
    avg_word_length = sum(len(word) for word in words) / len(words)
    complexity += avg_word_length * 0.5
    
    # Unique vocabulary ratio
    unique_ratio = len(set(word.lower() for word in words)) / len(words)
    complexity += unique_ratio * 10
    
    # Punctuation complexity
    punctuation_count = sum(1 for char in text if char in '.,;:!?()[]{}')
    complexity += (punctuation_count / len(words)) * 5
    
    # Capitalization variety
    cap_variety = len(set(char for char in text if char.isupper())) / max(1, len(text))
    complexity += cap_variety * 2
    
    return min(20.0, complexity)


def extract_fantasy_terms(text: str) -> List[str]:
    """
    Extract D&D/fantasy-specific terms from text.
    
    Args:
        text: Text to analyze
        
    Returns:
        List of fantasy terms found
    """
    fantasy_terms_db = {
        # D&D Classes
        'classes': ['barbarian', 'bard', 'cleric', 'druid', 'fighter', 'monk', 'paladin', 
                   'ranger', 'rogue', 'sorcerer', 'warlock', 'wizard', 'artificer'],
        
        # D&D Races
        'races': ['elf', 'dwarf', 'halfling', 'human', 'dragonborn', 'gnome', 'half-elf', 
                 'half-orc', 'tiefling', 'aasimar', 'genasi', 'goliath', 'tabaxi'],
        
        # Fantasy creatures
        'creatures': ['dragon', 'griffin', 'unicorn', 'phoenix', 'basilisk', 'chimera', 
                     'hydra', 'wyvern', 'pegasus', 'manticore', 'sphinx', 'kraken'],
        
        # Magic terms
        'magic': ['spell', 'cantrip', 'enchantment', 'divination', 'necromancy', 'illusion',
                 'transmutation', 'evocation', 'abjuration', 'conjuration', 'mana', 'arcane'],
        
        # Equipment
        'equipment': ['sword', 'axe', 'bow', 'shield', 'armor', 'helm', 'gauntlets', 
                     'potion', 'scroll', 'wand', 'staff', 'orb', 'tome', 'grimoire'],
        
        # Locations
        'locations': ['dungeon', 'castle', 'tavern', 'monastery', 'temple', 'shrine',
                     'forest', 'mountain', 'cave', 'ruins', 'tower', 'keep']
    }
    
    found_terms = []
    text_lower = text.lower()
    
    for category, terms in fantasy_terms_db.items():
        for term in terms:
            if term in text_lower:
                found_terms.append(term)
    
    return list(set(found_terms))  # Remove duplicates


def detect_sentiment(text: str) -> float:
    """
    Basic sentiment analysis for character descriptions.
    
    Args:
        text: Text to analyze
        
    Returns:
        Sentiment score (-1.0 to 1.0, negative to positive)
    """
    if not text:
        return 0.0
    
    # Simple word-based sentiment analysis
    positive_words = {
        'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'brilliant',
        'beautiful', 'lovely', 'nice', 'pleasant', 'happy', 'joy', 'love', 'peace',
        'hope', 'brave', 'heroic', 'noble', 'kind', 'gentle', 'wise', 'strong',
        'confident', 'successful', 'victory', 'triumph', 'glory', 'honor'
    }
    
    negative_words = {
        'bad', 'terrible', 'awful', 'horrible', 'disgusting', 'hate', 'angry',
        'sad', 'depressed', 'fear', 'scared', 'worried', 'anxious', 'evil',
        'dark', 'sinister', 'cruel', 'wicked', 'vile', 'corrupt', 'cursed',
        'doomed', 'failure', 'defeat', 'death', 'destruction', 'pain', 'suffering'
    }
    
    words = re.findall(r'\b\w+\b', text.lower())
    
    if not words:
        return 0.0
    
    positive_count = sum(1 for word in words if word in positive_words)
    negative_count = sum(1 for word in words if word in negative_words)
    
    total_sentiment_words = positive_count + negative_count
    
    if total_sentiment_words == 0:
        return 0.0
    
    # Calculate sentiment score
    sentiment = (positive_count - negative_count) / len(words)
    
    # Clamp to -1.0 to 1.0 range
    return max(-1.0, min(1.0, sentiment))


def extract_keywords(text: str, max_keywords: int = 10) -> List[Tuple[str, int]]:
    """
    Extract keywords with frequency counts.
    
    Args:
        text: Text to extract keywords from
        max_keywords: Maximum number of keywords to return
        
    Returns:
        List of (keyword, frequency) tuples
    """
    if not text:
        return []
    
    # Simple keyword extraction
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())  # Words 3+ characters
    
    # Remove common stop words
    stop_words = {
        'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had',
        'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how',
        'man', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did',
        'its', 'let', 'put', 'say', 'she', 'too', 'use', 'with', 'have', 'this',
        'will', 'your', 'from', 'they', 'know', 'want', 'been', 'good', 'much',
        'some', 'time', 'very', 'when', 'come', 'here', 'just', 'like', 'long',
        'make', 'many', 'over', 'such', 'take', 'than', 'them', 'well', 'were'
    }
    
    filtered_words = [word for word in words if word not in stop_words]
    
    # Count frequencies
    word_counts = Counter(filtered_words)
    
    # Return top keywords
    return word_counts.most_common(max_keywords)


def detect_language(text: str) -> Optional[str]:
    """
    Basic language detection for text.
    
    Args:
        text: Text to analyze
        
    Returns:
        Detected language code or None
    """
    if not text:
        return None
    
    # Very basic language detection based on character patterns
    text_sample = text[:200].lower()  # Use first 200 characters
    
    # Check for non-Latin scripts
    if any('\u4e00' <= char <= '\u9fff' for char in text_sample):
        return 'zh'  # Chinese
    elif any('\u3040' <= char <= '\u309f' or '\u30a0' <= char <= '\u30ff' for char in text_sample):
        return 'ja'  # Japanese
    elif any('\uac00' <= char <= '\ud7af' for char in text_sample):
        return 'ko'  # Korean
    elif any('\u0600' <= char <= '\u06ff' for char in text_sample):
        return 'ar'  # Arabic
    elif any('\u0400' <= char <= '\u04ff' for char in text_sample):
        return 'ru'  # Russian (Cyrillic)
    
    # For Latin scripts, use word patterns (very simplified)
    words = text_sample.split()
    
    # Common word patterns for different languages
    english_indicators = ['the', 'and', 'that', 'have', 'for', 'not', 'you', 'with']
    spanish_indicators = ['que', 'del', 'los', 'las', 'una', 'con', 'por', 'para']
    french_indicators = ['que', 'des', 'les', 'une', 'avec', 'pour', 'dans', 'sur']
    german_indicators = ['der', 'die', 'und', 'den', 'das', 'mit', 'für', 'auf']
    
    english_score = sum(1 for word in words if word in english_indicators)
    spanish_score = sum(1 for word in words if word in spanish_indicators)
    french_score = sum(1 for word in words if word in french_indicators)
    german_score = sum(1 for word in words if word in german_indicators)
    
    scores = {
        'en': english_score,
        'es': spanish_score,
        'fr': french_score,
        'de': german_score
    }
    
    if max(scores.values()) > 0:
        return max(scores, key=scores.get)
    
    return 'en'  # Default to English


def extract_cultural_references(text: str) -> List[str]:
    """
    Extract cultural references from text.
    
    Args:
        text: Text to analyze
        
    Returns:
        List of cultural references found
    """
    cultural_terms = {
        'norse': ['viking', 'norse', 'asgard', 'valhalla', 'odin', 'thor', 'loki', 'rune', 'berserker'],
        'greek': ['greek', 'athens', 'sparta', 'olympus', 'zeus', 'apollo', 'athena', 'troy', 'odyssey'],
        'roman': ['roman', 'rome', 'caesar', 'senate', 'legion', 'gladiator', 'colosseum', 'consul'],
        'egyptian': ['egyptian', 'pharaoh', 'pyramid', 'sphinx', 'nile', 'ra', 'isis', 'hieroglyph'],
        'celtic': ['celtic', 'druid', 'clan', 'gaelic', 'irish', 'scottish', 'welsh', 'bard'],
        'asian': ['chinese', 'japanese', 'samurai', 'ninja', 'martial', 'zen', 'dragon', 'emperor'],
        'arabic': ['arabic', 'desert', 'oasis', 'sultan', 'caliph', 'scimitar', 'djinn', 'bazaar'],
        'medieval': ['medieval', 'knight', 'castle', 'feudal', 'manor', 'crusade', 'chivalry']
    }
    
    found_references = []
    text_lower = text.lower()
    
    for culture, terms in cultural_terms.items():
        for term in terms:
            if term in text_lower:
                found_references.append(culture)
                break  # Only add culture once
    
    return found_references


# ============================================================================
# NAME GENERATION FUNCTIONS (CULTURE-AGNOSTIC)
# ============================================================================

def generate_character_name(culture_name: str, gender: Optional[str] = None, 
                          include_title: bool = False, 
                          include_epithet: bool = False) -> Optional[NameComponents]:
    """
    Generate a character name using the specified culture.
    
    Args:
        culture_name: Name of the culture to use
        gender: "male" or "female" (None for random)
        include_title: Whether to include titles
        include_epithet: Whether to include epithets
        
    Returns:
        NameComponents with generated name parts or None if culture not found
    """
    culture = get_culture(culture_name)
    if not culture:
        return None
    
    try:
        # Generate name using culture's methods
        if gender is None:
            gender = random.choice(["male", "female"])
        
        # Get name components from culture
        if gender == "male":
            first_names = culture.get_male_names()
        else:
            first_names = culture.get_female_names()
        
        first_name = random.choice(first_names) if first_names else "Unknown"
        
        # Get family name
        family_names = culture.get_family_names()
        last_name = random.choice(family_names) if family_names else None
        
        # Get title if requested
        title = None
        if include_title:
            titles = culture.get_titles()
            title = random.choice(titles) if titles else None
        
        # Get epithet if requested
        epithet = None
        if include_epithet:
            epithets = culture.get_epithets()
            epithet = random.choice(epithets) if epithets else None
        
        # Construct full name
        full_name_parts = []
        if title:
            full_name_parts.append(title)
        full_name_parts.append(first_name)
        if last_name:
            full_name_parts.append(last_name)
        if epithet:
            full_name_parts.append(epithet)
        
        full_name = " ".join(full_name_parts)
        
        # Get additional information
        pronunciation = culture.generate_pronunciation(first_name)
        meaning = culture.generate_meaning(first_name)
        
        # Get cultural metadata
        metadata = culture._get_metadata()
        
        return NameComponents(
            first_name=first_name,
            last_name=last_name,
            title=title,
            epithet=epithet,
            full_name=full_name,
            pronunciation=pronunciation,
            meaning=meaning,
            cultural_notes=metadata.cultural_notes,
            historical_context=metadata.historical_context
        )
    
    except Exception as e:
        # Log error but don't crash
        print(f"Error generating name for culture {culture_name}: {e}")
        return None


def batch_generate_names(culture_name: str, count: int, **kwargs) -> List[NameComponents]:
    """
    Generate multiple names at once.
    
    Args:
        culture_name: Name of the culture to use
        count: Number of names to generate
        **kwargs: Additional arguments for generate_character_name
        
    Returns:
        List of generated name components
    """
    names = []
    for _ in range(count):
        name = generate_character_name(culture_name, **kwargs)
        if name:
            names.append(name)
    
    return names


def get_available_cultures() -> List[str]:
    """
    Get list of available culture names.
    
    Returns:
        List of culture names
    """
    return list_cultures()


def get_cultures_by_type(culture_type: str) -> List[str]:
    """
    Get cultures filtered by type.
    
    Args:
        culture_type: Type of cultures to retrieve
        
    Returns:
        List of culture names of the specified type
    """
    try:
        # Convert string to enum if needed
        if isinstance(culture_type, str):
            culture_type = CultureType(culture_type.lower())
        
        from .cultures import get_cultures_by_type as get_by_type
        return get_by_type(culture_type)
    except (ValueError, ImportError):
        return []


# ============================================================================
# CONTENT GENERATION FUNCTIONS
# ============================================================================

def generate_personality_trait(background: Optional[str] = None, 
                             culture_name: Optional[str] = None) -> str:
    """
    Generate personality trait descriptions.
    
    Args:
        background: Character background to influence trait
        culture_name: Cultural style to influence trait
        
    Returns:
        Generated personality trait string
    """
    base_traits = [
        "I am always polite and respectful, even to those who don't deserve it.",
        "I have a quick wit and am always ready with a joke or clever comment.",
        "I am extremely curious and ask lots of questions about everything.",
        "I speak very quietly and rarely raise my voice in anger or excitement.",
        "I am fiercely loyal to my friends and would do anything for them.",
        "I have a hard time trusting others and prefer to work alone.",
        "I am always optimistic and look for the bright side in any situation.",
        "I have a strong sense of justice and cannot abide unfairness.",
        "I am very superstitious and see omens and portents everywhere.",
        "I love to tell stories and often embellish them for dramatic effect."
    ]
    
    # Modify based on background
    if background:
        background_lower = background.lower()
        if 'soldier' in background_lower or 'military' in background_lower:
            military_traits = [
                "I maintain strict discipline and expect the same from others.",
                "I have a military bearing and speak in short, precise sentences.",
                "I wake up early every day and keep my gear in perfect condition."
            ]
            base_traits.extend(military_traits)
        
        elif 'scholar' in background_lower or 'sage' in background_lower:
            scholarly_traits = [
                "I correct others' grammar and pronunciation constantly.",
                "I have an extensive vocabulary and use complex words unnecessarily.",
                "I become completely absorbed in my studies and forget to eat or sleep."
            ]
            base_traits.extend(scholarly_traits)
        
        elif 'criminal' in background_lower or 'thief' in background_lower:
            criminal_traits = [
                "I am always looking for the angle or advantage in any situation.",
                "I have a hard time sitting still and am always fidgeting.",
                "I never pass up an opportunity to make some easy money."
            ]
            base_traits.extend(criminal_traits)
    
    # Modify based on culture
    if culture_name:
        culture = get_culture(culture_name)
        if culture:
            try:
                cultural_traits = culture.get_cultural_traits()
                if cultural_traits:
                    base_traits.extend(cultural_traits[:3])  # Add a few cultural traits
            except (AttributeError, Exception):
                pass  # Culture doesn't have cultural traits method
    
    return random.choice(base_traits)


def generate_character_backstory(name_components: NameComponents, 
                               background: Optional[str] = None,
                               length: str = "medium") -> str:
    """
    Generate character backstory text.
    
    Args:
        name_components: Generated name components
        background: Character background
        length: "short", "medium", or "long"
        
    Returns:
        Generated backstory string
    """
    # Extract information from name components
    first_name = name_components.first_name
    cultural_context = name_components.cultural_notes or ""
    
    # Base story templates
    story_templates = {
        "short": [
            f"{first_name} grew up in a small village, where they learned the value of hard work and community. "
            f"Recent events have driven them to seek adventure beyond their humble beginnings.",
            
            f"Born into a family of modest means, {first_name} discovered their talents early in life. "
            f"Now they seek to make their mark upon the world through deed and determination.",
            
            f"{first_name} lived a quiet life until circumstances forced them to leave everything behind. "
            f"They now wander the world, seeking purpose and perhaps redemption."
        ],
        
        "medium": [
            f"{first_name} was born in a time of change and uncertainty. Their childhood was marked by "
            f"both hardship and wonder, as they learned to navigate a world that often seemed hostile to "
            f"their dreams. Despite early setbacks, they developed a strong sense of purpose and an "
            f"unshakeable belief in their own abilities. Recent events have set them on a path of adventure, "
            f"where they hope to prove themselves worthy of the legends they heard as a child.",
            
            f"The early years of {first_name}'s life were spent learning the traditions and customs of "
            f"their people. They showed great promise in their chosen field, but fate had other plans. "
            f"A chance encounter with a mysterious stranger revealed hidden truths about their heritage, "
            f"setting them on a quest that would take them far from home and into realms of danger and wonder."
        ],
        
        "long": [
            f"{first_name} was born during a fierce storm that many took as an omen of the turbulent life "
            f"that lay ahead. Their childhood was spent in the shadow of great events, watching as the world "
            f"around them changed in ways both subtle and profound. Early on, they displayed an unusual "
            f"combination of talents that set them apart from their peers, earning both admiration and suspicion "
            f"from those around them.\n\nAs they came of age, {first_name} faced a series of challenges that "
            f"tested not only their abilities but their character. Each trial taught them valuable lessons about "
            f"the nature of power, responsibility, and sacrifice. They learned that true strength comes not from "
            f"what one can take, but from what one is willing to give.\n\nNow, standing at the threshold of "
            f"their greatest adventure, {first_name} carries with them the wisdom of their experiences and the "
            f"hope that their actions might make the world a better place for those who come after."
        ]
    }
    
    # Select appropriate template
    templates = story_templates.get(length, story_templates["medium"])
    base_story = random.choice(templates)
    
    # Add cultural context if available
    if cultural_context and "emphasizing" in cultural_context.lower():
        try:
            cultural_part = cultural_context.split("emphasizing")[1].split(".")[0].strip()
            cultural_addition = f" Growing up in a culture emphasizing {cultural_part}, " \
                               f"{first_name} learned to value these ancient traditions."
            base_story += cultural_addition
        except (IndexError, AttributeError):
            pass
    
    # Add background-specific elements
    if background:
        background_additions = {
            'acolyte': f" Their early years were spent in religious study and contemplation.",
            'criminal': f" They learned early that sometimes survival requires bending the rules.",
            'folk hero': f" Their reputation for helping others preceded them wherever they went.",
            'hermit': f" Years of solitude taught them to look inward for strength and wisdom.",
            'noble': f" Born to privilege, they learned that true nobility comes from one's actions.",
            'scholar': f" Their thirst for knowledge drove them to seek understanding in ancient texts.",
            'soldier': f" Military training instilled in them discipline and tactical thinking."
        }
        
        for bg_key, addition in background_additions.items():
            if bg_key in background.lower():
                base_story += addition
                break
    
    return base_story


def generate_equipment_description(item_name: str, quality: str = "standard", 
                                 magical: bool = False) -> str:
    """
    Generate equipment descriptions.
    
    Args:
        item_name: Name of the equipment
        quality: Quality level ("poor", "standard", "fine", "masterwork")
        magical: Whether the item is magical
        
    Returns:
        Generated equipment description
    """
    # Base descriptions for common items
    base_descriptions = {
        'sword': 'A well-balanced blade with a sharp edge and sturdy crossguard.',
        'axe': 'A heavy-headed weapon designed for both combat and utility.',
        'bow': 'A curved piece of wood with a taut string, perfect for ranged combat.',
        'shield': 'A protective barrier that can deflect incoming attacks.',
        'armor': 'Protective gear that covers vital areas of the body.',
        'dagger': 'A short, pointed blade ideal for close combat.',
        'staff': 'A long wooden rod that can serve as both weapon and walking aid.',
        'wand': 'A slender magical implement used to channel arcane energies.',
        'ring': 'A circular band worn on the finger.',
        'amulet': 'A protective charm worn around the neck.',
        'cloak': 'A flowing outer garment that provides protection from the elements.',
        'boots': 'Sturdy footwear designed for long journeys.',
        'gloves': 'Hand coverings that provide both protection and dexterity.',
        'belt': 'A band worn around the waist to hold gear and weapons.'
    }
    
    # Get base description
    item_lower = item_name.lower()
    base_description = None
    
    for key, desc in base_descriptions.items():
        if key in item_lower:
            base_description = desc
            break
    
    if not base_description:
        base_description = f"A {item_name} of notable craftsmanship."
    
    # Modify based on quality
    quality_modifiers = {
        'poor': [
            'This item shows signs of wear and poor maintenance.',
            'The craftsmanship is shoddy and the materials are of low quality.',
            'It has seen better days and may not be entirely reliable.'
        ],
        'standard': [
            'This is a typical example of its kind, well-made and functional.',
            'The craftsmanship is solid and the materials are of good quality.',
            'It appears to be in good condition and ready for use.'
        ],
        'fine': [
            'This item shows superior craftsmanship and attention to detail.',
            'The materials are of excellent quality and expertly worked.',
            'Even at first glance, its exceptional nature is apparent.'
        ],
        'masterwork': [
            'This is a masterpiece of its kind, crafted by a true artisan.',
            'Every detail shows the hand of a master craftsperson.',
            'The quality is so exceptional that it borders on the magical.'
        ]
    }
    
    quality_addition = random.choice(quality_modifiers.get(quality, quality_modifiers['standard']))
    
    # Add magical properties if specified
    magical_addition = ""
    if magical:
        magical_properties = [
            'A faint magical aura surrounds this item.',
            'Runes of power are etched along its surface.',
            'It thrums with barely contained magical energy.',
            'The item seems to respond to the wielder\'s touch.',
            'Enchantments have been woven into its very essence.',
            'It glows softly with an inner light.',
            'The air around it shimmers with magical potential.'
        ]
        magical_addition = f" {random.choice(magical_properties)}"
    
    return f"{base_description} {quality_addition}{magical_addition}"


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def split_text_into_sentences(text: str) -> List[str]:
    """
    Split text into sentences.
    
    Args:
        text: Text to split
        
    Returns:
        List of sentences
    """
    if not text:
        return []
    
    # Simple sentence splitting
    sentences = re.split(r'[.!?]+', text)
    
    # Clean up sentences
    sentences = [s.strip() for s in sentences if s.strip()]
    
    return sentences


def join_sentences(sentences: List[str], separator: str = " ") -> str:
    """
    Join sentences with proper punctuation.
    
    Args:
        sentences: List of sentences to join
        separator: Separator between sentences
        
    Returns:
        Joined text
    """
    if not sentences:
        return ""
    
    # Ensure each sentence ends with punctuation
    processed_sentences = []
    for sentence in sentences:
        sentence = sentence.strip()
        if sentence and not sentence[-1] in '.!?':
            sentence += '.'
        processed_sentences.append(sentence)
    
    return separator.join(processed_sentences)


def create_text_summary(text: str, max_length: int = 100) -> str:
    """
    Create a summary of text.
    
    Args:
        text: Text to summarize
        max_length: Maximum length of summary
        
    Returns:
        Text summary
    """
    if not text or len(text) <= max_length:
        return text
    
    # Simple summary: take first sentence(s) up to max_length
    sentences = split_text_into_sentences(text)
    if not sentences:
        return truncate_text(text, max_length)
    
    summary = ""
    for sentence in sentences:
        if len(summary + sentence) <= max_length:
            summary += sentence + ". "
        else:
            break
    
    if not summary:
        # If first sentence is too long, truncate it
        summary = truncate_text(sentences[0], max_length)
    
    return summary.strip()


# ============================================================================
# EXPORTED SYMBOLS
# ============================================================================

__all__ = [
    # Type definitions
    'TextStyle',
    'ContentType', 
    'NameComponents',
    'TextAnalysis',
    'ValidationResult',
    
    # Text formatting
    'format_text',
    'sanitize_text_input',
    'normalize_whitespace',
    'truncate_text',
    
    # Text validation
    'validate_character_sheet_text',
    'validate_name_components',
    
    # Text analysis
    'analyze_text_content',
    'calculate_reading_level',
    'count_syllables',
    'calculate_text_complexity',
    'extract_fantasy_terms',
    'detect_sentiment',
    'extract_keywords',
    'detect_language',
    'extract_cultural_references',
    
    # Name generation (culture-agnostic)
    'generate_character_name',
    'batch_generate_names',
    'get_available_cultures',
    'get_cultures_by_type',
    
    # Content generation
    'generate_personality_trait',
    'generate_character_backstory',
    'generate_equipment_description',
    
    # Utility functions
    'split_text_into_sentences',
    'join_sentences',
    'create_text_summary'
]

# ============================================================================
# MODULE METADATA
# ============================================================================

__version__ = "1.0.0"
__description__ = "Text Processing Utilities for D&D Character Creation"

# Clean Architecture compliance
CLEAN_ARCHITECTURE_COMPLIANCE = {
    "layer": "core/utils",
    "dependencies": ["typing", "re", "random", "string", "unicodedata", "json", "collections", "math", "cultures"],
    "dependents": ["domain_services", "application_use_cases"],
    "infrastructure_independent": True,
    "pure_functions": True,
    "side_effects": "none",
    "focuses_on": "Text processing and manipulation utilities independent of specific cultures"
}