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
    ALL_SKILLS = [
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
    
    def __init__(self):
        """
        Initialize the skills system.
        """
        # Proficiency levels for each skill
        self.skill_proficiencies = {skill: ProficiencyLevel.NONE for skill in self.ALL_SKILLS}
        
        # Tool proficiencies (separate from skills but using similar mechanics)
        self.tool_proficiencies = set()
        
        # Passive skill values (calculated dynamically but can be cached)
        self._passive_skills = {}
    
    @abstractmethod
    def get_all_skills(self) -> List[str]:
        """
        Return a list of all available skills.
        
        Returns:
            List[str]: List of all skill names
        """
        pass
    
    @abstractmethod
    def get_skill_info(self, skill_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a skill.
        
        Args:
            skill_name: Name of the skill
            
        Returns:
            Dict[str, Any]: Dictionary with skill details
        """
        pass
    
    @abstractmethod
    def calculate_skill_modifier(self, skill_name: str, ability_scores: Dict[str, int],
                               proficiency_bonus: int) -> int:
        """
        Calculate modifier for a skill.
        
        Args:
            skill_name: Name of the skill
            ability_scores: Character's ability scores
            proficiency_bonus: Character's proficiency bonus
            
        Returns:
            int: Skill modifier
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
        Calculate passive value for a skill (typically 10 + modifier).
        
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
        
        Args:
            skill_name: Name of the skill
            ability_scores: Character's ability scores
            proficiency_bonus: Character's proficiency bonus
            difficulty_class: DC of the check
            advantage: Whether the check has advantage
            disadvantage: Whether the check has disadvantage
            
        Returns:
            Dict[str, Any]: Result of the skill check
        """
        pass
    
    @abstractmethod
    def add_tool_proficiency(self, tool_name: str) -> bool:
        """
        Add a tool proficiency.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            bool: True if successful
        """
        pass
    
    @abstractmethod
    def is_tool_proficient(self, tool_name: str) -> bool:
        """
        Check if character is proficient with a tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            bool: True if proficient
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
    
    @abstractmethod
    def get_recommended_skills(self, character_class: str, background: str) -> List[str]:
        """
        Get recommended skills based on class and background.
        
        Args:
            character_class: Character's class
            background: Character's background
            
        Returns:
            List[str]: Recommended skills
        """
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert skills information to dictionary format.
        
        Returns:
            Dict[str, Any]: Dictionary representation of skills
        """
        return {
            "skill_proficiencies": {
                skill: level.name for skill, level in self.skill_proficiencies.items()
            },
            "tool_proficiencies": list(self.tool_proficiencies)
        }
    
    def __str__(self) -> str:
        """
        String representation of skills.
        
        Returns:
            str: Formatted skills string
        """
        proficient_skills = [s for s, p in self.skill_proficiencies.items() 
                           if p == ProficiencyLevel.PROFICIENT]
        expertise_skills = [s for s, p in self.skill_proficiencies.items() 
                          if p == ProficiencyLevel.EXPERT]
        
        result = "Skills:\n"
        
        if proficient_skills:
            result += "  Proficient:\n"
            for skill in sorted(proficient_skills):
                result += f"    - {skill}\n"
        
        if expertise_skills:
            result += "  Expertise:\n"
            for skill in sorted(expertise_skills):
                result += f"    - {skill}\n"
        
        if self.tool_proficiencies:
            result += "  Tool Proficiencies:\n"
            for tool in sorted(self.tool_proficiencies):
                result += f"    - {tool}\n"
                
        return result