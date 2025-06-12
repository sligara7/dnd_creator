from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
from ..enums.content_types import ContentType
from ..enums.validation_types import BalanceCategory


@dataclass(frozen=True)
class BalanceMetrics:
    """
    Value object representing comprehensive balance metrics for generated content.
    
    This supports the Creative Content Framework's validation-first design by
    providing detailed balance analysis for all generated content types.
    """
    
    # === CORE BALANCE SCORES ===
    overall_score: float  # 0.0 (underpowered) to 1.0 (overpowered), 0.5 = balanced
    power_level: float    # Raw power assessment
    utility_score: float  # Out-of-combat utility
    versatility_score: float  # Flexibility and options
    scaling_score: float  # How well it scales with level
    
    # === CATEGORY SCORES ===
    category_scores: Dict[BalanceCategory, float] = field(default_factory=dict)
    
    # === DETAILED METRICS ===
    damage_per_round: Optional[float] = None
    healing_per_round: Optional[float] = None
    defensive_value: Optional[float] = None
    resource_efficiency: Optional[float] = None
    
    # === COMPARATIVE ANALYSIS ===
    compared_to_official: Optional[float] = None  # How it compares to official content
    power_level_tier: str = "standard"  # "low", "standard", "high", "epic"
    
    # === BALANCE ISSUES ===
    identified_issues: List[str] = field(default_factory=list)
    recommended_adjustments: List[str] = field(default_factory=list)
    
    # === METADATA ===
    content_type: ContentType
    level_range: Optional[tuple] = None  # (min_level, max_level) if applicable
    calculation_method: str = "standard"
    calculated_at: str = ""  # Timestamp
    
    def __post_init__(self):
        """Validate balance metrics on creation."""
        # Validate score ranges
        scores_to_check = [
            self.overall_score, self.power_level, self.utility_score,
            self.versatility_score, self.scaling_score
        ]
        
        for score in scores_to_check:
            if not (0.0 <= score <= 1.0):
                raise ValueError(f"Balance scores must be between 0.0 and 1.0, got {score}")
        
        # Validate power level tier
        valid_tiers = {"low", "standard", "high", "epic"}
        if self.power_level_tier not in valid_tiers:
            raise ValueError(f"Invalid power level tier: {self.power_level_tier}")
    
    @property
    def is_balanced(self) -> bool:
        """Check if content is considered balanced (score between 0.3 and 0.7)."""
        return 0.3 <= self.overall_score <= 0.7
    
    @property
    def is_overpowered(self) -> bool:
        """Check if content is overpowered (score > 0.7)."""
        return self.overall_score > 0.7
    
    @property
    def is_underpowered(self) -> bool:
        """Check if content is underpowered (score < 0.3)."""
        return self.overall_score < 0.3
    
    @property
    def balance_rating(self) -> str:
        """Get human-readable balance rating."""
        if self.overall_score < 0.2:
            return "Severely Underpowered"
        elif self.overall_score < 0.3:
            return "Underpowered"
        elif self.overall_score < 0.4:
            return "Slightly Weak"
        elif self.overall_score < 0.6:
            return "Well Balanced"
        elif self.overall_score < 0.7:
            return "Slightly Strong"
        elif self.overall_score < 0.8:
            return "Overpowered"
        else:
            return "Severely Overpowered"
    
    @property
    def has_critical_issues(self) -> bool:
        """Check if there are critical balance issues."""
        critical_keywords = ["game-breaking", "infinite", "exploit", "critical"]
        return any(
            any(keyword in issue.lower() for keyword in critical_keywords)
            for issue in self.identified_issues
        )
    
    def get_category_score(self, category: BalanceCategory) -> float:
        """Get score for a specific balance category."""
        return self.category_scores.get(category, 0.5)  # Default to neutral
    
    def get_balance_summary(self) -> Dict[str, Any]:
        """Get comprehensive balance summary."""
        return {
            "overall_rating": self.balance_rating,
            "overall_score": self.overall_score,
            "is_balanced": self.is_balanced,
            "power_tier": self.power_level_tier,
            "strengths": self._identify_strengths(),
            "weaknesses": self._identify_weaknesses(),
            "critical_issues": self.identified_issues if self.has_critical_issues else [],
            "recommended_adjustments": self.recommended_adjustments,
            "detailed_scores": {
                "power": self.power_level,
                "utility": self.utility_score,
                "versatility": self.versatility_score,
                "scaling": self.scaling_score
            }
        }
    
    def _identify_strengths(self) -> List[str]:
        """Identify areas where content excels."""
        strengths = []
        
        if self.power_level > 0.7:
            strengths.append("High combat effectiveness")
        if self.utility_score > 0.7:
            strengths.append("Excellent utility options")
        if self.versatility_score > 0.7:
            strengths.append("Great flexibility and adaptability")
        if self.scaling_score > 0.7:
            strengths.append("Scales well across levels")
        
        # Check category scores
        for category, score in self.category_scores.items():
            if score > 0.7:
                strengths.append(f"Strong {category.value}")
        
        return strengths
    
    def _identify_weaknesses(self) -> List[str]:
        """Identify areas where content is lacking."""
        weaknesses = []
        
        if self.power_level < 0.3:
            weaknesses.append("Low combat effectiveness")
        if self.utility_score < 0.3:
            weaknesses.append("Limited utility options")
        if self.versatility_score < 0.3:
            weaknesses.append("Inflexible, few options")
        if self.scaling_score < 0.3:
            weaknesses.append("Poor level scaling")
        
        # Check category scores
        for category, score in self.category_scores.items():
            if score < 0.3:
                weaknesses.append(f"Weak {category.value}")
        
        return weaknesses


@dataclass(frozen=True)
class AttackMetrics:
    """Balance metrics specific to attack capabilities."""
    
    attack_bonus: int
    damage_dice: str
    damage_bonus: int
    damage_type: str
    critical_range: int = 20
    special_properties: List[str] = field(default_factory=list)
    
    @property
    def average_damage(self) -> float:
        """Calculate average damage per attack."""
        # Parse dice string (e.g., "2d6", "1d8+3")
        if "d" not in self.damage_dice:
            return float(self.damage_bonus)
        
        try:
            if "+" in self.damage_dice:
                dice_part, bonus_part = self.damage_dice.split("+")
                base_bonus = int(bonus_part)
            else:
                dice_part = self.damage_dice
                base_bonus = 0
            
            num_dice, die_size = map(int, dice_part.split("d"))
            average_per_die = (die_size + 1) / 2
            
            return (num_dice * average_per_die) + base_bonus + self.damage_bonus
        except (ValueError, AttributeError):
            return float(self.damage_bonus)
    
    @property
    def damage_per_round_estimate(self) -> float:
        """Estimate damage per round accounting for hit chance."""
        # Assume 65% hit chance as baseline
        hit_chance = 0.65
        
        # Adjust for critical range
        crit_chance = (21 - self.critical_range) / 20
        normal_hit_chance = hit_chance - crit_chance
        
        normal_damage = self.average_damage * normal_hit_chance
        critical_damage = self.average_damage * 2 * crit_chance
        
        return normal_damage + critical_damage


@dataclass(frozen=True)
class DefensiveMetrics:
    """Balance metrics for defensive capabilities."""
    
    armor_class: int
    hit_points: int
    saving_throw_bonuses: Dict[str, int] = field(default_factory=dict)
    damage_resistances: List[str] = field(default_factory=list)
    damage_immunities: List[str] = field(default_factory=list)
    condition_immunities: List[str] = field(default_factory=list)
    
    @property
    def effective_hit_points(self) -> float:
        """Calculate effective HP accounting for resistances."""
        base_hp = self.hit_points
        
        # Simple resistance modifier (resistances roughly double effective HP)
        resistance_multiplier = 1.0 + (len(self.damage_resistances) * 0.3)
        immunity_multiplier = 1.0 + (len(self.damage_immunities) * 0.5)
        
        return base_hp * resistance_multiplier * immunity_multiplier
    
    @property
    def survivability_score(self) -> float:
        """Calculate overall survivability score (0.0 to 1.0)."""
        # Normalize AC (assuming 10-20 range for most content)
        ac_score = min(1.0, max(0.0, (self.armor_class - 10) / 10))
        
        # Normalize effective HP (assuming 0-200 range)
        hp_score = min(1.0, max(0.0, self.effective_hit_points / 200))
        
        # Average the scores
        return (ac_score + hp_score) / 2


@dataclass(frozen=True)
class ResourceMetrics:
    """Balance metrics for resource management."""
    
    resources_per_day: Dict[str, int] = field(default_factory=dict)
    resources_per_encounter: Dict[str, int] = field(default_factory=dict)
    resource_recovery_method: Dict[str, str] = field(default_factory=dict)  # "short", "long", "none"
    
    @property
    def resource_sustainability(self) -> float:
        """Calculate resource sustainability score (0.0 to 1.0)."""
        if not self.resources_per_day and not self.resources_per_encounter:
            return 1.0  # No resource limitations
        
        # Simple scoring based on resource availability
        daily_score = min(1.0, sum(self.resources_per_day.values()) / 10)
        encounter_score = min(1.0, sum(self.resources_per_encounter.values()) / 3)
        
        return max(daily_score, encounter_score)