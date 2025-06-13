from typing import Dict, List, Optional, Any
from ...core.abstractions.species import AbstractSpecies, SpeciesSize
from .content_registry import ContentRegistry

class SpeciesService:
    """
    Domain service for species-related operations.
    
    Handles species selection, trait application, and validation.
    """
    
    def __init__(self, content_registry: ContentRegistry):
        self.content_registry = content_registry
    
    def get_species_by_size(self, size: SpeciesSize) -> List[str]:
        """Get all species of a specific size."""
        matching_species = []
        
        for species_name in self.content_registry.list_available_species():
            species = self.content_registry.get_species(species_name)
            if species and species.get_size() == size:
                matching_species.append(species_name)
        
        return matching_species
    
    def get_species_by_ability_bonus(self, ability: str) -> List[str]:
        """Get species that provide a bonus to a specific ability."""
        matching_species = []
        
        for species_name in self.content_registry.list_available_species():
            species = self.content_registry.get_species(species_name)
            if species:
                bonuses = species.get_ability_score_increases()
                if ability in bonuses and bonuses[ability] > 0:
                    matching_species.append(species_name)
        
        return matching_species
    
    def get_species_with_trait(self, trait_name: str) -> List[str]:
        """Get species that have a specific trait."""
        matching_species = []
        
        for species_name in self.content_registry.list_available_species():
            species = self.content_registry.get_species(species_name)
            if species and species.has_feature(trait_name):
                matching_species.append(species_name)
        
        return matching_species
    
    def apply_species_to_character(self, character_data: Dict[str, Any], 
                                 species_name: str, 
                                 choices: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Apply species traits to character with player choices.
        
        Args:
            character_data: Character information
            species_name: Name of species to apply
            choices: Player choices for flexible traits
            
        Returns:
            Updated character data
        """
        species = self.content_registry.get_species(species_name)
        if not species:
            raise ValueError(f"Unknown species: {species_name}")
        
        # Apply base species traits
        updated_character = species.apply_to_character(character_data)
        
        # Apply player choices if provided
        if choices:
            updated_character = self._apply_species_choices(
                updated_character, species, choices
            )
        
        return updated_character
    
    def _apply_species_choices(self, character_data: Dict[str, Any], 
                             species: AbstractSpecies, 
                             choices: Dict[str, Any]) -> Dict[str, Any]:
        """Apply player choices for species traits."""
        updated_character = character_data.copy()
        
        # Handle flexible ability score increases (like Human)
        if "ability_scores" in choices:
            for ability, increase in choices["ability_scores"].items():
                current = updated_character["ability_scores"].get(ability, 10)
                updated_character["ability_scores"][ability] = current + increase
        
        # Handle skill proficiency choices
        if "skill_choice" in choices:
            skill = choices["skill_choice"]
            if skill not in updated_character["proficiencies"]["skills"]:
                updated_character["proficiencies"]["skills"].append(skill)
        
        # Handle language choices
        if "language_choice" in choices:
            language = choices["language_choice"]
            if language not in updated_character["languages"]:
                updated_character["languages"].append(language)
        
        return updated_character