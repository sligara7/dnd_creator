
from typing import Dict, Any, List
import re
import json

from backend.core.ollama_service import OllamaService

class LLMFeatsAdvisor:
    """
    Service for LLM-assisted feat recommendations and customization.
    
    This class handles all interactions with the LLM service to provide
    enhanced feat recommendations, narrative elements, and customization options.
    """
    
    def __init__(self, llm_service=None):
        """Initialize with optional custom LLM service"""
        self.llm_service = llm_service or OllamaService()
    
    def _create_prompt(self, task, context):
        """
        Create a well-structured prompt for the LLM.
        
        Args:
            task: The specific task (e.g., "recommend feats")
            context: Relevant context information
        
        Returns:
            str: Formatted prompt for the LLM
        """
        system_context = "You are a D&D 5e (2024 rules) character creation expert specializing in feats and character development."
        instructions = f"Based on the following information, {task}. Focus on D&D 5e rules and character development."
        
        prompt = f"{system_context}\n\n{instructions}\n\nInformation: {context}"
        return prompt
    
    def _extract_json(self, response):
        """Extract JSON from LLM response."""
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            
            # Try to extract an array response
            json_array_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_array_match:
                return json.loads(json_array_match.group(0))
        except Exception as e:
            print(f"Error parsing LLM response: {e}")
            return None
    
    def recommend_feats(self, character_data: Dict[str, Any], 
                      character_concept: str = None, 
                      count: int = 3) -> List[Dict[str, Any]]:
        """
        Recommend feats based on character data and concept.
        
        Args:
            character_data: Character attributes and stats
            character_concept: Text description of character concept
            count: Number of recommendations to return
            
        Returns:
            List[Dict[str, Any]]: Recommended feats with reasoning
        """
        # Extract relevant character information
        class_name = character_data.get("class", {}).get("name", "Unknown")
        race = character_data.get("race", {}).get("name", "Unknown")
        background = character_data.get("background", {}).get("name", "Unknown")
        level = character_data.get("level", 1)
        ability_scores = character_data.get("ability_scores", {})
        existing_feats = character_data.get("feats", [])
        
        # Create context for the prompt
        context = f"Character Information:\nClass: {class_name}\nRace: {race}\nBackground: {background}\nLevel: {level}\n"
        context += f"Ability Scores: {json.dumps(ability_scores)}\nExisting Feats: {', '.join(existing_feats)}\n"
        
        if character_concept:
            context += f"Character Concept: {character_concept}\n"
        
        prompt = self._create_prompt(
            f"recommend the top {count} feats for this character",
            context + "\n"
            f"For each recommended feat, provide its name, a brief description, "
            f"and an explanation of why it would be beneficial for this character. "
            f"Consider mechanical synergies, character concept, and roleplaying opportunities. "
            f"Return as a JSON array with 'name', 'description', and 'reason' keys."
        )
        
        try:
            response = self.llm_service.generate(prompt)
            recommendations = self._extract_json(response)
            
            if recommendations:
                return recommendations
        except Exception as e:
            print(f"Error getting feat recommendations: {e}")
        
        # Fallback
        return [{"name": "Alert", "description": "Always on watch", "reason": "Fallback recommendation"}]
    
    def generate_narrative_elements(self, feat_name: str, feat_desc: str, 
                                 character_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate narrative elements for a feat.
        
        Args:
            feat_name: Name of the feat
            feat_desc: Description of the feat
            character_data: Character attributes and stats
            
        Returns:
            Dict[str, str]: Narrative elements for the feat
        """
        class_name = character_data.get("class", {}).get("name", "Unknown")
        background = character_data.get("background", {}).get("name", "Unknown")
        
        prompt = self._create_prompt(
            "create narrative elements for this feat",
            f"Feat: {feat_name}\nDescription: {feat_desc}\n"
            f"Character Class: {class_name}\nBackground: {background}\n\n"
            f"Create narrative elements that describe how this feat manifests in the character's "
            f"abilities, behavior, and fighting style. Include roleplay suggestions and storytelling "
            f"opportunities. Return as JSON with 'manifestation', 'training_story', "
            f"'roleplay_suggestions', and 'character_moments' keys."
        )
        
        try:
            response = self.llm_service.generate(prompt)
            narrative = self._extract_json(response)
            
            if narrative:
                return narrative
        except Exception as e:
            print(f"Error generating narrative elements: {e}")
        
        # Fallback
        return {
            "manifestation": f"The {feat_name} feat manifests as a unique ability in your character.",
            "training_story": "You developed this ability through practice and determination.",
            "roleplay_suggestions": "Consider how this ability affects your character's confidence.",
            "character_moments": "This ability might shine in key dramatic moments."
        }
    
    def suggest_development_path(self, character_data: Dict[str, Any], 
                               future_levels: int = 3) -> Dict[str, Any]:
        """
        Suggest a feat development path for future levels.
        
        Args:
            character_data: Character attributes and stats
            future_levels: Number of levels to plan ahead
            
        Returns:
            Dict[str, Any]: Development path with feat suggestions
        """
        class_name = character_data.get("class", {}).get("name", "Unknown")
        subclass = character_data.get("subclass", "None")
        level = character_data.get("level", 1)
        ability_scores = character_data.get("ability_scores", {})
        existing_feats = character_data.get("feats", [])
        
        prompt = self._create_prompt(
            "suggest a feat development path",
            f"Character Information:\nClass: {class_name}\nSubclass: {subclass}\n"
            f"Current Level: {level}\nPlanning for: {future_levels} levels\n"
            f"Ability Scores: {json.dumps(ability_scores)}\nExisting Feats: {', '.join(existing_feats)}\n\n"
            f"Suggest a development path with feat choices for the next {future_levels} levels. "
            f"For each suggested feat, explain how it builds on previous choices and advances the character concept. "
            f"Return as JSON with a 'path' key containing an array of level recommendations."
        )
        
        try:
            response = self.llm_service.generate(prompt)
            path_data = self._extract_json(response)
            
            if path_data:
                return path_data
        except Exception as e:
            print(f"Error generating development path: {e}")
        
        # Fallback
        return {
            "path": [
                {"level": level + i, "feat": f"Suggested Feat {i}", "reasoning": "Build your character"} 
                for i in range(1, future_levels + 1)
            ]
        }
    
    def suggest_qualification_path(self, character_data: Dict[str, Any], 
                                 feat_name: str, 
                                 prerequisites: Dict[str, Any]) -> Dict[str, Any]:
        """
        Suggest a path to qualify for a feat.
        
        Args:
            character_data: Character attributes and stats
            feat_name: The feat to qualify for
            prerequisites: Feat prerequisites
            
        Returns:
            Dict[str, Any]: Qualification path with suggestions
        """
        class_name = character_data.get("class", {}).get("name", "Unknown")
        level = character_data.get("level", 1)
        ability_scores = character_data.get("ability_scores", {})
        
        prompt = self._create_prompt(
            "suggest a path to qualify for this feat",
            f"Character Information:\nClass: {class_name}\nLevel: {level}\n"
            f"Ability Scores: {json.dumps(ability_scores)}\n"
            f"Feat: {feat_name}\nPrerequisites: {json.dumps(prerequisites)}\n\n"
            f"Suggest the most efficient path for this character to qualify for the {feat_name} feat. "
            f"Consider ability score increases, multiclassing options, or other ways to meet prerequisites. "
            f"Return as JSON with 'steps', 'estimated_levels', and 'alternative_approaches' keys."
        )
        
        try:
            response = self.llm_service.generate(prompt)
            path_data = self._extract_json(response)
            
            if path_data:
                return path_data
        except Exception as e:
            print(f"Error generating qualification path: {e}")
        
        # Fallback
        return {
            "steps": [f"Work toward meeting the prerequisites for {feat_name}"],
            "estimated_levels": 2,
            "alternative_approaches": ["Consider alternative feats that don't have these prerequisites"]
        }
    
    def generate_transition_narrative(self, character_data: Dict[str, Any], 
                                    feat_name: str) -> str:
        """
        Generate a narrative describing how a character gains a new feat.
        
        Args:
            character_data: Character attributes and stats
            feat_name: The feat being gained
            
        Returns:
            str: Narrative text describing the transition
        """
        class_name = character_data.get("class", {}).get("name", "Unknown")
        background = character_data.get("background", {}).get("name", "Unknown")
        
        prompt = self._create_prompt(
            "create a narrative for gaining this feat",
            f"Character Information:\nClass: {class_name}\nBackground: {background}\n"
            f"Feat Being Gained: {feat_name}\n\n"
            f"Create a short narrative describing how this character discovers and develops "
            f"the abilities granted by the {feat_name} feat. This could involve training, "
            f"a dramatic event, a revelation, or a combination of factors. The narrative "
            f"should feel personal to this character's journey."
        )
        
        try:
            response = self.llm_service.generate(prompt)
            
            # Remove any JSON formatting if present
            clean_response = re.sub(r'```.*?```', '', response, flags=re.DOTALL)
            clean_response = re.sub(r'\{.*?\}', '', clean_response, flags=re.DOTALL)
            
            return clean_response.strip()
        except Exception as e:
            print(f"Error generating transition narrative: {e}")
        
        # Fallback
        return f"Through practice and determination, your character develops the abilities granted by the {feat_name} feat."
    
    def create_custom_feat(self, concept: str = None, 
                         character_data: Dict[str, Any] = None,
                         partial_data: Dict[str, Any] = None) -> CustomFeat:
        """
        Create a custom feat based on a concept or partial data.
        
        Args:
            concept: Brief description of the feat concept
            character_data: Character data for context
            partial_data: Partial feat data to complete
            
        Returns:
            CustomFeat: Custom feat instance
        """
        if not concept and not partial_data:
            raise ValueError("Must provide either concept or partial_data")
        
        if partial_data:
            context = f"Partial feat data: {json.dumps(partial_data)}\n\n"
            if character_data:
                context += f"Character class: {character_data.get('class', {}).get('name', 'Unknown')}\n"
                context += f"Character level: {character_data.get('level', 1)}\n\n"
            context += "Create a complete, balanced feat by filling in missing attributes."
            task = "complete this partial feat definition"
        else:
            context = f"Feat concept: {concept}\n\n"
            if character_data:
                context += f"Character class: {character_data.get('class', {}).get('name', 'Unknown')}\n"
                context += f"Character level: {character_data.get('level', 1)}\n\n"
            context += "Create a complete, balanced feat based on this concept."
            task = "create a complete custom feat"
        
        prompt = self._create_prompt(
            task,
            context + "\n\n"
            "Include the following attributes in your JSON response:\n"
            "- name: The feat name\n"
            "- description: Complete description\n"
            "- prerequisites: Object with any prerequisites\n"
            "- benefits: Object with mechanical benefits\n"
            "- category: Feat category\n"
            "- rarity: Feat rarity\n"
            "- narrative_elements: Object with roleplay elements\n"
            "- training_required: Boolean for training requirement\n"
            "- training_description: Description of training if required"
        )
        
        try:
            response = self.llm_service.generate(prompt)
            feat_data = self._extract_json(response)
            
            if feat_data:
                # Convert category and rarity strings to enums if needed
                if "category" in feat_data and isinstance(feat_data["category"], str):
                    try:
                        feat_data["category"] = FeatCategory(feat_data["category"])
                    except ValueError:
                        feat_data["category"] = FeatCategory.CUSTOM
                
                if "rarity" in feat_data and isinstance(feat_data["rarity"], str):
                    try:
                        feat_data["rarity"] = FeatRarity(feat_data["rarity"])
                    except ValueError:
                        feat_data["rarity"] = FeatRarity.CUSTOM
                
                # Create the custom feat
                return CustomFeat(**feat_data)
        except Exception as e:
            print(f"Error creating custom feat: {e}")
        
        # Fallback
        name = (partial_data or {}).get("name", f"Custom{concept.split()[0].title() if concept else ''}Feat")
        return CustomFeat(
            name=name,
            description=concept or "Custom feat",
            category=FeatCategory.CUSTOM,
            rarity=FeatRarity.CUSTOM
        )
    
    def analyze_feat_synergies(self, feat_list: List[str], 
                             character_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze synergies between feats.
        
        Args:
            feat_list: List of feat names
            character_data: Optional character data for context
            
        Returns:
            Dict[str, Any]: Synergy analysis
        """
        context = f"Feats: {', '.join(feat_list)}\n\n"
        
        if character_data:
            class_name = character_data.get("class", {}).get("name", "Unknown")
            context += f"Character Class: {class_name}\n"
            context += f"Character Level: {character_data.get('level', 1)}\n\n"
        
        prompt = self._create_prompt(
            "analyze feat synergies",
            context + 
            "Analyze how these feats synergize with each other. Identify combinations that work well together, "
            "any redundancies, and how they complement each other mechanically and narratively. "
            "Return as JSON with 'strong_synergies', 'weak_synergies', and 'overall_assessment' keys."
        )
        
        try:
            response = self.llm_service.generate(prompt)
            analysis = self._extract_json(response)
            
            if analysis:
                return analysis
        except Exception as e:
            print(f"Error analyzing feat synergies: {e}")
        
        # Fallback
        return {
            "strong_synergies": ["These feats generally work well together"],
            "weak_synergies": ["No significant conflicts identified"],
            "overall_assessment": "The selected feats form a coherent build"
        }

