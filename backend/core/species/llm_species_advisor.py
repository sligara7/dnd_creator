import re
import json
import logging
from typing import Dict, Any, Optional, List, Union
from backend.core.species.abstract_species import SpeciesSize
from backend.core.species.species import CustomSpecies
from backend.core.services.ollama_service import OllamaService

logger = logging.getLogger(__name__)

class LLMSpeciesAdvisor:
    """Service for generating custom species using LLM"""
    
    def __init__(self, llm_service=None):
        """Initialize the LLM species advisor"""
        self.llm_service = llm_service or OllamaService()
        self.allow_unbalanced = False
        self.theme_restrictions = True
        self.mechanics_restrictions = True
        self.system_prompt = "You are a D&D 5e (2024 rules) custom content creator specializing in balanced species creation."
    
    def _create_prompt(self, task, context):
        """Create a well-structured prompt for the LLM"""
        instructions = f"Based on the following information, {task}. Return your response as valid JSON."
        
        prompt = f"{self.system_prompt}\n\n{instructions}\n\nInformation: {context}"
        return prompt
    
    def _update_system_prompt(self):
        """Update system prompt based on creative parameters"""
        base_prompt = "You are a D&D 5e (2024 rules) custom content creator"
        
        if not self.theme_restrictions and not self.mechanics_restrictions:
            base_prompt = "You are a creative game designer with expertise in both D&D and other game systems"
        
        if self.allow_unbalanced:
            base_prompt += " who prioritizes creative concepts over strict balance"
        else:
            base_prompt += " specializing in balanced species creation"
            
        if not self.theme_restrictions:
            base_prompt += ". You embrace concepts from any genre or media"
        
        if not self.mechanics_restrictions:
            base_prompt += ". You're willing to invent new mechanics beyond standard D&D"
            
        self.system_prompt = base_prompt
    
    def _extract_json(self, response):
        """Extract JSON from LLM response with improved handling"""
        try:
            # Try to find JSON in code blocks first
            code_block_match = re.search(r'```(?:json)?\s*(\{.*?\})```', response, re.DOTALL)
            if code_block_match:
                return json.loads(code_block_match.group(1))
                
            # Fall back to searching for any JSON object
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
                
            # If no JSON found, try to extract structured text
            if "name:" in response and ("traits:" in response or "description:" in response):
                return self._parse_structured_text(response)
                
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
        return None
    
    def _parse_structured_text(self, text):
        """Parse structured text into a dictionary"""
        result = {}
        current_key = None
        current_value = []
        
        # Simple parser for "key: value" formatted text
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            # Check if this line starts a new key
            key_match = re.match(r'^([A-Za-z_]+):\s*(.*)$', line)
            if key_match:
                # Save previous key-value pair if exists
                if current_key and current_value:
                    result[current_key] = '\n'.join(current_value).strip()
                    current_value = []
                
                # Start new key
                current_key = key_match.group(1).lower()
                value_part = key_match.group(2).strip()
                if value_part:
                    current_value.append(value_part)
            elif current_key:
                # Continue previous value
                current_value.append(line)
        
        # Add the final key-value pair
        if current_key and current_value:
            result[current_key] = '\n'.join(current_value).strip()
            
        return result
    
    def generate_species_concept(self, concept_description: str) -> Dict[str, Any]:
        """Generate a high-level species concept based on a description"""
        prompt = self._create_prompt(
            "create a D&D species concept",
            f"Concept: {concept_description}\n\n"
            f"Generate a high-level concept for this species including: name, brief physical description, "
            f"cultural overview, and a unique trait that makes them special. Return as JSON."
        )
        
        try:
            response = self.llm_service.generate_text(prompt)
            concept_data = self._extract_json(response)
            if concept_data:
                return concept_data
        except Exception as e:
            logger.error(f"Error generating species concept: {e}")
        
        # Fallback if LLM fails
        return {
            "name": concept_description.split()[0].capitalize() + "folk",
            "physical_description": f"A humanoid species based on the concept: {concept_description}",
            "culture": "A unique culture with distinctive traditions",
            "special_trait": "Natural adaptability"
        }
    
    def generate_complete_species(self, concept: str = None, partial_data: Dict[str, Any] = None) -> CustomSpecies:
        """Generate a complete custom species with all required attributes"""
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
            response = self.llm_service.generate_text(prompt)
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
            logger.error(f"Error generating complete species: {e}")
        
        # Fallback if LLM fails
        name = (partial_data or {}).get("name", f"Custom{concept.split()[0].title()}") if concept else "CustomSpecies"
        return CustomSpecies(
            name=name,
            description=concept or "Custom species",
            traits={"Unique Biology": "This species has adapted to its environment in unique ways."}
        )
    
    def balance_species(self, species: CustomSpecies, creativity_priority: float = 0.5) -> CustomSpecies:
        """Balance a custom species with adjustable creativity vs. balance priority"""
        # Adjust instruction based on creativity priority
        balance_instruction = ""
        if creativity_priority < 0.3:
            balance_instruction = "Strictly adhere to D&D balance guidelines, even if it means simplifying creative concepts."
        elif creativity_priority < 0.7:
            balance_instruction = "Balance this species while preserving its core creative elements."
        else:
            balance_instruction = "Prioritize preserving creative elements over strict balance, making only minimal adjustments."
            
        prompt = self._create_prompt(
            "balance this custom species",
            f"Current species definition: {json.dumps(species.to_dict())}\n\n"
            f"Review this species for balance issues according to D&D 5e design principles.\n{balance_instruction}\n"
            f"Return the balanced version as JSON with the same structure."
        )
        
        try:
            response = self.llm_service.generate_text(prompt)
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
            logger.error(f"Error balancing species: {e}")
        
        # Return original if balancing fails
        return species
    
    def generate_variant(self, base_species: CustomSpecies, variation_concept: str) -> CustomSpecies:
        """Generate a variant of an existing species"""
        prompt = self._create_prompt(
            "create a variant of this species",
            f"Base species: {json.dumps(base_species.to_dict())}\n"
            f"Variation concept: {variation_concept}\n\n"
            f"Create a variant of this species that incorporates the variation concept. "
            f"Maintain core elements but add unique twists based on the variation. "
            f"Return the complete variant species as JSON."
        )
        
        try:
            response = self.llm_service.generate_text(prompt)
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
            logger.error(f"Error generating variant species: {e}")
        
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
        """Generate a unique trait for a species"""
        prompt = self._create_prompt(
            "create a unique species trait",
            f"Species concept: {species_concept}\nPower level: {power_level}\n\n"
            f"Create a unique and thematic trait for this species that feels {power_level}. "
            f"The trait should be mechanically interesting but appropriate for D&D 5e. "
            f"Return a JSON object with 'name' and 'description' keys."
        )
        
        try:
            response = self.llm_service.generate_text(prompt)
            trait_data = self._extract_json(response)
            
            if trait_data and "name" in trait_data and "description" in trait_data:
                return {trait_data["name"]: trait_data["description"]}
        except Exception as e:
            logger.error(f"Error generating unique trait: {e}")
        
        # Fallback trait
        trait_name = f"{species_concept.split()[0].title()} Heritage"
        trait_desc = f"You have inherited unique abilities from your {species_concept} ancestry."
        return {trait_name: trait_desc}
    
    def adapt_cross_genre_concept(self, genre: str, concept_description: str) -> CustomSpecies:
        """Adapt concepts from other genres/universes to D&D mechanics"""
        prompt = self._create_prompt(
            f"adapt this {genre} concept to D&D mechanics",
            f"Source concept from {genre}: {concept_description}\n\n"
            f"Create a D&D species that captures the essence and abilities of this concept "
            f"using D&D 5e mechanics. Be creative with trait names and mechanics to preserve "
            f"the original feel while making it work in D&D. Don't restrict yourself to traditional fantasy."
        )
        
        try:
            response = self.llm_service.generate_text(prompt)
            species_data = self._extract_json(response)
            
            if species_data:
                # Convert size string to enum if needed
                if "size" in species_data and isinstance(species_data["size"], str):
                    try:
                        species_data["size"] = SpeciesSize[species_data["size"]]
                    except KeyError:
                        species_data["size"] = SpeciesSize.MEDIUM
                
                return CustomSpecies(**species_data)
        except Exception as e:
            logger.error(f"Error adapting cross-genre concept: {e}")
        
        # Fallback - create simplified concept
        return self.generate_complete_species(f"{genre}-inspired {concept_description}")
    
    def create_unrestricted_species(self, concept_description: str, power_level: str = "standard") -> CustomSpecies:
        """Create species with minimal D&D restrictions for maximum creative freedom"""
        # Temporarily disable restrictions for this call
        original_theme = self.theme_restrictions
        original_mechanics = self.mechanics_restrictions
        original_balance = self.allow_unbalanced
        
        try:
            self.theme_restrictions = False
            self.mechanics_restrictions = False
            self.allow_unbalanced = power_level in ["high", "unrestricted"]
            self._update_system_prompt()
            
            prompt = self._create_prompt(
                "create an unrestricted species concept",
                f"Concept: {concept_description}\nPower level: {power_level}\n\n"
                f"Create a highly creative species with unique abilities. Don't restrict yourself to "
                f"traditional D&D balance or theme restrictions. Focus on capturing the concept's essence. "
                f"If the power level is 'high' or 'unrestricted', don't worry about balance concerns."
            )
            
            response = self.llm_service.generate_text(prompt)
            species_data = self._extract_json(response)
            
            if species_data:
                # Convert size string to enum if needed
                if "size" in species_data and isinstance(species_data["size"], str):
                    try:
                        species_data["size"] = SpeciesSize[species_data["size"]]
                    except KeyError:
                        species_data["size"] = SpeciesSize.MEDIUM
                
                return CustomSpecies(**species_data)
        except Exception as e:
            logger.error(f"Error creating unrestricted species: {e}")
        finally:
            # Restore original settings
            self.theme_restrictions = original_theme
            self.mechanics_restrictions = original_mechanics
            self.allow_unbalanced = original_balance
            self._update_system_prompt()
        
        # Fallback
        return self.generate_complete_species(concept_description)
    
    def translate_special_abilities(self, abilities: List[str], source_media: str) -> Dict[str, str]:
        """Translate special abilities from other media into D&D mechanics"""
        abilities_str = "\n".join([f"- {ability}" for ability in abilities])
        prompt = self._create_prompt(
            "translate special abilities to D&D mechanics",
            f"Source media: {source_media}\nAbilities to translate:\n{abilities_str}\n\n"
            f"Translate these abilities from {source_media} into D&D 5e mechanics. "
            f"For each ability, create a trait name and mechanics description that "
            f"captures the essence of the original ability while fitting within D&D's system. "
            f"Return a JSON object mapping trait names to their descriptions."
        )
        
        try:
            response = self.llm_service.generate_text(prompt)
            translation_data = self._extract_json(response)
            
            if translation_data and isinstance(translation_data, dict):
                return translation_data
        except Exception as e:
            logger.error(f"Error translating special abilities: {e}")
        
        # Fallback - simple conversions
        result = {}
        for ability in abilities:
            name = ability.split()[0].title() + " Mastery"
            description = f"You have the ability to {ability.lower()}."
            result[name] = description
        return result
    
    def add_technological_elements(self, species: CustomSpecies, tech_level: str) -> CustomSpecies:
        """Add technological elements to a species for sci-fi or advanced settings"""
        prompt = self._create_prompt(
            "add technological elements to this species",
            f"Base species: {json.dumps(species.to_dict())}\nTech level: {tech_level}\n\n"
            f"Modify this species by adding technological elements appropriate to the specified tech level. "
            f"Add or modify traits to incorporate technology while preserving the core identity. "
            f"Return the complete modified species as JSON."
        )
        
        try:
            response = self.llm_service.generate_text(prompt)
            modified_data = self._extract_json(response)
            
            if modified_data:
                # Convert size string to enum if needed
                if "size" in modified_data and isinstance(modified_data["size"], str):
                    try:
                        modified_data["size"] = SpeciesSize[modified_data["size"]]
                    except KeyError:
                        modified_data["size"] = species.size
                
                return CustomSpecies(**modified_data)
        except Exception as e:
            logger.error(f"Error adding technological elements: {e}")
        
        # Fallback - add a single tech trait
        species_dict = species.to_dict()
        tech_traits = {
            "primitive": "Primitive Tools: You are proficient with one artisan's tool of your choice.",
            "industrial": "Industrial Knowledge: You know the Mending cantrip and can cast Fabricate once per long rest.",
            "advanced": "Advanced Tech: You have integrated technology that allows you to cast Detect Magic at will.",
            "futuristic": "Future Tech: You can cast Alter Self once per short rest using technology."
        }
        
        if "traits" not in species_dict:
            species_dict["traits"] = {}
        
        species_dict["traits"][f"{tech_level.capitalize()} Technology"] = tech_traits.get(
            tech_level.lower(), 
            f"You have access to {tech_level} technology that enhances your capabilities."
        )
        species_dict["name"] = f"Tech-Enhanced {species.name}"
        
        return CustomSpecies(**species_dict)
    
    def generate_custom_mechanics(self, concept: str, mechanic_type: str) -> Dict[str, Any]:
        """Generate wholly new mechanics based on a concept"""
        prompt = self._create_prompt(
            "create custom game mechanics",
            f"Concept: {concept}\nMechanic type: {mechanic_type}\n\n"
            f"Create custom D&D 5e mechanics that represent this concept. Focus on {mechanic_type} mechanics. "
            f"The mechanics should be innovative but still compatible with D&D's core rules. "
            f"Return a JSON object with 'name', 'description', and 'rules' fields."
        )
        
        try:
            response = self.llm_service.generate_text(prompt)
            mechanics_data = self._extract_json(response)
            
            if mechanics_data:
                return mechanics_data
        except Exception as e:
            logger.error(f"Error generating custom mechanics: {e}")
        
        # Fallback - basic mechanic
        return {
            "name": concept.split()[0].title() + " Technique",
            "description": f"A special ability based on {concept}.",
            "rules": f"When using this ability for {mechanic_type} situations, you gain advantage on related checks."
        }
    
    def suggest_class_synergies(self, species: CustomSpecies) -> Dict[str, str]:
        """Suggest D&D classes that would synergize well with a custom species"""
        prompt = self._create_prompt(
            "suggest class synergies",
            f"Species: {json.dumps(species.to_dict())}\n\n"
            f"Suggest which D&D classes would synergize well with this custom species. "
            f"For each recommended class, explain why it's a good match based on the species traits, "
            f"ability scores, and overall theme. Return a JSON object mapping class names to explanations."
        )
        
        try:
            response = self.llm_service.generate_text(prompt)
            synergies = self._extract_json(response)
            
            if synergies and isinstance(synergies, dict):
                return synergies
        except Exception as e:
            logger.error(f"Error suggesting class synergies: {e}")
        
        # Fallback - generic suggestions
        return {
            "Fighter": f"The {species.name}'s natural adaptability makes them suitable for the versatile fighter class.",
            "Ranger": f"The {species.name}'s connection to nature aligns well with the ranger's abilities."
        }
    
    def set_creative_parameters(self, allow_unbalanced: bool = False, 
                           theme_restrictions: bool = False,
                           mechanics_restrictions: bool = False) -> None:
        """Configure how strictly the advisor adheres to D&D conventions"""
        self.allow_unbalanced = allow_unbalanced
        self.theme_restrictions = theme_restrictions
        self.mechanics_restrictions = mechanics_restrictions
        
        # Update system prompt based on settings
        self._update_system_prompt()
    
    def convert_from_external_system(self, system: str, species_data: Dict[str, Any]) -> CustomSpecies:
        """Convert a species from another game system to D&D"""
        prompt = self._create_prompt(
            f"convert species from {system} to D&D 5e",
            f"Source system: {system}\nSpecies data: {json.dumps(species_data)}\n\n"
            f"Convert this species from {system} to D&D 5e mechanics. Preserve the core themes "
            f"and abilities but adapt them to fit D&D's rule system. Return the converted species as JSON."
        )
        
        try:
            response = self.llm_service.generate_text(prompt)
            converted_data = self._extract_json(response)
            
            if converted_data:
                # Convert size string to enum if needed
                if "size" in converted_data and isinstance(converted_data["size"], str):
                    try:
                        converted_data["size"] = SpeciesSize[converted_data["size"]]
                    except KeyError:
                        converted_data["size"] = SpeciesSize.MEDIUM
                
                return CustomSpecies(**converted_data)
        except Exception as e:
            logger.error(f"Error converting from external system: {e}")
        
        # Fallback - generic conversion
        name = species_data.get("name", f"Converted{system.capitalize()}")
        return CustomSpecies(
            name=name,
            description=f"A species converted from {system}.",
            traits={"Otherworldly Origin": f"You originated in a {system} setting, granting you unique perspective."}
        )
    
    def merge_species_concepts(self, species1: Union[str, CustomSpecies], 
                          species2: Union[str, CustomSpecies]) -> CustomSpecies:
        """Merge two species concepts into a hybrid species"""
        # Convert string concepts to dicts if needed
        sp1 = species1.to_dict() if isinstance(species1, CustomSpecies) else {"concept": species1}
        sp2 = species2.to_dict() if isinstance(species2, CustomSpecies) else {"concept": species2}
        
        prompt = self._create_prompt(
            "merge two species concepts",
            f"Species 1: {json.dumps(sp1)}\nSpecies 2: {json.dumps(sp2)}\n\n"
            f"Create a hybrid species that combines elements from both input species. "
            f"The hybrid should have a unique identity while incorporating key traits, "
            f"themes and abilities from both sources. Return the complete hybrid species as JSON."
        )
        
        try:
            response = self.llm_service.generate_text(prompt)
            hybrid_data = self._extract_json(response)
            
            if hybrid_data:
                # Convert size string to enum if needed
                if "size" in hybrid_data and isinstance(hybrid_data["size"], str):
                    try:
                        hybrid_data["size"] = SpeciesSize[hybrid_data["size"]]
                    except KeyError:
                        hybrid_data["size"] = SpeciesSize.MEDIUM
                
                return CustomSpecies(**hybrid_data)
        except Exception as e:
            logger.error(f"Error merging species concepts: {e}")
        
        # Fallback - simple hybrid
        name1 = sp1.get("name", str(species1).split()[0])
        name2 = sp2.get("name", str(species2).split()[0])
        
        return CustomSpecies(
            name=f"{name1}-{name2} Hybrid",
            description=f"A hybrid species combining traits from {name1} and {name2}.",
            traits={"Hybrid Vigor": "Your mixed heritage grants you adaptability and resilience."}
        )
    
    def generate_evolutionary_variants(self, base_species: CustomSpecies, 
                                  environment: str) -> List[CustomSpecies]:
        """Generate evolutionary variants adapted to different environments"""
        prompt = self._create_prompt(
            "create environmental variants",
            f"Base species: {json.dumps(base_species.to_dict())}\nEnvironment: {environment}\n\n"
            f"Create an evolutionary variant of this species adapted to the specified environment. "
            f"Modify traits, abilities, and appearance to reflect adaptations to this environment. "
            f"Return the evolved variant as JSON."
        )
        
        try:
            response = self.llm_service.generate_text(prompt)
            variant_data = self._extract_json(response)
            
            if variant_data:
                # Convert size string to enum if needed
                if "size" in variant_data and isinstance(variant_data["size"], str):
                    try:
                        variant_data["size"] = SpeciesSize[variant_data["size"]]
                    except KeyError:
                        variant_data["size"] = base_species.size
                
                # Ensure different name
                if "name" not in variant_data or variant_data["name"] == base_species.name:
                    variant_data["name"] = f"{environment.capitalize()} {base_species.name}"
                    
                return [CustomSpecies(**variant_data)]
        except Exception as e:
            logger.error(f"Error generating evolutionary variants: {e}")
        
        # Fallback - basic variant
        base_dict = base_species.to_dict()
        base_dict["name"] = f"{environment.capitalize()} {base_species.name}"
        base_dict["custom_id"] = None
        
        env_traits = {
            "desert": "Desert Adaptation: You require half as much water as normal and have resistance to fire damage.",
            "underwater": "Water Breathing: You can breathe underwater and have a swim speed equal to your walking speed.",
            "volcanic": "Heat Resistance: You have resistance to fire damage and can tolerate extreme heat.",
            "arctic": "Cold Adaptation: You have resistance to cold damage and can tolerate extreme cold."
        }
        
        if "traits" not in base_dict:
            base_dict["traits"] = {}
            
        base_dict["traits"][f"{environment.capitalize()} Adaptation"] = env_traits.get(
            environment.lower(), 
            f"You have adapted to {environment} environments, granting you special survival capabilities."
        )
        
        return [CustomSpecies(**base_dict)]
    
    def export_to_format(self, species: CustomSpecies, format: str = "json") -> str:
        """Export species data to various formats for sharing/saving"""
        if format.lower() == "json":
            return json.dumps(species.to_dict(), indent=2)
            
        elif format.lower() == "markdown":
            # Create markdown documentation
            md = f"# {species.name}\n\n"
            md += f"## Description\n{species.description}\n\n"
            md += f"## Physical Traits\n{getattr(species, 'physical_traits', 'No information')}\n\n"
            md += f"## Culture\n{getattr(species, 'culture', 'No information')}\n\n"
            
            md += "## Game Statistics\n"
            md += f"- **Size:** {species.size.name if hasattr(species, 'size') else 'MEDIUM'}\n"
            md += f"- **Speed:** {getattr(species, 'speed', '30')} feet\n"
            
            if hasattr(species, 'ability_bonuses') and species.ability_bonuses:
                md += "- **Ability Score Increases:** "
                bonuses = []
                for ability, bonus in species.ability_bonuses.items():
                    bonuses.append(f"{ability.capitalize()} +{bonus}")
                md += ", ".join(bonuses) + "\n"
                
            md += "\n## Traits\n"
            if hasattr(species, 'traits') and species.traits:
                for trait_name, description in species.traits.items():
                    md += f"### {trait_name}\n{description}\n\n"
            else:
                md += "No special traits.\n"
                
            return md
            
        elif format.lower() == "homebrewery":
            # Create GM Binder / Homebrewery compatible markdown
            hb = "{{monster,frame\n"
            hb += f"## {species.name}\n"
            hb += "_A custom species for D&D 5th Edition_\n"
            hb += "___\n"
            hb += f"**Size.** {species.size.name if hasattr(species, 'size') else 'Medium'}\n"
            hb += f"**Speed.** {getattr(species, 'speed', '30')} feet\n"
            
            if hasattr(species, 'ability_bonuses') and species.ability_bonuses:
                hb += "**Ability Score Increase.** "
                bonuses = []
                for ability, bonus in species.ability_bonuses.items():
                    bonuses.append(f"{ability.capitalize()} +{bonus}")
                hb += ", ".join(bonuses) + "\n"
                
            if hasattr(species, 'traits') and species.traits:
                for trait_name, description in species.traits.items():
                    hb += f"**{trait_name}.** {description}\n"
            
            hb += "}}\n\n"
            hb += f"### Description\n{species.description}\n"
            return hb
            
        else:
            return json.dumps(species.to_dict())