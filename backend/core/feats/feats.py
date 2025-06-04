# feat.py
# Description: Handles character feats and special abilities.

from typing import Dict, List, Optional, Union, Any
import json
import re
import uuid
from enum import Enum

from backend.core.ollama_service import OllamaService
from backend.core.abilities.ability_scores import AbilityScores

class FeatRarity(Enum):
    """Enumeration for feat rarity types"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    VERY_RARE = "very_rare"
    LEGENDARY = "legendary"
    CUSTOM = "custom"  # For completely custom feats

class FeatCategory(Enum):
    """Categories for feats to help with organization and filtering"""
    COMBAT = "combat"
    MAGIC = "magic"
    SKILL = "skill"
    SOCIAL = "social"
    RACIAL = "racial"
    BACKGROUND = "background"
    GENERAL = "general"
    CUSTOM = "custom"  # For custom categories

class CustomFeat:
    """
    Class representing a custom feat that can be created or modified.
    
    This class provides a structure for creating completely new feats
    or customizing existing ones with LLM assistance.
    """
    
    def __init__(self,
                name: str,
                description: str,
                prerequisites: Dict[str, Any] = None,
                benefits: Dict[str, Any] = None,
                category: FeatCategory = FeatCategory.CUSTOM,
                rarity: FeatRarity = FeatRarity.CUSTOM,
                narrative_elements: Dict[str, str] = None,
                training_required: bool = False,
                training_description: str = "",
                custom_id: str = None):
        """
        Initialize a custom feat with all necessary attributes.
        
        Args:
            name: Name of the feat
            description: Description of what the feat does
            prerequisites: Dict of requirements to take this feat
            benefits: Dict of benefits the feat provides
            category: The category this feat belongs to
            rarity: How rare/powerful this feat is
            narrative_elements: Dict of storytelling elements
            training_required: Whether the feat requires training
            training_description: Description of required training
            custom_id: Unique identifier for the feat
        """
        self.name = name
        self.description = description
        self.prerequisites = prerequisites or {}
        self.benefits = benefits or {}
        self.category = category
        self.rarity = rarity
        self.narrative_elements = narrative_elements or {}
        self.training_required = training_required
        self.training_description = training_description
        self.custom_id = custom_id or str(uuid.uuid4())
        self.source = "Custom"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert feat to dictionary representation."""
        return {
            "name": self.name,
            "description": self.description,
            "prerequisites": self.prerequisites,
            "benefits": self.benefits,
            "category": self.category.value,
            "rarity": self.rarity.value,
            "narrative_elements": self.narrative_elements,
            "training_required": self.training_required,
            "training_description": self.training_description,
            "custom_id": self.custom_id,
            "source": self.source
        }

class LLMFeatAdvisor:
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


class FeatManager:
    """
    Manager for both standard and custom feats.
    
    This class provides a unified interface for working with standard D&D feats
    and completely custom feats, with full LLM assistance.
    """
    
    def __init__(self, llm_service=None):
        """Initialize the feat manager."""
        self.llm_service = llm_service or OllamaService()
        self.llm_advisor = LLMFeatAdvisor(self.llm_service)
        self.standard_feats = {}  # Will hold standard feat data by name
        self.custom_feats = {}  # Will hold custom feats by ID
        
        # Initialize standard feats
        self._initialize_standard_feats()
    
    def _initialize_standard_feats(self):
        """Initialize standard feats from core rules."""
        # This would normally load data from a database or file
        # For this example, we'll just create placeholder entries for common feats
        standard_feats = [
            {"name": "Alert", "description": "Always on watch for danger."},
            {"name": "Athlete", "description": "You have undergone extensive physical training."},
            {"name": "Actor", "description": "Skilled at mimicry and dramatics."},
            {"name": "Charger", "description": "You can use the dash action to make a special melee attack."},
            {"name": "Crossbow Expert", "description": "You have mastered the crossbow."},
            {"name": "Defensive Duelist", "description": "Quick with a blade to deflect attacks."},
            {"name": "Dual Wielder", "description": "Master of fighting with two weapons."},
            {"name": "Dungeon Delver", "description": "Alert to the hidden traps of dungeons."},
            {"name": "Elemental Adept", "description": "Master of a particular element of magic."},
            {"name": "Great Weapon Master", "description": "Skilled at making big swings with heavy weapons."}
        ]
        
        for feat in standard_feats:
            self.standard_feats[feat["name"]] = feat
    
    def get_all_feats(self, suggest_for_character: bool = False, 
                    character_data: Dict[str, Any] = None,
                    character_concept: str = None) -> List[Dict[str, Any]]:
        """
        Get all available feats, optionally with recommendations.
        
        Args:
            suggest_for_character: Whether to include recommendations
            character_data: Character data for recommendations
            character_concept: Character concept for recommendations
            
        Returns:
            List[Dict[str, Any]]: List of available feats
        """
        # Get all standard feats
        standard_feat_data = list(self.standard_feats.values())
        
        # Get all custom feats
        custom_feat_data = [feat.to_dict() for feat in self.custom_feats.values()]
        
        # Combine lists
        all_feats = standard_feat_data + custom_feat_data
        
        # If no recommendations needed, return all
        if not suggest_for_character or not character_data:
            return all_feats
        
        # Use LLM to recommend feats based on character data
        recommendations = self.llm_advisor.recommend_feats(
            character_data, character_concept
        )
        
        # Add recommendation reasoning to the feat data
        for feat in all_feats:
            for rec in recommendations:
                if feat["name"] == rec["name"]:
                    feat["recommendation_reason"] = rec.get("reason")
                    feat["recommendation_rank"] = recommendations.index(rec) + 1
        
        # Sort feats, putting recommended ones first
        return sorted(all_feats, key=lambda x: x.get("recommendation_rank", 999))
    
    def get_feat_details(self, feat_name: str, 
                       include_narrative_elements: bool = False,
                       character_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Get detailed information about a feat.
        
        Args:
            feat_name: Name of the feat
            include_narrative_elements: Whether to include narrative elements
            character_data: Character data for personalization
            
        Returns:
            Dict[str, Any]: Feat details
        """
        # Check standard feats
        if feat_name in self.standard_feats:
            details = self.standard_feats[feat_name].copy()
        else:
            # Check custom feats
            for custom_feat in self.custom_feats.values():
                if custom_feat.name.lower() == feat_name.lower():
                    details = custom_feat.to_dict()
                    break
            else:
                return None  # Feat not found
        
        # Add narrative elements if requested
        if include_narrative_elements and character_data:
            narrative = self.llm_advisor.generate_narrative_elements(
                feat_name, details.get("description", ""), character_data
            )
            details["narrative_elements"] = narrative
        
        return details
    
    def get_available_feats(self, character_data: Dict[str, Any], 
                          suggest_development_path: bool = False) -> List[Dict[str, Any]]:
        """
        Get feats available to a specific character.
        
        Args:
            character_data: Character attributes and stats
            suggest_development_path: Whether to include development path
            
        Returns:
            List[Dict[str, Any]]: Available feats
        """
        # Filter feats based on prerequisites
        available_feats = []
        
        for feat_name, feat_data in self.standard_feats.items():
            if self.validate_feat_prerequisites(character_data, feat_name):
                available_feats.append(feat_data)
        
        for custom_feat in self.custom_feats.values():
            if self.validate_feat_prerequisites(character_data, custom_feat.name):
                available_feats.append(custom_feat.to_dict())
        
        # Add development path if requested
        if suggest_development_path:
            path_data = self.llm_advisor.suggest_development_path(character_data)
            
            # Add development path suggestion to applicable feats
            for feat in available_feats:
                for path_step in path_data.get("path", []):
                    if feat["name"] == path_step.get("feat"):
                        feat["development_suggestion"] = {
                            "level": path_step.get("level"),
                            "reasoning": path_step.get("reasoning")
                        }
        
        return available_feats
    
    def validate_feat_prerequisites(self, character_data: Dict[str, Any], 
                                  feat_name: str,
                                  suggest_qualification_path: bool = False) -> Union[bool, Dict[str, Any]]:
        """
        Check if character meets feat prerequisites.
        
        Args:
            character_data: Character attributes and stats
            feat_name: Name of the feat to check
            suggest_qualification_path: Whether to suggest a path to qualify
            
        Returns:
            Union[bool, Dict[str, Any]]: True if qualified, or dict with qualification info
        """
        # Get the feat prerequisites
        prerequisites = {}
        
        # Check standard feats
        if feat_name in self.standard_feats:
            prerequisites = self.standard_feats[feat_name].get("prerequisites", {})
        else:
            # Check custom feats
            for custom_feat in self.custom_feats.values():
                if custom_feat.name.lower() == feat_name.lower():
                    prerequisites = custom_feat.prerequisites
                    break
        
        # If no prerequisites, automatically qualified
        if not prerequisites:
            return True
        
        # Check ability score prerequisites
        ability_scores = character_data.get("ability_scores", {})
        ability_prerequisites = prerequisites.get("ability_scores", {})
        
        for ability, required_score in ability_prerequisites.items():
            if ability_scores.get(ability.lower(), 0) < required_score:
                if not suggest_qualification_path:
                    return False
                
                # Generate qualification path
                path_data = self.llm_advisor.suggest_qualification_path(
                    character_data, feat_name, prerequisites
                )
                
                return {
                    "qualified": False,
                    "missing_prerequisites": {"ability_scores": {ability: required_score}},
                    "qualification_path": path_data
                }
        
        # Check level prerequisites
        if "level" in prerequisites and character_data.get("level", 1) < prerequisites["level"]:
            if not suggest_qualification_path:
                return False
            
            # Generate qualification path
            path_data = self.llm_advisor.suggest_qualification_path(
                character_data, feat_name, prerequisites
            )
            
            return {
                "qualified": False,
                "missing_prerequisites": {"level": prerequisites["level"]},
                "qualification_path": path_data
            }
        
        # Check class prerequisites
        if "class" in prerequisites:
            character_class = character_data.get("class", {}).get("name", "").lower()
            required_class = prerequisites["class"].lower()
            
            if character_class != required_class:
                if not suggest_qualification_path:
                    return False
                
                # Generate qualification path
                path_data = self.llm_advisor.suggest_qualification_path(
                    character_data, feat_name, prerequisites
                )
                
                return {
                    "qualified": False,
                    "missing_prerequisites": {"class": required_class},
                    "qualification_path": path_data
                }
        
        # All prerequisites met
        if suggest_qualification_path:
            return {"qualified": True}
        
        return True
    
    def apply_feat_benefits(self, character_data: Dict[str, Any], 
                          feat_name: str,
                          include_narrative_transition: bool = False) -> Dict[str, Any]:
        """
        Apply the benefits of a feat to character stats.
        
        Args:
            character_data: Character attributes to modify
            feat_name: Name of the feat to apply
            include_narrative_transition: Whether to include narrative
            
        Returns:
            Dict[str, Any]: Updated character data
        """
        # Get feat benefits
        benefits = {}
        
        # Check standard feats
        if feat_name in self.standard_feats:
            benefits = self.standard_feats[feat_name].get("benefits", {})
        else:
            # Check custom feats
            for custom_feat in self.custom_feats.values():
                if custom_feat.name.lower() == feat_name.lower():
                    benefits = custom_feat.benefits
                    break
        
        # Create a deep copy of character data
        updated_data = json.loads(json.dumps(character_data))
        
        # Apply ability score increases
        if "ability_scores" in benefits:
            for ability, bonus in benefits["ability_scores"].items():
                ability_lower = ability.lower()
                if ability_lower in updated_data["ability_scores"]:
                    updated_data["ability_scores"][ability_lower] += bonus
        
        # Apply skill proficiencies
        if "skill_proficiencies" in benefits:
            if "proficiencies" not in updated_data:
                updated_data["proficiencies"] = {}
            
            if "skills" not in updated_data["proficiencies"]:
                updated_data["proficiencies"]["skills"] = []
            
            for skill in benefits["skill_proficiencies"]:
                if skill not in updated_data["proficiencies"]["skills"]:
                    updated_data["proficiencies"]["skills"].append(skill)
        
        # Apply speed changes
        if "speed" in benefits:
            if "speed" not in updated_data:
                updated_data["speed"] = {}
            
            for speed_type, value in benefits["speed"].items():
                updated_data["speed"][speed_type] = value
        
        # Add feat to character's feat list
        if "feats" not in updated_data:
            updated_data["feats"] = []
        
        if feat_name not in updated_data["feats"]:
            updated_data["feats"].append(feat_name)
        
        # Add special traits
        if "special_traits" in benefits:
            if "special_traits" not in updated_data:
                updated_data["special_traits"] = []
            
            for trait in benefits["special_traits"]:
                if trait not in updated_data["special_traits"]:
                    updated_data["special_traits"].append(trait)
        
        # Add narrative transition if requested
        if include_narrative_transition:
            narrative = self.llm_advisor.generate_transition_narrative(character_data, feat_name)
            updated_data["narrative_elements"] = updated_data.get("narrative_elements", {})
            updated_data["narrative_elements"]["feat_transitions"] = updated_data["narrative_elements"].get("feat_transitions", {})
            updated_data["narrative_elements"]["feat_transitions"][feat_name] = narrative
        
        return updated_data
    
    def create_custom_feat(self, concept_or_data: Dict[str, Any], 
                         character_data: Dict[str, Any] = None) -> CustomFeat:
        """
        Create a custom feat based on concept or partial data.
        
        Args:
            concept_or_data: Concept description or partial feat data
            character_data: Character data for context (optional)
            
        Returns:
            CustomFeat: Newly created custom feat
        """
        # Check if we have a concept string or partial data
        if isinstance(concept_or_data, str):
            custom_feat = self.llm_advisor.create_custom_feat(concept=concept_or_data, character_data=character_data)
        else:
            custom_feat = self.llm_advisor.create_custom_feat(partial_data=concept_or_data, character_data=character_data)
        
        # Store the custom feat
        self.custom_feats[custom_feat.custom_id] = custom_feat
        return custom_feat
    
    def analyze_feat_synergies(self, feat_names: List[str], 
                             character_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze synergies between selected feats.
        
        Args:
            feat_names: List of feat names to analyze
            character_data: Character data for context
            
        Returns:
            Dict[str, Any]: Synergy analysis
        """
        return self.llm_advisor.analyze_feat_synergies(feat_names, character_data)


# Example usage
# def demonstrate_feat_customization():
#     """Demonstrate the features of the feat customization system"""
#     manager = FeatManager()
    
#     print("=== CREATING CUSTOM FEATS ===")
    
#     # Create from just a concept
#     battle_sage = manager.create_custom_feat(
#         "A feat that combines scholarly knowledge with battlefield tactics"
#     )
#     print(f"Created feat: {battle_sage.name}")
    
#     # Create with partial specification
#     shadow_step = manager.create_custom_feat({
#         "name": "Shadow Step",
#         "description": "You can step between shadows, teleporting short distances",
#         "prerequisites": {"ability_scores": {"Dexterity": 13}}
#     })
#     print(f"Created feat with partial spec: {shadow_step.name}")
    
#     print("\n=== FEAT RECOMMENDATIONS ===")
    
#     # Sample character data
#     character_data = {
#         "class": {"name": "Ranger"},
#         "level": 4,
#         "ability_scores": {"strength": 12, "dexterity": 16, "constitution": 14, 
#                          "intelligence": 10, "wisdom": 14, "charisma": 8},
#         "background": {"name": "Outlander"},
#         "proficiencies": {"skills": ["Survival", "Nature", "Stealth", "Perception"]},
#         "feats": []
#     }
    
#     # Get feat recommendations
#     concept = "A wilderness tracker who specializes in hunting dangerous beasts"
#     recommended = manager.get_all_feats(
#         suggest_for_character=True,
#         character_data=character_data,
#         character_concept=concept
#     )
#     print(f"Recommended feats for {concept}:")
#     for feat in recommended[:3]:
#         reason = feat.get("recommendation_reason", "No reason provided")
#         print(f"- {feat['name']}: {reason}")
    
#     print("\n=== NARRATIVE ELEMENTS ===")
    
#     # Get narrative elements for a feat
#     feat_details = manager.get_feat_details(
#         "Alert",
#         include_narrative_elements=True,
#         character_data=character_data
#     )
    
#     if feat_details and "narrative_elements" in feat_details:
#         print(f"Narrative elements for Alert feat:")
#         elements = feat_details["narrative_elements"]
#         for key, value in list(elements.items())[:2]:
#             print(f"- {key}: {value}")
    
#     print("\n=== FEAT DEVELOPMENT PATH ===")
    
#     # Get feat development path
#     available_feats = manager.get_available_feats(
#         character_data,
#         suggest_development_path=True
#     )
    
#     development_feats = [f for f in available_feats if "development_suggestion" in f]
#     if development_feats:
#         print("Suggested feat development path:")
#         for feat in development_feats[:2]:
#             suggestion = feat["development_suggestion"]
#             print(f"- Level {suggestion['level']}: {feat['name']} - {suggestion['reasoning']}")
    
#     return {
#         "battle_sage": battle_sage,
#         "shadow_step": shadow_step,
#         "recommendations": recommended[:3],
#         "narrative_elements": feat_details.get("narrative_elements") if feat_details else None
#     }


# if __name__ == "__main__":
#     demonstrate_feat_customization()