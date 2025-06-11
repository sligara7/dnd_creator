from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Dict, List, Optional, Union, Any, Tuple, Set

class Condition(Enum):
    """Standard conditions in D&D 5e (2024 Edition)."""
    BLINDED = auto()       # Can't see, auto-fail checks that need sight, attack rolls have disadvantage, attacks against have advantage
    CHARMED = auto()       # Can't attack charmer, charmer has advantage on social checks against creature
    DEAFENED = auto()      # Can't hear, auto-fail checks that need hearing
    FRIGHTENED = auto()    # Disadvantage on ability checks/attacks while source of fear in sight, can't willingly move closer to source
    GRAPPLED = auto()      # Speed is 0, ends if grappler incapacitated or separated from target
    INCAPACITATED = auto() # Can't take actions or reactions
    INVISIBLE = auto()     # Unseen (unless perceived by special means), attack rolls have advantage, attacks against have disadvantage
    PARALYZED = auto()     # Incapacitated, auto-fail STR/DEX saves, attacks have advantage, auto-crit if attacker within 5 feet
    PETRIFIED = auto()     # Transformed to stone, incapacitated, unaware of surroundings, 10× weight, doesn't age, resistance to all damage
    POISONED = auto()      # Disadvantage on attack rolls and ability checks
    PRONE = auto()         # Can only crawl, disadvantage on attack rolls, melee attacks against have advantage, ranged attacks against have disadvantage
    RESTRAINED = auto()    # Speed is 0, attack rolls have disadvantage, attacks against have advantage, disadvantage on DEX saves
    STUNNED = auto()       # Incapacitated, can't move, auto-fail STR/DEX saves, attack rolls against have advantage
    UNCONSCIOUS = auto()   # Incapacitated, can't move/speak, unaware of surroundings, drop everything, fall prone, auto-fail STR/DEX saves, attacks have advantage, auto-crit if attacker within 5 feet

class DeathSaveResult(Enum):
    """Possible results of a death saving throw."""
    SUCCESS = auto()       # Standard success (3 needed to stabilize)
    FAILURE = auto()       # Standard failure (3 causes death)
    CRITICAL_SUCCESS = auto()  # Natural 20: regain 1 HP immediately
    CRITICAL_FAILURE = auto()  # Natural 1: counts as two failures

class ConcentrationBreakResult(Enum):
    """Results of a concentration check when taking damage."""
    MAINTAINED = auto()    # Successfully maintained concentration
    BROKEN = auto()        # Lost concentration on the spell
    SPECIAL_MAINTENANCE = auto()  # Maintained through special ability (e.g., War Caster feat)

class AbstractConditions(ABC):
    """
    Abstract base class for managing conditions, death saves, exhaustion,
    and concentration in D&D 5e (2024 Edition).
    
    Conditions are temporary afflictions that alter a creature's capabilities.
    """
    
    # DC for concentration checks is 10 or half the damage taken, whichever is higher
    BASE_CONCENTRATION_DC = 10
    
    # Exhaustion now provides a -1 penalty to d20 tests per level in 2024 rules (maximum 10)
    MAX_EXHAUSTION_LEVEL = 10
    
    # Death saving throw DC
    DEATH_SAVE_DC = 10
    
    @abstractmethod
    def apply_condition(self, condition: Condition, duration: Optional[int] = None, 
                       source: Optional[str] = None) -> bool:
        """
        Apply a condition to the character.
        
        Per D&D 2024 rules, most conditions:
        - Have specific mechanical effects 
        - May have a duration (in rounds, minutes, etc.)
        - May be caused by specific sources (spells, monster abilities, etc.)
        
        Args:
            condition: Condition to apply
            duration: Duration in rounds (None for indefinite)
            source: Source of the condition
            
        Returns:
            bool: True if condition was successfully applied
        """
        pass
    
    @abstractmethod
    def remove_condition(self, condition: Condition) -> bool:
        """
        Remove a condition from the character.
        
        Per D&D 2024 rules, conditions can be removed by:
        - Spells like Lesser Restoration, Greater Restoration
        - Abilities that specifically remove conditions
        - Ending effects that caused the condition
        - Duration expiration
        
        Args:
            condition: Condition to remove
            
        Returns:
            bool: True if condition was successfully removed
        """
        pass
    
    @abstractmethod
    def has_condition(self, condition: Condition) -> bool:
        """
        Check if character has a specific condition.
        
        Args:
            condition: Condition to check
            
        Returns:
            bool: True if character has the condition
        """
        pass
    
    @abstractmethod
    def get_all_conditions(self) -> Dict[Condition, Dict[str, Any]]:
        """
        Get all conditions affecting the character.
        
        Returns:
            Dict[Condition, Dict[str, Any]]: All active conditions with their details
                including duration, source, etc.
        """
        pass
    
    @abstractmethod
    def is_immune_to_condition(self, condition: Condition) -> bool:
        """
        Check if character is immune to a specific condition.
        
        Per D&D 2024 rules:
        - Some species are immune to specific conditions
        - Some class features grant condition immunities
        - Some spells/items grant temporary condition immunities
        
        Args:
            condition: Condition to check
            
        Returns:
            bool: True if character is immune to the condition
        """
        pass
    
    @abstractmethod
    def get_condition_immunities(self) -> Set[Condition]:
        """
        Get all conditions the character is immune to.
        
        Returns:
            Set[Condition]: All condition immunities
        """
        pass
    
    @abstractmethod
    def update_condition_durations(self) -> Dict[Condition, bool]:
        """
        Update durations for all timed conditions (typically at end of turn).
        
        Returns:
            Dict[Condition, bool]: Conditions that expired during this update
        """
        pass
    
    @abstractmethod
    def add_exhaustion_level(self, levels: int = 1) -> int:
        """
        Add levels of exhaustion to the character.
        
        Per D&D 2024 rules:
        - Each level of exhaustion gives -1 penalty to d20 tests
        - At level 10, the character dies
        - Causes: Forced march, extreme environments, some spells, etc.
        
        Args:
            levels: Number of exhaustion levels to add
            
        Returns:
            int: New exhaustion level
        """
        pass
    
    @abstractmethod
    def remove_exhaustion_level(self, levels: int = 1) -> int:
        """
        Remove levels of exhaustion from the character.
        
        Per D&D 2024 rules:
        - A long rest reduces exhaustion level by 1
        - Spells like Greater Restoration remove one level
        - The Periapt of Health prevents exhaustion
        
        Args:
            levels: Number of exhaustion levels to remove
            
        Returns:
            int: New exhaustion level
        """
        pass
    
    @abstractmethod
    def get_exhaustion_level(self) -> int:
        """
        Get the character's current exhaustion level.
        
        Returns:
            int: Current exhaustion level (0-10)
        """
        pass
    
    @abstractmethod
    def get_exhaustion_penalty(self) -> int:
        """
        Get the penalty applied to d20 tests due to exhaustion.
        
        Per D&D 2024 rules:
        - Each level of exhaustion gives a -1 penalty to d20 tests
        - This includes attack rolls, saving throws, and ability checks
        
        Returns:
            int: Penalty to d20 tests (negative number)
        """
        pass
    
    @abstractmethod
    def roll_death_saving_throw(self) -> DeathSaveResult:
        """
        Roll a death saving throw.
        
        Per D&D 2024 rules:
        - Roll d20, no modifiers (unless from features like Blessing of the Dawn)
        - 10 or higher: success
        - 9 or lower: failure
        - Natural 20: regain 1 hit point
        - Natural 1: two failures
        - Three successes: become stable
        - Three failures: die
        
        Returns:
            DeathSaveResult: Result of the death save
        """
        pass
    
    @abstractmethod
    def get_death_save_count(self) -> Dict[str, int]:
        """
        Get current death saving throw success/failure counts.
        
        Returns:
            Dict[str, int]: Dictionary with:
                - "successes": Number of successes
                - "failures": Number of failures
        """
        pass
    
    @abstractmethod
    def reset_death_saves(self) -> None:
        """
        Reset death saving throw counts.
        
        This happens when:
        - Character regains any hit points
        - Character stabilizes
        - Character dies
        """
        pass
    
    @abstractmethod
    def is_stable(self) -> bool:
        """
        Check if an unconscious character is stable.
        
        Per D&D 2024 rules:
        - Stable characters don't need to make death saves
        - They remain unconscious for 1d4 hours
        - Or until they regain hit points
        
        Returns:
            bool: True if stable
        """
        pass
    
    @abstractmethod
    def stabilize(self) -> bool:
        """
        Stabilize a dying character.
        
        Per D&D 2024 rules, stabilization can occur from:
        - Three death save successes
        - Medicine check (DC 10)
        - Spare the Dying cantrip
        - Healer's kit
        
        Returns:
            bool: True if successfully stabilized
        """
        pass
    
    @abstractmethod
    def make_concentration_check(self, damage_taken: int) -> ConcentrationBreakResult:
        """
        Make a concentration check after taking damage.
        
        Per D&D 2024 rules:
        - DC equals 10 or half the damage taken, whichever is higher
        - It's a Constitution saving throw
        - War Caster feat gives advantage
        
        Args:
            damage_taken: Amount of damage that triggered the check
            
        Returns:
            ConcentrationBreakResult: Result of the concentration check
        """
        pass
    
    @abstractmethod
    def break_concentration(self) -> Dict[str, Any]:
        """
        Force break concentration on any concentration spells.
        
        Per D&D 2024 rules, concentration breaks when:
        - Character casts another concentration spell
        - Character takes damage and fails the save
        - Character is incapacitated or killed
        - Character is subject to an effect that breaks concentration
        
        Returns:
            Dict[str, Any]: Details of the broken concentration effect
        """
        pass
    
    @abstractmethod
    def is_concentrating(self) -> bool:
        """
        Check if character is currently concentrating on a spell.
        
        Returns:
            bool: True if concentrating
        """
        pass
    
    @abstractmethod
    def get_concentration_details(self) -> Dict[str, Any]:
        """
        Get details about what the character is concentrating on.
        
        Returns:
            Dict[str, Any]: Details of the concentration spell/effect
        """
        pass
    
    @abstractmethod
    def start_concentrating(self, spell_name: str, spell_level: int, duration: int) -> bool:
        """
        Start concentrating on a new spell.
        
        Per D&D 2024 rules:
        - This automatically breaks concentration on any previous spell
        
        Args:
            spell_name: Name of the spell
            spell_level: Level the spell is cast at
            duration: Duration in rounds
            
        Returns:
            bool: True if successfully started concentrating
        """
        pass
    
    @abstractmethod
    def get_condition_effects(self, condition: Condition) -> Dict[str, Any]:
        """
        Get mechanical effects of a specific condition.
        
        Args:
            condition: Condition to check
            
        Returns:
            Dict[str, Any]: Mechanical effects of the condition
        """
        pass
    
    @abstractmethod
    def apply_damage_to_dying(self, damage: int) -> Dict[str, Any]:
        """
        Apply damage to a character at 0 HP.
        
        Per D&D 2024 rules:
        - Any damage causes a death saving throw failure
        - Critical hits cause two failures
        - Damage equal to max HP causes instant death
        
        Args:
            damage: Amount of damage taken
            
        Returns:
            Dict[str, Any]: Results of applying the damage
        """
        pass
    
    @abstractmethod
    def heal_from_dying(self, healing: int) -> Dict[str, Any]:
        """
        Apply healing to a dying character.
        
        Per D&D 2024 rules:
        - Any healing brings character back to consciousness with that HP
        - Resets death saving throws
        - Removes the unconscious condition
        
        Args:
            healing: Amount of healing received
            
        Returns:
            Dict[str, Any]: Results of the healing
        """
        pass
    
    @abstractmethod
    def get_conditional_modifiers(self) -> Dict[str, int]:
        """
        Get all modifiers to rolls caused by conditions.
        
        For example:
        - Poisoned: Disadvantage on attack rolls and ability checks
        - Prone: Disadvantage on attack rolls, etc.
        
        Returns:
            Dict[str, int]: Dictionary of roll types and their modifiers
        """
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert condition data to dictionary format.
        
        Returns:
            Dict[str, Any]: Dictionary representation of conditions
        """
        pass