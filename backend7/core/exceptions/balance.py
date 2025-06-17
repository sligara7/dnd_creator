"""
Essential D&D Balance Exception Types

Streamlined balance-related exception handling following backend7 architecture.
Based on crude_functional.py patterns and essential-only philosophy.
"""

from typing import Optional, Dict, Any, List
from .base import DnDCharacterCreatorError

# ============ POWER BALANCE EXCEPTIONS ============

class PowerLevelError(DnDCharacterCreatorError):
    """Character power level balance violations."""
    
    def __init__(self, current_power: str, expected_power: str, reason: str, **kwargs):
        message = f"Power level mismatch: {current_power} vs expected {expected_power} - {reason}"
        details = {
            "current_power": current_power,
            "expected_power": expected_power,
            "reason": reason,
            **kwargs
        }
        super().__init__(message, details)
        self.current_power = current_power
        self.expected_power = expected_power

class StatArrayError(DnDCharacterCreatorError):
    """Ability score array balance violations."""
    
    def __init__(self, method: str, array: List[int], violation: str, **kwargs):
        message = f"Invalid {method} array {array}: {violation}"
        details = {
            "method": method,
            "array": array,
            "violation": violation,
            **kwargs
        }
        super().__init__(message, details)
        self.method = method
        self.array = array
        self.violation = violation

class PointBuyError(DnDCharacterCreatorError):
    """Point buy system balance violations."""
    
    def __init__(self, spent_points: int, available_points: int, issue: str, **kwargs):
        message = f"Point buy error: {spent_points}/{available_points} points - {issue}"
        details = {
            "spent_points": spent_points,
            "available_points": available_points,
            "issue": issue,
            **kwargs
        }
        super().__init__(message, details)
        self.spent_points = spent_points
        self.available_points = available_points

# ============ CAMPAIGN BALANCE EXCEPTIONS ============

class DifficultyMismatchError(DnDCharacterCreatorError):
    """Campaign difficulty and character power mismatch."""
    
    def __init__(self, character_power: str, campaign_difficulty: str, **kwargs):
        message = f"Character power ({character_power}) doesn't match campaign difficulty ({campaign_difficulty})"
        details = {
            "character_power": character_power,
            "campaign_difficulty": campaign_difficulty,
            **kwargs
        }
        super().__init__(message, details)
        self.character_power = character_power
        self.campaign_difficulty = campaign_difficulty

class TierImbalanceError(DnDCharacterCreatorError):
    """Character tier balance violations."""
    
    def __init__(self, character_level: int, expected_tier: str, actual_tier: str, **kwargs):
        message = f"Tier imbalance at level {character_level}: expected {expected_tier}, got {actual_tier}"
        details = {
            "character_level": character_level,
            "expected_tier": expected_tier,
            "actual_tier": actual_tier,
            **kwargs
        }
        super().__init__(message, details)
        self.character_level = character_level
        self.expected_tier = expected_tier
        self.actual_tier = actual_tier

# ============ EQUIPMENT BALANCE EXCEPTIONS ============

class WealthImbalanceError(DnDCharacterCreatorError):
    """Starting wealth balance violations."""
    
    def __init__(self, wealth_level: str, actual_gold: int, expected_range: tuple, **kwargs):
        message = f"Wealth imbalance: {actual_gold}gp outside {wealth_level} range {expected_range}"
        details = {
            "wealth_level": wealth_level,
            "actual_gold": actual_gold,
            "expected_range": expected_range,
            **kwargs
        }
        super().__init__(message, details)
        self.wealth_level = wealth_level
        self.actual_gold = actual_gold
        self.expected_range = expected_range

class MagicItemImbalanceError(DnDCharacterCreatorError):
    """Magic item availability balance violations."""
    
    def __init__(self, item_rarity: str, character_level: int, campaign_setting: str, **kwargs):
        message = f"Magic item imbalance: {item_rarity} item inappropriate for level {character_level} in {campaign_setting} campaign"
        details = {
            "item_rarity": item_rarity,
            "character_level": character_level,
            "campaign_setting": campaign_setting,
            **kwargs
        }
        super().__init__(message, details)
        self.item_rarity = item_rarity
        self.character_level = character_level
        self.campaign_setting = campaign_setting

# ============ MULTICLASS BALANCE EXCEPTIONS ============

class MulticlassImbalanceError(DnDCharacterCreatorError):
    """Multiclass combination balance issues."""
    
    def __init__(self, classes: List[str], imbalance_type: str, **kwargs):
        classes_str = "/".join(classes)
        message = f"Multiclass imbalance in {classes_str}: {imbalance_type}"
        details = {
            "classes": classes,
            "imbalance_type": imbalance_type,
            **kwargs
        }
        super().__init__(message, details)
        self.classes = classes
        self.imbalance_type = imbalance_type

# ============ UTILITY FUNCTIONS ============

def create_power_level_error(current: str, expected: str, reason: str) -> PowerLevelError:
    """Factory function for power level errors."""
    return PowerLevelError(current, expected, reason)

def create_stat_array_error(method: str, array: List[int], violation: str) -> StatArrayError:
    """Factory function for stat array errors."""
    return StatArrayError(method, array, violation)

def create_point_buy_error(spent: int, available: int, issue: str) -> PointBuyError:
    """Factory function for point buy errors."""
    return PointBuyError(spent, available, issue)

def is_balance_critical(error: DnDCharacterCreatorError) -> bool:
    """Check if balance error is critical to gameplay."""
    critical_types = [PowerLevelError, DifficultyMismatchError, TierImbalanceError]
    return any(isinstance(error, error_type) for error_type in critical_types)

def get_balance_severity(error: DnDCharacterCreatorError) -> str:
    """Get balance error severity level."""
    severity_map = {
        StatArrayError: "error",
        PointBuyError: "error",
        PowerLevelError: "critical",
        DifficultyMismatchError: "warning",
        TierImbalanceError: "error",
        WealthImbalanceError: "warning",
        MagicItemImbalanceError: "warning",
        MulticlassImbalanceError: "error"
    }
    return severity_map.get(type(error), "warning")

def requires_dm_approval(error: DnDCharacterCreatorError) -> bool:
    """Check if balance error requires DM approval to proceed."""
    approval_required = [
        PowerLevelError,
        MagicItemImbalanceError,
        MulticlassImbalanceError,
        WealthImbalanceError
    ]
    return any(isinstance(error, error_type) for error_type in approval_required)

# ============ ESSENTIAL EXPORTS ============

__all__ = [
    # Power balance exceptions
    'PowerLevelError',
    'StatArrayError', 
    'PointBuyError',
    
    # Campaign balance exceptions
    'DifficultyMismatchError',
    'TierImbalanceError',
    
    # Equipment balance exceptions
    'WealthImbalanceError',
    'MagicItemImbalanceError',
    
    # Multiclass balance exceptions
    'MulticlassImbalanceError',
    
    # Utility functions
    'create_power_level_error',
    'create_stat_array_error',
    'create_point_buy_error',
    'is_balance_critical',
    'get_balance_severity',
    'requires_dm_approval',
]

# ============ MODULE METADATA ============

__version__ = '1.0.0'
__description__ = 'Essential D&D balance exception handling'
__author__ = 'D&D Character Creator Backend7'

# Backend7 architecture compliance
BACKEND7_COMPLIANCE = {
    "layer": "core/exceptions",
    "focus": "balance_error_handling_only",
    "line_target": 150,
    "dependencies": ["base"],
    "philosophy": "crude_functional_inspired_simple_balance_exceptions"
}