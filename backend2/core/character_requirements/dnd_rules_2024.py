from abc import ABC
from enum import Enum
from typing import Dict, List, Set, Optional, Union, Tuple, Any

class DnDRules2024(ABC):
    """
    Abstract base class defining the rules for D&D 2024 Edition character creation.
    Contains constants and validation methods to enforce the rules of character creation.
    """
    
    # Ability Score Rules
    ABILITY_SCORE_MIN = 3
    ABILITY_SCORE_MAX = 20
    STANDARD_ARRAY = [15, 14, 13, 12, 10, 8]
    POINT_BUY_POINTS = 27
    POINT_BUY_COSTS = {
        8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 13: 5,
        14: 7, 15: 9, 16: 11, 17: 14, 18: 18
    }
    
    # Character Level Rules
    MIN_LEVEL = 1
    MAX_LEVEL = 20
    XP_BY_LEVEL = {
        1: 0, 2: 300, 3: 900, 4: 2700, 5: 6500, 6: 14000, 7: 23000, 8: 34000,
        9: 48000, 10: 64000, 11: 85000, 12: 100000, 13: 120000, 14: 140000,
        15: 165000, 16: 195000, 17: 225000, 18: 265000, 19: 305000, 20: 355000
    }
    
    # Proficiency Bonus by Level
    PROFICIENCY_BONUS_BY_LEVEL = {
        1: 2, 2: 2, 3: 2, 4: 2,
        5: 3, 6: 3, 7: 3, 8: 3,
        9: 4, 10: 4, 11: 4, 12: 4,
        13: 5, 14: 5, 15: 5, 16: 5,
        17: 6, 18: 6, 19: 6, 20: 6
    }
    
    # Hit Die by Class
    HIT_DIE_BY_CLASS = {
        "Barbarian": 12,
        "Fighter": 10, 
        "Paladin": 10,
        "Ranger": 10,
        "Monk": 8,
        "Rogue": 8,
        "Warlock": 8,
        "Bard": 8,
        "Cleric": 8,
        "Druid": 8,
        "Artificer": 8,
        "Wizard": 6,
        "Sorcerer": 6
    }
    
    # Valid Character Classes
    VALID_CLASSES = {
        "Artificer", "Barbarian", "Bard", "Cleric", "Druid", "Fighter",
        "Monk", "Paladin", "Ranger", "Rogue", "Sorcerer", "Warlock", "Wizard"
    }
    
    # Valid Alignments
    VALID_ETHICAL_ALIGNMENTS = {"Lawful", "Neutral", "Chaotic"}
    VALID_MORAL_ALIGNMENTS = {"Good", "Neutral", "Evil"}
    
    # Skills and their ability associations
    SKILLS = {
        "Athletics": "strength",
        "Acrobatics": "dexterity",
        "Sleight of Hand": "dexterity",
        "Stealth": "dexterity",
        "Arcana": "intelligence",
        "History": "intelligence",
        "Investigation": "intelligence",
        "Nature": "intelligence",
        "Religion": "intelligence",
        "Animal Handling": "wisdom",
        "Insight": "wisdom",
        "Medicine": "wisdom",
        "Perception": "wisdom",
        "Survival": "wisdom",
        "Deception": "charisma",
        "Intimidation": "charisma",
        "Performance": "charisma",
        "Persuasion": "charisma"
    }
    
    # Spellcasting
    MAX_SPELL_LEVEL = 9
    SPELL_SLOTS_BY_LEVEL = {
        # Format: class_level: [1st, 2nd, 3rd, 4th, 5th, 6th, 7th, 8th, 9th]
        1: [2, 0, 0, 0, 0, 0, 0, 0, 0],
        2: [3, 0, 0, 0, 0, 0, 0, 0, 0],
        3: [4, 2, 0, 0, 0, 0, 0, 0, 0],
        4: [4, 3, 0, 0, 0, 0, 0, 0, 0],
        5: [4, 3, 2, 0, 0, 0, 0, 0, 0],
        6: [4, 3, 3, 0, 0, 0, 0, 0, 0],
        7: [4, 3, 3, 1, 0, 0, 0, 0, 0],
        8: [4, 3, 3, 2, 0, 0, 0, 0, 0],
        9: [4, 3, 3, 3, 1, 0, 0, 0, 0],
        10: [4, 3, 3, 3, 2, 0, 0, 0, 0],
        11: [4, 3, 3, 3, 2, 1, 0, 0, 0],
        12: [4, 3, 3, 3, 2, 1, 0, 0, 0],
        13: [4, 3, 3, 3, 2, 1, 1, 0, 0],
        14: [4, 3, 3, 3, 2, 1, 1, 0, 0],
        15: [4, 3, 3, 3, 2, 1, 1, 1, 0],
        16: [4, 3, 3, 3, 2, 1, 1, 1, 0],
        17: [4, 3, 3, 3, 2, 1, 1, 1, 1],
        18: [4, 3, 3, 3, 3, 1, 1, 1, 1],
        19: [4, 3, 3, 3, 3, 2, 1, 1, 1],
        20: [4, 3, 3, 3, 3, 2, 2, 1, 1]
    }
    
    # Multiclassing ability score requirements
    MULTICLASS_REQUIREMENTS = {
        "Artificer": {"intelligence": 13},
        "Barbarian": {"strength": 13},
        "Bard": {"charisma": 13},
        "Cleric": {"wisdom": 13},
        "Druid": {"wisdom": 13},
        "Fighter": {"strength": 13, "dexterity": 13},  # Either STR or DEX
        "Monk": {"dexterity": 13, "wisdom": 13},
        "Paladin": {"strength": 13, "charisma": 13},
        "Ranger": {"dexterity": 13, "wisdom": 13},
        "Rogue": {"dexterity": 13},
        "Sorcerer": {"charisma": 13},
        "Warlock": {"charisma": 13},
        "Wizard": {"intelligence": 13}
    }
    
    # Equipment and Magic Items
    MAX_ATTUNED_ITEMS = 3
    ENCUMBRANCE_MULTIPLIER = 5  # Pounds per point of Strength
    HEAVY_LOAD_THRESHOLD = 2    # Times Strength score
    
    # Character Sizes
    VALID_SIZES = {"Tiny", "Small", "Medium", "Large", "Huge", "Gargantuan"}
    
    # Movement speeds
    BASE_MOVEMENT_SPEED = 30
    
    # Validation Methods
    @classmethod
    def is_valid_ability_score(cls, value: int) -> bool:
        """Check if an ability score is within valid range."""
        return cls.ABILITY_SCORE_MIN <= value <= cls.ABILITY_SCORE_MAX
    
    @classmethod
    def is_valid_level(cls, value: int) -> bool:
        """Check if a character level is valid."""
        return cls.MIN_LEVEL <= value <= cls.MAX_LEVEL
    
    @classmethod
    def is_valid_class(cls, class_name: str) -> bool:
        """Check if a class name is valid."""
        return class_name in cls.VALID_CLASSES
    
    @classmethod
    def is_valid_alignment(cls, ethical: str, moral: str) -> bool:
        """Check if alignment combination is valid."""
        return (ethical in cls.VALID_ETHICAL_ALIGNMENTS and 
                moral in cls.VALID_MORAL_ALIGNMENTS)
    
    @classmethod
    def is_valid_skill(cls, skill_name: str) -> bool:
        """Check if a skill name is valid."""
        return skill_name in cls.SKILLS
    
    @classmethod
    def is_valid_size(cls, size: str) -> bool:
        """Check if a size category is valid."""
        return size in cls.VALID_SIZES
    
    @classmethod
    def get_proficiency_bonus(cls, level: int) -> int:
        """Get proficiency bonus for a specific level."""
        if not cls.is_valid_level(level):
            raise ValueError(f"Invalid level: {level}")
        return cls.PROFICIENCY_BONUS_BY_LEVEL.get(level, 2)
    
    @classmethod
    def get_ability_modifier(cls, score: int) -> int:
        """Calculate ability modifier from score."""
        if not cls.is_valid_ability_score(score):
            raise ValueError(f"Invalid ability score: {score}")
        return (score - 10) // 2
    
    @classmethod
    def can_multiclass_into(cls, new_class: str, ability_scores: Dict[str, int]) -> Tuple[bool, str]:
        """Check if a character meets multiclass requirements."""
        if not cls.is_valid_class(new_class):
            return False, f"Invalid class: {new_class}"
            
        requirements = cls.MULTICLASS_REQUIREMENTS.get(new_class, {})
        for ability, min_score in requirements.items():
            if ability_scores.get(ability, 0) < min_score:
                return False, f"Requires {ability} {min_score}+ to multiclass into {new_class}"
                
        return True, f"Can multiclass into {new_class}"
    
    @classmethod
    def get_carrying_capacity(cls, strength: int, size: str) -> int:
        """Calculate carrying capacity in pounds."""
        if not cls.is_valid_ability_score(strength):
            raise ValueError(f"Invalid strength score: {strength}")
            
        # Base carrying capacity
        capacity = strength * cls.ENCUMBRANCE_MULTIPLIER
        
        # Size modifiers
        if size == "Tiny":
            capacity //= 2
        elif size == "Large":
            capacity *= 2
        elif size == "Huge":
            capacity *= 4
        elif size == "Gargantuan":
            capacity *= 8
            
        return capacity
    
    @classmethod
    def get_point_buy_cost(cls, score: int) -> int:
        """Get point buy cost for a specific ability score."""
        return cls.POINT_BUY_COSTS.get(score, 0)
    
    @classmethod
    def validate_standard_array(cls, scores: List[int]) -> bool:
        """Check if a set of scores matches the standard array."""
        if len(scores) != 6:
            return False
        return sorted(scores) == sorted(cls.STANDARD_ARRAY)
    
    @classmethod
    def calculate_level_from_xp(cls, xp: int) -> int:
        """Determine character level from XP."""
        for level in range(cls.MAX_LEVEL, 0, -1):
            if xp >= cls.XP_BY_LEVEL[level]:
                return level
        return 1
    
    @classmethod
    def get_xp_for_next_level(cls, current_level: int) -> Optional[int]:
        """Get XP required for next level."""
        if current_level >= cls.MAX_LEVEL:
            return None
        return cls.XP_BY_LEVEL[current_level + 1]
    
    @classmethod
    def get_max_spell_slots(cls, caster_level: int, slot_level: int) -> int:
        """Get maximum spell slots for a full caster at a given level."""
        if not cls.is_valid_level(caster_level) or slot_level < 1 or slot_level > cls.MAX_SPELL_LEVEL:
            return 0
        return cls.SPELL_SLOTS_BY_LEVEL[caster_level][slot_level - 1]
    
    @classmethod
    def get_multiclass_spellcaster_level(cls, class_levels: Dict[str, int]) -> int:
        """
        Calculate multiclass spellcaster level for spell slots.
        
        Full casters: Bard, Cleric, Druid, Sorcerer, Wizard
        Half casters: Paladin, Ranger
        Third casters: Artificer, Fighter (Eldritch Knight), Rogue (Arcane Trickster)
        Pact Magic: Warlock (handled separately)
        """
        full_caster_levels = 0
        half_caster_levels = 0
        third_caster_levels = 0
        
        for class_name, level in class_levels.items():
            if class_name in {"Bard", "Cleric", "Druid", "Sorcerer", "Wizard"}:
                full_caster_levels += level
            elif class_name in {"Paladin", "Ranger"}:
                half_caster_levels += level
            elif class_name == "Artificer":
                # Artificer rounds up, unlike other half-casters
                half_caster_levels += level
            # Would need subclass info for Fighter (EK) and Rogue (AT)
        
        # Half casters contribute half their level, rounded down
        # Third casters contribute a third of their level, rounded down
        return full_caster_levels + (half_caster_levels // 2) + (third_caster_levels // 3)