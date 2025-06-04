# feat.py
# Description: Handles character feats and special abilities.

from typing import Dict, List, Optional, Union, Any
import json
import re
import uuid
from enum import Enum

from backend.core.ollama_service import OllamaService
from backend.core.feats.llm_feats_advisor import LLMFeatsAdvisor

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

class FeatManager:
    """
    Manager for both standard and custom feats.
    
    This class provides a unified interface for working with standard D&D feats
    and completely custom feats, with full LLM assistance.
    """
    
    def __init__(self, llm_service=None):
        """Initialize the feat manager."""
        self.llm_service = llm_service or OllamaService()
        self.llm_advisor = LLMFeatsAdvisor(self.llm_service)
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