from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Dict, List, Optional, Union, Any, Tuple, Set

class ResourceType(Enum):
    """Enumeration of character resource types in D&D 5e (2024 Edition)."""
    SPELL_SLOT = auto()      # Spell slots for spellcasting
    CLASS_RESOURCE = auto()  # Class-specific resources (ki, rage, etc.)
    FEATURE_USE = auto()     # Limited-use features (Channel Divinity, etc.)
    INSPIRATION = auto()     # D&D inspiration (advantage on one roll)
    ITEM_CHARGE = auto()     # Magic item charges
    CONSUMABLE = auto()      # Consumable items (potions, scrolls, etc.)
    HIT_DICE = auto()        # Hit dice for recovery
    ACTION = auto()          # Actions, bonus actions, reactions
    MOVEMENT = auto()        # Movement speed

class ResourceRecoveryTiming(Enum):
    """When resources recover in D&D 5e (2024 Edition)."""
    SHORT_REST = auto()      # Recovers after short or long rest
    LONG_REST = auto()       # Recovers only after long rest
    DAWN = auto()            # Recovers at dawn
    DUSK = auto()            # Recovers at dusk
    TURN_START = auto()      # Recovers at start of creature's turn
    TURN_END = auto()        # Recovers at end of creature's turn
    INITIATIVE = auto()      # Recovers when initiative is rolled
    MILESTONE = auto()       # Recovers at story milestones
    SPECIAL = auto()         # Special recovery conditions
    NEVER = auto()           # Doesn't recover (consumables)

class AbstractResources(ABC):
    """
    Abstract base class for managing character resources in D&D 5e (2024 Edition).
    
    This class defines the interface for tracking and managing various character resources:
    - Spell slots for spellcasters
    - Class-specific resources like ki points, sorcery points, etc.
    - Limited-use features like Channel Divinity
    - Inspiration
    - Magic item charges and consumables
    """
    
    @abstractmethod
    def get_spell_slots(self) -> Dict[int, Dict[str, int]]:
        """
        Get current and maximum spell slots by level.
        
        Per D&D 2024 rules, spell slots are determined by:
        - Character's class and level
        - Spellcasting or Pact Magic features
        - Multiclassing rules for combined spellcasters
        
        Returns:
            Dict[int, Dict[str, int]]: Dictionary mapping spell levels to:
                - "current": Available spell slots
                - "maximum": Maximum spell slots
        """
        pass
    
    @abstractmethod
    def use_spell_slot(self, level: int) -> bool:
        """
        Use a spell slot of the specified level.
        
        Per D&D 2024 rules:
        - Cannot use a slot if none are available
        - Can use higher level slots for lower level spells
        - Warlocks have special rules for Pact Magic slots
        
        Args:
            level: Level of spell slot to use
            
        Returns:
            bool: True if successful, False if no slot available
        """
        pass
    
    @abstractmethod
    def recover_spell_slots(self, level: int, amount: int) -> int:
        """
        Recover spell slots of a specific level.
        
        Per D&D 2024 rules:
        - Most classes recover all slots on long rest
        - Warlocks recover all Pact Magic slots on short rest
        - Some features (Arcane Recovery, Natural Recovery) restore 
          slots during short rests
        
        Args:
            level: Level of spell slots to recover
            amount: Number of slots to recover
            
        Returns:
            int: Number of slots actually recovered
        """
        pass
    
    @abstractmethod
    def create_spell_slot(self, level: int) -> bool:
        """
        Create a new spell slot (for features like Sorcerer's Font of Magic).
        
        Per D&D 2024 rules, some features allow creating temporary spell slots.
        
        Args:
            level: Level of spell slot to create
            
        Returns:
            bool: True if successful
        """
        pass
    
    @abstractmethod
    def get_class_resource(self, resource_name: str) -> Dict[str, int]:
        """
        Get information about a class-specific resource.
        
        Examples of class resources in D&D 2024:
        - Barbarian: Rage uses
        - Bard: Bardic Inspiration uses
        - Druid: Wild Shape uses
        - Ki Points (Monk)
        - Sorcery Points (Sorcerer)
        - Lay on Hands pool (Paladin)
        - Superiority Dice (Fighter)
        
        Args:
            resource_name: Name of the resource
            
        Returns:
            Dict[str, int]: Dictionary with:
                - "current": Current amount
                - "maximum": Maximum amount
        """
        pass
    
    @abstractmethod
    def use_class_resource(self, resource_name: str, amount: int = 1) -> bool:
        """
        Use a specified amount of a class resource.
        
        Args:
            resource_name: Name of the resource
            amount: Amount to use
            
        Returns:
            bool: True if successful, False if insufficient resources
        """
        pass
    
    @abstractmethod
    def recover_class_resource(self, resource_name: str, amount: int) -> int:
        """
        Recover a specified amount of a class resource.
        
        Per D&D 2024 rules, recovery timing varies by class:
        - Some recover on short rest (Warlock spells, Fighter maneuvers)
        - Some recover on long rest (Wizard Arcane Recovery)
        - Some have special recovery (Natural Recovery, Font of Magic)
        
        Args:
            resource_name: Name of the resource
            amount: Amount to recover
            
        Returns:
            int: Amount actually recovered
        """
        pass
    
    @abstractmethod
    def add_class_resource(self, resource_name: str, maximum: int, recovery: ResourceRecoveryTiming) -> bool:
        """
        Add a new class resource.
        
        Args:
            resource_name: Name of the resource
            maximum: Maximum amount
            recovery: When the resource recovers
            
        Returns:
            bool: True if successfully added
        """
        pass
    
    @abstractmethod
    def get_feature_uses(self, feature_name: str) -> Dict[str, int]:
        """
        Get current and maximum uses for a limited-use feature.
        
        Examples of limited-use features in D&D 2024:
        - Channel Divinity
        - Wild Shape
        - Action Surge
        - Second Wind
        - Cleansing Touch
        
        Args:
            feature_name: Name of the feature
            
        Returns:
            Dict[str, int]: Dictionary with:
                - "current": Current uses
                - "maximum": Maximum uses
        """
        pass
    
    @abstractmethod
    def use_feature(self, feature_name: str) -> bool:
        """
        Use a limited-use feature.
        
        Args:
            feature_name: Name of the feature
            
        Returns:
            bool: True if successful, False if no uses remain
        """
        pass
    
    @abstractmethod
    def recover_feature_use(self, feature_name: str, amount: int = 1) -> int:
        """
        Recover uses of a limited-use feature.
        
        Args:
            feature_name: Name of the feature
            amount: Number of uses to recover
            
        Returns:
            int: Number of uses actually recovered
        """
        pass
    
    @abstractmethod
    def add_limited_feature(self, feature_name: str, uses: int, 
                         recovery: ResourceRecoveryTiming) -> bool:
        """
        Add a new limited-use feature.
        
        Args:
            feature_name: Name of the feature
            uses: Number of uses
            recovery: When uses recover
            
        Returns:
            bool: True if successfully added
        """
        pass
    
    @abstractmethod
    def has_inspiration(self) -> bool:
        """
        Check if character has inspiration.
        
        Per D&D 2024 rules:
        - Inspiration is awarded by the DM for good roleplay, clever ideas, etc.
        - Some features can also grant inspiration
        - Characters can only have one inspiration at a time
        
        Returns:
            bool: True if character has inspiration
        """
        pass
    
    @abstractmethod
    def grant_inspiration(self) -> bool:
        """
        Grant inspiration to the character.
        
        Per D&D 2024 rules, a character can only have one inspiration at a time.
        
        Returns:
            bool: True if inspiration was granted (False if already had it)
        """
        pass
    
    @abstractmethod
    def use_inspiration(self) -> bool:
        """
        Use inspiration for advantage on a roll.
        
        Per D&D 2024 rules:
        - Inspiration can be used to gain advantage on one attack roll, 
          saving throw, or ability check
        - Using inspiration expends it
        
        Returns:
            bool: True if inspiration was used
        """
        pass
    
    @abstractmethod
    def get_item_charges(self, item_name: str) -> Dict[str, int]:
        """
        Get current and maximum charges for a magic item.
        
        Per D&D 2024 rules:
        - Many magic items have a limited number of charges
        - Charges are typically recovered at dawn (but can vary)
        - Some items are destroyed when the last charge is used
        
        Args:
            item_name: Name of the item
            
        Returns:
            Dict[str, int]: Dictionary with:
                - "current": Current charges
                - "maximum": Maximum charges
        """
        pass
    
    @abstractmethod
    def use_item_charge(self, item_name: str, amount: int = 1) -> bool:
        """
        Use charges from a magic item.
        
        Args:
            item_name: Name of the item
            amount: Number of charges to use
            
        Returns:
            bool: True if successful
        """
        pass
    
    @abstractmethod
    def recover_item_charges(self, item_name: str, amount: Optional[int] = None) -> int:
        """
        Recover charges for a magic item.
        
        Per D&D 2024 rules:
        - Many items recover a specific number of charges at dawn
        - Some recover all charges
        - Some have special recovery conditions
        
        Args:
            item_name: Name of the item
            amount: Number of charges to recover (None = all)
            
        Returns:
            int: Number of charges recovered
        """
        pass
    
    @abstractmethod
    def add_item_with_charges(self, item_name: str, charges: int, max_charges: int,
                           recovery: ResourceRecoveryTiming) -> bool:
        """
        Add a new item with charges to the inventory.
        
        Args:
            item_name: Name of the item
            charges: Current charges
            max_charges: Maximum charges
            recovery: When charges recover
            
        Returns:
            bool: True if successfully added
        """
        pass
    
    @abstractmethod
    def get_consumables(self) -> Dict[str, int]:
        """
        Get all consumable items and their quantities.
        
        Consumables in D&D 2024 include:
        - Potions
        - Scrolls
        - Ammunition
        - Thrown weapons
        - Spell components with costs
        
        Returns:
            Dict[str, int]: Dictionary mapping item names to quantities
        """
        pass
    
    @abstractmethod
    def use_consumable(self, item_name: str, amount: int = 1) -> bool:
        """
        Use a consumable item.
        
        Args:
            item_name: Name of the item
            amount: Quantity to use
            
        Returns:
            bool: True if successful
        """
        pass
    
    @abstractmethod
    def add_consumable(self, item_name: str, amount: int) -> int:
        """
        Add consumable items to inventory.
        
        Args:
            item_name: Name of the item
            amount: Quantity to add
            
        Returns:
            int: New total quantity
        """
        pass
    
    @abstractmethod
    def get_hit_dice(self) -> Dict[str, Dict[str, int]]:
        """
        Get current and maximum hit dice by die type.
        
        Per D&D 2024 rules:
        - Hit dice are used during short rests to recover HP
        - Characters have different die types based on class (d6, d8, d10, d12)
        - Long rest recovers up to half of maximum hit dice
        
        Returns:
            Dict[str, Dict[str, int]]: Dictionary mapping die types to:
                - "current": Available dice
                - "maximum": Maximum dice
        """
        pass
    
    @abstractmethod
    def use_hit_dice(self, die_type: str, amount: int = 1) -> Dict[str, int]:
        """
        Use hit dice during a short rest.
        
        Per D&D 2024 rules:
        - Each hit die recovers HP equal to die roll + CON modifier
        
        Args:
            die_type: Type of hit die (d6, d8, d10, d12)
            amount: Number of dice to use
            
        Returns:
            Dict[str, int]: Dictionary with:
                - "dice_spent": Dice actually spent
                - "hp_recovered": HP recovered
        """
        pass
    
    @abstractmethod
    def recover_hit_dice(self, amount: Optional[int] = None) -> Dict[str, int]:
        """
        Recover hit dice after a long rest.
        
        Per D&D 2024 rules:
        - Long rest recovers up to half of max hit dice (minimum 1)
        
        Args:
            amount: Number to recover (None = half of maximum)
            
        Returns:
            Dict[str, int]: Dictionary mapping die types to dice recovered
        """
        pass
    
    @abstractmethod
    def get_actions_remaining(self) -> Dict[str, int]:
        """
        Get remaining actions for the current turn/round.
        
        Per D&D 2024 rules, characters typically have:
        - One action
        - One bonus action
        - One reaction per round
        - Movement up to their speed
        
        Returns:
            Dict[str, int]: Dictionary with available actions
        """
        pass
    
    @abstractmethod
    def use_action(self, action_type: str) -> bool:
        """
        Use an action type.
        
        Args:
            action_type: Type of action ("action", "bonus", "reaction")
            
        Returns:
            bool: True if successful
        """
        pass
    
    @abstractmethod
    def reset_actions(self) -> None:
        """
        Reset available actions for a new turn.
        
        Per D&D 2024 rules:
        - Actions and bonus actions reset at the start of a turn
        - Reactions reset at the start of a turn
        - Movement resets at the start of a turn
        """
        pass
    
    @abstractmethod
    def get_all_resources(self) -> Dict[ResourceType, Any]:
        """
        Get all character resources.
        
        Returns:
            Dict[ResourceType, Any]: All resources by type
        """
        pass
    
    @abstractmethod
    def reset_resources_by_timing(self, recovery_timing: ResourceRecoveryTiming) -> Dict[str, Any]:
        """
        Reset all resources that recover at a specific timing.
        
        Args:
            recovery_timing: When resources recover
            
        Returns:
            Dict[str, Any]: Resources that were reset
        """
        pass
    
    @abstractmethod
    def get_resources_by_recovery(self, recovery_timing: ResourceRecoveryTiming) -> Dict[str, Any]:
        """
        Get all resources that recover at a specific timing.
        
        Args:
            recovery_timing: When resources recover
            
        Returns:
            Dict[str, Any]: Resources with that recovery timing
        """
        pass
    
    @abstractmethod
    def convert_resources(self, from_resource: str, to_resource: str, amount: int) -> Dict[str, int]:
        """
        Convert one resource type to another (e.g. sorcery points to spell slots).
        
        Per D&D 2024 rules:
        - Some classes can convert between resource types
        - Example: Sorcerer's Font of Magic can convert between sorcery points and spell slots
        - Example: Warlock's Pact Magic spell slots can be converted to sorcery points
        
        Args:
            from_resource: Resource to convert from
            to_resource: Resource to convert to
            amount: Amount to convert
            
        Returns:
            Dict[str, int]: Dictionary with conversion results
        """
        pass
    
    @abstractmethod
    def check_resource_availability(self, resource_type: ResourceType, 
                                 resource_name: str, amount: int = 1) -> bool:
        """
        Check if a specific amount of a resource is available.
        
        Args:
            resource_type: Type of resource
            resource_name: Name of the specific resource
            amount: Amount needed
            
        Returns:
            bool: True if the resource is available
        """
        pass
    
    @abstractmethod
    def apply_resource_modifiers(self, modifiers: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply modifiers to resources (e.g. from magic items, feats, etc.).
        
        Examples:
        - Rod of the Pact Keeper: +N to Warlock spell save DC and attack rolls
        - Pearl of Power: Recover one expended spell slot up to 3rd level
        
        Args:
            modifiers: Dictionary of modifiers to apply
            
        Returns:
            Dict[str, Any]: Results of applying modifiers
        """
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert resource data to dictionary format.
        
        Returns:
            Dict[str, Any]: Dictionary representation of resources
        """
        pass