from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Dict, List, Optional, Union, Any, Tuple, Set

class GroupCheckMethod(Enum):
    """Methods for resolving group checks in D&D 5e (2024 Edition)."""
    MAJORITY = auto()        # Succeeds if majority of characters succeed
    AVERAGE = auto()         # Uses the average result of all checks
    BEST = auto()            # Uses the best individual result
    WORST = auto()           # Uses the worst individual result
    ASSISTED = auto()        # One character rolls with advantage from others

class GroupActivity(Enum):
    """Group activities in D&D 5e (2024 Edition)."""
    TRAVEL = auto()          # Overland travel
    EXPLORATION = auto()     # Searching a dungeon/area
    SOCIAL = auto()          # Group social interaction
    COMBAT = auto()          # Group combat tactics
    RESTING = auto()         # Group resting
    DOWNTIME = auto()        # Group downtime activities

class HelpActionType(Enum):
    """Types of help action in D&D 5e (2024 Edition)."""
    ABILITY_CHECK = auto()   # Help with ability checks (gives advantage)
    ATTACK = auto()          # Help with attack rolls (gives advantage)
    OTHER = auto()           # Other uses of the help action

class PartyRole(Enum):
    """Common party roles in D&D 5e (2024 Edition)."""
    TANK = auto()            # Absorbs damage, protects others
    STRIKER = auto()         # Deals high damage
    CONTROLLER = auto()      # Affects battlefield/multiple enemies
    SUPPORT = auto()         # Healing and buffs
    FACE = auto()            # Social interactions
    SCOUT = auto()           # Exploration and reconnaissance
    UTILITY = auto()         # Problem solving and special abilities

class AbstractGroupMechanics(ABC):
    """
    Abstract base class for group mechanics in D&D 5e (2024 Edition).
    
    This class handles all interactions between multiple characters including:
    - Group ability checks
    - Help action
    - Flanking and other tactical positioning
    - Shared resources
    - Party roles and synergies
    - Travel and exploration as a group
    """
    
    # Standard distances for group-related mechanics
    GROUP_VISIBILITY_DISTANCE = 60  # Standard distance in feet for group visibility
    CLOSE_FORMATION_DISTANCE = 10   # Distance in feet for close formation
    FLANKING_DISTANCE = 5           # Distance in feet for flanking
    
    @abstractmethod
    def perform_group_check(self, check_type: str, 
                         character_results: Dict[str, int], 
                         method: GroupCheckMethod = GroupCheckMethod.MAJORITY) -> Tuple[bool, int]:
        """
        Resolve a group ability check.
        
        Per D&D 2024 rules:
        - Group checks are used when multiple characters attempt something together
        - Success is determined by the group as a whole, not individuals
        - Standard method: Success if at least half the group succeeds
        - Used for: Stealth, Perception, Survival during travel, etc.
        
        Args:
            check_type: The type of check being performed
            character_results: Dictionary mapping character names to check results
            method: Method to determine group success
            
        Returns:
            Tuple[bool, int]: (Success, total/average result)
        """
        pass
    
    @abstractmethod
    def provide_help_action(self, helper_name: str, target_name: str, 
                         action_type: HelpActionType, task: str) -> Tuple[bool, str]:
        """
        Provide help action to another character.
        
        Per D&D 2024 rules:
        - Helper must be able to attempt the task alone
        - Must be within 5 feet for helping with attacks
        - Gives advantage on the ability check/attack roll
        - Uses the helper's action
        
        Args:
            helper_name: Character providing help
            target_name: Character receiving help
            action_type: Type of help being provided
            task: Specific task/check being helped with
            
        Returns:
            Tuple[bool, str]: (Success, description)
        """
        pass
    
    @abstractmethod
    def check_flanking(self, attacker1_name: str, attacker2_name: str, 
                     target_name: str, positions: Dict[str, Tuple[int, int]]) -> bool:
        """
        Check if creatures are flanking a target (optional rule).
        
        Per D&D 2024 rules (optional):
        - Attackers must be on opposite sides of the target
        - Both must be within 5 feet of the target
        - Neither can be incapacitated
        - Grants advantage on melee attack rolls
        
        Args:
            attacker1_name: First attacker
            attacker2_name: Second attacker
            target_name: Target being flanked
            positions: Dictionary mapping character names to (x,y) coordinates
            
        Returns:
            bool: True if flanking is achieved
        """
        pass
    
    @abstractmethod
    def share_resource(self, source_name: str, target_name: str, 
                     resource_type: str, amount: int) -> Tuple[bool, Dict[str, Any]]:
        """
        Share a resource between characters.
        
        Per D&D 2024 guidelines:
        - Some items can be shared during play (healing potions, etc.)
        - Typically requires an action or interaction
        - Must be within reach of each other
        
        Args:
            source_name: Character sharing the resource
            target_name: Character receiving the resource
            resource_type: Type of resource being shared
            amount: Amount of resource to share
            
        Returns:
            Tuple[bool, Dict[str, Any]]: (Success, details of shared resource)
        """
        pass
    
    @abstractmethod
    def coordinate_group_travel(self, characters: List[str], 
                             travel_pace: str, 
                             roles: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        Coordinate group travel.
        
        Per D&D 2024 rules:
        - Group travel pace (slow, normal, fast) affects stealth, perception
        - Characters can take specific roles during travel
        - Travel pace determines distance covered per day
        
        Args:
            characters: List of character names
            travel_pace: Pace of travel (slow, normal, fast)
            roles: Dictionary mapping roles to lists of character names
            
        Returns:
            Dict[str, Any]: Results of travel (distance, encounters, etc.)
        """
        pass
    
    @abstractmethod
    def manage_group_marching_order(self, characters: List[str], 
                                 formation: str) -> Dict[str, Tuple[int, int]]:
        """
        Manage the group's marching order.
        
        Per D&D 2024 guidelines:
        - Typical formations: Single file, two abreast, defensive, etc.
        - Affects surprise, opportunity for detection, etc.
        - Important for dungeon corridors and similar confined spaces
        
        Args:
            characters: List of character names
            formation: Type of formation
            
        Returns:
            Dict[str, Tuple[int, int]]: Positions of each character
        """
        pass
    
    @abstractmethod
    def distribute_loot(self, items: Dict[str, Any], 
                      characters: List[str]) -> Dict[str, List[str]]:
        """
        Assist with distributing loot among characters.
        
        Per D&D 2024 guidelines:
        - Track what items go to which characters
        - Optional methods: Even split, role-based, need-based
        - Includes gold, items, and other valuables
        
        Args:
            items: Dictionary of items to distribute
            characters: List of character names
            
        Returns:
            Dict[str, List[str]]: Distribution of items to characters
        """
        pass
    
    @abstractmethod
    def calculate_party_carrying_capacity(self, characters: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate the party's total carrying capacity.
        
        Per D&D 2024 rules:
        - Based on Strength scores of all characters
        - Affected by magic items (Bags of Holding, etc.)
        - Different movement penalties at different thresholds
        
        Args:
            characters: Dictionary mapping character names to their details
            
        Returns:
            Dict[str, Any]: Carrying capacity details
        """
        pass
    
    @abstractmethod
    def set_watch_rotation(self, characters: List[str], 
                        rest_duration: int, 
                        watches: int) -> Dict[int, List[str]]:
        """
        Set up a watch rotation for long rests.
        
        Per D&D 2024 guidelines:
        - Typically 8-hour rest with 2-hour watches
        - Characters on watch can't benefit from rest during their watch
        - Watches allow perception checks against threats
        
        Args:
            characters: List of character names
            rest_duration: Duration of rest in hours
            watches: Number of watch shifts
            
        Returns:
            Dict[int, List[str]]: Characters assigned to each watch
        """
        pass
    
    @abstractmethod
    def coordinate_group_stealth(self, character_checks: Dict[str, int]) -> Tuple[bool, int]:
        """
        Coordinate group stealth.
        
        Per D&D 2024 rules:
        - Group stealth check: Everyone rolls Dexterity (Stealth)
        - Success if at least half the group succeeds
        - Failure may result in detection
        
        Args:
            character_checks: Dictionary mapping character names to stealth check results
            
        Returns:
            Tuple[bool, int]: (Success, group result)
        """
        pass
    
    @abstractmethod
    def evaluate_party_balance(self, character_classes: Dict[str, str]) -> Dict[str, Any]:
        """
        Evaluate party balance across different roles.
        
        Per D&D 2024 guidelines:
        - Check coverage of key roles (tank, healer, damage, etc.)
        - Identify potential weaknesses
        - Not an official rule, but useful for party composition
        
        Args:
            character_classes: Dictionary mapping character names to their classes
            
        Returns:
            Dict[str, Any]: Analysis of party balance
        """
        pass
    
    @abstractmethod
    def calculate_party_xp_thresholds(self, character_levels: Dict[str, int]) -> Dict[str, int]:
        """
        Calculate party-wide XP thresholds for encounters.
        
        Per D&D 2024 rules:
        - Based on individual character levels
        - Used to balance encounters (easy, medium, hard, deadly)
        - Accounts for party size adjustments
        
        Args:
            character_levels: Dictionary mapping character names to levels
            
        Returns:
            Dict[str, int]: XP thresholds for different difficulties
        """
        pass
    
    @abstractmethod
    def perform_group_ability_contest(self, party_checks: Dict[str, int], 
                                   opposing_checks: Dict[str, int],
                                   method: GroupCheckMethod) -> Tuple[bool, str]:
        """
        Resolve a group ability contest against opponents.
        
        Per D&D 2024 guidelines:
        - Used when party contests against a group of NPCs
        - Examples: Tug-of-war, group intimidation, etc.
        
        Args:
            party_checks: Dictionary mapping party character names to check results
            opposing_checks: Dictionary mapping opponent names to check results
            method: Method to determine group success
            
        Returns:
            Tuple[bool, str]: (Party won, description)
        """
        pass
    
    @abstractmethod
    def apply_inspiration_sharing(self, source_name: str, 
                               target_name: str) -> Tuple[bool, str]:
        """
        Share inspiration between party members.
        
        Per D&D 2024 rules:
        - A character with inspiration can give it to another character
        - This is a way to reward good roleplaying between characters
        - Can only have one inspiration at a time
        
        Args:
            source_name: Character giving inspiration
            target_name: Character receiving inspiration
            
        Returns:
            Tuple[bool, str]: (Success, message)
        """
        pass
    
    @abstractmethod
    def coordinate_group_surprise(self, party_stealth: Dict[str, int],
                               enemy_perception: Dict[str, int]) -> Dict[str, bool]:
        """
        Determine surprise in group combat.
        
        Per D&D 2024 rules:
        - Compare Dexterity (Stealth) checks against passive Perception
        - Any creature that notices a threat is not surprised
        - Surprised creatures can't move or take actions on first turn
        
        Args:
            party_stealth: Dictionary mapping party names to stealth results
            enemy_perception: Dictionary mapping enemy names to perception results
            
        Returns:
            Dict[str, bool]: Which creatures are surprised
        """
        pass
    
    @abstractmethod
    def determine_group_initiative(self, character_initiatives: Dict[str, int]) -> Dict[int, List[str]]:
        """
        Determine initiative order for a group.
        
        Per D&D 2024 rules:
        - Each character rolls initiative (d20 + DEX modifier)
        - Optional rule: Group initiative (one roll for entire party)
        
        Args:
            character_initiatives: Dictionary mapping character names to initiative rolls
            
        Returns:
            Dict[int, List[str]]: Initiative order with characters at each count
        """
        pass
    
    @abstractmethod
    def assist_group_perception(self, character_checks: Dict[str, int]) -> Dict[str, Any]:
        """
        Manage group perception and investigation.
        
        Per D&D 2024 guidelines:
        - When multiple characters search an area
        - Can use best check or group check depending on circumstances
        - Different characters can focus on different aspects
        
        Args:
            character_checks: Dictionary mapping character names to perception/investigation results
            
        Returns:
            Dict[str, Any]: What the group discovers
        """
        pass
    
    @abstractmethod
    def coordinate_group_rest(self, characters: List[str], 
                           rest_type: str) -> Dict[str, Dict[str, Any]]:
        """
        Coordinate a group rest.
        
        Per D&D 2024 rules:
        - Short rest (1 hour) or long rest (8 hours)
        - Interruptions affect the whole group
        - Resources recovered for each character
        - Watch shifts during long rests
        
        Args:
            characters: List of character names
            rest_type: Type of rest ("short" or "long")
            
        Returns:
            Dict[str, Dict[str, Any]]: Results of rest for each character
        """
        pass
    
    @abstractmethod
    def calculate_group_downtime(self, character_activities: Dict[str, str],
                              duration: int) -> Dict[str, Dict[str, Any]]:
        """
        Calculate results of group downtime activities.
        
        Per D&D 2024 guidelines:
        - Characters can engage in different or collaborative activities
        - Some activities benefit from multiple participants
        - Duration in days determines progress
        
        Args:
            character_activities: Dictionary mapping character names to chosen activities
            duration: Duration in days
            
        Returns:
            Dict[str, Dict[str, Any]]: Results for each character
        """
        pass
    
    @abstractmethod
    def coordinate_group_overland_travel(self, characters: Dict[str, Dict[str, Any]],
                                      distance: int,
                                      terrain: str) -> Dict[str, Any]:
        """
        Coordinate group overland travel.
        
        Per D&D 2024 rules:
        - Travel pace affects distance covered and perception
        - Different terrain affects travel speed
        - Group uses slowest member's speed
        - Mounts and vehicles can affect travel speed
        
        Args:
            characters: Dictionary mapping character names to their details
            distance: Distance to travel in miles
            terrain: Type of terrain
            
        Returns:
            Dict[str, Any]: Results of travel
        """
        pass
    
    @abstractmethod
    def manage_party_spell_combinations(self, spells_cast: Dict[str, str]) -> Dict[str, Any]:
        """
        Manage interactions between multiple spells cast by the party.
        
        Per D&D 2024 guidelines:
        - Some spell combinations have special interactions
        - Multiple concentration spells from different casters
        - Area effect overlaps
        
        Args:
            spells_cast: Dictionary mapping character names to spells they're casting
            
        Returns:
            Dict[str, Any]: Results of spell interactions
        """
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert group mechanics data to dictionary format.
        
        Returns:
            Dict[str, Any]: Dictionary representation of group mechanics
        """
        pass