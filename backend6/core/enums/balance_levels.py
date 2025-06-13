"""
Balance Level Enumerations for Content Validation.

Defines balance assessment levels, validation severity, and power level
measurements for generated D&D content.
"""

from enum import Enum


class BalanceLevel(Enum):
    """Balance assessment levels for content evaluation."""
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
            self.SLIGHTLY_UNDERPOWERED, 
            self.BALANCED, 
            self.SLIGHTLY_OVERPOWERED
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
    
    @property
    def requires_adjustment(self) -> bool:
        """Check if content at this level requires adjustment."""
        return self in {
            self.SEVERELY_UNDERPOWERED,
            self.UNDERPOWERED,
            self.OVERPOWERED,
            self.SEVERELY_OVERPOWERED,
            self.BROKEN
        }


class ValidationLevel(Enum):
    """Validation strictness levels."""
    PERMISSIVE = "permissive"           # Allow minor rule bending
    STANDARD = "standard"               # Standard D&D compliance
    STRICT = "strict"                   # Rigid rule enforcement
    TOURNAMENT = "tournament"           # Tournament-level compliance
    
    @property
    def power_deviation_tolerance(self) -> float:
        """Get power level deviation tolerance."""
        tolerances = {
            self.PERMISSIVE: 0.3,      # 30% deviation allowed
            self.STANDARD: 0.2,        # 20% deviation allowed
            self.STRICT: 0.1,          # 10% deviation allowed
            self.TOURNAMENT: 0.05      # 5% deviation allowed
        }
        return tolerances[self]


class BalanceCategory(Enum):
    """Categories for balance assessment."""
    COMBAT_POWER = "combat_power"       # Direct combat effectiveness
    UTILITY = "utility"                 # Out-of-combat usefulness
    VERSATILITY = "versatility"         # Flexibility and options
    SURVIVABILITY = "survivability"     # Defensive capabilities
    RESOURCE_EFFICIENCY = "resource_efficiency"  # Resource cost vs. benefit
    SCALING = "scaling"                 # Level progression balance
    
    @property
    def weight_in_assessment(self) -> float:
        """Get weight of this category in overall balance assessment."""
        weights = {
            self.COMBAT_POWER: 0.25,
            self.UTILITY: 0.20,
            self.VERSATILITY: 0.15,
            self.SURVIVABILITY: 0.15,
            self.RESOURCE_EFFICIENCY: 0.15,
            self.SCALING: 0.10
        }
        return weights[self]


class PowerBenchmark(Enum):
    """Power level benchmarks for comparison."""
    CORE_SPECIES = "core_species"       # PHB species baseline
    CORE_CLASSES = "core_classes"       # PHB classes baseline
    CORE_SPELLS = "core_spells"         # PHB spells baseline
    CORE_FEATS = "core_feats"           # PHB feats baseline
    VARIANT_RULES = "variant_rules"     # Official variant rules
    OFFICIAL_SUPPLEMENTS = "official_supplements"  # Official expansions
    
    @property
    def comparison_strictness(self) -> float:
        """Get strictness multiplier for comparison."""
        strictness = {
            self.CORE_SPECIES: 1.0,
            self.CORE_CLASSES: 1.0,
            self.CORE_SPELLS: 1.0,
            self.CORE_FEATS: 1.0,
            self.VARIANT_RULES: 0.9,
            self.OFFICIAL_SUPPLEMENTS: 0.8
        }
        return strictness[self]