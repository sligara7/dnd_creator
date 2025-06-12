# core/entities/character_state.py
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from datetime import datetime

@dataclass
class CharacterState:
    """
    Pure entity representing character's current gameplay state.
    Contains only data and simple getters - no business logic.
    """
    
    # Health and Resources
    current_hit_points: int = 0
    temporary_hit_points: int = 0
    hit_dice_remaining: Dict[str, int] = field(default_factory=dict)
    
    # Spellcasting State
    spell_slots_remaining: Dict[int, int] = field(default_factory=dict)
    spells_prepared: List[str] = field(default_factory=list)
    
    # Action Economy
    actions_used: int = 0
    bonus_actions_used: int = 0
    reactions_used: int = 0
    
    # Conditions and Effects
    active_conditions: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    exhaustion_level: int = 0
    
    # Equipment State
    armor: Optional[str] = None
    shield: bool = False
    attuned_items: List[str] = field(default_factory=list)
    
    # Currency
    currency: Dict[str, int] = field(default_factory=lambda: {
        "copper": 0, "silver": 0, "electrum": 0, "gold": 0, "platinum": 0
    })
    
    # Session Tracking
    last_long_rest: Optional[datetime] = None
    last_short_rest: Optional[datetime] = None
    notes: Dict[str, str] = field(default_factory=dict)