from typing import Dict, List, Any, Tuple, Optional
import json
import uuid
import logging
from enum import Enum

from backend.core.services.ollama_service import OllamaService
from backend.core.classes.abstract_character_class import AbstractCharacterClass
from backend.core.classes.llm_class_advisor import LLMClassAdvisor
from backend.core.services.class_validation_service import ClassValidationService

logger = logging.getLogger(__name__)

class SpellcastingType(Enum):
    """Types of spellcasting a class might have"""
    NONE = "none"
    FULL = "full"
    HALF = "half"
    THIRD = "third"
    PACT = "pact"
    UNIQUE = "unique"

class CustomClass(AbstractCharacterClass):
    """Custom character class implementation with full LLM integration."""
    
    def __init__(self, name: str, **kwargs):
        """Initialize a custom character class."""
        self.name = name
        self.description = kwargs.get('description', '')
        self.hit_die = kwargs.get('hit_die', 8)
        self.primary_ability = kwargs.get('primary_ability', ["Strength"])
        self.saving_throw_proficiencies = kwargs.get('saving_throw_proficiencies', 
                                                   ["Strength", "Constitution"])
        self.armor_proficiencies = kwargs.get('armor_proficiencies', [])
        self.weapon_proficiencies = kwargs.get('weapon_proficiencies', ["Simple"])
        self.skill_proficiencies = kwargs.get('skill_proficiencies', 
                                            {"choose": 2, "from": ["Athletics", "Arcana", "History"]})
        self.tool_proficiencies = kwargs.get('tool_proficiencies', [])
        self.starting_equipment = kwargs.get('starting_equipment', 
                                           {"options": [{"items": ["Quarterstaff", "Explorer's Pack"]}]})
        self.class_features = kwargs.get('class_features', 
                                       {1: [{"name": "First Feature", 
                                            "description": "Your first class feature."}]})
        self.subclasses = kwargs.get('subclasses', [])
        self.spellcasting_type = kwargs.get('spellcasting_type', SpellcastingType.NONE)
        self.spellcasting_ability = kwargs.get('spellcasting_ability')
        self.class_resources = kwargs.get('class_resources', {})
        self.multiclass_requirements = kwargs.get('multiclass_requirements', {})
        self.suggested_builds = kwargs.get('suggested_builds', [])
        self.flavor_text = kwargs.get('flavor_text', {"combat_style": "Versatile", "personality": "Adaptable"})
        self.custom_id = kwargs.get('custom_id', str(uuid.uuid4()))
        self.source = "Custom"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert class to dictionary representation."""
        return {
            "name": self.name,
            "description": self.description,
            "hit_die": self.hit_die,
            "primary_ability": self.primary_ability,
            "saving_throw_proficiencies": self.saving_throw_proficiencies,
            "armor_proficiencies": self.armor_proficiencies,
            "weapon_proficiencies": self.weapon_proficiencies,
            "skill_proficiencies": self.skill_proficiencies,
            "tool_proficiencies": self.tool_proficiencies,
            "starting_equipment": self.starting_equipment,
            "class_features": self.class_features,
            "subclasses": self.subclasses,
            "spellcasting_type": self.spellcasting_type.value if hasattr(self.spellcasting_type, 'value') else self.spellcasting_type,
            "spellcasting_ability": self.spellcasting_ability,
            "class_resources": self.class_resources,
            "multiclass_requirements": self.multiclass_requirements,
            "suggested_builds": self.suggested_builds,
            "flavor_text": self.flavor_text,
            "custom_id": self.custom_id,
            "source": self.source
        }


class CharacterClassManager:
    """Manager for both standard and custom character classes."""
    
    CORE_CLASSES = [
        "Artificer", "Barbarian", "Bard", "Cleric", "Druid", 
        "Fighter", "Monk", "Paladin", "Ranger", "Rogue",
        "Sorcerer", "Warlock", "Wizard"
    ]
    
    def __init__(self, llm_service=None, validation_service=None):
        self.llm_service = llm_service or OllamaService()
        self.llm_creator = LLMClassAdvisor(self.llm_service)
        self.validation_service = validation_service or ClassValidationService(self.llm_service)
        self.standard_classes = self._initialize_standard_classes()
        self.custom_classes = {}
    
    def _initialize_standard_classes(self):
        """Initialize standard D&D classes."""
        return {class_name.lower(): {
            "name": class_name,
            "source": "Player's Handbook",
            "description": f"Standard {class_name} class from the core rules."
        } for class_name in self.CORE_CLASSES}
    
    # ----- CORE CLASS METHODS -----
    
    def get_all_classes(self, filtered_by_concept=False, character_concept=None):
        """Get all available classes, optionally filtered by character concept."""
        standard_class_data = list(self.standard_classes.values())
        custom_class_data = [cls.to_dict() for cls in self.custom_classes.values()]
        all_classes = standard_class_data + custom_class_data
        
        if not filtered_by_concept or not character_concept:
            return all_classes
            
        return self._recommend_classes_by_concept(all_classes, character_concept)
    
    def get_class_details(self, class_name, include_roleplay_guidance=False):
        """Get detailed information about a class."""
        class_key = class_name.lower()
        details = None
        
        # Find class in standard classes
        if class_key in self.standard_classes:
            details = self.standard_classes[class_key].copy()
        else:
            # Look in custom classes
            for custom_class in self.custom_classes.values():
                if custom_class.name.lower() == class_name.lower():
                    details = custom_class.to_dict()
                    break
        
        if not details:
            return None
            
        # Add roleplay guidance if requested
        if include_roleplay_guidance:
            details["roleplay_guidance"] = self._generate_roleplay_guidance(class_name, details)
            
        return details
    
    # ----- CLASS CREATION & MODIFICATION -----
    
    def create_custom_class(self, class_data):
        """Create a custom class from complete data, partial data, or just a concept."""
        # Create from concept or partial data
        custom_class = (
            self.llm_creator.generate_complete_class(concept=class_data.get("concept"))
            if "concept" in class_data and len(class_data) < 5
            else self.llm_creator.generate_complete_class(partial_data=class_data)
        )
        
        # Validate and balance
        is_valid, issues = self.validation_service.validate_class(custom_class)
        if not is_valid or issues:
            logger.info(f"Validation found {len(issues)} issues with class {custom_class.name}")
            custom_class = self.validation_service.apply_balance_corrections(custom_class, issues)
        
        # Store and return
        self.custom_classes[custom_class.custom_id] = custom_class
        return custom_class
    
    def modify_class(self, class_id, modification_type, **kwargs):
        """
        Unified method to modify a class in various ways.
        
        Args:
            class_id: ID of the class to modify
            modification_type: Type of modification ('feature', 'subclass', 'resource', 'refine')
            **kwargs: Arguments specific to the modification type
        
        Returns:
            CustomClass: Modified class
        """
        if class_id not in self.custom_classes:
            raise ValueError(f"No custom class found with ID: {class_id}")
            
        custom_class = self.custom_classes[class_id]
        class_data = custom_class.to_dict()
        
        # Handle different modification types
        if modification_type == 'feature':
            level, concept = kwargs.get('level'), kwargs.get('concept')
            feature = self.llm_creator.generate_class_feature(custom_class.name, level, concept)
            features = class_data.get("class_features", {})
            level_str = str(level)
            if level_str not in features:
                features[level_str] = []
            features[level_str].append(feature)
            class_data["class_features"] = features
            
        elif modification_type == 'subclass':
            concept = kwargs.get('concept')
            subclass = self.llm_creator.generate_subclass(custom_class.name, concept)
            class_data["subclasses"] = class_data.get("subclasses", []) + [subclass]
            
        elif modification_type == 'resource':
            name, data = kwargs.get('name'), kwargs.get('data')
            resources = class_data.get("class_resources", {})
            resources[name] = data
            class_data["class_resources"] = resources
            
        elif modification_type == 'refine':
            refinement = kwargs.get('refinement')
            return self.refine_class(class_id, refinement)
            
        else:
            raise ValueError(f"Unknown modification type: {modification_type}")
        
        # Convert spellcasting type if needed
        if isinstance(class_data.get("spellcasting_type"), str):
            try:
                class_data["spellcasting_type"] = SpellcastingType(class_data["spellcasting_type"])
            except ValueError:
                class_data["spellcasting_type"] = custom_class.spellcasting_type
        
        # Create updated class with a new ID
        class_data["custom_id"] = None
        updated_class = CustomClass(**class_data)
        self.custom_classes[updated_class.custom_id] = updated_class
        
        return updated_class
    
    def refine_class(self, class_id, refinement_request):
        """Refine a class based on user feedback."""
        if class_id not in self.custom_classes:
            raise ValueError(f"No custom class found with ID: {class_id}")
        
        original_class = self.custom_classes[class_id]
        
        # Generate refined class
        prompt = self.llm_creator._create_prompt(
            "refine a character class",
            f"Original class: {json.dumps(original_class.to_dict())}\n"
            f"Refinement request: {refinement_request}\n\n"
            f"Update this class according to the refinement request while maintaining game balance. "
            f"Preserve the core concept and only change what's necessary to address the request. "
            f"Return the complete refined class as JSON with the same structure."
        )
        
        try:
            response = self.llm_service.generate(prompt)
            refined_data = self.llm_creator._extract_json(response)
            
            if not refined_data:
                return original_class, [{"component": "refinement", 
                                       "issue": "Failed to generate refinements",
                                       "severity": "error"}]
            
            # Process spellcasting type
            if isinstance(refined_data.get("spellcasting_type"), str):
                try:
                    refined_data["spellcasting_type"] = SpellcastingType(refined_data["spellcasting_type"])
                except ValueError:
                    refined_data["spellcasting_type"] = original_class.spellcasting_type
                    
            # Create refined class
            refined_class = CustomClass(**refined_data)
            
            # Validate and apply corrections
            is_valid, issues = self.validation_service.validate_class(refined_class)
            if not is_valid:
                refined_class = self.validation_service.apply_balance_corrections(refined_class, issues)
                is_valid, issues = self.validation_service.validate_class(refined_class)
            
            # Store the refined class
            self.custom_classes[refined_class.custom_id] = refined_class
            
            return refined_class, issues
            
        except Exception as e:
            logger.error(f"Error refining class: {e}")
            return original_class, [{"component": "refinement", 
                                   "issue": f"Error during refinement: {str(e)}",
                                   "severity": "error"}]
    
    # ----- HELPER METHODS -----
    
    def _recommend_classes_by_concept(self, class_list, character_concept):
        """Use LLM to recommend classes based on character concept."""
        class_names = [c["name"] for c in class_list]
        
        prompt = self.llm_creator._create_prompt(
            "recommend classes for this character concept",
            f"Character concept: {character_concept}\n"
            f"Available classes: {', '.join(class_names)}\n\n"
            f"Recommend the top 3-5 classes that would best fit this character concept. "
            f"For each recommendation, provide a brief explanation of why it fits. "
            f"Return as JSON array with 'name' and 'reason' keys."
        )
        
        try:
            response = self.llm_service.generate(prompt)
            recommendations = self.llm_creator._extract_json(response)
            
            if recommendations and isinstance(recommendations, list):
                # Map recommendations to original class data
                recommended_names = [r["name"] for r in recommendations]
                return [{
                    **cls,
                    "recommendation_reason": next(
                        (r["reason"] for r in recommendations if r["name"] == cls["name"]),
                        None
                    )
                } for cls in class_list if cls["name"] in recommended_names]
                
        except Exception as e:
            logger.error(f"Error getting class recommendations: {e}")
        
        # Return unfiltered on failure
        return class_list
    
    def _generate_roleplay_guidance(self, class_name, class_details):
        """Generate roleplay guidance for a class using LLM."""
        description = class_details.get("description", f"A {class_name} class")
        
        prompt = self.llm_creator._create_prompt(
            "create roleplay guidance for this class",
            f"Class: {class_name}\nDescription: {description}\n\n"
            f"Provide roleplay guidance for this class including: personality suggestions, "
            f"background ideas, character quirks, roleplaying challenges, and RP dynamics with other classes."
        )
        
        try:
            response = self.llm_service.generate(prompt)
            guidance_data = self.llm_creator._extract_json(response)
            if guidance_data:
                return guidance_data
        except Exception as e:
            logger.error(f"Error generating roleplay guidance: {e}")
        
        # Fallback
        return {
            "personality_suggestions": [f"Consider how your {class_name}'s abilities shape their worldview"],
            "background_ideas": [f"A background that complements the {class_name}'s skills"],
            "character_quirks": [f"A unique habit related to their {class_name} abilities"]
        }