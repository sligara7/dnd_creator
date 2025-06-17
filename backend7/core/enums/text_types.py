"""
Essential Text Type Enums

Streamlined text type classifications following backend7 architecture.
Based on crude_functional.py patterns and essential-only philosophy.
"""

from enum import Enum, auto

# ============ CHARACTER TEXT CONTENT TYPES ============

class TextContentType(Enum):
    """Character text content classifications."""
    NAME = auto()              # Character name
    DESCRIPTION = auto()       # Physical description
    BACKSTORY = auto()         # Character history
    PERSONALITY = auto()       # Personality traits
    NOTES = auto()             # Player notes
    BIOGRAPHY = auto()         # Full character biography

class DescriptiveText(Enum):
    """Descriptive text categories."""
    APPEARANCE = auto()        # Physical appearance
    MANNERISMS = auto()        # Behavioral quirks
    SPEECH = auto()            # Speaking patterns
    CLOTHING = auto()          # Attire description
    EQUIPMENT = auto()         # Gear descriptions

class NarrativeText(Enum):
    """Narrative text types."""
    ORIGIN = auto()            # Character origins
    MOTIVATION = auto()        # Character goals
    RELATIONSHIPS = auto()     # Social connections
    SECRETS = auto()           # Hidden information
    ASPIRATIONS = auto()       # Future goals

# ============ FORMATTING TYPES ============

class TextFormat(Enum):
    """Text formatting options."""
    PLAIN = auto()             # No formatting
    MARKDOWN = auto()          # Markdown syntax
    HTML = auto()              # HTML markup
    RICH_TEXT = auto()         # Rich text format

class TextLength(Enum):
    """Text length classifications."""
    SHORT = auto()             # 1-50 characters
    MEDIUM = auto()            # 51-200 characters
    LONG = auto()              # 201-500 characters
    EXTENDED = auto()          # 500+ characters

class TextStyle(Enum):
    """Text style preferences."""
    FORMAL = auto()            # Formal writing
    CASUAL = auto()            # Informal writing
    DESCRIPTIVE = auto()       # Rich descriptions
    CONCISE = auto()           # Brief and direct
    NARRATIVE = auto()         # Story-like
    TECHNICAL = auto()         # Game mechanics focused

# ============ LANGUAGE AND TONE ============

class LanguageStyle(Enum):
    """Language style options."""
    MODERN = auto()            # Contemporary language
    ARCHAIC = auto()           # Old-fashioned speech
    FANTASY = auto()           # Fantasy-appropriate
    COLLOQUIAL = auto()        # Everyday speech
    ELOQUENT = auto()          # Sophisticated language

class ToneType(Enum):
    """Text tone classifications."""
    SERIOUS = auto()           # Serious tone
    HUMOROUS = auto()          # Light-hearted
    DRAMATIC = auto()          # Dramatic flair
    MYSTERIOUS = auto()        # Enigmatic
    HEROIC = auto()            # Noble and brave
    DARK = auto()              # Dark or gritty

# ============ CONTENT GENERATION ============

class GenerationStyle(Enum):
    """Text generation style preferences."""
    RANDOM = auto()            # Random generation
    TEMPLATE = auto()          # Template-based
    GUIDED = auto()            # User-guided creation
    ADAPTIVE = auto()          # Context-adaptive

class ContentDepth(Enum):
    """Content detail depth levels."""
    MINIMAL = auto()           # Basic information
    STANDARD = auto()          # Moderate detail
    DETAILED = auto()          # Rich content
    COMPREHENSIVE = auto()     # Complete coverage

# ============ TEXT VALIDATION ============

class ValidationLevel(Enum):
    """Text content validation levels."""
    NONE = auto()              # No validation
    BASIC = auto()             # Basic checks
    MODERATE = auto()          # Content appropriateness
    STRICT = auto()            # Comprehensive validation

# ============ UTILITY FUNCTIONS ============

def get_max_length(text_length: TextLength) -> int:
    """Get maximum character count for text length type."""
    length_limits = {
        TextLength.SHORT: 50,
        TextLength.MEDIUM: 200,
        TextLength.LONG: 500,
        TextLength.EXTENDED: 2000
    }
    return length_limits.get(text_length, 200)

def is_formatted_text(format_type: TextFormat) -> bool:
    """Check if text format includes markup."""
    return format_type in [TextFormat.MARKDOWN, TextFormat.HTML, TextFormat.RICH_TEXT]

def requires_processing(style: GenerationStyle) -> bool:
    """Check if generation style requires additional processing."""
    return style in [GenerationStyle.TEMPLATE, GenerationStyle.GUIDED, GenerationStyle.ADAPTIVE]

def is_creative_content(content_type: TextContentType) -> bool:
    """Check if content type involves creative writing."""
    return content_type in [
        TextContentType.DESCRIPTION,
        TextContentType.BACKSTORY,
        TextContentType.PERSONALITY,
        TextContentType.BIOGRAPHY
    ]

def get_appropriate_length(content_type: TextContentType) -> TextLength:
    """Get recommended text length for content type."""
    length_recommendations = {
        TextContentType.NAME: TextLength.SHORT,
        TextContentType.DESCRIPTION: TextLength.MEDIUM,
        TextContentType.BACKSTORY: TextLength.LONG,
        TextContentType.PERSONALITY: TextLength.MEDIUM,
        TextContentType.NOTES: TextLength.EXTENDED,
        TextContentType.BIOGRAPHY: TextLength.EXTENDED
    }
    return length_recommendations.get(content_type, TextLength.MEDIUM)

def supports_rich_formatting(format_type: TextFormat) -> bool:
    """Check if format supports rich text features."""
    return format_type in [TextFormat.HTML, TextFormat.RICH_TEXT]

# ============ TEXT TYPE MAPPINGS ============

CONTENT_CATEGORIES = {
    "character_basics": [
        TextContentType.NAME,
        TextContentType.DESCRIPTION
    ],
    "character_depth": [
        TextContentType.BACKSTORY,
        TextContentType.PERSONALITY,
        TextContentType.BIOGRAPHY
    ],
    "game_content": [
        TextContentType.NOTES
    ]
}

STYLE_COMPATIBILITY = {
    ToneType.SERIOUS: [LanguageStyle.FORMAL, LanguageStyle.ELOQUENT],
    ToneType.HUMOROUS: [LanguageStyle.COLLOQUIAL, LanguageStyle.MODERN],
    ToneType.DRAMATIC: [LanguageStyle.ELOQUENT, LanguageStyle.ARCHAIC],
    ToneType.HEROIC: [LanguageStyle.ELOQUENT, LanguageStyle.FANTASY]
}

# ============ ESSENTIAL EXPORTS ============

__all__ = [
    # Content types
    'TextContentType',
    'DescriptiveText',
    'NarrativeText',
    
    # Formatting
    'TextFormat',
    'TextLength',
    'TextStyle',
    
    # Language and tone
    'LanguageStyle',
    'ToneType',
    
    # Generation
    'GenerationStyle',
    'ContentDepth',
    'ValidationLevel',
    
    # Mappings
    'CONTENT_CATEGORIES',
    'STYLE_COMPATIBILITY',
    
    # Utility functions
    'get_max_length',
    'is_formatted_text',
    'requires_processing',
    'is_creative_content',
    'get_appropriate_length',
    'supports_rich_formatting',
]

# ============ MODULE METADATA ============

__version__ = '1.0.0'
__description__ = 'Essential text type enumerations'
__author__ = 'D&D Character Creator Backend7'

# Backend7 architecture compliance
BACKEND7_COMPLIANCE = {
    "layer": "core/enums",
    "focus": "text_classification_only",
    "line_target": 150,
    "dependencies": [],
    "philosophy": "crude_functional_inspired_essential_enums"
}