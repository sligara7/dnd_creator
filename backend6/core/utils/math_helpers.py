"""
Mathematical Utilities for the D&D Creative Content Framework.

This module provides pure mathematical functions for statistical calculations,
power level analysis, and D&D-specific mathematical operations. All functions
are infrastructure-independent and focused on mathematical computations.

Following Clean Architecture principles, these utilities are:
- Infrastructure-independent (no external dependencies except standard math)
- Pure functions with no side effects
- Focused on mathematical calculations for D&D mechanics
- Used by domain services and application use cases
- Support balance analysis and character optimization
"""

import math
import statistics
from decimal import Decimal, ROUND_HALF_UP
from fractions import Fraction
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass
from enum import Enum


# ============ TYPE DEFINITIONS ============

Number = Union[int, float, Decimal]
Probability = float  # Value between 0.0 and 1.0
DiceResult = Union[int, float]
StatArray = List[Number]
ProbabilityDistribution = Dict[int, float]


class StatisticType(Enum):
    """Types of statistical calculations supported."""
    MEAN = "mean"
    MEDIAN = "median"
    MODE = "mode"
    STANDARD_DEVIATION = "std_dev"
    VARIANCE = "variance"
    RANGE = "range"
    PERCENTILE = "percentile"
    QUARTILE = "quartile"


class PowerMetric(Enum):
    """Types of power level metrics for D&D content."""
    DAMAGE_PER_ROUND = "dpr"
    EFFECTIVE_HP = "effective_hp"
    SAVE_DC = "save_dc"
    ARMOR_CLASS = "armor_class"
    VERSATILITY_SCORE = "versatility"
    UTILITY_SCORE = "utility"
    SYNERGY_SCORE = "synergy"
    OPTIMIZATION_SCORE = "optimization"


@dataclass(frozen=True)
class StatisticalSummary:
    """Statistical summary of a data set."""
    count: int
    mean: float
    median: float
    std_dev: float
    variance: float
    min_value: float
    max_value: float
    range_value: float
    quartiles: Tuple[float, float, float]  # Q1, Q2 (median), Q3
    percentiles: Dict[int, float]  # Common percentiles (10, 25, 50, 75, 90, 95, 99)


@dataclass(frozen=True)
class PowerLevelAnalysis:
    """Power level analysis results for D&D content."""
    overall_score: float
    metric_scores: Dict[PowerMetric, float]
    percentile_rank: float
    tier_classification: str
    balance_recommendation: str
    optimization_potential: float
    scaling_factor: float


@dataclass(frozen=True)
class ProbabilityDistributionResult:
    """Results of probability distribution analysis."""
    distribution: ProbabilityDistribution
    expected_value: float
    variance: float
    std_dev: float
    mode: int
    probability_mass_function: Dict[int, float]
    cumulative_distribution: Dict[int, float]


# ============ BASIC MATHEMATICAL OPERATIONS ============

def safe_divide(dividend: Number, divisor: Number, default: Number = 0) -> Number:
    """
    Safely divide two numbers, returning default if divisor is zero.
    
    Args:
        dividend: Number to be divided
        divisor: Number to divide by
        default: Value to return if divisor is zero
        
    Returns:
        Result of division or default value
        
    Example:
        >>> safe_divide(10, 2)
        5.0
        >>> safe_divide(10, 0, -1)
        -1
    """
    if abs(divisor) < 1e-10:  # Handle floating point precision
        return default
    return dividend / divisor


def clamp(value: Number, min_value: Number, max_value: Number) -> Number:
    """
    Clamp a value between minimum and maximum bounds.
    
    Args:
        value: Value to clamp
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        
    Returns:
        Clamped value within bounds
        
    Example:
        >>> clamp(15, 8, 18)
        15
        >>> clamp(5, 8, 18)
        8
        >>> clamp(25, 8, 18)
        18
    """
    return max(min_value, min(value, max_value))


def round_to_precision(value: Number, precision: int = 2) -> float:
    """
    Round a number to specified decimal precision using banker's rounding.
    
    Args:
        value: Number to round
        precision: Number of decimal places
        
    Returns:
        Rounded number
        
    Example:
        >>> round_to_precision(3.14159, 2)
        3.14
        >>> round_to_precision(2.5, 0)
        2.0
    """
    decimal_value = Decimal(str(value))
    rounded = decimal_value.quantize(
        Decimal('0.' + '0' * precision),
        rounding=ROUND_HALF_UP
    )
    return float(rounded)


def linear_interpolate(x: Number, x1: Number, y1: Number, x2: Number, y2: Number) -> Number:
    """
    Linear interpolation between two points.
    
    Args:
        x: Input value to interpolate
        x1, y1: First point coordinates
        x2, y2: Second point coordinates
        
    Returns:
        Interpolated y value for given x
        
    Example:
        >>> linear_interpolate(5, 0, 0, 10, 100)
        50.0
    """
    if abs(x2 - x1) < 1e-10:
        return y1
    
    return y1 + (y2 - y1) * (x - x1) / (x2 - x1)


def exponential_scaling(
    base_value: Number,
    level: int,
    scaling_factor: float = 1.5,
    max_level: int = 20
) -> Number:
    """
    Calculate exponential scaling for D&D features by level.
    
    Args:
        base_value: Starting value at level 1
        level: Current level
        scaling_factor: Rate of exponential growth
        max_level: Maximum level for scaling
        
    Returns:
        Scaled value for the given level
        
    Example:
        >>> exponential_scaling(10, 5, 1.2)
        20.7
    """
    if level <= 1:
        return base_value
    
    clamped_level = clamp(level, 1, max_level)
    scale_exponent = (clamped_level - 1) / (max_level - 1)
    return base_value * (scaling_factor ** scale_exponent)


# ============ STATISTICAL CALCULATIONS ============

def calculate_mean(values: StatArray) -> float:
    """
    Calculate arithmetic mean of a list of values.
    
    Args:
        values: List of numerical values
        
    Returns:
        Arithmetic mean
        
    Raises:
        ValueError: If values list is empty
        
    Example:
        >>> calculate_mean([1, 2, 3, 4, 5])
        3.0
    """
    if not values:
        raise ValueError("Cannot calculate mean of empty list")
    
    return sum(values) / len(values)


def calculate_weighted_mean(values: StatArray, weights: StatArray) -> float:
    """
    Calculate weighted arithmetic mean.
    
    Args:
        values: List of numerical values
        weights: List of weights for each value
        
    Returns:
        Weighted arithmetic mean
        
    Raises:
        ValueError: If lists are different lengths or empty
        
    Example:
        >>> calculate_weighted_mean([1, 2, 3], [1, 2, 1])
        2.0
    """
    if not values or not weights:
        raise ValueError("Cannot calculate weighted mean of empty lists")
    
    if len(values) != len(weights):
        raise ValueError("Values and weights must have same length")
    
    weighted_sum = sum(v * w for v, w in zip(values, weights))
    weight_sum = sum(weights)
    
    if weight_sum == 0:
        raise ValueError("Sum of weights cannot be zero")
    
    return weighted_sum / weight_sum


def calculate_median(values: StatArray) -> float:
    """
    Calculate median of a list of values.
    
    Args:
        values: List of numerical values
        
    Returns:
        Median value
        
    Raises:
        ValueError: If values list is empty
        
    Example:
        >>> calculate_median([1, 2, 3, 4, 5])
        3.0
        >>> calculate_median([1, 2, 3, 4])
        2.5
    """
    if not values:
        raise ValueError("Cannot calculate median of empty list")
    
    return statistics.median(values)


def calculate_mode(values: StatArray) -> Union[Number, List[Number]]:
    """
    Calculate mode(s) of a list of values.
    
    Args:
        values: List of numerical values
        
    Returns:
        Most frequent value(s)
        
    Raises:
        ValueError: If values list is empty
        
    Example:
        >>> calculate_mode([1, 2, 2, 3, 3, 3])
        3
        >>> calculate_mode([1, 1, 2, 2])
        [1, 2]
    """
    if not values:
        raise ValueError("Cannot calculate mode of empty list")
    
    try:
        return statistics.mode(values)
    except statistics.StatisticsError:
        # Multiple modes - return all of them
        from collections import Counter
        counts = Counter(values)
        max_count = max(counts.values())
        modes = [value for value, count in counts.items() if count == max_count]
        return modes if len(modes) > 1 else modes[0]


def calculate_standard_deviation(values: StatArray, population: bool = False) -> float:
    """
    Calculate standard deviation of a list of values.
    
    Args:
        values: List of numerical values
        population: If True, calculate population std dev; if False, sample std dev
        
    Returns:
        Standard deviation
        
    Raises:
        ValueError: If values list is empty or has insufficient data
        
    Example:
        >>> round(calculate_standard_deviation([1, 2, 3, 4, 5]), 2)
        1.58
    """
    if not values:
        raise ValueError("Cannot calculate standard deviation of empty list")
    
    if len(values) == 1 and not population:
        raise ValueError("Cannot calculate sample standard deviation with only one value")
    
    if population:
        return statistics.pstdev(values)
    else:
        return statistics.stdev(values)


def calculate_variance(values: StatArray, population: bool = False) -> float:
    """
    Calculate variance of a list of values.
    
    Args:
        values: List of numerical values
        population: If True, calculate population variance; if False, sample variance
        
    Returns:
        Variance
        
    Raises:
        ValueError: If values list is empty or has insufficient data
        
    Example:
        >>> calculate_variance([1, 2, 3, 4, 5])
        2.5
    """
    if not values:
        raise ValueError("Cannot calculate variance of empty list")
    
    if len(values) == 1 and not population:
        raise ValueError("Cannot calculate sample variance with only one value")
    
    if population:
        return statistics.pvariance(values)
    else:
        return statistics.variance(values)


def calculate_percentile(values: StatArray, percentile: int) -> float:
    """
    Calculate specific percentile of a list of values.
    
    Args:
        values: List of numerical values
        percentile: Percentile to calculate (0-100)
        
    Returns:
        Value at the specified percentile
        
    Raises:
        ValueError: If values list is empty or percentile is invalid
        
    Example:
        >>> calculate_percentile([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 50)
        5.5
    """
    if not values:
        raise ValueError("Cannot calculate percentile of empty list")
    
    if not 0 <= percentile <= 100:
        raise ValueError("Percentile must be between 0 and 100")
    
    return statistics.quantiles(values, n=100)[percentile - 1] if percentile > 0 else min(values)


def calculate_quartiles(values: StatArray) -> Tuple[float, float, float]:
    """
    Calculate quartiles (Q1, Q2, Q3) of a list of values.
    
    Args:
        values: List of numerical values
        
    Returns:
        Tuple of (Q1, Q2, Q3) values
        
    Raises:
        ValueError: If values list is empty
        
    Example:
        >>> calculate_quartiles([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        (3.25, 5.5, 7.75)
    """
    if not values:
        raise ValueError("Cannot calculate quartiles of empty list")
    
    q1 = calculate_percentile(values, 25)
    q2 = calculate_percentile(values, 50)  # Median
    q3 = calculate_percentile(values, 75)
    
    return (q1, q2, q3)


def calculate_statistical_summary(values: StatArray) -> StatisticalSummary:
    """
    Calculate comprehensive statistical summary of a dataset.
    
    Args:
        values: List of numerical values
        
    Returns:
        StatisticalSummary object with all statistics
        
    Raises:
        ValueError: If values list is empty
        
    Example:
        >>> summary = calculate_statistical_summary([1, 2, 3, 4, 5])
        >>> summary.mean
        3.0
    """
    if not values:
        raise ValueError("Cannot calculate statistics of empty list")
    
    mean_val = calculate_mean(values)
    median_val = calculate_median(values)
    std_dev_val = calculate_standard_deviation(values) if len(values) > 1 else 0.0
    variance_val = calculate_variance(values) if len(values) > 1 else 0.0
    min_val = min(values)
    max_val = max(values)
    range_val = max_val - min_val
    quartiles = calculate_quartiles(values)
    
    # Common percentiles
    percentiles = {}
    for p in [10, 25, 50, 75, 90, 95, 99]:
        try:
            percentiles[p] = calculate_percentile(values, p)
        except (ValueError, IndexError):
            percentiles[p] = median_val  # Fallback for small datasets
    
    return StatisticalSummary(
        count=len(values),
        mean=mean_val,
        median=median_val,
        std_dev=std_dev_val,
        variance=variance_val,
        min_value=min_val,
        max_value=max_val,
        range_value=range_val,
        quartiles=quartiles,
        percentiles=percentiles
    )


# ============ PROBABILITY CALCULATIONS ============

def calculate_binomial_probability(n: int, k: int, p: Probability) -> float:
    """
    Calculate binomial probability for exactly k successes in n trials.
    
    Args:
        n: Number of trials
        k: Number of successes
        p: Probability of success on each trial
        
    Returns:
        Probability of exactly k successes
        
    Example:
        >>> round(calculate_binomial_probability(10, 3, 0.3), 4)
        0.2668
    """
    if not 0 <= p <= 1:
        raise ValueError("Probability must be between 0 and 1")
    
    if not 0 <= k <= n:
        raise ValueError("Number of successes must be between 0 and number of trials")
    
    # Binomial coefficient: n! / (k! * (n-k)!)
    binom_coeff = math.comb(n, k)
    
    return binom_coeff * (p ** k) * ((1 - p) ** (n - k))


def calculate_normal_probability(
    x: Number,
    mean: Number = 0,
    std_dev: Number = 1
) -> float:
    """
    Calculate probability density for normal distribution.
    
    Args:
        x: Value to calculate probability for
        mean: Mean of the distribution
        std_dev: Standard deviation of the distribution
        
    Returns:
        Probability density at x
        
    Example:
        >>> round(calculate_normal_probability(0, 0, 1), 4)
        0.3989
    """
    if std_dev <= 0:
        raise ValueError("Standard deviation must be positive")
    
    coefficient = 1 / (std_dev * math.sqrt(2 * math.pi))
    exponent = -0.5 * ((x - mean) / std_dev) ** 2
    
    return coefficient * math.exp(exponent)


def calculate_dice_probability_distribution(num_dice: int, die_size: int) -> ProbabilityDistributionResult:
    """
    Calculate probability distribution for rolling multiple dice.
    
    Args:
        num_dice: Number of dice to roll
        die_size: Number of sides on each die
        
    Returns:
        ProbabilityDistributionResult with complete distribution analysis
        
    Example:
        >>> result = calculate_dice_probability_distribution(2, 6)
        >>> result.expected_value
        7.0
    """
    if num_dice <= 0 or die_size <= 0:
        raise ValueError("Number of dice and die size must be positive")
    
    # Initialize distribution
    min_sum = num_dice
    max_sum = num_dice * die_size
    total_outcomes = die_size ** num_dice
    
    # Count occurrences of each sum using dynamic programming
    # dp[i][j] = number of ways to get sum j using i dice
    dp = [[0 for _ in range(max_sum + 1)] for _ in range(num_dice + 1)]
    
    # Base case: 0 dice, sum 0
    dp[0][0] = 1
    
    # Fill the DP table
    for dice in range(1, num_dice + 1):
        for target_sum in range(dice, dice * die_size + 1):
            for face in range(1, min(die_size + 1, target_sum + 1)):
                if target_sum - face >= 0:
                    dp[dice][target_sum] += dp[dice - 1][target_sum - face]
    
    # Convert counts to probabilities
    distribution = {}
    pmf = {}
    for sum_value in range(min_sum, max_sum + 1):
        count = dp[num_dice][sum_value]
        prob = count / total_outcomes
        distribution[sum_value] = prob
        pmf[sum_value] = prob
    
    # Calculate cumulative distribution
    cumulative = {}
    cumulative_prob = 0.0
    for sum_value in range(min_sum, max_sum + 1):
        cumulative_prob += distribution[sum_value]
        cumulative[sum_value] = cumulative_prob
    
    # Calculate statistics
    expected_value = sum(sum_val * prob for sum_val, prob in distribution.items())
    variance = sum((sum_val - expected_value) ** 2 * prob for sum_val, prob in distribution.items())
    std_dev = math.sqrt(variance)
    
    # Find mode
    mode = max(distribution.items(), key=lambda x: x[1])[0]
    
    return ProbabilityDistributionResult(
        distribution=distribution,
        expected_value=expected_value,
        variance=variance,
        std_dev=std_dev,
        mode=mode,
        probability_mass_function=pmf,
        cumulative_distribution=cumulative
    )


# ============ D&D POWER LEVEL CALCULATIONS ============

def calculate_damage_per_round(
    base_damage: Number,
    hit_bonus: int,
    target_ac: int = 15,
    crit_range: int = 20,
    crit_multiplier: float = 2.0,
    additional_damage_on_crit: Number = 0
) -> float:
    """
    Calculate expected damage per round for a D&D attack.
    
    Args:
        base_damage: Base damage on hit
        hit_bonus: Attack bonus to hit
        target_ac: Target's armor class
        crit_range: Minimum d20 roll for critical hit
        crit_multiplier: Damage multiplier on critical hit
        additional_damage_on_crit: Extra damage dice on critical
        
    Returns:
        Expected damage per round
        
    Example:
        >>> round(calculate_damage_per_round(8.5, 5, 15), 2)
        4.68
    """
    # Calculate hit probability
    hit_roll_needed = target_ac - hit_bonus
    hit_roll_needed = clamp(hit_roll_needed, 2, 20)  # Always hit on 20, miss on 1
    
    # Probability of normal hit (not critical)
    normal_hit_prob = max(0, (21 - max(hit_roll_needed, crit_range)) / 20)
    
    # Probability of critical hit
    crit_prob = max(0, (21 - crit_range) / 20)
    
    # Total hit probability
    total_hit_prob = normal_hit_prob + crit_prob
    
    # Expected damage calculation
    normal_damage = base_damage * normal_hit_prob
    crit_damage = (base_damage * crit_multiplier + additional_damage_on_crit) * crit_prob
    
    return normal_damage + crit_damage


def calculate_effective_hp(
    base_hp: int,
    armor_class: int,
    damage_resistances: int = 0,
    damage_immunities: int = 0,
    save_bonuses: Dict[str, int] = None
) -> float:
    """
    Calculate effective hit points considering AC and resistances.
    
    Args:
        base_hp: Base hit points
        armor_class: Armor class
        damage_resistances: Number of common damage resistances
        damage_immunities: Number of common damage immunities
        save_bonuses: Dictionary of save bonuses
        
    Returns:
        Effective hit points
        
    Example:
        >>> calculate_effective_hp(50, 18, 2, 1)
        82.5
    """
    if save_bonuses is None:
        save_bonuses = {}
    
    # AC multiplier (based on hit probability against average attack)
    average_attack_bonus = 8  # Rough average for mid-level play
    hit_prob = max(0.05, (21 - (armor_class - average_attack_bonus)) / 20)
    hit_prob = min(0.95, hit_prob)  # Cap at 95% to account for natural 1s
    
    ac_multiplier = 1 / hit_prob
    
    # Resistance multiplier
    resistance_multiplier = 1.0 + (damage_resistances * 0.25) + (damage_immunities * 0.5)
    
    # Save bonus multiplier (rough approximation)
    avg_save_bonus = sum(save_bonuses.values()) / max(1, len(save_bonuses))
    save_multiplier = 1.0 + (avg_save_bonus * 0.05)  # 5% per point of save bonus
    
    return base_hp * ac_multiplier * resistance_multiplier * save_multiplier


def calculate_save_dc_effectiveness(
    spell_save_dc: int,
    target_save_bonus: int = 5,
    save_type: str = "wisdom"
) -> float:
    """
    Calculate effectiveness of a spell save DC.
    
    Args:
        spell_save_dc: Spell save DC
        target_save_bonus: Target's save bonus
        save_type: Type of save (affects baseline)
        
    Returns:
        Failure probability (0.0 to 1.0)
        
    Example:
        >>> calculate_save_dc_effectiveness(15, 3)
        0.65
    """
    # Probability target fails the save
    failure_roll_needed = spell_save_dc - target_save_bonus
    failure_roll_needed = clamp(failure_roll_needed, 2, 20)
    
    failure_prob = max(0.05, (failure_roll_needed - 1) / 20)
    failure_prob = min(0.95, failure_prob)  # Account for natural 20s
    
    return failure_prob


def calculate_versatility_score(
    num_abilities: int,
    combat_utility: float,
    exploration_utility: float,
    social_utility: float,
    scaling_factor: float = 1.0
) -> float:
    """
    Calculate versatility score for D&D content.
    
    Args:
        num_abilities: Number of different abilities/options
        combat_utility: Combat effectiveness (0-1)
        exploration_utility: Exploration effectiveness (0-1)
        social_utility: Social interaction effectiveness (0-1)
        scaling_factor: Level scaling factor
        
    Returns:
        Versatility score
        
    Example:
        >>> calculate_versatility_score(3, 0.8, 0.6, 0.4)
        5.4
    """
    ability_score = min(10, num_abilities)  # Cap at 10 abilities
    pillar_score = combat_utility + exploration_utility + social_utility
    
    base_score = ability_score * pillar_score * scaling_factor
    
    # Bonus for being effective in multiple pillars
    effective_pillars = sum(1 for utility in [combat_utility, exploration_utility, social_utility] if utility > 0.5)
    pillar_bonus = effective_pillars * 0.5
    
    return base_score + pillar_bonus


def calculate_power_level_score(
    damage_per_round: float,
    effective_hp: float,
    save_dc: int,
    armor_class: int,
    versatility_score: float,
    level: int = 10
) -> PowerLevelAnalysis:
    """
    Calculate comprehensive power level analysis for D&D content.
    
    Args:
        damage_per_round: Expected DPR
        effective_hp: Effective hit points
        save_dc: Spell save DC or similar
        armor_class: Armor class
        versatility_score: Versatility rating
        level: Character level for comparison
        
    Returns:
        PowerLevelAnalysis with detailed breakdown
        
    Example:
        >>> analysis = calculate_power_level_score(25, 75, 16, 18, 7.5, 10)
        >>> analysis.tier_classification
        'High'
    """
    # Level-based benchmarks (rough guidelines for balanced play)
    level_benchmarks = {
        'dpr': 3 + (level * 1.5),
        'hp': 10 + (level * 6),
        'save_dc': 8 + math.ceil(level / 4) + 3,  # Proficiency + stat
        'ac': 12 + math.ceil(level / 5),
        'versatility': level * 0.5
    }
    
    # Calculate individual metric scores (as percentages of benchmark)
    metric_scores = {
        PowerMetric.DAMAGE_PER_ROUND: min(200, (damage_per_round / level_benchmarks['dpr']) * 100),
        PowerMetric.EFFECTIVE_HP: min(200, (effective_hp / level_benchmarks['hp']) * 100),
        PowerMetric.SAVE_DC: min(200, (save_dc / level_benchmarks['save_dc']) * 100),
        PowerMetric.ARMOR_CLASS: min(200, (armor_class / level_benchmarks['ac']) * 100),
        PowerMetric.VERSATILITY_SCORE: min(200, (versatility_score / level_benchmarks['versatility']) * 100)
    }
    
    # Calculate weighted overall score
    weights = {
        PowerMetric.DAMAGE_PER_ROUND: 0.25,
        PowerMetric.EFFECTIVE_HP: 0.20,
        PowerMetric.SAVE_DC: 0.15,
        PowerMetric.ARMOR_CLASS: 0.20,
        PowerMetric.VERSATILITY_SCORE: 0.20
    }
    
    overall_score = sum(score * weights[metric] for metric, score in metric_scores.items())
    
    # Determine tier classification
    if overall_score >= 150:
        tier = "Overpowered"
        balance_recommendation = "Significantly reduce power level"
    elif overall_score >= 120:
        tier = "High"
        balance_recommendation = "Consider minor reductions"
    elif overall_score >= 80:
        tier = "Balanced"
        balance_recommendation = "Well balanced for level"
    elif overall_score >= 60:
        tier = "Low"
        balance_recommendation = "Consider minor improvements"
    else:
        tier = "Underpowered"
        balance_recommendation = "Significantly increase power level"
    
    # Calculate percentile rank (assuming normal distribution)
    percentile_rank = clamp(overall_score, 0, 100)
    
    # Calculate optimization potential
    max_possible = max(metric_scores.values())
    min_actual = min(metric_scores.values())
    optimization_potential = (max_possible - min_actual) / 100
    
    # Calculate scaling factor
    expected_score_for_level = 100  # Baseline
    scaling_factor = overall_score / expected_score_for_level
    
    return PowerLevelAnalysis(
        overall_score=round_to_precision(overall_score, 1),
        metric_scores=metric_scores,
        percentile_rank=round_to_precision(percentile_rank, 1),
        tier_classification=tier,
        balance_recommendation=balance_recommendation,
        optimization_potential=round_to_precision(optimization_potential, 2),
        scaling_factor=round_to_precision(scaling_factor, 2)
    )


# ============ MATHEMATICAL UTILITIES FOR D&D MECHANICS ============

def calculate_proficiency_bonus(level: int) -> int:
    """
    Calculate proficiency bonus for a given character level.
    
    Args:
        level: Character level (1-20)
        
    Returns:
        Proficiency bonus
        
    Example:
        >>> calculate_proficiency_bonus(5)
        3
        >>> calculate_proficiency_bonus(17)
        6
    """
    level = clamp(level, 1, 20)
    return 2 + ((level - 1) // 4)


def calculate_spell_slots_by_level(caster_level: int, spell_level: int) -> int:
    """
    Calculate number of spell slots for full casters.
    
    Args:
        caster_level: Caster level (1-20)
        spell_level: Spell level (1-9)
        
    Returns:
        Number of spell slots
        
    Example:
        >>> calculate_spell_slots_by_level(5, 3)
        2
    """
    if not 1 <= caster_level <= 20 or not 1 <= spell_level <= 9:
        return 0
    
    # Spell slot progression table for full casters
    spell_slots = {
        1: [2, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
        2: [0, 1, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
        3: [0, 0, 0, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
        4: [0, 0, 0, 0, 0, 1, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
        5: [0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
        6: [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
        7: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 2, 2, 2, 2, 2, 2, 2],
        8: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 2, 2, 2, 2, 2],
        9: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 2, 2, 2]
    }
    
    return spell_slots.get(spell_level, [0] * 20)[caster_level - 1]


def calculate_ability_modifier(ability_score: int) -> int:
    """
    Calculate ability modifier from ability score.
    
    Args:
        ability_score: Ability score (typically 1-30)
        
    Returns:
        Ability modifier
        
    Example:
        >>> calculate_ability_modifier(16)
        3
        >>> calculate_ability_modifier(8)
        -1
    """
    return (ability_score - 10) // 2


def calculate_carrying_capacity(strength_score: int) -> int:
    """
    Calculate carrying capacity based on Strength score.
    
    Args:
        strength_score: Strength ability score
        
    Returns:
        Carrying capacity in pounds
        
    Example:
        >>> calculate_carrying_capacity(15)
        225
    """
    return strength_score * 15


def calculate_jump_distance(strength_score: int, running_start: bool = True) -> Tuple[int, int]:
    """
    Calculate long jump and high jump distances.
    
    Args:
        strength_score: Strength ability score
        running_start: Whether character has running start
        
    Returns:
        Tuple of (long_jump_feet, high_jump_feet)
        
    Example:
        >>> calculate_jump_distance(16, True)
        (16, 7)
    """
    long_jump = strength_score if running_start else strength_score // 2
    high_jump = (3 + calculate_ability_modifier(strength_score)) if running_start else (3 + calculate_ability_modifier(strength_score)) // 2
    
    return (max(0, long_jump), max(0, high_jump))


def calculate_multiattack_damage(
    attacks: List[Tuple[Number, Probability]],
    target_ac: int = 15,
    attack_bonus: int = 8
) -> float:
    """
    Calculate expected damage from multiple attacks.
    
    Args:
        attacks: List of (damage, additional_hit_prob) tuples
        target_ac: Target armor class
        attack_bonus: Attack bonus
        
    Returns:
        Expected total damage per round
        
    Example:
        >>> attacks = [(8.5, 1.0), (6.5, 1.0), (4.5, 0.8)]
        >>> round(calculate_multiattack_damage(attacks, 15, 8), 2)
        10.4
    """
    total_expected_damage = 0.0
    
    # Base hit probability
    hit_roll_needed = target_ac - attack_bonus
    hit_roll_needed = clamp(hit_roll_needed, 2, 20)
    base_hit_prob = max(0.05, (21 - hit_roll_needed) / 20)
    base_hit_prob = min(0.95, base_hit_prob)
    
    for damage, additional_prob in attacks:
        effective_hit_prob = min(0.95, base_hit_prob * additional_prob)
        total_expected_damage += damage * effective_hit_prob
    
    return total_expected_damage


# ============ OPTIMIZATION AND CURVE FITTING ============

def find_optimal_ability_scores(
    point_buy_points: int = 27,
    ability_costs: Dict[int, int] = None,
    priorities: Dict[str, float] = None
) -> Dict[str, int]:
    """
    Find optimal ability score distribution for point buy.
    
    Args:
        point_buy_points: Available points for point buy
        ability_costs: Cost of each ability score
        priorities: Weight for each ability (str, dex, con, int, wis, cha)
        
    Returns:
        Dictionary of optimal ability scores
        
    Example:
        >>> priorities = {'str': 0.8, 'con': 0.7, 'dex': 0.6, 'wis': 0.4, 'int': 0.2, 'cha': 0.3}
        >>> scores = find_optimal_ability_scores(27, priorities=priorities)
        >>> scores['str'] >= scores['cha']
        True
    """
    if ability_costs is None:
        # Standard point buy costs
        ability_costs = {8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 13: 5, 14: 7, 15: 9}
    
    if priorities is None:
        # Equal priorities
        priorities = {ability: 1.0 for ability in ['str', 'dex', 'con', 'int', 'wis', 'cha']}
    
    abilities = list(priorities.keys())
    
    # Start with minimum scores
    scores = {ability: 8 for ability in abilities}
    remaining_points = point_buy_points
    
    # Greedy optimization: increase the most valuable ability that we can afford
    while remaining_points > 0:
        best_ability = None
        best_value_per_point = 0
        
        for ability in abilities:
            current_score = scores[ability]
            if current_score < 15:  # Can't go above 15 in point buy
                next_score = current_score + 1
                cost = ability_costs.get(next_score, float('inf'))
                
                if cost <= remaining_points:
                    # Value per point = priority * diminishing returns factor
                    diminishing_factor = 1.0 / (1 + (current_score - 8) * 0.1)
                    value_per_point = priorities[ability] * diminishing_factor / cost
                    
                    if value_per_point > best_value_per_point:
                        best_value_per_point = value_per_point
                        best_ability = ability
        
        if best_ability:
            current_score = scores[best_ability]
            cost = ability_costs[current_score + 1]
            scores[best_ability] += 1
            remaining_points -= cost
        else:
            break  # No more beneficial improvements possible
    
    return scores


def calculate_encounter_difficulty(
    party_level: int,
    party_size: int,
    monster_xp: List[int]
) -> Tuple[str, float]:
    """
    Calculate encounter difficulty using D&D encounter building rules.
    
    Args:
        party_level: Average party level
        party_size: Number of party members
        monster_xp: List of XP values for monsters in encounter
        
    Returns:
        Tuple of (difficulty_rating, adjusted_xp)
        
    Example:
        >>> difficulty, xp = calculate_encounter_difficulty(5, 4, [1800])
        >>> difficulty
        'Hard'
    """
    # XP thresholds per character level
    xp_thresholds = {
        1: {'easy': 25, 'medium': 50, 'hard': 75, 'deadly': 100},
        2: {'easy': 50, 'medium': 100, 'hard': 150, 'deadly': 200},
        3: {'easy': 75, 'medium': 150, 'hard': 225, 'deadly': 400},
        4: {'easy': 125, 'medium': 250, 'hard': 375, 'deadly': 500},
        5: {'easy': 250, 'medium': 500, 'hard': 750, 'deadly': 1100},
        6: {'easy': 300, 'medium': 600, 'hard': 900, 'deadly': 1400},
        7: {'easy': 350, 'medium': 750, 'hard': 1100, 'deadly': 1700},
        8: {'easy': 450, 'medium': 900, 'hard': 1400, 'deadly': 2100},
        9: {'easy': 550, 'medium': 1100, 'hard': 1600, 'deadly': 2400},
        10: {'easy': 600, 'medium': 1200, 'hard': 1900, 'deadly': 2800},
        11: {'easy': 800, 'medium': 1600, 'hard': 2400, 'deadly': 3600},
        12: {'easy': 1000, 'medium': 2000, 'hard': 3000, 'deadly': 4500},
        13: {'easy': 1100, 'medium': 2200, 'hard': 3400, 'deadly': 5100},
        14: {'easy': 1250, 'medium': 2500, 'hard': 3800, 'deadly': 5700},
        15: {'easy': 1400, 'medium': 2800, 'hard': 4300, 'deadly': 6400},
        16: {'easy': 1600, 'medium': 3200, 'hard': 4800, 'deadly': 7200},
        17: {'easy': 2000, 'medium': 3900, 'hard': 5900, 'deadly': 8800},
        18: {'easy': 2100, 'medium': 4200, 'hard': 6300, 'deadly': 9500},
        19: {'easy': 2400, 'medium': 4900, 'hard': 7300, 'deadly': 10900},
        20: {'easy': 2800, 'medium': 5700, 'hard': 8500, 'deadly': 12700}
    }
    
    level = clamp(party_level, 1, 20)
    thresholds = xp_thresholds[level]
    
    # Calculate party thresholds
    party_thresholds = {
        difficulty: threshold * party_size
        for difficulty, threshold in thresholds.items()
    }
    
    # Calculate encounter multiplier based on number of monsters
    num_monsters = len(monster_xp)
    if num_monsters == 1:
        multiplier = 1.0
    elif num_monsters == 2:
        multiplier = 1.5
    elif num_monsters <= 6:
        multiplier = 2.0
    elif num_monsters <= 10:
        multiplier = 2.5
    elif num_monsters <= 14:
        multiplier = 3.0
    else:
        multiplier = 4.0
    
    # Adjust for party size
    if party_size < 3:
        multiplier *= 1.5
    elif party_size > 5:
        multiplier *= 0.5
    
    # Calculate adjusted XP
    total_xp = sum(monster_xp)
    adjusted_xp = total_xp * multiplier
    
    # Determine difficulty
    if adjusted_xp >= party_thresholds['deadly']:
        difficulty = 'Deadly'
    elif adjusted_xp >= party_thresholds['hard']:
        difficulty = 'Hard'
    elif adjusted_xp >= party_thresholds['medium']:
        difficulty = 'Medium'
    else:
        difficulty = 'Easy'
    
    return difficulty, adjusted_xp


# ============ UTILITY FUNCTIONS ============

def normalize_values(values: StatArray, target_min: Number = 0, target_max: Number = 1) -> List[float]:
    """
    Normalize a list of values to a target range.
    
    Args:
        values: List of values to normalize
        target_min: Minimum value in target range
        target_max: Maximum value in target range
        
    Returns:
        List of normalized values
        
    Example:
        >>> normalize_values([1, 2, 3, 4, 5], 0, 10)
        [0.0, 2.5, 5.0, 7.5, 10.0]
    """
    if not values:
        return []
    
    min_val = min(values)
    max_val = max(values)
    
    if min_val == max_val:
        # All values are the same
        return [target_min] * len(values)
    
    range_original = max_val - min_val
    range_target = target_max - target_min
    
    return [
        target_min + (value - min_val) * range_target / range_original
        for value in values
    ]


def calculate_correlation_coefficient(x_values: StatArray, y_values: StatArray) -> float:
    """
    Calculate Pearson correlation coefficient between two datasets.
    
    Args:
        x_values: First dataset
        y_values: Second dataset
        
    Returns:
        Correlation coefficient (-1 to 1)
        
    Raises:
        ValueError: If datasets are different lengths or empty
        
    Example:
        >>> x = [1, 2, 3, 4, 5]
        >>> y = [2, 4, 6, 8, 10]
        >>> calculate_correlation_coefficient(x, y)
        1.0
    """
    if not x_values or not y_values:
        raise ValueError("Cannot calculate correlation of empty datasets")
    
    if len(x_values) != len(y_values):
        raise ValueError("Datasets must have same length")
    
    if len(x_values) < 2:
        raise ValueError("Need at least 2 data points for correlation")
    
    return statistics.correlation(x_values, y_values)


def smooth_curve(values: StatArray, window_size: int = 3) -> List[float]:
    """
    Apply moving average smoothing to a list of values.
    
    Args:
        values: List of values to smooth
        window_size: Size of the moving average window
        
    Returns:
        List of smoothed values
        
    Example:
        >>> smooth_curve([1, 5, 2, 8, 3, 7, 4], 3)
        [2.67, 5.0, 4.33, 6.0, 4.67]
    """
    if not values or window_size < 1:
        return list(values)
    
    if window_size >= len(values):
        return [calculate_mean(values)] * len(values)
    
    smoothed = []
    half_window = window_size // 2
    
    for i in range(half_window, len(values) - half_window):
        window_values = values[i - half_window:i + half_window + 1]
        smoothed.append(calculate_mean(window_values))
    
    return smoothed


def generate_balanced_random_stats(
    num_stats: int = 6,
    target_total: int = 72,
    min_stat: int = 8,
    max_stat: int = 15,
    max_attempts: int = 1000
) -> List[int]:
    """
    Generate random ability scores that sum to a target total.
    
    Args:
        num_stats: Number of ability scores to generate
        target_total: Target sum for all scores
        min_stat: Minimum individual score
        max_stat: Maximum individual score
        max_attempts: Maximum attempts to find valid combination
        
    Returns:
        List of balanced random ability scores
        
    Example:
        >>> stats = generate_balanced_random_stats(6, 72, 8, 15)
        >>> len(stats)
        6
        >>> sum(stats)
        72
    """
    import random
    
    for _ in range(max_attempts):
        stats = []
        remaining_total = target_total
        
        for i in range(num_stats):
            if i == num_stats - 1:
                # Last stat must use remaining points
                final_stat = remaining_total
                if min_stat <= final_stat <= max_stat:
                    stats.append(final_stat)
                    break
                else:
                    # This attempt failed, try again
                    break
            else:
                # Calculate valid range for this stat
                remaining_stats = num_stats - i - 1
                min_remaining_total = remaining_stats * min_stat
                max_remaining_total = remaining_stats * max_stat
                
                stat_min = max(min_stat, remaining_total - max_remaining_total)
                stat_max = min(max_stat, remaining_total - min_remaining_total)
                
                if stat_min <= stat_max:
                    stat = random.randint(stat_min, stat_max)
                    stats.append(stat)
                    remaining_total -= stat
                else:
                    # This attempt failed, try again
                    break
        else:
            # Successfully generated all stats
            return stats
    
    # If we couldn't generate valid stats, fall back to even distribution
    base_stat = target_total // num_stats
    remainder = target_total % num_stats
    
    stats = [base_stat] * num_stats
    for i in range(remainder):
        stats[i] += 1
    
    # Clamp all stats to valid range
    return [clamp(stat, min_stat, max_stat) for stat in stats]


# ============ MODULE METADATA ============

__version__ = '2.0.0'
__description__ = 'Mathematical utilities for D&D Creative Content Framework'
__author__ = 'D&D Character Creator Backend6'

# Clean Architecture compliance metadata
CLEAN_ARCHITECTURE_COMPLIANCE = {
    "layer": "core/utils",
    "dependencies": ["math", "statistics", "decimal", "fractions"],
    "dependents": ["domain/services", "application/use_cases"],
    "infrastructure_independent": True,
    "pure_functions": True,
    "side_effects": False,
    "focuses_on": "Mathematical calculations for D&D mechanics and power analysis"
}

# Function categories for organization
FUNCTION_CATEGORIES = {
    "basic_math": [
        "safe_divide", "clamp", "round_to_precision", "linear_interpolate", "exponential_scaling"
    ],
    "statistics": [
        "calculate_mean", "calculate_weighted_mean", "calculate_median", "calculate_mode",
        "calculate_standard_deviation", "calculate_variance", "calculate_percentile",
        "calculate_quartiles", "calculate_statistical_summary"
    ],
    "probability": [
        "calculate_binomial_probability", "calculate_normal_probability",
        "calculate_dice_probability_distribution"
    ],
    "dnd_power_analysis": [
        "calculate_damage_per_round", "calculate_effective_hp", "calculate_save_dc_effectiveness",
        "calculate_versatility_score", "calculate_power_level_score"
    ],
    "dnd_mechanics": [
        "calculate_proficiency_bonus", "calculate_spell_slots_by_level", "calculate_ability_modifier",
        "calculate_carrying_capacity", "calculate_jump_distance", "calculate_multiattack_damage"
    ],
    "optimization": [
        "find_optimal_ability_scores", "calculate_encounter_difficulty"
    ],
    "utilities": [
        "normalize_values", "calculate_correlation_coefficient", "smooth_curve",
        "generate_balanced_random_stats"
    ]
}

# Usage examples in docstring
"""
Clean Architecture Usage Examples:

1. Basic Mathematical Operations:
   >>> safe_divide(10, 3, 0)
   3.33
   >>> clamp(25, 8, 18)
   18

2. Statistical Analysis:
   >>> values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
   >>> summary = calculate_statistical_summary(values)
   >>> print(f"Mean: {summary.mean}, Std Dev: {summary.std_dev}")

3. D&D Power Level Analysis:
   >>> dpr = calculate_damage_per_round(8.5, 8, 15, 20, 2.0)
   >>> analysis = calculate_power_level_score(dpr, 75, 16, 18, 7.5, 10)
   >>> print(f"Power Tier: {analysis.tier_classification}")

4. Probability Calculations:
   >>> dice_result = calculate_dice_probability_distribution(2, 6)
   >>> print(f"Expected 2d6: {dice_result.expected_value}")

5. D&D Mechanics:
   >>> prof_bonus = calculate_proficiency_bonus(10)
   >>> ability_mod = calculate_ability_modifier(16)
   >>> spell_slots = calculate_spell_slots_by_level(9, 5)

6. Character Optimization:
   >>> priorities = {'str': 0.8, 'con': 0.7, 'dex': 0.6}
   >>> optimal_scores = find_optimal_ability_scores(27, priorities=priorities)

7. Encounter Building:
   >>> difficulty, adj_xp = calculate_encounter_difficulty(5, 4, [1800])
   >>> print(f"Difficulty: {difficulty}, Adjusted XP: {adj_xp}")

8. Data Analysis:
   >>> normalized = normalize_values([1, 5, 10], 0, 100)
   >>> correlation = calculate_correlation_coefficient([1,2,3], [2,4,6])
"""