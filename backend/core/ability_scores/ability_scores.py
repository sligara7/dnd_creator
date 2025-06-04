import random
import math
from typing import Dict, List, Tuple, Optional, Union, Any
from enum import Enum
import json

from backend.core.ability_scores.abstract_ability_scores import AbstractAbilityScores

from backend.core.ability_scores.llm_ability_advisor import LLMAbilityAdvisor

class AbilityScore(Enum):
    """Enumeration of D&D ability scores with their abbreviations"""
    STRENGTH = "STR"
    DEXTERITY = "DEX"
    CONSTITUTION = "CON"
    INTELLIGENCE = "INT"
    WISDOM = "WIS"
    CHARISMA = "CHA"

class AbilityScores(AbstractAbilityScores):
    """Implementation of the ability score system for D&D 2024 rules"""
    
    # Standard array of ability scores per D&D rules
    STANDARD_ARRAY = [15, 14, 13, 12, 10, 8]
    
    # Point buy costs for ability scores
    POINT_BUY_COSTS = {
        8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 13: 5, 
        14: 7, 15: 9, 16: 11, 17: 14, 18: 18
    }
    
    # Maximum points for point buy (standard is 27)
    POINT_BUY_MAX = 27
    
    def __init__(self):
        """Initialize the ability score manager"""
        # Default minimum and maximum scores
        self.min_score = 3
        self.max_score = 20
        
        # Maximum racial bonus (typically +2)
        self.max_racial_bonus = 2
        
    def calculate_modifier(self, score: int, include_narrative_context: bool = False) -> Union[int, Tuple[int, str]]:
        """
        Calculate the modifier for a given ability score.
        
        Args:
            score: The ability score value
            include_narrative_context: Whether to include narrative description
            
        Returns:
            int or tuple: The modifier, with optional narrative context
        """
        modifier = math.floor((score - 10) / 2)
        
        if not include_narrative_context:
            return modifier
        
        # Provide narrative context based on modifier
        context = ""
        if modifier <= -5:
            context = "Critically deficient, severely impaired functioning in this area"
        elif modifier == -4:
            context = "Extremely poor capability, major disadvantage in related tasks"
        elif modifier == -3:
            context = "Very weak capability, struggles significantly with related activities"
        elif modifier == -2:
            context = "Notably below average, clear disadvantage in this area"
        elif modifier == -1:
            context = "Slightly below average capability"
        elif modifier == 0:
            context = "Average human capability"
        elif modifier == 1:
            context = "Slightly above average capability"
        elif modifier == 2:
            context = "Notably above average, trained or naturally gifted"
        elif modifier == 3:
            context = "Exceptional capability, professional-level talent"
        elif modifier == 4:
            context = "Remarkable ability, among the best in a region"
        elif modifier >= 5:
            context = "Legendary capability, among the best in the world"
            
        return (modifier, context)
    
    def get_point_buy_cost(self, score: int, character_concept: Optional[str] = None) -> Union[int, Dict[str, Any]]:
        """
        Get the cost of a score in point-buy system.
        
        Args:
            score: The ability score value
            character_concept: Optional character concept for distribution suggestions
            
        Returns:
            int or dict: Point cost or distribution suggestion
        """
        # Base functionality: return the point cost
        if score not in self.POINT_BUY_COSTS:
            return None
        
        cost = self.POINT_BUY_COSTS[score]
        
        if not character_concept:
            return cost
        
        # For LLM integration - this is a placeholder that would be replaced by actual LLM call
        # Would provide tailored point-buy distributions based on character concept
        concept_suggestions = {
            "point_cost": cost,
            "concept_analysis": f"Analyzing concept: {character_concept}",
            "suggested_distribution": self._generate_concept_distribution(character_concept)
        }
        
        return concept_suggestions
    
    def _generate_concept_distribution(self, concept: str) -> Dict[str, Any]:
        """
        Generate ability score distribution based on character concept.
        This would normally use LLM but uses a simple rule-based system as placeholder.
        
        Args:
            concept: Character concept description
            
        Returns:
            dict: Suggested ability score distribution
        """
        # This is a placeholder implementation
        # In the real implementation, this would call the LLM
        concept_lower = concept.lower()
        
        # Simple keyword matching for demonstration
        if "wizard" in concept_lower or "smart" in concept_lower or "intelligent" in concept_lower:
            return {
                "STR": 8, "DEX": 14, "CON": 14, "INT": 15, "WIS": 12, "CHA": 10,
                "explanation": "Focused on Intelligence for spellcasting with good Dexterity and Constitution for survival"
            }
        elif "fighter" in concept_lower or "strong" in concept_lower or "warrior" in concept_lower:
            return {
                "STR": 15, "DEX": 14, "CON": 14, "INT": 8, "WIS": 12, "CHA": 10,
                "explanation": "Prioritizing physical attributes with Strength for melee combat"
            }
        else:
            return {
                "STR": 10, "DEX": 14, "CON": 14, "INT": 12, "WIS": 13, "CHA": 10,
                "explanation": "Balanced distribution favoring Dexterity and Constitution for survivability"
            }
    
    def validate_ability_scores(self, scores_dict: Dict[str, int], 
                               include_playstyle_analysis: bool = False) -> Union[bool, Dict[str, Any]]:
        """
        Validate ability scores against rules.
        
        Args:
            scores_dict: Dictionary of ability scores
            include_playstyle_analysis: Whether to include playstyle analysis
            
        Returns:
            bool or dict: Validation result, with optional analysis
        """
        # Check if all required abilities are present
        required_abilities = [ability.name.lower() for ability in AbilityScore]
        for ability in required_abilities:
            if ability not in scores_dict:
                return False
        
        # Check if scores are within allowed range
        for ability, score in scores_dict.items():
            if score < self.min_score or score > self.max_score:
                return False
        
        # If no analysis requested, return simple validation result
        if not include_playstyle_analysis:
            return True
            
        # Provide playstyle analysis based on scores
        analysis = {
            "valid": True,
            "strengths": [],
            "weaknesses": [],
            "playstyle_suggestions": []
        }
        
        # Identify strengths (high scores)
        for ability, score in scores_dict.items():
            modifier = self.calculate_modifier(score)
            if modifier >= 3:
                analysis["strengths"].append(f"Exceptional {ability.capitalize()} ({score})")
            elif modifier >= 2:
                analysis["strengths"].append(f"Strong {ability.capitalize()} ({score})")
        
        # Identify weaknesses (low scores)
        for ability, score in scores_dict.items():
            modifier = self.calculate_modifier(score)
            if modifier <= -2:
                analysis["weaknesses"].append(f"Very weak {ability.capitalize()} ({score})")
            elif modifier <= -1:
                analysis["weaknesses"].append(f"Below average {ability.capitalize()} ({score})")
        
        # Generate playstyle suggestions
        # This would be more sophisticated with LLM integration
        if scores_dict["strength"] > scores_dict["dexterity"]:
            analysis["playstyle_suggestions"].append("Consider melee combat approaches using Strength-based weapons")
        else:
            analysis["playstyle_suggestions"].append("Favor finesse weapons and ranged attacks leveraging your Dexterity")
            
        if scores_dict["intelligence"] > scores_dict["wisdom"] and scores_dict["intelligence"] > scores_dict["charisma"]:
            analysis["playstyle_suggestions"].append("Seek knowledge-based solutions and rely on analytical thinking")
        elif scores_dict["wisdom"] > scores_dict["intelligence"] and scores_dict["wisdom"] > scores_dict["charisma"]:
            analysis["playstyle_suggestions"].append("Trust your instincts and intuition in decision making")
        elif scores_dict["charisma"] > scores_dict["intelligence"] and scores_dict["charisma"] > scores_dict["wisdom"]:
            analysis["playstyle_suggestions"].append("Lead through force of personality and social interactions")
        
        return analysis
    
    def generate_standard_array(self, character_class: Optional[str] = None, 
                                playstyle: Optional[str] = None) -> Union[List[int], Dict[str, Any]]:
        """
        Return the standard ability score array.
        
        Args:
            character_class: Optional character class for optimal placements
            playstyle: Optional character playstyle description
            
        Returns:
            list or dict: Standard array or optimized distribution
        """
        if not character_class and not playstyle:
            return self.STANDARD_ARRAY
        
        # Provide optimized distribution for the class and playstyle
        # This would use LLM in the real implementation
        suggested_assignment = {
            "array": self.STANDARD_ARRAY,
            "suggested_assignment": self._suggest_array_assignment(character_class, playstyle)
        }
        
        return suggested_assignment
    
    def _suggest_array_assignment(self, character_class: Optional[str], 
                               playstyle: Optional[str]) -> Dict[str, Any]:
        """
        Suggest optimal attribute placements based on class and character concept.
        This would normally use LLM but uses a simple rule-based system as placeholder.
        
        Args:
            character_class: Character class name
            playstyle: Character playstyle description
            
        Returns:
            dict: Suggested ability score assignment
        """
        # Simple rule-based implementation as placeholder
        # In real implementation, this would call the LLM
        
        standard_array = self.STANDARD_ARRAY.copy()
        
        if character_class and character_class.lower() == "fighter":
            if playstyle and "ranged" in playstyle.lower():
                return {
                    "STR": standard_array[3],  # 12
                    "DEX": standard_array[0],  # 15
                    "CON": standard_array[1],  # 14
                    "INT": standard_array[4],  # 10
                    "WIS": standard_array[2],  # 13
                    "CHA": standard_array[5],  # 8
                    "explanation": "Prioritizing Dexterity for ranged attacks with good Constitution for durability"
                }
            else:
                return {
                    "STR": standard_array[0],  # 15
                    "DEX": standard_array[2],  # 13
                    "CON": standard_array[1],  # 14
                    "INT": standard_array[4],  # 10
                    "WIS": standard_array[3],  # 12
                    "CHA": standard_array[5],  # 8
                    "explanation": "Prioritizing Strength for melee combat with good Constitution for durability"
                }
        
        elif character_class and character_class.lower() == "wizard":
            return {
                "STR": standard_array[5],  # 8
                "DEX": standard_array[2],  # 13
                "CON": standard_array[3],  # 12
                "INT": standard_array[0],  # 15
                "WIS": standard_array[1],  # 14
                "CHA": standard_array[4],  # 10
                "explanation": "Maximizing Intelligence for spellcasting with good Wisdom for perception"
            }
        
        # Default balanced assignment
        return {
            "STR": standard_array[2],  # 13
            "DEX": standard_array[1],  # 14
            "CON": standard_array[3],  # 12
            "INT": standard_array[4],  # 10
            "WIS": standard_array[0],  # 15
            "CHA": standard_array[5],  # 8
            "explanation": "Balanced assignment favoring Wisdom and Dexterity"
        }
    
    def generate_random_scores(self, method: str = "4d6_drop_lowest", 
                              suggest_concepts: bool = False) -> Union[List[int], Dict[str, Any]]:
        """
        Generate random ability scores.
        
        Args:
            method: Method to use ("4d6_drop_lowest", "3d6", etc.)
            suggest_concepts: Whether to suggest character concepts based on rolls
            
        Returns:
            list or dict: Random scores, with optional concept suggestions
        """
        scores = []
        
        if method == "4d6_drop_lowest":
            for _ in range(6):
                # Roll 4d6 and drop the lowest die
                rolls = [random.randint(1, 6) for _ in range(4)]
                rolls.remove(min(rolls))
                scores.append(sum(rolls))
        elif method == "3d6":
            for _ in range(6):
                # Standard 3d6
                scores.append(sum(random.randint(1, 6) for _ in range(3)))
        else:
            # Default to 4d6 drop lowest
            for _ in range(6):
                rolls = [random.randint(1, 6) for _ in range(4)]
                rolls.remove(min(rolls))
                scores.append(sum(rolls))
        
        # Sort in descending order
        scores.sort(reverse=True)
        
        if not suggest_concepts:
            return scores
        
        # Generate character concepts based on the scores
        # This would use LLM in the real implementation
        concepts = {
            "scores": scores,
            "suggested_concepts": self._generate_concepts_for_scores(scores)
        }
        
        return concepts
    
    def _generate_concepts_for_scores(self, scores: List[int]) -> List[Dict[str, Any]]:
        """
        Generate character concepts that fit random rolls.
        This would normally use LLM but uses a simple rule-based system as placeholder.
        
        Args:
            scores: List of random ability scores
            
        Returns:
            list: Suggested character concepts
        """
        # Simple rules-based implementation that would be replaced by LLM
        concepts = []
        
        # Sort scores for analysis but keep original order
        sorted_scores = sorted(scores, reverse=True)
        
        # Check for exceptional stats
        if sorted_scores[0] >= 16 and sorted_scores[1] >= 14:
            concepts.append({
                "concept": "Gifted Prodigy",
                "description": "A naturally talented individual with exceptional potential in multiple areas",
                "recommended_class": "Any"
            })
        
        # Check for balanced scores
        if all(score >= 10 for score in sorted_scores):
            concepts.append({
                "concept": "Well-Rounded Adventurer",
                "description": "Someone with no real weaknesses, capable in many different situations",
                "recommended_class": "Bard or Ranger"
            })
        
        # Check for very low scores (potential for interesting roleplay)
        if min(sorted_scores) <= 7:
            concepts.append({
                "concept": "Flawed Hero",
                "description": "A character with a significant weakness that must be overcome",
                "recommended_class": "Any, focus on classes that don't rely on the low ability"
            })
        
        # If no specific patterns detected
        if not concepts:
            concepts.append({
                "concept": "Aspiring Adventurer",
                "description": "A standard adventurer looking to make their mark on the world",
                "recommended_class": "Consider class that matches your highest score"
            })
            
        return concepts
    
    def apply_species_bonuses(self, scores_dict: Dict[str, int], species_bonuses: Dict[str, int],
                             include_narrative_elements: bool = False) -> Union[Dict[str, int], Dict[str, Any]]:
        """
        Apply species bonuses to scores.
        
        Args:
            scores_dict: Dictionary of base ability scores
            species_bonuses: Dictionary of bonuses by ability
            include_narrative_elements: Whether to include narrative explanations
            
        Returns:
            dict: Updated scores with bonuses applied, with optional narrative elements
        """
        # Create a copy to avoid modifying the original
        updated_scores = scores_dict.copy()
        
        # Apply bonuses
        for ability, bonus in species_bonuses.items():
            ability_lower = ability.lower()
            if ability_lower in updated_scores:
                updated_scores[ability_lower] += bonus
                # Ensure we don't exceed maximum score
                updated_scores[ability_lower] = min(updated_scores[ability_lower], self.max_score)
        
        if not include_narrative_elements:
            return updated_scores
        
        # Generate narrative elements for the species bonuses
        # This would use LLM in the real implementation
        narrative = {
            "updated_scores": updated_scores,
            "narrative_elements": self._generate_species_narrative(scores_dict, species_bonuses)
        }
        
        return narrative
    
    def _generate_species_narrative(self, scores_dict: Dict[str, int], 
                                  species_bonuses: Dict[str, int]) -> Dict[str, str]:
        """
        Generate narrative explanations for species traits.
        This would normally use LLM but uses a simple rule-based system as placeholder.
        
        Args:
            scores_dict: Original ability scores
            species_bonuses: Species ability bonuses
            
        Returns:
            dict: Narrative explanations for bonuses
        """
        # This is a placeholder that would be replaced by LLM-generated content
        narratives = {}
        
        for ability, bonus in species_bonuses.items():
            ability_lower = ability.lower()
            if ability_lower == "strength" and bonus > 0:
                narratives[ability_lower] = f"Your increased Strength (+{bonus}) manifests as naturally developed muscles and a powerful physique."
            elif ability_lower == "dexterity" and bonus > 0:
                narratives[ability_lower] = f"Your enhanced Dexterity (+{bonus}) gives you naturally quick reflexes and graceful movement."
            elif ability_lower == "constitution" and bonus > 0:
                narratives[ability_lower] = f"Your Constitution bonus (+{bonus}) reflects a hardy nature and exceptional endurance."
            elif ability_lower == "intelligence" and bonus > 0:
                narratives[ability_lower] = f"Your Intelligence increase (+{bonus}) represents natural analytical thinking and quick learning."
            elif ability_lower == "wisdom" and bonus > 0:
                narratives[ability_lower] = f"Your improved Wisdom (+{bonus}) manifests as heightened awareness and intuition."
            elif ability_lower == "charisma" and bonus > 0:
                narratives[ability_lower] = f"Your Charisma bonus (+{bonus}) reflects a naturally compelling presence and force of personality."
        
        return narratives

    def get_ability_score_descriptions(self, level: str = "basic") -> Dict[str, str]:
        """
        Get descriptions of what each ability score represents.
        
        Args:
            level: Detail level ("basic", "detailed", "gameplay")
            
        Returns:
            dict: Descriptions of ability scores
        """
        if level == "basic":
            return {
                "strength": "Physical power and carrying capacity",
                "dexterity": "Agility, reflexes, and balance",
                "constitution": "Endurance, stamina, and vitality",
                "intelligence": "Memory, reasoning, and learning capacity",
                "wisdom": "Awareness, intuition, and insight",
                "charisma": "Force of personality and social influence"
            }
        elif level == "detailed":
            return {
                "strength": "Measures physical power, carrying capacity, and effectiveness in melee combat. Affects your ability to lift, push, break objects, and deal damage with strength-based weapons.",
                "dexterity": "Represents agility, reflexes, balance, and coordination. Affects your armor class, initiative, certain weapon attacks, and many physical skills.",
                "constitution": "Determines endurance, stamina, health, and vital force. Affects hit points, resistance to poison, and ability to endure physical stress.",
                "intelligence": "Measures reasoning, memory, learning, and analytical thinking. Important for wizards and artificers, affects knowledge skills and languages known.",
                "wisdom": "Represents awareness, intuition, insight, and perceptiveness. Important for clerics, druids, and rangers, affects perception and resistance to mental effects.",
                "charisma": "Measures force of personality, persuasiveness, leadership, and confidence. Important for bards, paladins, sorcerers, and warlocks, affects social interactions."
            }
        elif level == "gameplay":
            return {
                "strength": "Used for: melee attack and damage rolls with non-finesse weapons, athletic checks like climbing and jumping, carrying capacity, breaking down doors, and grappling opponents.",
                "dexterity": "Used for: armor class calculation, initiative rolls, ranged attack rolls, melee attacks with finesse weapons, stealth, acrobatics, sleight of hand, and many saving throws against area effects.",
                "constitution": "Used for: hit point calculations, concentration checks for spellcasting, resisting poison and disease, enduring extreme environments, and saving throws against physical effects.",
                "intelligence": "Used for: wizard and artificer spellcasting, investigation checks, knowledge skills (arcana, history, nature, religion), language capabilities, and puzzle solving.",
                "wisdom": "Used for: cleric, druid, and ranger spellcasting, perception checks, insight into others' motives, survival skills, medicine, and saving throws against many magical effects.",
                "charisma": "Used for: bard, paladin, sorcerer, and warlock spellcasting, social interaction skills (deception, intimidation, performance, persuasion), and resisting certain magical effects."
            }
        else:
            return self.get_ability_score_descriptions("basic")

    def generate_ability_score_quirks(self, scores_dict: Dict[str, int]) -> Dict[str, str]:
        """
        Generate character quirks based on extremely high or low ability scores.
        
        Args:
            scores_dict: Dictionary of ability scores
            
        Returns:
            dict: Character quirks for notable ability scores
        """
        quirks = {}
        
        for ability, score in scores_dict.items():
            if score >= 18:
                if ability == "strength":
                    quirks[ability] = "Unconsciously breaks fragile objects when agitated; prefers to stand rather than sit on flimsy furniture"
                elif ability == "dexterity":
                    quirks[ability] = "Habitually performs small feats of manual dexterity like coin rolls across knuckles; rarely remains still"
                elif ability == "constitution":
                    quirks[ability] = "Has an unusual tolerance for extreme temperatures; can eat almost anything without ill effect"
                elif ability == "intelligence":
                    quirks[ability] = "Mentally calculates distances and measurements automatically; frequently references obscure facts"
                elif ability == "wisdom":
                    quirks[ability] = "Often knows what others will say before they speak; notices subtle environmental changes others miss"
                elif ability == "charisma":
                    quirks[ability] = "Strangers often divulge personal secrets without prompting; animals and children gravitate toward them"
            elif score <= 6:
                if ability == "strength":
                    quirks[ability] = "Struggles with heavy backpacks and often asks for help with physical tasks; avoids heavy objects"
                elif ability == "dexterity":
                    quirks[ability] = "Frequently knocks over drinks or bumps into objects; tends to wear simple clothing without complex fasteners"
                elif ability == "constitution":
                    quirks[ability] = "Carries remedies for various ailments; often mentions specific foods or environments that cause discomfort"
                elif ability == "intelligence":
                    quirks[ability] = "Takes statements very literally; maintains simple routines and becomes confused when they change"
                elif ability == "wisdom":
                    quirks[ability] = "Easily distracted by trivial things; often misreads others' intentions and social cues"
                elif ability == "charisma":
                    quirks[ability] = "Speaks in monotone or with unusual cadence; unintentionally says inappropriate things in social situations"
                    
        return quirks


# Example usage
# if __name__ == "__main__":
#     # Create instances
#     ability_scores = AbilityScores()
#     llm_advisor = LLMAbilityAdvisor()
    
#     # Example ability scores
#     sample_scores = {"strength": 14, "dexterity": 16, "constitution": 12, 
#                      "intelligence": 10, "wisdom": 8, "charisma": 15}
    
#     # Calculate modifier with narrative context
#     str_mod, context = ability_scores.calculate_modifier(14, include_narrative_context=True)
#     print(f"Strength 14 modifier: {str_mod} - {context}")
    
#     # Validate scores with playstyle analysis
#     analysis = ability_scores.validate_ability_scores(sample_scores, include_playstyle_analysis=True)
#     if isinstance(analysis, dict):
#         print(f"Strengths: {analysis['strengths']}")
#         print(f"Weaknesses: {analysis['weaknesses']}")
#         print(f"Suggestions: {analysis['playstyle_suggestions']}")
    
#     # Generate character quirks
#     quirks = ability_scores.generate_ability_score_quirks(sample_scores)
#     for ability, quirk in quirks.items():
#         print(f"{ability.capitalize()} quirk: {quirk}")
    
#     # LLM advisor example
#     gameplay_implications = llm_advisor.explain_gameplay_implications("dexterity", 16)
#     print(gameplay_implications)