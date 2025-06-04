from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union, Any, Tuple, Set
import json
import re
import uuid
from enum import Enum, auto

from backend.core.species.abstract_species import AbstractSpecies, SpeciesSize
from backend.core.services.ollama_service import OllamaService
from backend.core.species.llm_species_advisor import LLMSpeciesAdvisor

class Species(AbstractSpecies):
    """
    Implementation of the base species class for D&D 5e (2024 Edition).
    
    This class provides the standard implementations for the core species
    from the Player's Handbook and other official sources.
    """
    
    def __init__(self, 
                 name: str, 
                 size: SpeciesSize = SpeciesSize.MEDIUM,
                 speed: int = 30,
                 darkvision: int = 0,
                 languages: List[str] = None,
                 resistances: List[str] = None,
                 traits: Dict[str, Any] = None,
                 proficiencies: List[str] = None,
                 vision_types: List[str] = None,
                 ability_bonuses: Dict[str, int] = None,
                 description: str = "",
                 subraces: List[Dict[str, Any]] = None,
                 source: str = "Player's Handbook"):
        """
        Initialize a species.
        
        Args:
            name: Species name
            size: Size category of the species
            speed: Base walking speed in feet
            darkvision: Range of darkvision in feet (0 for none)
            languages: Languages known by the species
            resistances: Damage types the species has resistance to
            traits: Special traits of the species
            proficiencies: Skill or tool proficiencies granted by the species
            vision_types: Special vision types (e.g., "Blindsight", "Truesight")
            ability_bonuses: Bonuses to ability scores
            description: Description of the species
            subraces: List of subraces for this species
            source: Source book for the species
        """
        super().__init__(
            name=name,
            size=size,
            speed=speed,
            darkvision=darkvision,
            languages=languages or ["Common"],
            resistances=resistances or [],
            traits=traits or {},
            proficiencies=proficiencies or [],
            vision_types=vision_types or []
        )
        
        self.ability_bonuses = ability_bonuses or {}
        self.description = description
        self.subraces = subraces or []
        self.source = source
    
    def get_all_species(self) -> List[Dict[str, Any]]:
        """
        Get a list of all species.
        
        Returns:
            List[Dict[str, Any]]: List of species data
        """
        # This would normally query a database or config file
        # For this implementation, we'll return the core species list
        return [
            {"name": species, "source": "Player's Handbook"} 
            for species in self.CORE_SPECIES
        ]
    
    def get_species_details(self, species_name: str) -> Optional[Dict[str, Any]]:
        """
        Get details for a specific species.
        
        Args:
            species_name: Name of the species
            
        Returns:
            Optional[Dict[str, Any]]: Species details or None if not found
        """
        # In a real implementation, this would look up details
        # For now, return basic info if it matches this instance
        if species_name.lower() == self.name.lower():
            return self.to_dict()
        return None
    
    def get_traits(self) -> Dict[str, str]:
        """
        Get traits for this species.
        
        Returns:
            Dict[str, str]: Dictionary of trait names and descriptions
        """
        return self.traits
    
    def apply_species_bonuses(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply species bonuses to character data.
        
        Args:
            character_data: Character data to modify
            
        Returns:
            Dict[str, Any]: Updated character data with species bonuses
        """
        updated_data = character_data.copy()
        
        # Apply ability score bonuses
        if "ability_scores" in updated_data and self.ability_bonuses:
            for ability, bonus in self.ability_bonuses.items():
                ability_lower = ability.lower()
                if ability_lower in updated_data["ability_scores"]:
                    updated_data["ability_scores"][ability_lower] += bonus
        
        # Apply speed
        updated_data["speed"] = updated_data.get("speed", {})
        updated_data["speed"]["walk"] = self.speed
        
        # Apply darkvision
        if self.darkvision > 0:
            updated_data["senses"] = updated_data.get("senses", {})
            updated_data["senses"]["darkvision"] = self.darkvision
        
        # Apply languages
        updated_data["languages"] = updated_data.get("languages", [])
        for language in self.languages:
            if language not in updated_data["languages"]:
                updated_data["languages"].append(language)
        
        # Apply resistances
        if self.resistances:
            updated_data["resistances"] = updated_data.get("resistances", [])
            for resistance in self.resistances:
                if resistance not in updated_data["resistances"]:
                    updated_data["resistances"].append(resistance)
        
        # Apply proficiencies
        if self.proficiencies:
            updated_data["proficiencies"] = updated_data.get("proficiencies", {})
            updated_data["proficiencies"]["skills"] = updated_data["proficiencies"].get("skills", [])
            for proficiency in self.proficiencies:
                if proficiency not in updated_data["proficiencies"]["skills"]:
                    updated_data["proficiencies"]["skills"].append(proficiency)
        
        # Apply traits (implementation depends on how traits are applied to characters)
        
        return updated_data
    
    def get_species_by_size(self, size: SpeciesSize) -> List[str]:
        """
        Get species names that match the specified size.
        
        Args:
            size: Size category to filter by
            
        Returns:
            List[str]: List of species names with the specified size
        """
        if self.size == size:
            return [self.name]
        return []
    
    def get_species_by_ability_bonus(self, ability: str) -> List[str]:
        """
        Get species names that provide a bonus to the specified ability.
        
        Args:
            ability: Ability to filter by
            
        Returns:
            List[str]: List of species names with the specified ability bonus
        """
        if ability.lower() in [a.lower() for a in self.ability_bonuses.keys()]:
            return [self.name]
        return []
    
    def get_species_by_feature(self, feature: str) -> List[str]:
        """
        Get species names that have the specified feature.
        
        Args:
            feature: Feature to filter by
            
        Returns:
            List[str]: List of species names with the specified feature
        """
        feature_lower = feature.lower()
        
        # Check traits
        for trait_name in self.traits.keys():
            if feature_lower in trait_name.lower():
                return [self.name]
        
        # Check resistances
        for resistance in self.resistances:
            if feature_lower in resistance.lower():
                return [self.name]
                
        # Check vision types
        for vision in self.vision_types:
            if feature_lower in vision.lower():
                return [self.name]
        
        return []
    
    def get_lineage_options(self, species_name: str) -> List[Dict[str, Any]]:
        """
        Get available lineage options (subraces) for a species.
        
        Args:
            species_name: Species name
            
        Returns:
            List[Dict[str, Any]]: List of lineage options
        """
        if species_name.lower() == self.name.lower():
            return self.subraces
        return []
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert species to dictionary representation.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the species
        """
        return {
            "name": self.name,
            "size": self.size.name,
            "speed": self.speed,
            "darkvision": self.darkvision,
            "languages": self.languages,
            "resistances": self.resistances,
            "traits": self.traits,
            "proficiencies": self.proficiencies,
            "vision_types": self.vision_types,
            "ability_bonuses": self.ability_bonuses,
            "description": self.description,
            "subraces": self.subraces,
            "source": self.source
        }

class CustomSpecies(Species):
    """
    Custom species implementation with full LLM integration.
    
    This class allows creation of completely custom species with:
    1. Full manual specification of all attributes
    2. Semi-automatic creation with some attributes specified and others generated by LLM
    3. Fully automatic generation based on a concept description
    4. Variant creation based on existing species
    """
    
    def __init__(self, 
                 name: str,
                 size: SpeciesSize = SpeciesSize.MEDIUM,
                 speed: int = 30,
                 darkvision: int = 0,
                 languages: List[str] = None,
                 resistances: List[str] = None,
                 traits: Dict[str, Any] = None,
                 proficiencies: List[str] = None,
                 vision_types: List[str] = None,
                 ability_bonuses: Dict[str, int] = None,
                 description: str = "",
                 culture: str = "",
                 physical_traits: str = "",
                 custom_id: str = None):
        """
        Initialize a custom species.
        
        Args:
            name: Species name
            size: Size category
            speed: Base walking speed in feet
            darkvision: Range of darkvision in feet (0 for none)
            languages: Languages known by the species
            resistances: Damage types the species has resistance to
            traits: Special traits of the species
            proficiencies: Skill or tool proficiencies granted
            vision_types: Special vision types
            ability_bonuses: Bonuses to ability scores (+1, +2, etc.)
            description: General description of the species
            culture: Description of the species' culture
            physical_traits: Description of physical characteristics
            custom_id: Unique identifier for the custom species
        """
        super().__init__(
            name=name,
            size=size,
            speed=speed,
            darkvision=darkvision,
            languages=languages or ["Common"],
            resistances=resistances or [],
            traits=traits or {},
            proficiencies=proficiencies or [],
            vision_types=vision_types or [],
            ability_bonuses=ability_bonuses or {},
            description=description,
            source="Custom"
        )
        
        # Additional custom species properties
        self.culture = culture
        self.physical_traits = physical_traits
        self.custom_id = custom_id or str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        """Enhanced dictionary representation including custom fields"""
        base_dict = super().to_dict()
        base_dict.update({
            "culture": self.culture,
            "physical_traits": self.physical_traits,
            "custom_id": self.custom_id
        })
        return base_dict

class SpeciesManager:
    """
    Unified class for managing, creating, and customizing species.
    
    This class provides a seamless interface for:
    1. Creating and managing standard species
    2. Creating completely custom species with LLM assistance
    3. Searching, filtering, and recommending species
    4. Enhancing species descriptions and traits with LLM
    """
    
    def __init__(self, llm_service=None):
        """Initialize the species manager with optional custom LLM service"""
        self.llm_service = llm_service or OllamaService()
        self.llm_creator = LLMSpeciesAdvisor(self.llm_service)
        self.custom_species = {}  # Repository of custom species by ID
        self.standard_species = {}  # Repository of standard species by name
        
        # Initialize standard species from the core rules
        self._initialize_standard_species()
    
    def _initialize_standard_species(self):
        """Initialize the standard species from core rules"""
        # This would normally load data from a database or file
        # For this example, we'll just create placeholder entries
        for species_name in AbstractSpecies.CORE_SPECIES:
            self.standard_species[species_name] = Species(
                name=species_name,
                description=f"Standard {species_name} species from the Player's Handbook",
                source="Player's Handbook"
            )
    
    # === CORE SPECIES MANAGEMENT ===
    
    def get_all_species(self, filtered_by_character_concept: bool = False, 
                       character_concept: str = None) -> List[Dict[str, Any]]:
        """
        Get all available species, optionally filtered by character concept.
        
        Args:
            filtered_by_character_concept: Whether to use LLM to recommend species
            character_concept: Character concept to filter/recommend by
            
        Returns:
            List[Dict[str, Any]]: List of species data
        """
        # Get all standard species
        standard_species_data = [species.to_dict() for species in self.standard_species.values()]
        
        # Get all custom species
        custom_species_data = [species.to_dict() for species in self.custom_species.values()]
        
        # Combine lists
        all_species = standard_species_data + custom_species_data
        
        # If no filtering, return all
        if not filtered_by_character_concept or not character_concept:
            return all_species
        
        # Use LLM to recommend species based on character concept
        return self._recommend_species_by_concept(all_species, character_concept)
    
    def _recommend_species_by_concept(self, species_list: List[Dict[str, Any]], 
                                    character_concept: str) -> List[Dict[str, Any]]:
        """Use LLM to recommend species based on character concept"""
        # Format species names for the prompt
        species_names = [s["name"] for s in species_list]
        species_str = ", ".join(species_names)
        
        prompt = self.llm_creator._create_prompt(
            "recommend species for this character concept",
            f"Character concept: {character_concept}\n"
            f"Available species: {species_str}\n\n"
            f"Recommend the top 3-5 species that would best fit this character concept. "
            f"For each recommendation, provide a brief explanation of why it fits. "
            f"Return as JSON array with 'name' and 'reason' keys."
        )
        
        try:
            response = self.llm_service.generate(prompt)
            
            # Try to parse JSON from the response
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                recommendations = json.loads(json_match.group(0))
                
                # Filter species list to keep only recommended ones
                recommended_names = [r["name"] for r in recommendations]
                filtered_list = [
                    {**species, "recommendation_reason": next(
                        (r["reason"] for r in recommendations if r["name"] == species["name"]), 
                        None
                    )}
                    for species in species_list 
                    if species["name"] in recommended_names
                ]
                
                return filtered_list
        except Exception as e:
            print(f"Error getting species recommendations: {e}")
        
        # Return unfiltered list if LLM fails
        return species_list
    
    def get_species_details(self, species_name: str, 
                          include_roleplay_guidance: bool = False) -> Dict[str, Any]:
        """
        Get detailed information about a species.
        
        Args:
            species_name: Name of the species
            include_roleplay_guidance: Whether to include LLM roleplay guidance
            
        Returns:
            Dict[str, Any]: Species details
        """
        # Find the species
        species = None
        
        # Check standard species
        if species_name in self.standard_species:
            species = self.standard_species[species_name]
        else:
            # Check custom species
            for custom_species in self.custom_species.values():
                if custom_species.name.lower() == species_name.lower():
                    species = custom_species
                    break
        
        if not species:
            return None
        
        # Get basic details
        details = species.to_dict()
        
        # Add roleplay guidance if requested
        if include_roleplay_guidance:
            roleplay_guidance = self._generate_roleplay_guidance(species)
            details["roleplay_guidance"] = roleplay_guidance
        
        return details
    
    def _generate_roleplay_guidance(self, species) -> Dict[str, Any]:
        """Generate roleplay guidance for a species using LLM"""
        prompt = self.llm_creator._create_prompt(
            "create roleplay guidance",
            f"Species: {species.name}\nDescription: {species.description}\n"
            f"Culture: {getattr(species, 'culture', 'Unknown')}\n"
            f"Traits: {json.dumps(species.traits)}\n\n"
            f"Provide roleplay guidance for this species including: personality tendencies, "
            f"social interactions, cultural values, common behaviors, and unique perspectives. "
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
            "personality": f"Members of the {species.name} species tend to be adaptable and diverse.",
            "social_interactions": "They interact with others based on their individual personality.",
            "cultural_values": "Their cultural values vary widely.",
            "behaviors": "Their behaviors are determined by their upbringing and experiences."
        }
    
    def get_species_traits(self, species_name: str, 
                         include_creative_applications: bool = False) -> Dict[str, Any]:
        """
        Get traits for a species with optional creative applications.
        
        Args:
            species_name: Name of the species
            include_creative_applications: Whether to include LLM suggested applications
            
        Returns:
            Dict[str, Any]: Species traits with optional creative applications
        """
        # Find the species
        for standard_name, species in self.standard_species.items():
            if standard_name.lower() == species_name.lower():
                traits = species.get_traits()
                if not include_creative_applications:
                    return traits
                    
                return self._enhance_traits_with_creative_applications(species_name, traits)
        
        # Check custom species
        for custom_species in self.custom_species.values():
            if custom_species.name.lower() == species_name.lower():
                traits = custom_species.get_traits()
                if not include_creative_applications:
                    return traits
                    
                return self._enhance_traits_with_creative_applications(species_name, traits)
        
        return {}
    
    def _enhance_traits_with_creative_applications(self, species_name: str, 
                                               traits: Dict[str, str]) -> Dict[str, Any]:
        """Use LLM to suggest creative applications for species traits"""
        traits_str = "\n".join([f"- {name}: {desc}" for name, desc in traits.items()])
        
        prompt = self.llm_creator._create_prompt(
            "suggest creative applications for species traits",
            f"Species: {species_name}\nTraits:\n{traits_str}\n\n"
            f"For each trait, suggest 2-3 creative ways to use it beyond combat, "
            f"such as in exploration, social interaction, problem-solving, or roleplaying. "
            f"Return as JSON with trait names as keys and arrays of creative applications as values."
        )
        
        try:
            response = self.llm_service.generate(prompt)
            applications_data = self.llm_creator._extract_json(response)
            
            if applications_data:
                # Format the result with both descriptions and applications
                enhanced_traits = {}
                for trait_name, trait_desc in traits.items():
                    enhanced_traits[trait_name] = {
                        "description": trait_desc,
                        "creative_applications": applications_data.get(trait_name, [
                            "Use creatively in roleplaying situations",
                            "Consider non-combat applications"
                        ])
                    }
                return enhanced_traits
        except Exception as e:
            print(f"Error generating creative trait applications: {e}")
        
        # Fallback - return original traits with placeholder applications
        enhanced_traits = {}
        for trait_name, trait_desc in traits.items():
            enhanced_traits[trait_name] = {
                "description": trait_desc,
                "creative_applications": [
                    "Use creatively in roleplaying situations",
                    "Consider non-combat applications"
                ]
            }
        return enhanced_traits
    
    # === CUSTOM SPECIES CREATION ===
    
    def create_custom_species(self, species_data: Dict[str, Any]) -> CustomSpecies:
        """
        Create a custom species with the specified data.
        
        Args:
            species_data: Custom species definition (can be partial)
            
        Returns:
            CustomSpecies: New custom species instance
        """
        # If just a concept is provided, generate everything
        if "concept" in species_data and len(species_data) < 5:
            species = self.create_species_from_concept(species_data["concept"])
        else:
            # Generate from partial data
            species = self.llm_creator.generate_complete_species(partial_data=species_data)
            
        # Balance the species
        species = self.llm_creator.balance_species(species)
        
        # Store the custom species
        self.custom_species[species.custom_id] = species
        return species
    
    def create_species_from_concept(self, concept: str) -> CustomSpecies:
        """
        Create a complete species from a simple concept description.
        
        Args:
            concept: Brief description of the desired species
            
        Returns:
            CustomSpecies: Fully detailed species
        """
        species = self.llm_creator.generate_complete_species(concept=concept)
        self.custom_species[species.custom_id] = species
        return species
    
    def generate_variant_species(self, base_species_id: str, 
                                variation_concept: str) -> CustomSpecies:
        """
        Generate a variant of an existing species.
        
        Args:
            base_species_id: ID of the base species
            variation_concept: Description of how the variant differs
            
        Returns:
            CustomSpecies: Variant species
        """
        # Find the base species
        base_species = self.custom_species.get(base_species_id)
        if not base_species:
            # Try to find by name for standard species
            for name, species in self.standard_species.items():
                if name == base_species_id:
                    # Convert standard species to custom for variation
                    base_species = CustomSpecies(
                        name=species.name,
                        size=species.size,
                        speed=species.speed,
                        darkvision=species.darkvision,
                        languages=species.languages,
                        resistances=species.resistances,
                        traits=species.traits,
                        proficiencies=species.proficiencies,
                        vision_types=species.vision_types,
                        ability_bonuses=species.ability_bonuses,
                        description=species.description
                    )
                    break
        
        if not base_species:
            raise ValueError(f"No species found with ID or name: {base_species_id}")
            
        # Generate variant
        variant = self.llm_creator.generate_variant(base_species, variation_concept)
        self.custom_species[variant.custom_id] = variant
        return variant
    
    def add_unique_trait_to_species(self, species_id: str, 
                                 trait_concept: str, 
                                 power_level: str = "balanced") -> CustomSpecies:
        """
        Add a unique LLM-generated trait to a species.
        
        Args:
            species_id: ID of the species to modify
            trait_concept: Description of the trait concept
            power_level: "mild", "balanced", or "powerful"
            
        Returns:
            CustomSpecies: Updated species with the new trait
        """
        # Find the species
        species = self.custom_species.get(species_id)
        if not species:
            raise ValueError(f"No custom species found with ID: {species_id}")
        
        # Generate the trait
        new_trait = self.llm_creator.generate_unique_trait(trait_concept, power_level)
        
        # Make a copy of the species with the new trait
        species_data = species.to_dict()
        traits = species_data.get("traits", {}).copy()
        traits.update(new_trait)
        species_data["traits"] = traits
        species_data["custom_id"] = None  # Generate new ID
        
        # Convert size string to enum if needed
        if "size" in species_data and isinstance(species_data["size"], str):
            try:
                species_data["size"] = SpeciesSize[species_data["size"]]
            except KeyError:
                species_data["size"] = species.size
                
        # Create the updated species
        updated_species = CustomSpecies(**species_data)
        self.custom_species[updated_species.custom_id] = updated_species
        
        return updated_species
    
    def get_random_species_suggestion(self, world_theme: str = None) -> Dict[str, Any]:
        """
        Get a random species suggestion, optionally themed for a world.
        
        Args:
            world_theme: Optional theme for the world (desert, forest, etc.)
            
        Returns:
            Dict[str, Any]: Species concept suggestion
        """
        return self.llm_creator.generate_species_concept(
            f"A unique species for a {world_theme} world" if world_theme else "A unique fantasy species"
        )
    
    # === SEARCH AND FILTER METHODS ===
    
    def get_species_by_size(self, size: SpeciesSize) -> List[Dict[str, Any]]:
        """
        Get species matching a specific size.
        
        Args:
            size: Size to filter by
            
        Returns:
            List[Dict[str, Any]]: Matching species
        """
        results = []
        
        # Check standard species
        for species in self.standard_species.values():
            if species.size == size:
                results.append(species.to_dict())
        
        # Check custom species
        for species in self.custom_species.values():
            if species.size == size:
                results.append(species.to_dict())
        
        return results
    
    def get_species_by_ability_bonus(self, ability: str) -> List[Dict[str, Any]]:
        """
        Get species that provide a bonus to a specific ability.
        
        Args:
            ability: Ability to filter by
            
        Returns:
            List[Dict[str, Any]]: Matching species
        """
        results = []
        ability_lower = ability.lower()
        
        # Check standard species
        for species in self.standard_species.values():
            if hasattr(species, 'ability_bonuses') and species.ability_bonuses:
                for bonus_ability in species.ability_bonuses:
                    if bonus_ability.lower() == ability_lower:
                        results.append(species.to_dict())
                        break
        
        # Check custom species
        for species in self.custom_species.values():
            if species.ability_bonuses:
                for bonus_ability in species.ability_bonuses:
                    if bonus_ability.lower() == ability_lower:
                        results.append(species.to_dict())
                        break
        
        return results
    
    def get_species_by_feature(self, feature: str) -> List[Dict[str, Any]]:
        """
        Get species that have a specific feature.
        
        Args:
            feature: Feature to filter by
            
        Returns:
            List[Dict[str, Any]]: Matching species
        """
        results = []
        feature_lower = feature.lower()
        
        # Check standard species
        for species in self.standard_species.values():
            # Check traits
            for trait_name in species.traits.keys():
                if feature_lower in trait_name.lower():
                    results.append(species.to_dict())
                    break
            
            # Check resistances
            for resistance in species.resistances:
                if feature_lower in resistance.lower():
                    if species.to_dict() not in results:
                        results.append(species.to_dict())
                    break
        
        # Check custom species
        for species in self.custom_species.values():
            # Check traits
            for trait_name in species.traits.keys():
                if feature_lower in trait_name.lower():
                    results.append(species.to_dict())
                    break
            
            # Check resistances
            for resistance in species.resistances:
                if feature_lower in resistance.lower():
                    if species.to_dict() not in results:
                        results.append(species.to_dict())
                    break
        
        return results
    
    def search_species(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Search for species by name, trait, or description.
        
        Args:
            search_term: Term to search for
            
        Returns:
            List[Dict[str, Any]]: Matching species
        """
        results = []
        search_term_lower = search_term.lower()
        
        # Search all species
        for species in list(self.standard_species.values()) + list(self.custom_species.values()):
            # Search name
            if search_term_lower in species.name.lower():
                results.append(species.to_dict())
                continue
                
            # Search description
            if search_term_lower in species.description.lower():
                results.append(species.to_dict())
                continue
                
            # Search traits
            for trait_name, trait_desc in species.traits.items():
                if search_term_lower in trait_name.lower() or search_term_lower in trait_desc.lower():
                    results.append(species.to_dict())
                    break
        
        return results
    
    def _search_in_all_species(self, condition_func):
        """Helper to apply a condition to all standard and custom species"""
        results = []
        for species in list(self.standard_species.values()) + list(self.custom_species.values()):
            if condition_func(species):
                results.append(species.to_dict())
        return results


# Example usage
# def demonstrate_species_manager():
#     """Demonstrate the capabilities of the SpeciesManager"""
#     manager = SpeciesManager()
    
#     print("=== CREATING CUSTOM SPECIES ===")
    
#     # Create from just a concept
#     crystal_folk = manager.create_species_from_concept(
#         "A crystalline humanoid species with gems embedded in their skin that can redirect light"
#     )
#     print(f"Created species: {crystal_folk.name}")
    
#     # Create with partial specification
#     plant_folk = manager.create_custom_species({
#         "name": "Florians",
#         "concept": "Plant-based humanoids who photosynthesize and can root into soil",
#         "size": "MEDIUM",
#         "resistances": ["poison"],
#         "traits": {
#             "Photosynthesis": "You need only half the food a normal humanoid requires if you spend at least 4 hours in sunlight each day."
#         }
#     })
#     print(f"Created species with partial spec: {plant_folk.name}")
    
#     # Generate a variant
#     winter_variant = manager.generate_variant_species(
#         plant_folk.custom_id, 
#         "adapted to cold winter climates with evergreen features"
#     )
#     print(f"Created variant: {winter_variant.name}")
    
#     # Add unique trait
#     enhanced_plant = manager.add_unique_trait_to_species(
#         plant_folk.custom_id,
#         "ability to communicate with plants and trees",
#         "balanced"
#     )
#     print(f"Added unique trait to create: {enhanced_plant.name}")
    
#     print("\n=== SPECIES RECOMMENDATIONS ===")
    
#     # Get species recommendations based on concept
#     stealth_concept = "A character focused on stealth, deception, and operating at night"
#     recommended = manager.get_all_species(
#         filtered_by_character_concept=True,
#         character_concept=stealth_concept
#     )
#     print(f"Recommended species for {stealth_concept}:")
#     for species in recommended[:3]:
#         reason = species.get("recommendation_reason", "No reason provided")
#         print(f"- {species['name']}: {reason}")
    
#     print("\n=== CREATIVE TRAIT APPLICATIONS ===")
    
#     # Get creative applications for traits
#     if crystal_folk.traits:
#         trait_applications = manager.get_species_traits(
#             crystal_folk.name,
#             include_creative_applications=True
#         )
#         for trait_name, trait_data in trait_applications.items():
#             print(f"\n{trait_name}: {trait_data['description']}")
#             print("Creative applications:")
#             for app in trait_data.get("creative_applications", [])[:2]:
#                 print(f"- {app}")
    
#     return {
#         "crystal_folk": crystal_folk,
#         "plant_folk": plant_folk,
#         "winter_variant": winter_variant,
#         "enhanced_plant": enhanced_plant
#     }


# if __name__ == "__main__":
#     demonstrate_species_manager()