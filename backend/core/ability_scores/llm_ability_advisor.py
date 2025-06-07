from typing import Dict, List, Any, Optional
import json
import logging

from backend.core.advisor.base_advisor import BaseAdvisor
from backend.core.ability_scores.ability_scores import AbilityScores

logger = logging.getLogger(__name__)

class LLMAbilityAdvisor(BaseAdvisor):
    """
    LLM-powered advisor for ability scores, providing recommendations,
    explanations and character concept generation based on ability scores.
    """

    def __init__(self, llm_service=None, cache_enabled=True):
        """Initialize the ability scores advisor with the LLM service."""
        system_prompt = (
            "You are a D&D 5e (2024 rules) ability scores expert. "
            "Provide guidance on ability scores, modifiers, and their implications for characters."
        )
        super().__init__(llm_service, system_prompt, cache_enabled)
        self.ability_scores = AbilityScores()

    def explain_modifier_narrative(self, score: int, ability: str) -> str:
        """Provide narrative description of what a modifier means in practical terms."""
        modifier = self.ability_scores.calculate_modifier(score)
        
        prompt = self._format_prompt(
            f"Explain {ability} score of {score} (modifier {modifier:+d})",
            f"The character has a {ability.capitalize()} score of {score}, giving them a modifier of {modifier:+d}.",
            [
                "Practical explanation of what this means in everyday situations",
                "How this affects the character during adventures",
                "Physical or mental manifestation of this ability score",
                "Common activities where this score is relevant"
            ]
        )
        
        response = self._get_llm_response(
            "modifier_narrative", 
            prompt, 
            {"ability": ability, "score": score}
        )
        
        # Simple validation that we got a meaningful response
        if response and len(response) > 20:
            return response
            
        # Fallback if response is insufficient
        modifier, context = self.ability_scores.calculate_modifier(score, include_narrative_context=True)
        ability_desc = self.ability_scores.get_ability_score_descriptions("detailed").get(ability.lower(), "")
        return f"A {ability.capitalize()} score of {score} gives a {modifier:+d} modifier. {context}. {ability_desc}"

    def suggest_point_buy_distribution(self, character_concept: str) -> Dict[str, Any]:
        """Suggest optimal point-buy distribution based on character concept."""
        prompt = self._format_prompt(
            "Point-buy ability score distribution",
            f"Character concept: {character_concept}\n\n"
            f"Point-buy rules: Scores range from 8-15 before racial bonuses. "
            f"Costs: 8:0, 9:1, 10:2, 11:3, 12:4, 13:5, 14:7, 15:9 points. "
            f"Maximum 27 points total.",
            [
                "STR, DEX, CON, INT, WIS, CHA scores using point-buy system",
                "Brief explanation of why these scores fit the concept",
                "Total point cost (must equal exactly 27)"
            ]
        )
        
        response = self._get_llm_response(
            "point_buy", 
            prompt, 
            {"concept": character_concept}
        )
        
        # Try to extract JSON from the response
        distribution = self._extract_json(response)
        if distribution and all(key in distribution for key in ["STR", "DEX", "CON", "INT", "WIS", "CHA"]):
            # Add explanation if not present
            if "explanation" not in distribution:
                distribution["explanation"] = "These scores fit your character concept."
            return distribution
        
        # Fallback to built-in method if extraction fails
        logger.warning("Failed to extract valid point-buy distribution from LLM response")
        return self.ability_scores._generate_concept_distribution(character_concept)

    def analyze_ability_scores(self, scores_dict: Dict[str, int]) -> Dict[str, Any]:
        """Analyze strengths and weaknesses of an ability score distribution."""
        # Format scores for prompt
        scores_str = ", ".join(f"{ability.capitalize()}: {score}" for ability, score in scores_dict.items())
        
        prompt = self._format_prompt(
            "Analyze ability scores",
            f"Ability scores: {scores_str}",
            [
                "Strengths based on high scores",
                "Weaknesses based on low scores",
                "Suggested playstyles that leverage these scores",
                "Character class recommendations that match this distribution"
            ]
        )
        
        response = self._get_llm_response(
            "analyze_scores", 
            prompt, 
            scores_dict
        )
        
        analysis = self._extract_json(response)
        if analysis and "strengths" in analysis and "weaknesses" in analysis:
            analysis["valid"] = True
            
            # Add character quirks based on extreme scores
            analysis["quirks"] = self.generate_character_quirks(scores_dict)
            
            return analysis
        
        # Fallback to built-in method if extraction fails
        logger.warning("Failed to extract valid ability score analysis from LLM response")
        analysis = self.ability_scores.validate_ability_scores(scores_dict, include_playstyle_analysis=True)
        analysis["quirks"] = self.ability_scores.generate_ability_score_quirks(scores_dict)
        return analysis

    def generate_character_quirks(self, scores_dict: Dict[str, int]) -> Dict[str, str]:
        """Generate character quirks based on extremely high or low ability scores."""
        # Only process extreme scores to avoid unnecessary LLM calls
        extreme_scores = {
            ability: score for ability, score in scores_dict.items() 
            if score >= 18 or score <= 6
        }
        
        if not extreme_scores:
            return {}
            
        # Format scores for prompt
        scores_str = ", ".join(f"{ability.capitalize()}: {score}" for ability, score in extreme_scores.items())
        
        prompt = self._format_prompt(
            "Generate character quirks",
            f"Character has these notable ability scores: {scores_str}",
            [
                "Unique behavioral traits resulting from these scores",
                "Physical manifestations of these extreme abilities",
                "Roleplay suggestions for these ability score extremes",
                "How these quirks might appear in social interactions"
            ]
        )
        
        response = self._get_llm_response(
            "character_quirks", 
            prompt, 
            extreme_scores
        )
        
        quirks = self._extract_json(response)
        if quirks:
            return quirks
        
        # Fallback to built-in method if extraction fails
        logger.warning("Failed to extract valid character quirks from LLM response")
        return self.ability_scores.generate_ability_score_quirks(scores_dict)

    def suggest_standard_array_placement(self, character_class: str, playstyle: str) -> Dict[str, Any]:
        """Suggest optimal standard array placement for a character concept."""
        standard_array = self.ability_scores.STANDARD_ARRAY
        array_str = ", ".join(str(score) for score in standard_array)
        
        prompt = self._format_prompt(
            "Standard array placement",
            f"Character class: {character_class}\nPlaystyle: {playstyle}\n"
            f"Standard array values: {array_str} (these six values must be assigned to STR, DEX, CON, INT, WIS, CHA)",
            [
                "Optimal assignment of standard array values to ability scores",
                "Explanation of why this arrangement fits the class and playstyle",
                "Primary abilities to focus on for this build"
            ]
        )
        
        response = self._get_llm_response(
            "standard_array", 
            prompt, 
            {"class": character_class, "playstyle": playstyle}
        )
        
        distribution = self._extract_json(response)
        if distribution and all(key in distribution for key in ["STR", "DEX", "CON", "INT", "WIS", "CHA"]):
            return distribution
        
        # Fallback to built-in method if extraction fails
        logger.warning("Failed to extract valid standard array placement from LLM response")
        return self.ability_scores._suggest_array_assignment(character_class, playstyle)

    def suggest_concepts_for_rolls(self, scores: List[int]) -> List[Dict[str, Any]]:
        """Suggest character concepts based on random ability scores."""
        scores_str = ", ".join(str(score) for score in sorted(scores, reverse=True))
        
        prompt = self._format_prompt(
            "Character concepts for rolled scores",
            f"Randomly rolled ability scores: {scores_str}",
            [
                "2-3 character concepts that would work well with these scores",
                "Each concept should include a name/title, description, and recommended classes",
                "How to allocate these scores for each concept"
            ]
        )
        
        response = self._get_llm_response(
            "concepts_for_rolls", 
            prompt, 
            {"scores": scores}
        )
        
        concepts = self._extract_json(response)
        if isinstance(concepts, list) and len(concepts) > 0:
            return concepts
        
        # Fallback to built-in method if extraction fails
        logger.warning("Failed to extract valid concept suggestions from LLM response")
        return self.ability_scores._generate_concepts_for_scores(scores)

    def explain_species_traits(self, species: str, bonuses: Dict[str, int]) -> Dict[str, str]:
        """Provide narrative explanations for species ability bonuses."""
        # Format bonuses for the prompt
        bonus_str = ", ".join(f"{ability}: +{bonus}" for ability, bonus in bonuses.items())
        
        prompt = self._format_prompt(
            f"{species} trait explanations",
            f"Species: {species}\nAbility score bonuses: {bonus_str}",
            [
                "How natural traits manifest as ability score bonuses",
                "Physical or mental characteristics that explain these bonuses",
                "Cultural factors that might influence these traits"
            ]
        )
        
        response = self._get_llm_response(
            "species_traits", 
            prompt, 
            {"species": species, "bonuses": bonuses}
        )
        
        explanations = self._extract_json(response)
        if explanations:
            return explanations
        
        # Fallback to simple templated responses
        logger.warning("Failed to extract valid species trait explanations from LLM response")
        narratives = {}
        for ability, bonus in bonuses.items():
            ability_lower = ability.lower()
            if ability_lower == "strength":
                narratives[ability_lower] = f"{species}s have +{bonus} Strength, reflecting their powerful build and muscular physique."
            elif ability_lower == "dexterity":
                narratives[ability_lower] = f"{species}s have +{bonus} Dexterity due to their naturally quick reflexes and agile movement."
            elif ability_lower == "constitution":
                narratives[ability_lower] = f"{species}s have +{bonus} Constitution, showing their hardy nature and physical resilience."
            elif ability_lower == "intelligence":
                narratives[ability_lower] = f"{species}s have +{bonus} Intelligence, representing their natural aptitude for knowledge and learning."
            elif ability_lower == "wisdom":
                narratives[ability_lower] = f"{species}s have +{bonus} Wisdom, reflecting their intuition and awareness."
            elif ability_lower == "charisma":
                narratives[ability_lower] = f"{species}s have +{bonus} Charisma, manifesting as a natural presence and force of personality."
            
        return narratives

    def explain_gameplay_implications(self, ability: str, score: int) -> str:
        """Explain gameplay implications of an ability score for new players."""
        modifier = self.ability_scores.calculate_modifier(score)
        
        prompt = self._format_prompt(
            f"{ability} gameplay implications",
            f"Ability: {ability}\nScore: {score}\nModifier: {modifier:+d}",
            [
                "What this ability affects in gameplay",
                "Skills based on this ability",
                "Practical advice for a player with this score",
                "When this ability will be most important during adventures"
            ]
        )
        
        response = self._get_llm_response(
            "gameplay_implications", 
            prompt, 
            {"ability": ability, "score": score}
        )
        
        if response and len(response) > 50:
            return response
        
        # Fallback to structured response
        logger.warning("Failed to get meaningful gameplay implications from LLM response")
        gameplay_descriptions = self.ability_scores.get_ability_score_descriptions("gameplay")
        basic_desc = gameplay_descriptions.get(ability.lower(), "No description available.")
        
        # Add modifier-specific advice
        if modifier <= -2:
            advice = f"With a {modifier} modifier, you'll struggle with {ability.lower()}-based activities. Consider avoiding situations that require {ability.lower()} checks when possible."
        elif modifier == -1:
            advice = f"Your {modifier} modifier means you're slightly below average. Be cautious when attempting {ability.lower()}-based actions."
        elif modifier == 0:
            advice = f"With a +0 modifier, you're average in {ability.lower()}. You won't have bonuses or penalties."
        elif modifier <= 2:
            advice = f"Your +{modifier} modifier gives you an edge in {ability.lower()}-based activities. Look for opportunities to use this ability."
        else:
            advice = f"With a +{modifier} modifier, you excel at {ability.lower()}-based tasks. This is a major strength to leverage in gameplay."
            
        return f"{basic_desc}\n\nWith your score of {score} ({modifier:+d}): {advice}"

    def generate_character_concept(self, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Generate complete character concept with suggested ability scores based on preferences."""
        # Format preferences into a string
        pref_str = "\n".join([f"- {key}: {value}" for key, value in preferences.items()])
        
        prompt = self._format_prompt(
            "Generate character concept",
            f"Player preferences:\n{pref_str}",
            [
                "Character concept name/title",
                "Brief character description",
                "Suggested ability scores (STR, DEX, CON, INT, WIS, CHA)",
                "Personality traits",
                "Background suggestion",
                "Class suggestions"
            ]
        )
        
        response = self._get_llm_response(
            "generate_concept", 
            prompt, 
            preferences
        )
        
        concept = self._extract_json(response)
        if concept and "concept_name" in concept and "suggested_ability_scores" in concept:
            return concept
        
        # Fallback to hardcoded response
        logger.warning("Failed to extract valid character concept from LLM response")
        return {
            "concept_name": "The Determined Scholar",
            "description": "A bookish individual who has left their studies to gain practical experience",
            "suggested_ability_scores": {
                "strength": 10, "dexterity": 12, "constitution": 14,
                "intelligence": 15, "wisdom": 13, "charisma": 8
            },
            "personality_traits": [
                "Always has their nose in a book",
                "Takes detailed notes about new discoveries"
            ],
            "background": "Sage or Academic",
            "class_suggestions": ["Wizard", "Artificer", "Knowledge Cleric"]
        }