from typing import Dict, Any, List
import re
import json

from backend.core.advisor.base_advisor import BaseAdvisor

class LLMFeatsAdvisor(BaseAdvisor):
    """
    Service for LLM-assisted feat recommendations and customization.
    
    This class handles all interactions with the LLM service to provide
    enhanced feat recommendations, narrative elements, and customization options.
    """
    
    def __init__(self, llm_service=None, cache_enabled=True):
        """
        Initialize the LLM feats advisor.
        
        Args:
            llm_service: LLM service client for generating responses
            cache_enabled: Whether to enable response caching
        """
        # Initialize base advisor with feats-specific system prompt
        system_prompt = "You are a D&D 5e (2024 rules) character creation expert specializing in feats and character development."
        super().__init__(llm_service, system_prompt, cache_enabled)
    
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
        
        prompt = self._format_prompt(
            f"recommend the top {count} feats for this character",
            context,
            [
                "For each recommended feat, provide its name",
                "Include a brief description of each feat",
                "Explain why it would be beneficial for this character",
                "Consider mechanical synergies, character concept, and roleplaying opportunities"
            ]
        )
        
        try:
            response = self._get_llm_response(
                "feat_recommendations", 
                prompt, 
                {"class": class_name, "level": level, "count": count}
            )
            
            # Extract JSON from response
            recommendations = self._extract_json(response)
            
            if recommendations:
                return recommendations
                
            # If no JSON was found, try to parse the response
            feats = []
            feat_blocks = re.findall(r'(?:\d+\.\s+|\*\s+)([^:]+):', response, re.IGNORECASE) or []
            
            for i, feat_name in enumerate(feat_blocks[:count]):
                feat = {
                    "name": feat_name.strip(),
                    "description": "Feat description unavailable",
                    "reason": "Recommended for your character"
                }
                feats.append(feat)
                
            if feats:
                return feats
                
        except Exception as e:
            self.logger.error(f"Error getting feat recommendations: {str(e)}")
        
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
        
        context = f"Feat: {feat_name}\nDescription: {feat_desc}\n"
        context += f"Character Class: {class_name}\nBackground: {background}\n"
        
        prompt = self._format_prompt(
            "create narrative elements for this feat",
            context,
            [
                "Describe how this feat manifests in the character's abilities and behavior",
                "Create a training story explaining how the character developed this ability",
                "Provide roleplay suggestions for how to showcase this feat",
                "Suggest dramatic character moments where this feat could shine"
            ]
        )
        
        try:
            response = self._get_llm_response(
                "feat_narrative", 
                prompt, 
                {"feat": feat_name, "class": class_name}
            )
            
            # Extract JSON from response
            narrative = self._extract_json(response)
            
            if narrative:
                return narrative
                
            # If no JSON was found, create a structured response manually
            manifestation = re.search(r'(?:Manifestation|Abilities):(.*?)(?:\n\n|\n[A-Z])', response, re.IGNORECASE | re.DOTALL)
            training = re.search(r'(?:Training|Story):(.*?)(?:\n\n|\n[A-Z])', response, re.IGNORECASE | re.DOTALL)
            roleplay = re.search(r'(?:Roleplay|Suggestions):(.*?)(?:\n\n|\n[A-Z])', response, re.IGNORECASE | re.DOTALL)
            moments = re.search(r'(?:Character|Moments|Dramatic):(.*?)(?:\n\n|\Z)', response, re.IGNORECASE | re.DOTALL)
            
            return {
                "manifestation": manifestation.group(1).strip() if manifestation else f"The {feat_name} feat manifests as a unique ability.",
                "training_story": training.group(1).strip() if training else "You developed this ability through practice.",
                "roleplay_suggestions": roleplay.group(1).strip() if roleplay else "Consider how this ability affects your character.",
                "character_moments": moments.group(1).strip() if moments else "This ability might shine in key dramatic moments."
            }
            
        except Exception as e:
            self.logger.error(f"Error generating narrative elements: {str(e)}")
        
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
        
        context = f"Character Information:\nClass: {class_name}\nSubclass: {subclass}\n"
        context += f"Current Level: {level}\nPlanning for: {future_levels} levels\n"
        context += f"Ability Scores: {json.dumps(ability_scores)}\nExisting Feats: {', '.join(existing_feats)}\n"
        
        prompt = self._format_prompt(
            "suggest a feat development path",
            context,
            [
                "Provide a step-by-step path for feat selection over the next few levels",
                "Explain how each suggested feat builds on previous choices",
                "Describe how the feat progression advances the character concept",
                f"Include specific recommendations for the next {future_levels} levels"
            ]
        )
        
        try:
            response = self._get_llm_response(
                "feat_development_path", 
                prompt, 
                {"class": class_name, "level": level, "future_levels": future_levels}
            )
            
            # Extract JSON from response
            path_data = self._extract_json(response)
            
            if path_data:
                return path_data
                
        except Exception as e:
            self.logger.error(f"Error generating development path: {str(e)}")
        
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
        
        context = f"Character Information:\nClass: {class_name}\nLevel: {level}\n"
        context += f"Ability Scores: {json.dumps(ability_scores)}\n"
        context += f"Feat: {feat_name}\nPrerequisites: {json.dumps(prerequisites)}\n"
        
        prompt = self._format_prompt(
            "suggest a path to qualify for this feat",
            context,
            [
                "Outline the most efficient steps to meet the feat prerequisites",
                "Consider ability score increases, multiclassing options, or other methods",
                "Estimate how many levels it would take to qualify",
                "Suggest alternative approaches if the primary path is too lengthy"
            ]
        )
        
        try:
            response = self._get_llm_response(
                "feat_qualification_path", 
                prompt, 
                {"feat": feat_name, "class": class_name, "level": level}
            )
            
            # Extract JSON from response
            path_data = self._extract_json(response)
            
            if path_data:
                return path_data
                
        except Exception as e:
            self.logger.error(f"Error generating qualification path: {str(e)}")
        
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
        
        context = f"Character Information:\nClass: {class_name}\nBackground: {background}\n"
        context += f"Feat Being Gained: {feat_name}\n"
        
        prompt = self._format_prompt(
            "create a narrative for gaining this feat",
            context,
            [
                "Write a short, evocative story describing how the character discovers this ability",
                "Include details about the training, event, or revelation that leads to this feat",
                "Make the narrative feel personal to this character's journey",
                "Focus on storytelling rather than mechanics"
            ]
        )
        
        try:
            response = self._get_llm_response(
                "feat_transition_narrative", 
                prompt, 
                {"feat": feat_name, "class": class_name}
            )
            
            # Remove any JSON formatting if present
            clean_response = re.sub(r'```.*?```', '', response, flags=re.DOTALL)
            clean_response = re.sub(r'\{.*?\}', '', clean_response, flags=re.DOTALL)
            
            return clean_response.strip()
            
        except Exception as e:
            self.logger.error(f"Error generating transition narrative: {str(e)}")
        
        # Fallback
        return f"Through practice and determination, your character develops the abilities granted by the {feat_name} feat."
    
    def create_custom_feat(self, concept: str = None, 
                         character_data: Dict[str, Any] = None,
                         partial_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create a custom feat based on a concept or partial data.
        
        Args:
            concept: Brief description of the feat concept
            character_data: Character data for context
            partial_data: Partial feat data to complete
            
        Returns:
            Dict[str, Any]: Custom feat data
        """
        if not concept and not partial_data:
            raise ValueError("Must provide either concept or partial_data")
        
        if partial_data:
            context = f"Partial feat data: {json.dumps(partial_data)}\n"
            if character_data:
                context += f"Character class: {character_data.get('class', {}).get('name', 'Unknown')}\n"
                context += f"Character level: {character_data.get('level', 1)}\n"
            task = "complete this partial feat definition"
        else:
            context = f"Feat concept: {concept}\n"
            if character_data:
                context += f"Character class: {character_data.get('class', {}).get('name', 'Unknown')}\n"
                context += f"Character level: {character_data.get('level', 1)}\n"
            task = "create a complete custom feat"
        
        prompt = self._format_prompt(
            task,
            context,
            [
                "Create a complete, balanced feat definition",
                "Include name, description, prerequisites, and benefits",
                "Define the feat category and rarity",
                "Add narrative elements and training requirements",
                "Ensure the feat follows D&D 5e design principles"
            ]
        )
        
        try:
            response = self._get_llm_response(
                "custom_feat_creation", 
                prompt, 
                {"concept": concept or "partial", "class": character_data.get("class", {}).get("name", "Unknown") if character_data else "Any"}
            )
            
            # Extract JSON from response
            feat_data = self._extract_json(response)
            
            if feat_data:
                return feat_data
                
        except Exception as e:
            self.logger.error(f"Error creating custom feat: {str(e)}")
        
        # Fallback
        name = (partial_data or {}).get("name", f"Custom{concept.split()[0].title() if concept else ''}Feat")
        return {
            "name": name,
            "description": concept or "Custom feat",
            "prerequisites": {},
            "benefits": {},
            "category": "CUSTOM",
            "rarity": "UNCOMMON",
            "narrative_elements": {
                "flavor_text": "This feat represents a unique ability developed through training and experience."
            },
            "training_required": False,
            "training_description": ""
        }
    
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
        context = f"Feats: {', '.join(feat_list)}\n"
        
        if character_data:
            class_name = character_data.get("class", {}).get("name", "Unknown")
            context += f"Character Class: {class_name}\n"
            context += f"Character Level: {character_data.get('level', 1)}\n"
        
        prompt = self._format_prompt(
            "analyze feat synergies",
            context,
            [
                "Identify combinations of feats that work well together",
                "Note any redundancies or conflicting mechanics",
                "Explain how the feats complement each other mechanically",
                "Describe potential narrative synergies between the feats",
                "Provide an overall assessment of the feat combination"
            ]
        )
        
        try:
            response = self._get_llm_response(
                "feat_synergy_analysis", 
                prompt, 
                {"feats": feat_list, "class": character_data.get("class", {}).get("name", "Unknown") if character_data else "Any"}
            )
            
            # Extract JSON from response
            analysis = self._extract_json(response)
            
            if analysis:
                return analysis
                
        except Exception as e:
            self.logger.error(f"Error analyzing feat synergies: {str(e)}")
        
        # Fallback
        return {
            "strong_synergies": ["These feats generally work well together"],
            "weak_synergies": ["No significant conflicts identified"],
            "overall_assessment": "The selected feats form a coherent build"
        }