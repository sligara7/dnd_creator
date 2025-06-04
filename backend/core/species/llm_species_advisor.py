import re
import json
from typing import Dict, Any, Optional
from backend.core.species.abstract_species import SpeciesSize
from backend.core.species.species import CustomSpecies
from backend.core.ollama_service import OllamaService

class LLMSpeciesAdvisor:
    """Service for generating custom species using LLM"""
    
    def __init__(self, llm_service=None):
        """
        Initialize the LLM species creator.
        
        Args:
            llm_service: Service for LLM integration (default: OllamaService)
        """
        self.llm_service = llm_service or OllamaService()
    
    def _create_prompt(self, task, context):
        """
        Create a well-structured prompt for the LLM.
        
        Args:
            task: The specific task (e.g., "create a custom species")
            context: Relevant context information
        
        Returns:
            str: Formatted prompt
        """
        system_context = "You are a D&D 5e (2024 rules) custom content creator specializing in balanced species creation."
        instructions = f"Based on the following information, {task}. Keep your response focused on D&D rules and balance."
        
        prompt = f"{system_context}\n\n{instructions}\n\nInformation: {context}"
        return prompt
    
    def _extract_json(self, response):
        """
        Extract JSON from LLM response.
        
        Args:
            response: Text response from LLM
            
        Returns:
            dict: Parsed JSON or None if parsing fails
        """
        try:
            # Try to parse JSON from the response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
        except Exception as e:
            print(f"Error parsing LLM response: {e}")
            return None
    
    def generate_species_concept(self, concept_description: str) -> Dict[str, Any]:
        """
        Generate a high-level species concept based on a description.
        
        Args:
            concept_description: Brief description of the desired species
            
        Returns:
            Dict[str, Any]: Species concept information
        """
        prompt = self._create_prompt(
            "create a D&D species concept",
            f"Concept: {concept_description}\n\n"
            f"Generate a high-level concept for this species including: name, brief physical description, "
            f"cultural overview, and a unique trait that makes them special. Return as JSON."
        )
        
        try:
            response = self.llm_service.generate(prompt)
            concept_data = self._extract_json(response)
            if concept_data:
                return concept_data
        except Exception as e:
            print(f"Error generating species concept: {e}")
        
        # Fallback if LLM fails
        return {
            "name": concept_description.split()[0].capitalize() + "folk",
            "physical_description": f"A humanoid species based on the concept: {concept_description}",
            "culture": "A unique culture with distinctive traditions",
            "special_trait": "Natural adaptability"
        }
    
    def generate_complete_species(self, concept: str = None, partial_data: Dict[str, Any] = None) -> CustomSpecies:
        """
        Generate a complete custom species with all required attributes.
        
        Args:
            concept: Brief concept description (alternative to partial_data)
            partial_data: Partially specified species data to fill in
            
        Returns:
            CustomSpecies: Fully defined custom species
        """
        if not concept and not partial_data:
            raise ValueError("Must provide either concept or partial_data")
        
        if partial_data:
            context = f"Partial species data: {json.dumps(partial_data)}\n\n"
            context += "Fill in all missing attributes to create a complete, balanced species."
            task = "complete this partial species definition"
        else:
            context = f"Species concept: {concept}\n\n"
            context += "Create a complete, balanced species definition based on this concept."
            task = "create a complete custom species"
        
        prompt = self._create_prompt(
            task,
            context + "\n\n"
            "Include the following attributes in your JSON response:\n"
            "- name: The species name\n"
            "- size: 'SMALL', 'MEDIUM', or 'LARGE'\n"
            "- speed: Base walking speed in feet\n"
            "- darkvision: Range in feet (0 for none)\n"
            "- languages: Array of languages known\n"
            "- resistances: Array of damage resistances (if any)\n"
            "- traits: Object mapping trait names to descriptions\n"
            "- proficiencies: Array of skill or tool proficiencies\n"
            "- vision_types: Array of special vision types\n"
            "- ability_bonuses: Object mapping abilities to bonuses\n"
            "- description: General description\n"
            "- culture: Cultural description\n"
            "- physical_traits: Physical appearance description"
        )
        
        try:
            response = self.llm_service.generate(prompt)
            species_data = self._extract_json(response)
            
            if species_data:
                # Convert size string to enum
                if "size" in species_data and isinstance(species_data["size"], str):
                    try:
                        species_data["size"] = SpeciesSize[species_data["size"]]
                    except KeyError:
                        species_data["size"] = SpeciesSize.MEDIUM
                
                # Create the custom species
                return CustomSpecies(**species_data)
        except Exception as e:
            print(f"Error generating complete species: {e}")
        
        # Fallback if LLM fails
        name = (partial_data or {}).get("name", f"Custom{concept.split()[0].title()}") if concept else "CustomSpecies"
        return CustomSpecies(
            name=name,
            description=concept or "Custom species",
            traits={"Unique Biology": "This species has adapted to its environment in unique ways."}
        )
    
    def balance_species(self, species: CustomSpecies) -> CustomSpecies:
        """
        Balance a custom species to ensure it follows D&D design principles.
        
        Args:
            species: The species to balance
            
        Returns:
            CustomSpecies: Balanced version of the species
        """
        prompt = self._create_prompt(
            "balance this custom species",
            f"Current species definition: {json.dumps(species.to_dict())}\n\n"
            f"Review this species for balance issues according to D&D 5e (2024) design principles.\n"
            f"Adjust any overpowered or underpowered traits, ability bonuses, or special features.\n"
            f"Return the balanced version as JSON with the same structure."
        )
        
        try:
            response = self.llm_service.generate(prompt)
            balanced_data = self._extract_json(response)
            
            if balanced_data:
                # Convert size string to enum if needed
                if "size" in balanced_data and isinstance(balanced_data["size"], str):
                    try:
                        balanced_data["size"] = SpeciesSize[balanced_data["size"]]
                    except KeyError:
                        balanced_data["size"] = species.size
                
                # Create balanced species
                return CustomSpecies(**balanced_data)
        except Exception as e:
            print(f"Error balancing species: {e}")
        
        # Return original if balancing fails
        return species
    
    def generate_variant(self, base_species: CustomSpecies, variation_concept: str) -> CustomSpecies:
        """
        Generate a variant of an existing species.
        
        Args:
            base_species: The base species to create a variant from
            variation_concept: Description of how the variant differs
            
        Returns:
            CustomSpecies: Variant species
        """
        prompt = self._create_prompt(
            "create a variant of this species",
            f"Base species: {json.dumps(base_species.to_dict())}\n"
            f"Variation concept: {variation_concept}\n\n"
            f"Create a variant of this species that incorporates the variation concept. "
            f"Maintain core elements but add unique twists based on the variation. "
            f"Return the complete variant species as JSON."
        )
        
        try:
            response = self.llm_service.generate(prompt)
            variant_data = self._extract_json(response)
            
            if variant_data:
                # Ensure the variant has a different name
                if "name" not in variant_data or variant_data["name"] == base_species.name:
                    variant_data["name"] = f"{base_species.name} ({variation_concept.split()[0].title()})"
                
                # Convert size string to enum if needed
                if "size" in variant_data and isinstance(variant_data["size"], str):
                    try:
                        variant_data["size"] = SpeciesSize[variant_data["size"]]
                    except KeyError:
                        variant_data["size"] = base_species.size
                
                return CustomSpecies(**variant_data)
        except Exception as e:
            print(f"Error generating variant species: {e}")
        
        # Fallback - create simple variant 
        variant_data = base_species.to_dict()
        variant_data["name"] = f"{base_species.name} ({variation_concept.split()[0].title()})"
        variant_data["description"] = f"{base_species.description}\nThis variant {variation_concept}."
        variant_data["custom_id"] = None  # Generate new ID
        
        # Convert size to enum if it's a string
        if "size" in variant_data and isinstance(variant_data["size"], str):
            try:
                variant_data["size"] = SpeciesSize[variant_data["size"]]
            except KeyError:
                variant_data["size"] = base_species.size
        
        return CustomSpecies(**variant_data)
    
    def generate_unique_trait(self, species_concept: str, power_level: str = "balanced") -> Dict[str, str]:
        """
        Generate a unique trait for a species.
        
        Args:
            species_concept: Brief description of the species
            power_level: "mild", "balanced", or "powerful"
            
        Returns:
            Dict[str, str]: Trait name and description
        """
        prompt = self._create_prompt(
            "create a unique species trait",
            f"Species concept: {species_concept}\nPower level: {power_level}\n\n"
            f"Create a unique and thematic trait for this species that feels {power_level}. "
            f"The trait should be mechanically interesting but appropriate for D&D 5e (2024). "
            f"Return a JSON object with 'name' and 'description' keys."
        )
        
        try:
            response = self.llm_service.generate(prompt)
            trait_data = self._extract_json(response)
            
            if trait_data and "name" in trait_data and "description" in trait_data:
                return {trait_data["name"]: trait_data["description"]}
        except Exception as e:
            print(f"Error generating unique trait: {e}")
        
        # Fallback trait
        trait_name = f"{species_concept.split()[0].title()} Heritage"
        trait_desc = f"You have inherited unique abilities from your {species_concept} ancestry."
        return {trait_name: trait_desc}
    
    def _extract_json(self, response):
        """Extract JSON from LLM response."""
        try:
            # Try to find JSON in code blocks first
            code_block_match = re.search(r'```(?:json)?\s*(\{.*?\})```', response, re.DOTALL)
            if code_block_match:
                return json.loads(code_block_match.group(1))
                
            # Fall back to searching for any JSON object
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
        return None

