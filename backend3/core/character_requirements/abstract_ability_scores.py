from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any

class AbilityScores(ABC):
    """
    Abstract base class defining the interface for handling character ability scores in D&D 5e (2024 Edition).
    
    This class establishes the contract for ability score operations according to the official rules.
    """
    
    # Core ability score names
    ABILITY_SCORES = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
    
    # Official ability score limits
    MIN_SCORE = 3  # Absolute minimum (per rules)
    MAX_SCORE = 20  # Maximum without magical enhancement
    MAX_SCORE_HARD_CAP = 30  # Absolute maximum with magical enhancement
    
    # Official point buy system parameters
    POINT_BUY_TOTAL = 27  # Standard point-buy budget
    POINT_BUY_MIN = 8     # Minimum score in point-buy
    POINT_BUY_MAX = 15    # Maximum score in point-buy
    
    @abstractmethod
    def calculate_modifier(self, score: int) -> int:
        """
        Calculate ability modifier based on score.
        
        Per D&D 2024 rules, modifier = floor((score - 10) / 2)
        
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
        
        Per D&D 2024 rules:
        Score 8: 0 points
        Score 9: 1 point
        Score 10: 2 points
        Score 11: 3 points
        Score 12: 4 points
        Score 13: 5 points
        Score 14: 7 points
        Score 15: 9 points
        
        Args:
            score: The ability score to calculate cost for
            
        Returns:
            int: Point-buy cost
        """
        pass

    @abstractmethod
    def validate_ability_scores(self, scores_dict: Dict[str, int]) -> bool:
        """
        Validate ability scores against official rules.
        
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
        
        Per D&D 2024 rules, the standard array is [15, 14, 13, 12, 10, 8]
        
        Returns:
            List[int]: Standard array of ability scores
        """
        pass

    @abstractmethod
    def generate_random_scores(self) -> List[int]:
        """
        Generate random ability scores using 4d6 drop lowest method.
        
        Per D&D 2024 rules: Roll 4d6, drop the lowest die, sum the remaining three.
        Repeat six times to generate the six ability scores.
        
        Returns:
            List[int]: Randomly generated ability scores
        """
        pass

    @abstractmethod
    def apply_species_bonuses(self, scores_dict: Dict[str, int], species_bonuses: Dict[str, int]) -> Dict[str, int]:
        """
        Apply species bonuses to ability scores.
        
        Per D&D 2024 rules, species may provide specific ability score increases.
        
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
        
        Per D&D 2024 rules, ASIs typically allow +2 to one score and +1 to another,
        or +1 to three different scores, subject to the MAX_SCORE cap.
        
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