"""
Creativity Level Enumerations for Content Generation.

Defines the levels of creative freedom allowed during character and content
generation, balancing creative expression with D&D rule compliance.
"""

from enum import Enum


class CreativityLevel(Enum):
    """Levels of creative freedom for content generation."""
    CONSERVATIVE = "conservative"       # Minimal custom content, stick to official
    STANDARD = "standard"              # Balanced custom content within norms
    HIGH = "high"                      # Extensive custom content, creative freedom
    MAXIMUM = "maximum"                # Unlimited creativity within D&D framework
    
    @property
    def allows_custom_species(self) -> bool:
        """Check if this level allows custom species generation."""
        return self in {self.STANDARD, self.HIGH, self.MAXIMUM}
    
    @property
    def allows_custom_classes(self) -> bool:
        """Check if this level allows custom class generation."""
        return self in {self.HIGH, self.MAXIMUM}
    
    @property
    def allows_signature_equipment(self) -> bool:
        """Check if this level allows signature equipment generation."""
        return self in {self.STANDARD, self.HIGH, self.MAXIMUM}
    
    @property
    def max_custom_content_per_character(self) -> int:
        """Get maximum custom content items per character."""
        limits = {
            self.CONSERVATIVE: 1,
            self.STANDARD: 5,
            self.HIGH: 10,
            self.MAXIMUM: 20
        }
        return limits[self]
    
    @property
    def generation_temperature(self) -> float:
        """Get LLM temperature for this creativity level."""
        temperatures = {
            self.CONSERVATIVE: 0.3,
            self.STANDARD: 0.7,
            self.HIGH: 0.9,
            self.MAXIMUM: 1.1
        }
        return temperatures[self]


class GenerationMethod(Enum):
    """Methods for generating content."""
    LLM_CREATIVE = "llm_creative"       # AI-driven creative generation
    TEMPLATE_BASED = "template_based"   # Template-based generation
    HYBRID = "hybrid"                   # Combination of LLM and templates
    PROCEDURAL = "procedural"           # Algorithm-based generation
    
    @property
    def uses_ai(self) -> bool:
        """Check if this method uses AI assistance."""
        return self in {self.LLM_CREATIVE, self.HYBRID}


class ContentComplexity(Enum):
    """Complexity levels for generated content."""
    SIMPLE = "simple"                   # Basic mechanics, easy to understand
    MODERATE = "moderate"               # Standard complexity, balanced features
    COMPLEX = "complex"                 # Advanced mechanics, multiple interactions
    MASTERWORK = "masterwork"           # Highly detailed, premium content
    
    @property
    def generation_effort_multiplier(self) -> float:
        """Get generation effort multiplier for this complexity."""
        multipliers = {
            self.SIMPLE: 1.0,
            self.MODERATE: 1.5,
            self.COMPLEX: 2.0,
            self.MASTERWORK: 3.0
        }
        return multipliers[self]


class ThematicConsistency(Enum):
    """Levels of thematic consistency enforcement."""
    LOOSE = "loose"                     # Flexible theme interpretation
    MODERATE = "moderate"               # Balanced theme enforcement
    STRICT = "strict"                   # Rigid theme consistency
    ABSOLUTE = "absolute"               # Perfect thematic alignment required
    
    @property
    def allows_theme_deviation(self) -> bool:
        """Check if theme deviation is allowed."""
        return self in {self.LOOSE, self.MODERATE}