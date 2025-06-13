"""
Character Progression Type Enumerations.

Defines progression-related enums for level advancement, milestone tracking,
and character evolution throughout levels 1-20.
"""

from enum import Enum


class ProgressionType(Enum):
    """Types of character progression."""
    SINGLE_CLASS = "single_class"       # Single class progression
    MULTICLASS = "multiclass"           # Multiple class progression
    HYBRID = "hybrid"                   # Mixed progression with variants
    
    @property
    def complexity_multiplier(self) -> float:
        """Get complexity multiplier for progression calculations."""
        multipliers = {
            self.SINGLE_CLASS: 1.0,
            self.MULTICLASS: 1.5,
            self.HYBRID: 2.0
        }
        return multipliers[self]


class MilestoneType(Enum):
    """Types of character progression milestones."""
    LEVEL_UP = "level_up"               # Standard level advancement
    CLASS_FEATURE = "class_feature"     # New class feature gained
    SUBCLASS_FEATURE = "subclass_feature"  # New subclass feature
    SPELL_LEVEL = "spell_level"         # New spell level access
    ABILITY_SCORE = "ability_score"     # Ability score improvement
    FEAT = "feat"                       # New feat acquisition
    SIGNATURE_ABILITY = "signature_ability"  # Character-defining ability
    EQUIPMENT_UPGRADE = "equipment_upgrade"  # Major equipment advancement
    THEMATIC_EVOLUTION = "thematic_evolution"  # Character theme development
    
    @property
    def is_major_milestone(self) -> bool:
        """Check if this is a major character milestone."""
        return self in {
            self.SUBCLASS_FEATURE,
            self.SPELL_LEVEL,
            self.SIGNATURE_ABILITY,
            self.THEMATIC_EVOLUTION
        }


class FeatureCategory(Enum):
    """Categories of character features."""
    CORE_FEATURE = "core_feature"       # Essential class features
    OPTIONAL_FEATURE = "optional_feature"  # Optional class features
    SIGNATURE_FEATURE = "signature_feature"  # Character-unique features
    CUSTOM_FEATURE = "custom_feature"   # Generated custom features
    EQUIPMENT_FEATURE = "equipment_feature"  # Equipment-based features
    
    @property
    def is_customizable(self) -> bool:
        """Check if this feature category can be customized."""
        return self in {
            self.SIGNATURE_FEATURE,
            self.CUSTOM_FEATURE,
            self.EQUIPMENT_FEATURE
        }


class ScalingType(Enum):
    """Types of feature scaling with level."""
    NONE = "none"                       # No scaling
    LINEAR = "linear"                   # Linear progression
    STEPPED = "stepped"                 # Steps at specific levels
    EXPONENTIAL = "exponential"         # Exponential growth
    SPELL_SLOT = "spell_slot"          # Follows spell slot progression
    PROFICIENCY = "proficiency"         # Scales with proficiency bonus
    
    @property
    def requires_calculation(self) -> bool:
        """Check if scaling requires dynamic calculation."""
        return self in {
            self.LINEAR,
            self.EXPONENTIAL,
            self.SPELL_SLOT,
            self.PROFICIENCY
        }


class ThematicTier(Enum):
    """Thematic character development tiers."""
    APPRENTICE = "apprentice"           # Levels 1-4: Learning the basics
    JOURNEYMAN = "journeyman"           # Levels 5-10: Developing expertise
    EXPERT = "expert"                   # Levels 11-16: Mastering abilities
    LEGEND = "legend"                   # Levels 17-20: Legendary status
    
    @property
    def power_tier_equivalent(self) -> str:
        """Get equivalent D&D power tier."""
        equivalents = {
            self.APPRENTICE: "tier_1",
            self.JOURNEYMAN: "tier_2", 
            self.EXPERT: "tier_3",
            self.LEGEND: "tier_4"
        }
        return equivalents[self]
    
    @classmethod
    def from_level(cls, level: int) -> 'ThematicTier':
        """Get thematic tier for a specific level."""
        if 1 <= level <= 4:
            return cls.APPRENTICE
        elif 5 <= level <= 10:
            return cls.JOURNEYMAN
        elif 11 <= level <= 16:
            return cls.EXPERT
        elif 17 <= level <= 20:
            return cls.LEGEND
        else:
            raise ValueError(f"Invalid level: {level}")