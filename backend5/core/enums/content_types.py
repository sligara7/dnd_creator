"""
Content Type Enumerations

Enums related to content generation, validation, and processing for D&D 5e content.
These enums represent the core business concepts for content creation and management.
"""

from enum import Enum, auto
from typing import List, Set


class ContentType(Enum):
    """
    Primary types of D&D content that can be generated.
    
    These represent the main content categories supported by the generator.
    """
    SPECIES = "species"
    CHARACTER_CLASS = "character_class"
    SUBCLASS = "subclass"
    BACKGROUND = "background"
    FEAT = "feat"
    SPELL = "spell"
    EQUIPMENT = "equipment"
    MAGIC_ITEM = "magic_item"
    MONSTER = "monster"
    ADVENTURE_HOOK = "adventure_hook"
    
    @property
    def is_character_option(self) -> bool:
        """Check if this content type is a character option."""
        return self in {
            self.SPECIES, self.CHARACTER_CLASS, self.SUBCLASS, 
            self.BACKGROUND, self.FEAT
        }
    
    @property
    def is_item(self) -> bool:
        """Check if this content type is an item."""
        return self in {self.EQUIPMENT, self.MAGIC_ITEM}
    
    @property
    def requires_mechanics(self) -> bool:
        """Check if this content type requires mechanical rules."""
        return self in {
            self.SPECIES, self.CHARACTER_CLASS, self.SUBCLASS,
            self.FEAT, self.SPELL, self.EQUIPMENT, self.MAGIC_ITEM, self.MONSTER
        }


class GenerationMethod(Enum):
    """
    Methods for generating content.
    
    Defines the different approaches used to create new D&D content.
    """
    CONCEPT_DRIVEN = "concept_driven"     # Start with thematic concept
    TEMPLATE_BASED = "template_based"     # Use existing templates
    RULE_BASED = "rule_based"            # Follow mechanical rules strictly
    AI_ASSISTED = "ai_assisted"          # Use AI for creative generation
    HYBRID = "hybrid"                    # Combine multiple methods
    PROCEDURAL = "procedural"            # Algorithm-based generation
    
    @property
    def uses_ai(self) -> bool:
        """Check if this method uses AI assistance."""
        return self in {self.AI_ASSISTED, self.HYBRID}
    
    @property
    def is_deterministic(self) -> bool:
        """Check if this method produces deterministic results."""
        return self in {self.TEMPLATE_BASED, self.RULE_BASED, self.PROCEDURAL}


class ValidationSeverity(Enum):
    """
    Severity levels for validation issues.
    
    Used to categorize validation problems by their impact.
    """
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    
    def __lt__(self, other):
        """Enable comparison of severity levels."""
        severity_order = [self.INFO, self.WARNING, self.ERROR, self.CRITICAL]
        return severity_order.index(self) < severity_order.index(other)
    
    @property
    def blocks_generation(self) -> bool:
        """Check if this severity level should block content generation."""
        return self in {self.ERROR, self.CRITICAL}


class BalanceLevel(Enum):
    """
    Balance levels for content evaluation.
    
    Represents how balanced content is compared to official D&D standards.
    """
    SEVERELY_UNDERPOWERED = "severely_underpowered"
    UNDERPOWERED = "underpowered"
    SLIGHTLY_UNDERPOWERED = "slightly_underpowered"
    BALANCED = "balanced"
    SLIGHTLY_OVERPOWERED = "slightly_overpowered"
    OVERPOWERED = "overpowered"
    SEVERELY_OVERPOWERED = "severely_overpowered"
    BROKEN = "broken"
    
    @property
    def is_acceptable(self) -> bool:
        """Check if this balance level is acceptable for play."""
        return self in {
            self.SLIGHTLY_UNDERPOWERED, self.BALANCED, self.SLIGHTLY_OVERPOWERED
        }
    
    @property
    def power_rating(self) -> float:
        """Get numerical power rating (0.0 to 2.0, 1.0 = balanced)."""
        ratings = {
            self.SEVERELY_UNDERPOWERED: 0.1,
            self.UNDERPOWERED: 0.4,
            self.SLIGHTLY_UNDERPOWERED: 0.8,
            self.BALANCED: 1.0,
            self.SLIGHTLY_OVERPOWERED: 1.2,
            self.OVERPOWERED: 1.6,
            self.SEVERELY_OVERPOWERED: 1.9,
            self.BROKEN: 2.0
        }
        return ratings[self]


class ContentRarity(Enum):
    """
    Rarity levels for generated content following D&D 5e standards.
    
    Matches official D&D rarity categories for consistency.
    """
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    VERY_RARE = "very_rare"
    LEGENDARY = "legendary"
    ARTIFACT = "artifact"
    
    @property
    def availability_level(self) -> int:
        """Get availability level (1-6, higher = rarer)."""
        levels = {
            self.COMMON: 1,
            self.UNCOMMON: 2,
            self.RARE: 3,
            self.VERY_RARE: 4,
            self.LEGENDARY: 5,
            self.ARTIFACT: 6
        }
        return levels[self]
    
    @property
    def requires_dm_approval(self) -> bool:
        """Check if this rarity typically requires DM approval."""
        return self in {self.LEGENDARY, self.ARTIFACT}


class ContentSource(Enum):
    """
    Source of content creation.
    
    Tracks the origin and method of content creation for attribution and filtering.
    """
    CORE_RULES = "core_rules"           # Official D&D content
    GENERATED = "generated"             # AI-generated content
    CUSTOM = "custom"                   # User-created content
    HYBRID = "hybrid"                   # Mix of generated and custom
    COMMUNITY = "community"             # Community-contributed content
    IMPORTED = "imported"               # Imported from external sources
    
    @property
    def is_official(self) -> bool:
        """Check if this is official D&D content."""
        return self == self.CORE_RULES
    
    @property
    def requires_review(self) -> bool:
        """Check if content from this source requires review."""
        return self in {self.GENERATED, self.COMMUNITY, self.IMPORTED}


class QualityLevel(Enum):
    """
    Quality assessment levels for generated content.
    
    Represents the overall quality and completeness of generated content.
    """
    DRAFT = "draft"                     # Initial generation, needs work
    ROUGH = "rough"                     # Basic structure, needs refinement
    GOOD = "good"                       # Well-formed, minor issues
    EXCELLENT = "excellent"             # High quality, ready for use
    PROFESSIONAL = "professional"       # Publication-ready quality
    
    def __lt__(self, other):
        """Enable comparison of quality levels."""
        quality_order = [self.DRAFT, self.ROUGH, self.GOOD, self.EXCELLENT, self.PROFESSIONAL]
        return quality_order.index(self) < quality_order.index(other)
    
    @property
    def is_usable(self) -> bool:
        """Check if content at this quality level is usable in games."""
        return self in {self.GOOD, self.EXCELLENT, self.PROFESSIONAL}
    
    @property
    def quality_score(self) -> float:
        """Get numerical quality score (0.0 to 1.0)."""
        scores = {
            self.DRAFT: 0.2,
            self.ROUGH: 0.4,
            self.GOOD: 0.6,
            self.EXCELLENT: 0.8,
            self.PROFESSIONAL: 1.0
        }
        return scores[self]


class ComplexityLevel(Enum):
    """
    Complexity levels for content generation and usage.
    
    Indicates how complex content is to generate, understand, and use.
    """
    SIMPLE = "simple"                   # Easy to understand and use
    MODERATE = "moderate"               # Some complexity, manageable
    COMPLEX = "complex"                 # Requires careful consideration
    ADVANCED = "advanced"               # Complex interactions and rules
    EXPERT = "expert"                   # Requires deep system knowledge
    
    @property
    def generation_difficulty(self) -> float:
        """Get generation difficulty multiplier."""
        difficulties = {
            self.SIMPLE: 1.0,
            self.MODERATE: 1.5,
            self.COMPLEX: 2.0,
            self.ADVANCED: 2.5,
            self.EXPERT: 3.0
        }
        return difficulties[self]
    
    @property
    def requires_expertise(self) -> bool:
        """Check if this complexity requires system expertise."""
        return self in {self.ADVANCED, self.EXPERT}


class ThemeCategory(Enum):
    """
    Thematic categories for content organization.
    
    Broad thematic groupings that help organize and categorize content.
    """
    # Core fantasy themes
    ARCANE = "arcane"                   # Magic and wizardry
    DIVINE = "divine"                   # Gods and religion
    NATURE = "nature"                   # Natural world and primal forces
    MARTIAL = "martial"                 # Combat and warfare
    
    # Specific themes
    ELEMENTAL = "elemental"             # Elemental forces
    SHADOW = "shadow"                   # Darkness and stealth
    CELESTIAL = "celestial"             # Heavenly and angelic
    INFERNAL = "infernal"               # Hellish and demonic
    UNDEAD = "undead"                   # Death and undeath
    ABERRANT = "aberrant"               # Alien and otherworldly
    
    # Social themes
    NOBLE = "noble"                     # Aristocracy and courts
    CRIMINAL = "criminal"               # Thieves and outlaws
    SCHOLARLY = "scholarly"             # Knowledge and learning
    ARTISAN = "artisan"                 # Crafts and creation
    
    # Adventure themes
    EXPLORATION = "exploration"         # Discovery and travel
    MYSTERY = "mystery"                 # Secrets and investigation
    HORROR = "horror"                   # Fear and suspense
    HEROIC = "heroic"                   # Classic heroism
    
    @property
    def is_magical(self) -> bool:
        """Check if this theme involves magic."""
        return self in {
            self.ARCANE, self.DIVINE, self.ELEMENTAL, self.CELESTIAL,
            self.INFERNAL, self.UNDEAD, self.ABERRANT
        }
    
    @property
    def is_social(self) -> bool:
        """Check if this theme is socially focused."""
        return self in {self.NOBLE, self.CRIMINAL, self.SCHOLARLY, self.ARTISAN}


class PowerTier(Enum):
    """
    Power tiers matching D&D 5e level ranges.
    
    Official D&D power tier system for organizing content by appropriate level ranges.
    """
    TIER_1 = "tier_1"    # Levels 1-4: Local heroes
    TIER_2 = "tier_2"    # Levels 5-10: Heroes of the realm
    TIER_3 = "tier_3"    # Levels 11-16: Masters of the realm
    TIER_4 = "tier_4"    # Levels 17-20: Masters of the world
    
    @property
    def level_range(self) -> tuple[int, int]:
        """Get the level range for this tier."""
        ranges = {
            self.TIER_1: (1, 4),
            self.TIER_2: (5, 10),
            self.TIER_3: (11, 16),
            self.TIER_4: (17, 20)
        }
        return ranges[self]
    
    @property
    def min_level(self) -> int:
        """Get minimum level for this tier."""
        return self.level_range[0]
    
    @property
    def max_level(self) -> int:
        """Get maximum level for this tier."""
        return self.level_range[1]
    
    @classmethod
    def from_level(cls, level: int) -> 'PowerTier':
        """Get power tier for a specific level."""
        if 1 <= level <= 4:
            return cls.TIER_1
        elif 5 <= level <= 10:
            return cls.TIER_2
        elif 11 <= level <= 16:
            return cls.TIER_3
        elif 17 <= level <= 20:
            return cls.TIER_4
        else:
            raise ValueError(f"Invalid level: {level}")


class ContentStatus(Enum):
    """
    Status of content in the creation/review pipeline.
    
    Tracks the current state of content through the generation and review process.
    """
    DRAFT = "draft"                     # Initial creation
    IN_REVIEW = "in_review"             # Under review
    NEEDS_REVISION = "needs_revision"   # Requires changes
    APPROVED = "approved"               # Ready for use
    PUBLISHED = "published"             # Available to users
    ARCHIVED = "archived"               # No longer active
    REJECTED = "rejected"               # Not suitable for use
    
    @property
    def is_active(self) -> bool:
        """Check if content with this status is actively available."""
        return self in {self.APPROVED, self.PUBLISHED}
    
    @property
    def needs_attention(self) -> bool:
        """Check if content with this status needs attention."""
        return self in {self.DRAFT, self.IN_REVIEW, self.NEEDS_REVISION}


# Content type groupings for easier management
CHARACTER_OPTIONS = {
    ContentType.SPECIES,
    ContentType.CHARACTER_CLASS,
    ContentType.SUBCLASS,
    ContentType.BACKGROUND,
    ContentType.FEAT
}

ITEM_TYPES = {
    ContentType.EQUIPMENT,
    ContentType.MAGIC_ITEM
}

MECHANICAL_CONTENT = {
    ContentType.SPECIES,
    ContentType.CHARACTER_CLASS,
    ContentType.SUBCLASS,
    ContentType.FEAT,
    ContentType.SPELL,
    ContentType.EQUIPMENT,
    ContentType.MAGIC_ITEM,
    ContentType.MONSTER
}

NARRATIVE_CONTENT = {
    ContentType.BACKGROUND,
    ContentType.ADVENTURE_HOOK
}


def get_content_types_by_category(category: str) -> Set[ContentType]:
    """
    Get content types by category name.
    
    Args:
        category: Category name ('character_options', 'items', 'mechanical', 'narrative')
        
    Returns:
        Set of ContentType enums in that category
    """
    categories = {
        'character_options': CHARACTER_OPTIONS,
        'items': ITEM_TYPES,
        'mechanical': MECHANICAL_CONTENT,
        'narrative': NARRATIVE_CONTENT
    }
    
    return categories.get(category, set())


def get_compatible_themes(content_type: ContentType) -> Set[ThemeCategory]:
    """
    Get themes that are compatible with a content type.
    
    Args:
        content_type: The content type to check
        
    Returns:
        Set of compatible themes
    """
    # All themes are generally compatible, but some have natural affinities
    if content_type in {ContentType.SPELL, ContentType.MAGIC_ITEM}:
        return {theme for theme in ThemeCategory if theme.is_magical}
    elif content_type == ContentType.BACKGROUND:
        return {theme for theme in ThemeCategory if theme.is_social}
    else:
        return set(ThemeCategory)