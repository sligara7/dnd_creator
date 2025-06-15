"""
Enhanced Text Processing Utilities for D&D Creative Content Framework.

COMPLETELY REFACTORED: Full integration with enhanced culture system, validation framework,
and LLM providers following CREATIVE_VALIDATION_APPROACH philosophy.

This module provides enhanced pure utility functions for:
- Text formatting and validation for character sheets with enum integration
- Natural language processing for character descriptions with cultural context
- Lore text analysis and generation with LLM provider support
- String manipulation and sanitization with culture-aware processing
- Content generation using enhanced cultural naming systems with validation
- Multi-language support for international D&D content with cultural authenticity
- Character generation support with preset compatibility and enhancement targeting

Enhanced Features:
- Complete integration with enhanced culture_types enums
- Culture-aware text processing with authenticity level assessment
- LLM provider integration for enhanced content generation
- Creative validation approach with constructive enhancement suggestions
- Character generation focus with preset compatibility
- Enhancement category targeting for content improvement
- Gaming utility optimization throughout text processing

Following Clean Architecture principles, these utilities are:
- Infrastructure-independent (configurable LLM providers)
- Pure functions with no side effects (where possible)
- Focused on text processing and enhanced linguistic operations
- Used by domain services and application use cases with culture integration
- Support character creation and content generation workflows with validation
- Culture-aware processing with enum-based cultural insights

This module integrates with the enhanced cultures module at /backend6/core/utils/cultures/
and validation system at /backend6/core/utils/validation/ for comprehensive cultural support.
"""

import re
import random
import string
import unicodedata
from typing import Dict, List, Optional, Tuple, Union, Set, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
from collections import Counter, defaultdict
import math
from datetime import datetime

# Enhanced culture system imports
from ..cultures import (
    get_culture_enhanced,
    list_cultures_enhanced,
    get_cultures_by_type_enhanced,
    generate_culture_content,
    CultureGenerationRequest,
    CultureGenerationResult
)

# Enhanced validation system imports
from ..validation import (
    validate_culture_for_characters,
    quick_culture_assessment,
    validate_character_culture_enhanced,
    get_culture_enhancement_suggestions_enhanced,
    EnhancedCreativeCultureValidator,
    EnhancedCreativeValidationResult
)

# Enhanced enum imports
from ...enums.culture_types import (
    # Core generation and validation enums
    CultureGenerationType,
    CultureAuthenticityLevel,
    CultureCreativityLevel,
    CultureSourceType,
    CultureComplexityLevel,
    CultureValidationSeverity,
    
    # Enhancement system enums
    CultureEnhancementCategory,
    CultureEnhancementPriority,
    CultureGenerationStatus,
    
    # Cultural structure enums
    CultureNamingStructure,
    CultureGenderSystem,
    CultureLinguisticFamily,
    CultureTemporalPeriod,
    
    # Enhanced utility functions
    suggest_creative_culture_enhancements,
    calculate_character_generation_score,
    get_character_generation_recommendations,
    
    # Preset system
    CHARACTER_CULTURE_PRESETS
)

# LLM provider integration
from ...abstractions.culture_llm_providers import (
    CultureLLMProvider,
    CultureGenerationPrompt,
    CultureLLMResponse,
    get_default_culture_provider,
    register_culture_provider
)

# ============================================================================
# ENHANCED TYPE DEFINITIONS AND ENUMS
# ============================================================================

class EnhancedTextStyle(Enum):
    """Enhanced text formatting styles with cultural awareness."""
    PLAIN = "plain"
    TITLE_CASE = "title"
    UPPER_CASE = "upper"
    LOWER_CASE = "lower"
    SENTENCE_CASE = "sentence"
    CAMEL_CASE = "camel"
    SNAKE_CASE = "snake"
    KEBAB_CASE = "kebab"
    # NEW: Cultural formatting styles
    CULTURAL_TRADITIONAL = "cultural_traditional"
    CULTURAL_MODERN = "cultural_modern"
    FANTASY_ARCHAIC = "fantasy_archaic"
    GAMING_FRIENDLY = "gaming_friendly"


class EnhancedContentType(Enum):
    """Enhanced types of D&D content for processing with cultural context."""
    # Character-related content
    CHARACTER_NAME = "character_name"
    CHARACTER_NICKNAME = "character_nickname"
    CHARACTER_TITLE = "character_title"
    CHARACTER_EPITHET = "character_epithet"
    
    # Location content
    PLACE_NAME = "place_name"
    SETTLEMENT_NAME = "settlement_name"
    GEOGRAPHIC_FEATURE = "geographic_feature"
    
    # Item and equipment content
    ITEM_NAME = "item_name"
    WEAPON_NAME = "weapon_name"
    ARTIFACT_NAME = "artifact_name"
    
    # Magical content
    SPELL_NAME = "spell_name"
    ABILITY_NAME = "ability_name"
    RITUAL_NAME = "ritual_name"
    
    # Character background content
    PERSONALITY_TRAIT = "personality_trait"
    IDEAL = "ideal"
    BOND = "bond"
    FLAW = "flaw"
    MOTIVATION = "motivation"
    FEAR = "fear"
    
    # Narrative content
    BACKGROUND_STORY = "background_story"
    CHARACTER_HISTORY = "character_history"
    CULTURAL_BACKGROUND = "cultural_background"
    
    # Physical descriptions
    PHYSICAL_DESCRIPTION = "physical_description"
    CLOTHING_DESCRIPTION = "clothing_description"
    EQUIPMENT_DESCRIPTION = "equipment_description"
    
    # Cultural content (NEW)
    CULTURAL_TRADITION = "cultural_tradition"
    CULTURAL_VALUE = "cultural_value"
    CULTURAL_CUSTOM = "cultural_custom"
    CULTURAL_CONFLICT = "cultural_conflict"
    CULTURAL_MYSTERY = "cultural_mystery"
    
    # Gaming utility content (NEW)
    PRONUNCIATION_GUIDE = "pronunciation_guide"
    GAMING_NOTES = "gaming_notes"
    CHARACTER_HOOK = "character_hook"


@dataclass(frozen=True)
class EnhancedNameComponents:
    """Enhanced components of a generated name with cultural context."""
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
    
    # NEW: Enhanced cultural context
    culture_name: Optional[str] = None
    authenticity_level: Optional[CultureAuthenticityLevel] = None
    naming_structure: Optional[CultureNamingStructure] = None
    gender_system: Optional[CultureGenderSystem] = None
    linguistic_family: Optional[CultureLinguisticFamily] = None
    
    # NEW: Gaming utility
    gaming_pronunciation: Optional[str] = None
    memorability_score: Optional[float] = None
    table_friendliness_score: Optional[float] = None
    character_archetype_fit: Optional[List[str]] = None
    
    # NEW: Validation and enhancement
    validation_result: Optional[EnhancedCreativeValidationResult] = None
    enhancement_suggestions: Optional[List[str]] = None
    character_generation_score: Optional[float] = None


@dataclass(frozen=True)
class EnhancedTextAnalysis:
    """Enhanced analysis results for text content with cultural insights."""
    # Basic metrics
    word_count: int
    character_count: int
    sentence_count: int
    paragraph_count: int
    reading_level: float
    complexity_score: float
    
    # Content analysis
    fantasy_terms: List[str]
    sentiment_score: float
    keywords: List[Tuple[str, int]]
    language_detected: Optional[str]
    cultural_references: List[str]
    
    # NEW: Enhanced cultural analysis
    detected_culture_patterns: List[str] = field(default_factory=list)
    authenticity_indicators: Dict[str, float] = field(default_factory=dict)
    creativity_markers: List[str] = field(default_factory=list)
    cultural_consistency_score: float = 0.0
    
    # NEW: Character generation insights
    character_background_potential: float = 0.0
    name_generation_quality: float = 0.0
    gaming_utility_score: float = 0.0
    roleplay_potential: float = 0.0
    
    # NEW: Enhancement opportunities
    enhancement_categories: List[CultureEnhancementCategory] = field(default_factory=list)
    improvement_suggestions: List[str] = field(default_factory=list)
    preset_compatibility: Dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class EnhancedValidationResult:
    """Enhanced text validation result with cultural context."""
    is_valid: bool
    errors: List[str]
    warnings: List[str] = field(default_factory=list)
    
    # NEW: Cultural validation
    cultural_appropriateness: float = 1.0
    authenticity_score: float = 0.5
    creativity_score: float = 0.5
    
    # NEW: Character generation readiness
    character_generation_ready: bool = True
    gaming_table_ready: bool = True
    enhancement_priority: CultureEnhancementPriority = CultureEnhancementPriority.OPTIONAL
    
    # NEW: Enhancement suggestions
    enhancement_categories: List[CultureEnhancementCategory] = field(default_factory=list)
    suggested_improvements: List[str] = field(default_factory=list)
    validation_notes: List[str] = field(default_factory=list)


# ============================================================================
# ENHANCED CORE TEXT FORMATTING FUNCTIONS
# ============================================================================

def format_text_enhanced(text: str, style: EnhancedTextStyle, 
                        cultural_context: Optional[str] = None,
                        authenticity_level: Optional[CultureAuthenticityLevel] = None) -> str:
    """
    Enhanced text formatting with cultural awareness.
    
    Args:
        text: Text to format
        style: Enhanced formatting style to apply
        cultural_context: Optional culture name for cultural formatting
        authenticity_level: Optional authenticity level for historical accuracy
        
    Returns:
        Formatted text string with cultural considerations
        
    Examples:
        >>> format_text_enhanced("thorin ironforge", EnhancedTextStyle.CULTURAL_TRADITIONAL, "norse")
        "Thorin Ironforge"
        >>> format_text_enhanced("magic_sword", EnhancedTextStyle.GAMING_FRIENDLY)
        "Magic Sword"
    """
    if not text:
        return text
    
    # Handle basic styles first
    if style == EnhancedTextStyle.PLAIN:
        return text
    elif style == EnhancedTextStyle.TITLE_CASE:
        return text.title()
    elif style == EnhancedTextStyle.UPPER_CASE:
        return text.upper()
    elif style == EnhancedTextStyle.LOWER_CASE:
        return text.lower()
    elif style == EnhancedTextStyle.SENTENCE_CASE:
        return text.capitalize()
    elif style == EnhancedTextStyle.CAMEL_CASE:
        words = re.split(r'[\s_-]+', text.lower())
        return words[0] + ''.join(word.capitalize() for word in words[1:])
    elif style == EnhancedTextStyle.SNAKE_CASE:
        text = re.sub(r'([A-Z])', r'_\1', text)
        text = re.sub(r'[\s-]+', '_', text)
        return text.lower().strip('_')
    elif style == EnhancedTextStyle.KEBAB_CASE:
        text = re.sub(r'([A-Z])', r'-\1', text)
        text = re.sub(r'[\s_]+', '-', text)
        return text.lower().strip('-')
    
    # Handle enhanced cultural styles
    elif style == EnhancedTextStyle.CULTURAL_TRADITIONAL:
        return _apply_cultural_traditional_formatting(text, cultural_context, authenticity_level)
    elif style == EnhancedTextStyle.CULTURAL_MODERN:
        return _apply_cultural_modern_formatting(text, cultural_context)
    elif style == EnhancedTextStyle.FANTASY_ARCHAIC:
        return _apply_fantasy_archaic_formatting(text)
    elif style == EnhancedTextStyle.GAMING_FRIENDLY:
        return _apply_gaming_friendly_formatting(text)
    
    return text


def _apply_cultural_traditional_formatting(text: str, cultural_context: Optional[str],
                                         authenticity_level: Optional[CultureAuthenticityLevel]) -> str:
    """Apply traditional cultural formatting based on context."""
    if not cultural_context:
        return text.title()
    
    try:
        culture = get_culture_enhanced(cultural_context)
        if culture and hasattr(culture, 'apply_traditional_formatting'):
            return culture.apply_traditional_formatting(text, authenticity_level)
    except Exception:
        pass
    
    # Fallback to enhanced title case with cultural patterns
    if cultural_context.lower() in ['norse', 'viking', 'germanic']:
        # Norse names often have compound elements
        if ' ' in text:
            parts = text.split()
            return ' '.join(part.capitalize() for part in parts)
        else:
            return text.capitalize()
    elif cultural_context.lower() in ['celtic', 'irish', 'scottish', 'welsh']:
        # Celtic names often have specific capitalization patterns
        text = text.title()
        # Handle common Celtic prefixes
        text = re.sub(r'\bMac([A-Z])', r'Mac\1', text)
        text = re.sub(r'\bO\'([A-Z])', r"O'\1", text)
        return text
    elif cultural_context.lower() in ['asian', 'chinese', 'japanese', 'korean']:
        # Asian names often have specific ordering
        return text.title()
    
    return text.title()


def _apply_cultural_modern_formatting(text: str, cultural_context: Optional[str]) -> str:
    """Apply modern cultural formatting."""
    # Modern formatting tends to be more standardized
    return text.title()


def _apply_fantasy_archaic_formatting(text: str) -> str:
    """Apply fantasy archaic formatting for medieval/fantasy feel."""
    # Add archaic elements where appropriate
    text = text.title()
    
    # Replace some modern patterns with archaic ones
    replacements = {
        r'\bThe\b': 'Ye',
        r'\bAnd\b': '&',
        r'\bOf\b': 'of'  # Keep 'of' lowercase in titles
    }
    
    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text)
    
    return text


def _apply_gaming_friendly_formatting(text: str) -> str:
    """Apply gaming-friendly formatting for table use."""
    # Gaming-friendly formatting prioritizes readability and brevity
    text = text.replace('_', ' ').replace('-', ' ')
    words = text.split()
    
    # Capitalize important words, keep articles/prepositions lowercase
    small_words = {'a', 'an', 'and', 'as', 'at', 'but', 'by', 'for', 'if', 'in', 
                  'nor', 'of', 'on', 'or', 'so', 'the', 'to', 'up', 'yet'}
    
    result = []
    for i, word in enumerate(words):
        if i == 0 or word.lower() not in small_words:
            result.append(word.capitalize())
        else:
            result.append(word.lower())
    
    return ' '.join(result)


def sanitize_text_input_enhanced(text: str, max_length: int = 1000, 
                               allow_unicode: bool = True,
                               content_type: Optional[EnhancedContentType] = None,
                               cultural_context: Optional[str] = None) -> str:
    """
    Enhanced sanitization with cultural awareness and content type validation.
    
    Args:
        text: Text to sanitize
        max_length: Maximum allowed length
        allow_unicode: Whether to allow Unicode characters
        content_type: Type of content for specialized sanitization
        cultural_context: Cultural context for appropriate character handling
        
    Returns:
        Sanitized text string with cultural considerations
    """
    if not text:
        return ""
    
    # Content-type specific length limits
    if content_type:
        content_max_lengths = {
            EnhancedContentType.CHARACTER_NAME: 50,
            EnhancedContentType.CHARACTER_NICKNAME: 30,
            EnhancedContentType.CHARACTER_TITLE: 100,
            EnhancedContentType.PERSONALITY_TRAIT: 200,
            EnhancedContentType.BACKGROUND_STORY: 2000,
            EnhancedContentType.PHYSICAL_DESCRIPTION: 500,
            EnhancedContentType.CULTURAL_TRADITION: 300,
            EnhancedContentType.PRONUNCIATION_GUIDE: 100
        }
        max_length = min(max_length, content_max_lengths.get(content_type, max_length))
    
    # Truncate to max length
    text = text[:max_length]
    
    # Remove or replace dangerous characters
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
    
    # Handle Unicode with cultural awareness
    if not allow_unicode:
        # But preserve culturally important diacritics if cultural context suggests it
        if cultural_context and _should_preserve_diacritics(cultural_context):
            # Preserve common diacritics for this culture
            preserved_chars = _get_cultural_diacritics(cultural_context)
            text = ''.join(char if char in preserved_chars or ord(char) < 128 
                          else unicodedata.normalize('NFKD', char).encode('ascii', 'ignore').decode('ascii')
                          for char in text)
        else:
            text = unicodedata.normalize('NFKD', text)
            text = text.encode('ascii', 'ignore').decode('ascii')
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Content-type specific sanitization
    if content_type == EnhancedContentType.CHARACTER_NAME:
        # Names should only contain letters, spaces, hyphens, apostrophes, and periods
        text = re.sub(r'[^a-zA-Z\s\'-\.\u00C0-\u017F]', '', text)
    elif content_type == EnhancedContentType.PRONUNCIATION_GUIDE:
        # Pronunciation guides can contain more phonetic characters
        text = re.sub(r'[^a-zA-Z\s\'-\.\[\]\/\u00C0-\u017F]', '', text)
    
    # Remove potentially harmful patterns
    dangerous_patterns = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
        r'<iframe[^>]*>.*?</iframe>'
    ]
    
    for pattern in dangerous_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)
    
    return text


def _should_preserve_diacritics(cultural_context: str) -> bool:
    """Determine if diacritics should be preserved for a cultural context."""
    diacritic_cultures = [
        'french', 'spanish', 'portuguese', 'italian', 'german', 'scandinavian',
        'norse', 'celtic', 'polish', 'czech', 'hungarian', 'romanian'
    ]
    return any(culture in cultural_context.lower() for culture in diacritic_cultures)


def _get_cultural_diacritics(cultural_context: str) -> str:
    """Get culturally appropriate diacritics to preserve."""
    cultural_diacritics = {
        'french': 'àáâäèéêëîïôöùúûüÿç',
        'spanish': 'àáéíñóúü',
        'german': 'äöüß',
        'scandinavian': 'åæøäöé',
        'norse': 'åæøþð',
        'celtic': 'áéíóúàèìòù'
    }
    
    for culture, diacritics in cultural_diacritics.items():
        if culture in cultural_context.lower():
            return diacritics + diacritics.upper()
    
    return 'àáâäèéêëîïôöùúûüÿç'  # Default to French diacritics


# ============================================================================
# ENHANCED TEXT VALIDATION FUNCTIONS
# ============================================================================

def validate_character_sheet_text_enhanced(text: str, content_type: EnhancedContentType,
                                         cultural_context: Optional[str] = None,
                                         target_preset: Optional[str] = None) -> EnhancedValidationResult:
    """
    Enhanced validation for character sheet text with cultural awareness.
    
    Args:
        text: Text to validate
        content_type: Type of content being validated
        cultural_context: Optional culture name for cultural validation
        target_preset: Optional preset for optimization validation
        
    Returns:
        EnhancedValidationResult with comprehensive validation and enhancement suggestions
    """
    errors = []
    warnings = []
    enhancement_categories = []
    suggested_improvements = []
    validation_notes = []
    
    if not text:
        errors.append("Text cannot be empty")
        return EnhancedValidationResult(
            is_valid=False, 
            errors=errors, 
            warnings=warnings,
            character_generation_ready=False,
            enhancement_priority=CultureEnhancementPriority.CHARACTER_CRITICAL,
            enhancement_categories=[CultureEnhancementCategory.CHARACTER_NAMES],
            suggested_improvements=["Add content to enable character generation"]
        )
    
    # Content-specific validation with cultural awareness
    cultural_appropriateness = 1.0
    authenticity_score = 0.5
    creativity_score = 0.5
    
    if content_type == EnhancedContentType.CHARACTER_NAME:
        validation_result = _validate_character_name_enhanced(text, cultural_context, target_preset)
        errors.extend(validation_result['errors'])
        warnings.extend(validation_result['warnings'])
        enhancement_categories.extend(validation_result['enhancement_categories'])
        suggested_improvements.extend(validation_result['suggested_improvements'])
        cultural_appropriateness = validation_result['cultural_appropriateness']
        authenticity_score = validation_result['authenticity_score']
        
    elif content_type == EnhancedContentType.PERSONALITY_TRAIT:
        validation_result = _validate_personality_trait_enhanced(text, cultural_context)
        errors.extend(validation_result['errors'])
        warnings.extend(validation_result['warnings'])
        creativity_score = validation_result['creativity_score']
        
    elif content_type == EnhancedContentType.BACKGROUND_STORY:
        validation_result = _validate_background_story_enhanced(text, cultural_context, target_preset)
        errors.extend(validation_result['errors'])
        warnings.extend(validation_result['warnings'])
        enhancement_categories.extend(validation_result['enhancement_categories'])
        suggested_improvements.extend(validation_result['suggested_improvements'])
        
    elif content_type in [EnhancedContentType.CULTURAL_TRADITION, EnhancedContentType.CULTURAL_VALUE]:
        validation_result = _validate_cultural_content_enhanced(text, cultural_context)
        errors.extend(validation_result['errors'])
        warnings.extend(validation_result['warnings'])
        cultural_appropriateness = validation_result['cultural_appropriateness']
        authenticity_score = validation_result['authenticity_score']
    
    # General quality checks
    if text.count('\n') > 10:
        warnings.append("Text has many line breaks - consider reformatting for better readability")
        enhancement_categories.append(CultureEnhancementCategory.GAMING_UTILITY)
    
    # Check for character variety
    unique_chars = len(set(text.lower().replace(' ', '')))
    if unique_chars < 3 and len(text) > 10:
        errors.append("Text lacks character variety")
        enhancement_categories.append(CultureEnhancementCategory.CREATIVE_ELEMENTS)
    
    # Gaming utility assessment
    gaming_table_ready = _assess_gaming_table_readiness(text, content_type)
    if not gaming_table_ready:
        warnings.append("Content could be optimized for gaming table use")
        enhancement_categories.append(CultureEnhancementCategory.GAMING_UTILITY)
        suggested_improvements.append("Consider simplifying for easier table use")
    
    # Enhancement priority assessment
    enhancement_priority = CultureEnhancementPriority.OPTIONAL
    if errors:
        enhancement_priority = CultureEnhancementPriority.CHARACTER_CRITICAL
    elif len(warnings) > 2:
        enhancement_priority = CultureEnhancementPriority.CHARACTER_IMPORTANT
    elif enhancement_categories:
        enhancement_priority = CultureEnhancementPriority.GAMING_HELPFUL
    
    return EnhancedValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        cultural_appropriateness=cultural_appropriateness,
        authenticity_score=authenticity_score,
        creativity_score=creativity_score,
        character_generation_ready=len(errors) == 0,
        gaming_table_ready=gaming_table_ready,
        enhancement_priority=enhancement_priority,
        enhancement_categories=list(set(enhancement_categories)),
        suggested_improvements=suggested_improvements,
        validation_notes=validation_notes
    )


def _validate_character_name_enhanced(name: str, cultural_context: Optional[str],
                                    target_preset: Optional[str]) -> Dict[str, Any]:
    """Enhanced character name validation with cultural context."""
    errors = []
    warnings = []
    enhancement_categories = []
    suggested_improvements = []
    
    # Basic validation
    if len(name) > 50:
        errors.append("Character name too long (max 50 characters)")
    if len(name.strip()) < 2:
        errors.append("Character name too short")
        enhancement_categories.append(CultureEnhancementCategory.CHARACTER_NAMES)
    
    # Cultural validation
    cultural_appropriateness = 1.0
    authenticity_score = 0.5
    
    if cultural_context:
        try:
            culture = get_culture_enhanced(cultural_context)
            if culture:
                # Use culture's name validation if available
                if hasattr(culture, 'validate_name'):
                    culture_validation = culture.validate_name(name)
                    if not culture_validation.get('is_valid', True):
                        warnings.extend(culture_validation.get('warnings', []))
                        cultural_appropriateness = culture_validation.get('appropriateness_score', 0.8)
                        authenticity_score = culture_validation.get('authenticity_score', 0.5)
                
                # Check name pattern consistency
                name_pattern_result = _assess_name_cultural_pattern(name, culture)
                if name_pattern_result['needs_improvement']:
                    warnings.append(f"Name doesn't match typical {cultural_context} patterns")
                    suggested_improvements.append(f"Consider names more typical of {cultural_context} culture")
                    enhancement_categories.append(CultureEnhancementCategory.CULTURAL_TRAITS)
        except Exception:
            validation_notes = [f"Could not validate against {cultural_context} culture patterns"]
    
    # Gaming utility validation
    if target_preset == "gaming_optimized" or target_preset == "table_friendly":
        gaming_assessment = _assess_name_gaming_utility(name)
        if gaming_assessment['difficulty_score'] > 0.7:
            warnings.append("Name may be difficult to pronounce at gaming table")
            enhancement_categories.append(CultureEnhancementCategory.PRONUNCIATION)
            suggested_improvements.append("Consider simpler pronunciation for table use")
    
    # Character validation patterns
    if not re.match(r'^[a-zA-Z\s\'-\.\u00C0-\u017F]+$', name):
        errors.append("Character name contains invalid characters")
        enhancement_categories.append(CultureEnhancementCategory.CHARACTER_NAMES)
    
    return {
        'errors': errors,
        'warnings': warnings,
        'enhancement_categories': enhancement_categories,
        'suggested_improvements': suggested_improvements,
        'cultural_appropriateness': cultural_appropriateness,
        'authenticity_score': authenticity_score
    }


def _validate_personality_trait_enhanced(trait: str, cultural_context: Optional[str]) -> Dict[str, Any]:
    """Enhanced personality trait validation."""
    errors = []
    warnings = []
    creativity_score = 0.5
    
    if len(trait) > 200:
        errors.append("Personality trait too long (max 200 characters)")
    if len(trait.split()) < 3:
        warnings.append("Personality trait should be at least 3 words for richness")
    if not trait.strip().endswith('.'):
        warnings.append("Personality trait should end with a period")
    
    # Assess creativity
    creativity_indicators = ['unique', 'unusual', 'distinctive', 'memorable', 'interesting']
    if any(indicator in trait.lower() for indicator in creativity_indicators):
        creativity_score += 0.2
    
    # Check for cultural integration
    if cultural_context:
        try:
            culture = get_culture_enhanced(cultural_context)
            if culture and hasattr(culture, 'get_cultural_traits'):
                cultural_traits = culture.get_cultural_traits()
                if cultural_traits and any(ct.lower() in trait.lower() for ct in cultural_traits):
                    creativity_score += 0.3
        except Exception:
            pass
    
    return {
        'errors': errors,
        'warnings': warnings,
        'creativity_score': min(1.0, creativity_score)
    }


def _validate_background_story_enhanced(story: str, cultural_context: Optional[str],
                                      target_preset: Optional[str]) -> Dict[str, Any]:
    """Enhanced background story validation."""
    errors = []
    warnings = []
    enhancement_categories = []
    suggested_improvements = []
    
    if len(story) > 2000:
        errors.append("Background story too long (max 2000 characters)")
    
    word_count = len(story.split())
    if word_count < 10:
        warnings.append("Background story should be at least 10 words")
        enhancement_categories.append(CultureEnhancementCategory.NARRATIVE_DEPTH)
    elif word_count > 500:
        warnings.append("Background story is quite long - consider condensing for table use")
        enhancement_categories.append(CultureEnhancementCategory.GAMING_UTILITY)
        if target_preset in ["gaming_optimized", "table_friendly"]:
            suggested_improvements.append("Shorten story for better gaming table usability")
    
    # Check for character hooks
    hook_indicators = ['conflict', 'mystery', 'secret', 'quest', 'revenge', 'lost', 'seeking']
    if not any(indicator in story.lower() for indicator in hook_indicators):
        warnings.append("Background story could benefit from character hooks for roleplay")
        enhancement_categories.append(CultureEnhancementCategory.BACKGROUND_HOOKS)
        suggested_improvements.append("Add character hooks like conflicts, mysteries, or personal quests")
    
    return {
        'errors': errors,
        'warnings': warnings,
        'enhancement_categories': enhancement_categories,
        'suggested_improvements': suggested_improvements
    }


def _validate_cultural_content_enhanced(content: str, cultural_context: Optional[str]) -> Dict[str, Any]:
    """Enhanced cultural content validation."""
    errors = []
    warnings = []
    cultural_appropriateness = 1.0
    authenticity_score = 0.5
    
    if not cultural_context:
        warnings.append("Cultural content would benefit from cultural context")
        return {
            'errors': errors,
            'warnings': warnings,
            'cultural_appropriateness': cultural_appropriateness,
            'authenticity_score': authenticity_score
        }
    
    try:
        # Use validation system to assess cultural content
        culture_data = {'cultural_content': content, 'name': f'Validation Culture for {cultural_context}'}
        validation_result = validate_culture_for_characters(culture_data, target_preset="creative_focused")
        
        cultural_appropriateness = validation_result.creative_quality_score
        authenticity_score = validation_result.character_support_score
        
        if cultural_appropriateness < 0.6:
            warnings.append("Cultural content could be more culturally integrated")
        if authenticity_score < 0.6:
            warnings.append("Cultural content could be more authentic to the cultural context")
            
    except Exception:
        warnings.append("Could not validate cultural content against cultural context")
    
    return {
        'errors': errors,
        'warnings': warnings,
        'cultural_appropriateness': cultural_appropriateness,
        'authenticity_score': authenticity_score
    }


def _assess_name_cultural_pattern(name: str, culture) -> Dict[str, Any]:
    """Assess how well a name matches cultural patterns."""
    try:
        if hasattr(culture, 'assess_name_pattern'):
            return culture.assess_name_pattern(name)
        
        # Basic pattern assessment
        all_names = []
        if hasattr(culture, 'get_male_names'):
            all_names.extend(culture.get_male_names() or [])
        if hasattr(culture, 'get_female_names'):
            all_names.extend(culture.get_female_names() or [])
        
        if not all_names:
            return {'needs_improvement': False, 'similarity_score': 0.5}
        
        # Simple similarity check
        name_lower = name.lower()
        similarities = []
        
        for culture_name in all_names:
            culture_name_lower = culture_name.lower()
            # Check for common prefixes/suffixes
            similarity = 0
            if name_lower[:2] == culture_name_lower[:2]:
                similarity += 0.3
            if name_lower[-2:] == culture_name_lower[-2:]:
                similarity += 0.3
            if len(name) == len(culture_name):
                similarity += 0.2
            similarities.append(similarity)
        
        avg_similarity = sum(similarities) / len(similarities) if similarities else 0
        
        return {
            'needs_improvement': avg_similarity < 0.3,
            'similarity_score': avg_similarity
        }
        
    except Exception:
        return {'needs_improvement': False, 'similarity_score': 0.5}


def _assess_name_gaming_utility(name: str) -> Dict[str, Any]:
    """Assess gaming utility of a name."""
    difficulty_score = 0.0
    
    # Length assessment
    if len(name) > 12:
        difficulty_score += 0.3
    elif len(name) > 8:
        difficulty_score += 0.1
    
    # Pronunciation difficulty
    difficult_patterns = ['sch', 'tch', 'pht', 'xth', 'ght']
    for pattern in difficult_patterns:
        if pattern in name.lower():
            difficulty_score += 0.2
    
    # Multiple apostrophes or hyphens
    special_chars = name.count("'") + name.count("-")
    if special_chars > 1:
        difficulty_score += 0.2
    
    # Consonant clusters
    consonant_clusters = 0
    for i in range(len(name) - 1):
        if name[i].lower() not in 'aeiou' and name[i + 1].lower() not in 'aeiou':
            consonant_clusters += 1
    
    if consonant_clusters > 3:
        difficulty_score += 0.3
    
    return {
        'difficulty_score': min(1.0, difficulty_score),
        'gaming_friendly': difficulty_score < 0.4
    }


def _assess_gaming_table_readiness(text: str, content_type: EnhancedContentType) -> bool:
    """Assess if content is ready for gaming table use."""
    # Length thresholds for different content types
    length_thresholds = {
        EnhancedContentType.CHARACTER_NAME: 50,
        EnhancedContentType.PERSONALITY_TRAIT: 150,
        EnhancedContentType.BACKGROUND_STORY: 300,  # Shorter for table use
        EnhancedContentType.PHYSICAL_DESCRIPTION: 200,
        EnhancedContentType.CULTURAL_TRADITION: 200
    }
    
    max_length = length_thresholds.get(content_type, 200)
    if len(text) > max_length:
        return False
    
    # Check for overly complex language
    complex_words = len([word for word in text.split() if len(word) > 12])
    if complex_words > len(text.split()) * 0.1:  # More than 10% complex words
        return False
    
    # Check sentence complexity
    sentences = re.split(r'[.!?]+', text)
    avg_sentence_length = sum(len(s.split()) for s in sentences if s.strip()) / max(len(sentences), 1)
    if avg_sentence_length > 25:  # Very long sentences
        return False
    
    return True


# ============================================================================
# ENHANCED TEXT ANALYSIS FUNCTIONS
# ============================================================================

def analyze_text_content_enhanced(text: str, cultural_context: Optional[str] = None,
                                target_preset: Optional[str] = None) -> EnhancedTextAnalysis:
    """
    Enhanced text analysis with cultural insights and character generation focus.
    
    Args:
        text: Text to analyze
        cultural_context: Optional culture name for cultural analysis
        target_preset: Optional preset for compatibility analysis
        
    Returns:
        EnhancedTextAnalysis with comprehensive metrics and cultural insights
    """
    if not text:
        return EnhancedTextAnalysis(
            word_count=0, character_count=0, sentence_count=0, paragraph_count=0,
            reading_level=0.0, complexity_score=0.0, fantasy_terms=[],
            sentiment_score=0.0, keywords=[], language_detected=None, cultural_references=[]
        )
    
    # Basic analysis
    word_count = len(text.split())
    character_count = len(text)
    sentence_count = len(re.findall(r'[.!?]+', text))
    paragraph_count = len([p for p in text.split('\n\n') if p.strip()])
    
    reading_level = calculate_reading_level_enhanced(text)
    complexity_score = calculate_text_complexity_enhanced(text)
    fantasy_terms = extract_fantasy_terms_enhanced(text)
    sentiment_score = detect_sentiment_enhanced(text)
    keywords = extract_keywords_enhanced(text)
    language_detected = detect_language_enhanced(text)
    cultural_references = extract_cultural_references_enhanced(text)
    
    # Enhanced cultural analysis
    detected_culture_patterns = _detect_culture_patterns(text, cultural_context)
    authenticity_indicators = _assess_authenticity_indicators(text, cultural_context)
    creativity_markers = _extract_creativity_markers(text)
    cultural_consistency_score = _calculate_cultural_consistency(text, cultural_context)
    
    # Character generation insights
    character_background_potential = _assess_character_background_potential(text)
    name_generation_quality = _assess_name_generation_quality(text)
    gaming_utility_score = _assess_text_gaming_utility(text)
    roleplay_potential = _assess_roleplay_potential(text)
    
    # Enhancement opportunities
    enhancement_categories = _identify_enhancement_categories(text, cultural_context)
    improvement_suggestions = _generate_improvement_suggestions(text, enhancement_categories)
    preset_compatibility = _assess_preset_compatibility(text, target_preset)
    
    return EnhancedTextAnalysis(
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
        cultural_references=cultural_references,
        detected_culture_patterns=detected_culture_patterns,
        authenticity_indicators=authenticity_indicators,
        creativity_markers=creativity_markers,
        cultural_consistency_score=cultural_consistency_score,
        character_background_potential=character_background_potential,
        name_generation_quality=name_generation_quality,
        gaming_utility_score=gaming_utility_score,
        roleplay_potential=roleplay_potential,
        enhancement_categories=enhancement_categories,
        improvement_suggestions=improvement_suggestions,
        preset_compatibility=preset_compatibility
    )


def calculate_reading_level_enhanced(text: str) -> float:
    """Enhanced reading level calculation with cultural context awareness."""
    if not text or not text.strip():
        return 0.0
    
    sentences = re.findall(r'[.!?]+', text)
    words = text.split()
    syllables = sum(count_syllables_enhanced(word) for word in words)
    
    if len(sentences) == 0 or len(words) == 0:
        return 0.0
    
    avg_sentence_length = len(words) / len(sentences)
    avg_syllables_per_word = syllables / len(words)
    
    # Enhanced Flesch Reading Ease with fantasy/cultural adjustments
    reading_ease = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
    
    # Adjust for fantasy terminology complexity
    fantasy_terms = extract_fantasy_terms_enhanced(text)
    if fantasy_terms:
        fantasy_adjustment = min(10, len(fantasy_terms) * 2)  # Reduce readability for fantasy terms
        reading_ease -= fantasy_adjustment
    
    return max(0.0, min(100.0, reading_ease))


def count_syllables_enhanced(word: str) -> int:
    """Enhanced syllable counting with better accuracy for fantasy names."""
    word = word.lower().strip('.,!?";')
    if not word:
        return 0
    
    # Special handling for common fantasy name patterns
    if any(pattern in word for pattern in ['ae', 'ael', 'ian', 'ien', 'tion']):
        # These patterns often have specific syllable counts
        if word.endswith('tion'):
            return len(re.findall(r'[aeiouy]+', word[:-4])) + 1
        elif 'ae' in word:
            return len(re.findall(r'[aeiouy]+', word)) + 1  # 'ae' usually adds a syllable
    
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


def calculate_text_complexity_enhanced(text: str) -> float:
    """Enhanced text complexity calculation with cultural and gaming considerations."""
    if not text:
        return 0.0
    
    words = text.split()
    if not words:
        return 0.0
    
    complexity = 0.0
    
    # Average word length (cultural names often longer)
    avg_word_length = sum(len(word) for word in words) / len(words)
    complexity += avg_word_length * 0.5
    
    # Unique vocabulary ratio
    unique_ratio = len(set(word.lower() for word in words)) / len(words)
    complexity += unique_ratio * 10
    
    # Punctuation complexity (fantasy content often has more apostrophes, etc.)
    punctuation_count = sum(1 for char in text if char in '.,;:!?()[]{}\'"-')
    complexity += (punctuation_count / len(words)) * 5
    
    # Cultural complexity indicators
    cultural_complexity = 0
    complex_patterns = ['æ', 'œ', 'ð', 'þ', "'", '-']  # Common in fantasy/cultural names
    for pattern in complex_patterns:
        cultural_complexity += text.count(pattern) * 0.5
    complexity += cultural_complexity
    
    # Fantasy term complexity
    fantasy_terms = extract_fantasy_terms_enhanced(text)
    complexity += len(fantasy_terms) * 0.3
    
    return min(20.0, complexity)


def extract_fantasy_terms_enhanced(text: str) -> List[str]:
    """Enhanced fantasy term extraction with cultural awareness."""
    fantasy_terms_db = {
        # D&D Classes
        'classes': ['barbarian', 'bard', 'cleric', 'druid', 'fighter', 'monk', 'paladin', 
                   'ranger', 'rogue', 'sorcerer', 'warlock', 'wizard', 'artificer', 'bloodhunter'],
        
        # D&D Races
        'races': ['elf', 'dwarf', 'halfling', 'human', 'dragonborn', 'gnome', 'half-elf', 
                 'half-orc', 'tiefling', 'aasimar', 'genasi', 'goliath', 'tabaxi', 'kenku',
                 'lizardfolk', 'triton', 'firbolg', 'goblin', 'hobgoblin', 'bugbear'],
        
        # Fantasy creatures
        'creatures': ['dragon', 'griffin', 'unicorn', 'phoenix', 'basilisk', 'chimera', 
                     'hydra', 'wyvern', 'pegasus', 'manticore', 'sphinx', 'kraken', 'tarrasque',
                     'beholder', 'mindflayer', 'owlbear', 'bulette', 'rust monster'],
        
        # Magic terms
        'magic': ['spell', 'cantrip', 'enchantment', 'divination', 'necromancy', 'illusion',
                 'transmutation', 'evocation', 'abjuration', 'conjuration', 'mana', 'arcane',
                 'ritual', 'component', 'reagent', 'familiar', 'construct', 'elemental'],
        
        # Equipment
        'equipment': ['sword', 'axe', 'bow', 'shield', 'armor', 'helm', 'gauntlets', 
                     'potion', 'scroll', 'wand', 'staff', 'orb', 'tome', 'grimoire',
                     'scimitar', 'rapier', 'crossbow', 'mace', 'flail', 'halberd'],
        
        # Locations
        'locations': ['dungeon', 'castle', 'tavern', 'monastery', 'temple', 'shrine',
                     'forest', 'mountain', 'cave', 'ruins', 'tower', 'keep', 'citadel',
                     'sanctum', 'crypt', 'catacomb', 'underdark', 'feywild', 'shadowfell'],
        
        # Cultural terms
        'cultural': ['clan', 'tribe', 'kingdom', 'empire', 'guild', 'order', 'covenant',
                    'brotherhood', 'sisterhood', 'council', 'court', 'noble', 'peasant',
                    'merchant', 'artisan', 'scholar', 'sage', 'lore', 'legend', 'myth']
    }
    
    found_terms = []
    text_lower = text.lower()
    
    for category, terms in fantasy_terms_db.items():
        for term in terms:
            if term in text_lower:
                found_terms.append(term)
    
    return list(set(found_terms))


def detect_sentiment_enhanced(text: str) -> float:
    """Enhanced sentiment analysis with cultural and character context."""
    if not text:
        return 0.0
    
    # Enhanced word sets for character/fantasy context
    positive_words = {
        'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'brilliant',
        'beautiful', 'lovely', 'nice', 'pleasant', 'happy', 'joy', 'love', 'peace',
        'hope', 'brave', 'heroic', 'noble', 'kind', 'gentle', 'wise', 'strong',
        'confident', 'successful', 'victory', 'triumph', 'glory', 'honor', 'righteous',
        'blessed', 'divine', 'sacred', 'pure', 'loyal', 'faithful', 'just', 'virtuous'
    }
    
    negative_words = {
        'bad', 'terrible', 'awful', 'horrible', 'disgusting', 'hate', 'angry',
        'sad', 'depressed', 'fear', 'scared', 'worried', 'anxious', 'evil',
        'dark', 'sinister', 'cruel', 'wicked', 'vile', 'corrupt', 'cursed',
        'doomed', 'failure', 'defeat', 'death', 'destruction', 'pain', 'suffering',
        'betrayal', 'treachery', 'malice', 'spite', 'vengeance', 'tyranny'
    }
    
    # Neutral/complex words that can be positive or negative depending on context
    complex_words = {
        'power': 0.1, 'magic': 0.1, 'ancient': 0.05, 'mysterious': 0.05,
        'strong': 0.2, 'fierce': 0.1, 'wild': 0.05, 'bold': 0.15
    }
    
    words = re.findall(r'\b\w+\b', text.lower())
    
    if not words:
        return 0.0
    
    positive_count = sum(1 for word in words if word in positive_words)
    negative_count = sum(1 for word in words if word in negative_words)
    complex_score = sum(complex_words.get(word, 0) for word in words)
    
    total_sentiment_words = positive_count + negative_count
    
    if total_sentiment_words == 0:
        return complex_score / len(words)  # Return just complex word influence
    
    # Calculate sentiment score with complex word influence
    sentiment = (positive_count - negative_count) / len(words) + complex_score / len(words)
    
    return max(-1.0, min(1.0, sentiment))


def extract_keywords_enhanced(text: str, max_keywords: int = 10,
                            cultural_context: Optional[str] = None) -> List[Tuple[str, int]]:
    """Enhanced keyword extraction with cultural awareness."""
    if not text:
        return []
    
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    
    # Enhanced stop words (more comprehensive)
    stop_words = {
        'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had',
        'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how',
        'man', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did',
        'its', 'let', 'put', 'say', 'she', 'too', 'use', 'with', 'have', 'this',
        'will', 'your', 'from', 'they', 'know', 'want', 'been', 'good', 'much',
        'some', 'time', 'very', 'when', 'come', 'here', 'just', 'like', 'long',
        'make', 'many', 'over', 'such', 'take', 'than', 'them', 'well', 'were',
        'there', 'would', 'could', 'should', 'might', 'about', 'after', 'before'
    }
    
    filtered_words = [word for word in words if word not in stop_words]
    
    # Boost fantasy/cultural terms
    fantasy_terms = extract_fantasy_terms_enhanced(text)
    cultural_terms = extract_cultural_references_enhanced(text)
    
    word_counts = Counter(filtered_words)
    
    # Boost important terms
    for term in fantasy_terms:
        if term in word_counts:
            word_counts[term] = int(word_counts[term] * 1.5)
    
    for term in cultural_terms:
        if term in word_counts:
            word_counts[term] = int(word_counts[term] * 1.3)
    
    return word_counts.most_common(max_keywords)


def detect_language_enhanced(text: str) -> Optional[str]:
    """Enhanced language detection with better cultural pattern recognition."""
    if not text:
        return None
    
    text_sample = text[:300].lower()  # Use more text for better detection
    
    # Check for non-Latin scripts first
    if any('\u4e00' <= char <= '\u9fff' for char in text_sample):
        return 'zh'
    elif any('\u3040' <= char <= '\u309f' or '\u30a0' <= char <= '\u30ff' for char in text_sample):
        return 'ja'
    elif any('\uac00' <= char <= '\ud7af' for char in text_sample):
        return 'ko'
    elif any('\u0600' <= char <= '\u06ff' for char in text_sample):
        return 'ar'
    elif any('\u0400' <= char <= '\u04ff' for char in text_sample):
        return 'ru'
    
    # Enhanced Latin script detection
    words = text_sample.split()
    
    language_indicators = {
        'en': ['the', 'and', 'that', 'have', 'for', 'not', 'you', 'with', 'his', 'they', 'from', 'she', 'her', 'been', 'than', 'its', 'said'],
        'es': ['que', 'del', 'los', 'las', 'una', 'con', 'por', 'para', 'como', 'más', 'pero', 'sus', 'ser', 'han', 'está'],
        'fr': ['que', 'des', 'les', 'une', 'avec', 'pour', 'dans', 'sur', 'sont', 'plus', 'tout', 'cette', 'ces', 'été', 'peut'],
        'de': ['der', 'die', 'und', 'den', 'das', 'mit', 'für', 'auf', 'ist', 'dem', 'ein', 'eine', 'auch', 'sich', 'aus'],
        'it': ['che', 'del', 'della', 'una', 'con', 'per', 'nel', 'sul', 'sono', 'più', 'come', 'anche', 'alla', 'gli', 'essere'],
        'pt': ['que', 'dos', 'das', 'uma', 'com', 'por', 'para', 'como', 'mais', 'mas', 'seus', 'ser', 'tem', 'está', 'pela']
    }
    
    scores = {}
    for lang, indicators in language_indicators.items():
        score = sum(1 for word in words if word in indicators)
        if len(words) > 0:
            scores[lang] = score / len(words)
        else:
            scores[lang] = 0
    
    if max(scores.values()) > 0.02:  # At least 2% indicator words
        return max(scores, key=scores.get)
    
    return 'en'  # Default to English


def extract_cultural_references_enhanced(text: str) -> List[str]:
    """Enhanced cultural reference extraction with expanded categories."""
    cultural_terms = {
        'norse': ['viking', 'norse', 'asgard', 'valhalla', 'odin', 'thor', 'loki', 'rune', 'berserker', 'ragnarok', 'mjolnir', 'valkyrie', 'einherjar'],
        'greek': ['greek', 'athens', 'sparta', 'olympus', 'zeus', 'apollo', 'athena', 'troy', 'odyssey', 'iliad', 'hades', 'poseidon', 'hermes'],
        'roman': ['roman', 'rome', 'caesar', 'senate', 'legion', 'gladiator', 'colosseum', 'consul', 'emperor', 'centurion', 'tribune'],
        'egyptian': ['egyptian', 'pharaoh', 'pyramid', 'sphinx', 'nile', 'ra', 'isis', 'hieroglyph', 'anubis', 'horus', 'osiris', 'mummy'],
        'celtic': ['celtic', 'druid', 'clan', 'gaelic', 'irish', 'scottish', 'welsh', 'bard', 'tuatha', 'sidhe', 'banshee', 'leprechaun'],
        'asian': ['chinese', 'japanese', 'samurai', 'ninja', 'martial', 'zen', 'dragon', 'emperor', 'shogun', 'daimyo', 'sensei', 'dojo'],
        'arabic': ['arabic', 'desert', 'oasis', 'sultan', 'caliph', 'scimitar', 'djinn', 'bazaar', 'mosque', 'minaret', 'caravan'],
        'medieval': ['medieval', 'knight', 'castle', 'feudal', 'manor', 'crusade', 'chivalry', 'squire', 'tournament', 'courtly'],
        'fantasy': ['elven', 'dwarven', 'orcish', 'dragon', 'magic', 'spell', 'wizard', 'sorcerer', 'enchanted', 'mystical'],
        'slavic': ['slavic', 'russian', 'polish', 'czech', 'boyar', 'cossack', 'tsar', 'baba', 'yaga', 'firebird', 'domovoi'],
        'indian': ['indian', 'hindu', 'buddhist', 'maharaja', 'guru', 'ashram', 'karma', 'dharma', 'sanskrit', 'vedic'],
        'african': ['african', 'tribal', 'shaman', 'ancestor', 'spirit', 'savanna', 'jungle', 'chief', 'elder', 'griot']
    }
    
    found_references = []
    text_lower = text.lower()
    
    for culture, terms in cultural_terms.items():
        culture_score = sum(1 for term in terms if term in text_lower)
        if culture_score > 0:
            found_references.append(culture)
    
    return found_references


# Enhanced analysis helper functions
def _detect_culture_patterns(text: str, cultural_context: Optional[str]) -> List[str]:
    """Detect cultural patterns in text."""
    patterns = []
    
    if not cultural_context:
        return patterns
    
    try:
        culture = get_culture_enhanced(cultural_context)
        if culture and hasattr(culture, 'detect_patterns'):
            return culture.detect_patterns(text)
    except Exception:
        pass
    
    # Basic pattern detection based on cultural context
    if 'norse' in cultural_context.lower():
        if any(pattern in text.lower() for pattern in ['son of', 'daughter of', 'the']):
            patterns.append('patronymic_naming')
        if any(pattern in text.lower() for pattern in ['forge', 'hammer', 'iron', 'stone']):
            patterns.append('craft_terminology')
    
    elif 'celtic' in cultural_context.lower():
        if any(pattern in text.lower() for pattern in ['mac', "o'", 'clan']):
            patterns.append('celtic_naming')
        if any(pattern in text.lower() for pattern in ['druid', 'spirit', 'forest']):
            patterns.append('nature_connection')
    
    return patterns

def _assess_authenticity_indicators(text: str, cultural_context: Optional[str]) -> Dict[str, float]:
    """Assess authenticity indicators for cultural context."""
    indicators = {
        'historical_accuracy': 0.5,
        'cultural_consistency': 0.5,
        'linguistic_authenticity': 0.5,
        'traditional_elements': 0.5
    }
    
    if not cultural_context:
        return indicators
    
    text_lower = text.lower()
    
    # Cultural-specific authenticity patterns
    authenticity_patterns = {
        'norse': {
            'historical': ['viking', 'raid', 'longship', 'thing', 'jarl', 'karl', 'thrall'],
            'linguistic': ['son', 'dottir', 'bjorn', 'ulf', 'thor', 'erik'],
            'traditional': ['rune', 'mead', 'hall', 'forge', 'weapon', 'honor']
        },
        'celtic': {
            'historical': ['clan', 'chieftain', 'bard', 'warrior', 'tribe'],
            'linguistic': ['mac', "o'", 'glen', 'loch', 'ben'],
            'traditional': ['druid', 'stone', 'circle', 'spirit', 'forest', 'sacred']
        },
        'greek': {
            'historical': ['polis', 'citizen', 'philosopher', 'democracy', 'senate'],
            'linguistic': ['os', 'us', 'ius', 'phon', 'graph'],
            'traditional': ['temple', 'oracle', 'festival', 'symposium', 'agora']
        }
    }
    
    # Find matching cultural patterns
    cultural_key = None
    for key in authenticity_patterns.keys():
        if key in cultural_context.lower():
            cultural_key = key
            break
    
    if cultural_key:
        patterns = authenticity_patterns[cultural_key]
        
        # Historical accuracy
        historical_matches = sum(1 for term in patterns['historical'] if term in text_lower)
        indicators['historical_accuracy'] = min(1.0, historical_matches * 0.2 + 0.3)
        
        # Linguistic authenticity
        linguistic_matches = sum(1 for term in patterns['linguistic'] if term in text_lower)
        indicators['linguistic_authenticity'] = min(1.0, linguistic_matches * 0.15 + 0.4)
        
        # Traditional elements
        traditional_matches = sum(1 for term in patterns['traditional'] if term in text_lower)
        indicators['traditional_elements'] = min(1.0, traditional_matches * 0.1 + 0.4)
        
        # Cultural consistency (average of all indicators)
        indicators['cultural_consistency'] = sum(indicators.values()) / len(indicators)
    
    return indicators


def _extract_creativity_markers(text: str) -> List[str]:
    """Extract markers that indicate creative content."""
    creativity_markers = []
    text_lower = text.lower()
    
    # Creative language indicators
    creative_terms = [
        'unique', 'unusual', 'mysterious', 'ancient', 'legendary', 'mythical',
        'magical', 'enchanted', 'cursed', 'blessed', 'sacred', 'forbidden',
        'lost', 'hidden', 'secret', 'forgotten', 'unknown', 'strange',
        'wonderful', 'magnificent', 'extraordinary', 'remarkable'
    ]
    
    for term in creative_terms:
        if term in text_lower:
            creativity_markers.append(f'creative_language:{term}')
    
    # Fantasy elements
    fantasy_elements = [
        'dragon', 'magic', 'spell', 'wizard', 'sorcerer', 'enchantment',
        'artifact', 'relic', 'prophecy', 'quest', 'destiny', 'power'
    ]
    
    for element in fantasy_elements:
        if element in text_lower:
            creativity_markers.append(f'fantasy_element:{element}')
    
    # Narrative structure markers
    if any(phrase in text_lower for phrase in ['once upon', 'long ago', 'in the beginning']):
        creativity_markers.append('narrative_opening')
    
    if any(phrase in text_lower for phrase in ['legend tells', 'it is said', 'stories speak']):
        creativity_markers.append('legendary_framing')
    
    # Creative naming patterns
    if re.search(r"[A-Z][a-z]+('[A-Z][a-z]+|[A-Z][a-z]+)", text):
        creativity_markers.append('creative_naming_apostrophe')
    
    if re.search(r'[A-Z][a-z]+-[A-Z][a-z]+', text):
        creativity_markers.append('creative_naming_hyphen')
    
    return creativity_markers


def _calculate_cultural_consistency(text: str, cultural_context: Optional[str]) -> float:
    """Calculate how culturally consistent the text is."""
    if not cultural_context:
        return 0.5
    
    try:
        # Use validation system for consistency check
        temp_culture_data = {
            'name': f'Consistency Check Culture',
            'description': text,
            'cultural_context': cultural_context
        }
        
        validation_result = validate_culture_for_characters(temp_culture_data)
        return validation_result.creative_quality_score
        
    except Exception:
        # Fallback to simple consistency check
        cultural_references = extract_cultural_references_enhanced(text)
        if cultural_context.lower() in [ref.lower() for ref in cultural_references]:
            return 0.8
        elif cultural_references:
            return 0.6
        else:
            return 0.4


def _assess_character_background_potential(text: str) -> float:
    """Assess how well text supports character background generation."""
    potential_score = 0.0
    text_lower = text.lower()
    
    # Character development indicators
    character_elements = [
        'personality', 'trait', 'behavior', 'motivation', 'goal', 'desire',
        'fear', 'secret', 'past', 'history', 'family', 'childhood',
        'experience', 'skill', 'talent', 'weakness', 'strength'
    ]
    
    character_matches = sum(1 for element in character_elements if element in text_lower)
    potential_score += min(0.4, character_matches * 0.05)
    
    # Story hooks
    hook_elements = [
        'conflict', 'mystery', 'quest', 'revenge', 'justice', 'love',
        'betrayal', 'loyalty', 'honor', 'duty', 'prophecy', 'curse'
    ]
    
    hook_matches = sum(1 for element in hook_elements if element in text_lower)
    potential_score += min(0.3, hook_matches * 0.1)
    
    # Relationship indicators
    relationship_elements = [
        'friend', 'enemy', 'ally', 'rival', 'mentor', 'student',
        'master', 'companion', 'partner', 'lover', 'family'
    ]
    
    relationship_matches = sum(1 for element in relationship_elements if element in text_lower)
    potential_score += min(0.3, relationship_matches * 0.08)
    
    return min(1.0, potential_score)


def _assess_name_generation_quality(text: str) -> float:
    """Assess quality of names in text for character generation."""
    # Extract potential names (capitalized words)
    potential_names = re.findall(r'\b[A-Z][a-z]{2,}\b', text)
    
    if not potential_names:
        return 0.0
    
    quality_score = 0.0
    
    # Diversity of names
    unique_names = set(potential_names)
    diversity_score = min(0.3, len(unique_names) * 0.1)
    quality_score += diversity_score
    
    # Name length appropriateness (4-12 characters ideal)
    appropriate_length_count = sum(1 for name in potential_names if 4 <= len(name) <= 12)
    length_score = min(0.3, (appropriate_length_count / len(potential_names)) * 0.3)
    quality_score += length_score
    
    # Pronunciation friendliness
    pronunciation_friendly = 0
    for name in potential_names:
        if not any(pattern in name.lower() for pattern in ['sch', 'tch', 'pht']):
            pronunciation_friendly += 1
    
    pronunciation_score = min(0.4, (pronunciation_friendly / len(potential_names)) * 0.4)
    quality_score += pronunciation_score
    
    return min(1.0, quality_score)


def _assess_text_gaming_utility(text: str) -> float:
    """Assess how useful text is for gaming table use."""
    utility_score = 0.0
    
    # Length assessment (shorter is better for table use)
    if len(text) <= 200:
        utility_score += 0.3
    elif len(text) <= 500:
        utility_score += 0.2
    elif len(text) <= 1000:
        utility_score += 0.1
    
    # Readability (simpler is better for table use)
    reading_level = calculate_reading_level_enhanced(text)
    if reading_level >= 70:  # Easy to read
        utility_score += 0.3
    elif reading_level >= 50:  # Fairly easy
        utility_score += 0.2
    elif reading_level >= 30:  # Standard
        utility_score += 0.1
    
    # Gaming-specific elements
    gaming_elements = [
        'roll', 'check', 'save', 'advantage', 'disadvantage', 'bonus',
        'penalty', 'difficulty', 'challenge', 'encounter', 'combat'
    ]
    
    gaming_matches = sum(1 for element in gaming_elements if element in text.lower())
    utility_score += min(0.2, gaming_matches * 0.05)
    
    # Quick reference potential
    if any(pattern in text for pattern in ['•', '-', '1.', '2.', '3.']):
        utility_score += 0.2  # Has list structure
    
    return min(1.0, utility_score)


def _assess_roleplay_potential(text: str) -> float:
    """Assess how well text supports roleplay opportunities."""
    roleplay_score = 0.0
    text_lower = text.lower()
    
    # Dialogue indicators
    dialogue_markers = ['"', "'", 'said', 'spoke', 'whispered', 'shouted', 'declared']
    if any(marker in text for marker in dialogue_markers):
        roleplay_score += 0.2
    
    # Personality descriptors
    personality_words = [
        'brave', 'cautious', 'bold', 'shy', 'aggressive', 'peaceful',
        'cunning', 'honest', 'loyal', 'treacherous', 'kind', 'cruel',
        'wise', 'foolish', 'patient', 'impulsive', 'calm', 'angry'
    ]
    
    personality_matches = sum(1 for word in personality_words if word in text_lower)
    roleplay_score += min(0.3, personality_matches * 0.05)
    
    # Emotional content
    emotion_words = [
        'love', 'hate', 'fear', 'joy', 'anger', 'sadness', 'hope',
        'despair', 'pride', 'shame', 'guilt', 'relief', 'excitement'
    ]
    
    emotion_matches = sum(1 for word in emotion_words if word in text_lower)
    roleplay_score += min(0.3, emotion_matches * 0.08)
    
    # Conflict/tension indicators
    conflict_words = [
        'conflict', 'tension', 'struggle', 'challenge', 'obstacle',
        'problem', 'dilemma', 'choice', 'decision', 'consequence'
    ]
    
    conflict_matches = sum(1 for word in conflict_words if word in text_lower)
    roleplay_score += min(0.2, conflict_matches * 0.1)
    
    return min(1.0, roleplay_score)


def _identify_enhancement_categories(text: str, cultural_context: Optional[str]) -> List[CultureEnhancementCategory]:
    """Identify enhancement categories that would benefit the text."""
    categories = []
    text_lower = text.lower()
    
    # Character names assessment
    potential_names = re.findall(r'\b[A-Z][a-z]{2,}\b', text)
    if len(potential_names) < 3:
        categories.append(CultureEnhancementCategory.CHARACTER_NAMES)
    
    # Cultural traits assessment
    cultural_indicators = ['tradition', 'custom', 'belief', 'value', 'practice']
    if not any(indicator in text_lower for indicator in cultural_indicators):
        categories.append(CultureEnhancementCategory.CULTURAL_TRAITS)
    
    # Gaming utility assessment
    if len(text) > 500 or calculate_reading_level_enhanced(text) < 40:
        categories.append(CultureEnhancementCategory.GAMING_UTILITY)
    
    # Pronunciation assessment
    difficult_names = [name for name in potential_names 
                      if any(pattern in name.lower() for pattern in ['sch', 'tch', 'pht'])]
    if difficult_names:
        categories.append(CultureEnhancementCategory.PRONUNCIATION)
    
    # Background hooks assessment
    hook_indicators = ['conflict', 'mystery', 'secret', 'quest', 'revenge']
    if not any(indicator in text_lower for indicator in hook_indicators):
        categories.append(CultureEnhancementCategory.BACKGROUND_HOOKS)
    
    # Narrative depth assessment
    narrative_indicators = ['story', 'legend', 'history', 'tale', 'myth']
    if not any(indicator in text_lower for indicator in narrative_indicators):
        categories.append(CultureEnhancementCategory.NARRATIVE_DEPTH)
    
    return categories


def _generate_improvement_suggestions(text: str, 
                                    enhancement_categories: List[CultureEnhancementCategory]) -> List[str]:
    """Generate specific improvement suggestions based on enhancement categories."""
    suggestions = []
    
    for category in enhancement_categories:
        if category == CultureEnhancementCategory.CHARACTER_NAMES:
            suggestions.append("Add more diverse character names for better name generation")
            
        elif category == CultureEnhancementCategory.CULTURAL_TRAITS:
            suggestions.append("Include more cultural traditions, values, or customs")
            
        elif category == CultureEnhancementCategory.GAMING_UTILITY:
            suggestions.append("Simplify language and shorten content for table use")
            
        elif category == CultureEnhancementCategory.PRONUNCIATION:
            suggestions.append("Add pronunciation guides for complex names")
            
        elif category == CultureEnhancementCategory.BACKGROUND_HOOKS:
            suggestions.append("Add character conflicts, mysteries, or personal quests")
            
        elif category == CultureEnhancementCategory.NARRATIVE_DEPTH:
            suggestions.append("Include more cultural stories, legends, or historical context")
            
        elif category == CultureEnhancementCategory.ROLEPLAY_ELEMENTS:
            suggestions.append("Add personality traits, relationships, or emotional elements")
            
        elif category == CultureEnhancementCategory.CHARACTER_MOTIVATIONS:
            suggestions.append("Include character goals, fears, or driving motivations")
    
    return suggestions


def _assess_preset_compatibility(text: str, target_preset: Optional[str]) -> Dict[str, float]:
    """Assess compatibility with different CHARACTER_CULTURE_PRESETS."""
    compatibility = {}
    
    if not target_preset:
        # Assess against all available presets
        preset_names = list(CHARACTER_CULTURE_PRESETS.keys()) if CHARACTER_CULTURE_PRESETS else [
            'gaming_optimized', 'creative_focused', 'character_rich', 'narrative_deep', 'table_friendly'
        ]
    else:
        preset_names = [target_preset]
    
    for preset_name in preset_names:
        score = 0.5  # Base compatibility
        
        if 'gaming' in preset_name or 'table' in preset_name:
            # Gaming presets prefer shorter, simpler content
            if len(text) <= 300:
                score += 0.2
            if calculate_reading_level_enhanced(text) >= 60:
                score += 0.2
            if _assess_text_gaming_utility(text) >= 0.7:
                score += 0.1
                
        elif 'creative' in preset_name:
            # Creative presets prefer more imaginative content
            creativity_markers = _extract_creativity_markers(text)
            score += min(0.3, len(creativity_markers) * 0.05)
            
        elif 'character' in preset_name:
            # Character presets prefer content that supports character development
            score += _assess_character_background_potential(text) * 0.4
            
        elif 'narrative' in preset_name:
            # Narrative presets prefer story-rich content
            if _assess_roleplay_potential(text) >= 0.6:
                score += 0.3
            narrative_words = ['story', 'legend', 'history', 'tale', 'myth']
            if any(word in text.lower() for word in narrative_words):
                score += 0.2
        
        compatibility[preset_name] = min(1.0, score)
    
    return compatibility

def _assess_authenticity_indicators(text: str, cultural_context: Optional[str]) -> Dict[str, float]:
    """Assess authenticity indicators for cultural context."""
    indicators = {
        'historical_accuracy': 0.5,
        'cultural_consistency': 0.5,
        'linguistic_authenticity': 0.5,
        'traditional_elements': 0.5
    }
    
    if not cultural_context:
        return indicators
    
    text_lower = text.lower()
    
    # Cultural-specific authenticity patterns
    authenticity_patterns = {
        'norse': {
            'historical': ['viking', 'raid', 'longship', 'thing', 'jarl', 'karl', 'thrall'],
            'linguistic': ['son', 'dottir', 'bjorn', 'ulf', 'thor', 'erik'],
            'traditional': ['rune', 'mead', 'hall', 'forge', 'weapon', 'honor']
        },
        'celtic': {
            'historical': ['clan', 'chieftain', 'bard', 'warrior', 'tribe'],
            'linguistic': ['mac', "o'", 'glen', 'loch', 'ben'],
            'traditional': ['druid', 'stone', 'circle', 'spirit', 'forest', 'sacred']
        },
        'greek': {
            'historical': ['polis', 'citizen', 'philosopher', 'democracy', 'senate'],
            'linguistic': ['os', 'us', 'ius', 'phon', 'graph'],
            'traditional': ['temple', 'oracle', 'festival', 'symposium', 'agora']
        }
    }
    
    # Find matching cultural patterns
    cultural_key = None
    for key in authenticity_patterns.keys():
        if key in cultural_context.lower():
            cultural_key = key
            break
    
    if cultural_key:
        patterns = authenticity_patterns[cultural_key]
        
        # Historical accuracy
        historical_matches = sum(1 for term in patterns['historical'] if term in text_lower)
        indicators['historical_accuracy'] = min(1.0, historical_matches * 0.2 + 0.3)
        
        # Linguistic authenticity
        linguistic_matches = sum(1 for term in patterns['linguistic'] if term in text_lower)
        indicators['linguistic_authenticity'] = min(1.0, linguistic_matches * 0.15 + 0.4)
        
        # Traditional elements
        traditional_matches = sum(1 for term in patterns['traditional'] if term in text_lower)
        indicators['traditional_elements'] = min(1.0, traditional_matches * 0.1 + 0.4)
        
        # Cultural consistency (average of all indicators)
        indicators['cultural_consistency'] = sum(indicators.values()) / len(indicators)
    
    return indicators


def _extract_creativity_markers(text: str) -> List[str]:
    """Extract markers that indicate creative content."""
    creativity_markers = []
    text_lower = text.lower()
    
    # Creative language indicators
    creative_terms = [
        'unique', 'unusual', 'mysterious', 'ancient', 'legendary', 'mythical',
        'magical', 'enchanted', 'cursed', 'blessed', 'sacred', 'forbidden',
        'lost', 'hidden', 'secret', 'forgotten', 'unknown', 'strange',
        'wonderful', 'magnificent', 'extraordinary', 'remarkable'
    ]
    
    for term in creative_terms:
        if term in text_lower:
            creativity_markers.append(f'creative_language:{term}')
    
    # Fantasy elements
    fantasy_elements = [
        'dragon', 'magic', 'spell', 'wizard', 'sorcerer', 'enchantment',
        'artifact', 'relic', 'prophecy', 'quest', 'destiny', 'power'
    ]
    
    for element in fantasy_elements:
        if element in text_lower:
            creativity_markers.append(f'fantasy_element:{element}')
    
    # Narrative structure markers
    if any(phrase in text_lower for phrase in ['once upon', 'long ago', 'in the beginning']):
        creativity_markers.append('narrative_opening')
    
    if any(phrase in text_lower for phrase in ['legend tells', 'it is said', 'stories speak']):
        creativity_markers.append('legendary_framing')
    
    # Creative naming patterns
    if re.search(r"[A-Z][a-z]+('[A-Z][a-z]+|[A-Z][a-z]+)", text):
        creativity_markers.append('creative_naming_apostrophe')
    
    if re.search(r'[A-Z][a-z]+-[A-Z][a-z]+', text):
        creativity_markers.append('creative_naming_hyphen')
    
    return creativity_markers


def _calculate_cultural_consistency(text: str, cultural_context: Optional[str]) -> float:
    """Calculate how culturally consistent the text is."""
    if not cultural_context:
        return 0.5
    
    try:
        # Use validation system for consistency check
        temp_culture_data = {
            'name': f'Consistency Check Culture',
            'description': text,
            'cultural_context': cultural_context
        }
        
        validation_result = validate_culture_for_characters(temp_culture_data)
        return validation_result.creative_quality_score
        
    except Exception:
        # Fallback to simple consistency check
        cultural_references = extract_cultural_references_enhanced(text)
        if cultural_context.lower() in [ref.lower() for ref in cultural_references]:
            return 0.8
        elif cultural_references:
            return 0.6
        else:
            return 0.4


def _assess_character_background_potential(text: str) -> float:
    """Assess how well text supports character background generation."""
    potential_score = 0.0
    text_lower = text.lower()
    
    # Character development indicators
    character_elements = [
        'personality', 'trait', 'behavior', 'motivation', 'goal', 'desire',
        'fear', 'secret', 'past', 'history', 'family', 'childhood',
        'experience', 'skill', 'talent', 'weakness', 'strength'
    ]
    
    character_matches = sum(1 for element in character_elements if element in text_lower)
    potential_score += min(0.4, character_matches * 0.05)
    
    # Story hooks
    hook_elements = [
        'conflict', 'mystery', 'quest', 'revenge', 'justice', 'love',
        'betrayal', 'loyalty', 'honor', 'duty', 'prophecy', 'curse'
    ]
    
    hook_matches = sum(1 for element in hook_elements if element in text_lower)
    potential_score += min(0.3, hook_matches * 0.1)
    
    # Relationship indicators
    relationship_elements = [
        'friend', 'enemy', 'ally', 'rival', 'mentor', 'student',
        'master', 'companion', 'partner', 'lover', 'family'
    ]
    
    relationship_matches = sum(1 for element in relationship_elements if element in text_lower)
    potential_score += min(0.3, relationship_matches * 0.08)
    
    return min(1.0, potential_score)


def _assess_name_generation_quality(text: str) -> float:
    """Assess quality of names in text for character generation."""
    # Extract potential names (capitalized words)
    potential_names = re.findall(r'\b[A-Z][a-z]{2,}\b', text)
    
    if not potential_names:
        return 0.0
    
    quality_score = 0.0
    
    # Diversity of names
    unique_names = set(potential_names)
    diversity_score = min(0.3, len(unique_names) * 0.1)
    quality_score += diversity_score
    
    # Name length appropriateness (4-12 characters ideal)
    appropriate_length_count = sum(1 for name in potential_names if 4 <= len(name) <= 12)
    length_score = min(0.3, (appropriate_length_count / len(potential_names)) * 0.3)
    quality_score += length_score
    
    # Pronunciation friendliness
    pronunciation_friendly = 0
    for name in potential_names:
        if not any(pattern in name.lower() for pattern in ['sch', 'tch', 'pht']):
            pronunciation_friendly += 1
    
    pronunciation_score = min(0.4, (pronunciation_friendly / len(potential_names)) * 0.4)
    quality_score += pronunciation_score
    
    return min(1.0, quality_score)


def _assess_text_gaming_utility(text: str) -> float:
    """Assess how useful text is for gaming table use."""
    utility_score = 0.0
    
    # Length assessment (shorter is better for table use)
    if len(text) <= 200:
        utility_score += 0.3
    elif len(text) <= 500:
        utility_score += 0.2
    elif len(text) <= 1000:
        utility_score += 0.1
    
    # Readability (simpler is better for table use)
    reading_level = calculate_reading_level_enhanced(text)
    if reading_level >= 70:  # Easy to read
        utility_score += 0.3
    elif reading_level >= 50:  # Fairly easy
        utility_score += 0.2
    elif reading_level >= 30:  # Standard
        utility_score += 0.1
    
    # Gaming-specific elements
    gaming_elements = [
        'roll', 'check', 'save', 'advantage', 'disadvantage', 'bonus',
        'penalty', 'difficulty', 'challenge', 'encounter', 'combat'
    ]
    
    gaming_matches = sum(1 for element in gaming_elements if element in text.lower())
    utility_score += min(0.2, gaming_matches * 0.05)
    
    # Quick reference potential
    if any(pattern in text for pattern in ['•', '-', '1.', '2.', '3.']):
        utility_score += 0.2  # Has list structure
    
    return min(1.0, utility_score)


def _assess_roleplay_potential(text: str) -> float:
    """Assess how well text supports roleplay opportunities."""
    roleplay_score = 0.0
    text_lower = text.lower()
    
    # Dialogue indicators
    dialogue_markers = ['"', "'", 'said', 'spoke', 'whispered', 'shouted', 'declared']
    if any(marker in text for marker in dialogue_markers):
        roleplay_score += 0.2
    
    # Personality descriptors
    personality_words = [
        'brave', 'cautious', 'bold', 'shy', 'aggressive', 'peaceful',
        'cunning', 'honest', 'loyal', 'treacherous', 'kind', 'cruel',
        'wise', 'foolish', 'patient', 'impulsive', 'calm', 'angry'
    ]
    
    personality_matches = sum(1 for word in personality_words if word in text_lower)
    roleplay_score += min(0.3, personality_matches * 0.05)
    
    # Emotional content
    emotion_words = [
        'love', 'hate', 'fear', 'joy', 'anger', 'sadness', 'hope',
        'despair', 'pride', 'shame', 'guilt', 'relief', 'excitement'
    ]
    
    emotion_matches = sum(1 for word in emotion_words if word in text_lower)
    roleplay_score += min(0.3, emotion_matches * 0.08)
    
    # Conflict/tension indicators
    conflict_words = [
        'conflict', 'tension', 'struggle', 'challenge', 'obstacle',
        'problem', 'dilemma', 'choice', 'decision', 'consequence'
    ]
    
    conflict_matches = sum(1 for word in conflict_words if word in text_lower)
    roleplay_score += min(0.2, conflict_matches * 0.1)
    
    return min(1.0, roleplay_score)


def _identify_enhancement_categories(text: str, cultural_context: Optional[str]) -> List[CultureEnhancementCategory]:
    """Identify enhancement categories that would benefit the text."""
    categories = []
    text_lower = text.lower()
    
    # Character names assessment
    potential_names = re.findall(r'\b[A-Z][a-z]{2,}\b', text)
    if len(potential_names) < 3:
        categories.append(CultureEnhancementCategory.CHARACTER_NAMES)
    
    # Cultural traits assessment
    cultural_indicators = ['tradition', 'custom', 'belief', 'value', 'practice']
    if not any(indicator in text_lower for indicator in cultural_indicators):
        categories.append(CultureEnhancementCategory.CULTURAL_TRAITS)
    
    # Gaming utility assessment
    if len(text) > 500 or calculate_reading_level_enhanced(text) < 40:
        categories.append(CultureEnhancementCategory.GAMING_UTILITY)
    
    # Pronunciation assessment
    difficult_names = [name for name in potential_names 
                      if any(pattern in name.lower() for pattern in ['sch', 'tch', 'pht'])]
    if difficult_names:
        categories.append(CultureEnhancementCategory.PRONUNCIATION)
    
    # Background hooks assessment
    hook_indicators = ['conflict', 'mystery', 'secret', 'quest', 'revenge']
    if not any(indicator in text_lower for indicator in hook_indicators):
        categories.append(CultureEnhancementCategory.BACKGROUND_HOOKS)
    
    # Narrative depth assessment
    narrative_indicators = ['story', 'legend', 'history', 'tale', 'myth']
    if not any(indicator in text_lower for indicator in narrative_indicators):
        categories.append(CultureEnhancementCategory.NARRATIVE_DEPTH)
    
    return categories


def _generate_improvement_suggestions(text: str, 
                                    enhancement_categories: List[CultureEnhancementCategory]) -> List[str]:
    """Generate specific improvement suggestions based on enhancement categories."""
    suggestions = []
    
    for category in enhancement_categories:
        if category == CultureEnhancementCategory.CHARACTER_NAMES:
            suggestions.append("Add more diverse character names for better name generation")
            
        elif category == CultureEnhancementCategory.CULTURAL_TRAITS:
            suggestions.append("Include more cultural traditions, values, or customs")
            
        elif category == CultureEnhancementCategory.GAMING_UTILITY:
            suggestions.append("Simplify language and shorten content for table use")
            
        elif category == CultureEnhancementCategory.PRONUNCIATION:
            suggestions.append("Add pronunciation guides for complex names")
            
        elif category == CultureEnhancementCategory.BACKGROUND_HOOKS:
            suggestions.append("Add character conflicts, mysteries, or personal quests")
            
        elif category == CultureEnhancementCategory.NARRATIVE_DEPTH:
            suggestions.append("Include more cultural stories, legends, or historical context")
            
        elif category == CultureEnhancementCategory.ROLEPLAY_ELEMENTS:
            suggestions.append("Add personality traits, relationships, or emotional elements")
            
        elif category == CultureEnhancementCategory.CHARACTER_MOTIVATIONS:
            suggestions.append("Include character goals, fears, or driving motivations")
    
    return suggestions


def _assess_preset_compatibility(text: str, target_preset: Optional[str]) -> Dict[str, float]:
    """Assess compatibility with different CHARACTER_CULTURE_PRESETS."""
    compatibility = {}
    
    if not target_preset:
        # Assess against all available presets
        preset_names = list(CHARACTER_CULTURE_PRESETS.keys()) if CHARACTER_CULTURE_PRESETS else [
            'gaming_optimized', 'creative_focused', 'character_rich', 'narrative_deep', 'table_friendly'
        ]
    else:
        preset_names = [target_preset]
    
    for preset_name in preset_names:
        score = 0.5  # Base compatibility
        
        if 'gaming' in preset_name or 'table' in preset_name:
            # Gaming presets prefer shorter, simpler content
            if len(text) <= 300:
                score += 0.2
            if calculate_reading_level_enhanced(text) >= 60:
                score += 0.2
            if _assess_text_gaming_utility(text) >= 0.7:
                score += 0.1
                
        elif 'creative' in preset_name:
            # Creative presets prefer more imaginative content
            creativity_markers = _extract_creativity_markers(text)
            score += min(0.3, len(creativity_markers) * 0.05)
            
        elif 'character' in preset_name:
            # Character presets prefer content that supports character development
            score += _assess_character_background_potential(text) * 0.4
            
        elif 'narrative' in preset_name:
            # Narrative presets prefer story-rich content
            if _assess_roleplay_potential(text) >= 0.6:
                score += 0.3
            narrative_words = ['story', 'legend', 'history', 'tale', 'myth']
            if any(word in text.lower() for word in narrative_words):
                score += 0.2
        
        compatibility[preset_name] = min(1.0, score)
    
    return compatibility


# ============================================================================
# MODULE EXPORTS AND VALIDATION
# ============================================================================

__all__ = [
    # Enhanced type definitions
    "EnhancedTextStyle",
    "EnhancedContentType", 
    "EnhancedNameComponents",
    "EnhancedTextAnalysis",
    "EnhancedValidationResult",
    
    # Enhanced core functions
    "format_text_enhanced",
    "sanitize_text_input_enhanced",
    "validate_character_sheet_text_enhanced",
    "analyze_text_content_enhanced",
    
    # Enhanced analysis functions
    "calculate_reading_level_enhanced",
    "count_syllables_enhanced",
    "calculate_text_complexity_enhanced",
    "extract_fantasy_terms_enhanced",
    "detect_sentiment_enhanced",
    "extract_keywords_enhanced",
    "detect_language_enhanced",
    "extract_cultural_references_enhanced"
]

# ============================================================================
# MODULE METADATA
# ============================================================================

__version__ = "3.0.0"
__author__ = "D&D Character Creator Team"
__description__ = "Enhanced Text Processing Utilities with Cultural Awareness and Character Generation Focus"

# Clean Architecture compliance
CLEAN_ARCHITECTURE_COMPLIANCE = {
    "layer": "core/utils",
    "pure_functions": True,
    "stateless": True,
    "infrastructure_independent": True
}
