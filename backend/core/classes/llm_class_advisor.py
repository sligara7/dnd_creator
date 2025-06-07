import json
import logging
from typing import Dict, List, Any, Union
from enum import Enum

from backend.core.advisor.base_advisor import BaseAdvisor
from backend.core.classes.class_models import CustomClass, SpellcastingType

logger = logging.getLogger(__name__)

class LLMClassAdvisor(BaseAdvisor):
    """Service for generating custom character classes using LLM"""
    
    def __init__(self, llm_service=None, cache_enabled=True):
        """Initialize with optional custom LLM service"""
        system_prompt = "You are a D&D 5e (2024 rules) game designer specializing in balanced class creation."
        super().__init__(llm_service, system_prompt, cache_enabled)
    
    def generate_class_concept(self, concept_description: str) -> Dict[str, Any]:
        """Generate a high-level class concept based on a description."""
        prompt = self._format_prompt(
            "Create a D&D character class concept",
            f"Concept: {concept_description}",
            [
                "Name for this class concept",
                "Brief description of the class",
                "Playstyle summary",
                "Primary abilities",
                "A unique class mechanic"
            ]
        )
        
        try:
            response = self._get_llm_response(
                "class_concept", 
                prompt, 
                {"concept": concept_description[:50]}
            )
            
            concept_data = self._extract_json(response)
            if concept_data:
                return concept_data
        except Exception as e:
            logger.error(f"Error generating class concept: {e}")
        
        # Fallback
        return {
            "name": concept_description.split()[0].capitalize() + "master",
            "description": f"A class based on the concept: {concept_description}",
            "playstyle": "Balanced between combat and utility abilities",
            "primary_abilities": ["Dexterity", "Wisdom"],
            "unique_mechanic": "Adaptability in various situations"
        }
    
    def generate_complete_class(self, concept: str = None, partial_data: Dict[str, Any] = None) -> CustomClass:
        """Generate a complete custom class with all required attributes."""
        if not concept and not partial_data:
            raise ValueError("Must provide either concept or partial_data")
        
        if partial_data:
            context = f"Partial class data: {json.dumps(partial_data)}\n\n"
            context += "Fill in all missing attributes to create a complete, balanced class."
            task = "Complete this partial class definition"
        else:
            context = f"Class concept: {concept}"
            task = "Create a complete custom character class based on this concept"
        
        prompt = self._format_prompt(
            task,
            context,
            [
                "name: The class name",
                "description: Class description",
                "hit_die: Hit die size (6, 8, 10, or 12)",
                "primary_ability: Array of primary abilities",
                "saving_throw_proficiencies: Array of saving throw proficiencies (max 2)",
                "armor_proficiencies: Array of armor proficiencies",
                "weapon_proficiencies: Array of weapon proficiencies",
                "skill_proficiencies: Object with 'choose' (number) and 'from' (array of skills)",
                "tool_proficiencies: Array of tool proficiencies",
                "starting_equipment: Object with equipment options",
                "class_features: Object mapping levels (1-20) to arrays of features",
                "spellcasting_type: 'none', 'full', 'half', 'third', 'pact', or 'unique'",
                "spellcasting_ability: Ability used for spellcasting (if applicable)",
                "class_resources: Object describing class-specific resources",
                "multiclass_requirements: Object mapping abilities to minimum scores",
                "flavor_text: Object with flavor elements"
            ]
        )
        
        try:
            response = self._get_llm_response(
                "complete_class",
                prompt,
                {"concept": concept[:50] if concept else "partial_class"}
            )
            
            class_data = self._extract_json(response)
            
            if class_data:
                # Convert spellcasting type string to enum
                if "spellcasting_type" in class_data:
                    try:
                        class_data["spellcasting_type"] = SpellcastingType(class_data["spellcasting_type"])
                    except ValueError:
                        class_data["spellcasting_type"] = SpellcastingType.NONE
                
                # Create the custom class
                return CustomClass(**class_data)
        except Exception as e:
            logger.error(f"Error generating complete class: {e}")
        
        # Fallback if LLM fails
        name = (partial_data or {}).get("name", f"Custom{concept.split()[0].title()}") if concept else "CustomClass"
        return CustomClass(
            name=name,
            description=concept or "Custom character class",
            hit_die=8,
            primary_ability=["Dexterity", "Wisdom"],
            saving_throw_proficiencies=["Dexterity", "Wisdom"],
            armor_proficiencies=["Light"],
            weapon_proficiencies=["Simple"],
            skill_proficiencies={"choose": 3, "from": ["Acrobatics", "Insight", "Perception", "Stealth"]},
            class_features={
                1: [{"name": "Custom Feature", "description": "A unique feature for this class."}]
            }
        )
    
    def generate_class_feature(self, class_name: str, level: int, 
                             feature_concept: str) -> Dict[str, Any]:
        """Generate a class feature for a specific level."""
        prompt = self._format_prompt(
            "Create a balanced class feature",
            f"Class: {class_name}\nLevel: {level}\nConcept: {feature_concept}",
            [
                "Feature name",
                "Description of what the feature does",
                "Mechanics of how the feature works",
                "Limitations (e.g., uses per day, restrictions)"
            ]
        )
        
        try:
            response = self._get_llm_response(
                "class_feature",
                prompt,
                {"class": class_name, "level": level, "concept": feature_concept[:50]}
            )
            
            feature_data = self._extract_json(response)
            
            if feature_data:
                return feature_data
        except Exception as e:
            logger.error(f"Error generating class feature: {e}")
        
        # Fallback
        return {
            "name": f"{feature_concept.split()[0].title()} Technique",
            "description": f"A technique based on {feature_concept}.",
            "mechanics": "You can use an action to activate this ability.",
            "limitations": "You can use this feature a number of times equal to your proficiency bonus per long rest."
        }
    
    def generate_subclass(self, base_class_name: str, 
                        subclass_concept: str) -> Dict[str, Any]:
        """Generate a subclass for a base class."""
        prompt = self._format_prompt(
            "Create a character subclass",
            f"Base Class: {base_class_name}\nSubclass Concept: {subclass_concept}",
            [
                "Subclass name",
                "Description of the subclass concept",
                "Features at appropriate levels for this type of subclass"
            ]
        )
        
        try:
            response = self._get_llm_response(
                "subclass",
                prompt,
                {"base_class": base_class_name, "concept": subclass_concept[:50]}
            )
            
            subclass_data = self._extract_json(response)
            
            if subclass_data:
                return subclass_data
        except Exception as e:
            logger.error(f"Error generating subclass: {e}")
        
        # Fallback
        return {
            "name": f"{subclass_concept.split()[0].title()} {base_class_name}",
            "description": f"A {base_class_name} that specializes in {subclass_concept}.",
            "features": {
                "3": [{"name": "Specialization Feature", "description": f"You gain abilities related to {subclass_concept}."}]
            }
        }
    
    def balance_class(self, custom_class: CustomClass) -> CustomClass:
        """Balance a custom class to ensure it follows D&D design principles."""
        prompt = self._format_prompt(
            "Balance this custom class",
            f"Class definition: {json.dumps(custom_class.to_dict())}",
            [
                "Appropriate power level compared to official classes",
                "Expected number of features per level",
                "Balanced saving throw proficiencies (usually one strong, one weak)",
                "Appropriate hit die size",
                "Resource scaling that matches class power"
            ]
        )
        
        try:
            response = self._get_llm_response(
                "balance_class",
                prompt,
                {"class_name": custom_class.name}
            )
            
            balanced_data = self._extract_json(response)
            
            if balanced_data:
                # Convert spellcasting type string to enum if needed
                if "spellcasting_type" in balanced_data:
                    try:
                        balanced_data["spellcasting_type"] = SpellcastingType(balanced_data["spellcasting_type"])
                    except ValueError:
                        balanced_data["spellcasting_type"] = custom_class.spellcasting_type
                
                # Create balanced class
                return CustomClass(**balanced_data)
        except Exception as e:
            logger.error(f"Error balancing class: {e}")
        
        # Return original if balancing fails
        return custom_class
    
    def generate_starting_equipment(self, class_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate starting equipment options for a class."""
        prompt = self._format_prompt(
            "Create starting equipment options",
            f"Class: {json.dumps(class_data)}",
            [
                "Equipment package options",
                "Consideration of class proficiencies",
                "Thematic equipment choices",
                "Balance comparable to official classes"
            ]
        )
        
        try:
            response = self._get_llm_response(
                "starting_equipment",
                prompt,
                {"class_name": class_data.get("name", "CustomClass")}
            )
            
            equipment_data = self._extract_json(response)
            
            if equipment_data:
                return equipment_data
        except Exception as e:
            logger.error(f"Error generating starting equipment: {e}")
        
        # Fallback
        return {
            "options": [
                {"items": ["A simple weapon", "Explorer's Pack", "10 darts"]},
                {"items": ["A martial weapon", "Dungeoneer's Pack", "Shield"]}
            ]
        }
    
    def suggest_multiclass_combinations(self, class_name: str) -> List[Dict[str, Any]]:
        """Suggest effective multiclass combinations for a class."""
        prompt = self._format_prompt(
            "Suggest multiclass combinations",
            f"Class: {class_name}",
            [
                "3-5 effective multiclass combinations",
                "Why each combination works well",
                "Recommended level split between classes",
                "Build focus and synergies"
            ]
        )
        
        try:
            response = self._get_llm_response(
                "multiclass_suggestions",
                prompt,
                {"class_name": class_name}
            )
            
            result = self._extract_json(response)
            if result and isinstance(result, list):
                return result
        except Exception as e:
            logger.error(f"Error generating multiclass suggestions: {e}")
        
        # Fallback
        return [
            {
                "classes": f"{class_name}/Fighter",
                "synergy": "Adds combat durability and fighting styles",
                "level_split": f"{class_name} X/Fighter 2",
                "build_focus": "Combat enhancement"
            },
            {
                "classes": f"{class_name}/Rogue",
                "synergy": "Adds skills and sneak attack",
                "level_split": f"{class_name} X/Rogue 3",
                "build_focus": "Skill utility and damage"
            }
        ]
    
    def adapt_character_from_media(
        self,
        character_name: str,
        source_media: str,
        power_level: str = "balanced",  # "low", "balanced", "high", "cinematic"
        setting_adaptation: str = "fantasy"  # "fantasy", "modern", "futuristic", etc.
    ) -> CustomClass:
        """
        Adapt a character from another media source (movies, comics, books) into a D&D class.
        
        Args:
            character_name: Name of the character to adapt (e.g., "Groot", "Batman")
            source_media: Source of the character (e.g., "Marvel", "DC Comics", "Tolkien")
            power_level: Desired power level in D&D terms
            setting_adaptation: Type of setting to adapt the character to
            
        Returns:
            CustomClass: A complete class based on the character
        """
        # Validate power level
        valid_power_levels = ["low", "balanced", "high", "cinematic"]
        if power_level.lower() not in valid_power_levels:
            power_level = "balanced"
        
        prompt = self._format_prompt(
            "Adapt a character from another media to a D&D class",
            f"Character: {character_name}\nSource: {source_media}\n"
            f"Power Level: {power_level}\nSetting: {setting_adaptation}",
            [
                "Complete D&D class definition based on character",
                "Preservation of core abilities and identity",
                "Class features that reflect signature character moments",
                "Resource systems or mechanics that capture the character's style"
            ]
        )
        
        try:
            response = self._get_llm_response(
                "adapt_character",
                prompt,
                {"character": character_name, "source": source_media, "power": power_level}
            )
            
            class_data = self._extract_json(response)
            
            if class_data:
                # Convert spellcasting type if present
                if "spellcasting_type" in class_data:
                    try:
                        class_data["spellcasting_type"] = SpellcastingType(class_data["spellcasting_type"])
                    except ValueError:
                        class_data["spellcasting_type"] = SpellcastingType.NONE
                        
                # Ensure complete class features
                if "class_features" not in class_data or not class_data["class_features"]:
                    class_data["class_features"] = {
                        "1": [{"name": f"{character_name}'s Essence", 
                              "description": f"You channel the essence of {character_name}."}]
                    }
                
                return CustomClass(**class_data)
        except Exception as e:
            logger.error(f"Error adapting character from media: {e}")
        
        # Fallback - simplified class based on character
        class_name = f"{character_name.split()[0]}borne"
        
        return CustomClass(
            name=class_name,
            description=f"A class inspired by {character_name} from {source_media}.",
            hit_die=10,
            primary_ability=["Strength", "Constitution"],
            saving_throw_proficiencies=["Strength", "Constitution"],
            armor_proficiencies=["Light", "Medium"],
            weapon_proficiencies=["Simple", "Martial"],
            class_features={
                "1": [{"name": f"{character_name}'s Legacy", 
                     "description": f"You channel the essence of {character_name}, gaining unique abilities."}]
            }
        )
    
    def create_non_humanoid_class(
        self,
        species_concept: str,  # e.g., "sentient tree", "living construct", "energy being"
        core_abilities: List[str],
        design_focus: str = "balanced"  # "thematic", "balanced", "mechanical"
    ) -> CustomClass:
        """
        Create a class designed specifically for non-humanoid characters.
        """
        # Validate design focus
        valid_focus_types = ["thematic", "balanced", "mechanical"]
        if design_focus.lower() not in valid_focus_types:
            design_focus = "balanced"
            
        abilities_text = "\n".join([f"- {ability}" for ability in core_abilities])
        
        prompt = self._format_prompt(
            "Create a class for a non-humanoid character",
            f"Non-humanoid Concept: {species_concept}\n"
            f"Core Abilities:\n{abilities_text}\n"
            f"Design Focus: {design_focus}",
            [
                "Class name and description",
                "Features that reflect non-humanoid physiology",
                "Creative solutions for equipment and traditional class elements",
                "Special movement, senses, or communication abilities"
            ]
        )
        
        try:
            response = self._get_llm_response(
                "non_humanoid_class",
                prompt,
                {"concept": species_concept, "focus": design_focus}
            )
            
            class_data = self._extract_json(response)
            
            if class_data:
                # Convert spellcasting type if present
                if "spellcasting_type" in class_data:
                    try:
                        class_data["spellcasting_type"] = SpellcastingType(class_data["spellcasting_type"])
                    except ValueError:
                        class_data["spellcasting_type"] = SpellcastingType.NONE
                
                # Convert saving_throws to saving_throw_proficiencies if necessary
                if "saving_throws" in class_data and "saving_throw_proficiencies" not in class_data:
                    class_data["saving_throw_proficiencies"] = class_data.pop("saving_throws")
                
                return CustomClass(**class_data)
        except Exception as e:
            logger.error(f"Error creating non-humanoid class: {e}")
        
        # Fallback
        concept_word = species_concept.split()[0].capitalize()
        class_name = f"{concept_word}form"
        
        # Generate basic class features from core abilities
        features = {}
        for i, ability in enumerate(core_abilities[:3]):  # Use up to first 3 abilities
            level = 1 if i == 0 else (i * 3)  # Place at levels 1, 3, 6
            if level not in features:
                features[str(level)] = []  # Use string keys for levels
            
            features[str(level)].append({
                "name": f"{ability.split()[0].title()} Manifestation",
                "description": f"You manifest the ability to {ability.lower()}."
            })
        
        # Ensure level 1 features exist
        if "1" not in features:
            features["1"] = [{
                "name": f"{concept_word} Nature",
                "description": f"Your {species_concept} physiology grants you unique capabilities."
            }]
        
        return CustomClass(
            name=class_name,
            description=f"A class designed for {species_concept} characters.",
            hit_die=8,
            primary_ability=["Constitution", "Wisdom"],
            saving_throw_proficiencies=["Constitution", "Wisdom"],
            class_features=features,
            armor_proficiencies=["None"],  # Non-humanoid might not use standard armor
            weapon_proficiencies=["Natural Weapons"]  # Non-humanoid might use natural weapons
        )
    
    # Additional methods for class generation follow the same pattern...
    # I've refactored the first several methods to show the pattern
    
    def _preprocess_class_data(self, class_data: Dict[str, Any]) -> Dict[str, Any]:
        """Standardize and clean up class data from LLM responses"""
        processed_data = class_data.copy()
        
        # Handle spellcasting_type conversion
        if "spellcasting_type" in processed_data and isinstance(processed_data["spellcasting_type"], str):
            try:
                processed_data["spellcasting_type"] = SpellcastingType(processed_data["spellcasting_type"])
            except ValueError:
                processed_data["spellcasting_type"] = SpellcastingType.NONE
        
        # Handle saving_throws naming convention
        if "saving_throws" in processed_data and "saving_throw_proficiencies" not in processed_data:
            processed_data["saving_throw_proficiencies"] = processed_data.pop("saving_throws")
        
        # Ensure class features are using string keys
        if "class_features" in processed_data:
            features = {}
            for level, level_features in processed_data["class_features"].items():
                features[str(level)] = level_features
            processed_data["class_features"] = features
        
        # Ensure primary_ability is a list
        if "primary_ability" in processed_data and isinstance(processed_data["primary_ability"], str):
            processed_data["primary_ability"] = [processed_data["primary_ability"]]
        
        return processed_data
    
    def standardize_class_data(self, class_data: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure class data follows a consistent format before CustomClass creation."""
        std_data = self._preprocess_class_data(class_data)
        
        # Ensure all required fields exist
        required_fields = ["name", "hit_die", "primary_ability", "saving_throw_proficiencies", "class_features"]
        for field in required_fields:
            if field not in std_data:
                if field == "name":
                    std_data[field] = "Custom Class"
                elif field == "hit_die":
                    std_data[field] = 8
                elif field == "primary_ability":
                    std_data[field] = ["Dexterity"]
                elif field == "saving_throw_proficiencies":
                    std_data[field] = ["Dexterity", "Constitution"]
                elif field == "class_features":
                    std_data[field] = {"1": [{"name": "Basic Feature", "description": "A basic class feature."}]}
        
        return std_data