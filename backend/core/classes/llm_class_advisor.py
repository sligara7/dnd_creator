import json
import re
import logging
from typing import Dict, List, Any, Optional, Union
from enum import Enum

from backend.core.services.ollama_service import OllamaService
from backend.core.classes.class_models import CustomClass, SpellcastingType

logger = logging.getLogger(__name__)

class LLMClassAdvisor:
    """Service for generating custom character classes using LLM"""
    
    def __init__(self, llm_service=None, system_context=None):
        """Initialize with optional custom LLM service"""
        self.llm_service = llm_service or OllamaService()
        self.system_context = system_context or "You are a D&D 5e (2024 rules) game designer specializing in balanced class creation."
    
    def _create_prompt(self, task: str, context: str, output_format: str = None) -> str:
        """Create a well-structured prompt for the LLM."""
        instructions = f"Based on the following information, {task}. Focus on game balance and D&D 5e design principles."
        
        if output_format:
            instructions += f" Return your response as {output_format}."
        else:
            instructions += " Return your response as valid JSON."
            
        prompt = f"{self.system_context}\n\n{instructions}\n\nInformation: {context}"
        return prompt
    
    def _extract_json(self, response: str) -> Union[Dict, List, None]:
        """Extract JSON from LLM response with robust handling."""
        try:
            # Try to find JSON object first
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
                
            # Then try to find JSON array
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
                
            # Try to extract JSON from code blocks
            code_block_match = re.search(r'```(?:json)?\s*(\{.*?\})```', response, re.DOTALL)
            if code_block_match:
                return json.loads(code_block_match.group(1))
                
            array_block_match = re.search(r'```(?:json)?\s*(\[.*?\])```', response, re.DOTALL)
            if array_block_match:
                return json.loads(array_block_match.group(1))
                
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
        
        return None
    
    def generate_class_concept(self, concept_description: str) -> Dict[str, Any]:
        """Generate a high-level class concept based on a description."""
        prompt = self._create_prompt(
            "create a D&D character class concept",
            f"Concept: {concept_description}\n\n"
            f"Generate a high-level concept for this class including: name, brief description, "
            f"playstyle summary, primary abilities, and a unique class mechanic."
        )
        
        try:
            response = self.llm_service.generate(prompt)
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
            task = "complete this partial class definition"
        else:
            context = f"Class concept: {concept}\n\n"
            context += "Create a complete, balanced character class based on this concept."
            task = "create a complete custom character class"
        
        prompt = self._create_prompt(
            task,
            context + "\n\n"
            "Include the following attributes in your JSON response:\n"
            "- name: The class name\n"
            "- description: Class description\n"
            "- hit_die: Hit die size (6, 8, 10, or 12)\n"
            "- primary_ability: Array of primary abilities\n"
            "- saving_throw_proficiencies: Array of saving throw proficiencies (max 2)\n"
            "- armor_proficiencies: Array of armor proficiencies\n"
            "- weapon_proficiencies: Array of weapon proficiencies\n"
            "- skill_proficiencies: Object with 'choose' (number) and 'from' (array of skills)\n"
            "- tool_proficiencies: Array of tool proficiencies\n"
            "- starting_equipment: Object with equipment options\n"
            "- class_features: Object mapping levels (1-20) to arrays of features\n"
            "- spellcasting_type: 'none', 'full', 'half', 'third', 'pact', or 'unique'\n"
            "- spellcasting_ability: Ability used for spellcasting (if applicable)\n"
            "- class_resources: Object describing class-specific resources\n"
            "- multiclass_requirements: Object mapping abilities to minimum scores\n"
            "- flavor_text: Object with flavor elements"
        )
        
        try:
            response = self.llm_service.generate(prompt)
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
        prompt = self._create_prompt(
            "create a balanced class feature",
            f"Class: {class_name}\nLevel: {level}\nConcept: {feature_concept}\n\n"
            f"Create a balanced and thematic class feature appropriate for this level. "
            f"It should fit the class theme and be comparable in power to official classes. "
            f"Return as JSON with 'name', 'description', 'mechanics', 'limitations' (e.g., uses per day)."
        )
        
        try:
            response = self.llm_service.generate(prompt)
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
        prompt = self._create_prompt(
            "create a character subclass",
            f"Base Class: {base_class_name}\nSubclass Concept: {subclass_concept}\n\n"
            f"Create a balanced and thematic subclass that specializes the base class according to the concept. "
            f"Include features at the appropriate levels for subclasses of this type. "
            f"Return as JSON with 'name', 'description', and 'features' (mapping levels to feature arrays)."
        )
        
        try:
            response = self.llm_service.generate(prompt)
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
        prompt = self._create_prompt(
            "balance this custom class",
            f"Class definition: {json.dumps(custom_class.to_dict())}\n\n"
            f"Review this class for balance issues according to D&D 5e (2024) design principles.\n"
            f"Check for:\n"
            f"1. Appropriate power level compared to official classes\n"
            f"2. Expected number of features per level\n"
            f"3. Balanced saving throw proficiencies (usually one strong, one weak)\n"
            f"4. Appropriate hit die size\n"
            f"5. Resource scaling that matches class power\n\n"
            f"Return the balanced version as JSON with the same structure."
        )
        
        try:
            response = self.llm_service.generate(prompt)
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
        prompt = self._create_prompt(
            "create starting equipment options",
            f"Class: {json.dumps(class_data)}\n\n"
            f"Create balanced and thematic starting equipment options for this class. "
            f"Consider the class's proficiencies, playstyle, and typical role in an adventuring party. "
            f"Return as JSON with 'options' array containing different equipment packages."
        )
        
        try:
            response = self.llm_service.generate(prompt)
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
        prompt = self._create_prompt(
            "suggest multiclass combinations",
            f"Class: {class_name}\n\n"
            f"Suggest 3-5 effective multiclass combinations with this class. "
            f"For each, explain why the combination works well, what levels to take in each class, "
            f"and what synergies to look for. Return as JSON array with objects containing "
            f"'classes', 'synergy', 'level_split', and 'build_focus' keys."
        )
        
        try:
            response = self.llm_service.generate(prompt)
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
        
        prompt = self._create_prompt(
            "adapt a character from another media to a D&D class",
            f"Character: {character_name}\nSource: {source_media}\n"
            f"Power Level: {power_level}\nSetting: {setting_adaptation}\n\n"
            f"Convert this character's abilities, themes, and identity into a complete D&D character class. "
            f"Preserve the core essence and playstyle while ensuring it's compatible with D&D mechanics. "
            f"Focus on what makes this character unique and translate that into class features.\n\n"
            f"Provide a complete class definition as JSON including name, description, hit_die, "
            f"primary_ability, saving_throws, proficiencies, class features for all levels, "
            f"and any special resource systems or mechanics needed."
        )
        
        try:
            response = self.llm_service.generate(prompt)
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
        
        Args:
            species_concept: The non-humanoid concept (e.g., "sentient tree" for Groot)
            core_abilities: Key abilities the non-humanoid possesses
            design_focus: Whether to prioritize theme, balance, or mechanical uniqueness
            
        Returns:
            CustomClass: A class tailored for the non-humanoid concept
        """
        # Validate design focus
        valid_focus_types = ["thematic", "balanced", "mechanical"]
        if design_focus.lower() not in valid_focus_types:
            design_focus = "balanced"
            
        abilities_text = "\n".join([f"- {ability}" for ability in core_abilities])
        
        prompt = self._create_prompt(
            "create a class for a non-humanoid character",
            f"Non-humanoid Concept: {species_concept}\n"
            f"Core Abilities:\n{abilities_text}\n"
            f"Design Focus: {design_focus}\n\n"
            f"Create a class that embraces the unique nature of this non-humanoid concept. "
            f"Incorporate features that reflect the physical and metaphysical realities of such a being. "
            f"Include creative solutions for equipment, spellcasting, and other traditional class elements.\n\n"
            f"Provide a complete class definition as JSON including name, description, hit_die, "
            f"primary_ability, saving_throws, proficiencies, class features for all levels, "
            f"and any special resource systems or mechanics needed to represent this non-humanoid character."
        )
        
        try:
            response = self.llm_service.generate(prompt)
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
    
    def generate_unique_resource_system(
        self,
        class_concept: str,
        thematic_element: str,  # e.g., "growth" for Groot, "technology" for Iron Man
        complexity: str = "moderate"  # "simple", "moderate", "complex"
    ) -> Dict[str, Any]:
        """
        Generate a custom resource system thematically tied to the character concept.
        
        Args:
            class_concept: Brief description of the class
            thematic_element: Core thematic element to base resources around
            complexity: Desired complexity of the resource system
            
        Returns:
            Dict containing the complete resource system definition
        """
        # Validate complexity
        valid_complexity = ["simple", "moderate", "complex"]
        if complexity.lower() not in valid_complexity:
            complexity = "moderate"
            
        prompt = self._create_prompt(
            "create a unique resource system",
            f"Class Concept: {class_concept}\n"
            f"Thematic Element: {thematic_element}\n"
            f"Complexity: {complexity}\n\n"
            f"Design a unique resource system that goes beyond standard D&D resources like spell slots. "
            f"Create something thematically appropriate that captures the essence of the concept. "
            f"Include how the resource is gained, spent, and tracked, along with any special mechanics.\n\n"
            f"Return a JSON object with:\n"
            f"- 'name': Name of the resource system\n"
            f"- 'resource_name': What the individual resources are called\n"
            f"- 'description': How the resource system works thematically\n"
            f"- 'mechanics': Object describing how resources are gained, spent, and tracked\n"
            f"- 'scaling': How the resource pool grows with level\n"
            f"- 'abilities': Array of special abilities that use this resource\n"
            f"- 'limitations': Any restrictions or weaknesses of the system\n"
            f"- 'tracking_method': How to track this resource on a character sheet"
        )
        
        try:
            response = self.llm_service.generate(prompt)
            resource_data = self._extract_json(response)
            
            if resource_data:
                return resource_data
        except Exception as e:
            logger.error(f"Error generating unique resource system: {e}")
        
        # Fallback
        resource_name = f"{thematic_element.capitalize()} Points"
        
        return {
            "name": f"{thematic_element.capitalize()} Power System",
            "resource_name": resource_name,
            "description": f"A resource system based on {thematic_element} that powers unique abilities.",
            "mechanics": {
                "starting_amount": "Equal to your level + your primary ability modifier",
                "recovery": "Regain all points after a long rest. Regain half (rounded down) after a short rest.",
                "spending": f"Different abilities cost different amounts of {resource_name}."
            },
            "scaling": "The pool increases with level and ability score improvements.",
            "abilities": [
                {
                    "name": f"Minor {thematic_element.capitalize()} Power",
                    "cost": "1 point",
                    "effect": "A minor effect related to the thematic element"
                },
                {
                    "name": f"Major {thematic_element.capitalize()} Power",
                    "cost": "3 points",
                    "effect": "A major effect related to the thematic element"
                }
            ],
            "limitations": f"Once you spend all your {resource_name}, you must rest to recover them.",
            "tracking_method": f"Add a {resource_name} tracker to your character sheet with checkboxes or counters."
        }
    
    def translate_powers_to_features(
        self,
        powers: List[str],
        source_genre: str,  # e.g., "superhero", "anime", "fantasy"
        power_scale: str = "balanced"  # "low", "balanced", "high", "legendary"
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Convert powers from other genres into balanced D&D class features.
        
        Args:
            powers: List of powers to convert
            source_genre: Original genre of the powers
            power_scale: Desired power level in D&D terms
            
        Returns:
            Dict mapping level numbers to lists of features
        """
        # Validate power scale
        valid_power_scales = ["low", "balanced", "high", "legendary"]
        if power_scale.lower() not in valid_power_scales:
            power_scale = "balanced"
            
        powers_text = "\n".join([f"- {power}" for power in powers])
        
        prompt = self._create_prompt(
            "translate powers to D&D class features",
            f"Powers:\n{powers_text}\n"
            f"Source Genre: {source_genre}\n"
            f"Power Scale: {power_scale}\n\n"
            f"Convert these powers from {source_genre} into balanced D&D class features. "
            f"Distribute them across appropriate class levels (1-20). "
            f"For each power, create one or more features that capture its essence while working within D&D's rules. "
            f"Include limitations, resource costs, and scaling that feels appropriate.\n\n"
            f"Return a JSON object mapping level numbers (as strings) to arrays of features, "
            f"where each feature has 'name', 'description', 'mechanics', and 'source_power' fields."
        )
        
        try:
            response = self.llm_service.generate(prompt)
            features_data = self._extract_json(response)
            
            if features_data:
                # If the response is already correctly formatted, return it
                if all(isinstance(key, str) and key.isdigit() for key in features_data.keys()):
                    return features_data
                
                # If we got an array of features instead of a level map, organize them by level
                if isinstance(features_data, list):
                    organized_features = {}
                    for feature in features_data:
                        if "level" in feature:
                            level = str(feature["level"])
                            if level not in organized_features:
                                organized_features[level] = []
                            feature_copy = feature.copy()
                            if "level" in feature_copy:
                                del feature_copy["level"]  # Remove redundant level field
                            organized_features[level].append(feature_copy)
                    
                    if organized_features:
                        return organized_features
        except Exception as e:
            logger.error(f"Error translating powers to features: {e}")
        
        # Fallback - distribute powers across levels
        features_by_level = {}
        
        # Determine power distribution based on power scale and number of powers
        level_distribution = []
        if power_scale == "low":
            level_distribution = [3, 6, 10, 14]  # Slower progression
        elif power_scale == "high":
            level_distribution = [1, 3, 5, 7]    # Faster progression
        elif power_scale == "legendary":
            level_distribution = [1, 2, 3, 5]    # Very fast progression
        else:  # balanced
            level_distribution = [1, 5, 9, 13]   # Standard progression
        
        # Distribute powers
        for i, power in enumerate(powers):
            # Determine which level to assign this power
            if i >= len(level_distribution):
                level = min(20, level_distribution[-1] + (i - len(level_distribution) + 1) * 2)
            else:
                level = level_distribution[i]
            
            level_str = str(level)
            if level_str not in features_by_level:
                features_by_level[level_str] = []
            
            power_name = power.strip().split()[0].title() if power.strip() else f"Power {i+1}"
            
            features_by_level[level_str].append({
                "name": f"{power_name}",
                "description": f"You can harness the power of {power.lower()}.",
                "mechanics": "As an action, you can use this power. You can use this feature once, and regain the ability to do so after a short or long rest.",
                "source_power": power
            })
        
        # Ensure we have at least one level 1 feature
        if "1" not in features_by_level:
            features_by_level["1"] = [{
                "name": f"{source_genre.capitalize()} Aptitude",
                "description": f"You have an innate connection to {source_genre} energies.",
                "mechanics": "You gain proficiency in one skill of your choice.",
                "source_power": "Innate talent"
            }]
            
        return features_by_level
    
    def create_hybrid_class(
        self,
        primary_concept: str,
        secondary_concept: str,
        balance_ratio: str = "60/40"  # e.g., "50/50", "70/30" - primary/secondary
    ) -> CustomClass:
        """
        Combine multiple class concepts into a coherent hybrid.
        
        Args:
            primary_concept: Main class concept
            secondary_concept: Secondary class concept to incorporate
            balance_ratio: How to balance features between concepts
            
        Returns:
            CustomClass: A hybrid class combining both concepts
        """
        prompt = self._create_prompt(
            "create a hybrid class",
            f"Primary Concept: {primary_concept}\n"
            f"Secondary Concept: {secondary_concept}\n"
            f"Balance Ratio: {balance_ratio}\n\n"
            f"Create a hybrid class that combines elements from both concepts into a cohesive whole. "
            f"Blend their mechanics, themes, and playstyles according to the specified ratio. "
            f"Ensure the result feels like a unified design rather than just features from two sources.\n\n"
            f"Provide a complete class definition as JSON including name, description, hit_die, "
            f"primary_ability, saving_throws, proficiencies, class features for all levels, "
            f"and any special resource systems or mechanics needed."
        )
        
        try:
            response = self.llm_service.generate(prompt)
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
            logger.error(f"Error creating hybrid class: {e}")
        
        # Fallback - create basic hybrid class
        primary_word = primary_concept.split()[0].capitalize()
        secondary_word = secondary_concept.split()[0].capitalize()
        class_name = f"{primary_word}{secondary_word}"
        
        return CustomClass(
            name=class_name,
            description=f"A hybrid class combining {primary_concept} and {secondary_concept}.",
            hit_die=8,
            primary_ability=["Dexterity", "Wisdom"],
            saving_throw_proficiencies=["Dexterity", "Wisdom"],
            armor_proficiencies=["Light"],
            weapon_proficiencies=["Simple"],
            class_features={
                "1": [
                    {"name": f"{primary_word} Affinity", 
                     "description": f"You gain abilities related to {primary_concept}."},
                    {"name": f"{secondary_word} Techniques", 
                     "description": f"You have learned techniques from {secondary_concept}."}
                ]
            }
        )
    
    def generate_cross_genre_mechanics(
        self,
        genre: str,  # e.g., "sci-fi", "western", "horror"
        mechanic_concept: str,
        adaptation_style: str = "translation"  # "translation", "fusion", "reimagining"
    ) -> List[Dict[str, Any]]:
        """
        Create mechanics that adapt concepts from other genres into D&D.
        
        Args:
            genre: Source genre for the mechanic
            mechanic_concept: Brief description of the mechanic
            adaptation_style: How to adapt the mechanic to D&D
            
        Returns:
            List of mechanics with descriptions and rules
        """
        # Validate adaptation style
        valid_styles = ["translation", "fusion", "reimagining"]
        if adaptation_style.lower() not in valid_styles:
            adaptation_style = "translation"
            
        prompt = self._create_prompt(
            "create cross-genre mechanics",
            f"Source Genre: {genre}\n"
            f"Mechanic Concept: {mechanic_concept}\n"
            f"Adaptation Style: {adaptation_style}\n\n"
            f"Create D&D mechanics that bring {genre} elements into the game. "
            f"Design rules that evoke the feeling of {mechanic_concept} while working within D&D's framework. "
            f"Focus on creating a {adaptation_style} that feels both authentic to the source and functional in D&D.\n\n"
            f"Return a JSON array of mechanics, each with:\n"
            f"- 'name': Name of the mechanic\n"
            f"- 'description': Thematic description\n"
            f"- 'rules': How it works mechanically\n"
            f"- 'integration': How it integrates with existing D&D rules\n"
            f"- 'examples': 2-3 examples of the mechanic in play\n"
            f"- 'variations': Different ways this mechanic could be implemented"
        )
        
        try:
            response = self.llm_service.generate(prompt)
            mechanics = self._extract_json(response)
            
            if mechanics and isinstance(mechanics, list):
                return mechanics
            if mechanics and isinstance(mechanics, dict) and "mechanics" in mechanics:
                return mechanics["mechanics"]
            if mechanics:
                return [mechanics]  # Convert single mechanic to list
        except Exception as e:
            logger.error(f"Error generating cross-genre mechanics: {e}")
        
        # Fallback - create basic mechanics
        return [{
            "name": f"{genre.capitalize()} {mechanic_concept.split()[0].title()}",
            "description": f"This mechanic adapts {mechanic_concept} from {genre} to D&D.",
            "rules": "When using this mechanic, roll a d20 and add your proficiency bonus plus your relevant ability modifier.",
            "integration": "This mechanic is used as an action in combat or as part of skill checks in exploration.",
            "examples": [
                f"Using {mechanic_concept} to overcome an obstacle.",
                f"Applying {mechanic_concept} in a social interaction."
            ],
            "variations": [
                "Basic version: Usable once per long rest.",
                "Advanced version: Costs a resource point but is more powerful."
            ]
        }]
    
    def generate_transformations(
        self,
        base_form: str,  # e.g., "human", "elf", "sentient tree"
        transformation_triggers: List[str],
        transformation_themes: List[str],  # e.g., ["growth", "adaptation"] for Groot
        power_progression: str = "scaling"  # "static", "scaling", "situational"
    ) -> Dict[str, Any]:
        """
        Create transformation mechanics for shape-shifting or form-changing characters.
        
        Args:
            base_form: The character's default form
            transformation_triggers: What causes transformations
            transformation_themes: Thematic elements of transformations
            power_progression: How transformations scale with level
            
        Returns:
            Dict containing transformation mechanics and rules
        """
        # Validate power progression
        valid_progressions = ["static", "scaling", "situational"]
        if power_progression.lower() not in valid_progressions:
            power_progression = "scaling"
            
        triggers_text = "\n".join([f"- {trigger}" for trigger in transformation_triggers])
        themes_text = "\n".join([f"- {theme}" for theme in transformation_themes])
        
        prompt = self._create_prompt(
            "create transformation mechanics",
            f"Base Form: {base_form}\n"
            f"Transformation Triggers:\n{triggers_text}\n"
            f"Transformation Themes:\n{themes_text}\n"
            f"Power Progression: {power_progression}\n\n"
            f"Design transformation mechanics that enable characters to change forms or states. "
            f"Create a system that balances power with limitations and costs. "
            f"Include rules for triggering, maintaining, and ending transformations. "
            f"Detail how transformations affect abilities, statistics, and capabilities.\n\n"
            f"Return a JSON object with:\n"
            f"- 'name': Name of the transformation system\n"
            f"- 'description': How transformations work thematically\n"
            f"- 'base_form': Description of the default state\n"
            f"- 'transformation_forms': Array of different forms/transformations\n"
            f"- 'activation': How transformations are triggered\n"
            f"- 'duration': How long transformations last\n"
            f"- 'limitations': Costs or restrictions on transformations\n"
            f"- 'progression': How transformations improve with level\n"
            f"- 'mechanics': Detailed game rules for transformations"
        )
        
        try:
            response = self.llm_service.generate(prompt)
            transformation_data = self._extract_json(response)
            
            if transformation_data:
                return transformation_data
        except Exception as e:
            logger.error(f"Error generating transformation mechanics: {e}")
        
        # Fallback - basic transformation system
        theme_name = transformation_themes[0].capitalize() if transformation_themes else "Adaptive"
        trigger_name = transformation_triggers[0].capitalize() if transformation_triggers else "Willpower"
        
        return {
            "name": f"{theme_name} Transformation",
            "description": f"A transformation system based on {', '.join(transformation_themes)}.",
            "base_form": f"In your base form, you appear as a {base_form}.",
            "transformation_forms": [
                {
                    "name": f"{theme_name} Form",
                    "description": f"Your body transforms, emphasizing {transformation_themes[0] if transformation_themes else 'adaptation'}.",
                    "benefits": ["Increased physical capabilities", "Special abilities related to the transformation theme"],
                    "drawbacks": ["Limited duration", "Recovery period after use"]
                }
            ],
            "activation": f"You can transform as an action when {transformation_triggers[0] if transformation_triggers else 'you choose to do so'}.",
            "duration": "The transformation lasts for 1 minute, or until you end it as a bonus action.",
            "limitations": "After transforming, you cannot do so again until you complete a short or long rest.",
            "progression": {
                "tier1": "At levels 1-5, basic transformation with limited capabilities.",
                "tier2": "At levels 6-10, improved transformation with enhanced abilities.",
                "tier3": "At levels 11+, mastered transformation with powerful capabilities."
            },
            "mechanics": "While transformed, you gain +2 to Strength and Constitution, and your size increases by one category if possible."
        }
    
    def adapt_iconic_abilities(
        self,
        character_name: str,
        source_media: str,
        iconic_abilities: List[str],
        adaptation_challenge: str = "standard"  # "simple", "standard", "complex"
    ) -> Dict[str, Any]:
        """
        Adapt specific iconic abilities from characters in other media.
        Perfect for signature moves like Groot's limb extension or "I am Groot" communication.
        
        Args:
            character_name: Name of the character
            source_media: Source of the character
            iconic_abilities: List of specific signature abilities to adapt
            adaptation_challenge: Complexity of adapting these abilities
            
        Returns:
            Dict containing adaptations of the iconic abilities
        """
        # Validate adaptation challenge
        valid_challenges = ["simple", "standard", "complex"]
        if adaptation_challenge.lower() not in valid_challenges:
            adaptation_challenge = "standard"
            
        abilities_text = "\n".join([f"- {ability}" for ability in iconic_abilities])
        
        prompt = self._create_prompt(
            "adapt iconic character abilities",
            f"Character: {character_name}\n"
            f"Source: {source_media}\n"
            f"Iconic Abilities:\n{abilities_text}\n"
            f"Adaptation Challenge: {adaptation_challenge}\n\n"
            f"Create D&D mechanics that faithfully adapt these iconic abilities. "
            f"Preserve what makes them recognizable while ensuring they work within D&D's rules. "
            f"For each ability, provide multiple options for implementation at different power levels.\n\n"
            f"Return a JSON object with the following structure:\n"
            f"- 'abilities': Array of ability objects, each containing:\n"
            f"  - 'original_ability': Name of the original ability\n"
            f"  - 'description': Brief description of how the ability works in source material\n"
            f"  - 'adaptations': Array of implementation options with:\n"
            f"    - 'name': Feature name\n"
            f"    - 'power_level': 'low', 'medium', or 'high'\n"
            f"    - 'mechanics': How it works in D&D terms\n"
            f"    - 'limitations': Restrictions, costs, or cooldowns\n"
            f"    - 'scaling': How it improves with character level"
        )
        
        try:
            response = self.llm_service.generate(prompt)
            adaptations = self._extract_json(response)
            
            if adaptations and "abilities" in adaptations:
                return adaptations
            elif adaptations:
                # Handle case where LLM returned different but valid structure
                return {"abilities": adaptations if isinstance(adaptations, list) else [adaptations]}
                
        except Exception as e:
            logger.error(f"Error adapting iconic abilities: {e}")
        
        # Fallback - create basic adaptations
        fallback_abilities = []
        for ability in iconic_abilities:
            ability_name = ability.split()[0].title() if ability else "Ability"
            fallback_abilities.append({
                "original_ability": ability,
                "description": f"This is {character_name}'s signature ability from {source_media}",
                "adaptations": [
                    {
                        "name": f"{ability_name} (Basic)",
                        "power_level": "low",
                        "mechanics": f"As an action, you can use a simplified version of {ability}",
                        "limitations": "You can use this ability a number of times equal to your proficiency bonus per long rest",
                        "scaling": "The effect becomes more powerful at 5th, 11th, and 17th level"
                    },
                    {
                        "name": f"{ability_name} (Advanced)",
                        "power_level": "medium",
                        "mechanics": f"You can use {ability} with greater flexibility and power",
                        "limitations": "Costs a resource point from your class resource pool",
                        "scaling": "Additional effects become available at higher levels"
                    }
                ]
            })
        
        return {"abilities": fallback_abilities}
    
    def suggest_class_optimization(
        self,
        class_name: str,
        character_level: int,
        playstyle_focus: str = "balanced"  # "damage", "support", "control", "balanced"
    ) -> Dict[str, Any]:
        """
        Generate optimization suggestions for playing a specific class effectively.
        
        Args:
            class_name: Name of the class to optimize
            character_level: Current or target character level
            playstyle_focus: Desired playstyle emphasis
            
        Returns:
            Dict containing optimization recommendations
        """
        # Validate level
        character_level = max(1, min(20, character_level))
        
        # Validate playstyle focus
        valid_playstyles = ["damage", "support", "control", "balanced", "utility", "tanking"]
        if playstyle_focus.lower() not in valid_playstyles:
            playstyle_focus = "balanced"
        
        prompt = self._create_prompt(
            "optimize a character class",
            f"Class: {class_name}\n"
            f"Level: {character_level}\n"
            f"Playstyle Focus: {playstyle_focus}\n\n"
            f"Provide comprehensive optimization advice for playing this class effectively. "
            f"Focus on the specified playstyle and character level. "
            f"Include ability score priorities, feat recommendations, multiclass options, "
            f"combat tactics, and resource management.\n\n"
            f"Return a JSON object with:\n"
            f"- 'ability_scores': Recommended ability score priorities\n"
            f"- 'feats': Recommended feats with explanations\n"
            f"- 'multiclass': Optional multiclass recommendations\n"
            f"- 'combat_tactics': Effective combat strategies\n"
            f"- 'resource_management': How to manage class resources\n"
            f"- 'recommended_subclasses': Best subclasses for this playstyle\n"
            f"- 'equipment': Recommended items and gear\n"
            f"- 'common_mistakes': Pitfalls to avoid"
        )
        
        try:
            response = self.llm_service.generate(prompt)
            optimization_data = self._extract_json(response)
            
            if optimization_data:
                return optimization_data
        except Exception as e:
            logger.error(f"Error suggesting class optimization: {e}")
        
        # Fallback
        return {
            "ability_scores": ["Primary: Depends on class", "Secondary: Constitution for survivability"],
            "feats": ["Recommended feats would be listed here"],
            "multiclass": ["Potential multiclass options would be suggested"],
            "combat_tactics": ["Effective combat strategies would be detailed"],
            "resource_management": "Tips for managing class resources efficiently",
            "recommended_subclasses": ["Suitable subclasses would be listed"],
            "equipment": ["Recommended items would be suggested"],
            "common_mistakes": ["Common pitfalls would be listed"]
        }
    
    def create_themed_subclass_collection(
        self,
        theme: str,  # e.g., "elementalist", "shadow magic", "cosmic power"
        base_classes: List[str] = None,  # list of class names, or None for all core classes
        design_approach: str = "unified"  # "unified", "specialized", "experimental"
    ) -> Dict[str, Dict[str, Any]]:
        """
        Create a collection of thematically linked subclasses for different base classes.
        
        Args:
            theme: The unifying theme for all subclasses
            base_classes: Which classes to create subclasses for (or None for standard classes)
            design_approach: How to approach the design of these subclasses
            
        Returns:
            Dict mapping class names to subclass definitions
        """
        # Use standard classes if none provided
        if not base_classes or not isinstance(base_classes, list) or len(base_classes) == 0:
            base_classes = ["Fighter", "Wizard", "Rogue", "Cleric"]
        
        # Validate design approach
        valid_approaches = ["unified", "specialized", "experimental"]
        if design_approach.lower() not in valid_approaches:
            design_approach = "unified"
            
        classes_text = ", ".join(base_classes)
        
        prompt = self._create_prompt(
            "create a themed subclass collection",
            f"Theme: {theme}\n"
            f"Base Classes: {classes_text}\n"
            f"Design Approach: {design_approach}\n\n"
            f"Create a collection of subclasses for the specified base classes, all united by the common theme. "
            f"Each subclass should feel unique to its base class while clearly belonging to the same theme. "
            f"If using a unified approach, ensure shared mechanics across subclasses. "
            f"If specialized, focus on what makes each class unique within the theme. "
            f"If experimental, push boundaries of traditional design within theme constraints.\n\n"
            f"Return a JSON object mapping each base class name to its subclass definition, "
            f"where each subclass has 'name', 'description', and 'features' (mapping levels to feature arrays). "
            f"Include a 'theme_mechanics' field explaining any shared mechanics."
        )
        
        try:
            response = self.llm_service.generate(prompt)
            subclass_collection = self._extract_json(response)
            
            if subclass_collection:
                return subclass_collection
        except Exception as e:
            logger.error(f"Error creating themed subclass collection: {e}")
        
        # Fallback - create basic subclasses
        collection = {}
        theme_word = theme.split()[0].capitalize()
        
        for base_class in base_classes[:4]:  # Limit to first 4 classes in case of long list
            collection[base_class] = {
                "name": f"{theme_word} {base_class}",
                "description": f"A {base_class} subclass focused on {theme}.",
                "features": {
                    "3": [{"name": f"{theme_word} Power", "description": f"You gain abilities related to {theme}."}]
                }
            }
        
        collection["theme_mechanics"] = f"All subclasses share a connection to {theme}, manifesting differently for each class."
        
        return collection
    
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