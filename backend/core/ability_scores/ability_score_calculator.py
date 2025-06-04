"""
Ability Score Calculator

Provides utility methods for calculating and manipulating D&D ability scores.
This class handles the mathematical and algorithmic aspects of ability scores
separate from character state management.
"""

from typing import Dict, List, Tuple, Optional, Any
import random

class AbilityScoreCalculator:
    """
    A utility class for D&D ability score calculations.
    
    This class provides stateless methods for generating ability scores,
    calculating modifiers, optimizing scores for different classes,
    and applying various bonuses and improvements.
    """
    
    @staticmethod
    def calculate_modifier(score: int) -> int:
        """
        Calculate the ability modifier for a given ability score.
        
        Args:
            score: The ability score value
            
        Returns:
            int: The calculated modifier
        """
        return (score - 10) // 2
        
    @staticmethod
    def calculate_all_modifiers(ability_scores: Dict[str, int]) -> Dict[str, int]:
        """
        Calculate modifiers for all ability scores.
        
        Args:
            ability_scores: Dictionary of ability scores (e.g., {'strength': 14, 'dexterity': 12})
            
        Returns:
            Dict[str, int]: Dictionary of modifiers for each ability
        """
        return {
            ability: AbilityScoreCalculator.calculate_modifier(score)
            for ability, score in ability_scores.items()
        }
        
    @staticmethod
    def generate_standard_array() -> List[int]:
        """
        Generate the standard array of ability scores (15, 14, 13, 12, 10, 8).
        
        Returns:
            List[int]: The standard ability score array
        """
        return [15, 14, 13, 12, 10, 8]
        
    @staticmethod
    def generate_point_buy(points_spent: Dict[str, int]) -> Dict[str, int]:
        """
        Calculate ability scores using the point buy system.
        
        Args:
            points_spent: Dictionary mapping ability names to points spent
            
        Returns:
            Dict[str, int]: Resulting ability scores
        """
        # Base score is 8
        scores = {ability: 8 for ability in points_spent}
        
        # Point buy cost table
        # Score : Cost
        point_costs = {
            9: 1, 10: 2, 11: 3, 12: 4, 13: 5, 14: 7, 15: 9
        }
        
        # Calculate scores based on points spent
        for ability, points in points_spent.items():
            remaining_points = points
            score = 8
            
            while remaining_points > 0 and score < 15:
                next_score = score + 1
                cost = point_costs.get(next_score, 0)
                
                if cost <= remaining_points:
                    score = next_score
                    remaining_points -= cost
                else:
                    break
                    
            scores[ability] = score
            
        return scores
        
    @staticmethod
    def roll_ability_scores(method: str = '4d6_drop_lowest', num_sets: int = 1) -> List[List[int]]:
        """
        Generate ability scores using dice rolling methods.
        
        Args:
            method: Rolling method ('4d6_drop_lowest', '3d6', etc.)
            num_sets: Number of sets to roll
            
        Returns:
            List[List[int]]: List of ability score sets
        """
        result = []
        
        for _ in range(num_sets):
            set_scores = []
            
            for _ in range(6):  # 6 ability scores
                if method == '4d6_drop_lowest':
                    # Roll 4d6, drop the lowest die
                    rolls = [random.randint(1, 6) for _ in range(4)]
                    rolls.remove(min(rolls))
                    set_scores.append(sum(rolls))
                elif method == '3d6':
                    # Standard 3d6
                    rolls = [random.randint(1, 6) for _ in range(3)]
                    set_scores.append(sum(rolls))
                else:
                    # Default to 4d6 drop lowest
                    rolls = [random.randint(1, 6) for _ in range(4)]
                    rolls.remove(min(rolls))
                    set_scores.append(sum(rolls))
            
            result.append(set_scores)
            
        return result
        
    @staticmethod
    def get_class_primary_abilities(class_name: str) -> List[str]:
        """
        Get the primary abilities for a given class.
        
        Args:
            class_name: Name of the character class
            
        Returns:
            List[str]: List of primary abilities for the class
        """
        class_abilities = {
            'barbarian': ['strength', 'constitution'],
            'bard': ['charisma', 'dexterity'],
            'cleric': ['wisdom', 'constitution'],
            'druid': ['wisdom', 'constitution'],
            'fighter': ['strength', 'constitution'],
            'monk': ['dexterity', 'wisdom'],
            'paladin': ['strength', 'charisma'],
            'ranger': ['dexterity', 'wisdom'],
            'rogue': ['dexterity', 'intelligence'],
            'sorcerer': ['charisma', 'constitution'],
            'warlock': ['charisma', 'constitution'],
            'wizard': ['intelligence', 'constitution'],
        }
        
        return class_abilities.get(class_name.lower(), ['constitution', 'dexterity'])
        
    @staticmethod
    def optimize_for_class(scores: List[int], class_name: str) -> Dict[str, int]:
        """
        Optimally assign ability scores for a given class.
        
        Args:
            scores: List of ability score values to assign
            class_name: Character class name
            
        Returns:
            Dict[str, int]: Optimally assigned ability scores
        """
        abilities = ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']
        primary_abilities = AbilityScoreCalculator.get_class_primary_abilities(class_name)
        
        # Sort scores in descending order
        sorted_scores = sorted(scores, reverse=True)
        
        # Create ability score dictionary
        result = {}
        
        # Assign highest scores to primary abilities
        for ability in primary_abilities:
            if sorted_scores:
                result[ability] = sorted_scores.pop(0)
        
        # Constitution is always important if not already assigned
        if 'constitution' not in result and sorted_scores:
            result['constitution'] = sorted_scores.pop(0)
        
        # Assign remaining scores to remaining abilities
        remaining_abilities = [a for a in abilities if a not in result]
        for ability in remaining_abilities:
            if sorted_scores:
                result[ability] = sorted_scores.pop(0)
            else:
                result[ability] = 8  # Default minimum
                
        return result
        
    @staticmethod
    def apply_species_bonuses(base_scores: Dict[str, int], species_bonuses: Dict[str, int]) -> Dict[str, int]:
        """
        Apply species/racial ability score bonuses.
        
        Args:
            base_scores: Base ability scores
            species_bonuses: Bonuses to apply to specific abilities
            
        Returns:
            Dict[str, int]: Updated ability scores with bonuses applied
        """
        result = base_scores.copy()
        
        for ability, bonus in species_bonuses.items():
            if ability in result:
                result[ability] += bonus
        
        return result
    
    @staticmethod
    def get_default_species_bonuses(species_name: str) -> Dict[str, int]:
        """
        Get default ability score bonuses for a species.
        
        Args:
            species_name: Name of the species/race
            
        Returns:
            Dict[str, int]: Dictionary of ability bonuses
        """
        # Default D&D 5e racial bonuses
        species_bonuses = {
            'human': {ability: 1 for ability in ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']},
            'elf': {'dexterity': 2, 'intelligence': 1},
            'dwarf': {'constitution': 2, 'wisdom': 1},
            'halfling': {'dexterity': 2, 'charisma': 1},
            'dragonborn': {'strength': 2, 'charisma': 1},
            'gnome': {'intelligence': 2, 'dexterity': 1},
            'half-elf': {'charisma': 2, 'choice': 2},  # 'choice' indicates player chooses
            'half-orc': {'strength': 2, 'constitution': 1},
            'tiefling': {'charisma': 2, 'intelligence': 1}
        }
        
        return species_bonuses.get(species_name.lower(), {})
        
    @staticmethod
    def apply_ability_score_improvement(current_scores: Dict[str, int], 
                                     improvements: Dict[str, int]) -> Dict[str, int]:
        """
        Apply ability score improvements (e.g., from level-ups).
        
        Args:
            current_scores: Current ability scores
            improvements: Dictionary mapping abilities to improvement values
            
        Returns:
            Dict[str, int]: Updated ability scores with improvements applied
        """
        result = current_scores.copy()
        
        for ability, improvement in improvements.items():
            if ability in result:
                result[ability] += improvement
                # Cap at 20 as per D&D rules
                result[ability] = min(result[ability], 20)
        
        return result
        
    @staticmethod
    def available_asi_options(class_name: str, level: int) -> Dict[str, Any]:
        """
        Get available Ability Score Improvement options for a class and level.
        
        Args:
            class_name: Character class name
            level: Character level
            
        Returns:
            Dict[str, Any]: Information about ASI options
        """
        # Standard ASI levels for all classes
        standard_asi_levels = [4, 8, 12, 16, 19]
        
        # Special case for Fighter
        if class_name.lower() == 'fighter':
            standard_asi_levels = [4, 6, 8, 12, 14, 16, 19]
        
        # Special case for Rogue
        elif class_name.lower() == 'rogue':
            standard_asi_levels = [4, 8, 10, 12, 16, 19]
        
        return {
            'available': level in standard_asi_levels,
            'options': [
                {'type': 'ability_score_improvement', 'description': '+2 to one ability score or +1 to two ability scores'},
                {'type': 'feat', 'description': 'Take a feat instead of an ability score improvement'}
            ],
            'max_score': 20
        }
        
    @staticmethod
    def check_valid_array(scores: List[int]) -> bool:
        """
        Check if a set of ability scores is valid according to D&D rules.
        
        Args:
            scores: List of ability scores to validate
            
        Returns:
            bool: Whether the scores form a valid array
        """
        if len(scores) != 6:
            return False
            
        # Check if all scores are within valid range
        for score in scores:
            if score < 3 or score > 20:
                return False
                
        return True
    
    @staticmethod
    def get_ability_check_bonus(ability_score: int, proficient: bool = False, 
                             proficiency_bonus: int = 2, expertise: bool = False) -> int:
        """
        Calculate bonus for ability checks.
        
        Args:
            ability_score: The ability score value
            proficient: Whether the character is proficient in this check
            proficiency_bonus: Character's proficiency bonus
            expertise: Whether the character has expertise (double proficiency)
            
        Returns:
            int: Total bonus for the ability check
        """
        ability_modifier = AbilityScoreCalculator.calculate_modifier(ability_score)
        
        if expertise:
            proficiency_modifier = proficiency_bonus * 2
        elif proficient:
            proficiency_modifier = proficiency_bonus
        else:
            proficiency_modifier = 0
        
        return ability_modifier + proficiency_modifier