"""
Balance scoring and calculation utilities.

This module provides pure functions for calculating balance scores and metrics
for generated content, supporting the Creative Content Framework's validation-first
design with comprehensive balance assessment.
"""

from typing import Dict, List, Optional, Any, Tuple
from ..enums.content_types import ContentType
from ..enums.dnd_constants import Ability, DamageType
from ..value_objects.balance_metrics import BalanceMetrics, AttackMetrics, DefensiveMetrics, ResourceMetrics


# === CORE BALANCE CALCULATIONS ===

def calculate_overall_balance_score(
    power_level: float,
    utility_score: float, 
    versatility_score: float,
    scaling_score: float,
    weights: Optional[Dict[str, float]] = None
) -> float:
    """
    Calculate overall balance score from component scores.
    
    Args:
        power_level: Combat power score (0.0-1.0)
        utility_score: Non-combat utility score (0.0-1.0)
        versatility_score: Flexibility/options score (0.0-1.0)
        scaling_score: Level scaling score (0.0-1.0)
        weights: Optional weights for each component
        
    Returns:
        Overall balance score (0.0-1.0), where 0.5 is balanced
    """
    if weights is None:
        weights = {"power": 0.3, "utility": 0.25, "versatility": 0.25, "scaling": 0.2}
    
    # Normalize weights to sum to 1.0
    total_weight = sum(weights.values())
    if total_weight > 0:
        weights = {k: v / total_weight for k, v in weights.items()}
    
    return (
        power_level * weights.get("power", 0.3) +
        utility_score * weights.get("utility", 0.25) +
        versatility_score * weights.get("versatility", 0.25) +
        scaling_score * weights.get("scaling", 0.2)
    )


def calculate_power_level_score(
    damage_output: float,
    defensive_value: float,
    resource_efficiency: float,
    level: int = 1
) -> float:
    """
    Calculate power level score based on combat metrics.
    
    Args:
        damage_output: Expected damage per round
        defensive_value: Survivability metric (AC, HP, etc.)
        resource_efficiency: Resource usage effectiveness (0.0-1.0)
        level: Character/content level for normalization
        
    Returns:
        Power level score (0.0-1.0), where 0.5 is balanced
    """
    # Level-based expected values (D&D 5e benchmarks)
    expected_damage = 4 + (level * 1.5)  # Rough damage scaling
    expected_defense = 10 + level  # AC scaling approximation
    
    # Normalize components (1.5x expected = max score to allow for powerful content)
    damage_score = min(1.0, damage_output / (expected_damage * 1.5)) if expected_damage > 0 else 0.0
    defense_score = min(1.0, defensive_value / (expected_defense * 1.5)) if expected_defense > 0 else 0.0
    efficiency_score = min(1.0, max(0.0, resource_efficiency))
    
    # Weight damage higher for power assessment
    return (damage_score * 0.5 + defense_score * 0.3 + efficiency_score * 0.2)


def calculate_utility_score(
    skill_bonuses: Dict[str, int],
    special_abilities: List[str],
    out_of_combat_features: List[str],
    social_abilities: List[str]
) -> float:
    """
    Calculate utility score for non-combat effectiveness.
    
    Args:
        skill_bonuses: Skill proficiencies and bonuses
        special_abilities: Special utility abilities
        out_of_combat_features: Non-combat features
        social_abilities: Social interaction abilities
        
    Returns:
        Utility score (0.0-1.0)
    """
    # Score based on breadth and depth of utility
    skill_score = min(1.0, len(skill_bonuses) / 10)  # Up to 10 skills for max score
    ability_score = min(1.0, len(special_abilities) / 5)  # Up to 5 abilities for max score
    feature_score = min(1.0, len(out_of_combat_features) / 3)  # Up to 3 features for max score
    social_score = min(1.0, len(social_abilities) / 3)  # Up to 3 social abilities for max score
    
    # Weight toward special abilities as they're more impactful
    return (skill_score * 0.3 + ability_score * 0.4 + feature_score * 0.2 + social_score * 0.1)


def calculate_versatility_score(
    available_options: List[str],
    situational_abilities: List[str],
    resource_flexibility: float,
    role_coverage: List[str]
) -> float:
    """
    Calculate versatility score for flexibility and adaptability.
    
    Args:
        available_options: Different tactical options available
        situational_abilities: Abilities useful in specific situations
        resource_flexibility: How flexibly resources can be used (0.0-1.0)
        role_coverage: Different roles this content can fill
        
    Returns:
        Versatility score (0.0-1.0)
    """
    # Score based on options and flexibility
    option_score = min(1.0, len(available_options) / 8)  # Up to 8 options for max score
    situational_score = min(1.0, len(situational_abilities) / 4)  # Up to 4 situational abilities
    flexibility_score = min(1.0, max(0.0, resource_flexibility))
    role_score = min(1.0, len(role_coverage) / 4)  # Up to 4 roles for max score
    
    # Equal weighting for versatility components
    return (option_score + situational_score + flexibility_score + role_score) / 4


def calculate_scaling_score(
    level_progression: Dict[int, float],
    min_level: int = 1,
    max_level: int = 20
) -> float:
    """
    Calculate how well content scales across levels.
    
    Args:
        level_progression: Power values at different levels
        min_level: Minimum relevant level
        max_level: Maximum relevant level
        
    Returns:
        Scaling score (0.0-1.0)
    """
    if not level_progression or len(level_progression) < 2:
        return 0.5  # Neutral if no progression data
    
    levels = sorted(level_progression.keys())
    values = [level_progression[level] for level in levels]
    
    # Check for consistent growth
    growth_rates = []
    for i in range(1, len(values)):
        if values[i-1] != 0:
            growth_rate = (values[i] - values[i-1]) / values[i-1]
            growth_rates.append(growth_rate)
    
    if not growth_rates:
        return 0.5
    
    # Good scaling has consistent positive growth
    avg_growth = sum(growth_rates) / len(growth_rates)
    growth_consistency = 1.0 - (max(growth_rates) - min(growth_rates)) / 2 if len(growth_rates) > 1 else 1.0
    
    # Combine growth rate and consistency
    growth_score = min(1.0, max(0.0, (avg_growth + 0.1) / 0.3))  # Target ~20% growth per tier
    consistency_score = max(0.0, growth_consistency)
    
    return (growth_score + consistency_score) / 2


# === DAMAGE AND COMBAT CALCULATIONS ===

def calculate_damage_per_round(
    attack_bonus: int,
    damage_dice: str,
    damage_bonus: int,
    num_attacks: int = 1,
    target_ac: int = 15,
    critical_range: int = 20
) -> float:
    """
    Calculate expected damage per round against a target.
    
    Args:
        attack_bonus: Attack roll bonus
        damage_dice: Damage dice string (e.g., "2d6")
        damage_bonus: Flat damage bonus
        num_attacks: Number of attacks per round
        target_ac: Target's Armor Class
        critical_range: Critical hit range (20 = only natural 20)
        
    Returns:
        Expected damage per round
    """
    # Calculate hit chance
    hit_threshold = target_ac - attack_bonus
    hit_chance = max(0.05, min(0.95, (21 - hit_threshold) / 20))  # 5% min, 95% max
    
    # Calculate critical chance
    crit_chance = (21 - critical_range) / 20
    normal_hit_chance = max(0.0, hit_chance - crit_chance)
    
    # Parse damage dice
    average_damage = parse_average_damage(damage_dice) + damage_bonus
    
    # Calculate expected damage
    normal_damage = average_damage * normal_hit_chance
    critical_damage = average_damage * 2 * crit_chance  # Critical hits double dice damage
    
    return (normal_damage + critical_damage) * num_attacks


def parse_average_damage(damage_dice: str) -> float:
    """
    Parse damage dice string and return average damage.
    
    Args:
        damage_dice: Dice notation (e.g., "2d6", "1d8+2")
        
    Returns:
        Average damage from dice
    """
    if not damage_dice or "d" not in damage_dice:
        return 0.0
    
    try:
        # Handle bonus in dice string
        bonus = 0
        if "+" in damage_dice:
            dice_part, bonus_str = damage_dice.split("+", 1)
            bonus = int(bonus_str.strip())
        elif "-" in damage_dice and damage_dice.count("-") == 1:
            dice_part, bonus_str = damage_dice.split("-", 1)
            bonus = -int(bonus_str.strip())
        else:
            dice_part = damage_dice
        
        # Parse dice
        num_dice, die_size = map(int, dice_part.strip().split("d"))
        average_per_die = (die_size + 1) / 2
        
        return (num_dice * average_per_die) + bonus
    
    except (ValueError, AttributeError):
        return 0.0


def calculate_survivability_score(
    armor_class: int,
    hit_points: int,
    saving_throws: Optional[Dict[str, int]] = None,
    resistances: Optional[List[str]] = None,
    immunities: Optional[List[str]] = None,
    level: int = 1
) -> float:
    """
    Calculate survivability score based on defensive capabilities.
    
    Args:
        armor_class: Armor Class
        hit_points: Hit Points
        saving_throws: Saving throw bonuses by ability
        resistances: Damage resistances
        immunities: Damage immunities
        level: Character level for normalization
        
    Returns:
        Survivability score (0.0-1.0)
    """
    saving_throws = saving_throws or {}
    resistances = resistances or []
    immunities = immunities or []
    
    # Expected values by level
    expected_ac = 10 + (level // 2)  # Rough AC progression
    expected_hp = 8 + (level * 6)    # Rough HP progression
    
    # AC score
    ac_ratio = armor_class / expected_ac if expected_ac > 0 else 1.0
    ac_score = min(1.0, max(0.0, (ac_ratio - 0.8) / 0.4 + 0.5))  # Scale around expected AC
    
    # HP score with resistance/immunity modifiers
    effective_hp = hit_points
    effective_hp *= (1 + len(resistances) * 0.3)  # Resistances increase effective HP
    effective_hp *= (1 + len(immunities) * 0.5)   # Immunities increase effective HP more
    
    hp_ratio = effective_hp / expected_hp if expected_hp > 0 else 1.0
    hp_score = min(1.0, max(0.0, hp_ratio / 1.5))  # Scale to 1.5x expected for max score
    
    # Saving throw score
    save_score = min(1.0, len(saving_throws) / 6)  # Up to 6 saves
    
    return (ac_score * 0.4 + hp_score * 0.4 + save_score * 0.2)


def calculate_resource_efficiency(
    resources_per_day: Optional[Dict[str, int]] = None,
    resources_per_encounter: Optional[Dict[str, int]] = None,
    recovery_methods: Optional[Dict[str, str]] = None
) -> float:
    """
    Calculate resource efficiency score.
    
    Args:
        resources_per_day: Daily resource limits
        resources_per_encounter: Per-encounter resource limits
        recovery_methods: How resources recover ("short", "long", "none")
        
    Returns:
        Resource efficiency score (0.0-1.0)
    """
    resources_per_day = resources_per_day or {}
    resources_per_encounter = resources_per_encounter or {}
    recovery_methods = recovery_methods or {}
    
    if not resources_per_day and not resources_per_encounter:
        return 1.0  # No resource limits = perfect efficiency
    
    # Score based on resource availability and recovery
    daily_resources = sum(resources_per_day.values())
    encounter_resources = sum(resources_per_encounter.values())
    
    # Short rest recovery is more efficient than long rest
    recovery_bonus = 0.0
    for recovery in recovery_methods.values():
        if recovery == "short":
            recovery_bonus += 0.3
        elif recovery == "long":
            recovery_bonus += 0.1
    
    # Normalize to reasonable range (assume 6-8 encounters per day)
    base_score = min(1.0, (daily_resources + encounter_resources * 7) / 20)
    return min(1.0, base_score + recovery_bonus)


# === CONTENT-SPECIFIC BALANCE METRICS ===

def create_balance_metrics(
    content_data: Dict[str, Any],
    content_type: ContentType,
    level: int = 1
) -> BalanceMetrics:
    """
    Create comprehensive balance metrics for content.
    
    Args:
        content_data: Raw content data dictionary
        content_type: Type of content being analyzed
        level: Content level for scaling calculations
        
    Returns:
        Complete BalanceMetrics object
    """
    # Content-type specific balance calculation
    balance_calculators = {
        ContentType.SPECIES: _create_species_balance_metrics,
        ContentType.CHARACTER_CLASS: _create_class_balance_metrics,
        ContentType.EQUIPMENT: _create_equipment_balance_metrics,
        ContentType.SPELL: _create_spell_balance_metrics,
        ContentType.FEAT: _create_feat_balance_metrics,
    }
    
    calculator = balance_calculators.get(content_type, _create_generic_balance_metrics)
    return calculator(content_data, level)


def _create_species_balance_metrics(content_data: Dict[str, Any], level: int) -> BalanceMetrics:
    """Create balance metrics specific to species/races."""
    # Extract species-specific features
    ability_bonuses = content_data.get("ability_score_increases", {})
    racial_features = content_data.get("racial_features", [])
    proficiencies = content_data.get("proficiencies", [])
    size = content_data.get("size", "Medium")
    
    # Calculate component scores
    # ASI value: +2/+1 split = standard, +3 total = high, +1 total = low
    total_asi = sum(ability_bonuses.values()) if ability_bonuses else 0
    power_score = min(1.0, max(0.2, total_asi / 3))  # Scale around +3 total
    
    utility_score = min(1.0, len(proficiencies) / 4)  # Skills, tools, etc.
    versatility_score = min(1.0, len(racial_features) / 3)  # Racial features provide options
    scaling_score = 0.4  # Most racial features don't scale much (intentionally low)
    
    overall_score = calculate_overall_balance_score(
        power_score, utility_score, versatility_score, scaling_score
    )
    
    # Determine power tier based on features
    power_tier = "standard"
    if total_asi >= 4 or len(racial_features) >= 4:
        power_tier = "high"
    elif total_asi <= 1 or len(racial_features) <= 1:
        power_tier = "low"
    
    return BalanceMetrics(
        overall_score=overall_score,
        power_level=power_score,
        utility_score=utility_score,
        versatility_score=versatility_score,
        scaling_score=scaling_score,
        content_type=ContentType.SPECIES,
        power_level_tier=power_tier,
        calculation_method="species_specific",
        level_range=(1, 20)  # Species features apply at all levels
    )


def _create_class_balance_metrics(content_data: Dict[str, Any], level: int) -> BalanceMetrics:
    """Create balance metrics specific to character classes."""
    # Extract class features
    hit_die = content_data.get("hit_die", 8)
    proficiencies = content_data.get("proficiencies", {})
    class_features = content_data.get("class_features", {})
    spellcasting = content_data.get("spellcasting", {})
    subclass_count = len(content_data.get("subclasses", []))
    
    # Calculate scores based on class capabilities
    power_score = _calculate_class_power_score(hit_die, class_features, spellcasting, level)
    utility_score = _calculate_class_utility_score(proficiencies, class_features)
    versatility_score = _calculate_class_versatility_score(class_features, spellcasting, subclass_count)
    scaling_score = _calculate_class_scaling_score(class_features)
    
    overall_score = calculate_overall_balance_score(
        power_score, utility_score, versatility_score, scaling_score
    )
    
    # Determine power tier
    power_tier = "standard"
    if power_score >= 0.7:
        power_tier = "high"
    elif power_score <= 0.3:
        power_tier = "low"
    
    return BalanceMetrics(
        overall_score=overall_score,
        power_level=power_score,
        utility_score=utility_score,
        versatility_score=versatility_score,
        scaling_score=scaling_score,
        content_type=ContentType.CHARACTER_CLASS,
        power_level_tier=power_tier,
        calculation_method="class_specific",
        level_range=(1, 20)
    )


def _create_equipment_balance_metrics(content_data: Dict[str, Any], level: int) -> BalanceMetrics:
    """Create balance metrics specific to equipment/items."""
    rarity = content_data.get("rarity", "common")
    enhancement_bonus = content_data.get("enhancement_bonus", 0)
    special_properties = content_data.get("properties", [])
    damage_dice = content_data.get("damage", "")
    armor_class = content_data.get("armor_class", 0)
    
    # Power based on enhancement and damage
    damage_power = parse_average_damage(damage_dice) / 10 if damage_dice else 0
    enhancement_power = enhancement_bonus / 3
    power_score = min(1.0, damage_power + enhancement_power)
    
    # Utility based on special properties
    utility_score = min(1.0, len(special_properties) / 3)
    
    # Versatility based on properties and usage flexibility
    versatility_score = min(1.0, len(special_properties) / 4)
    
    # Equipment generally doesn't scale
    scaling_score = 0.3
    
    overall_score = calculate_overall_balance_score(
        power_score, utility_score, versatility_score, scaling_score
    )
    
    # Power tier based on rarity
    tier_map = {
        "common": "low",
        "uncommon": "standard", 
        "rare": "standard",
        "very rare": "high",
        "legendary": "high",
        "artifact": "epic"
    }
    power_tier = tier_map.get(rarity.lower(), "standard")
    
    return BalanceMetrics(
        overall_score=overall_score,
        power_level=power_score,
        utility_score=utility_score,
        versatility_score=versatility_score,
        scaling_score=scaling_score,
        content_type=ContentType.EQUIPMENT,
        power_level_tier=power_tier,
        calculation_method="equipment_specific"
    )


def _create_spell_balance_metrics(content_data: Dict[str, Any], level: int) -> BalanceMetrics:
    """Create balance metrics specific to spells."""
    spell_level = content_data.get("level", 1)
    damage = content_data.get("damage", "")
    duration = content_data.get("duration", "")
    range_val = content_data.get("range", "")
    area_of_effect = content_data.get("area_of_effect", "")
    
    # Power based on damage and spell level
    base_damage = parse_average_damage(damage) if damage else 0
    expected_damage = spell_level * 3.5  # Rough spell damage scaling
    damage_ratio = base_damage / expected_damage if expected_damage > 0 else 0
    power_score = min(1.0, damage_ratio)
    
    # Utility based on duration and non-damage effects
    utility_indicators = ["buff", "debuff", "control", "utility"]
    utility_features = sum(1 for indicator in utility_indicators 
                          if indicator in str(content_data).lower())
    utility_score = min(1.0, utility_features / 2)
    
    # Versatility based on area, range, and flexibility
    versatility_factors = 0
    if area_of_effect:
        versatility_factors += 1
    if "choice" in str(content_data).lower():
        versatility_factors += 1
    if range_val and range_val.lower() not in ["self", "touch"]:
        versatility_factors += 1
    
    versatility_score = min(1.0, versatility_factors / 3)
    
    # Scaling based on spell level and upcast potential
    scaling_score = min(1.0, spell_level / 5)  # Higher level spells scale better
    if "higher level" in str(content_data).lower():
        scaling_score = min(1.0, scaling_score + 0.3)
    
    overall_score = calculate_overall_balance_score(
        power_score, utility_score, versatility_score, scaling_score
    )
    
    # Power tier based on spell level
    if spell_level <= 2:
        power_tier = "low"
    elif spell_level <= 5:
        power_tier = "standard"
    elif spell_level <= 8:
        power_tier = "high"
    else:
        power_tier = "epic"
    
    return BalanceMetrics(
        overall_score=overall_score,
        power_level=power_score,
        utility_score=utility_score,
        versatility_score=versatility_score,
        scaling_score=scaling_score,
        content_type=ContentType.SPELL,
        power_level_tier=power_tier,
        calculation_method="spell_specific",
        level_range=(spell_level, 20)
    )


def _create_feat_balance_metrics(content_data: Dict[str, Any], level: int) -> BalanceMetrics:
    """Create balance metrics specific to feats."""
    prerequisites = content_data.get("prerequisites", [])
    benefits = content_data.get("benefits", [])
    asi_bonus = content_data.get("ability_score_increase", {})
    
    # Power based on benefits and ASI
    asi_power = sum(asi_bonus.values()) / 2 if asi_bonus else 0  # ASI worth less in feats
    benefit_power = len(benefits) / 3  # Up to 3 benefits for max power
    power_score = min(1.0, asi_power + benefit_power)
    
    # Utility based on out-of-combat benefits
    utility_keywords = ["skill", "tool", "language", "proficiency"]
    utility_benefits = sum(1 for benefit in benefits 
                          if any(keyword in str(benefit).lower() for keyword in utility_keywords))
    utility_score = min(1.0, utility_benefits / 2)
    
    # Versatility based on situational benefits
    versatility_score = min(1.0, len(benefits) / 4)
    
    # Feats generally don't scale much
    scaling_score = 0.2
    
    overall_score = calculate_overall_balance_score(
        power_score, utility_score, versatility_score, scaling_score
    )
    
    # Power tier based on prerequisites and impact
    power_tier = "standard"
    if len(prerequisites) >= 2 or len(benefits) >= 4:
        power_tier = "high"
    elif not prerequisites and len(benefits) <= 1:
        power_tier = "low"
    
    return BalanceMetrics(
        overall_score=overall_score,
        power_level=power_score,
        utility_score=utility_score,
        versatility_score=versatility_score,
        scaling_score=scaling_score,
        content_type=ContentType.FEAT,
        power_level_tier=power_tier,
        calculation_method="feat_specific"
    )


def _create_generic_balance_metrics(
    content_data: Dict[str, Any], 
    content_type: ContentType, 
    level: int
) -> BalanceMetrics:
    """Create generic balance metrics for any content type."""
    # Generic scoring based on common attributes
    power_score = 0.5  # Default to balanced
    utility_score = 0.5
    versatility_score = 0.5
    scaling_score = 0.5
    
    # Try to extract common balance indicators
    content_str = str(content_data).lower()
    
    if any(word in content_str for word in ["damage", "attack", "combat"]):
        power_score = min(1.0, power_score + 0.2)
    if any(word in content_str for word in ["utility", "skill", "tool", "proficiency"]):
        utility_score = min(1.0, utility_score + 0.2)
    if any(word in content_str for word in ["choice", "option", "versatile", "flexible"]):
        versatility_score = min(1.0, versatility_score + 0.2)
    if any(word in content_str for word in ["level", "scale", "improve"]):
        scaling_score = min(1.0, scaling_score + 0.2)
    
    overall_score = calculate_overall_balance_score(
        power_score, utility_score, versatility_score, scaling_score
    )
    
    return BalanceMetrics(
        overall_score=overall_score,
        power_level=power_score,
        utility_score=utility_score,
        versatility_score=versatility_score,
        scaling_score=scaling_score,
        content_type=content_type,
        power_level_tier="standard",
        calculation_method="generic"
    )


# === CLASS BALANCE HELPER FUNCTIONS ===

def _calculate_class_power_score(
    hit_die: int, 
    class_features: Dict[str, Any], 
    spellcasting: Dict[str, Any], 
    level: int
) -> float:
    """Calculate power score for a character class."""
    # Base score from hit die (d6=0.5, d8=0.67, d10=0.83, d12=1.0)
    hit_die_score = hit_die / 12
    
    # Combat features score
    combat_keywords = ["attack", "damage", "weapon", "fighting"]
    combat_features = sum(1 for feature_name in class_features.keys() 
                         if any(keyword in feature_name.lower() for keyword in combat_keywords))
    combat_score = min(1.0, combat_features / 3)
    
    # Spellcasting score
    spell_score = 0.0
    if spellcasting:
        spell_type = spellcasting.get("type", "").lower()
        if spell_type == "full":
            spell_score = 0.8
        elif spell_type in ["half", "half-caster"]:
            spell_score = 0.4
        elif spell_type in ["third", "one-third"]:
            spell_score = 0.3
        elif spell_type in ["warlock", "pact"]:
            spell_score = 0.6
    
    return (hit_die_score * 0.3 + combat_score * 0.4 + spell_score * 0.3)


def _calculate_class_utility_score(proficiencies: Dict[str, Any], class_features: Dict[str, Any]) -> float:
    """Calculate utility score for a character class."""
    skill_count = len(proficiencies.get("skills", []))
    tool_count = len(proficiencies.get("tools", []))
    
    # Count utility-focused features
    utility_keywords = ["skill", "proficiency", "expertise", "tool", "language"]
    utility_features = sum(1 for feature_name in class_features.keys() 
                          if any(keyword in feature_name.lower() for keyword in utility_keywords))
    
    skill_score = min(1.0, skill_count / 4)  # Up to 4 skills
    tool_score = min(1.0, tool_count / 3)   # Up to 3 tools
    feature_score = min(1.0, utility_features / 3)  # Up to 3 utility features
    
    return (skill_score * 0.4 + tool_score * 0.2 + feature_score * 0.4)


def _calculate_class_versatility_score(
    class_features: Dict[str, Any], 
    spellcasting: Dict[str, Any], 
    subclass_count: int
) -> float:
    """Calculate versatility score for a character class."""
    # Count choice-based features
    choice_keywords = ["choice", "option", "select", "choose"]
    choice_features = sum(1 for feature_name in class_features.keys() 
                         if any(keyword in feature_name.lower() for keyword in choice_keywords))
    choice_score = min(1.0, choice_features / 3)
    
    # Spellcasting versatility
    spell_versatility = 0.0
    if spellcasting:
        spells_known = spellcasting.get("spells_known", [])
        if isinstance(spells_known, list):
            spell_versatility = min(1.0, len(spells_known) / 20)
        elif spellcasting.get("type") == "prepared":
            spell_versatility = 0.8  # Prepared casters are very versatile
    
    # Subclass variety
    subclass_score = min(1.0, subclass_count / 5)  # Up to 5 subclasses for max score
    
    return (choice_score * 0.4 + spell_versatility * 0.4 + subclass_score * 0.2)


def _calculate_class_scaling_score(class_features: Dict[str, Any]) -> float:
    """Calculate scaling score for a character class."""
    # Count features that improve with level
    scaling_keywords = ["level", "scale", "improve", "increase", "additional"]
    scaling_features = 0
    
    for feature_name, feature_data in class_features.items():
        if any(keyword in feature_name.lower() for keyword in scaling_keywords):
            scaling_features += 1
        elif isinstance(feature_data, dict) and any(keyword in str(feature_data).lower() 
                                                   for keyword in scaling_keywords):
            scaling_features += 1
    
    return min(1.0, scaling_features / 5)  # Up to 5 scaling features for max score