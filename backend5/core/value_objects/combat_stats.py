from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass(frozen=True)
class AttackRoll:
    """Value object representing an attack roll."""
    attack_bonus: int
    damage_dice: str
    damage_bonus: int
    damage_type: str
    critical_range: int = 20
    
    @property
    def average_damage(self) -> float:
        """Calculate average damage per hit."""
        # Parse dice and calculate average
        pass

@dataclass(frozen=True)  
class DefensiveStats:
    """Value object for defensive statistics."""
    armor_class: int
    hit_points: int
    saving_throw_bonuses: Dict[str, int]
    damage_resistances: List[str]
    damage_immunities: List[str]
    condition_immunities: List[str]