"""
Ability Scores Module

Manages ability scores calculation, modifications, and derived statistics for D&D characters.
Provides methods for generating, assigning, and optimizing ability scores.
"""

from typing import Dict, List, Tuple, Optional, Any, Union
import random
import json
from pathlib import Path

try:
    from backend.core.character.abstract_character import AbstractCharacterClass
except ImportError:
    # Fallback for development
    AbstractCharacterClass = object


class AbilityScores(AbstractCharacterClass):
    """
    Handles all ability score-related functionality for D&D character creation.
    
    This class manages the generation, assignment, modification, and optimization
    of character ability scores, providing methods for different generation techniques,
    calculating modifiers, and applying bonuses from species, classes, and other sources.
    """

    def __init__(self, rules_data_path: str = None):
        """
        Initialize the AbilityScores manager.
        
        Args:
            rules_data_path: Optional path to rules data directory
        """
        self.ability_names = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        
        # Standard generation methods
        self.generation_methods = {
            "standard_array": [15, 14, 13, 12, 10, 8],
            "basic_array": [13, 12, 11, 10, 9, 8],  # Simpler array for beginners
            "heroic_array": [16, 15, 13, 12, 10, 8],  # Higher power level
        }
        
        # Point buy costs (D&D 5e uses a 27-point system)
        self.point_buy_costs = {
            8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 13: 5, 14: 7, 15: 9
        }
        self.point_buy_min = 8
        self.point_buy_max = 15
        self.point_buy_points = 27
        
        # Load class and species data for optimization recommendations
        self.data_dir = Path(rules_data_path) if rules_data_path else Path("backend/data/rules")
        self._load_rules_data()
        
    def _load_rules_data(self):
        """Load rules data from JSON files."""
        try:
            # Load class data for ability score recommendations
            with open(self.data_dir / "classes.json", "r") as f:
                self.class_data = json.load(f)
                
            # Load species data for ability score bonuses
            with open(self.data_dir / "species.json", "r") as f:
                self.species_data = json.load(f)
                
        except FileNotFoundError as e:
            print(f"Warning: Could not load rules data: {e}")
            # Initialize with empty data as fallback
            self.class_data = {}
            self.species_data = {}
    
    def generate_ability_scores(self, method: str = 'standard_array', custom_values: List[int] = None) -> List[int]:
        """
        Generate a set of ability scores using the specified method.
        
        Args:
            method: Generation method ('standard_array', 'point_buy', 'rolled', or 'custom')
            custom_values: Custom ability score values if method is 'custom'
            
        Returns:
            List[int]: Generated ability scores
        """
        if method == 'custom' and custom_values:
            # Validate custom values
            if len(custom_values) != 6:
                raise ValueError("Custom values must have exactly 6 ability scores")
            for score in custom_values:
                if not isinstance(score, int) or score < 3 or score > 20:
                    raise ValueError("Ability scores must be integers between 3 and 20")
            return custom_values
        
        elif method in self.generation_methods:
            # Use a predefined array
            return self.generation_methods[method].copy()
        
        elif method == 'point_buy':
            # Start with all 8s for point buy
            return [8, 8, 8, 8, 8, 8]
        
        elif method == 'rolled':
            # Roll 4d6, drop lowest, six times
            rolled_scores = []
            for _ in range(6):
                rolls = [random.randint(1, 6) for _ in range(4)]
                # Drop lowest roll
                rolls.remove(min(rolls))
                rolled_scores.append(sum(rolls))
            
            # Sort in descending order
            rolled_scores.sort(reverse=True)
            return rolled_scores
        
        else:
            # Default to standard array if method not recognized
            print(f"Warning: Unrecognized method '{method}', using standard array")
            return self.generation_methods["standard_array"].copy()
    
    def assign_ability_scores(self, scores: List[int], class_type: str, 
                            species: str = None) -> Dict[str, int]:
        """
        Assign ability scores optimally based on class and species.
        
        Args:
            scores: List of ability score values to assign
            class_type: Character class name
            species: Optional species/race name
            
        Returns:
            Dict[str, int]: Assigned ability scores by name
        """
        # Ensure scores are sorted in descending order
        sorted_scores = sorted(scores, reverse=True)
        
        # Get class ability priorities
        priorities = self._get_class_ability_priorities(class_type)
        
        # Create a dictionary to store the assigned scores
        ability_scores = {}
        
        # Assign scores based on priorities
        for i, ability in enumerate(priorities):
            # Make sure we don't go out of bounds
            if i < len(sorted_scores):
                ability_scores[ability] = sorted_scores[i]
            else:
                # Fallback if we have fewer scores than abilities
                ability_scores[ability] = 10  # Default value
        
        # Ensure all abilities have a value
        for ability in self.ability_names:
            if ability not in ability_scores:
                # Assign remaining scores or default
                if len(ability_scores) < len(sorted_scores):
                    ability_scores[ability] = sorted_scores[len(ability_scores)]
                else:
                    ability_scores[ability] = 10  # Default value
        
        return ability_scores
    
    def calculate_ability_modifiers(self, scores: Dict[str, int]) -> Dict[str, int]:
        """
        Calculate ability modifiers from scores using the D&D formula.
        
        Args:
            scores: Dictionary of ability scores
            
        Returns:
            Dict[str, int]: Calculated ability modifiers
        """
        modifiers = {}
        for ability, score in scores.items():
            # D&D formula: (score - 10) / 2, rounded down
            modifiers[ability] = (score - 10) // 2
        
        return modifiers
    
    def apply_species_bonuses(self, ability_scores: Dict[str, int], 
                           species: str, subrace: str = None) -> Dict[str, int]:
        """
        Apply species (race) ability score bonuses.
        
        Args:
            ability_scores: Dictionary of ability scores
            species: Species/race name
            subrace: Optional subrace name
            
        Returns:
            Dict[str, int]: Updated ability scores with applied bonuses
        """
        # Normalize species name for lookup
        species_key = species.lower().replace(" ", "_") if species else ""
        
        if not species_key or species_key not in self.species_data:
            return ability_scores
        
        # Get species data
        species_info = self.species_data[species_key]
        
        # Apply species ability bonuses
        updated_scores = ability_scores.copy()
        for ability, bonus in species_info.get("ability_bonuses", {}).items():
            if ability in updated_scores:
                updated_scores[ability] += bonus
        
        # Apply subrace bonuses if applicable
        if subrace:
            subrace_key = subrace.lower().replace(" ", "_")
            subraces = species_info.get("subraces", {})
            
            if subrace_key in subraces:
                subrace_info = subraces[subrace_key]
                
                # Apply subrace ability bonuses
                for ability, bonus in subrace_info.get("ability_bonuses", {}).items():
                    if ability in updated_scores:
                        updated_scores[ability] += bonus
        
        # Ensure no score exceeds 20 (the natural maximum in D&D 5e)
        for ability, score in updated_scores.items():
            if score > 20:
                updated_scores[ability] = 20
        
        return updated_scores
    
    def apply_asi_or_feat(self, ability_scores: Dict[str, int], 
                        choice: Union[Dict[str, int], str]) -> Dict[str, int]:
        """
        Apply Ability Score Improvement (ASI) or feat.
        
        Args:
            ability_scores: Dictionary of current ability scores
            choice: Either a dictionary of ability improvements or a feat name
            
        Returns:
            Dict[str, int]: Updated ability scores
        """
        updated_scores = ability_scores.copy()
        
        # Check if choice is an ASI dictionary
        if isinstance(choice, dict):
            for ability, increase in choice.items():
                if ability in updated_scores:
                    updated_scores[ability] += increase
                    
                    # Ensure no score exceeds 20 (the natural maximum in D&D 5e)
                    if updated_scores[ability] > 20:
                        updated_scores[ability] = 20
        
        # If it's a feat, apply any ASIs associated with that feat
        elif isinstance(choice, str):
            feat_name = choice.lower().replace(" ", "_")
            
            # We would need a feat database to implement this properly
            # For now, let's handle just a few common feats that provide ASIs
            feat_asi_map = {
                "athlete": {"strength": 1, "dexterity": 1},
                "actor": {"charisma": 1},
                "durable": {"constitution": 1},
                "keen_mind": {"intelligence": 1},
                "observant": {"wisdom": 1},
                "resilient": {},  # Would need to know which ability
                "heavy_armor_master": {"strength": 1},
                "weapon_master": {"strength": 1},
                "moderately_armored": {"dexterity": 1},
                "lightly_armored": {"dexterity": 1}
            }
            
            if feat_name in feat_asi_map:
                for ability, increase in feat_asi_map[feat_name].items():
                    updated_scores[ability] += increase
                    
                    # Ensure no score exceeds 20
                    if updated_scores[ability] > 20:
                        updated_scores[ability] = 20
        
        return updated_scores
    
    def suggest_optimal_distribution(self, class_type: str, species: str = None,
                                  subrace: str = None, method: str = 'standard_array',
                                  rolled_scores: List[int] = None) -> Dict[str, Any]:
        """
        Suggest optimal ability score distribution for a given class and species.
        
        Args:
            class_type: Character class name
            species: Optional species/race name
            subrace: Optional subrace name
            method: Ability score generation method
            rolled_scores: Optional list of rolled scores if method is 'rolled'
            
        Returns:
            Dict[str, Any]: Suggested ability score distribution with explanations
        """
        # Generate base scores based on the method
        if method == 'rolled' and rolled_scores:
            base_scores = sorted(rolled_scores, reverse=True)
        else:
            base_scores = self.generate_ability_scores(method)
        
        # Get class priorities
        priorities = self._get_class_ability_priorities(class_type)
        priority_explanations = self._get_class_ability_explanations(class_type)
        
        # Assign scores based on priorities
        assigned_scores = {}
        for i, ability in enumerate(priorities):
            if i < len(base_scores):
                assigned_scores[ability] = base_scores[i]
        
        # Fill in any missing abilities
        for ability in self.ability_names:
            if ability not in assigned_scores:
                # Assign remaining scores or default
                remaining_scores = [s for s in base_scores if s not in assigned_scores.values()]
                if remaining_scores:
                    assigned_scores[ability] = remaining_scores[0]
                    base_scores.remove(remaining_scores[0])
                else:
                    assigned_scores[ability] = 10  # Default value
        
        # Apply species bonuses if provided
        if species:
            assigned_scores = self.apply_species_bonuses(assigned_scores, species, subrace)
        
        # Calculate resulting modifiers
        modifiers = self.calculate_ability_modifiers(assigned_scores)
        
        # Create the result with explanations
        result = {
            "suggested_scores": assigned_scores,
            "resulting_modifiers": modifiers,
            "priorities": priorities[:3],  # Top 3 priorities
            "explanations": {
                ability: priority_explanations.get(ability, "General utility")
                for ability in priorities[:3]
            },
            "species_bonuses": self._get_species_ability_bonuses(species, subrace) if species else {},
            "generation_method": method
        }
        
        return result
    
    def validate_point_buy(self, ability_scores: Dict[str, int]) -> Tuple[bool, str, int]:
        """
        Validate that ability scores conform to point buy rules.
        
        Args:
            ability_scores: Dictionary of ability scores
            
        Returns:
            Tuple[bool, str, int]: (Valid, Error Message, Points Used)
        """
        # Check if all scores are within allowed point buy range
        for ability, score in ability_scores.items():
            if score < self.point_buy_min or score > self.point_buy_max:
                return (False, f"{ability.capitalize()} score {score} outside point buy range ({self.point_buy_min}-{self.point_buy_max})", 0)
                
        # Calculate total point cost
        points_used = 0
        for score in ability_scores.values():
            if score in self.point_buy_costs:
                points_used += self.point_buy_costs[score]
            else:
                return (False, f"Score {score} not valid in point buy system", 0)
        
        # Check if within point budget
        if points_used > self.point_buy_points:
            return (False, f"Used {points_used} points, exceeding maximum of {self.point_buy_points}", points_used)
            
        return (True, f"Valid point buy using {points_used}/{self.point_buy_points} points", points_used)
    
    def point_buy_calculator(self, scores: Dict[str, int]) -> Dict[str, Any]:
        """
        Calculate point buy costs for the given scores.
        
        Args:
            scores: Dictionary of ability scores
            
        Returns:
            Dict[str, Any]: Point buy calculation results
        """
        results = {
            "individual_costs": {},
            "total_cost": 0,
            "remaining_points": self.point_buy_points,
            "valid": True,
            "message": ""
        }
        
        # Calculate individual costs
        for ability, score in scores.items():
            if score in self.point_buy_costs:
                cost = self.point_buy_costs[score]
                results["individual_costs"][ability] = cost
                results["total_cost"] += cost
            else:
                results["individual_costs"][ability] = "invalid"
                results["valid"] = False
                results["message"] = f"Score {score} for {ability} not valid in point buy system"
        
        # Calculate remaining points
        results["remaining_points"] = self.point_buy_points - results["total_cost"]
        
        # Validate total
        if results["valid"]:
            if results["total_cost"] > self.point_buy_points:
                results["valid"] = False
                results["message"] = f"Used {results['total_cost']} points, exceeding maximum of {self.point_buy_points}"
            else:
                results["message"] = f"Valid point buy using {results['total_cost']}/{self.point_buy_points} points"
        
        return results
    
    def generate_random_character_stats(self, class_type: str = None, 
                                     species: str = None, subrace: str = None) -> Dict[str, Any]:
        """
        Generate a complete random set of ability scores for a character.
        
        Args:
            class_type: Optional character class for optimization
            species: Optional species/race for bonuses
            subrace: Optional subrace for additional bonuses
            
        Returns:
            Dict[str, Any]: Complete ability score information
        """
        # Roll random scores
        rolled_scores = self.generate_ability_scores(method='rolled')
        
        # If class specified, assign optimally
        if class_type:
            assigned_scores = self.assign_ability_scores(rolled_scores, class_type)
        else:
            # Assign randomly
            random.shuffle(rolled_scores)
            assigned_scores = {ability: rolled_scores[i] for i, ability in enumerate(self.ability_names)}
        
        # Apply species bonuses if specified
        if species:
            assigned_scores = self.apply_species_bonuses(assigned_scores, species, subrace)
        
        # Calculate modifiers
        modifiers = self.calculate_ability_modifiers(assigned_scores)
        
        return {
            "scores": assigned_scores,
            "modifiers": modifiers,
            "generation_method": "rolled",
            "original_rolls": rolled_scores
        }
    
    def _get_class_ability_priorities(self, class_type: str) -> List[str]:
        """
        Get ability score priorities for a given class.
        
        Args:
            class_type: Character class name
            
        Returns:
            List[str]: Ordered list of ability priorities
        """
        # Normalize class name for lookup
        class_key = class_type.lower().replace(" ", "_") if class_type else ""
        
        if not class_key or class_key not in self.class_data:
            # Default priorities as fallback
            return ["strength", "constitution", "dexterity", "wisdom", "intelligence", "charisma"]
        
        # Get class data
        class_info = self.class_data[class_key]
        
        # Get primary and secondary abilities
        primary = class_info.get("primary_ability", "").lower()
        secondary = class_info.get("secondary_ability", "").lower()
        
        # Build priorities list
        priorities = []
        
        # Add primary ability if it exists
        if primary and primary in self.ability_names:
            priorities.append(primary)
        
        # Add secondary ability if it exists
        if secondary and secondary in self.ability_names:
            priorities.append(secondary)
        
        # Constitution is almost always important
        if "constitution" not in priorities:
            priorities.append("constitution")
        
        # Add remaining abilities based on general utility for the class
        class_specific_order = self._get_class_specific_order(class_key)
        
        for ability in class_specific_order:
            if ability not in priorities:
                priorities.append(ability)
        
        return priorities
    
    def _get_class_specific_order(self, class_key: str) -> List[str]:
        """
        Get class-specific ability score priority ordering.
        
        Args:
            class_key: Normalized class name key
            
        Returns:
            List[str]: Ordered list of abilities
        """
        # Define class-specific ability priorities
        class_priorities = {
            "barbarian": ["strength", "constitution", "dexterity", "wisdom", "charisma", "intelligence"],
            "bard": ["charisma", "dexterity", "constitution", "intelligence", "wisdom", "strength"],
            "cleric": ["wisdom", "constitution", "strength", "dexterity", "charisma", "intelligence"],
            "druid": ["wisdom", "constitution", "dexterity", "intelligence", "charisma", "strength"],
            "fighter": ["strength", "constitution", "dexterity", "wisdom", "intelligence", "charisma"],
            "monk": ["dexterity", "wisdom", "constitution", "strength", "intelligence", "charisma"],
            "paladin": ["strength", "charisma", "constitution", "wisdom", "intelligence", "dexterity"],
            "ranger": ["dexterity", "wisdom", "constitution", "intelligence", "strength", "charisma"],
            "rogue": ["dexterity", "intelligence", "constitution", "wisdom", "charisma", "strength"],
            "sorcerer": ["charisma", "constitution", "dexterity", "wisdom", "intelligence", "strength"],
            "warlock": ["charisma", "constitution", "dexterity", "wisdom", "intelligence", "strength"],
            "wizard": ["intelligence", "constitution", "dexterity", "wisdom", "charisma", "strength"]
        }
        
        return class_priorities.get(class_key, self.ability_names)
    
    def _get_class_ability_explanations(self, class_type: str) -> Dict[str, str]:
        """
        Get explanations for why each ability is important for a class.
        
        Args:
            class_type: Character class name
            
        Returns:
            Dict[str, str]: Explanations by ability name
        """
        # Normalize class name for lookup
        class_key = class_type.lower().replace(" ", "_") if class_type else ""
        
        # Default explanations
        default_explanations = {
            "strength": "Useful for carrying capacity and melee attacks",
            "dexterity": "Improves AC, initiative, and ranged attacks",
            "constitution": "Increases hit points and helps with concentration saves",
            "intelligence": "Determines number of skills and knowledge checks",
            "wisdom": "Improves perception and willpower saves",
            "charisma": "Enhances social interactions and persuasion"
        }
        
        # Class-specific explanations
        class_explanations = {
            "barbarian": {
                "strength": "Primary attack ability for melee weapons and determines damage bonus",
                "constitution": "Increases hit points and improves Unarmored Defense AC",
                "dexterity": "Secondary ability for AC when not wearing heavy armor"
            },
            "bard": {
                "charisma": "Primary spellcasting ability and affects many bard abilities",
                "dexterity": "Improves AC with light armor and helps with many skills",
                "constitution": "Increases hit points and helps maintain concentration on spells"
            },
            "cleric": {
                "wisdom": "Primary spellcasting ability determining spell save DC and attack bonus",
                "constitution": "Increases hit points and helps maintain concentration on spells",
                "strength": "Useful for melee attacks if taking a frontline role"
            },
            "druid": {
                "wisdom": "Primary spellcasting ability determining spell save DC and attack bonus",
                "constitution": "Increases hit points and helps maintain concentration on spells",
                "dexterity": "Improves AC while wearing non-metal armor"
            },
            "fighter": {
                "strength": "Primary attack ability for melee weapons (unless using Dexterity builds)",
                "constitution": "Increases hit points for better frontline staying power",
                "dexterity": "Important for initiative and AC, primary for ranged fighters"
            },
            "monk": {
                "dexterity": "Primary attack ability and contributes to AC with Unarmored Defense",
                "wisdom": "Increases AC with Unarmored Defense and affects ki save DC",
                "constitution": "Increases hit points for better survivability"
            },
            "paladin": {
                "strength": "Primary attack ability for melee weapons",
                "charisma": "Spellcasting ability and improves aura bonuses",
                "constitution": "Increases hit points for better frontline staying power"
            },
            "ranger": {
                "dexterity": "Primary attack ability for ranged and finesse weapons",
                "wisdom": "Spellcasting ability and improves key ranger skills",
                "constitution": "Increases hit points for better survivability"
            },
            "rogue": {
                "dexterity": "Primary attack ability for Sneak Attack and improves key skills",
                "intelligence": "Improves Investigation and other skills, important for Arcane Trickster",
                "constitution": "Increases hit points for better survivability"
            },
            "sorcerer": {
                "charisma": "Primary spellcasting ability determining spell save DC and attack bonus",
                "constitution": "Increases hit points and helps maintain concentration on spells",
                "dexterity": "Improves AC without armor and helps with Dexterity saves"
            },
            "warlock": {
                "charisma": "Primary spellcasting ability determining spell save DC and attack bonus",
                "constitution": "Increases hit points and helps maintain concentration on spells",
                "dexterity": "Improves AC with light armor and helps with Dexterity saves"
            },
            "wizard": {
                "intelligence": "Primary spellcasting ability determining spell save DC and attack bonus",
                "constitution": "Increases hit points and helps maintain concentration on spells",
                "dexterity": "Improves AC without armor and helps with Dexterity saves"
            }
        }
        
        # Get class-specific explanations or use defaults
        if class_key in class_explanations:
            explanations = default_explanations.copy()
            explanations.update(class_explanations[class_key])
            return explanations
        else:
            return default_explanations
            
    def _get_species_ability_bonuses(self, species: str, subrace: str = None) -> Dict[str, int]:
        """
        Get ability bonuses for a species/race and subrace.
        
        Args:
            species: Species/race name
            subrace: Optional subrace name
            
        Returns:
            Dict[str, int]: Ability bonuses
        """
        bonuses = {}
        
        # Normalize species name for lookup
        species_key = species.lower().replace(" ", "_") if species else ""
        
        if not species_key or species_key not in self.species_data:
            return bonuses
        
        # Get species data
        species_info = self.species_data[species_key]
        
        # Get base species bonuses
        bonuses = species_info.get("ability_bonuses", {}).copy()
        
        # Apply subrace bonuses if applicable
        if subrace:
            subrace_key = subrace.lower().replace(" ", "_")
            subraces = species_info.get("subraces", {})
            
            if subrace_key in subraces:
                subrace_info = subraces[subrace_key]
                
                # Add subrace ability bonuses
                for ability, bonus in subrace_info.get("ability_bonuses", {}).items():
                    if ability in bonuses:
                        bonuses[ability] += bonus
                    else:
                        bonuses[ability] = bonus
        
        return bonuses