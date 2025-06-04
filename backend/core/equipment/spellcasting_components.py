# spellcasting_components.py
# Description: Handles items needed for spellcasting including foci and material components

from typing import Dict, List, Optional, Union, Any, Tuple
import json
import re
from enum import Enum

from backend.core.equipment.equipment import Equipment, EquipmentCategory, RarityType

class ComponentType(Enum):
    """Types of spellcasting components"""
    ARCANE_FOCUS = "arcane_focus"     # Used by wizards, sorcerers, and warlocks
    DRUIDIC_FOCUS = "druidic_focus"   # Used by druids
    HOLY_SYMBOL = "holy_symbol"       # Used by clerics and paladins
    MATERIAL = "material"             # Physical components consumed during casting
    COMPONENT_POUCH = "component_pouch"  # Contains common material components
    SPELLBOOK = "spellbook"           # For preparing and recording spells
    MUSICAL_INSTRUMENT = "musical_instrument"  # Can be used as a focus by bards
    SPECIAL = "special"               # Unusual or specific components

class FocusProperty(Enum):
    """Special properties that spellcasting foci can have"""
    CONDUCTIVE = "conductive"          # Better conducts magical energy
    RESONANT = "resonant"              # Enhances certain types of spells
    DURABLE = "durable"                # More resistant to damage
    ATTUNED = "attuned"                # Well-attuned to its wielder
    EFFICIENT = "efficient"            # Reduces component costs for some spells
    DISTINCTIVE = "distinctive"        # Visually distinctive or impressive
    CONCEALED = "concealed"            # Can be hidden or disguised
    TRADITIONAL = "traditional"        # Made using traditional methods
    PERSONALIZED = "personalized"      # Customized for the spellcaster
    AMPLIFYING = "amplifying"          # Slightly increases spell range/area
    FOCUSING = "focusing"              # Helps with concentration
    ORNATE = "ornate"                  # Elaborately decorated
    PLAIN = "plain"                    # Simple and unadorned
    ILLUMINATING = "illuminating"      # Provides light when casting
    UNUSUAL = "unusual"                # Strange or exotic in design

class SpellcastingComponents(Equipment):
    """
    Class for handling spellcasting components, foci, and related spellcasting items.
    
    Extends the Equipment class with functionality for creating, customizing, and
    managing items needed for spellcasting in D&D 5e.
    """
    
    def __init__(self, llm_service=None):
        """Initialize the spellcasting components manager with parent equipment functionality."""
        super().__init__(llm_service)
        
        # Additional spellcasting component configuration
        self.class_component_mapping = {
            "wizard": ["arcane_focus", "spellbook", "component_pouch"],
            "sorcerer": ["arcane_focus", "component_pouch"],
            "warlock": ["arcane_focus", "component_pouch"],
            "cleric": ["holy_symbol", "component_pouch"],
            "druid": ["druidic_focus", "component_pouch"],
            "paladin": ["holy_symbol"],
            "ranger": ["component_pouch"],
            "bard": ["musical_instrument", "component_pouch"],
            "artificer": ["arcane_focus", "thieves_tools", "component_pouch"]
        }
        
        # Map of material components for common spells
        self.common_material_components = {
            "identify": {"pearl": {"value": {"gp": 100}, "consumed": False}},
            "chromatic orb": {"diamond": {"value": {"gp": 50}, "consumed": False}},
            "revivify": {"diamonds": {"value": {"gp": 300}, "consumed": True}},
            "raise dead": {"diamonds": {"value": {"gp": 500}, "consumed": True}},
            "hero's feast": {"jeweled bowl": {"value": {"gp": 1000}, "consumed": False}},
            "resurrection": {"diamonds": {"value": {"gp": 1000}, "consumed": True}},
            "true resurrection": {"diamonds": {"value": {"gp": 25000}, "consumed": True}}
        }
        
        # Arcane focus types
        self.arcane_focus_types = ["orb", "crystal", "rod", "staff", "wand", "other"]
        
        # Holy symbol types
        self.holy_symbol_types = ["amulet", "emblem", "reliquary", "vestment"]
        
        # Druidic focus types
        self.druidic_focus_types = ["sprig_of_mistletoe", "totem", "wooden_staff", 
                                   "yew_wand", "natural_object"]
    
    def get_components_by_type(self, component_type: Union[ComponentType, str]) -> List[Dict[str, Any]]:
        """
        Get components filtered by type.
        
        Args:
            component_type: Type to filter by (enum or string)
            
        Returns:
            List[Dict[str, Any]]: List of components of the type
        """
        if isinstance(component_type, str):
            # Try to convert string to enum
            try:
                component_type = ComponentType(component_type.lower())
            except ValueError:
                # If not a valid type, return empty list
                return []
        
        # Look in all categories since components might be scattered in different collections
        results = []
        
        # Check all equipment categories
        for collection in [self.gear, self.trinkets]:
            for item_id, item_data in collection.items():
                if "component_type" in item_data and item_data["component_type"] == component_type:
                    results.append(item_data)
        
        return results
    
    def get_components_for_class(self, character_class: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get appropriate spellcasting components for a character class.
        
        Args:
            character_class: Character class
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: Components organized by type
        """
        class_key = character_class.lower()
        results = {}
        
        if class_key in self.class_component_mapping:
            component_types = self.class_component_mapping[class_key]
            
            for comp_type in component_types:
                try:
                    enum_type = ComponentType(comp_type)
                    components = self.get_components_by_type(enum_type)
                    results[comp_type] = components
                except ValueError:
                    # If not a valid enum value, skip
                    continue
        
        return results
    
    def get_material_component_for_spell(self, spell_name: str) -> Optional[Dict[str, Any]]:
        """
        Get material component information for a specific spell.
        
        Args:
            spell_name: Name of the spell
            
        Returns:
            Optional[Dict[str, Any]]: Material component details if required
        """
        spell_key = spell_name.lower()
        
        if spell_key in self.common_material_components:
            return self.common_material_components[spell_key]
        
        return None
    
    def create_custom_focus(self, 
                         name: str,
                         component_type: ComponentType,
                         description: str = None,
                         properties: List[str] = None,
                         cost: Dict[str, int] = None,
                         weight: float = 1.0) -> Dict[str, Any]:
        """
        Create a custom spellcasting focus.
        
        Args:
            name: Name of the focus
            component_type: Type of component
            description: Description of the focus
            properties: List of focus properties
            cost: Cost in currency values
            weight: Weight in pounds
            
        Returns:
            Dict[str, Any]: Created focus data
        """
        if description is None:
            if component_type == ComponentType.ARCANE_FOCUS:
                description = "A handheld item used to channel arcane magic."
            elif component_type == ComponentType.DRUIDIC_FOCUS:
                description = "An object that channels the powers of nature."
            elif component_type == ComponentType.HOLY_SYMBOL:
                description = "A symbol representing a deity or pantheon."
            elif component_type == ComponentType.COMPONENT_POUCH:
                description = "A small pouch containing common spell components."
            elif component_type == ComponentType.SPELLBOOK:
                description = "A book for recording and preparing spells."
            else:
                description = "An item used in spellcasting."
        
        # Set default cost if none provided
        if cost is None:
            if component_type == ComponentType.ARCANE_FOCUS:
                cost = {"gp": 10}
            elif component_type == ComponentType.DRUIDIC_FOCUS:
                cost = {"gp": 5}
            elif component_type == ComponentType.HOLY_SYMBOL:
                cost = {"gp": 5}
            elif component_type == ComponentType.COMPONENT_POUCH:
                cost = {"gp": 25}
            elif component_type == ComponentType.SPELLBOOK:
                cost = {"gp": 50}
            else:
                cost = {"gp": 10}
        
        # Generate focus ID
        focus_id = f"{component_type.value}_{name.lower().replace(' ', '_')}"
        
        # Create the focus data
        focus_data = {
            "id": focus_id,
            "name": name,
            "category": EquipmentCategory.ADVENTURING_GEAR,
            "component_type": component_type,
            "description": description,
            "cost": cost,
            "weight": weight
        }
        
        # Add properties if provided
        if properties:
            focus_data["properties"] = properties
        
        # Add to gear collection
        self.gear[focus_id] = focus_data
        
        return focus_data
    
    def enhance_focus_with_llm(self, 
                            focus_id: str, 
                            enhancement_type: str = "description",
                            character_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Enhance a spellcasting focus with LLM-generated content.
        
        Args:
            focus_id: ID of the focus to enhance
            enhancement_type: Type of enhancement (description, history, affinity)
            character_data: Optional character data for personalization
            
        Returns:
            Dict[str, Any]: Enhanced focus data
        """
        focus_data = self._find_item_by_id(focus_id)
        if not focus_data or "component_type" not in focus_data:
            return {"error": "Focus item not found"}
            
        # Create a copy to avoid modifying the original
        enhanced_focus = focus_data.copy()
        
        if enhancement_type.lower() == "description":
            # Generate enhanced physical description
            prompt = self.llm_advisor._create_prompt(
                "enhance spellcasting focus description",
                f"Focus: {focus_data.get('name')}\n"
                f"Type: {focus_data.get('component_type').value if isinstance(focus_data.get('component_type'), ComponentType) else 'unknown'}\n"
                f"Current Description: {focus_data.get('description', '')}\n\n"
                "Create a rich, detailed physical description of this spellcasting focus that brings it to life. "
                "Describe its appearance, materials, craftsmanship, any decorative elements, how it feels to hold, "
                "and any subtle magical qualities it might possess (without providing mechanical benefits). "
                "The description should help a player visualize and connect with their character's spellcasting tool."
            )
            
            try:
                response = self.llm_advisor.llm_service.generate(prompt)
                
                # Clean up the response
                clean_response = re.sub(r'```.*?```', '', response, flags=re.DOTALL)
                clean_response = re.sub(r'\{.*?\}', '', clean_response, flags=re.DOTALL)
                
                enhanced_focus["detailed_description"] = clean_response.strip()
            except Exception as e:
                print(f"Error enhancing focus description: {e}")
                enhanced_focus["detailed_description"] = focus_data.get("description", "A standard spellcasting focus.")
                
        elif enhancement_type.lower() == "history":
            # Generate focus history
            prompt = self.llm_advisor._create_prompt(
                "create spellcasting focus history",
                f"Focus: {focus_data.get('name')}\n"
                f"Type: {focus_data.get('component_type').value if isinstance(focus_data.get('component_type'), ComponentType) else 'unknown'}\n\n"
                "Create an interesting history for this spellcasting focus, including where it came from, "
                "who might have crafted or used it before, notable magical events it may have been involved in, "
                "and how it might have come into the character's possession. The history should add depth "
                "and narrative hooks for this important magical tool."
            )
            
            try:
                response = self.llm_advisor.llm_service.generate(prompt)
                enhanced_focus["history"] = response
            except Exception as e:
                print(f"Error generating focus history: {e}")
                enhanced_focus["history"] = f"This {focus_data.get('name')} has a history yet to be uncovered."
            
        elif enhancement_type.lower() == "affinity":
            # Generate spell affinities based on the focus
            char_context = ""
            if character_data:
                char_context = (f"Character Class: {character_data.get('class', 'Unknown')}\n"
                              f"Character Level: {character_data.get('level', 'Unknown')}\n"
                              f"Spellcasting Style: {character_data.get('spellcasting_style', 'Unknown')}\n\n")
                
            prompt = self.llm_advisor._create_prompt(
                "create spellcasting focus affinities",
                f"Focus: {focus_data.get('name')}\n"
                f"Type: {focus_data.get('component_type').value if isinstance(focus_data.get('component_type'), ComponentType) else 'unknown'}\n"
                f"{char_context}"
                "Describe which types of spells or magical effects this focus seems to have a particular "
                "affinity or resonance with. This should not provide mechanical bonuses, but rather suggest "
                "narrative flourishes for how certain types of spells might look or feel when cast using "
                "this specific focus. Consider the focus's materials, design, history, and other qualities "
                "when determining its affinities."
                "Return as JSON with 'primary_affinity', 'secondary_affinity', 'visual_effects', and 'roleplay_suggestions' keys."
            )
            
            try:
                response = self.llm_advisor.llm_service.generate(prompt)
                affinity_data = self.llm_advisor._extract_json(response)
                
                if affinity_data:
                    enhanced_focus["spell_affinities"] = affinity_data
                else:
                    enhanced_focus["spell_affinities"] = {
                        "primary_affinity": "No particular affinity detected",
                        "visual_effects": "Standard magical effects"
                    }
            except Exception as e:
                print(f"Error generating focus affinities: {e}")
                enhanced_focus["spell_affinities"] = {
                    "primary_affinity": "No particular affinity detected",
                    "visual_effects": "Standard magical effects"
                }
        
        return enhanced_focus
    
    def recommend_focus_for_character(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recommend an appropriate focus for a specific character.
        
        Args:
            character_data: Character details including class, background, etc.
            
        Returns:
            Dict[str, Any]: Focus recommendations with rationale
        """
        character_class = character_data.get("class", "").lower()
        background = character_data.get("background", "").lower()
        personality = character_data.get("personality", "")
        backstory = character_data.get("backstory", "")
        
        # Determine appropriate component type for class
        component_types = []
        if character_class in self.class_component_mapping:
            for comp_type in self.class_component_mapping[character_class]:
                try:
                    component_types.append(ComponentType(comp_type))
                except ValueError:
                    pass
        
        if not component_types:
            return {"error": "No suitable component types for this class"}
        
        # Use LLM to recommend a focus
        prompt = self.llm_advisor._create_prompt(
            "recommend spellcasting focus",
            f"Character Class: {character_data.get('class')}\n"
            f"Background: {background}\n"
            f"Personality: {personality}\n"
            f"Backstory Excerpt: {backstory[:200] + '...' if len(backstory) > 200 else backstory}\n"
            f"Available Component Types: {', '.join([ct.value for ct in component_types])}\n\n"
            "Recommend appropriate spellcasting focuses or components for this character based on "
            "their class, personality, and background. Include specific suggestions for appearance, "
            "materials, and style that would suit the character thematically. Explain why each "
            "recommendation would be particularly fitting for this character."
            "Return as JSON with 'primary_recommendation', 'alternative_options', 'appearance_suggestions', and 'thematic_reasons' keys."
        )
        
        try:
            response = self.llm_advisor.llm_service.generate(prompt)
            recommendations = self.llm_advisor._extract_json(response)
            
            if recommendations:
                return {
                    "character_class": character_data.get("class"),
                    "focus_recommendations": recommendations
                }
        except Exception as e:
            print(f"Error recommending focus: {e}")
        
        # Fallback response
        return {
            "character_class": character_data.get("class"),
            "focus_recommendations": {
                "primary_recommendation": f"Standard {component_types[0].value if component_types else 'focus'}",
                "alternative_options": ["Component pouch"],
                "appearance_suggestions": "Design based on character background",
                "thematic_reasons": "Matches character class requirements"
            }
        }
    
    def create_material_component_kit(self, 
                                   character_class: str,
                                   spell_levels: List[int] = [0, 1],
                                   exclude_expensive: bool = True) -> Dict[str, Any]:
        """
        Create a kit of material components for spells a character might know.
        
        Args:
            character_class: Class of the character
            spell_levels: Levels of spells to include components for
            exclude_expensive: Whether to exclude components costing over 25gp
            
        Returns:
            Dict[str, Any]: Material component kit details
        """
        # Use LLM to generate appropriate component kit
        prompt = self.llm_advisor._create_prompt(
            "create material component kit",
            f"Character Class: {character_class}\n"
            f"Spell Levels: {', '.join(map(str, spell_levels))}\n"
            f"Exclude Expensive Components: {exclude_expensive}\n\n"
            f"Create a detailed kit of material components that a {character_class} would carry for "
            f"casting spells of levels {', '.join(map(str, spell_levels))}. Include common components "
            f"used in multiple spells, as well as specific components for signature spells of this class. "
            f"{'Exclude components costing over 25gp.' if exclude_expensive else 'Include some expensive components.'} "
            f"For each component, list the spells it could be used for and any special storage considerations."
            "Return as JSON with 'kit_name', 'common_components', 'specific_components', 'storage_container', and 'total_weight' keys."
        )
        
        try:
            response = self.llm_advisor.llm_service.generate(prompt)
            kit_data = self.llm_advisor._extract_json(response)
            
            if kit_data:
                # Generate an ID for the kit
                kit_id = f"component_kit_{character_class.lower()}"
                
                # Create a proper item object
                kit_item = {
                    "id": kit_id,
                    "name": kit_data.get("kit_name", f"{character_class} Component Kit"),
                    "category": EquipmentCategory.ADVENTURING_GEAR,
                    "component_type": ComponentType.MATERIAL,
                    "description": f"A collection of material components for {character_class} spells.",
                    "components": {
                        "common": kit_data.get("common_components", []),
                        "specific": kit_data.get("specific_components", [])
                    },
                    "storage": kit_data.get("storage_container", "Simple pouch"),
                    "weight": kit_data.get("total_weight", 1.0),
                    "cost": {"gp": 5}  # Basic kit cost
                }
                
                # Add to gear collection
                self.gear[kit_id] = kit_item
                
                return kit_item
        except Exception as e:
            print(f"Error creating component kit: {e}")
        
        # Fallback kit
        fallback_kit = {
            "id": f"component_kit_{character_class.lower()}",
            "name": f"{character_class} Component Kit",
            "category": EquipmentCategory.ADVENTURING_GEAR,
            "component_type": ComponentType.MATERIAL,
            "description": f"A basic collection of material components for {character_class} spells.",
            "components": {
                "common": ["Pinch of sand", "Small feather", "Bit of phosphorus"],
                "specific": ["As required for specific spells"]
            },
            "storage": "Component pouch",
            "weight": 2.0,
            "cost": {"gp": 5}
        }
        
        # Add to gear collection
        self.gear[fallback_kit["id"]] = fallback_kit
        
        return fallback_kit
    
    def check_component_requirements(self, 
                                  spell_name: str, 
                                  inventory: List[Dict[str, Any]],
                                  has_component_pouch: bool = False) -> Dict[str, Any]:
        """
        Check if a character has the required components for a spell.
        
        Args:
            spell_name: Name of the spell to cast
            inventory: Character's inventory items
            has_component_pouch: Whether the character has a component pouch
            
        Returns:
            Dict[str, Any]: Component availability check results
        """
        # Get material component requirements
        component_req = self.get_material_component_for_spell(spell_name)
        
        # If no special material components required, or component pouch covers it
        if not component_req:
            return {
                "spell": spell_name,
                "components_required": False,
                "has_requirements": True,
                "notes": "No material components required or all components are trivial."
            }
            
        # Check for expensive components
        expensive_components = {}
        for component_name, details in component_req.items():
            value = details.get("value", {})
            # Calculate value in copper pieces for comparison
            value_cp = 0
            if "cp" in value:
                value_cp += value["cp"]
            if "sp" in value:
                value_cp += value["sp"] * 10
            if "gp" in value:
                value_cp += value["gp"] * 100
                
            # If component costs money, component pouch doesn't cover it
            if value_cp > 0:
                expensive_components[component_name] = {
                    "value": value,
                    "consumed": details.get("consumed", False)
                }
        
        # If no expensive components and has component pouch
        if not expensive_components and has_component_pouch:
            return {
                "spell": spell_name,
                "components_required": True,
                "has_requirements": True,
                "covered_by_pouch": True,
                "notes": "All required components are covered by component pouch."
            }
        
        # Check inventory for expensive components
        missing_components = {}
        for component_name, details in expensive_components.items():
            component_found = False
            
            # Look for the component in inventory
            for item in inventory:
                if component_name.lower() in item.get("name", "").lower():
                    component_found = True
                    break
                    
            if not component_found:
                missing_components[component_name] = details
        
        # Return results
        if missing_components:
            return {
                "spell": spell_name,
                "components_required": True,
                "has_requirements": False,
                "missing_components": missing_components,
                "notes": f"Missing required components: {', '.join(missing_components.keys())}."
            }
        else:
            return {
                "spell": spell_name,
                "components_required": True,
                "has_requirements": True,
                "expensive_components": expensive_components,
                "notes": "All required components are present in inventory."
            }
    
    def describe_spellcasting_visuals(self, 
                                   spell_name: str,
                                   focus_id: str = None,
                                   character_data: Dict[str, Any] = None) -> str:
        """
        Generate a description of how a spell looks when cast with a specific focus.
        
        Args:
            spell_name: Name of the spell being cast
            focus_id: ID of the spellcasting focus used
            character_data: Optional character data for context
            
        Returns:
            str: Description of spellcasting visuals
        """
        # Get focus data if provided
        focus_data = None
        if focus_id:
            focus_data = self._find_item_by_id(focus_id)
        
        # Build character context
        char_context = ""
        if character_data:
            char_context = f"Character: {character_data.get('name', 'Unknown')}, "
            char_context += f"a {character_data.get('race', 'unknown')} {character_data.get('class', 'spellcaster')}\n"
            
            if "spellcasting_style" in character_data:
                char_context += f"Spellcasting Style: {character_data['spellcasting_style']}\n"
        
        # Build focus context
        focus_context = ""
        if focus_data:
            focus_context = f"Spellcasting Focus: {focus_data.get('name')}\n"
            focus_context += f"Focus Type: {focus_data.get('component_type').value if isinstance(focus_data.get('component_type'), ComponentType) else 'unknown'}\n"
            focus_context += f"Description: {focus_data.get('description', '')}\n"
            
            # Add focus affinities if they exist
            if "spell_affinities" in focus_data:
                affinities = focus_data["spell_affinities"]
                if "primary_affinity" in affinities:
                    focus_context += f"Primary Affinity: {affinities['primary_affinity']}\n"
                if "visual_effects" in affinities:
                    focus_context += f"Visual Effects: {affinities['visual_effects']}\n"
        
        # Create prompt for LLM
        prompt = self.llm_advisor._create_prompt(
            "describe spellcasting visuals",
            f"Spell: {spell_name}\n"
            f"{focus_context}\n"
            f"{char_context}\n\n"
            "Create a vivid, detailed description of how this spell appears when cast, including "
            "the gestures, verbal components, and visual effects. Describe how the magic flows "
            "through or interacts with the spellcasting focus, and any unique sensory details "
            "that would be apparent to observers. The description should help a player narrate "
            "their spellcasting in an evocative and memorable way."
        )
        
        try:
            response = self.llm_advisor.llm_service.generate(prompt)
            
            # Clean up the response by removing any JSON formatting
            clean_response = re.sub(r'```.*?```', '', response, flags=re.DOTALL)
            clean_response = re.sub(r'\{.*?\}', '', clean_response, flags=re.DOTALL)
            
            return clean_response.strip()
        except Exception as e:
            print(f"Error generating spellcasting visuals: {e}")
            
        # Fallback description
        return f"As you cast {spell_name}, the magic flows through your focus, culminating in the spell's effect."