from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Dict, List, Optional, Union, Any, Tuple, Set

class RestType(Enum):
    """Types of rest in D&D 5e (2024 Edition)."""
    SHORT_REST = auto()  # 1 hour of light activity
    LONG_REST = auto()   # 8 hours (6 hours sleep + 2 hours light activity)
    CATNAP = auto()      # 10-minute magical short rest (from spell)
    MEDITATION = auto()  # Special rest for certain species/classes (like Elves)

class ResourceRecoveryType(Enum):
    """When character resources recover in D&D 5e (2024 Edition)."""
    SHORT_REST = auto()  # Resources that recover after a short or long rest
    LONG_REST = auto()   # Resources that recover only after a long rest
    DAILY = auto()       # Resources that recover at a specific time of day
    DAWN = auto()        # Resources that recover at dawn
    DUSK = auto()        # Resources that recover at dusk
    SPECIAL = auto()     # Custom recovery conditions

class AbstractResting(ABC):
    """
    Abstract base class for handling character resting in D&D 5e (2024 Edition).
    
    Resting is a critical mechanic in D&D that allows characters to recover:
    - Hit points
    - Hit dice
    - Spell slots
    - Class features
    - Magic item charges
    
    D&D 2024 defines two main types of rest:
    1. Short Rest (1 hour)
    2. Long Rest (8 hours, with at least 6 hours of sleep)
    """
    
    @abstractmethod
    def take_short_rest(self, duration_minutes: int = 60) -> Dict[str, Any]:
        """
        Perform a short rest.
        
        Per D&D 2024 rules:
        - Short rest requires 1 hour of light activity
        - Characters can spend one or more Hit Dice to recover HP
        - Each Hit Die spent recovers HP equal to die roll + CON modifier
        - Some class features recover after a short rest
        
        Args:
            duration_minutes: Time spent resting in minutes (normally 60)
            
        Returns:
            Dict[str, Any]: Results of the short rest including:
                - hit_dice_spent: Number of hit dice spent
                - hp_recovered: HP recovered from hit dice
                - features_recovered: List of features that recovered
                - complete: Whether the rest was completed successfully
        """
        pass
    
    @abstractmethod
    def take_long_rest(self, duration_hours: int = 8, sleep_hours: int = 6) -> Dict[str, Any]:
        """
        Perform a long rest.
        
        Per D&D 2024 rules:
        - Long rest requires 8 hours (at least 6 hours of sleep, 2 hours of light activity)
        - Recovers all HP
        - Recovers up to half of max Hit Dice (minimum 1)
        - Resets most class features with "long rest" recovery
        - Some features recharge "daily" or "at dawn/dusk" instead
        - Can only benefit from one long rest per 24-hour period
        - Must have at least 1 HP to benefit from a rest
        - Long rest can be interrupted by 1+ hour of strenuous activity
        
        Args:
            duration_hours: Total time spent resting in hours (normally 8)
            sleep_hours: Time spent sleeping in hours (normally 6+)
            
        Returns:
            Dict[str, Any]: Results of the long rest including:
                - hp_recovered: HP recovered
                - hit_dice_recovered: Hit dice recovered
                - features_recovered: List of features that recovered
                - spell_slots_recovered: Spell slots recovered
                - complete: Whether the rest was completed successfully
        """
        pass
    
    @abstractmethod
    def spend_hit_die(self, num_dice: int = 1) -> Dict[str, int]:
        """
        Spend hit dice to recover hit points during a short rest.
        
        Per D&D 2024 rules:
        - Each hit die recovers HP equal to the die roll + CON modifier
        - Character must have available hit dice to spend
        - Hit die type is based on character class
        
        Args:
            num_dice: Number of hit dice to spend
            
        Returns:
            Dict[str, int]: Dictionary with:
                - dice_spent: Number of dice actually spent
                - hp_recovered: HP recovered
        """
        pass
    
    @abstractmethod
    def get_available_hit_dice(self) -> Dict[str, int]:
        """
        Get available hit dice by type.
        
        Returns:
            Dict[str, int]: Dictionary mapping hit die types to count
        """
        pass
    
    @abstractmethod
    def recover_hit_points(self, amount: int) -> int:
        """
        Recover hit points.
        
        Per D&D 2024 rules:
        - Characters cannot exceed their maximum HP
        - Some special abilities modify HP recovery
        
        Args:
            amount: Amount of HP to recover
            
        Returns:
            int: Actual HP recovered
        """
        pass
    
    @abstractmethod
    def recover_hit_dice(self, amount: int) -> int:
        """
        Recover spent hit dice.
        
        Per D&D 2024 rules:
        - Long rest recovers up to half total hit dice (minimum 1)
        - Cannot exceed maximum hit dice
        
        Args:
            amount: Number of hit dice to recover
            
        Returns:
            int: Actual number of hit dice recovered
        """
        pass
    
    @abstractmethod
    def get_recoverable_resources(self, rest_type: RestType) -> Dict[str, Any]:
        """
        Get all resources that can be recovered by a specific rest type.
        
        Args:
            rest_type: Type of rest
            
        Returns:
            Dict[str, Any]: Dictionary of recoverable resources
        """
        pass
    
    @abstractmethod
    def recover_class_resources(self, rest_type: RestType) -> Dict[str, Any]:
        """
        Recover class resources based on rest type.
        
        Per D&D 2024 rules:
        - Different class features recover based on rest type
        - Examples: Channel Divinity (short), Rage uses (long), etc.
        
        Args:
            rest_type: Type of rest
            
        Returns:
            Dict[str, Any]: Dictionary mapping resource names to recovery amounts
        """
        pass
    
    @abstractmethod
    def recover_spell_slots(self) -> Dict[int, int]:
        """
        Recover spell slots after a long rest.
        
        Per D&D 2024 rules:
        - Long rest restores all expended spell slots
        - Warlocks have special rules (recover on short rest)
        
        Returns:
            Dict[int, int]: Dictionary mapping spell levels to slots recovered
        """
        pass
    
    @abstractmethod
    def can_benefit_from_long_rest(self) -> Tuple[bool, str]:
        """
        Check if character can benefit from a long rest.
        
        Per D&D 2024 rules:
        - Character can only benefit from one long rest per 24 hours
        - Character must have at least 1 HP to benefit from a rest
        
        Returns:
            Tuple[bool, str]: (Can benefit, explanation)
        """
        pass
    
    @abstractmethod
    def is_resting_interrupted(self, activity_time_minutes: int, is_strenuous: bool) -> bool:
        """
        Check if a rest is interrupted.
        
        Per D&D 2024 rules:
        - Short rest: Interrupted by any combat or strenuous activity
        - Long rest: Can include up to 2 hours of light activity
        - Long rest: Interrupted by 1+ hour of strenuous activity
        
        Args:
            activity_time_minutes: Duration of the activity in minutes
            is_strenuous: Whether the activity is strenuous
            
        Returns:
            bool: True if rest is interrupted
        """
        pass
    
    @abstractmethod
    def get_time_since_last_long_rest(self) -> float:
        """
        Get time elapsed since the last long rest.
        
        Returns:
            float: Hours since last long rest
        """
        pass
    
    @abstractmethod
    def handle_special_rest_traits(self, rest_type: RestType) -> Dict[str, Any]:
        """
        Apply special traits that modify resting.
        
        Per D&D 2024 rules, some species/classes have special rest traits:
        - Elves (Trance): Can get the benefits of a long rest in 4 hours
        - Warforged: Don't sleep but must still rest to benefit
        - Some feats/items may modify rest benefits
        
        Args:
            rest_type: Type of rest
            
        Returns:
            Dict[str, Any]: Effects of special traits
        """
        pass
    
    @abstractmethod
    def recover_magic_item_charges(self) -> Dict[str, int]:
        """
        Recover magic item charges.
        
        Per D&D 2024 rules:
        - Many magic items recover charges at dawn
        - Some have different recovery schedules
        
        Returns:
            Dict[str, int]: Dictionary mapping item names to charges recovered
        """
        pass
    
    @abstractmethod
    def roll_for_exhaustion(self, sleep_hours: int) -> Tuple[bool, int]:
        """
        Roll for exhaustion after insufficient rest.
        
        Per D&D 2024 rules:
        - Characters who don't get a full long rest might gain exhaustion
        - DC 10 Constitution saving throw to avoid gaining a level of exhaustion
        
        Args:
            sleep_hours: Hours of sleep obtained
            
        Returns:
            Tuple[bool, int]: (Gained exhaustion, new exhaustion level)
        """
        pass
    
    @abstractmethod
    def restore_expended_features(self, feature_name: str) -> bool:
        """
        Restore a specific expended feature.
        
        Args:
            feature_name: Name of the feature to restore
            
        Returns:
            bool: True if successfully restored
        """
        pass
    
    @abstractmethod
    def get_current_state(self) -> Dict[str, Any]:
        """
        Get the current resting state of the character.
        
        Returns:
            Dict[str, Any]: Dictionary with:
                - current_hp: Current hit points
                - max_hp: Maximum hit points
                - hit_dice: Available hit dice
                - exhaustion: Current exhaustion level
                - resources: Available class resources
                - spell_slots: Available spell slots
        """
        pass
    
    @abstractmethod
    def simulate_rest_benefits(self, rest_type: RestType) -> Dict[str, Any]:
        """
        Simulate the benefits of a rest without applying them.
        
        A useful preview function for players.
        
        Args:
            rest_type: Type of rest to simulate
            
        Returns:
            Dict[str, Any]: Potential benefits
        """
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert resting data to dictionary format.
        
        Returns:
            Dict[str, Any]: Dictionary representation of resting state
        """
        pass