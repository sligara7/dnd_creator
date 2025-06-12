"""
Mechanical categories for D&D content analysis.

This enum defines categories of mechanical elements that can be extracted
from content descriptions, supporting the Creative Content Framework's
mechanical validation and balance assessment.
"""

from enum import Enum


class MechanicalCategory(Enum):
    """Categories of mechanical elements found in D&D content."""
    
    # Combat Mechanics
    DAMAGE = "damage"
    HEALING = "healing"
    ATTACK = "attack"
    DEFENSE = "defense"
    
    # Status Effects
    CONDITION = "condition"
    BUFF = "buff"
    DEBUFF = "debuff"
    
    # Dice and Checks
    ABILITY_CHECK = "ability_check"
    SAVING_THROW = "saving_throw"
    SKILL_CHECK = "skill_check"
    
    # Resources and Limits
    RESOURCE = "resource"
    USAGE_LIMIT = "usage_limit"
    RECHARGE = "recharge"
    
    # Spatial and Temporal
    DURATION = "duration"
    RANGE = "range"
    AREA = "area"
    
    # Progression
    SCALING = "scaling"
    LEVEL_REQUIREMENT = "level_requirement"
    
    # Special Mechanics
    REACTION = "reaction"
    BONUS_ACTION = "bonus_action"
    LEGENDARY_ACTION = "legendary_action"
    RITUAL = "ritual"
    CONCENTRATION = "concentration"