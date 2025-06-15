"""
Dice Notation Parsing and Calculation Utilities for D&D Creative Content Framework.

This module provides pure utility functions for:
- Parsing standard dice notation (1d8+3, 2d6+STR, 3d6kh2, etc.)
- Calculating dice statistics and probabilities with FULL probability distributions
- Handling ability score modifiers in dice expressions
- Supporting D&D-specific dice mechanics (advantage, disadvantage, critical hits)
- Validating and normalizing dice notation strings

Following Clean Architecture principles, these utilities are:
- Infrastructure-independent (no external dependencies)
- Pure functions with no side effects
- Focused on dice mechanics and mathematical calculations
- Used by domain services and application use cases
- Support character creation and combat calculations

FULL PROBABILITY DISTRIBUTION FEATURES:
- Exact calculations for all standard D&D dice combinations
- Dynamic programming for efficient computation
- Convolution mathematics for combining dice
- Advanced modifier support with precise probabilities
- Fallback approximations for extremely complex expressions
"""

import re
import math
import random
from typing import Dict, List, Optional, Tuple, Union, Any, NamedTuple
from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from itertools import product
from collections import defaultdict


# ============================================================================
# TYPE DEFINITIONS AND ENUMS
# ============================================================================

class DiceType(Enum):
    """Standard D&D dice types."""
    D4 = 4
    D6 = 6
    D8 = 8
    D10 = 10
    D12 = 12
    D20 = 20
    D100 = 100
    PERCENTILE = 100  # Alias for d100


class RollModifier(Enum):
    """Types of roll modifiers."""
    NONE = "none"
    ADVANTAGE = "advantage"      # Roll twice, take higher
    DISADVANTAGE = "disadvantage"  # Roll twice, take lower
    KEEP_HIGHEST = "kh"         # Keep highest N dice
    KEEP_LOWEST = "kl"          # Keep lowest N dice
    DROP_HIGHEST = "dh"         # Drop highest N dice
    DROP_LOWEST = "dl"          # Drop lowest N dice
    REROLL = "r"                # Reroll on specific values
    REROLL_ONCE = "ro"          # Reroll once on specific values
    EXPLODING = "x"             # Exploding dice (reroll max)
    CRITICAL = "crit"           # Critical hit multiplier


class AbilityScore(Enum):
    """D&D ability scores for modifier lookup."""
    STRENGTH = "STR"
    DEXTERITY = "DEX"
    CONSTITUTION = "CON"
    INTELLIGENCE = "INT"
    WISDOM = "WIS"
    CHARISMA = "CHA"


@dataclass(frozen=True)
class DiceRoll:
    """Represents a single dice roll component."""
    count: int
    sides: int
    modifier_type: RollModifier = RollModifier.NONE
    modifier_value: Optional[int] = None
    
    def __str__(self) -> str:
        base = f"{self.count}d{self.sides}"
        if self.modifier_type != RollModifier.NONE:
            if self.modifier_value is not None:
                base += f"{self.modifier_type.value}{self.modifier_value}"
            else:
                base += self.modifier_type.value
        return base


@dataclass(frozen=True)
class DiceExpression:
    """Complete dice expression with all components."""
    dice_rolls: List[DiceRoll]
    static_modifier: int = 0
    ability_modifier: Optional[AbilityScore] = None
    proficiency_bonus: bool = False
    
    def __str__(self) -> str:
        parts = [str(roll) for roll in self.dice_rolls]
        
        if self.static_modifier > 0:
            parts.append(f"+{self.static_modifier}")
        elif self.static_modifier < 0:
            parts.append(str(self.static_modifier))
        
        if self.ability_modifier:
            parts.append(f"+{self.ability_modifier.value}")
        
        if self.proficiency_bonus:
            parts.append("+PROF")
        
        return "".join(parts)


class RollResult(NamedTuple):
    """Result of a dice roll calculation."""
    total: int
    individual_rolls: List[List[int]]  # Grouped by dice expression
    kept_rolls: List[List[int]]        # After applying modifiers
    discarded_rolls: List[List[int]]   # Rolls that were discarded
    modifier_total: int
    expression: str
    breakdown: str


@dataclass(frozen=True)
class DiceStatistics:
    """Statistical analysis of dice expression with FULL probability distribution."""
    minimum: int
    maximum: int
    average: float
    variance: float
    standard_deviation: float
    median: float
    mode: List[int]
    probability_distribution: Dict[int, float]  # ALWAYS populated when possible
    
    # Additional statistical measures
    skewness: Optional[float] = None
    kurtosis: Optional[float] = None
    percentiles: Optional[Dict[int, float]] = None  # 25th, 50th, 75th, 90th, 95th, 99th
    
    def __post_init__(self):
        """Calculate additional statistics from distribution if available."""
        if self.probability_distribution:
            # Calculate percentiles
            percentiles = _calculate_percentiles_from_distribution(self.probability_distribution)
            object.__setattr__(self, 'percentiles', percentiles)
            
            # Calculate skewness and kurtosis
            skewness = _calculate_skewness_from_distribution(self.probability_distribution, self.average, self.standard_deviation)
            kurtosis = _calculate_kurtosis_from_distribution(self.probability_distribution, self.average, self.standard_deviation)
            object.__setattr__(self, 'skewness', skewness)
            object.__setattr__(self, 'kurtosis', kurtosis)


# ============================================================================
# DICE NOTATION PARSING
# ============================================================================

# Comprehensive regex patterns for dice notation
DICE_PATTERN = re.compile(
    r'(\d+)?d(\d+)'              # Basic dice (optional count + d + sides)
    r'(?:'                       # Optional modifier group
    r'(kh|kl|dh|dl)(\d+)|'      # Keep/drop highest/lowest
    r'(r|ro)([<>=]?\d+)|'       # Reroll conditions
    r'(x)(\d+)?|'               # Exploding dice
    r'(adv|advantage)|'         # Advantage
    r'(dis|disadvantage)'       # Disadvantage
    r')?',
    re.IGNORECASE
)

FULL_EXPRESSION_PATTERN = re.compile(
    r'^'                         # Start of string
    r'([+\-]?\d*d\d+(?:[a-z]+\d*)*)'  # Dice components
    r'([+\-]\d+)*'              # Static modifiers
    r'([+\-](?:STR|DEX|CON|INT|WIS|CHA))*'  # Ability modifiers
    r'([+\-]PROF)*'             # Proficiency bonus
    r'$',                       # End of string
    re.IGNORECASE
)

MODIFIER_PATTERN = re.compile(r'([+\-])(\d+|STR|DEX|CON|INT|WIS|CHA|PROF)', re.IGNORECASE)


def parse_dice_notation(notation: str) -> Optional[DiceExpression]:
    """
    Parse dice notation string into structured format.
    
    Args:
        notation: Dice notation string (e.g., "1d8+3", "2d6+STR", "1d20adv")
        
    Returns:
        DiceExpression object or None if invalid
        
    Examples:
        >>> parse_dice_notation("1d8+3")
        DiceExpression(dice_rolls=[DiceRoll(1, 8)], static_modifier=3)
        >>> parse_dice_notation("2d6+STR")
        DiceExpression(dice_rolls=[DiceRoll(2, 6)], ability_modifier=AbilityScore.STRENGTH)
        >>> parse_dice_notation("1d20adv")
        DiceExpression(dice_rolls=[DiceRoll(1, 20, RollModifier.ADVANTAGE)])
    """
    if not notation or not isinstance(notation, str):
        return None
    
    # Clean and normalize input
    normalized = normalize_dice_notation(notation)
    if not normalized:
        return None
    
    # Extract dice components
    dice_rolls = []
    dice_matches = DICE_PATTERN.findall(normalized)
    
    for match in dice_matches:
        count_str, sides_str = match[0], match[1]
        count = int(count_str) if count_str else 1
        sides = int(sides_str)
        
        # Validate dice type
        if sides not in [d.value for d in DiceType] and sides not in [2, 3]:
            continue  # Skip invalid dice types
        
        # Parse modifiers
        modifier_type = RollModifier.NONE
        modifier_value = None
        
        # Keep/Drop modifiers
        if match[2]:  # kh, kl, dh, dl
            modifier_type = RollModifier(match[2].lower())
            modifier_value = int(match[3])
        
        # Reroll modifiers
        elif match[4]:  # r, ro
            modifier_type = RollModifier(match[4].lower())
            modifier_value = _parse_reroll_condition(match[5])
        
        # Exploding dice
        elif match[6]:  # x
            modifier_type = RollModifier.EXPLODING
            modifier_value = int(match[7]) if match[7] else sides
        
        # Advantage/Disadvantage
        elif match[8]:  # advantage
            modifier_type = RollModifier.ADVANTAGE
        elif match[9]:  # disadvantage
            modifier_type = RollModifier.DISADVANTAGE
        
        dice_rolls.append(DiceRoll(count, sides, modifier_type, modifier_value))
    
    if not dice_rolls:
        return None
    
    # Parse static modifiers and ability scores
    static_modifier = 0
    ability_modifier = None
    proficiency_bonus = False
    
    modifier_matches = MODIFIER_PATTERN.findall(normalized)
    for sign, value in modifier_matches:
        multiplier = 1 if sign == '+' else -1
        
        if value.isdigit():
            static_modifier += multiplier * int(value)
        elif value.upper() in [ab.value for ab in AbilityScore]:
            ability_modifier = AbilityScore(value.upper())
        elif value.upper() == 'PROF':
            proficiency_bonus = True
    
    return DiceExpression(
        dice_rolls=dice_rolls,
        static_modifier=static_modifier,
        ability_modifier=ability_modifier,
        proficiency_bonus=proficiency_bonus
    )


def normalize_dice_notation(notation: str) -> Optional[str]:
    """
    Normalize dice notation string for consistent parsing.
    
    Args:
        notation: Raw dice notation string
        
    Returns:
        Normalized string or None if invalid
        
    Examples:
        >>> normalize_dice_notation("1 d 8 + 3")
        "1d8+3"
        >>> normalize_dice_notation("d20 advantage")
        "1d20adv"
    """
    if not notation:
        return None
    
    # Remove whitespace and convert to lowercase
    normalized = re.sub(r'\s+', '', notation.strip().lower())
    
    # Handle common abbreviations
    replacements = {
        'advantage': 'adv',
        'disadvantage': 'dis',
        'keephighest': 'kh',
        'keeplowest': 'kl',
        'drophighest': 'dh',
        'droplowest': 'dl',
        'explode': 'x',
        'exploding': 'x'
    }
    
    for old, new in replacements.items():
        normalized = normalized.replace(old, new)
    
    # Ensure dice have explicit count (d20 -> 1d20)
    normalized = re.sub(r'(?<![0-9])d(\d+)', r'1d\1', normalized)
    
    # Normalize signs (ensure + or - before modifiers)
    normalized = re.sub(r'(?<![+\-])(str|dex|con|int|wis|cha|prof)', r'+\1', normalized)
    
    return normalized.upper()


def validate_dice_notation(notation: str) -> Tuple[bool, List[str]]:
    """
    Validate dice notation and return validation errors.
    
    Args:
        notation: Dice notation string to validate
        
    Returns:
        Tuple of (is_valid, error_messages)
        
    Examples:
        >>> validate_dice_notation("1d8+3")
        (True, [])
        >>> validate_dice_notation("1d7+3")
        (False, ["Invalid die type: d7"])
    """
    errors = []
    
    if not notation or not isinstance(notation, str):
        errors.append("Empty or invalid notation")
        return False, errors
    
    # Check for basic format
    if not re.search(r'\d*d\d+', notation, re.IGNORECASE):
        errors.append("No valid dice found in notation")
        return False, errors
    
    # Parse and validate
    try:
        expression = parse_dice_notation(notation)
        if not expression:
            errors.append("Failed to parse dice notation")
            return False, errors
        
        # Validate dice types
        for dice_roll in expression.dice_rolls:
            if dice_roll.sides not in [d.value for d in DiceType] and dice_roll.sides not in [2, 3]:
                errors.append(f"Invalid die type: d{dice_roll.sides}")
            
            if dice_roll.count <= 0:
                errors.append(f"Invalid dice count: {dice_roll.count}")
            
            if dice_roll.count > 100:
                errors.append(f"Too many dice: {dice_roll.count} (max 100)")
            
            # Validate modifiers
            if dice_roll.modifier_type in [RollModifier.KEEP_HIGHEST, RollModifier.KEEP_LOWEST]:
                if dice_roll.modifier_value and dice_roll.modifier_value >= dice_roll.count:
                    errors.append(f"Cannot keep {dice_roll.modifier_value} dice from {dice_roll.count}")
    
    except Exception as e:
        errors.append(f"Parsing error: {str(e)}")
    
    return len(errors) == 0, errors


def _parse_reroll_condition(condition_str: str) -> int:
    """Parse reroll condition string (e.g., '1', '<=2', '>18')."""
    if not condition_str:
        return 1  # Default reroll on 1
    
    # Simple number
    if condition_str.isdigit():
        return int(condition_str)
    
    # Comparison operators (simplified - just return the number for now)
    match = re.search(r'([<>=]+)?(\d+)', condition_str)
    if match:
        return int(match.group(2))
    
    return 1


# ============================================================================
# DICE ROLLING AND CALCULATION
# ============================================================================

def roll_dice(expression: Union[str, DiceExpression], 
              ability_scores: Optional[Dict[str, int]] = None,
              proficiency_bonus: int = 2) -> RollResult:
    """
    Roll dice according to the expression and return detailed results.
    
    Args:
        expression: Dice expression string or DiceExpression object
        ability_scores: Dictionary of ability scores for modifier lookup
        proficiency_bonus: Proficiency bonus value
        
    Returns:
        RollResult with detailed breakdown
        
    Examples:
        >>> result = roll_dice("1d8+3")
        >>> result.total  # Random value between 4-11
        >>> result = roll_dice("2d6+STR", {"STR": 16})
        >>> result.total  # 2d6 + 3 (STR modifier)
    """
    if isinstance(expression, str):
        parsed_expr = parse_dice_notation(expression)
        if not parsed_expr:
            raise ValueError(f"Invalid dice notation: {expression}")
    else:
        parsed_expr = expression
    
    # Initialize tracking variables
    all_rolls = []
    kept_rolls = []
    discarded_rolls = []
    dice_total = 0
    
    # Roll each dice component
    for dice_roll in parsed_expr.dice_rolls:
        individual_dice, kept_dice, discarded_dice = _roll_single_dice_component(dice_roll)
        
        all_rolls.append(individual_dice)
        kept_rolls.append(kept_dice)
        discarded_rolls.append(discarded_dice)
        dice_total += sum(kept_dice)
    
    # Calculate modifier total
    modifier_total = parsed_expr.static_modifier
    
    if parsed_expr.ability_modifier and ability_scores:
        ability_name = parsed_expr.ability_modifier.value
        if ability_name in ability_scores:
            modifier_total += calculate_ability_modifier(ability_scores[ability_name])
    
    if parsed_expr.proficiency_bonus:
        modifier_total += proficiency_bonus
    
    total = dice_total + modifier_total
    
    # Generate breakdown string
    breakdown_parts = []
    for i, (dice_roll, rolls) in enumerate(zip(parsed_expr.dice_rolls, kept_rolls)):
        if dice_roll.modifier_type == RollModifier.NONE:
            breakdown_parts.append(f"{dice_roll} = [{', '.join(map(str, rolls))}]")
        else:
            all_roll_values = all_rolls[i]
            discarded_values = discarded_rolls[i]
            breakdown_parts.append(
                f"{dice_roll} = [{', '.join(map(str, all_roll_values))}] "
                f"→ [{', '.join(map(str, rolls))}]"
                + (f" (discarded: [{', '.join(map(str, discarded_values))}])" if discarded_values else "")
            )
    
    if modifier_total != 0:
        breakdown_parts.append(f"modifiers = {modifier_total:+d}")
    
    breakdown = " + ".join(breakdown_parts) + f" = {total}"
    
    return RollResult(
        total=total,
        individual_rolls=all_rolls,
        kept_rolls=kept_rolls,
        discarded_rolls=discarded_rolls,
        modifier_total=modifier_total,
        expression=str(parsed_expr),
        breakdown=breakdown
    )


def _roll_single_dice_component(dice_roll: DiceRoll) -> Tuple[List[int], List[int], List[int]]:
    """
    Roll a single dice component and apply modifiers.
    
    Returns:
        Tuple of (all_rolls, kept_rolls, discarded_rolls)
    """
    count = dice_roll.count
    sides = dice_roll.sides
    modifier_type = dice_roll.modifier_type
    modifier_value = dice_roll.modifier_value
    
    # Handle advantage/disadvantage (roll twice)
    if modifier_type in [RollModifier.ADVANTAGE, RollModifier.DISADVANTAGE]:
        if count != 1:
            raise ValueError("Advantage/disadvantage only applies to single dice")
        
        roll1 = random.randint(1, sides)
        roll2 = random.randint(1, sides)
        all_rolls = [roll1, roll2]
        
        if modifier_type == RollModifier.ADVANTAGE:
            kept = [max(roll1, roll2)]
            discarded = [min(roll1, roll2)]
        else:  # disadvantage
            kept = [min(roll1, roll2)]
            discarded = [max(roll1, roll2)]
        
        return all_rolls, kept, discarded
    
    # Regular rolls
    all_rolls = []
    for _ in range(count):
        roll = random.randint(1, sides)
        
        # Handle exploding dice
        if modifier_type == RollModifier.EXPLODING:
            explode_on = modifier_value or sides
            explosion_count = 0
            while roll >= explode_on and explosion_count < 10:  # Prevent infinite loops
                all_rolls.append(roll)
                roll = random.randint(1, sides)
                explosion_count += 1
        
        all_rolls.append(roll)
    
    # Apply keep/drop modifiers
    if modifier_type in [RollModifier.KEEP_HIGHEST, RollModifier.KEEP_LOWEST, 
                        RollModifier.DROP_HIGHEST, RollModifier.DROP_LOWEST]:
        
        sorted_rolls = sorted(all_rolls, reverse=True)
        keep_count = modifier_value or 1
        
        if modifier_type == RollModifier.KEEP_HIGHEST:
            kept = sorted_rolls[:keep_count]
            discarded = sorted_rolls[keep_count:]
        elif modifier_type == RollModifier.KEEP_LOWEST:
            kept = sorted_rolls[-keep_count:]
            discarded = sorted_rolls[:-keep_count] if keep_count < len(sorted_rolls) else []
        elif modifier_type == RollModifier.DROP_HIGHEST:
            kept = sorted_rolls[keep_count:]
            discarded = sorted_rolls[:keep_count]
        else:  # DROP_LOWEST
            kept = sorted_rolls[:-keep_count] if keep_count < len(sorted_rolls) else []
            discarded = sorted_rolls[-keep_count:]
        
        return all_rolls, kept, discarded
    
    # Handle reroll modifiers
    if modifier_type in [RollModifier.REROLL, RollModifier.REROLL_ONCE]:
        reroll_value = modifier_value or 1
        final_rolls = []
        discarded = []
        
        for roll in all_rolls:
            current_roll = roll
            reroll_count = 0
            max_rerolls = 1 if modifier_type == RollModifier.REROLL_ONCE else 10
            
            while (current_roll <= reroll_value and reroll_count < max_rerolls):
                discarded.append(current_roll)
                current_roll = random.randint(1, sides)
                reroll_count += 1
            
            final_rolls.append(current_roll)
        
        return all_rolls + discarded, final_rolls, discarded
    
    # No modifiers - keep all rolls
    return all_rolls, all_rolls, []


# ============================================================================
# FULL PROBABILITY DISTRIBUTION IMPLEMENTATION
# ============================================================================

def calculate_dice_statistics(expression: Union[str, DiceExpression],
                            ability_scores: Optional[Dict[str, int]] = None,
                            proficiency_bonus: int = 2) -> DiceStatistics:
    """
    Calculate statistical properties of a dice expression with FULL probability distribution.
    
    This is the COMPLETE implementation that always tries to calculate exact distributions.
    Falls back to approximations only for extremely complex cases.
    
    Args:
        expression: Dice expression to analyze
        ability_scores: Ability scores for modifier calculation
        proficiency_bonus: Proficiency bonus value
        
    Returns:
        DiceStatistics with comprehensive analysis including FULL probability distribution
        
    Examples:
        >>> stats = calculate_dice_statistics("1d8+3")
        >>> stats.minimum  # 4
        >>> stats.maximum  # 11
        >>> stats.average  # 7.5
        >>> len(stats.probability_distribution)  # 8 (values 4-11)
        >>> sum(stats.probability_distribution.values())  # 1.0 (probabilities sum to 1)
        >>> stats.percentiles[50]  # Median from exact distribution
    """
    if isinstance(expression, str):
        parsed_expr = parse_dice_notation(expression)
        if not parsed_expr:
            raise ValueError(f"Invalid dice notation: {expression}")
    else:
        parsed_expr = expression
    
    # Calculate modifier total
    modifier_total = parsed_expr.static_modifier
    
    if parsed_expr.ability_modifier and ability_scores:
        ability_name = parsed_expr.ability_modifier.value
        if ability_name in ability_scores:
            modifier_total += calculate_ability_modifier(ability_scores[ability_name])
    
    if parsed_expr.proficiency_bonus:
        modifier_total += proficiency_bonus
    
    # Calculate FULL probability distribution for dice rolls
    dice_distribution = _calculate_complete_dice_distribution(parsed_expr)
    
    if not dice_distribution:
        # Fallback to approximation ONLY if absolutely necessary
        return _calculate_approximate_statistics(parsed_expr, modifier_total)
    
    # Apply modifier to distribution
    final_distribution = {}
    for dice_total, probability in dice_distribution.items():
        final_value = dice_total + modifier_total
        if final_value in final_distribution:
            final_distribution[final_value] += probability
        else:
            final_distribution[final_value] = probability
    
    # Normalize probabilities (handle floating point errors)
    total_prob = sum(final_distribution.values())
    if abs(total_prob - 1.0) > 1e-10:
        for key in final_distribution:
            final_distribution[key] /= total_prob
    
    # Calculate comprehensive statistics from EXACT distribution
    values = sorted(final_distribution.keys())
    
    minimum = min(values)
    maximum = max(values)
    
    # Expected value (mean) - EXACT
    average = sum(value * prob for value, prob in final_distribution.items())
    
    # Variance: E[X²] - (E[X])² - EXACT
    expected_square = sum(value * value * prob for value, prob in final_distribution.items())
    variance = expected_square - (average * average)
    standard_deviation = math.sqrt(max(0, variance))  # Prevent negative due to floating point
    
    # Median: EXACT value where cumulative probability >= 0.5
    median = _calculate_exact_median_from_distribution(final_distribution)
    
    # Mode: EXACT value(s) with highest probability
    mode = _calculate_exact_mode_from_distribution(final_distribution)
    
    return DiceStatistics(
        minimum=minimum,
        maximum=maximum,
        average=average,
        variance=variance,
        standard_deviation=standard_deviation,
        median=median,
        mode=mode,
        probability_distribution=final_distribution
    )


def _calculate_complete_dice_distribution(expression: DiceExpression) -> Dict[int, float]:
    """
    Calculate the COMPLETE probability distribution for a dice expression.
    
    This is the master function that handles ALL dice combinations with FULL precision.
    Uses multiple strategies to ensure we get exact distributions whenever possible.
    
    Args:
        expression: Parsed dice expression
        
    Returns:
        Dictionary mapping possible totals to their EXACT probabilities
        Empty dict only if expression is computationally intractable
    """
    # Aggressive complexity checking - we want to calculate as much as possible
    total_outcomes = 1
    max_single_component_outcomes = 0
    
    for dice_roll in expression.dice_rolls:
        component_outcomes = _estimate_component_complexity(dice_roll)
        if component_outcomes == -1:  # Infinite outcomes (exploding dice)
            # Use approximation for exploding dice
            pass
        else:
            total_outcomes *= component_outcomes
            max_single_component_outcomes = max(max_single_component_outcomes, component_outcomes)
    
    # More generous limits - we want FULL distributions whenever possible
    if total_outcomes > 10_000_000:  # 10 million combinations max
        return {}
    
    # Calculate distribution for each dice component
    component_distributions = []
    
    for dice_roll in expression.dice_rolls:
        component_dist = _calculate_comprehensive_single_dice_distribution(dice_roll)
        if not component_dist:
            return {}  # Component too complex
        component_distributions.append(component_dist)
    
    # Combine all component distributions using EXACT convolution
    if len(component_distributions) == 1:
        return component_distributions[0]
    
    # Progressive convolution with size management
    combined_distribution = component_distributions[0]
    for i in range(1, len(component_distributions)):
        combined_distribution = _exact_convolve_distributions(
            combined_distribution, 
            component_distributions[i]
        )
        
        # More generous size limits
        if len(combined_distribution) > 50000:  # 50k possible outcomes max
            return {}
    
    return combined_distribution


def _calculate_comprehensive_single_dice_distribution(dice_roll: DiceRoll) -> Dict[int, float]:
    """
    Calculate COMPREHENSIVE probability distribution for a single dice roll component.
    
    Handles ALL modifiers with maximum precision possible.
    """
    count = dice_roll.count
    sides = dice_roll.sides
    modifier_type = dice_roll.modifier_type
    modifier_value = dice_roll.modifier_value
    
    # Handle advantage/disadvantage (EXACT calculation)
    if modifier_type == RollModifier.ADVANTAGE and count == 1:
        return _calculate_exact_advantage_distribution(sides)
    
    elif modifier_type == RollModifier.DISADVANTAGE and count == 1:
        return _calculate_exact_disadvantage_distribution(sides)
    
    # Handle exploding dice (best approximation possible)
    elif modifier_type == RollModifier.EXPLODING:
        return _calculate_exploding_dice_distribution_advanced(count, sides, modifier_value)
    
    # Handle reroll mechanics (EXACT when possible)
    elif modifier_type in [RollModifier.REROLL, RollModifier.REROLL_ONCE]:
        return _calculate_exact_reroll_distribution(count, sides, modifier_type, modifier_value)
    
    # Calculate base distribution for multiple dice (EXACT)
    base_distribution = _calculate_exact_base_dice_distribution(count, sides)
    
    # Apply keep/drop modifiers (EXACT through enumeration)
    if modifier_type in [RollModifier.KEEP_HIGHEST, RollModifier.KEEP_LOWEST, 
                        RollModifier.DROP_HIGHEST, RollModifier.DROP_LOWEST]:
        return _apply_exact_keep_drop_modifier(count, sides, modifier_type, modifier_value)
    
    return base_distribution


def _calculate_exact_base_dice_distribution(count: int, sides: int) -> Dict[int, float]:
    """
    Calculate EXACT probability distribution for rolling multiple standard dice.
    
    Uses optimized dynamic programming for maximum efficiency and precision.
    """
    if count <= 0 or sides <= 0:
        return {0: 1.0}
    
    # Optimized DP using Fraction for EXACT arithmetic when needed
    use_fractions = count * sides <= 1000  # Use exact fractions for smaller problems
    
    if use_fractions:
        return _calculate_exact_base_dice_distribution_fractions(count, sides)
    else:
        return _calculate_exact_base_dice_distribution_float(count, sides)


def _calculate_exact_base_dice_distribution_fractions(count: int, sides: int) -> Dict[int, float]:
    """Calculate using exact fraction arithmetic for perfect precision."""
    current_dist = {0: Fraction(1, 1)}
    
    for die_num in range(1, count + 1):
        next_dist = {}
        
        for prev_sum, prev_prob in current_dist.items():
            for face in range(1, sides + 1):
                new_sum = prev_sum + face
                if new_sum not in next_dist:
                    next_dist[new_sum] = Fraction(0, 1)
                next_dist[new_sum] += prev_prob / sides
        
        current_dist = next_dist
    
    # Convert fractions to floats for return
    return {key: float(val) for key, val in current_dist.items()}


def _calculate_exact_base_dice_distribution_float(count: int, sides: int) -> Dict[int, float]:
    """Calculate using high-precision floating point."""
    current_dist = {0: 1.0}
    
    for die_num in range(1, count + 1):
        next_dist = defaultdict(float)
        
        for prev_sum, prev_prob in current_dist.items():
            prob_per_face = prev_prob / sides
            for face in range(1, sides + 1):
                new_sum = prev_sum + face
                next_dist[new_sum] += prob_per_face
        
        current_dist = dict(next_dist)
    
    return current_dist


def _calculate_exact_advantage_distribution(sides: int) -> Dict[int, float]:
    """Calculate EXACT probability distribution for advantage."""
    distribution = {}
    total_outcomes = sides * sides
    
    for result in range(1, sides + 1):
        # EXACT calculation: count all ways to get this result with advantage
        ways = 0
        for die1 in range(1, sides + 1):
            for die2 in range(1, sides + 1):
                if max(die1, die2) == result:
                    ways += 1
        
        probability = ways / total_outcomes
        distribution[result] = probability
    
    return distribution


def _calculate_exact_disadvantage_distribution(sides: int) -> Dict[int, float]:
    """Calculate EXACT probability distribution for disadvantage."""
    distribution = {}
    total_outcomes = sides * sides
    
    for result in range(1, sides + 1):
        # EXACT calculation: count all ways to get this result with disadvantage
        ways = 0
        for die1 in range(1, sides + 1):
            for die2 in range(1, sides + 1):
                if min(die1, die2) == result:
                    ways += 1
        
        probability = ways / total_outcomes
        distribution[result] = probability
    
    return distribution


def _calculate_exploding_dice_distribution_advanced(count: int, sides: int, 
                                                  explode_on: Optional[int] = None) -> Dict[int, float]:
    """
    Advanced calculation for exploding dice using finite-state approximation.
    
    Models exploding dice as a finite Markov chain for better accuracy.
    """
    if explode_on is None:
        explode_on = sides
    
    # Probability that a die explodes
    explode_prob = (sides - explode_on + 1) / sides
    
    if explode_prob >= 1.0:
        return {}  # Would explode infinitely
    
    # Model each die with finite explosion limit for computational tractability
    max_explosions_per_die = 5  # Allow up to 5 explosions per die
    
    # Calculate single exploding die distribution
    single_die_dist = {}
    
    # Non-exploding outcomes
    for face in range(1, explode_on):
        single_die_dist[face] = 1.0 / sides
    
    # Exploding outcomes - use geometric series approximation
    for explosions in range(max_explosions_per_die + 1):
        explosion_prob = (explode_prob ** explosions) * (1 - explode_prob)
        if explosions == max_explosions_per_die:
            explosion_prob = explode_prob ** explosions  # All remaining probability
        
        for exploding_face in range(explode_on, sides + 1):
            total_value = exploding_face + explosions * sides  # Approximate value
            if total_value not in single_die_dist:
                single_die_dist[total_value] = 0.0
            single_die_dist[total_value] += explosion_prob / (sides - explode_on + 1)
    
    # Combine multiple exploding dice
    if count == 1:
        return single_die_dist
    
    # Use convolution for multiple dice
    result_dist = single_die_dist
    for _ in range(count - 1):
        result_dist = _exact_convolve_distributions(result_dist, single_die_dist)
        if len(result_dist) > 10000:  # Prevent explosion
            break
    
    return result_dist


def _calculate_exact_reroll_distribution(count: int, sides: int, 
                                       reroll_type: RollModifier, 
                                       reroll_value: Optional[int]) -> Dict[int, float]:
    """Calculate EXACT distribution for dice with reroll mechanics."""
    if reroll_value is None:
        reroll_value = 1
    
    if reroll_type == RollModifier.REROLL_ONCE:
        # EXACT calculation for reroll-once
        single_die_probs = {}
        
        for face in range(1, sides + 1):
            if face <= reroll_value:
                # This face gets rerolled once
                # P(final = face) = P(initial = reroll) * P(reroll = face)
                prob_initial_reroll = reroll_value / sides
                prob_reroll_to_face = 1.0 / sides
                single_die_probs[face] = prob_initial_reroll * prob_reroll_to_face
            else:
                # This face can happen initially or after reroll
                prob_initial = 1.0 / sides
                prob_after_reroll = (reroll_value / sides) * (1.0 / sides)
                single_die_probs[face] = prob_initial + prob_after_reroll
        
    else:  # REROLL (infinite rerolls)
        # EXACT calculation for infinite rerolls
        single_die_probs = {}
        
        # Only non-reroll faces can be final results
        non_reroll_faces = sides - reroll_value
        if non_reroll_faces <= 0:
            return {}  # Would reroll forever
        
        for face in range(1, sides + 1):
            if face <= reroll_value:
                single_die_probs[face] = 0.0  # Never a final result
            else:
                # Equal probability among all non-reroll outcomes
                single_die_probs[face] = 1.0 / non_reroll_faces
    
    # Normalize probabilities
    total_prob = sum(single_die_probs.values())
    if total_prob > 0:
        for face in single_die_probs:
            single_die_probs[face] /= total_prob
    
    # Build distribution for multiple dice using EXACT convolution
    return _calculate_exact_distribution_from_single_die_probs(count, single_die_probs)


def _apply_exact_keep_drop_modifier(count: int, sides: int, 
                                  modifier_type: RollModifier, 
                                  modifier_value: Optional[int]) -> Dict[int, float]:
    """
    Calculate EXACT distribution after applying keep/drop modifiers.
    
    Uses complete enumeration for EXACT results when computationally feasible.
    """
    if modifier_value is None:
        modifier_value = 1
    
    # Generous limits for exact calculation
    max_enumerable_combinations = 100000  # 100k combinations
    total_combinations = sides ** count
    
    if total_combinations > max_enumerable_combinations:
        return {}  # Too many to enumerate exactly
    
    # EXACT enumeration of all possible roll combinations
    distribution = defaultdict(float)
    
    # Generate all possible combinations
    for combination in product(range(1, sides + 1), repeat=count):
        # Apply keep/drop logic
        sorted_rolls = sorted(combination, reverse=True)
        
        if modifier_type == RollModifier.KEEP_HIGHEST:
            kept_rolls = sorted_rolls[:modifier_value]
        elif modifier_type == RollModifier.KEEP_LOWEST:
            kept_rolls = sorted_rolls[-modifier_value:]
        elif modifier_type == RollModifier.DROP_HIGHEST:
            kept_rolls = sorted_rolls[modifier_value:]
        else:  # DROP_LOWEST
            kept_rolls = sorted_rolls[:-modifier_value] if modifier_value < len(sorted_rolls) else []
        
        total = sum(kept_rolls)
        distribution[total] += 1.0 / total_combinations
    
    return dict(distribution)


def _calculate_exact_distribution_from_single_die_probs(count: int, 
                                                      single_die_probs: Dict[int, float]) -> Dict[int, float]:
    """
    Calculate EXACT distribution for multiple dice given single-die probabilities.
    
    Uses optimized dynamic programming with exact arithmetic when possible.
    """
    current_dist = {0: 1.0}
    
    for die_num in range(1, count + 1):
        next_dist = defaultdict(float)
        
        for prev_sum, prev_prob in current_dist.items():
            for face, face_prob in single_die_probs.items():
                new_sum = prev_sum + face
                next_dist[new_sum] += prev_prob * face_prob
        
        current_dist = dict(next_dist)
    
    return current_dist


def _exact_convolve_distributions(dist1: Dict[int, float], 
                                dist2: Dict[int, float]) -> Dict[int, float]:
    """
    EXACT convolution of two probability distributions.
    
    Uses optimized algorithms for combining independent random variables.
    """
    result = defaultdict(float)
    
    for value1, prob1 in dist1.items():
        for value2, prob2 in dist2.items():
            sum_value = value1 + value2
            result[sum_value] += prob1 * prob2
    
    return dict(result)


def _calculate_exact_median_from_distribution(distribution: Dict[int, float]) -> float:
    """Calculate EXACT median from probability distribution."""
    # Sort values and calculate cumulative probabilities
    sorted_items = sorted(distribution.items())
    cumulative_prob = 0.0
    
    for value, prob in sorted_items:
        cumulative_prob += prob
        if cumulative_prob >= 0.5:
            return float(value)
    
    # Should not reach here with valid distribution
    return float(sorted_items[-1][0]) if sorted_items else 0.0


def _calculate_exact_mode_from_distribution(distribution: Dict[int, float]) -> List[int]:
    """Calculate EXACT mode(s) from probability distribution."""
    if not distribution:
        return []
    
    max_prob = max(distribution.values())
    modes = [value for value, prob in distribution.items() 
             if abs(prob - max_prob) < 1e-12]  # Very tight tolerance for exact comparison
    
    return sorted(modes)


def _estimate_component_complexity(dice_roll: DiceRoll) -> int:
    """
    Estimate computational complexity for a single dice component.
    
    Returns -1 for infinite complexity (exploding dice).
    """
    if dice_roll.modifier_type == RollModifier.EXPLODING:
        return -1  # Infinite outcomes
    
    base_outcomes = dice_roll.sides ** dice_roll.count
    
    if dice_roll.modifier_type in [RollModifier.REROLL, RollModifier.REROLL_ONCE]:
        return base_outcomes * 2  # Approximate doubling due to rerolls
    
    return base_outcomes


def _calculate_percentiles_from_distribution(distribution: Dict[int, float]) -> Dict[int, float]:
    """Calculate percentiles from exact probability distribution."""
    if not distribution:
        return {}
    
    # Sort values and calculate cumulative distribution
    sorted_items = sorted(distribution.items())
    percentiles = {}
    cumulative_prob = 0.0
    
    target_percentiles = [25, 50, 75, 90, 95, 99]
    percentile_index = 0
    
    for value, prob in sorted_items:
        cumulative_prob += prob
        
        # Check if we've reached any target percentiles
        while (percentile_index < len(target_percentiles) and 
               cumulative_prob >= target_percentiles[percentile_index] / 100.0):
            percentiles[target_percentiles[percentile_index]] = float(value)
            percentile_index += 1
    
    return percentiles


def _calculate_skewness_from_distribution(distribution: Dict[int, float], 
                                        mean: float, std_dev: float) -> Optional[float]:
    """Calculate skewness from probability distribution."""
    if std_dev == 0:
        return None
    
    # Third moment about the mean
    third_moment = sum((value - mean) ** 3 * prob for value, prob in distribution.items())
    skewness = third_moment / (std_dev ** 3)
    
    return skewness


def _calculate_kurtosis_from_distribution(distribution: Dict[int, float], 
                                        mean: float, std_dev: float) -> Optional[float]:
    """Calculate kurtosis from probability distribution."""
    if std_dev == 0:
        return None
    
    # Fourth moment about the mean
    fourth_moment = sum((value - mean) ** 4 * prob for value, prob in distribution.items())
    kurtosis = fourth_moment / (std_dev ** 4) - 3  # Excess kurtosis
    
    return kurtosis


# ============================================================================
# FALLBACK APPROXIMATION FUNCTIONS
# ============================================================================

def _calculate_approximate_statistics(expression: DiceExpression, 
                                    modifier_total: int) -> DiceStatistics:
    """
    Fallback method for expressions too complex for exact calculation.
    
    Uses sophisticated approximations when exact calculation is impossible.
    """
    # Calculate approximate bounds and averages
    dice_min = 0
    dice_max = 0
    dice_avg = 0.0
    dice_var = 0.0
    
    for dice_roll in expression.dice_rolls:
        roll_min, roll_max, roll_avg, roll_var = _calculate_advanced_single_dice_stats(dice_roll)
        dice_min += roll_min
        dice_max += roll_max
        dice_avg += roll_avg
        dice_var += roll_var
    
    # Final statistics
    minimum = dice_min + modifier_total
    maximum = dice_max + modifier_total
    average = dice_avg + modifier_total
    variance = dice_var
    standard_deviation = math.sqrt(max(0, variance))
    
    # Approximate median and mode
    median = average
    mode = [int(round(average))]
    
    # Try to create a simple distribution for basic cases
    approximate_distribution = _create_approximate_distribution(
        minimum, maximum, average, standard_deviation
    )
    
    return DiceStatistics(
        minimum=minimum,
        maximum=maximum,
        average=average,
        variance=variance,
        standard_deviation=standard_deviation,
        median=median,
        mode=mode,
        probability_distribution=approximate_distribution
    )


def _calculate_advanced_single_dice_stats(dice_roll: DiceRoll) -> Tuple[int, int, float, float]:
    """Calculate advanced statistics for a single dice component with better approximations."""
    count = dice_roll.count
    sides = dice_roll.sides
    modifier_type = dice_roll.modifier_type
    modifier_value = dice_roll.modifier_value
    
    # Base statistics
    base_min = count
    base_max = count * sides
    base_avg = count * (sides + 1) / 2
    base_var = count * (sides * sides - 1) / 12
    
    # Advanced adjustments for modifiers
    if modifier_type == RollModifier.ADVANTAGE:
        # Better approximation for advantage
        adjusted_avg = base_avg + (sides - 1) / 3
        adjusted_var = base_var * 0.8  # Advantage reduces variance
        return 1, sides, adjusted_avg, adjusted_var
    
    elif modifier_type == RollModifier.DISADVANTAGE:
        # Better approximation for disadvantage
        adjusted_avg = base_avg - (sides - 1) / 3
        adjusted_var = base_var * 0.8  # Disadvantage reduces variance
        return 1, sides, adjusted_avg, adjusted_var
    
    elif modifier_type == RollModifier.KEEP_HIGHEST:
        keep_count = modifier_value or 1
        if keep_count >= count:
            return base_min, base_max, base_avg, base_var
        
        # Improved approximation for keep highest
        expected_improvement = (sides - 1) * (count - keep_count) / (count + 1)
        new_avg = (base_avg * keep_count / count) + expected_improvement
        new_var = base_var * (keep_count / count) * 0.9  # Reduced variance
        return keep_count, keep_count * sides, new_avg, new_var
    
    elif modifier_type == RollModifier.EXPLODING:
        explode_on = modifier_value or sides
        explode_prob = (sides - explode_on + 1) / sides
        
        if explode_prob > 0 and explode_prob < 1:
            # Expected additional dice from explosions
            expected_explosions = explode_prob / (1 - explode_prob)
            explosion_avg = expected_explosions * (sides + 1) / 2
            
            return base_min, base_max * 3, base_avg + explosion_avg, base_var * 2
    
    # Default case
    return base_min, base_max, base_avg, base_var


def _create_approximate_distribution(minimum: int, maximum: int, 
                                   average: float, std_dev: float) -> Dict[int, float]:
    """Create an approximate normal distribution for simple cases."""
    if maximum - minimum > 100:  # Too wide to approximate
        return {}
    
    distribution = {}
    
    # Use normal approximation for the distribution
    for value in range(minimum, maximum + 1):
        # Standard normal calculation
        z_score = (value - average) / std_dev if std_dev > 0 else 0
        
        # Approximate probability using normal distribution
        prob = math.exp(-0.5 * z_score * z_score) / (std_dev * math.sqrt(2 * math.pi))
        
        if prob > 1e-6:  # Only include significant probabilities
            distribution[value] = prob
    
    # Normalize probabilities
    total_prob = sum(distribution.values())
    if total_prob > 0:
        for key in distribution:
            distribution[key] /= total_prob
    
    return distribution


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def calculate_ability_modifier(ability_score: int) -> int:
    """
    Calculate ability modifier from ability score.
    
    Args:
        ability_score: Ability score (1-30)
        
    Returns:
        Ability modifier
        
    Examples:
        >>> calculate_ability_modifier(16)
        3
        >>> calculate_ability_modifier(8)
        -1
    """
    return (ability_score - 10) // 2


def get_dice_type_from_sides(sides: int) -> Optional[DiceType]:
    """
    Get DiceType enum from number of sides.
    
    Args:
        sides: Number of sides on the die
        
    Returns:
        DiceType or None if not a standard die
    """
    try:
        return DiceType(sides)
    except ValueError:
        return None


def is_standard_die(sides: int) -> bool:
    """
    Check if a die is a standard D&D die type.
    
    Args:
        sides: Number of sides
        
    Returns:
        True if standard die type
    """
    return sides in [d.value for d in DiceType] or sides in [2, 3]


def format_dice_result(result: RollResult, show_breakdown: bool = True) -> str:
    """
    Format dice roll result for display.
    
    Args:
        result: Roll result to format
        show_breakdown: Whether to show detailed breakdown
        
    Returns:
        Formatted string
        
    Examples:
        >>> result = roll_dice("1d8+3")
        >>> format_dice_result(result)
        "1d8+3 = [6] + 3 = 9"
    """
    if show_breakdown:
        return f"{result.expression} = {result.breakdown}"
    else:
        return f"{result.expression} = {result.total}"


def format_dice_statistics(stats: DiceStatistics, detailed: bool = True) -> str:
    """
    Format dice statistics for display with full distribution information.
    
    Args:
        stats: DiceStatistics to format
        detailed: Whether to show detailed information
        
    Returns:
        Formatted statistics string
    """
    lines = [
        f"Range: {stats.minimum} - {stats.maximum}",
        f"Average: {stats.average:.2f}",
        f"Median: {stats.median:.2f}",
        f"Mode: {', '.join(map(str, stats.mode))}",
        f"Std Dev: {stats.standard_deviation:.2f}"
    ]
    
    if detailed and stats.percentiles:
        percentile_str = ", ".join(f"{p}%: {v:.1f}" for p, v in sorted(stats.percentiles.items()))
        lines.append(f"Percentiles: {percentile_str}")
    
    if detailed and stats.skewness is not None:
        lines.append(f"Skewness: {stats.skewness:.3f}")
    
    if stats.probability_distribution:
        lines.append(f"Distribution: {len(stats.probability_distribution)} possible outcomes")
        if detailed and len(stats.probability_distribution) <= 20:
            dist_str = ", ".join(f"{v}: {p:.3f}" for v, p in sorted(stats.probability_distribution.items()))
            lines.append(f"Probabilities: {dist_str}")
    else:
        lines.append("Distribution: Approximated (too complex for exact calculation)")
    
    return "\n".join(lines)


def suggest_dice_notation(description: str) -> List[str]:
    """
    Suggest dice notation based on natural language description.
    
    Args:
        description: Natural language description
        
    Returns:
        List of suggested dice notations
        
    Examples:
        >>> suggest_dice_notation("sword damage")
        ["1d8", "1d8+STR", "2d6"]
        >>> suggest_dice_notation("fireball damage")
        ["8d6", "6d6", "10d6"]
    """
    suggestions = []
    desc_lower = description.lower()
    
    # Common D&D damage patterns
    if any(weapon in desc_lower for weapon in ['sword', 'blade', 'slash']):
        suggestions.extend(["1d8", "1d8+STR", "1d6+STR"])
    
    if any(weapon in desc_lower for weapon in ['bow', 'arrow', 'shot']):
        suggestions.extend(["1d8+DEX", "1d6+DEX"])
    
    if any(spell in desc_lower for spell in ['fireball', 'lightning', 'fire']):
        suggestions.extend(["8d6", "6d6", "10d6"])
    
    if any(heal in desc_lower for heal in ['heal', 'cure', 'restore']):
        suggestions.extend(["1d8+WIS", "2d4+WIS", "1d4+WIS"])
    
    if 'attack' in desc_lower:
        suggestions.extend(["1d20+STR", "1d20+DEX", "1d20+PROF"])
    
    if 'save' in desc_lower:
        suggestions.extend(["1d20+CON", "1d20+WIS", "1d20+DEX"])
    
    # Default suggestions if nothing matches
    if not suggestions:
        suggestions = ["1d20", "1d8", "1d6", "1d4", "2d6"]
    
    return suggestions[:10]  # Limit to top 10 suggestions


def compare_dice_expressions(expr1: str, expr2: str) -> Dict[str, Any]:
    """
    Compare two dice expressions statistically using FULL distributions when possible.
    
    Args:
        expr1: First dice expression
        expr2: Second dice expression
        
    Returns:
        Comprehensive comparison results including distribution analysis
        
    Examples:
        >>> compare_dice_expressions("1d8+3", "2d4+2")
        {"expr1_better": False, "average_difference": -0.5, "distribution_overlap": 0.75, ...}
    """
    try:
        stats1 = calculate_dice_statistics(expr1)
        stats2 = calculate_dice_statistics(expr2)
        
        comparison = {
            "expression_1": expr1,
            "expression_2": expr2,
            "stats_1": {
                "min": stats1.minimum,
                "max": stats1.maximum,
                "avg": stats1.average,
                "std_dev": stats1.standard_deviation,
                "has_exact_distribution": bool(stats1.probability_distribution)
            },
            "stats_2": {
                "min": stats2.minimum,
                "max": stats2.maximum,
                "avg": stats2.average,
                "std_dev": stats2.standard_deviation,
                "has_exact_distribution": bool(stats2.probability_distribution)
            },
            "comparison": {
                "expr1_higher_average": stats1.average > stats2.average,
                "expr1_higher_maximum": stats1.maximum > stats2.maximum,
                "expr1_more_consistent": stats1.standard_deviation < stats2.standard_deviation,
                "average_difference": stats1.average - stats2.average,
                "max_difference": stats1.maximum - stats2.maximum,
                "variance_ratio": stats1.variance / stats2.variance if stats2.variance > 0 else float('inf')
            }
        }
        
        # Add distribution comparison if both have exact distributions
        if stats1.probability_distribution and stats2.probability_distribution:
            overlap = _calculate_distribution_overlap(
                stats1.probability_distribution, 
                stats2.probability_distribution
            )
            comparison["distribution_analysis"] = {
                "overlap_coefficient": overlap,
                "expr1_dominates": _check_stochastic_dominance(
                    stats1.probability_distribution, 
                    stats2.probability_distribution
                ),
                "expr2_dominates": _check_stochastic_dominance(
                    stats2.probability_distribution, 
                    stats1.probability_distribution
                )
            }
        
        return comparison
    
    except Exception as e:
        return {"error": str(e)}


def _calculate_distribution_overlap(dist1: Dict[int, float], dist2: Dict[int, float]) -> float:
    """Calculate overlap coefficient between two probability distributions."""
    overlap = 0.0
    all_values = set(dist1.keys()) | set(dist2.keys())
    
    for value in all_values:
        prob1 = dist1.get(value, 0.0)
        prob2 = dist2.get(value, 0.0)
        overlap += min(prob1, prob2)
    
    return overlap


def _check_stochastic_dominance(dist1: Dict[int, float], dist2: Dict[int, float]) -> bool:
    """Check if dist1 first-order stochastically dominates dist2."""
    # Get all possible values
    all_values = sorted(set(dist1.keys()) | set(dist2.keys()))
    
    # Calculate cumulative distributions
    cumulative1 = 0.0
    cumulative2 = 0.0
    
    for value in all_values:
        cumulative1 += dist1.get(value, 0.0)
        cumulative2 += dist2.get(value, 0.0)
        
        # For first-order stochastic dominance, CDF1(x) <= CDF2(x) for all x
        if cumulative1 > cumulative2 + 1e-10:  # Small tolerance for floating point
            return False
    
    return True


def simulate_dice_rolls(expression: str, num_simulations: int = 1000,
                       ability_scores: Optional[Dict[str, int]] = None) -> Dict[str, Any]:
    """
    Simulate many dice rolls to analyze statistical properties.
    
    Args:
        expression: Dice expression to simulate
        num_simulations: Number of simulations to run
        ability_scores: Ability scores for modifiers
        
    Returns:
        Simulation results with comprehensive statistics
    """
    results = []
    
    for _ in range(num_simulations):
        try:
            result = roll_dice(expression, ability_scores)
            results.append(result.total)
        except Exception:
            continue
    
    if not results:
        return {"error": "No successful rolls"}
    
    # Calculate comprehensive statistics
    results.sort()
    n = len(results)
    
    mean = sum(results) / n
    variance = sum((x - mean) ** 2 for x in results) / n
    std_dev = math.sqrt(variance)
    
    # Calculate additional statistics
    median = results[n // 2]
    q1 = results[n // 4]
    q3 = results[3 * n // 4]
    
    return {
        "expression": expression,
        "simulations": num_simulations,
        "successful_rolls": n,
        "results": {
            "minimum": min(results),
            "maximum": max(results),
            "mean": round(mean, 3),
            "median": median,
            "std_deviation": round(std_dev, 3),
            "variance": round(variance, 3),
            "quartiles": {
                "q1": q1,
                "q2": median,
                "q3": q3,
                "iqr": q3 - q1
            },
            "percentiles": {
                "5th": results[n // 20],
                "10th": results[n // 10],
                "25th": q1,
                "50th": median,
                "75th": q3,
                "90th": results[9 * n // 10],
                "95th": results[19 * n // 20]
            }
        },
        "distribution": _create_histogram(results),
        "simulation_quality": {
            "convergence_check": abs(mean - results[-n//10:][0]) < std_dev / 10,
            "sample_size_adequate": n >= max(100, int(std_dev * 10))
        }
    }


def _create_histogram(results: List[int], bins: int = 20) -> Dict[str, List]:
    """Create histogram data from roll results."""
    if not results:
        return {"bins": [], "counts": [], "frequencies": []}
    
    min_val = min(results)
    max_val = max(results)
    
    if min_val == max_val:
        return {
            "bins": [f"{min_val}"],
            "counts": [len(results)],
            "frequencies": [1.0]
        }
    
    # Create bins
    bin_width = (max_val - min_val) / bins
    bin_edges = [min_val + i * bin_width for i in range(bins + 1)]
    bin_counts = [0] * bins
    
    # Count occurrences in each bin
    for result in results:
        bin_index = min(int((result - min_val) / bin_width), bins - 1)
        bin_counts[bin_index] += 1
    
    # Calculate frequencies
    total_count = len(results)
    frequencies = [count / total_count for count in bin_counts]
    
    # Format bin labels
    bin_labels = []
    for i in range(bins):
        start = bin_edges[i]
        end = bin_edges[i + 1]
        if i == bins - 1:  # Last bin includes the maximum
            bin_labels.append(f"{start:.1f}-{end:.1f}")
        else:
            bin_labels.append(f"{start:.1f}-{end:.1f}")
    
    return {
        "bins": bin_labels,
        "counts": bin_counts,
        "frequencies": frequencies
    }


def optimize_dice_for_target(target_average: float, 
                           available_dice: Optional[List[int]] = None,
                           max_dice_count: int = 10,
                           max_modifier: int = 15) -> List[str]:
    """
    Find dice combinations that produce a target average.
    
    Args:
        target_average: Desired average damage/value
        available_dice: List of available die sizes
        max_dice_count: Maximum number of dice to consider
        max_modifier: Maximum static modifier to consider
        
    Returns:
        List of dice expressions that approximate the target, sorted by accuracy
    """
    if available_dice is None:
        available_dice = [4, 6, 8, 10, 12, 20]
    
    suggestions = []
    
    # Try different combinations
    for sides in available_dice:
        die_average = (sides + 1) / 2
        
        # Single die with modifier
        needed_modifier = target_average - die_average
        if abs(needed_modifier) <= max_modifier:
            expr = f"1d{sides}"
            if needed_modifier > 0:
                expr += f"+{int(needed_modifier)}"
            elif needed_modifier < 0:
                expr += f"{int(needed_modifier)}"
            
            try:
                stats = calculate_dice_statistics(expr)
                error = abs(stats.average - target_average)
                suggestions.append((expr, error, stats.average))
            except:
                pass
        
        # Multiple dice with modifier
        for count in range(2, max_dice_count + 1):
            total_dice_average = count * die_average
            needed_modifier = target_average - total_dice_average
            
            if abs(needed_modifier) <= max_modifier:
                expr = f"{count}d{sides}"
                if needed_modifier > 0.5:
                    expr += f"+{int(round(needed_modifier))}"
                elif needed_modifier < -0.5:
                    expr += f"{int(round(needed_modifier))}"
                
                try:
                    stats = calculate_dice_statistics(expr)
                    error = abs(stats.average - target_average)
                    suggestions.append((expr, error, stats.average))
                except:
                    pass
    
    # Sort by accuracy (lowest error first)
    suggestions.sort(key=lambda x: x[1])
    
    # Return top 10 suggestions with their statistics
    result = []
    for expr, error, actual_avg in suggestions[:10]:
        result.append({
            "expression": expr,
            "actual_average": round(actual_avg, 2),
            "target_average": target_average,
            "error": round(error, 3),
            "accuracy_percent": round((1 - error / target_average) * 100, 1) if target_average > 0 else 0
        })
    
    return [item["expression"] for item in result]


def generate_damage_dice_for_level(level: int, damage_type: str = "weapon") -> List[str]:
    """
    Generate appropriate damage dice for character level.
    
    Args:
        level: Character level (1-20)
        damage_type: Type of damage ("weapon", "spell", "cantrip")
        
    Returns:
        List of appropriate dice expressions
        
    Examples:
        >>> generate_damage_dice_for_level(5, "weapon")
        ["1d8+3", "1d6+3", "2d6+3"]
        >>> generate_damage_dice_for_level(10, "spell")
        ["6d6", "8d6", "4d8", "3d10"]
    """
    suggestions = []
    
    if damage_type == "weapon":
        # Weapon damage scales with ability scores and magic weapons
        base_modifier = min(5, 2 + level // 4)  # Ability modifier + magic bonus
        
        # Basic weapon dice
        suggestions.extend([
            f"1d8+{base_modifier}",  # Longsword, battleaxe
            f"1d6+{base_modifier}",  # Shortsword, scimitar
            f"2d6+{base_modifier}",  # Greatsword
            f"1d12+{base_modifier}", # Greataxe
            f"1d10+{base_modifier}", # Heavy crossbow
            f"1d4+{base_modifier}"   # Dagger
        ])
        
        # Higher level considerations
        if level >= 5:  # Extra Attack available
            suggestions.extend([
                f"2d8+{base_modifier*2}",  # Two attacks with longsword
                f"2d6+{base_modifier*2}",  # Two attacks with shortsword
            ])
        
        if level >= 11:  # Additional extra attack for fighters
            suggestions.extend([
                f"3d8+{base_modifier*3}",  # Three attacks
                f"4d6+{base_modifier*4}",  # Multiple light weapon attacks
            ])
        
        # Magic weapon scaling
        if level >= 8:
            magic_bonus = 1 + (level - 8) // 4  # +1 at 8th, +2 at 12th, +3 at 16th
            suggestions.extend([
                f"1d8+{base_modifier + magic_bonus}",
                f"2d6+{base_modifier + magic_bonus}",
            ])
    
    elif damage_type == "spell":
        # Spell damage scales with spell slot level
        max_spell_level = min(9, 1 + (level - 1) // 2)  # Rough spell level progression
        
        # Common spell damage patterns
        for spell_level in range(1, min(max_spell_level + 1, 10)):
            # Damage scales roughly 1d6 per spell level for damage spells
            base_dice = spell_level + 2  # Start higher for damage spells
            
            suggestions.extend([
                f"{base_dice}d6",      # Fireball-style
                f"{base_dice - 1}d8",  # Cone of cold-style
                f"{base_dice // 2 + 1}d12",  # High damage, fewer dice
                f"{base_dice + 1}d4",  # Magic missile-style
                f"{base_dice - 1}d10", # Lightning bolt-style
            ])
        
        # Specific high-level spells
        if level >= 9:  # 5th level spells
            suggestions.extend(["8d6", "6d8", "4d12"])
        if level >= 13: # 7th level spells
            suggestions.extend(["12d6", "10d8", "6d12"])
        if level >= 17: # 9th level spells
            suggestions.extend(["20d6", "15d8", "12d10"])
    
    elif damage_type == "cantrip":
        # Cantrip damage scales at specific levels (1st, 5th, 11th, 17th)
        if level < 5:
            dice_count = 1
        elif level < 11:
            dice_count = 2
        elif level < 17:
            dice_count = 3
        else:
            dice_count = 4
        
        suggestions.extend([
            f"{dice_count}d10",  # Eldritch Blast, Fire Bolt
            f"{dice_count}d8",   # Sacred Flame
            f"{dice_count}d6",   # Ray of Frost
            f"{dice_count}d4",   # Minor damage cantrips
            f"{dice_count}d12",  # High damage cantrips
        ])
    
    elif damage_type == "healing":
        # Healing scales with spell level and wisdom modifier
        wisdom_modifier = 3 + level // 5  # Approximate wisdom modifier growth
        
        suggestions.extend([
            f"1d8+{wisdom_modifier}",    # Cure Wounds 1st level
            f"2d8+{wisdom_modifier}",    # Cure Wounds 2nd level
            f"3d8+{wisdom_modifier}",    # Cure Wounds 3rd level
            f"4d8+{wisdom_modifier}",    # Cure Wounds 4th level
            f"1d4+{wisdom_modifier}",    # Healing Word
            f"2d4+{wisdom_modifier}",    # Mass Healing Word
        ])
        
        if level >= 9:  # Higher level healing
            suggestions.extend([
                f"8d8+{wisdom_modifier}",   # Mass Cure Wounds
                f"6d8+{wisdom_modifier}",   # Heal (partial)
                "70",                       # Heal spell (fixed amount)
            ])
    
    # Remove duplicates and sort by expected damage
    suggestions = list(set(suggestions))
    
    # Sort suggestions by average damage (highest first)
    def get_average_damage(expr):
        try:
            stats = calculate_dice_statistics(expr)
            return stats.average
        except:
            return 0
    
    suggestions.sort(key=get_average_damage, reverse=True)
    
    return suggestions[:15]  # Return top 15 suggestions


# ============================================================================
# VALIDATION AND UTILITY FUNCTIONS
# ============================================================================

def batch_validate_dice_expressions(expressions: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    Validate multiple dice expressions and return comprehensive results.
    
    Args:
        expressions: List of dice notation strings to validate
        
    Returns:
        Dictionary mapping expressions to validation results
    """
    results = {}
    
    for expr in expressions:
        try:
            # Basic validation
            is_valid, errors = validate_dice_notation(expr)
            
            # If valid, get statistics
            if is_valid:
                stats = calculate_dice_statistics(expr)
                results[expr] = {
                    "valid": True,
                    "errors": [],
                    "statistics": {
                        "min": stats.minimum,
                        "max": stats.maximum,
                        "average": round(stats.average, 2),
                        "std_dev": round(stats.standard_deviation, 2),
                        "has_distribution": bool(stats.probability_distribution)
                    }
                }
            else:
                results[expr] = {
                    "valid": False,
                    "errors": errors,
                    "statistics": None
                }
                
        except Exception as e:
            results[expr] = {
                "valid": False,
                "errors": [f"Exception: {str(e)}"],
                "statistics": None
            }
    
    return results


def analyze_dice_fairness(expression: str) -> Dict[str, Any]:
    """
    Analyze the fairness and randomness properties of a dice expression.
    
    Args:
        expression: Dice expression to analyze
        
    Returns:
        Fairness analysis results
    """
    try:
        stats = calculate_dice_statistics(expression)
        
        analysis = {
            "expression": expression,
            "fairness_metrics": {
                "coefficient_of_variation": stats.standard_deviation / stats.average if stats.average > 0 else float('inf'),
                "range_ratio": (stats.maximum - stats.minimum) / stats.average if stats.average > 0 else float('inf'),
                "is_symmetric": abs(stats.skewness) < 0.1 if stats.skewness is not None else None,
                "has_single_mode": len(stats.mode) == 1,
            },
            "randomness_quality": "unknown"
        }
        
        # Assess overall fairness
        cv = analysis["fairness_metrics"]["coefficient_of_variation"]
        if cv < 0.3:
            analysis["randomness_quality"] = "low_variance"
        elif cv < 0.7:
            analysis["randomness_quality"] = "moderate_variance"
        else:
            analysis["randomness_quality"] = "high_variance"
        
        # Distribution analysis if available
        if stats.probability_distribution:
            # Check for uniform-like distribution
            probs = list(stats.probability_distribution.values())
            max_prob = max(probs)
            min_prob = min(probs)
            uniformity = 1 - (max_prob - min_prob) / max_prob if max_prob > 0 else 0
            
            analysis["distribution_analysis"] = {
                "uniformity_score": round(uniformity, 3),
                "entropy": _calculate_entropy(stats.probability_distribution),
                "effective_outcomes": len([p for p in probs if p > 0.01])  # Outcomes with >1% probability
            }
        
        return analysis
        
    except Exception as e:
        return {"error": str(e)}


def _calculate_entropy(distribution: Dict[int, float]) -> float:
    """Calculate Shannon entropy of a probability distribution."""
    entropy = 0.0
    for prob in distribution.values():
        if prob > 0:
            entropy -= prob * math.log2(prob)
    return entropy


def get_dice_complexity_score(expression: str) -> Dict[str, Any]:
    """
    Calculate a complexity score for a dice expression.
    
    Args:
        expression: Dice expression to analyze
        
    Returns:
        Complexity analysis
    """
    try:
        parsed = parse_dice_notation(expression)
        if not parsed:
            return {"error": "Invalid expression"}
        
        complexity_score = 0
        factors = {
            "total_dice": 0,
            "unique_die_types": 0,
            "modifiers": 0,
            "advanced_mechanics": 0
        }
        
        die_types = set()
        
        for dice_roll in parsed.dice_rolls:
            factors["total_dice"] += dice_roll.count
            die_types.add(dice_roll.sides)
            
            # Modifier complexity
            if dice_roll.modifier_type != 'none':
                factors["advanced_mechanics"] += 1
                
                if dice_roll.modifier_type in ['advantage', 'disadvantage']:
                    complexity_score += 2
                elif dice_roll.modifier_type in ['kh', 'kl', 'dh', 'dl']:
                    complexity_score += 3
                elif dice_roll.modifier_type in ['exploding']:
                    complexity_score += 5
                elif dice_roll.modifier_type in ['reroll', 'reroll_once']:
                    complexity_score += 4
        
        factors["unique_die_types"] = len(die_types)
        
        # Base complexity from dice count
        complexity_score += factors["total_dice"]
        
        # Complexity from variety
        complexity_score += factors["unique_die_types"] * 0.5
        
        # Static modifiers add minimal complexity
        if parsed.static_modifier != 0:
            factors["modifiers"] += 1
            complexity_score += 0.5
        
        if parsed.ability_modifier:
            factors["modifiers"] += 1
            complexity_score += 0.5
            
        if parsed.proficiency_bonus:
            factors["modifiers"] += 1
            complexity_score += 0.5
        
        # Complexity categories
        if complexity_score <= 2:
            category = "simple"
        elif complexity_score <= 5:
            category = "moderate"
        elif complexity_score <= 10:
            category = "complex"
        else:
            category = "very_complex"
        
        return {
            "expression": expression,
            "complexity_score": round(complexity_score, 1),
            "category": category,
            "factors": factors,
            "computational_feasibility": complexity_score < 15
        }
        
    except Exception as e:
        return {"error": str(e)}


# ============================================================================
# EXPORT AND REPORTING FUNCTIONS
# ============================================================================

def generate_dice_report(expressions: List[str]) -> Dict[str, Any]:
    """
    Generate comprehensive report for multiple dice expressions.
    
    Args:
        expressions: List of dice expressions to analyze
        
    Returns:
        Comprehensive analysis report
    """
    report = {
        "total_expressions": len(expressions),
        "valid_expressions": 0,
        "invalid_expressions": 0,
        "summary_statistics": {},
        "complexity_analysis": {},
        "recommendations": [],
        "detailed_results": {}
    }
    
    all_averages = []
    all_variances = []
    complexity_scores = []
    
    for expr in expressions:
        try:
            # Validate
            is_valid, errors = validate_dice_notation(expr)
            
            if is_valid:
                report["valid_expressions"] += 1
                
                # Get statistics
                stats = calculate_dice_statistics(expr)
                complexity = get_dice_complexity_score(expr)
                
                all_averages.append(stats.average)
                all_variances.append(stats.variance)
                complexity_scores.append(complexity.get("complexity_score", 0))
                
                report["detailed_results"][expr] = {
                    "statistics": {
                        "range": f"{stats.minimum}-{stats.maximum}",
                        "average": round(stats.average, 2),
                        "std_dev": round(stats.standard_deviation, 2)
                    },
                    "complexity": complexity.get("category", "unknown"),
                    "has_exact_distribution": bool(stats.probability_distribution)
                }
            else:
                report["invalid_expressions"] += 1
                report["detailed_results"][expr] = {
                    "valid": False,
                    "errors": errors
                }
                
        except Exception as e:
            report["invalid_expressions"] += 1
            report["detailed_results"][expr] = {
                "valid": False,
                "errors": [str(e)]
            }
    
    # Summary statistics
    if all_averages:
        report["summary_statistics"] = {
            "average_damage_range": f"{min(all_averages):.1f} - {max(all_averages):.1f}",
            "mean_average_damage": round(sum(all_averages) / len(all_averages), 2),
            "variance_range": f"{min(all_variances):.1f} - {max(all_variances):.1f}",
            "complexity_range": f"{min(complexity_scores):.1f} - {max(complexity_scores):.1f}"
        }
    
    # Generate recommendations
    if report["valid_expressions"] > 0:
        if report["invalid_expressions"] > 0:
            report["recommendations"].append("Some expressions are invalid - check syntax and dice types")
        
        if complexity_scores and max(complexity_scores) > 10:
            report["recommendations"].append("Some expressions are very complex - consider simplification")
        
        if all_variances and max(all_variances) > 20:
            report["recommendations"].append("Some expressions have high variance - results may be unpredictable")
        
        if not report["recommendations"]:
            report["recommendations"].append("All expressions look good!")
    
    return report


# ============================================================================
# MODULE CONSTANTS AND METADATA
# ============================================================================

# Version and compliance information
__version__ = '2.1.0'
__description__ = 'Comprehensive dice notation parsing and calculation utilities for D&D with FULL probability distributions'

# Clean Architecture compliance metadata
CLEAN_ARCHITECTURE_COMPLIANCE = {
    "layer": "core/utils",
    "dependencies": ["re", "math", "random", "typing", "fractions", "itertools", "collections"],
    "dependents": ["domain/services", "application/use_cases"],
    "infrastructure_independent": True,
    "pure_functions": True,
    "side_effects": "minimal",  # Only random number generation
    "focuses_on": "Dice mechanics, probability distributions, and mathematical calculations for D&D"
}

# Function categories for organization
FUNCTION_CATEGORIES = {
    "parsing": [
        "parse_dice_notation", "normalize_dice_notation", "validate_dice_notation"
    ],
    "rolling": [
        "roll_dice", "simulate_dice_rolls", "_roll_single_dice_component"
    ],
    "statistics": [
        "calculate_dice_statistics", "compare_dice_expressions", "analyze_dice_fairness"
    ],
    "probability_distributions": [
        "_calculate_complete_dice_distribution", "_calculate_comprehensive_single_dice_distribution",
        "_calculate_exact_base_dice_distribution", "_calculate_exact_advantage_distribution",
        "_exact_convolve_distributions"
    ],
    "utilities": [
        "calculate_ability_modifier", "format_dice_result", "format_dice_statistics",
        "suggest_dice_notation", "generate_damage_dice_for_level", "optimize_dice_for_target"
    ],
    "validation": [
        "is_standard_die", "get_dice_type_from_sides", "batch_validate_dice_expressions"
    ],
    "analysis": [
        "get_dice_complexity_score", "generate_dice_report", "_calculate_entropy"
    ]
}

# Supported dice mechanics
SUPPORTED_MECHANICS = {
    "basic": ["XdY", "XdY+Z", "XdY-Z"],
    "ability_modifiers": ["XdY+STR", "XdY+DEX", "XdY+CON", "XdY+INT", "XdY+WIS", "XdY+CHA"],
    "advantage_disadvantage": ["XdYadv", "XdYdis"],
    "keep_drop": ["XdYkh", "XdYkl", "XdYdh", "XdYdl"],
    "reroll": ["XdYr", "XdYro"],
    "exploding": ["XdYx"],
    "proficiency": ["XdY+PROF"]
}