"""
Culture Generation Type Definitions.

Defines comprehensive type system for AI-powered culture generation including
generation types, authenticity levels, creativity constraints, and validation
categories for maintaining educational accuracy and cultural respect.

This module provides:
- Culture generation workflow types
- Authenticity and accuracy level definitions
- Creative freedom constraint levels
- Cultural research source types
- Validation severity categories
- Generation status tracking enums
"""

from enum import Enum, auto
from typing import Dict, List, Optional


class CultureGenerationType(Enum):
    """Types of culture generation workflows."""
    CUSTOM = auto()          # User-defined culture from prompt
    ENHANCEMENT = auto()     # Enhancing existing pre-built cultures
    ANALYSIS = auto()        # Analyzing character concepts for cultural elements
    HYBRID = auto()          # Combining multiple cultural elements
    DERIVATIVE = auto()      # Creating variants of existing cultures
    RECONSTRUCTION = auto()  # Reconstructing cultures from partial information


class CultureAuthenticityLevel(Enum):
    """Levels of cultural authenticity and historical accuracy."""
    ACADEMIC = auto()        # Academic-level research and accuracy
    HIGH = auto()           # Strict adherence to cultural accuracy
    MODERATE = auto()       # Balanced authenticity with creative liberties
    CREATIVE = auto()       # Focus on creativity over strict accuracy
    FANTASY = auto()        # Fantasy adaptation of cultural elements
    NONE = auto()           # No authenticity requirements, purely creative
    
    @property
    def description(self) -> str:
        """Get description of authenticity level."""
        descriptions = {
            self.ACADEMIC: "Academic-level research with scholarly sources",
            self.HIGH: "High historical accuracy with minimal creative liberties", 
            self.MODERATE: "Balanced approach maintaining cultural respect",
            self.CREATIVE: "Creative interpretation while maintaining cultural essence",
            self.FANTASY: "Fantasy adaptation suitable for gaming contexts",
            self.NONE: "Pure creativity without historical constraints"
        }
        return descriptions.get(self, "Unknown authenticity level")


class CultureCreativityLevel(Enum):
    """Levels of creativity allowed in culture generation."""
    CONSERVATIVE = auto()    # Minimal creative changes, strict historical accuracy
    BALANCED = auto()       # Moderate creativity balanced with authenticity
    CREATIVE = auto()       # High creativity with cultural foundation
    EXPERIMENTAL = auto()   # Maximum creativity, experimental combinations
    UNRESTRICTED = auto()   # No creative restrictions, pure imagination
    
    @property
    def creative_freedom_percentage(self) -> int:
        """Get approximate creative freedom percentage."""
        percentages = {
            self.CONSERVATIVE: 10,
            self.BALANCED: 35,
            self.CREATIVE: 60,
            self.EXPERIMENTAL: 85,
            self.UNRESTRICTED: 100
        }
        return percentages.get(self, 0)


class CultureSourceType(Enum):
    """Types of cultural research sources."""
    HISTORICAL = auto()      # Historical civilizations and cultures
    MYTHOLOGICAL = auto()    # Mythological and legendary cultures
    LITERARY = auto()        # Cultures from literature and stories
    LINGUISTIC = auto()      # Language-based cultural patterns
    REGIONAL = auto()        # Geographic/regional cultural variations
    RELIGIOUS = auto()       # Religious and spiritual traditions
    OCCUPATIONAL = auto()    # Professional/craft-based cultures
    TEMPORAL = auto()        # Time period-specific cultures
    HYBRID_CULTURAL = auto() # Combinations of multiple source types


class CultureComplexityLevel(Enum):
    """Complexity levels for generated cultures."""
    SIMPLE = auto()          # Basic naming patterns only
    STANDARD = auto()        # Names, titles, basic cultural elements
    DETAILED = auto()        # Rich cultural context and traditions
    COMPREHENSIVE = auto()   # Full cultural system with deep lore
    SCHOLARLY = auto()       # Academic-level detail and research
    
    @property
    def expected_elements(self) -> int:
        """Get expected number of cultural elements."""
        elements = {
            self.SIMPLE: 50,      # Basic name lists
            self.STANDARD: 150,   # Names + titles + basic traits
            self.DETAILED: 300,   # Rich cultural content
            self.COMPREHENSIVE: 500, # Full cultural system
            self.SCHOLARLY: 750   # Extensive academic detail
        }
        return elements.get(self, 0)


class CultureValidationCategory(Enum):
    """Categories for culture validation."""
    LINGUISTIC = auto()      # Language patterns and authenticity
    HISTORICAL = auto()      # Historical accuracy and context
    CULTURAL = auto()        # Cultural sensitivity and respect
    EDUCATIONAL = auto()     # Educational value and appropriateness
    GAMING = auto()          # Suitability for gaming contexts
    TECHNICAL = auto()       # Technical implementation correctness
    COMPLETENESS = auto()    # Completeness of required elements


class CultureValidationSeverity(Enum):
    """Severity levels for culture validation issues."""
    CRITICAL = auto()        # Blocks generation, must be fixed
    HIGH = auto()           # Significant issues requiring attention
    MEDIUM = auto()         # Moderate issues, recommended fixes
    LOW = auto()            # Minor issues, optional improvements
    INFO = auto()           # Informational notices
    
    @property
    def should_block_generation(self) -> bool:
        """Whether this severity should block culture generation."""
        return self == self.CRITICAL


class CultureGenerationStatus(Enum):
    """Status tracking for culture generation workflow."""
    PENDING = auto()         # Generation request received
    ANALYZING = auto()       # Analyzing user input and requirements
    RESEARCHING = auto()     # Conducting cultural research
    GENERATING = auto()      # LLM generating cultural content
    PARSING = auto()         # Parsing LLM response
    VALIDATING = auto()      # Validating generated culture
    ENHANCING = auto()       # Enhancing with additional details
    FINALIZING = auto()      # Final processing and formatting
    COMPLETED = auto()       # Generation successfully completed
    FAILED = auto()          # Generation failed
    CANCELLED = auto()       # Generation cancelled by user
    
    @property
    def is_terminal(self) -> bool:
        """Whether this status represents a terminal state."""
        return self in {self.COMPLETED, self.FAILED, self.CANCELLED}
    
    @property
    def progress_percentage(self) -> Optional[int]:
        """Get approximate progress percentage for this status."""
        progress = {
            self.PENDING: 0,
            self.ANALYZING: 10,
            self.RESEARCHING: 25,
            self.GENERATING: 50,
            self.PARSING: 70,
            self.VALIDATING: 80,
            self.ENHANCING: 90,
            self.FINALIZING: 95,
            self.COMPLETED: 100,
            self.FAILED: None,
            self.CANCELLED: None
        }
        return progress.get(self)


class CultureNamingStructure(Enum):
    """Naming structure patterns for cultures."""
    GIVEN_FAMILY = auto()    # Given name + Family name (Western style)
    FAMILY_GIVEN = auto()    # Family name + Given name (East Asian style)
    PATRONYMIC = auto()      # Name + Father's name (Nordic/Slavic style)
    MATRONYMIC = auto()      # Name + Mother's name
    CLAN_INDIVIDUAL = auto() # Clan name + Individual name
    TITLE_NAME = auto()      # Title + Name (Noble/Religious style)
    DESCRIPTIVE = auto()     # Descriptive epithets and nicknames
    MONONYM = auto()          # Single names only
    COMPLEX = auto()         # Multiple naming conventions combined


class CultureGenderSystem(Enum):
    """Gender systems for cultural naming."""
    BINARY = auto()          # Male/Female binary system
    NEUTRAL = auto()         # Gender-neutral naming system
    FLUID = auto()           # Flexible gender expression in names
    ROLE_BASED = auto()      # Names based on social roles
    AGE_BASED = auto()       # Names change with age/life stage
    ACHIEVEMENT_BASED = auto() # Names based on accomplishments


class CultureLinguisticFamily(Enum):
    """Major linguistic families for authentic language patterns."""
    INDO_EUROPEAN = auto()   # Indo-European language family
    SINO_TIBETAN = auto()    # Chinese, Tibetan language family
    AFROASIATIC = auto()     # Arabic, Hebrew, Egyptian language family
    NIGER_CONGO = auto()     # African language family
    AUSTRONESIAN = auto()    # Pacific Islander language family
    TRANS_NEW_GUINEA = auto() # Papua New Guinea language family
    ALTAIC = auto()          # Turkic, Mongolian language family
    AMERINDIAN = auto()      # Native American language families
    CONSTRUCTED = auto()     # Constructed languages (Tolkien, etc.)
    FANTASY = auto()         # Pure fantasy linguistic patterns


class CultureTemporalPeriod(Enum):
    """Historical time periods for cultural context."""
    PREHISTORIC = auto()     # Before written history
    ANCIENT = auto()         # Ancient civilizations (3000 BCE - 500 CE)
    CLASSICAL = auto()       # Classical antiquity (800 BCE - 600 CE)
    MEDIEVAL = auto()        # Medieval period (500 - 1500 CE)
    RENAISSANCE = auto()     # Renaissance (1300 - 1600 CE)
    EARLY_MODERN = auto()    # Early modern (1450 - 1800 CE)
    INDUSTRIAL = auto()      # Industrial age (1760 - 1840 CE)
    MODERN = auto()          # Modern era (1800 - 1950 CE)
    CONTEMPORARY = auto()    # Contemporary (1950 - present)
    FUTURISTIC = auto()      # Speculative future
    TIMELESS = auto()        # Not bound to specific time period
    MYTHOLOGICAL = auto()    # Mythological/legendary time


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_default_authenticity_for_source(source_type: CultureSourceType) -> CultureAuthenticityLevel:
    """Get recommended authenticity level for source type."""
    defaults = {
        CultureSourceType.HISTORICAL: CultureAuthenticityLevel.HIGH,
        CultureSourceType.MYTHOLOGICAL: CultureAuthenticityLevel.MODERATE,
        CultureSourceType.LITERARY: CultureAuthenticityLevel.CREATIVE,
        CultureSourceType.LINGUISTIC: CultureAuthenticityLevel.HIGH,
        CultureSourceType.REGIONAL: CultureAuthenticityLevel.MODERATE,
        CultureSourceType.RELIGIOUS: CultureAuthenticityLevel.HIGH,
        CultureSourceType.OCCUPATIONAL: CultureAuthenticityLevel.MODERATE,
        CultureSourceType.TEMPORAL: CultureAuthenticityLevel.MODERATE,
        CultureSourceType.HYBRID_CULTURAL: CultureAuthenticityLevel.CREATIVE
    }
    return defaults.get(source_type, CultureAuthenticityLevel.MODERATE)


def get_complexity_for_authenticity(authenticity: CultureAuthenticityLevel) -> CultureComplexityLevel:
    """Get recommended complexity level for authenticity level."""
    complexity_mapping = {
        CultureAuthenticityLevel.ACADEMIC: CultureComplexityLevel.SCHOLARLY,
        CultureAuthenticityLevel.HIGH: CultureComplexityLevel.COMPREHENSIVE,
        CultureAuthenticityLevel.MODERATE: CultureComplexityLevel.DETAILED,
        CultureAuthenticityLevel.CREATIVE: CultureComplexityLevel.STANDARD,
        CultureAuthenticityLevel.FANTASY: CultureComplexityLevel.STANDARD,
        CultureAuthenticityLevel.NONE: CultureComplexityLevel.SIMPLE
    }
    return complexity_mapping.get(authenticity, CultureComplexityLevel.STANDARD)


def validate_culture_configuration(
    generation_type: CultureGenerationType,
    authenticity: CultureAuthenticityLevel,
    creativity: CultureCreativityLevel,
    complexity: CultureComplexityLevel
) -> List[str]:
    """Validate culture generation configuration for conflicts."""
    issues = []
    
    # Check for authenticity/creativity conflicts
    if authenticity == CultureAuthenticityLevel.ACADEMIC and creativity == CultureCreativityLevel.UNRESTRICTED:
        issues.append("Academic authenticity conflicts with unrestricted creativity")
    
    if authenticity == CultureAuthenticityLevel.HIGH and creativity in {
        CultureCreativityLevel.EXPERIMENTAL, CultureCreativityLevel.UNRESTRICTED
    }:
        issues.append("High authenticity may conflict with experimental creativity")
    
    # Check for complexity/authenticity alignment
    if authenticity == CultureAuthenticityLevel.ACADEMIC and complexity == CultureComplexityLevel.SIMPLE:
        issues.append("Academic authenticity requires higher complexity than simple")
    
    if authenticity == CultureAuthenticityLevel.NONE and complexity == CultureComplexityLevel.SCHOLARLY:
        issues.append("Scholarly complexity unnecessary without authenticity requirements")
    
    return issues


# ============================================================================
# CONFIGURATION PRESETS
# ============================================================================

# Predefined configuration presets for common use cases
CULTURE_GENERATION_PRESETS = {
    "academic_research": {
        "authenticity": CultureAuthenticityLevel.ACADEMIC,
        "creativity": CultureCreativityLevel.CONSERVATIVE,
        "complexity": CultureComplexityLevel.SCHOLARLY,
        "source_types": [CultureSourceType.HISTORICAL, CultureSourceType.LINGUISTIC]
    },
    "educational_gaming": {
        "authenticity": CultureAuthenticityLevel.HIGH,
        "creativity": CultureCreativityLevel.BALANCED,
        "complexity": CultureComplexityLevel.DETAILED,
        "source_types": [CultureSourceType.HISTORICAL, CultureSourceType.MYTHOLOGICAL]
    },
    "creative_fantasy": {
        "authenticity": CultureAuthenticityLevel.CREATIVE,
        "creativity": CultureCreativityLevel.CREATIVE,
        "complexity": CultureComplexityLevel.STANDARD,
        "source_types": [CultureSourceType.MYTHOLOGICAL, CultureSourceType.LITERARY]
    },
    "experimental_worldbuilding": {
        "authenticity": CultureAuthenticityLevel.FANTASY,
        "creativity": CultureCreativityLevel.EXPERIMENTAL,
        "complexity": CultureComplexityLevel.COMPREHENSIVE,
        "source_types": [CultureSourceType.HYBRID_CULTURAL]
    },
    "quick_generation": {
        "authenticity": CultureAuthenticityLevel.MODERATE,
        "creativity": CultureCreativityLevel.BALANCED,
        "complexity": CultureComplexityLevel.SIMPLE,
        "source_types": [CultureSourceType.HISTORICAL]
    }
}


# ============================================================================
# MODULE METADATA
# ============================================================================

__version__ = "1.0.0"
__description__ = "Culture Generation Type Definitions for D&D Character Creator"

# Clean Architecture compliance
CLEAN_ARCHITECTURE_COMPLIANCE = {
    "layer": "core/enums",
    "dependencies": ["enum", "typing"],
    "dependents": ["culture_generator", "dynamic_culture_service", "culture_validation"],
    "infrastructure_independent": True,
    "pure_functions": True,
    "side_effects": "none",
    "focuses_on": "Type definitions for culture generation system"
}