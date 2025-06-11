from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Dict, List, Optional, Union, Any, Tuple, Set

class ProficiencyLevel(Enum):
    """Enumeration of proficiency levels for skills in D&D 5e (2024 Edition)."""
    NONE = 0        # No proficiency (0x proficiency bonus)
    PROFICIENT = 1  # Proficient (1x proficiency bonus)
    EXPERT = 2      # Expertise (2x proficiency bonus)

class SkillCategory(Enum):
    """Categorization of skills by common usage in D&D 5e."""
    SOCIAL = auto()      # Social interaction skills
    EXPLORATION = auto()  # Exploration and environment skills
    KNOWLEDGE = auto()    # Knowledge and information skills
    PHYSICAL = auto()     # Physical activity skills
    PERCEPTION = auto()   # Awareness and detection skills

class AbstractSkills(ABC):
    """
    Abstract base class for handling character skills in D&D 5e (2024 Edition).
    
    Skills in D&D represent specific areas of training and expertise that characters
    can use to overcome challenges. Each skill is tied to one of the six ability scores
    and can have different levels of proficiency.
    """
    
    # Standard skills in D&D 5e (2024 Edition)
    STANDARD_SKILLS = [
        "Acrobatics", "Animal Handling", "Arcana", "Athletics", "Deception",
        "History", "Insight", "Intimidation", "Investigation", "Medicine",
        "Nature", "Perception", "Performance", "Persuasion", "Religion",
        "Sleight of Hand", "Stealth", "Survival"
    ]
    
    # Map skills to their primary abilities
    SKILL_TO_ABILITY = {
        "Acrobatics": "dexterity",
        "Animal Handling": "wisdom",
        "Arcana": "intelligence",
        "Athletics": "strength",
        "Deception": "charisma",
        "History": "intelligence",
        "Insight": "wisdom",
        "Intimidation": "charisma",
        "Investigation": "intelligence",
        "Medicine": "wisdom",
        "Nature": "intelligence",
        "Perception": "wisdom",
        "Performance": "charisma",
        "Persuasion": "charisma",
        "Religion": "intelligence",
        "Sleight of Hand": "dexterity",
        "Stealth": "dexterity",
        "Survival": "wisdom"
    }
    
    # Map skills to categories
    SKILL_TO_CATEGORY = {
        "Acrobatics": SkillCategory.PHYSICAL,
        "Animal Handling": SkillCategory.SOCIAL,
        "Arcana": SkillCategory.KNOWLEDGE,
        "Athletics": SkillCategory.PHYSICAL,
        "Deception": SkillCategory.SOCIAL,
        "History": SkillCategory.KNOWLEDGE,
        "Insight": SkillCategory.SOCIAL,
        "Intimidation": SkillCategory.SOCIAL,
        "Investigation": SkillCategory.KNOWLEDGE,
        "Medicine": SkillCategory.KNOWLEDGE,
        "Nature": SkillCategory.KNOWLEDGE,
        "Perception": SkillCategory.PERCEPTION,
        "Performance": SkillCategory.SOCIAL,
        "Persuasion": SkillCategory.SOCIAL,
        "Religion": SkillCategory.KNOWLEDGE,
        "Sleight of Hand": SkillCategory.PHYSICAL,
        "Stealth": SkillCategory.PHYSICAL,
        "Survival": SkillCategory.EXPLORATION
    }
    
    @abstractmethod
    def get_skill_ability(self, skill_name: str) -> str:
        """
        Get the ability associated with a skill.
        
        Per D&D 2024 rules, each skill is associated with a specific ability.
        
        Args:
            skill_name: Name of the skill
            
        Returns:
            str: Associated ability ("strength", "dexterity", etc.)
        """
        pass
    
    @abstractmethod
    def calculate_skill_modifier(self, skill_name: str, ability_scores: Dict[str, int],
                              proficiency_bonus: int) -> int:
        """
        Calculate modifier for a skill check.
        
        Per D&D 2024 rules:
        - Base modifier is the ability score modifier
        - Add proficiency bonus if proficient
        - Add twice proficiency bonus if expert
        
        Args:
            skill_name: Name of the skill
            ability_scores: Character's ability scores
            proficiency_bonus: Character's proficiency bonus
            
        Returns:
            int: Total skill modifier
        """
        pass
    
    @abstractmethod
    def set_skill_proficiency(self, skill_name: str, proficiency_level: ProficiencyLevel) -> bool:
        """
        Set proficiency level for a skill.
        
        Args:
            skill_name: Name of the skill
            proficiency_level: Level of proficiency
            
        Returns:
            bool: True if successful
        """
        pass
    
    @abstractmethod
    def get_proficiency_level(self, skill_name: str) -> ProficiencyLevel:
        """
        Get proficiency level for a skill.
        
        Args:
            skill_name: Name of the skill
            
        Returns:
            ProficiencyLevel: Current proficiency level
        """
        pass
    
    @abstractmethod
    def get_skill_dc_by_difficulty(self, difficulty: str) -> int:
        """
        Get recommended DC for a skill check based on difficulty.
        
        Per D&D 2024 rules:
        - Very Easy: DC 5
        - Easy: DC 10
        - Moderate: DC 15
        - Hard: DC 20
        - Very Hard: DC 25
        - Nearly Impossible: DC 30
        
        Args:
            difficulty: Difficulty level
            
        Returns:
            int: Recommended DC
        """
        pass
    
    @abstractmethod
    def get_skills_by_ability(self, ability: str) -> List[str]:
        """
        Get skills associated with a specific ability.
        
        Args:
            ability: Ability name (e.g., "strength", "dexterity")
            
        Returns:
            List[str]: List of skills for that ability
        """
        pass
    
    @abstractmethod
    def get_skills_by_category(self, category: SkillCategory) -> List[str]:
        """
        Get skills by category.
        
        Args:
            category: Skill category to filter by
            
        Returns:
            List[str]: List of skills in the category
        """
        pass
    
    @abstractmethod
    def get_passive_skill_value(self, skill_name: str, ability_scores: Dict[str, int],
                             proficiency_bonus: int) -> int:
        """
        Calculate passive value for a skill.
        
        Per D&D 2024 rules, passive check = 10 + skill modifier.
        Most commonly used for Perception but applicable to any skill.
        
        Args:
            skill_name: Name of the skill
            ability_scores: Character's ability scores
            proficiency_bonus: Character's proficiency bonus
            
        Returns:
            int: Passive skill value
        """
        pass
    
    @abstractmethod
    def perform_skill_check(self, skill_name: str, ability_scores: Dict[str, int],
                         proficiency_bonus: int, difficulty_class: int,
                         advantage: bool = False, disadvantage: bool = False) -> Dict[str, Any]:
        """
        Perform a skill check.
        
        Per D&D 2024 rules:
        - Roll d20 + ability modifier + applicable proficiency bonus
        - With advantage, roll twice and take the higher roll
        - With disadvantage, roll twice and take the lower roll
        - Success if result equals or exceeds the DC
        
        Args:
            skill_name: Name of the skill
            ability_scores: Character's ability scores
            proficiency_bonus: Character's proficiency bonus
            difficulty_class: DC of the check
            advantage: Whether the check has advantage
            disadvantage: Whether the check has disadvantage
            
        Returns:
            Dict[str, Any]: Result of the skill check including:
                - success: Whether the check succeeded
                - roll: The dice roll result
                - total: The total check result
                - modifier: The total modifier applied
        """
        pass
    
    @abstractmethod
    def handle_group_check(self, skill_name: str, character_modifiers: List[int],
                        difficulty_class: int) -> Dict[str, Any]:
        """
        Perform a group check for multiple characters.
        
        Per D&D 2024 rules, group checks succeed if at least half the group succeeds.
        
        Args:
            skill_name: Skill being checked
            character_modifiers: List of each character's modifier for the skill
            difficulty_class: DC of the check
            
        Returns:
            Dict[str, Any]: Result of the group check
        """
        pass
    
    @abstractmethod
    def get_class_skills(self, character_class: str) -> List[str]:
        """
        Get skills typically associated with a class.
        
        Per D&D 2024 rules, each class has a list of skills to choose from
        for starting proficiencies.
        
        Args:
            character_class: Character's class
            
        Returns:
            List[str]: Skills associated with the class
        """
        pass
    
    @abstractmethod
    def get_background_skills(self, background: str) -> List[str]:
        """
        Get skills granted by a background.
        
        Per D&D 2024 rules, backgrounds typically provide two skill proficiencies.
        
        Args:
            background: Character's background
            
        Returns:
            List[str]: Skills granted by the background
        """
        pass
    
    @abstractmethod
    def get_proficient_skills(self) -> List[str]:
        """
        Get list of skills the character is proficient in.
        
        Returns:
            List[str]: Skills with proficiency
        """
        pass
    
    @abstractmethod
    def get_expertise_skills(self) -> List[str]:
        """
        Get list of skills the character has expertise in.
        
        Returns:
            List[str]: Skills with expertise
        """
        pass
    
    @abstractmethod
    def calculate_all_skill_modifiers(self, ability_scores: Dict[str, int],
                                   proficiency_bonus: int) -> Dict[str, int]:
        """
        Calculate modifiers for all skills.
        
        Args:
            ability_scores: Character's ability scores
            proficiency_bonus: Character's proficiency bonus
            
        Returns:
            Dict[str, int]: Mapping of skill names to modifiers
        """
        pass