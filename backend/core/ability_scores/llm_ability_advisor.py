
from backend.core.services.ollama_service import OllamaService

class LLMAbilityAdvisor:
    def __init__(self, llm_service=None):
        if llm_service is None:
            self.llm_service = OllamaService()
        else:
            self.llm_service = llm_service
        self.ability_scores = AbilityScores()

    def _create_prompt(self, task, context):
        """
        Create a well-structured prompt for the LLM.
        
        Args:
            task: The specific task (e.g., "explain ability score")
            context: Relevant context information
            
        Returns:
            str: Formatted prompt
        """
        system_context = "You are a D&D 5e (2024 rules) character creation assistant."
        instructions = f"Based on the following information, {task}. Keep your answer concise and focused on D&D rules."
        
        prompt = f"{system_context}\n\n{instructions}\n\nInformation: {context}"
        return prompt
        
    def explain_modifier_narrative(self, score: int, ability: str) -> str:
        """
        Provide narrative description of what a modifier means in practical terms.
        
        Args:
            score: Ability score value
            ability: Which ability (strength, dexterity, etc.)
            
        Returns:
            str: Narrative description
        """
        modifier = self.ability_scores.calculate_modifier(score)
        
        prompt = self._create_prompt(
            f"explain what a {ability} score of {score} (modifier {modifier:+d}) means in narrative terms",
            f"The character has a {ability.capitalize()} score of {score}, giving them a modifier of {modifier:+d}. "
            f"Provide a practical explanation of what this means for the character in everyday situations and during adventures."
        )
        
        try:
            response = self.llm_service.generate(prompt)
            if response and len(response) > 20:  # Basic validation that we got a real response
                return response
        except Exception as e:
            print(f"Error getting LLM response for modifier narrative: {e}")
        
        # Fallback if LLM fails
        modifier, context = self.ability_scores.calculate_modifier(score, include_narrative_context=True)
        ability_desc = self.ability_scores.get_ability_score_descriptions("detailed").get(ability.lower(), "")
        return f"A {ability.capitalize()} score of {score} gives a {modifier:+d} modifier. {context}. {ability_desc}"
    
    def suggest_point_buy_distribution(self, character_concept: str) -> Dict[str, Any]:
        """
        Suggest optimal point-buy distribution based on character concept.
        
        Args:
            character_concept: Description of character concept
            
        Returns:
            dict: Suggested ability score distribution
        """
        prompt = self._create_prompt(
            "suggest an optimal point-buy ability score distribution",
            f"Character concept: {character_concept}\n"
            f"Point-buy rules: Scores range from 8-15 before racial bonuses. "
            f"Costs: 8:0, 9:1, 10:2, 11:3, 12:4, 13:5, 14:7, 15:9 points. "
            f"Maximum 27 points total. Return a JSON object with STR, DEX, CON, INT, WIS, CHA scores and an explanation."
        )
        
        try:
            response = self.llm_service.generate(prompt)
            
            # Try to parse JSON from the response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                distribution = json.loads(json_match.group(0))
                
                # Add explanation if not present
                if "explanation" not in distribution:
                    distribution["explanation"] = response.replace(json_match.group(0), "").strip()
                    
                return distribution
        except Exception as e:
            print(f"Error parsing LLM response for point buy: {e}")
        
        # Fallback to built-in method if LLM fails
        return self.ability_scores._generate_concept_distribution(character_concept)
    
    def analyze_ability_scores(self, scores_dict: Dict[str, int]) -> Dict[str, Any]:
        """
        Analyze strengths and weaknesses of an ability score distribution.
        
        Args:
            scores_dict: Dictionary of ability scores
            
        Returns:
            dict: Analysis of the distribution
        """
        # Format scores for prompt
        scores_str = ", ".join(f"{ability.capitalize()}: {score}" for ability, score in scores_dict.items())
        
        prompt = self._create_prompt(
            "analyze these ability scores and suggest playstyles",
            f"Ability scores: {scores_str}\n\n"
            f"Identify strengths and weaknesses, and suggest playstyle approaches that would work well with this distribution. "
            f"Return results in JSON format with keys for 'strengths', 'weaknesses', and 'playstyle_suggestions'."
        )
        
        try:
            response = self.llm_service.generate(prompt)
            
            # Try to parse JSON from the response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group(0))
                analysis["valid"] = True
                
                # Add character quirks based on extreme scores
                analysis["quirks"] = self.generate_character_quirks(scores_dict)
                
                return analysis
        except Exception as e:
            print(f"Error parsing LLM response for ability score analysis: {e}")
        
        # Fallback to built-in method if LLM fails
        analysis = self.ability_scores.validate_ability_scores(scores_dict, include_playstyle_analysis=True)
        analysis["quirks"] = self.ability_scores.generate_ability_score_quirks(scores_dict)
        return analysis
    
    def generate_character_quirks(self, scores_dict: Dict[str, int]) -> Dict[str, str]:
        """
        Generate character quirks based on extremely high or low ability scores using LLM.
        
        Args:
            scores_dict: Dictionary of ability scores
            
        Returns:
            dict: Character quirks for notable ability scores
        """
        quirks = {}
        
        # Only process extreme scores to avoid unnecessary LLM calls
        extreme_scores = {
            ability: score for ability, score in scores_dict.items() 
            if score >= 18 or score <= 6
        }
        
        if not extreme_scores:
            return quirks
            
        # Format scores for prompt
        scores_str = ", ".join(f"{ability.capitalize()}: {score}" for ability, score in extreme_scores.items())
        
        prompt = self._create_prompt(
            "generate character quirks for these extreme ability scores",
            f"Character has these notable ability scores: {scores_str}\n\n"
            f"Generate unique and interesting character quirks or mannerisms that would result from "
            f"these extremely high or low ability scores. Return as JSON with ability names as keys and quirk descriptions as values."
        )
        
        try:
            response = self.llm_service.generate(prompt)
            
            # Try to parse JSON from the response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
        except Exception as e:
            print(f"Error parsing LLM response for quirks: {e}")
        
        # Fallback to built-in method if LLM fails
        return self.ability_scores.generate_ability_score_quirks(scores_dict)
    
    def suggest_standard_array_placement(self, character_class: str, playstyle: str) -> Dict[str, Any]:
        """
        Suggest optimal standard array placement for a character concept.
        
        Args:
            character_class: Character's class
            playstyle: Description of desired playstyle
            
        Returns:
            dict: Suggested ability score placement
        """
        standard_array = self.ability_scores.STANDARD_ARRAY
        array_str = ", ".join(str(score) for score in standard_array)
        
        prompt = self._create_prompt(
            "suggest optimal ability score placement using the standard array",
            f"Character class: {character_class}\nPlaystyle: {playstyle}\n"
            f"Standard array values: {array_str} (these six values must be assigned to STR, DEX, CON, INT, WIS, CHA)\n\n"
            f"Recommend the optimal placement of these six values to the six ability scores. "
            f"Return as JSON with STR, DEX, CON, INT, WIS, CHA as keys, the assigned values, and an explanation of your reasoning."
        )
        
        try:
            response = self.llm_service.generate(prompt)
            
            # Try to parse JSON from the response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
        except Exception as e:
            print(f"Error parsing LLM response for standard array placement: {e}")
        
        # Fallback to built-in method if LLM fails
        return self.ability_scores._suggest_array_assignment(character_class, playstyle)
    
    def suggest_concepts_for_rolls(self, scores: List[int]) -> List[Dict[str, Any]]:
        """
        Suggest character concepts based on random ability scores.
        
        Args:
            scores: List of randomly rolled scores
            
        Returns:
            list: Suggested character concepts
        """
        scores_str = ", ".join(str(score) for score in sorted(scores, reverse=True))
        
        prompt = self._create_prompt(
            "suggest character concepts based on these rolled ability scores",
            f"Randomly rolled ability scores: {scores_str}\n\n"
            f"Suggest 2-3 character concepts that would work well with these scores. For each concept, provide: "
            f"1) A concept name/title, 2) A brief description, and 3) Recommended classes. "
            f"Return as JSON array where each object has 'concept', 'description', and 'recommended_class' keys."
        )
        
        try:
            response = self.llm_service.generate(prompt)
            
            # Try to parse JSON from the response
            import re
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
        except Exception as e:
            print(f"Error parsing LLM response for concept suggestions: {e}")
        
        # Fallback to built-in method if LLM fails
        return self.ability_scores._generate_concepts_for_scores(scores)
    
    def explain_species_traits(self, species: str, bonuses: Dict[str, int]) -> Dict[str, str]:
        """
        Provide narrative explanations for species ability bonuses.
        
        Args:
            species: Character's species (race)
            bonuses: Ability score bonuses
            
        Returns:
            dict: Narrative explanations
        """
        # Format bonuses for the prompt
        bonus_str = ", ".join(f"{ability}: +{bonus}" for ability, bonus in bonuses.items())
        
        prompt = self._create_prompt(
            "explain how species traits manifest as ability score bonuses",
            f"Species: {species}\nAbility score bonuses: {bonus_str}\n\n"
            f"Explain how the natural traits, physiology, and culture of this species manifest as these specific ability score bonuses. "
            f"Be descriptive but concise. Return as JSON with ability names as keys and narrative explanations as values."
        )
        
        try:
            response = self.llm_service.generate(prompt)
            
            # Try to parse JSON from the response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
        except Exception as e:
            print(f"Error parsing LLM response for species traits: {e}")
        
        # Fallback to simple templated responses if LLM fails
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
        """
        Explain gameplay implications of an ability score for new players.
        
        Args:
            ability: The ability to explain
            score: The score value
            
        Returns:
            str: Gameplay explanation
        """
        modifier = self.ability_scores.calculate_modifier(score)
        
        prompt = self._create_prompt(
            "explain gameplay implications of this ability score",
            f"Ability: {ability}\nScore: {score}\nModifier: {modifier:+d}\n\n"
            f"Explain what this ability score and modifier mean in gameplay terms. Include: "
            f"1) What this ability affects in the game, 2) What skills are based on it, "
            f"3) Practical advice for a player with this score, and 4) When this ability will be most important."
        )
        
        try:
            response = self.llm_service.generate(prompt)
            if response and len(response) > 50:  # Basic validation that we got a real response
                return response
        except Exception as e:
            print(f"Error getting LLM response for gameplay implications: {e}")
        
        # Fallback to structured response if LLM fails
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
        """
        Generate complete character concept with suggested ability scores based on preferences.
        
        Args:
            preferences: Dictionary of character preferences
            
        Returns:
            dict: Complete character concept
        """
        # Format preferences into a string
        pref_str = "\n".join([f"- {key}: {value}" for key, value in preferences.items()])
        
        prompt = self._create_prompt(
            "generate a D&D character concept",
            f"Player preferences:\n{pref_str}\n\n"
            f"Generate a character concept including: concept_name, description, "
            f"suggested_ability_scores, personality_traits, background, and class_suggestions. "
            f"Return as valid JSON."
        )
        
        try:
            response = self.llm_service.generate(prompt)
            
            # Try to parse JSON from response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
        except Exception as e:
            print(f"Error with LLM response: {e}")
        
        # Fallback to hardcoded response if LLM fails
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
