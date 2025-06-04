from abc import ABC, abstractmethod
import math
import random
from typing import Dict, List, Tuple, Optional, Any

class AbilityScores(ABC):
    """
    Abstract base class for handling character ability scores in D&D 5e (2024 Edition).
    
    Ability scores in D&D define a character's natural capabilities:
    - Strength (STR): Physical power and carrying capacity
    - Dexterity (DEX): Agility, reflexes, and balance
    - Constitution (CON): Health, stamina, and vital force
    - Intelligence (INT): Mental acuity, information recall, analytical skill
    - Wisdom (WIS): Awareness, intuition, and insight
    - Charisma (CHA): Force of personality, persuasiveness, leadership
    """
    
    # Define ability score constants
    ABILITY_SCORES = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
    
    # Define ability score limits
    MIN_SCORE = 3  # Absolute minimum
    MAX_SCORE = 20  # Maximum without magical enhancement
    MAX_SCORE_HARD_CAP = 30  # Absolute maximum with magical enhancement
    
    # Point buy system constants
    POINT_BUY_TOTAL = 27  # Standard point-buy budget
    POINT_BUY_MIN = 8     # Minimum score in point-buy
    POINT_BUY_MAX = 15    # Maximum score in point-buy
    
    def __init__(self, scores: Dict[str, int] = None):
        """
        Initialize ability scores.
        
        Args:
            scores: Dictionary mapping ability names to scores
        """
        if scores is None:
            # Use standard array by default
            score_array = self.generate_standard_array()
            self.scores = dict(zip(self.ABILITY_SCORES, score_array))
        else:
            # Validate and set provided scores
            if self.validate_ability_scores(scores):
                self.scores = scores
            else:
                raise ValueError("Invalid ability scores provided")

    @abstractmethod
    def calculate_modifier(self, score: int) -> int:
        """
        Calculate ability modifier based on score.
        
        Args:
            score: Ability score value
            
        Returns:
            int: Ability modifier
        """
        pass

    @abstractmethod
    def get_point_buy_cost(self, score: int) -> int:
        """
        Get the point-buy cost for a specific score.
        
        Args:
            score: The ability score to calculate cost for
            
        Returns:
            int: Point-buy cost
        """
        pass

    @abstractmethod
    def validate_ability_scores(self, scores_dict: Dict[str, int]) -> bool:
        """
        Validate ability scores against rules.
        
        Args:
            scores_dict: Dictionary of ability scores
            
        Returns:
            bool: True if valid, False otherwise
        """
        pass

    @abstractmethod
    def generate_standard_array(self) -> List[int]:
        """
        Return the standard ability score array.
        
        Returns:
            List[int]: Standard array of ability scores
        """
        pass

    @abstractmethod
    def generate_random_scores(self) -> List[int]:
        """
        Generate random ability scores using 4d6 drop lowest method.
        
        Returns:
            List[int]: Randomly generated ability scores
        """
        pass

    @abstractmethod
    def apply_species_bonuses(self, scores_dict: Dict[str, int], species_bonuses: Dict[str, int]) -> Dict[str, int]:
        """
        Apply species bonuses to ability scores.
        
        Args:
            scores_dict: Current ability scores
            species_bonuses: Bonuses to apply
            
        Returns:
            Dict[str, int]: Updated ability scores with bonuses applied
        """
        pass
        
    @abstractmethod
    def calculate_total_point_buy_cost(self, scores_dict: Dict[str, int]) -> int:
        """
        Calculate the total point-buy cost for a set of ability scores.
        
        Args:
            scores_dict: Dictionary of ability scores
            
        Returns:
            int: Total point-buy cost
        """
        pass
        
    @abstractmethod
    def apply_ability_score_improvement(self, scores_dict: Dict[str, int], improvements: Dict[str, int]) -> Dict[str, int]:
        """
        Apply Ability Score Improvements (ASI).
        
        Args:
            scores_dict: Current ability scores
            improvements: Improvements to apply (e.g., {"strength": 2, "constitution": 1})
            
        Returns:
            Dict[str, int]: Updated ability scores with improvements applied
        """
        pass
        
    @abstractmethod
    def get_all_modifiers(self, scores_dict: Dict[str, int]) -> Dict[str, int]:
        """
        Get all ability modifiers from scores.
        
        Args:
            scores_dict: Dictionary of ability scores
            
        Returns:
            Dict[str, int]: Dictionary of ability modifiers
        """
        pass
        
    @abstractmethod
    def suggest_ability_score_distribution(self, character_class: str) -> Dict[str, int]:
        """
        Suggest an optimal ability score distribution for a specific class.
        
        Args:
            character_class: The character class to optimize for
            
        Returns:
            Dict[str, int]: Suggested ability score distribution
        """
        pass
        
    def __str__(self) -> str:
        """
        String representation of ability scores.
        
        Returns:
            str: Formatted ability scores
        """
        result = "Ability Scores:\n"
        for ability, score in self.scores.items():
            modifier = self.calculate_modifier(score)
            sign = "+" if modifier >= 0 else ""
            result += f"  {ability.capitalize()}: {score} ({sign}{modifier})\n"
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert ability scores to dictionary format.
        
        Returns:
            Dict: Dictionary representation of ability scores
        """
        return {
            "scores": self.scores,
            "modifiers": {
                ability: self.calculate_modifier(score) 
                for ability, score in self.scores.items()
            }
        }