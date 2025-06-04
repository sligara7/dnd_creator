# trinkets.py
# Description: Handles small, unique items that provide flavor and sometimes minor bonuses

from typing import Dict, List, Optional, Union, Any, Tuple
import json
import re
import random
from enum import Enum

from backend.core.equipment.equipment import Equipment, EquipmentCategory, RarityType

class TrinketOrigin(Enum):
    """Origins or themes of trinkets"""
    ARCANE = "arcane"           # Associated with magic or magical phenomena
    NATURAL = "natural"         # From nature (plants, animals, natural formations)
    RELIGIOUS = "religious"     # Connected to deities or religious practices
    HISTORICAL = "historical"   # Remnants of past civilizations or events
    PERSONAL = "personal"       # Items of personal significance
    BIZARRE = "bizarre"         # Strange and unusual items
    OMINOUS = "ominous"         # Unsettling or disturbing items
    MONSTROUS = "monstrous"     # From monsters or magical creatures
    PLANAR = "planar"           # Associated with other planes of existence
    CULTURAL = "cultural"       # Specific to a particular culture or society
    MARITIME = "maritime"       # Related to seas, oceans, or sailing
    UNDERGROUND = "underground" # Found in caves, dungeons, or the Underdark

class TrinketProperty(Enum):
    """Special properties that trinkets might have"""
    GLOWS_IN_DARK = "glows_in_dark"
    CHANGES_COLOR = "changes_color"
    STRANGE_ODOR = "strange_odor"
    FEELS_UNUSUAL = "feels_unusual"
    MAKES_SOUND = "makes_sound"
    ALWAYS_WARM = "always_warm"
    ALWAYS_COLD = "always_cold"
    NEVER_GETS_DIRTY = "never_gets_dirty"
    SLIGHTLY_LEVITATES = "slightly_levitates"
    ATTRACTS_SMALL_CREATURES = "attracts_small_creatures"
    REPELS_INSECTS = "repels_insects"
    MILD_ILLUSION = "mild_illusion"
    FAINT_AURA = "faint_aura"
    UNBREAKABLE = "unbreakable"
    COMPASS_LIKE = "compass_like"
    SLIGHTLY_LUCKY = "slightly_lucky"
    UNSETTLING = "unsettling"
    MOOD_REFLECTING = "mood_reflecting"
    APPEARS_IN_DREAMS = "appears_in_dreams"
    NEVER_GETS_WET = "never_gets_wet"

class Trinkets(Equipment):
    """
    Class for handling trinkets - small, unique items that provide flavor and sometimes minor bonuses.
    
    Extends the Equipment class with trinket-specific functionality for creating, 
    generating, and enhancing trinkets for character flavor and minor benefits.
    """
    
    def __init__(self, llm_service=None):
        """Initialize the trinkets manager with parent equipment functionality."""
        super().__init__(llm_service)
        
        # Additional trinket configuration
        self.character_trinket_mapping = {
            "backgrounds": {
                "noble": ["signet_ring", "family_crest", "small_portrait", "silk_handkerchief"],
                "criminal": ["lucky_charm", "marked_cards", "small_knife", "wanted_poster"],
                "sage": ["ancient_text", "unusual_quill", "star_chart", "peculiar_lens"],
                "soldier": ["medal", "trophy", "enemy_insignia", "broken_weapon"],
                "hermit": ["religious_icon", "animal_tooth", "strange_herb", "crude_map"],
                "outlander": ["tribal_fetish", "unusual_pelt", "foreign_coin", "trophy"],
                "acolyte": ["holy_symbol", "prayer_book", "religious_token", "ceremonial_item"]
            },
            "classes": {
                "wizard": ["arcane_trinket", "strange_component", "miniature_familiar", "glowing_crystal"],
                "cleric": ["religious_keepsake", "symbolic_relic", "blessed_token", "ceremonial_item"],
                "fighter": ["lucky_charm", "old_banner", "trophy", "battle_memento"],
                "rogue": ["shiny_bauble", "loaded_dice", "unusual_lockpick", "mysterious_key"],
                "ranger": ["animal_fetish", "unusual_plant", "creature_trophy", "natural_curiosity"],
                "bard": ["unusual_instrument", "theater_mask", "poetry_fragment", "exotic_token"],
                "druid": ["strange_seed", "unusual_stone", "animal_token", "wooden_figurine"],
                "warlock": ["patron_token", "eldritch_symbol", "strange_crystal", "whisper_stone"]
            }
        }
        
        # Properties that can be influenced by origin
        self.origin_property_tendencies = {
            TrinketOrigin.ARCANE: [TrinketProperty.GLOWS_IN_DARK, TrinketProperty.FAINT_AURA, TrinketProperty.MILD_ILLUSION],
            TrinketOrigin.NATURAL: [TrinketProperty.STRANGE_ODOR, TrinketProperty.ATTRACTS_SMALL_CREATURES, TrinketProperty.REPELS_INSECTS],
            TrinketOrigin.RELIGIOUS: [TrinketProperty.NEVER_GETS_DIRTY, TrinketProperty.FAINT_AURA, TrinketProperty.ALWAYS_WARM],
            TrinketOrigin.OMINOUS: [TrinketProperty.UNSETTLING, TrinketProperty.ALWAYS_COLD, TrinketProperty.STRANGE_ODOR],
            TrinketOrigin.PLANAR: [TrinketProperty.SLIGHTLY_LEVITATES, TrinketProperty.COMPASS_LIKE, TrinketProperty.APPEARS_IN_DREAMS]
        }
    
    def get_trinkets_by_origin(self, origin: Union[TrinketOrigin, str]) -> List[Dict[str, Any]]:
        """
        Get trinkets filtered by origin.
        
        Args:
            origin: Origin to filter by (enum or string)
            
        Returns:
            List[Dict[str, Any]]: List of trinkets from the origin
        """
        if isinstance(origin, str):
            # Try to convert string to enum
            try:
                origin = TrinketOrigin(origin.lower())
            except ValueError:
                # If not a valid origin, return empty list
                return []
        
        return [
            t for t in self.trinkets.values() 
            if "origin" in t and t["origin"] == origin
        ]
    
    def get_trinkets_by_property(self, property_name: Union[TrinketProperty, str]) -> List[Dict[str, Any]]:
        """
        Get trinkets that have a specific property.
        
        Args:
            property_name: Property to filter by (enum or string)
            
        Returns:
            List[Dict[str, Any]]: List of trinkets with the property
        """
        property_str = property_name.value if isinstance(property_name, TrinketProperty) else str(property_name).lower()
        
        return [
            t for t in self.trinkets.values() 
            if "properties" in t and any(property_str in prop.lower() for prop in t["properties"])
        ]
    
    def get_trinkets_for_character(self, background: str = None, 
                                character_class: str = None, 
                                backstory: str = None,
                                count: int = 1) -> List[Dict[str, Any]]:
        """
        Get appropriate trinkets for a character based on their background and class.
        
        Args:
            background: Character background
            character_class: Character class
            backstory: Character backstory for LLM matching
            count: Number of trinkets to return
            
        Returns:
            List[Dict[str, Any]]: List of suitable trinkets
        """
        suitable_trinkets = []
        
        # First collect trinkets based on background
        if background and background.lower() in self.character_trinket_mapping["backgrounds"]:
            trinket_ids = self.character_trinket_mapping["backgrounds"][background.lower()]
            for trinket_id in trinket_ids:
                trinket = self._find_item_by_id(trinket_id)
                if trinket:
                    suitable_trinkets.append(trinket)
        
        # Then collect trinkets based on class
        if character_class and character_class.lower() in self.character_trinket_mapping["classes"]:
            trinket_ids = self.character_trinket_mapping["classes"][character_class.lower()]
            for trinket_id in trinket_ids:
                trinket = self._find_item_by_id(trinket_id)
                if trinket and trinket not in suitable_trinkets:
                    suitable_trinkets.append(trinket)
        
        # If we don't have enough trinkets, or if backstory is provided, use LLM
        if len(suitable_trinkets) < count or backstory:
            # Use LLM to select or generate appropriate trinkets
            llm_trinkets = self.llm_advisor.recommend_trinkets(
                background=background,
                character_class=character_class,
                backstory=backstory,
                count=max(1, count - len(suitable_trinkets))
            )
            
            # Add LLM suggestions that aren't already in the list
            for trinket in llm_trinkets:
                existing_names = [t.get("name", "").lower() for t in suitable_trinkets]
                if trinket.get("name", "").lower() not in existing_names:
                    suitable_trinkets.append(trinket)
        
        # Ensure we don't exceed the requested count
        return suitable_trinkets[:count]
    
    def generate_random_trinket(self, origin: TrinketOrigin = None, 
                             has_property: bool = True) -> Dict[str, Any]:
        """
        Generate a random trinket, optionally from a specific origin.
        
        Args:
            origin: Optional origin to restrict generation
            has_property: Whether the trinket should have special properties
            
        Returns:
            Dict[str, Any]: Generated trinket data
        """
        # If origin is specified, use it, otherwise pick random
        if origin is None:
            origin = random.choice(list(TrinketOrigin))
        
        # Use LLM to generate a trinket based on the origin
        prompt = self.llm_advisor._create_prompt(
            "generate random trinket",
            f"Trinket Origin: {origin.value}\n"
            f"Should Have Special Property: {has_property}\n\n"
            "Generate a unique and interesting trinket that a D&D 5e character might possess. "
            "The trinket should be small, non-magical (though possibly magical in appearance), "
            "and primarily serve as a flavor item rather than providing mechanical benefits. "
            "Include a name, physical description, history, and how a character might have acquired it. "
            "If it should have special properties, include 1-2 minor unusual qualities."
            "Return as JSON with 'name', 'description', 'history', 'possible_acquisition', and 'properties' keys."
        )
        
        try:
            response = self.llm_advisor.llm_service.generate(prompt)
            trinket_data = self.llm_advisor._extract_json(response)
            
            if trinket_data:
                # Generate an ID
                trinket_id = f"trinket_{trinket_data.get('name', '').lower().replace(' ', '_')}"
                
                # Create a proper trinket object
                trinket = {
                    "id": trinket_id,
                    "name": trinket_data.get("name", "Mysterious Trinket"),
                    "category": EquipmentCategory.TRINKET,
                    "origin": origin,
                    "description": trinket_data.get("description", ""),
                    "history": trinket_data.get("history", ""),
                    "acquisition": trinket_data.get("possible_acquisition", ""),
                    "weight": 0.1,  # Trinkets are typically very light
                    "cost": {"cp": 1},  # Trinkets generally have little monetary value
                    "properties": trinket_data.get("properties", [])
                }
                
                # Add to trinkets collection
                self.trinkets[trinket_id] = trinket
                
                return trinket
        except Exception as e:
            print(f"Error generating random trinket: {e}")
        
        # Fallback response if LLM fails
        fallback_trinket = {
            "id": f"trinket_{origin.value}_{random.randint(1, 1000)}",
            "name": f"Mysterious {origin.value.title()} Trinket",
            "category": EquipmentCategory.TRINKET,
            "origin": origin,
            "description": "A curious small item with unclear purpose.",
            "weight": 0.1,
            "cost": {"cp": 1}
        }
        
        if has_property:
            # If origin has associated properties, use one of those
            if origin in self.origin_property_tendencies:
                fallback_property = random.choice(self.origin_property_tendencies[origin])
                fallback_trinket["properties"] = [fallback_property.value]
            else:
                # Otherwise pick a random property
                fallback_property = random.choice(list(TrinketProperty))
                fallback_trinket["properties"] = [fallback_property.value]
        
        # Add to trinkets collection
        self.trinkets[fallback_trinket["id"]] = fallback_trinket
        
        return fallback_trinket
    
    def create_custom_trinket(self, 
                           name: str,
                           description: str,
                           origin: TrinketOrigin = TrinketOrigin.BIZARRE,
                           properties: List[str] = None,
                           history: str = None) -> Dict[str, Any]:
        """
        Create a custom trinket with specified attributes.
        
        Args:
            name: Name of the trinket
            description: Description of the trinket
            origin: Origin/theme of the trinket
            properties: List of special properties
            history: History or background of the trinket
            
        Returns:
            Dict[str, Any]: Created trinket data
        """
        # Generate a unique ID for the trinket
        trinket_id = f"trinket_{name.lower().replace(' ', '_')}"
        
        # Create the trinket data
        trinket_data = {
            "id": trinket_id,
            "name": name,
            "category": EquipmentCategory.TRINKET,
            "origin": origin,
            "description": description,
            "weight": 0.1,  # Trinkets are typically very light
            "cost": {"cp": 1},  # Trinkets generally have little monetary value
        }
        
        # Add properties if provided
        if properties:
            trinket_data["properties"] = properties
            
        # Add history if provided
        if history:
            trinket_data["history"] = history
        
        # Add to trinkets collection
        self.trinkets[trinket_id] = trinket_data
        
        return trinket_data
    
    def enhance_trinket_with_llm(self, 
                               trinket_id: str, 
                               enhancement_type: str = "description",
                               character_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Enhance trinket with LLM-generated content.
        
        Args:
            trinket_id: ID of the trinket to enhance
            enhancement_type: Type of enhancement (description, history, significance)
            character_context: Optional character data for personalization
            
        Returns:
            Dict[str, Any]: Enhanced trinket data
        """
        trinket_data = self._find_item_by_id(trinket_id)
        if not trinket_data:
            return {"error": "Trinket not found"}
            
        # Create a copy to avoid modifying the original
        enhanced_trinket = trinket_data.copy()
        
        if enhancement_type.lower() == "description":
            # Generate enhanced physical description
            prompt = self.llm_advisor._create_prompt(
                "enhance trinket description",
                f"Trinket: {trinket_data.get('name')}\n"
                f"Current Description: {trinket_data.get('description', '')}\n"
                f"Origin: {trinket_data.get('origin').value if isinstance(trinket_data.get('origin'), TrinketOrigin) else 'unknown'}\n\n"
                "Create a rich, detailed physical description of this trinket that brings it to life. "
                "Describe its appearance, materials, size, weight, texture, any unusual features, and "
                "the general impression it gives. The description should help a player visualize "
                "the trinket as a unique, intriguing object."
            )
            
            try:
                response = self.llm_advisor.llm_service.generate(prompt)
                
                # Clean up the response
                clean_response = re.sub(r'```.*?```', '', response, flags=re.DOTALL)
                clean_response = re.sub(r'\{.*?\}', '', clean_response, flags=re.DOTALL)
                
                enhanced_trinket["detailed_description"] = clean_response.strip()
            except Exception as e:
                print(f"Error enhancing trinket description: {e}")
                enhanced_trinket["detailed_description"] = trinket_data.get("description", "A curious trinket.")
                
        elif enhancement_type.lower() == "history":
            # Generate trinket history/origin story
            prompt = self.llm_advisor._create_prompt(
                "create trinket history",
                f"Trinket: {trinket_data.get('name')}\n"
                f"Description: {trinket_data.get('description', '')}\n"
                f"Origin: {trinket_data.get('origin').value if isinstance(trinket_data.get('origin'), TrinketOrigin) else 'unknown'}\n\n"
                "Create an intriguing history for this trinket, including where it came from, "
                "who might have owned it before, how it was made, any legends associated with it, "
                "and how it might have ended up in the hands of an adventurer. The history should "
                "add depth and narrative hooks for this otherwise simple object."
            )
            
            try:
                response = self.llm_advisor.llm_service.generate(prompt)
                enhanced_trinket["history"] = response
            except Exception as e:
                print(f"Error generating trinket history: {e}")
                enhanced_trinket["history"] = f"This {trinket_data.get('name')} has a story yet to be discovered."
            
        elif enhancement_type.lower() == "significance":
            # Generate personal significance for a character
            char_context = ""
            if character_context:
                char_context = (f"Character: {character_context.get('name', 'Unknown')}, "
                              f"a {character_context.get('race', 'unknown')} "
                              f"{character_context.get('class', 'adventurer')}\n"
                              f"Background: {character_context.get('background', 'Unknown')}\n"
                              f"Personality: {character_context.get('personality', 'Not specified')}\n\n")
                
            prompt = self.llm_advisor._create_prompt(
                "create trinket personal significance",
                f"Trinket: {trinket_data.get('name')}\n"
                f"Description: {trinket_data.get('description', '')}\n"
                f"{char_context}"
                "Create a meaningful personal connection between this trinket and the character. "
                "Explain why this trinket is special to them, how they might have acquired it, "
                "what memories or emotions it evokes, and how it might influence their behavior or decisions. "
                "The significance should feel personal and provide roleplaying opportunities."
            )
            
            try:
                response = self.llm_advisor.llm_service.generate(prompt)
                enhanced_trinket["personal_significance"] = response
            except Exception as e:
                print(f"Error generating personal significance: {e}")
                enhanced_trinket["personal_significance"] = "This item holds some personal meaning to you."
        
        return enhanced_trinket
    
    def generate_trinket_table(self, count: int = 100, 
                             theme: str = None) -> List[Dict[str, Any]]:
        """
        Generate a table of random trinkets, optionally with a theme.
        
        Args:
            count: Number of trinkets to generate
            theme: Optional theme or environment for the trinkets
            
        Returns:
            List[Dict[str, Any]]: Generated trinket table
        """
        # Use LLM to generate a trinket table
        prompt = self.llm_advisor._create_prompt(
            "generate trinket table",
            f"Number of Trinkets: {count}\n"
            f"Theme: {theme if theme else 'Various'}\n\n"
            f"Generate a table of {count} unique trinkets for D&D 5e characters. "
            "Each trinket should be small, mainly serve a narrative purpose, and be intriguing "
            "or mysterious in some way. For each trinket, provide a brief but evocative description. "
            f"{f'All trinkets should fit the theme: {theme}.' if theme else ''}"
            "Return as JSON with an array of objects, each containing 'index' and 'description' keys."
        )
        
        try:
            response = self.llm_advisor.llm_service.generate(prompt)
            table_data = self.llm_advisor._extract_json(response)
            
            if table_data and isinstance(table_data, list):
                return table_data
            elif table_data and "trinkets" in table_data and isinstance(table_data["trinkets"], list):
                return table_data["trinkets"]
        except Exception as e:
            print(f"Error generating trinket table: {e}")
        
        # Fallback with simple trinkets
        fallback_table = []
        for i in range(1, count + 1):
            fallback_table.append({
                "index": i,
                "description": f"A small, curious {theme if theme else 'mysterious'} trinket ({i}/{count})"
            })
        
        return fallback_table
    
    def roll_random_trinket(self, trinket_table: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Roll for a random trinket from a trinket table.
        
        Args:
            trinket_table: Optional specific trinket table to use
            
        Returns:
            Dict[str, Any]: Random trinket result
        """
        # If no table provided, generate a default one with 20 entries
        if not trinket_table:
            trinket_table = self.generate_trinket_table(count=20)
        
        # Roll a random trinket
        random_entry = random.choice(trinket_table)
        
        # Create a trinket entry from the table result
        trinket_id = f"random_trinket_{random_entry.get('index', random.randint(1, 1000))}"
        
        trinket = {
            "id": trinket_id,
            "name": f"Random Trinket {random_entry.get('index', '')}",
            "category": EquipmentCategory.TRINKET,
            "description": random_entry.get("description", "A mysterious trinket"),
            "weight": 0.1,
            "cost": {"cp": 1}
        }
        
        # Add to trinkets collection
        self.trinkets[trinket_id] = trinket
        
        return trinket