from typing import Dict, List, Optional, Union, Any, Set
import json
import re
import uuid
from enum import Enum

from backend.core.classes.abstract_character_class import AbstractCharacterClass
from backend.core.classes.llm_class_advisor import LLMClassAdvisor

class SpellcastingType(Enum):
    """Types of spellcasting a class might have"""
    NONE = "none"
    FULL = "full"       # Like Wizard, Cleric (levels 1-9)
    HALF = "half"       # Like Ranger, Paladin (levels 1-5)
    THIRD = "third"     # Like Eldritch Knight, Arcane Trickster (levels 1-4)
    PACT = "pact"       # Like Warlock (unique system)
    UNIQUE = "unique"   # Custom spellcasting system

class ClassResource(Enum):
    """Common class resource types"""
    NONE = "none"
    SPELL_SLOTS = "spell_slots"
    SORCERY_POINTS = "sorcery_points"
    KI = "ki"
    RAGE = "rage"
    SUPERIORITY_DICE = "superiority_dice"
    BARDIC_INSPIRATION = "bardic_inspiration"
    WILD_SHAPE = "wild_shape"
    CHANNEL_DIVINITY = "channel_divinity"
    INFUSIONS = "infusions"
    PACT_MAGIC = "pact_magic"
    LAY_ON_HANDS = "lay_on_hands"
    CUSTOM = "custom"  # For completely custom resources

class CustomClass:
    """
    Custom character class implementation with full LLM integration.
    
    Allows creation of brand new classes with:
    1. Manual specification of all attributes
    2. Semi-automatic creation with some attributes specified and others generated
    3. Fully automatic generation based on a concept description
    """
    
    def __init__(self,
                 name: str,
                 description: str = "",
                 hit_die: int = 8,
                 primary_ability: List[str] = None,
                 saving_throw_proficiencies: List[str] = None,
                 armor_proficiencies: List[str] = None,
                 weapon_proficiencies: List[str] = None,
                 skill_proficiencies: Dict[str, int] = None,
                 tool_proficiencies: List[str] = None,
                 starting_equipment: Dict[str, Any] = None,
                 class_features: Dict[int, List[Dict[str, Any]]] = None,
                 subclasses: List[Dict[str, Any]] = None,
                 spellcasting_type: SpellcastingType = SpellcastingType.NONE,
                 spellcasting_ability: str = None,
                 class_resources: Dict[str, Dict[str, Any]] = None,
                 multiclass_requirements: Dict[str, int] = None,
                 suggested_builds: List[Dict[str, Any]] = None,
                 flavor_text: Dict[str, str] = None,
                 custom_id: str = None):
        """
        Initialize a custom character class.
        
        Args:
            name: Class name
            description: Class description
            hit_die: Hit die size (d6, d8, d10, d12)
            primary_ability: List of primary abilities for the class
            saving_throw_proficiencies: List of saving throw proficiencies
            armor_proficiencies: List of armor proficiencies
            weapon_proficiencies: List of weapon proficiencies
            skill_proficiencies: Dict of skill proficiencies and how many to choose
            tool_proficiencies: List of tool proficiencies
            starting_equipment: Dict of starting equipment options
            class_features: Dict mapping levels to lists of features
            subclasses: List of subclass options
            spellcasting_type: Type of spellcasting (if any)
            spellcasting_ability: Ability used for spellcasting (if applicable)
            class_resources: Class resources (ki points, rage, channel divinity, etc.)
            multiclass_requirements: Ability score requirements for multiclassing
            suggested_builds: Suggested character builds
            flavor_text: Flavor text for roleplaying the class
            custom_id: Unique identifier for the class
        """
        self.name = name
        self.description = description
        self.hit_die = hit_die
        self.primary_ability = primary_ability or ["Strength"]
        self.saving_throw_proficiencies = saving_throw_proficiencies or ["Strength", "Constitution"]
        self.armor_proficiencies = armor_proficiencies or []
        self.weapon_proficiencies = weapon_proficiencies or ["Simple"]
        self.skill_proficiencies = skill_proficiencies or {"choose": 2, "from": ["Athletics", "Arcana", "History"]}
        self.tool_proficiencies = tool_proficiencies or []
        self.starting_equipment = starting_equipment or {"options": [{"items": ["Quarterstaff", "Explorer's Pack"]}]}
        self.class_features = class_features or {1: [{"name": "First Feature", "description": "Your first class feature."}]}
        self.subclasses = subclasses or []
        self.spellcasting_type = spellcasting_type
        self.spellcasting_ability = spellcasting_ability
        self.class_resources = class_resources or {}
        self.multiclass_requirements = multiclass_requirements or {}
        self.suggested_builds = suggested_builds or []
        self.flavor_text = flavor_text or {"combat_style": "Versatile", "personality": "Adaptable"}
        self.custom_id = custom_id or str(uuid.uuid4())
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
            "spellcasting_type": self.spellcasting_type.value,
            "spellcasting_ability": self.spellcasting_ability,
            "class_resources": self.class_resources,
            "multiclass_requirements": self.multiclass_requirements,
            "suggested_builds": self.suggested_builds,
            "flavor_text": self.flavor_text,
            "custom_id": self.custom_id,
            "source": self.source
        }



class CharacterClassManager:
    
    """
    Manager for both standard and custom character classes.
    
    This class provides a unified interface for working with standard D&D classes
    and completely custom classes, with full LLM assistance.
    """
    
    # Core classes from the 2024 Player's Handbook
    CORE_CLASSES = [
        "Artificer", "Barbarian", "Bard", "Cleric", "Druid", 
        "Fighter", "Monk", "Paladin", "Ranger", "Rogue",
        "Sorcerer", "Warlock", "Wizard"
    ]
    
    def __init__(self, llm_service=None):
        """Initialize the class manager."""
        self.llm_service = llm_service or OllamaService()
        self.llm_creator = LLMClassAdvisor(self.llm_service)
        self.standard_classes = {}  # Will hold standard class instances
        self.custom_classes = {}  # Will hold custom class instances by ID
        
        # Initialize standard classes
        self._initialize_standard_classes()
    
    def _initialize_standard_classes(self):
        """Initialize standard classes from core rules."""
        # This would normally load data from a database or file
        # For this example, we'll just create placeholder entries
        for class_name in self.CORE_CLASSES:
            self.standard_classes[class_name.lower()] = {
                "name": class_name,
                "source": "Player's Handbook",
                "description": f"Standard {class_name} class from the core rules."
                # Other properties would be loaded here
            }
    
    # === CORE CLASS METHODS ===
    
    def get_all_classes(self, filtered_by_concept: bool = False, 
                       character_concept: str = None) -> List[Dict[str, Any]]:
        """
        Get all available classes, optionally filtered by character concept.
        
        Args:
            filtered_by_concept: Whether to use LLM to recommend classes
            character_concept: Character concept to filter/recommend by
            
        Returns:
            List[Dict[str, Any]]: List of class data
        """
        # Get all standard classes
        standard_class_data = list(self.standard_classes.values())
        
        # Get all custom classes
        custom_class_data = [cls.to_dict() for cls in self.custom_classes.values()]
        
        # Combine lists
        all_classes = standard_class_data + custom_class_data
        
        # If no filtering, return all
        if not filtered_by_concept or not character_concept:
            return all_classes
        
        # Use LLM to recommend classes based on character concept
        return self._recommend_classes_by_concept(all_classes, character_concept)
    
    def _recommend_classes_by_concept(self, class_list: List[Dict[str, Any]], 
                                    character_concept: str) -> List[Dict[str, Any]]:
        """
        Use LLM to recommend classes based on character concept.
        
        Args:
            class_list: List of all available classes
            character_concept: Character concept description
            
        Returns:
            List[Dict[str, Any]]: Filtered and ranked class list with recommendations
        """
        class_names = [c["name"] for c in class_list]
        class_str = ", ".join(class_names)
        
        prompt = self.llm_creator._create_prompt(
            "recommend classes for this character concept",
            f"Character concept: {character_concept}\n"
            f"Available classes: {class_str}\n\n"
            f"Recommend the top 3-5 classes that would best fit this character concept. "
            f"For each recommendation, provide a brief explanation of why it fits. "
            f"Return as JSON array with 'name' and 'reason' keys."
        )
        
        try:
            response = self.llm_service.generate(prompt)
            
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                recommendations = json.loads(json_match.group(0))
                
                # Filter class list to keep only recommended ones
                recommended_names = [r["name"] for r in recommendations]
                filtered_list = [
                    {**cls, "recommendation_reason": next(
                        (r["reason"] for r in recommendations if r["name"] == cls["name"]),
                        None
                    )}
                    for cls in class_list 
                    if cls["name"] in recommended_names
                ]
                
                return filtered_list
        except Exception as e:
            print(f"Error getting class recommendations: {e}")
        
        # Return unfiltered list if LLM fails
        return class_list
    
    def get_class_details(self, class_name: str,
                        include_roleplay_guidance: bool = False) -> Dict[str, Any]:
        """
        Get detailed information about a class.
        
        Args:
            class_name: Name of the class
            include_roleplay_guidance: Whether to include LLM roleplay guidance
            
        Returns:
            Dict[str, Any]: Class details
        """
        # Find the class
        class_key = class_name.lower()
        if class_key in self.standard_classes:
            details = self.standard_classes[class_key].copy()
        else:
            # Look for custom classes
            for custom_class in self.custom_classes.values():
                if custom_class.name.lower() == class_name.lower():
                    details = custom_class.to_dict()
                    break
            else:
                return None  # Class not found
        
        # Add roleplay guidance if requested
        if include_roleplay_guidance:
            roleplay_guidance = self._generate_roleplay_guidance(class_name, details)
            details["roleplay_guidance"] = roleplay_guidance
            
        return details
    
    def _generate_roleplay_guidance(self, class_name: str, class_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate roleplay guidance for a class using LLM.
        
        Args:
            class_name: Name of the class
            class_details: Class details dictionary
            
        Returns:
            Dict[str, Any]: Roleplay guidance
        """
        description = class_details.get("description", f"A {class_name} class")
        
        prompt = self.llm_creator._create_prompt(
            "create roleplay guidance for this class",
            f"Class: {class_name}\nDescription: {description}\n\n"
            f"Provide roleplay guidance for this class including: personality suggestions, "
            f"background ideas, character quirks, roleplaying challenges, and RP dynamics with other classes. "
            f"Return as JSON with appropriate keys."
        )
        
        try:
            response = self.llm_service.generate(prompt)
            guidance_data = self.llm_creator._extract_json(response)
            
            if guidance_data:
                return guidance_data
        except Exception as e:
            print(f"Error generating roleplay guidance: {e}")
        
        # Fallback
        return {
            "personality_suggestions": [
                f"Consider how your {class_name}'s abilities shape their worldview",
                "Think about what motivated them to pursue this path"
            ],
            "background_ideas": [
                f"A background that complements the {class_name}'s skills",
                f"A background that contrasts with typical {class_name} stereotypes"
            ],
            "character_quirks": [
                f"A unique habit related to their {class_name} abilities",
                "A distinctive way they approach problems"
            ]
        }
    
    def get_class_features(self, class_name: str, level: int) -> List[Dict[str, Any]]:
        """
        Get features available to a class at a given level.
        
        Args:
            class_name: Name of the class
            level: Character level
            
        Returns:
            List[Dict[str, Any]]: List of features
        """
        # For standard classes, we would load this from a data source
        # For custom classes, we access the stored features
        
        class_key = class_name.lower()
        if class_key in self.standard_classes:
            # Placeholder implementation for standard classes
            return [{"name": f"{class_name} Feature {level}", "description": "Feature description"}]
        
        # Look for custom classes
        for custom_class in self.custom_classes.values():
            if custom_class.name.lower() == class_name.lower():
                # Return features for this level
                return custom_class.class_features.get(level, [])
        
        return []  # No features found
    
    def get_class_progression(self, class_name: str) -> Dict[int, Dict[str, Any]]:
        """
        Get level progression table for a class.
        
        Args:
            class_name: Name of the class
            
        Returns:
            Dict[int, Dict[str, Any]]: Progression table
        """
        # For standard classes, we would load this from a data source
        # For custom classes, we generate a progression from the features
        
        class_key = class_name.lower()
        if class_key in self.standard_classes:
            # Placeholder progression for standard classes
            return {level: {"features": [f"Level {level} feature"]} for level in range(1, 21)}
        
        # Look for custom classes
        for custom_class in self.custom_classes.values():
            if custom_class.name.lower() == class_name.lower():
                # Generate progression from features
                progression = {}
                for level in range(1, 21):
                    progression[level] = {
                        "features": [f["name"] for f in custom_class.class_features.get(level, [])],
                        "resources": self._get_resource_progression(custom_class, level)
                    }
                return progression
        
        return {}  # No progression found
    
    def _get_resource_progression(self, custom_class: CustomClass, level: int) -> Dict[str, Any]:
        """
        Calculate resource progression for a custom class at a specific level.
        
        Args:
            custom_class: The custom class
            level: Character level
            
        Returns:
            Dict[str, Any]: Resource values at this level
        """
        resources = {}
        
        # Process each class resource
        for resource_name, resource_data in custom_class.class_resources.items():
            if "progression" in resource_data:
                # Direct progression list
                if isinstance(resource_data["progression"], list) and len(resource_data["progression"]) >= level:
                    resources[resource_name] = resource_data["progression"][level-1]
                # Formula-based progression
                elif "formula" in resource_data:
                    formula = resource_data["formula"]
                    # Simple placeholder formula processing
                    if "level" in formula:
                        value = eval(formula.replace("level", str(level)))
                        resources[resource_name] = value
        
        # Handle spellcasting progression
        if custom_class.spellcasting_type != SpellcastingType.NONE:
            spell_slots = self._calculate_spell_slots(custom_class.spellcasting_type, level)
            if spell_slots:
                resources["spell_slots"] = spell_slots
        
        return resources
    
    def _calculate_spell_slots(self, spellcasting_type: SpellcastingType, level: int) -> Dict[int, int]:
        """
        Calculate spell slots for a given spellcasting type and level.
        
        Args:
            spellcasting_type: Type of spellcasting
            level: Character level
            
        Returns:
            Dict[int, int]: Spell slots by spell level
        """
        # Simplified spell slot calculation
        if spellcasting_type == SpellcastingType.FULL:
            # Full caster progression (simplified)
            max_spell_level = min(9, (level + 1) // 2)
            slots = {1: 2}  # Start with 2 1st-level slots
            
            if level >= 3:
                slots[2] = 2
            if level >= 5:
                slots[3] = 2
            if level >= 7:
                slots[4] = 1
            if level >= 9:
                slots[5] = 1
            # And so on for higher levels...
            
            return slots
            
        elif spellcasting_type == SpellcastingType.HALF:
            # Half caster progression (simplified)
            max_spell_level = min(5, (level + 1) // 4)
            if level < 2:
                return {}  # No spell slots at level 1
                
            slots = {1: 2}  # Start with 2 1st-level slots at level 2
            
            if level >= 5:
                slots[2] = 2
            if level >= 9:
                slots[3] = 2
            # And so on...
            
            return slots
        
        # Add other progressions as needed
        
        return {}  # No spell slots
    
    def get_saving_throw_proficiencies(self, class_name: str) -> List[str]:
        """
        Get saving throw proficiencies for a class.
        
        Args:
            class_name: Name of the class
            
        Returns:
            List[str]: List of saving throw proficiencies
        """
        class_key = class_name.lower()
        if class_key in self.standard_classes:
            # Placeholder for standard classes
            return ["Strength", "Constitution"]
        
        # Look for custom classes
        for custom_class in self.custom_classes.values():
            if custom_class.name.lower() == class_name.lower():
                return custom_class.saving_throw_proficiencies
        
        return []  # No proficiencies found
    
    def get_starting_equipment(self, class_name: str) -> Dict[str, Any]:
        """
        Get starting equipment options for a class.
        
        Args:
            class_name: Name of the class
            
        Returns:
            Dict[str, Any]: Starting equipment options
        """
        class_key = class_name.lower()
        if class_key in self.standard_classes:
            # Placeholder for standard classes
            return {"options": [{"items": ["Basic equipment"]}]}
        
        # Look for custom classes
        for custom_class in self.custom_classes.values():
            if custom_class.name.lower() == class_name.lower():
                return custom_class.starting_equipment
        
        return {"options": []}  # No equipment found
    
    # === CUSTOM CLASS CREATION AND MANAGEMENT ===
    
    def create_custom_class(self, class_data: Dict[str, Any]) -> CustomClass:
        """
        Create a custom class with the specified data.
        
        Args:
            class_data: Custom class definition (can be partial)
            
        Returns:
            CustomClass: New custom class instance
        """
        # If just a concept is provided, generate everything
        if "concept" in class_data and len(class_data) < 5:
            custom_class = self.create_class_from_concept(class_data["concept"])
        else:
            # Generate from partial data
            custom_class = self.llm_creator.generate_complete_class(partial_data=class_data)
            
        # Balance the class
        balanced_class = self.llm_creator.balance_class(custom_class)
        
        # Store the custom class
        self.custom_classes[balanced_class.custom_id] = balanced_class
        return balanced_class
    
    def create_class_from_concept(self, concept: str) -> CustomClass:
        """
        Create a complete class from a simple concept description.
        
        Args:
            concept: Brief description of the desired class
            
        Returns:
            CustomClass: Fully detailed class
        """
        custom_class = self.llm_creator.generate_complete_class(concept=concept)
        self.custom_classes[custom_class.custom_id] = custom_class
        return custom_class
    
    def add_feature_to_class(self, class_id: str, level: int, 
                           feature_concept: str) -> CustomClass:
        """
        Add a new feature to a custom class at the specified level.
        
        Args:
            class_id: ID of the custom class
            level: Level at which to add the feature
            feature_concept: Brief description of the feature
            
        Returns:
            CustomClass: Updated custom class with the new feature
        """
        if class_id not in self.custom_classes:
            raise ValueError(f"No custom class found with ID: {class_id}")
        
        custom_class = self.custom_classes[class_id]
        
        # Generate the new feature
        new_feature = self.llm_creator.generate_class_feature(
            custom_class.name, level, feature_concept
        )
        
        # Make a copy of the class with the new feature
        class_data = custom_class.to_dict()
        
        # Convert spellcasting type string to enum if needed
        if "spellcasting_type" in class_data:
            try:
                class_data["spellcasting_type"] = SpellcastingType(class_data["spellcasting_type"])
            except ValueError:
                class_data["spellcasting_type"] = custom_class.spellcasting_type
        
        # Add the new feature
        features = class_data.get("class_features", {})
        if str(level) not in features:
            features[str(level)] = []
        features[str(level)].append(new_feature)
        class_data["class_features"] = features
        
        # Generate new ID
        class_data["custom_id"] = None
        
        # Create and store updated class
        updated_class = CustomClass(**class_data)
        self.custom_classes[updated_class.custom_id] = updated_class
        
        return updated_class
    
    def add_subclass_to_class(self, class_id: str, 
                            subclass_concept: str) -> CustomClass:
        """
        Add a new subclass to a custom class.
        
        Args:
            class_id: ID of the custom class
            subclass_concept: Brief description of the subclass
            
        Returns:
            CustomClass: Updated custom class with the new subclass
        """
        if class_id not in self.custom_classes:
            raise ValueError(f"No custom class found with ID: {class_id}")
        
        custom_class = self.custom_classes[class_id]
        
        # Generate the new subclass
        new_subclass = self.llm_creator.generate_subclass(
            custom_class.name, subclass_concept
        )
        
        # Make a copy of the class with the new subclass
        class_data = custom_class.to_dict()
        
        # Convert spellcasting type string to enum if needed
        if "spellcasting_type" in class_data:
            try:
                class_data["spellcasting_type"] = SpellcastingType(class_data["spellcasting_type"])
            except ValueError:
                class_data["spellcasting_type"] = custom_class.spellcasting_type
        
        # Add the new subclass
        subclasses = class_data.get("subclasses", [])
        subclasses.append(new_subclass)
        class_data["subclasses"] = subclasses
        
        # Generate new ID
        class_data["custom_id"] = None
        
        # Create and store updated class
        updated_class = CustomClass(**class_data)
        self.custom_classes[updated_class.custom_id] = updated_class
        
        return updated_class
    
    def modify_class_resource(self, class_id: str, resource_name: str, 
                            resource_data: Dict[str, Any]) -> CustomClass:
        """
        Add or modify a class resource.
        
        Args:
            class_id: ID of the custom class
            resource_name: Name of the resource
            resource_data: Resource definition
            
        Returns:
            CustomClass: Updated custom class
        """
        if class_id not in self.custom_classes:
            raise ValueError(f"No custom class found with ID: {class_id}")
        
        custom_class = self.custom_classes[class_id]
        
        # Make a copy of the class with the modified resource
        class_data = custom_class.to_dict()
        
        # Convert spellcasting type string to enum if needed
        if "spellcasting_type" in class_data:
            try:
                class_data["spellcasting_type"] = SpellcastingType(class_data["spellcasting_type"])
            except ValueError:
                class_data["spellcasting_type"] = custom_class.spellcasting_type
        
        # Update the resource
        resources = class_data.get("class_resources", {})
        resources[resource_name] = resource_data
        class_data["class_resources"] = resources
        
        # Generate new ID
        class_data["custom_id"] = None
        
        # Create and store updated class
        updated_class = CustomClass(**class_data)
        self.custom_classes[updated_class.custom_id] = updated_class
        
        return updated_class
    
    def get_similar_official_classes(self, custom_class_id: str) -> List[Dict[str, Any]]:
        """
        Find official classes similar to a custom class.
        
        Args:
            custom_class_id: ID of the custom class
            
        Returns:
            List[Dict[str, Any]]: Similar official classes with similarity scores
        """
        if custom_class_id not in self.custom_classes:
            raise ValueError(f"No custom class found with ID: {custom_class_id}")
        
        custom_class = self.custom_classes[custom_class_id]
        
        prompt = self.llm_creator._create_prompt(
            "find similar official classes",
            f"Custom class: {json.dumps(custom_class.to_dict())}\n"
            f"Official classes: {', '.join(self.CORE_CLASSES)}\n\n"
            f"Find the 3 most similar official D&D classes to this custom class. "
            f"For each, explain the similarities and differences. "
            f"Return as JSON array with 'name', 'similarity_score' (1-10), and 'comparison' keys."
        )
        
        try:
            response = self.llm_service.generate(prompt)
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
        except Exception as e:
            print(f"Error finding similar classes: {e}")
        
        # Fallback
        return [
            {
                "name": self.CORE_CLASSES[0],
                "similarity_score": 7,
                "comparison": f"Similar to {custom_class.name} in core mechanics, but with different flavor."
            },
            {
                "name": self.CORE_CLASSES[1],
                "similarity_score": 5,
                "comparison": f"Some overlapping features with {custom_class.name}, but different focus."
            }
        ]



# Example usage
# def demonstrate_custom_class_creation():
#     """Demonstrate the capabilities of the CustomClass system"""
#     manager = CharacterClassManager()
    
#     print("=== CREATING CUSTOM CLASSES ===")
    
#     # Create from just a concept
#     magic_hunter = manager.create_class_from_concept(
#         "A magic hunter who uses arcane knowledge to track down and counter spellcasters"
#     )
#     print(f"Created class: {magic_hunter.name}")
    
#     # Create with partial specification
#     elemental_dancer = manager.create_custom_class({
#         "name": "Elemental Dancer",
#         "concept": "A martial artist who channels elemental energy through graceful movements",
#         "hit_die": 8,
#         "primary_ability": ["Dexterity", "Wisdom"],
#         "saving_throw_proficiencies": ["Dexterity", "Wisdom"]
#     })
#     print(f"Created class with partial spec: {elemental_dancer.name}")
    
#     # Add a feature
#     updated_dancer = manager.add_feature_to_class(
#         elemental_dancer.custom_id,
#         3,
#         "A technique that lets them create a whirling sphere of elemental energy"
#     )
#     print(f"Added feature to level 3 of {updated_dancer.name}")
    
#     # Add a subclass
#     with_subclass = manager.add_subclass_to_class(
#         updated_dancer.custom_id, 
#         "A dancer who specializes in fire element techniques"
#     )
#     print(f"Added subclass to {with_subclass.name}")
    
#     print("\n=== CLASS RECOMMENDATIONS ===")
    
#     # Get class recommendations based on concept
#     stealth_concept = "A character focused on stealth, deception, and gathering intelligence"
#     recommended = manager.get_all_classes(
#         filtered_by_concept=True,
#         character_concept=stealth_concept
#     )
#     print(f"Recommended classes for {stealth_concept}:")
#     for cls in recommended[:3]:
#         reason = cls.get("recommendation_reason", "No reason provided")
#         print(f"- {cls['name']}: {reason}")
    
#     print("\n=== ROLEPLAY GUIDANCE ===")
    
#     # Get roleplay guidance for a class
#     guidance = manager.get_class_details(
#         magic_hunter.name,
#         include_roleplay_guidance=True
#     )
#     if "roleplay_guidance" in guidance:
#         print(f"Roleplay guidance for {magic_hunter.name}:")
#         for key, value in list(guidance["roleplay_guidance"].items())[:2]:
#             if isinstance(value, list):
#                 print(f"- {key}: {value[0]}")
#             else:
#                 print(f"- {key}: {value}")
    
#     return {
#         "magic_hunter": magic_hunter,
#         "elemental_dancer": elemental_dancer,
#         "with_feature": updated_dancer,
#         "with_subclass": with_subclass
#     }


# if __name__ == "__main__":
#     demonstrate_custom_class_creation()