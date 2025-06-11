from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Dict, List, Optional, Union, Any, Tuple, Set

class AttackType(Enum):
    """Types of attacks in D&D 5e (2024 Edition)."""
    MELEE_WEAPON = auto()    # Melee weapon attacks
    RANGED_WEAPON = auto()   # Ranged weapon attacks
    MELEE_SPELL = auto()     # Melee spell attacks
    RANGED_SPELL = auto()    # Ranged spell attacks
    UNARMED = auto()         # Unarmed strikes
    IMPROVISED = auto()      # Improvised weapon attacks
    SPECIAL = auto()         # Special attack types (monster abilities, etc.)

class DamageType(Enum):
    """Damage types in D&D 5e (2024 Edition)."""
    ACID = auto()
    BLUDGEONING = auto()
    COLD = auto()
    FIRE = auto()
    FORCE = auto()
    LIGHTNING = auto()
    NECROTIC = auto()
    PIERCING = auto()
    POISON = auto()
    PSYCHIC = auto()
    RADIANT = auto()
    SLASHING = auto()
    THUNDER = auto()

class DamageModifierType(Enum):
    """How damage is modified in D&D 5e (2024 Edition)."""
    NORMAL = auto()          # Normal damage
    RESISTANCE = auto()      # Half damage (rounded down)
    VULNERABILITY = auto()   # Double damage
    IMMUNITY = auto()        # No damage
    SPECIAL = auto()         # Special damage modification (e.g., Rage, Heavy Weapon Master)

class AbstractCombatStats(ABC):
    """
    Abstract base class for managing combat statistics in D&D 5e (2024 Edition).
    
    This class handles all combat-related calculations including:
    - Initiative
    - Attack rolls and modifiers
    - Damage calculations
    - Critical hits
    - Saving throws
    """
    
    # Standard combat constants
    STANDARD_CRITICAL_HIT_THRESHOLD = 20
    STANDARD_CRITICAL_MISS_THRESHOLD = 1
    STANDARD_ADVANTAGE_BONUS = 3.5  # Average statistical bonus from advantage
    
    @abstractmethod
    def calculate_initiative(self) -> int:
        """
        Calculate initiative bonus.
        
        Per D&D 2024 rules:
        - Base initiative is the Dexterity modifier
        - Some features add bonuses (Alert feat, etc.)
        - Some features allow using different abilities
        
        Returns:
            int: Initiative modifier
        """
        pass
    
    @abstractmethod
    def roll_initiative(self) -> int:
        """
        Roll initiative for combat.
        
        Per D&D 2024 rules:
        - d20 + initiative bonus
        
        Returns:
            int: Initiative roll result
        """
        pass
    
    @abstractmethod
    def get_attack_bonus(self, attack_type: AttackType, weapon_name: Optional[str] = None,
                      spell_name: Optional[str] = None) -> int:
        """
        Calculate attack bonus for a specific attack.
        
        Per D&D 2024 rules:
        - Weapon attacks: Ability modifier + proficiency (if proficient)
        - Spell attacks: Spellcasting ability + proficiency
        - Unarmed strikes: STR modifier + proficiency
        - Improvised: Ability modifier (typically no proficiency)
        
        Args:
            attack_type: Type of attack
            weapon_name: Name of weapon (for weapon attacks)
            spell_name: Name of spell (for spell attacks)
            
        Returns:
            int: Total attack bonus
        """
        pass
    
    @abstractmethod
    def calculate_spell_attack_bonus(self) -> int:
        """
        Calculate spell attack bonus.
        
        Per D&D 2024 rules:
        - Spellcasting ability modifier + proficiency bonus
        
        Returns:
            int: Spell attack bonus
        """
        pass
    
    @abstractmethod
    def calculate_spell_save_dc(self) -> int:
        """
        Calculate spell save DC.
        
        Per D&D 2024 rules:
        - 8 + spellcasting ability modifier + proficiency bonus
        
        Returns:
            int: Spell save DC
        """
        pass
    
    @abstractmethod
    def calculate_damage(self, attack_type: AttackType, weapon_name: Optional[str] = None,
                      spell_name: Optional[str] = None, spell_level: Optional[int] = None,
                      is_critical: bool = False) -> Dict[str, Any]:
        """
        Calculate damage for an attack.
        
        Per D&D 2024 rules:
        - Weapon damage die + ability modifier
        - Critical hits: Extra dice (typically double dice)
        - Spell damage based on spell and spell level
        
        Args:
            attack_type: Type of attack
            weapon_name: Name of weapon (for weapon attacks)
            spell_name: Name of spell (for spell attacks)
            spell_level: Level spell is cast at (for spells)
            is_critical: Whether the attack is a critical hit
            
        Returns:
            Dict[str, Any]: Dictionary with damage details
        """
        pass
    
    @abstractmethod
    def determine_critical_threshold(self, attack_type: AttackType, 
                                  weapon_name: Optional[str] = None) -> int:
        """
        Determine critical hit threshold for an attack.
        
        Per D&D 2024 rules:
        - Standard: Natural 20
        - Some features modify this (Champion Fighter, Hexblade, etc.)
        
        Args:
            attack_type: Type of attack
            weapon_name: Name of weapon (for weapon attacks)
            
        Returns:
            int: Minimum roll for a critical hit
        """
        pass
    
    @abstractmethod
    def calculate_critical_hit_damage(self, base_damage: Dict[DamageType, int], 
                                    attack_type: AttackType) -> Dict[DamageType, int]:
        """
        Calculate critical hit damage.
        
        Per D&D 2024 rules:
        - Roll all damage dice twice and add them together
        - Modifiers are not doubled
        - Some features add extra dice on crits
        
        Args:
            base_damage: Base damage by damage type
            attack_type: Type of attack
            
        Returns:
            Dict[DamageType, int]: Critical hit damage by damage type
        """
        pass
    
    @abstractmethod
    def calculate_saving_throw_bonus(self, ability: str) -> int:
        """
        Calculate bonus for a saving throw.
        
        Per D&D 2024 rules:
        - Base: Ability modifier
        - Add proficiency bonus if proficient
        - Some features add bonuses to specific saves
        
        Args:
            ability: Ability score (STR, DEX, CON, INT, WIS, CHA)
            
        Returns:
            int: Total saving throw bonus
        """
        pass
    
    @abstractmethod
    def has_advantage_on_attack(self, attack_type: AttackType, 
                             target_condition: Optional[List[str]] = None) -> Tuple[bool, str]:
        """
        Check if character has advantage on an attack roll.
        
        Per D&D 2024 rules, advantage sources include:
        - Attacking a prone target (melee only)
        - Attacking an invisible target
        - Attacking with combat advantage (flanking, optional rule)
        - Attacking from hiding
        
        Args:
            attack_type: Type of attack
            target_condition: Conditions affecting the target
            
        Returns:
            Tuple[bool, str]: (Has advantage, reason)
        """
        pass
    
    @abstractmethod
    def has_disadvantage_on_attack(self, attack_type: AttackType, 
                                target_condition: Optional[List[str]] = None) -> Tuple[bool, str]:
        """
        Check if character has disadvantage on an attack roll.
        
        Per D&D 2024 rules, disadvantage sources include:
        - Attacking while prone
        - Attacking an invisible target
        - Attacking at long range
        - Attacking while poisoned
        
        Args:
            attack_type: Type of attack
            target_condition: Conditions affecting the target
            
        Returns:
            Tuple[bool, str]: (Has disadvantage, reason)
        """
        pass
    
    @abstractmethod
    def get_damage_modifiers(self, damage_type: DamageType) -> DamageModifierType:
        """
        Get character's damage modifiers for a damage type.
        
        Per D&D 2024 rules:
        - Resistance: Half damage
        - Vulnerability: Double damage
        - Immunity: No damage
        
        Args:
            damage_type: Type of damage
            
        Returns:
            DamageModifierType: How damage is modified
        """
        pass
    
    @abstractmethod
    def apply_damage_modifiers(self, damage: Dict[DamageType, int]) -> Dict[DamageType, int]:
        """
        Apply resistances, vulnerabilities, etc. to damage.
        
        Args:
            damage: Raw damage by damage type
            
        Returns:
            Dict[DamageType, int]: Modified damage by damage type
        """
        pass
    
    @abstractmethod
    def get_weapon_properties(self, weapon_name: str) -> Dict[str, Any]:
        """
        Get properties of a weapon that affect combat.
        
        Per D&D 2024 rules, relevant properties include:
        - Damage die
        - Damage type
        - Range
        - Properties (finesse, heavy, light, two-handed, etc.)
        
        Args:
            weapon_name: Name of the weapon
            
        Returns:
            Dict[str, Any]: Weapon properties
        """
        pass
    
    @abstractmethod
    def modify_attack_roll(self, base_roll: int, attack_type: AttackType, 
                        has_advantage: bool = False, 
                        has_disadvantage: bool = False) -> Dict[str, Any]:
        """
        Apply all modifiers to an attack roll.
        
        Args:
            base_roll: Base d20 roll
            attack_type: Type of attack
            has_advantage: Whether attack has advantage
            has_disadvantage: Whether attack has disadvantage
            
        Returns:
            Dict[str, Any]: Modified attack roll details
        """
        pass
    
    @abstractmethod
    def get_weapon_damage_die(self, weapon_name: str) -> str:
        """
        Get the damage die for a weapon.
        
        Args:
            weapon_name: Name of the weapon
            
        Returns:
            str: Damage die (e.g., "1d8", "2d6")
        """
        pass
    
    @abstractmethod
    def get_ability_for_attack(self, attack_type: AttackType, 
                            weapon_name: Optional[str] = None) -> str:
        """
        Determine which ability modifier to use for an attack.
        
        Per D&D 2024 rules:
        - Melee weapons: STR by default, or DEX for finesse
        - Ranged weapons: DEX by default
        - Thrown weapons: STR for melee weapons, DEX for ranged
        - Spell attacks: Spellcasting ability
        
        Args:
            attack_type: Type of attack
            weapon_name: Name of weapon (for weapon attacks)
            
        Returns:
            str: Ability to use (STR, DEX, etc.)
        """
        pass
    
    @abstractmethod
    def calculate_attack_damage_modifier(self, attack_type: AttackType, 
                                      weapon_name: Optional[str] = None) -> int:
        """
        Calculate ability modifier for damage.
        
        Per D&D 2024 rules:
        - Melee weapons: STR modifier
        - Ranged weapons: DEX modifier
        - Finesse weapons: STR or DEX (whichever used for attack)
        - Thrown weapons: Same as attack
        - Special cases: Great Weapon Fighting, Dueling style, etc.
        
        Args:
            attack_type: Type of attack
            weapon_name: Name of weapon (for weapon attacks)
            
        Returns:
            int: Damage modifier
        """
        pass
    
    @abstractmethod
    def can_make_opportunity_attack(self) -> bool:
        """
        Check if character can make an opportunity attack.
        
        Per D&D 2024 rules:
        - Must have reaction available
        - Must not be incapacitated
        
        Returns:
            bool: True if can make opportunity attack
        """
        pass
    
    @abstractmethod
    def calculate_grapple_modifier(self) -> int:
        """
        Calculate modifier for grapple attempts.
        
        Per D&D 2024 rules:
        - Athletics (STR) check
        - Target contests with Athletics (STR) or Acrobatics (DEX)
        
        Returns:
            int: Grapple check modifier
        """
        pass
    
    @abstractmethod
    def calculate_shove_modifier(self) -> int:
        """
        Calculate modifier for shove attempts.
        
        Per D&D 2024 rules:
        - Athletics (STR) check
        - Target contests with Athletics (STR) or Acrobatics (DEX)
        
        Returns:
            int: Shove check modifier
        """
        pass
    
    @abstractmethod
    def get_special_attacks(self) -> Dict[str, Dict[str, Any]]:
        """
        Get special attacks available to the character.
        
        Examples in D&D 2024:
        - Sneak Attack (Rogue)
        - Divine Smite (Paladin)
        - Flurry of Blows (Monk)
        - Extra Attack (Fighter, etc.)
        
        Returns:
            Dict[str, Dict[str, Any]]: Special attacks with details
        """
        pass
    
    @abstractmethod
    def get_weapon_attack_options(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all weapon attack options available to character.
        
        Returns:
            Dict[str, Dict[str, Any]]: Weapon attacks with details
        """
        pass
    
    @abstractmethod
    def get_spell_attack_options(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all spell attack options available to character.
        
        Returns:
            Dict[str, Dict[str, Any]]: Spell attacks with details
        """
        pass
    
    @abstractmethod
    def calculate_two_weapon_fighting_damage(self, main_hand_weapon: str, 
                                          off_hand_weapon: str) -> Dict[str, Any]:
        """
        Calculate damage for two-weapon fighting.
        
        Per D&D 2024 rules:
        - Off-hand weapon must have light property
        - No ability modifier to damage unless Two-Weapon Fighting style
        
        Args:
            main_hand_weapon: Main hand weapon name
            off_hand_weapon: Off-hand weapon name
            
        Returns:
            Dict[str, Any]: Two-weapon fighting damage details
        """
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert combat stats to dictionary format.
        
        Returns:
            Dict[str, Any]: Dictionary representation of combat stats
        """
        pass