from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Dict, List, Optional, Union, Any, Tuple

class ExperienceSource(Enum):
    """Enumeration of experience point sources in D&D 5e (2024 Edition)."""
    COMBAT = auto()           # Combat encounters
    QUEST = auto()            # Completing quests/objectives
    ROLEPLAY = auto()         # Good roleplaying
    MILESTONE = auto()        # Story milestone achievements
    PUZZLE = auto()           # Solving puzzles
    EXPLORATION = auto()      # Discovering new areas or lore
    TRAINING = auto()         # Dedicated training during downtime
    CRAFTING = auto()         # Creating items
    RESEARCH = auto()         # Discovering knowledge
    OTHER = auto()            # Miscellaneous sources

class AdvancementMethod(Enum):
    """Enumeration of character advancement methods in D&D 5e (2024 Edition)."""
    EXPERIENCE_POINTS = auto()  # Traditional XP tracking
    MILESTONE = auto()          # Level up at story milestones
    TRAINING = auto()           # Combined XP and downtime training
    MIXED = auto()              # Combination of methods

class DowntimeActivity(Enum):
    """Enumeration of downtime activities in D&D 5e (2024 Edition)."""
    CRAFTING = auto()           # Creating items
    TRAINING = auto()           # Learning new skills or abilities
    CAROUSING = auto()          # Making social contacts
    RESEARCH = auto()           # Acquiring knowledge
    WORK = auto()               # Earning money
    CRIME = auto()              # Illegal activities
    RELIGIOUS_SERVICE = auto()  # Serving a deity or organization
    PIT_FIGHTING = auto()       # Participating in combat sports
    RECUPERATING = auto()       # Recovering from injuries or conditions
    SELLING_MAGIC_ITEMS = auto()  # Finding buyers for magic items
    BUYING_MAGIC_ITEMS = auto()   # Finding sellers of magic items
    SCRIBING_SPELLS = auto()      # Copying spells into a spellbook
    CUSTOM = auto()              # Custom activities

class AbstractExperience(ABC):
    """
    Abstract base class defining the contract for character experience and advancement
    in D&D 5e (2024 Edition).
    
    This class handles all aspects of character advancement including:
    - Experience point tracking and calculation
    - Level determination based on XP thresholds
    - Milestone-based advancement
    - Downtime activities and their benefits
    """
    
    # Official XP thresholds for each level as per D&D 2024 rules
    XP_THRESHOLDS = {
        1: 0,
        2: 300,
        3: 900,
        4: 2700,
        5: 6500,
        6: 14000,
        7: 23000,
        8: 34000,
        9: 48000,
        10: 64000,
        11: 85000,
        12: 100000,
        13: 120000,
        14: 140000,
        15: 165000,
        16: 195000,
        17: 225000,
        18: 265000,
        19: 305000,
        20: 355000
    }
    
    # Challenge Rating to XP conversion table
    CR_TO_XP = {
        0: 10,
        1/8: 25,
        1/4: 50,
        1/2: 100,
        1: 200,
        2: 450,
        3: 700,
        4: 1100,
        5: 1800,
        6: 2300,
        7: 2900,
        8: 3900,
        9: 5000,
        10: 5900,
        11: 7200,
        12: 8400,
        13: 10000,
        14: 11500,
        15: 13000,
        16: 15000,
        17: 18000,
        18: 20000,
        19: 22000,
        20: 25000,
        21: 33000,
        22: 41000,
        23: 50000,
        24: 62000,
        25: 75000,
        26: 90000,
        27: 105000,
        28: 120000,
        29: 135000,
        30: 155000
    }
    
    # XP multipliers based on number of monsters (2024 rules)
    ENCOUNTER_XP_MULTIPLIERS = {
        1: 1.0,
        2: 1.5,
        3: 2.0,
        4: 2.0,
        5: 2.0,
        6: 2.0,
        7: 2.5,
        8: 2.5,
        9: 2.5,
        10: 2.5,
        11: 3.0,
        12: 3.0,
        13: 3.0,
        14: 3.0,
        15: 4.0
    }
    
    @abstractmethod
    def get_current_xp(self) -> int:
        """
        Get the character's current XP total.
        
        Returns:
            int: Current XP
        """
        pass
    
    @abstractmethod
    def get_current_level(self) -> int:
        """
        Get the character's current level based on XP or milestones.
        
        Per D&D 2024 rules, this is determined by:
        - For XP-based: Comparing current XP to the XP_THRESHOLDS
        - For milestone-based: The level granted by story progress
        
        Returns:
            int: Current character level (1-20)
        """
        pass
    
    @abstractmethod
    def get_advancement_method(self) -> AdvancementMethod:
        """
        Get the character's current advancement method.
        
        Returns:
            AdvancementMethod: Current advancement method
        """
        pass
    
    @abstractmethod
    def set_advancement_method(self, method: AdvancementMethod) -> bool:
        """
        Set the character's advancement method.
        
        Per D&D 2024 rules, DMs may choose between XP-based or milestone-based advancement.
        
        Args:
            method: The advancement method to use
            
        Returns:
            bool: True if successfully set
        """
        pass
    
    @abstractmethod
    def add_xp(self, amount: int, source: ExperienceSource = ExperienceSource.OTHER) -> int:
        """
        Add XP to the character from a specified source.
        
        Args:
            amount: Amount of XP to add
            source: Source of the XP
            
        Returns:
            int: New XP total
        """
        pass
    
    @abstractmethod
    def check_level_up(self) -> Tuple[bool, Optional[int]]:
        """
        Check if the character has enough XP to level up.
        
        Returns:
            Tuple[bool, Optional[int]]: (Can level up, New level if applicable)
        """
        pass
    
    @abstractmethod
    def apply_milestone(self) -> Tuple[bool, int]:
        """
        Apply a milestone advancement to the character.
        
        Per D&D 2024 rules, milestone advancement grants a level when significant
        story goals are achieved, regardless of XP accumulated.
        
        Returns:
            Tuple[bool, int]: (Success, New level)
        """
        pass
    
    @abstractmethod
    def get_xp_to_next_level(self) -> int:
        """
        Get XP needed to reach the next level.
        
        Returns:
            int: XP needed
        """
        pass
    
    @abstractmethod
    def get_xp_for_encounter(self, monster_crs: List[float], party_size: int) -> int:
        """
        Calculate total XP award for an encounter.
        
        Per D&D 2024 rules:
        1. Sum base XP values for all monsters
        2. Apply multiplier based on number of monsters
        3. Divide by number of party members
        
        Args:
            monster_crs: List of monster Challenge Ratings
            party_size: Number of characters in the party
            
        Returns:
            int: XP to award to each character
        """
        pass
    
    @abstractmethod
    def get_encounter_difficulty(self, monster_crs: List[float], party_levels: List[int]) -> str:
        """
        Calculate the difficulty of an encounter.
        
        Per D&D 2024 rules, encounters are categorized as:
        - Easy
        - Medium
        - Hard
        - Deadly
        
        Args:
            monster_crs: List of monster Challenge Ratings
            party_levels: List of party member levels
            
        Returns:
            str: Difficulty rating
        """
        pass
    
    @abstractmethod
    def get_xp_history(self) -> Dict[str, Any]:
        """
        Get the character's XP history.
        
        Returns:
            Dict[str, Any]: XP by source and session
        """
        pass
    
    @abstractmethod
    def reset_xp(self) -> bool:
        """
        Reset the character's XP to 0 (level 1).
        
        Returns:
            bool: True if successfully reset
        """
        pass
    
    @abstractmethod
    def get_available_downtime_activities(self) -> Dict[DowntimeActivity, Dict[str, Any]]:
        """
        Get all downtime activities available to the character.
        
        Per D&D 2024 rules, available downtime activities may depend on:
        - Character level
        - Location
        - Character proficiencies and abilities
        - Faction memberships
        
        Returns:
            Dict[DowntimeActivity, Dict[str, Any]]: Available activities with details
        """
        pass
    
    @abstractmethod
    def perform_downtime_activity(self, activity: DowntimeActivity, days: int, **kwargs) -> Dict[str, Any]:
        """
        Perform a downtime activity.
        
        Per D&D 2024 rules, downtime activities:
        - Take a specific number of days
        - May require ability checks
        - Can provide various benefits (money, items, contacts, etc.)
        - May involve complications
        
        Args:
            activity: The downtime activity to perform
            days: Number of days spent
            **kwargs: Additional parameters for the activity
            
        Returns:
            Dict[str, Any]: Results of the activity
        """
        pass
    
    @abstractmethod
    def get_downtime_training_options(self) -> Dict[str, Any]:
        """
        Get training options available during downtime.
        
        Per D&D 2024 rules, characters can train to gain:
        - Tool proficiencies
        - Language proficiencies
        - Skill proficiencies (with DM approval)
        
        Training typically requires:
        - Time (at least 10 workweeks)
        - Money (at least 250 gp)
        - A suitable teacher
        
        Returns:
            Dict[str, Any]: Available training options
        """
        pass
    
    @abstractmethod
    def train_proficiency(self, proficiency_type: str, specific_proficiency: str, 
                       weeks: int, cost: int) -> bool:
        """
        Train to gain a new proficiency during downtime.
        
        Args:
            proficiency_type: Type of proficiency (skill, tool, language)
            specific_proficiency: The specific proficiency to learn
            weeks: Workweeks spent training
            cost: Gold cost of training
            
        Returns:
            bool: True if training was successful
        """
        pass
    
    @abstractmethod
    def get_crafting_options(self) -> Dict[str, Any]:
        """
        Get available crafting options.
        
        Per D&D 2024 rules:
        - Crafting requires appropriate tool proficiency
        - Item cost and rarity determine time required
        - Special materials may be needed for certain items
        
        Returns:
            Dict[str, Any]: Available crafting options
        """
        pass
    
    @abstractmethod
    def craft_item(self, item_name: str, days: int, cost: int, **kwargs) -> Dict[str, Any]:
        """
        Craft an item during downtime.
        
        Per D&D 2024 rules:
        - Character must be proficient with appropriate tools
        - Basic crafting: 5 gp of progress per day
        - Magic items have special requirements
        
        Args:
            item_name: Name of the item to craft
            days: Days spent crafting
            cost: Material cost
            **kwargs: Additional crafting parameters
            
        Returns:
            Dict[str, Any]: Result of crafting
        """
        pass
    
    @abstractmethod
    def get_research_topics(self) -> List[str]:
        """
        Get available research topics.
        
        Per D&D 2024 rules, research might:
        - Uncover lore about magical items
        - Reveal monster weaknesses
        - Provide historical information
        - Discover spell scrolls
        
        Returns:
            List[str]: Available research topics
        """
        pass
    
    @abstractmethod
    def research_topic(self, topic: str, days: int, cost: int) -> Dict[str, Any]:
        """
        Research a topic during downtime.
        
        Args:
            topic: Topic to research
            days: Days spent researching
            cost: Cost of research (library access, materials, etc.)
            
        Returns:
            Dict[str, Any]: Research results
        """
        pass
    
    @abstractmethod
    def get_xp_for_downtime(self, activity: DowntimeActivity, days: int, success: bool) -> int:
        """
        Calculate XP gained from downtime activities (if applicable).
        
        Some DMs award XP for significant downtime accomplishments.
        
        Args:
            activity: The activity performed
            days: Days spent
            success: Whether the activity was successful
            
        Returns:
            int: XP awarded (0 if none)
        """
        pass
    
    @abstractmethod
    def milestone_progress(self) -> Dict[str, Any]:
        """
        Get information about milestone progression.
        
        For milestone-based advancement, this tracks:
        - Completed story milestones
        - Current objectives
        - Progress toward next level
        
        Returns:
            Dict[str, Any]: Milestone progress information
        """
        pass
    
    @abstractmethod
    def predict_levels_by_sessions(self, avg_xp_per_session: int, sessions: int) -> Dict[int, int]:
        """
        Predict future levels based on average XP per session.
        
        A planning tool for DMs and players.
        
        Args:
            avg_xp_per_session: Average XP earned per session
            sessions: Number of future sessions
            
        Returns:
            Dict[int, int]: Mapping of session numbers to predicted levels
        """
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert experience data to dictionary format.
        
        Returns:
            Dict[str, Any]: Dictionary representation of experience data
        """
        pass