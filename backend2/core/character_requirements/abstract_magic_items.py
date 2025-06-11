from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Dict, List, Optional, Union, Any, Tuple, Set

class MagicItemRarity(Enum):
    """Magic item rarity classifications in D&D 5e (2024 Edition)."""
    COMMON = auto()
    UNCOMMON = auto()
    RARE = auto()
    VERY_RARE = auto()
    LEGENDARY = auto()
    ARTIFACT = auto()

class MagicItemType(Enum):
    """Types of magic items in D&D 5e (2024 Edition)."""
    ARMOR = auto()
    WEAPON = auto()
    POTION = auto()
    RING = auto()
    ROD = auto()
    SCROLL = auto()
    STAFF = auto()
    WAND = auto()
    WONDEROUS = auto()

class ItemSlot(Enum):
    """Body slots where magic items can be worn in D&D 5e (2024 Edition)."""
    HEAD = auto()        # Helmets, circlets, etc.
    EYES = auto()        # Goggles, eye patches, etc.
    NECK = auto()        # Amulets, necklaces, etc.
    SHOULDERS = auto()   # Cloaks, mantles, etc.
    CHEST = auto()       # Armor, robes, etc.
    BODY = auto()        # Robes, vestments, etc. (full body)
    WAIST = auto()       # Belts, girdles, etc.
    WRISTS = auto()      # Bracers, bracelets, etc.
    HANDS = auto()       # Gloves, gauntlets, etc.
    FINGERS = auto()     # Rings (typically limited to 2)
    FEET = auto()        # Boots, shoes, etc.
    HELD = auto()        # Weapons, shields, orbs, etc.

class IdentificationState(Enum):
    """States of magic item identification in D&D 5e (2024 Edition)."""
    UNIDENTIFIED = auto()     # Properties unknown
    PARTIALLY_IDENTIFIED = auto()  # Some properties known
    IDENTIFIED = auto()       # All properties known
    ATTUNED = auto()          # Fully identified and attuned

class AbstractMagicItems(ABC):
    """
    Abstract base class for magic item mechanics in D&D 5e (2024 Edition).
    
    This class handles all aspects of magic item interaction including:
    - Item rarity and properties
    - Attunement rules
    - Charge management
    - Item identification
    - Item usage and effects
    """
    
    # Maximum number of attuned items per D&D 2024 rules
    MAX_ATTUNED_ITEMS = 3
    
    # Time required for attunement (in hours)
    ATTUNEMENT_TIME = 1
    
    # Base prices by rarity per DMG guidelines
    ITEM_PRICE_RANGES = {
        MagicItemRarity.COMMON: (50, 100),
        MagicItemRarity.UNCOMMON: (101, 500),
        MagicItemRarity.RARE: (501, 5000),
        MagicItemRarity.VERY_RARE: (5001, 50000),
        MagicItemRarity.LEGENDARY: (50001, 500000),
        MagicItemRarity.ARTIFACT: (None, None)  # Priceless
    }
    
    @abstractmethod
    def add_magic_item(self, item_name: str, item_type: MagicItemType, 
                     rarity: MagicItemRarity, requires_attunement: bool = False,
                     charges: Optional[int] = None, max_charges: Optional[int] = None,
                     properties: Dict[str, Any] = None) -> bool:
        """
        Add a magic item to the character's inventory.
        
        Per D&D 2024 rules, magic items have:
        - A type (armor, weapon, wondrous, etc.)
        - A rarity (common to artifact)
        - Some require attunement
        - Some have charges
        
        Args:
            item_name: Name of the item
            item_type: Type of magic item
            rarity: Item rarity
            requires_attunement: Whether attunement is required
            charges: Current charges (if applicable)
            max_charges: Maximum charges (if applicable)
            properties: Additional item properties
            
        Returns:
            bool: True if successfully added
        """
        pass
    
    @abstractmethod
    def remove_magic_item(self, item_name: str) -> bool:
        """
        Remove a magic item from the character's inventory.
        
        Per D&D 2024 rules:
        - Removing an attuned item breaks attunement
        
        Args:
            item_name: Name of the item
            
        Returns:
            bool: True if successfully removed
        """
        pass
    
    @abstractmethod
    def get_magic_item_details(self, item_name: str) -> Dict[str, Any]:
        """
        Get details about a specific magic item.
        
        Returns:
            Dict[str, Any]: Complete item details
        """
        pass
    
    @abstractmethod
    def get_all_magic_items(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all magic items in the character's inventory.
        
        Returns:
            Dict[str, Dict[str, Any]]: Dictionary mapping item names to details
        """
        pass
    
    @abstractmethod
    def attune_to_item(self, item_name: str) -> Tuple[bool, str]:
        """
        Attempt to attune to a magic item.
        
        Per D&D 2024 rules:
        - Characters can be attuned to a maximum of 3 items
        - Attunement requires a short rest (1 hour)
        - Some items have prerequisites for attunement
        
        Args:
            item_name: Name of the item
            
        Returns:
            Tuple[bool, str]: (Success, message)
        """
        pass
    
    @abstractmethod
    def break_attunement(self, item_name: str) -> bool:
        """
        Break attunement with a magic item.
        
        Per D&D 2024 rules:
        - Attunement ends if:
            - Item is more than 100 feet away for 24+ hours
            - Character dies
            - Another character attunes to the item
            - Character voluntarily breaks attunement (during a short rest)
        
        Args:
            item_name: Name of the item
            
        Returns:
            bool: True if attunement was successfully broken
        """
        pass
    
    @abstractmethod
    def get_attuned_items(self) -> List[str]:
        """
        Get all items the character is currently attuned to.
        
        Returns:
            List[str]: Names of attuned items
        """
        pass
    
    @abstractmethod
    def can_attune_to_more_items(self) -> bool:
        """
        Check if character can attune to additional items.
        
        Per D&D 2024 rules:
        - Maximum of 3 attuned items per character
        - Some special features may modify this limit
        
        Returns:
            bool: True if character can attune to more items
        """
        pass
    
    @abstractmethod
    def get_attunement_limit(self) -> int:
        """
        Get character's maximum number of attunable items.
        
        Returns:
            int: Maximum number of items character can be attuned to
        """
        pass
    
    @abstractmethod
    def use_item_charge(self, item_name: str, charges: int = 1) -> Tuple[bool, int]:
        """
        Use charges from a magic item.
        
        Per D&D 2024 rules:
        - Many items have limited charges
        - Some are destroyed when last charge is used
        - Some risk being destroyed when last charge is used
        
        Args:
            item_name: Name of the item
            charges: Number of charges to use
            
        Returns:
            Tuple[bool, int]: (Success, charges remaining)
        """
        pass
    
    @abstractmethod
    def recharge_item(self, item_name: str, charges: Optional[int] = None) -> Tuple[bool, int]:
        """
        Recharge a magic item.
        
        Per D&D 2024 rules:
        - Many items recover charges at dawn
        - Some recover at other times or under special circumstances
        - Some recover a fixed amount, others variable (e.g., 1d4+2)
        
        Args:
            item_name: Name of the item
            charges: Number of charges to restore (None = full recharge)
            
        Returns:
            Tuple[bool, int]: (Success, new charge total)
        """
        pass
    
    @abstractmethod
    def recharge_all_items(self, time_of_day: str = "dawn") -> Dict[str, int]:
        """
        Recharge all magic items that recover at a specific time.
        
        Args:
            time_of_day: When items recharge ("dawn", "dusk", etc.)
            
        Returns:
            Dict[str, int]: Items recharged with their new charge totals
        """
        pass
    
    @abstractmethod
    def identify_item(self, item_name: str, 
                   method: str = "identify_spell") -> Tuple[bool, Dict[str, Any]]:
        """
        Attempt to identify a magic item.
        
        Per D&D 2024 rules:
        - The identify spell reveals most properties
        - A short rest with physical contact can reveal properties
        - Some properties only reveal themselves when certain conditions are met
        - Some cursed items disguise their true nature
        
        Args:
            item_name: Name of the item
            method: Method of identification
            
        Returns:
            Tuple[bool, Dict[str, Any]]: (Success, revealed properties)
        """
        pass
    
    @abstractmethod
    def get_item_identification_state(self, item_name: str) -> IdentificationState:
        """
        Get current identification state of an item.
        
        Args:
            item_name: Name of the item
            
        Returns:
            IdentificationState: Current identification state
        """
        pass
    
    @abstractmethod
    def apply_item_bonuses(self, item_name: str) -> Dict[str, Any]:
        """
        Apply bonuses and effects from a magic item.
        
        Per D&D 2024 rules:
        - Items can grant bonuses to:
            - AC
            - Attack and damage rolls
            - Saving throws
            - Ability checks
            - Spell save DC and attack rolls
            - And many more specific effects
        
        Args:
            item_name: Name of the item
            
        Returns:
            Dict[str, Any]: Applied bonuses and effects
        """
        pass
    
    @abstractmethod
    def get_all_item_bonuses(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all bonuses from all magic items.
        
        Returns:
            Dict[str, Dict[str, Any]]: All bonuses by source
        """
        pass
    
    @abstractmethod
    def activate_item(self, item_name: str, 
                   activation_type: str = "command") -> Tuple[bool, Dict[str, Any]]:
        """
        Activate a magic item's power.
        
        Per D&D 2024 rules, activation types include:
        - Command word
        - Consumed (potions, scrolls)
        - Worn (constant effect while worn)
        - Action
        - Special
        
        Args:
            item_name: Name of the item
            activation_type: How the item is activated
            
        Returns:
            Tuple[bool, Dict[str, Any]]: (Success, effect details)
        """
        pass
    
    @abstractmethod
    def check_item_requirements(self, item_name: str) -> Tuple[bool, str]:
        """
        Check if character meets requirements to use an item.
        
        Per D&D 2024 rules:
        - Some items require:
            - Specific class
            - Spellcasting ability
            - Alignment
            - Species
            - Other special requirements
        
        Args:
            item_name: Name of the item
            
        Returns:
            Tuple[bool, str]: (Meets requirements, explanation)
        """
        pass
    
    @abstractmethod
    def equip_item(self, item_name: str, slot: Optional[ItemSlot] = None) -> Tuple[bool, str]:
        """
        Equip a magic item to a body slot.
        
        Per D&D 2024 rules:
        - Most wearable magic items occupy a specific body slot
        - Can't wear two items in the same slot (except rings)
        - Some slots have special rules (e.g., ring fingers limited to 2)
        
        Args:
            item_name: Name of the item
            slot: Body slot to equip to (None for automatic)
            
        Returns:
            Tuple[bool, str]: (Success, message)
        """
        pass
    
    @abstractmethod
    def unequip_item(self, item_name: str) -> bool:
        """
        Unequip a magic item.
        
        Args:
            item_name: Name of the item
            
        Returns:
            bool: True if successfully unequipped
        """
        pass
    
    @abstractmethod
    def check_for_cursed_items(self) -> Dict[str, Dict[str, Any]]:
        """
        Check for cursed items and their effects.
        
        Per D&D 2024 rules:
        - Cursed items may:
            - Prevent removal (attunement)
            - Apply negative effects
            - Have special removal conditions
        
        Returns:
            Dict[str, Dict[str, Any]]: Cursed items and their effects
        """
        pass
    
    @abstractmethod
    def get_item_value(self, item_name: str) -> Optional[int]:
        """
        Get the estimated gold piece value of a magic item.
        
        Per D&D 2024 rules:
        - Value depends primarily on rarity
        - Some items have specific values
        
        Args:
            item_name: Name of the item
            
        Returns:
            Optional[int]: Value in gold pieces (None if priceless)
        """
        pass
    
    @abstractmethod
    def get_items_by_rarity(self, rarity: MagicItemRarity) -> List[str]:
        """
        Get all items of a specific rarity.
        
        Args:
            rarity: Item rarity
            
        Returns:
            List[str]: Items of that rarity
        """
        pass
    
    @abstractmethod
    def get_items_by_type(self, item_type: MagicItemType) -> List[str]:
        """
        Get all items of a specific type.
        
        Args:
            item_type: Item type
            
        Returns:
            List[str]: Items of that type
        """
        pass
    
    @abstractmethod
    def get_items_requiring_attunement(self) -> Dict[str, bool]:
        """
        Get all items requiring attunement and their attunement status.
        
        Returns:
            Dict[str, bool]: Dictionary mapping item names to attunement status
        """
        pass
    
    @abstractmethod
    def can_use_item(self, item_name: str) -> Tuple[bool, str]:
        """
        Check if character can use a specific magic item.
        
        Args:
            item_name: Name of the item
            
        Returns:
            Tuple[bool, str]: (Can use, explanation)
        """
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert magic item data to dictionary format.
        
        Returns:
            Dict[str, Any]: Dictionary representation of magic items
        """
        pass