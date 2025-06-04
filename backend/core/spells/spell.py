# spell.py
# Description: Handles spellcasting and spell management.

from typing import Dict, List, Any, Optional, Union, Tuple
import json

from backend.core.services.ollama_service import OllamaService
from backend.core.spells.llm_spells_advisor import LLMSpellsAdvisor
from backend.core.spells.abstract_spells import AbstractSpells

class Spell(AbstractSpells):
    """
    Implementation of AbstractSpells for D&D 2024 edition.
    Handles spell management, lookup, and spellcasting mechanics.
    """
    
    def __init__(self):
        """Initialize the spells data for D&D 2024 edition."""
        self.llm_advisor = LLMSpellsAdvisor()
        
        # Load spell data - in a real implementation, this would be loaded from a database or JSON file
        # Here, we're defining a small subset of spells for demonstration
        self._spells_data = {
            "fireball": {
                "name": "Fireball",
                "level": 3,
                "school": "evocation",
                "casting_time": "1 action",
                "range": "150 feet",
                "components": "V, S, M (a tiny ball of bat guano and sulfur)",
                "duration": "Instantaneous",
                "description": "A bright streak flashes from your pointing finger to a point you choose within range and then blossoms with a low roar into an explosion of flame. Each creature in a 20-foot-radius sphere centered on that point must make a Dexterity saving throw. A target takes 8d6 fire damage on a failed save, or half as much damage on a successful one.",
                "higher_levels": "When you cast this spell using a spell slot of 4th level or higher, the damage increases by 1d6 for each slot level above 3rd.",
                "classes": ["sorcerer", "wizard", "artificer"],
                "damage": {
                    "type": "fire",
                    "dice": "8d6"
                }
            },
            "cure wounds": {
                "name": "Cure Wounds",
                "level": 1,
                "school": "evocation",
                "casting_time": "1 action",
                "range": "Touch",
                "components": "V, S",
                "duration": "Instantaneous",
                "description": "A creature you touch regains a number of hit points equal to 1d8 + your spellcasting ability modifier. This spell has no effect on undead or constructs.",
                "higher_levels": "When you cast this spell using a spell slot of 2nd level or higher, the healing increases by 1d8 for each slot level above 1st.",
                "classes": ["bard", "cleric", "druid", "paladin", "ranger", "artificer"],
                "healing": {
                    "dice": "1d8",
                    "bonus": "spellcasting_mod"
                }
            },
            "magic missile": {
                "name": "Magic Missile",
                "level": 1,
                "school": "evocation",
                "casting_time": "1 action",
                "range": "120 feet",
                "components": "V, S",
                "duration": "Instantaneous",
                "description": "You create three glowing darts of magical force. Each dart hits a creature of your choice that you can see within range. A dart deals 1d4 + 1 force damage to its target.",
                "higher_levels": "When you cast this spell using a spell slot of 2nd level or higher, the spell creates one more dart for each slot level above 1st.",
                "classes": ["sorcerer", "wizard"],
                "damage": {
                    "type": "force",
                    "dice": "1d4+1",
                    "darts": 3
                }
            }
        }
        
        # Mapping of class names to their spellcasting abilities
        self._class_spellcasting_abilities = {
            "artificer": "intelligence",
            "bard": "charisma",
            "cleric": "wisdom",
            "druid": "wisdom",
            "paladin": "charisma",
            "ranger": "wisdom",
            "sorcerer": "charisma",
            "warlock": "charisma",
            "wizard": "intelligence"
        }
        
        # Map of class to prepared spell formula types
        self._preparation_formulas = {
            "artificer": "level_plus_mod",  # Level + modifier
            "cleric": "level_plus_mod",
            "druid": "level_plus_mod",
            "paladin": "half_level_plus_mod",  # Half level (rounded down) + mod
            "wizard": "level_plus_mod",
            "ranger": "level_plus_mod",
            "bard": "known_spells",  # Uses known spells, not prepared
            "sorcerer": "known_spells",
            "warlock": "known_spells"
        }
        
        # Known spells by class and level (for classes that use known spells rather than preparation)
        self._known_spells_table = {
            "bard": {1: 4, 2: 5, 3: 6, 4: 7, 5: 8, 6: 9, 7: 10, 8: 11, 9: 12, 10: 14, 11: 15,
                    12: 15, 13: 16, 14: 18, 15: 19, 16: 19, 17: 20, 18: 22, 19: 22, 20: 22},
            "sorcerer": {1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7, 7: 8, 8: 9, 9: 10, 10: 11, 11: 12,
                        12: 12, 13: 13, 14: 13, 15: 14, 16: 14, 17: 15, 18: 15, 19: 16, 20: 16},
            "warlock": {1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7, 7: 8, 8: 9, 9: 10, 10: 10, 11: 11,
                       12: 11, 13: 12, 14: 12, 15: 13, 16: 13, 17: 14, 18: 14, 19: 15, 20: 15}
        }
    
    def get_all_spells(self) -> List[Dict[str, Any]]:
        """
        Return a list of all available spells.
        
        Returns:
            List[Dict[str, Any]]: List of all spells with basic information
        """
        return [
            {
                "name": spell_data["name"],
                "level": spell_data["level"],
                "school": spell_data["school"],
                "casting_time": spell_data["casting_time"],
                "classes": spell_data["classes"]
            }
            for spell_data in self._spells_data.values()
        ]
    
    def get_spell_details(self, spell_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a spell.
        
        Args:
            spell_name (str): Name of the spell
            
        Returns:
            Dict[str, Any] or None: Detailed spell information or None if not found
        """
        spell_key = spell_name.lower()
        
        if spell_key in self._spells_data:
            return self._spells_data[spell_key]
        
        # If the spell is not in our database, try to get it from the LLM
        try:
            llm_spell = self.llm_advisor.get_spell_details(spell_name)
            if llm_spell:
                return llm_spell
        except Exception as e:
            print(f"Error retrieving spell details from LLM: {e}")
        
        return None
    
    def get_class_spell_list(self, class_name: str, level: int = None) -> List[Dict[str, Any]]:
        """
        Get spells available to a class at a specific level.
        
        Args:
            class_name (str): Name of the class
            level (int, optional): Character level or spell level
                                   If None, returns all spells for the class
                                   
        Returns:
            List[Dict[str, Any]]: List of spells available to the class
        """
        class_name_lower = class_name.lower()
        spells = []
        
        for spell_key, spell_data in self._spells_data.items():
            if class_name_lower in [c.lower() for c in spell_data["classes"]]:
                # If level is specified and it's a character level, check if the spell is available at that level
                if level is not None and spell_data["level"] <= self._get_max_spell_level(class_name_lower, level):
                    spells.append({
                        "name": spell_data["name"],
                        "level": spell_data["level"],
                        "school": spell_data["school"]
                    })
                # If level is specified and it's a spell level, check if the spell is of that level
                elif level is not None and spell_data["level"] == level:
                    spells.append({
                        "name": spell_data["name"],
                        "level": spell_data["level"],
                        "school": spell_data["school"]
                    })
                # If no level is specified, include all spells for the class
                elif level is None:
                    spells.append({
                        "name": spell_data["name"],
                        "level": spell_data["level"],
                        "school": spell_data["school"]
                    })
        
        # If we don't have any spells or have very few, supplement with LLM
        if len(spells) < 5:
            try:
                llm_spells = self.llm_advisor.get_class_spell_list(class_name, level)
                # Merge and deduplicate spells
                existing_names = set(spell["name"].lower() for spell in spells)
                for spell in llm_spells:
                    if spell["name"].lower() not in existing_names:
                        spells.append(spell)
                        existing_names.add(spell["name"].lower())
            except Exception as e:
                print(f"Error retrieving class spell list from LLM: {e}")
        
        return sorted(spells, key=lambda x: x["level"])
    
    def calculate_spell_save_dc(self, ability_score: int, proficiency_bonus: int) -> int:
        """
        Calculate spell save DC based on ability score and proficiency bonus.
        
        Args:
            ability_score (int): Spellcasting ability score
            proficiency_bonus (int): Character's proficiency bonus
            
        Returns:
            int: Spell save DC
        """
        # Spell save DC = 8 + proficiency bonus + ability modifier
        ability_modifier = (ability_score - 10) // 2
        return 8 + proficiency_bonus + ability_modifier
    
    def calculate_spell_attack_bonus(self, ability_score: int, proficiency_bonus: int) -> int:
        """
        Calculate spell attack bonus based on ability score and proficiency bonus.
        
        Args:
            ability_score (int): Spellcasting ability score
            proficiency_bonus (int): Character's proficiency bonus
            
        Returns:
            int: Spell attack bonus
        """
        # Spell attack bonus = proficiency bonus + ability modifier
        ability_modifier = (ability_score - 10) // 2
        return proficiency_bonus + ability_modifier
    
    def get_prepared_spells_limit(self, class_name: str, level: int, ability_score: int) -> int:
        """
        Calculate how many spells a character can prepare.
        
        Args:
            class_name (str): Character's class
            level (int): Character level
            ability_score (int): Spellcasting ability score
            
        Returns:
            int: Number of spells that can be prepared
        """
        class_name_lower = class_name.lower()
        ability_modifier = (ability_score - 10) // 2
        
        # Get formula type for the class
        formula_type = self._preparation_formulas.get(class_name_lower, "level_plus_mod")
        
        if formula_type == "known_spells":
            # Classes like bard, sorcerer, warlock use fixed known spells
            if class_name_lower in self._known_spells_table:
                return self._known_spells_table[class_name_lower].get(level, 0)
            return 0
            
        elif formula_type == "level_plus_mod":
            # Classes like cleric, druid, wizard: level + ability modifier
            return max(1, level + ability_modifier)
            
        elif formula_type == "half_level_plus_mod":
            # Classes like paladin: half level (rounded down) + ability modifier
            return max(1, level // 2 + ability_modifier)
            
        # Default case
        return max(1, level + ability_modifier)
    
    def search_spells(self, query: str, **filters) -> List[Dict[str, Any]]:
        """
        Search for spells matching query and filters.
        
        Args:
            query (str): Search query
            **filters: Additional filters like level, school, class, etc.
            
        Returns:
            List[Dict[str, Any]]: List of matching spells
        """
        results = []
        query_lower = query.lower()
        
        for spell_key, spell_data in self._spells_data.items():
            # Check if query matches spell name or description
            name_match = query_lower in spell_data["name"].lower()
            desc_match = query_lower in spell_data.get("description", "").lower()
            
            if name_match or desc_match:
                # Apply additional filters if specified
                include = True
                
                for filter_key, filter_value in filters.items():
                    if filter_key == "level" and spell_data["level"] != filter_value:
                        include = False
                        break
                    elif filter_key == "school" and spell_data["school"] != filter_value.lower():
                        include = False
                        break
                    elif filter_key == "class" and filter_value.lower() not in [c.lower() for c in spell_data["classes"]]:
                        include = False
                        break
                
                if include:
                    results.append({
                        "name": spell_data["name"],
                        "level": spell_data["level"],
                        "school": spell_data["school"],
                        "classes": spell_data["classes"]
                    })
        
        # If we have few results, supplement with LLM
        if len(results) < 3:
            try:
                llm_results = self.llm_advisor.search_spells(query, **filters)
                # Merge and deduplicate
                existing_names = set(spell["name"].lower() for spell in results)
                for spell in llm_results:
                    if spell["name"].lower() not in existing_names:
                        results.append(spell)
                        existing_names.add(spell["name"].lower())
            except Exception as e:
                print(f"Error searching spells with LLM: {e}")
        
        return results
    
    def get_spellcasting_ability(self, class_name: str) -> str:
        """
        Get the spellcasting ability for a class.
        
        Args:
            class_name (str): The character class
            
        Returns:
            str: Spellcasting ability (intelligence, wisdom, charisma)
        """
        class_name_lower = class_name.lower()
        return self._class_spellcasting_abilities.get(class_name_lower, "charisma")
    
    def _get_max_spell_level(self, class_name: str, character_level: int) -> int:
        """
        Get the maximum spell level available to a class at a given character level.
        
        Args:
            class_name (str): Name of the class
            character_level (int): Character level
            
        Returns:
            int: Maximum spell level
        """
        # Simplified spell slot progression for full casters
        full_caster_progression = {
            1: 1, 2: 1, 3: 2, 4: 2, 5: 3, 6: 3, 7: 4, 8: 4, 9: 5,
            10: 5, 11: 6, 12: 6, 13: 7, 14: 7, 15: 8, 16: 8, 17: 9,
            18: 9, 19: 9, 20: 9
        }
        
        # Half-casters (paladin, ranger, artificer)
        half_caster_progression = {
            1: 0, 2: 1, 3: 1, 4: 1, 5: 2, 6: 2, 7: 2, 8: 2, 9: 3,
            10: 3, 11: 3, 12: 3, 13: 4, 14: 4, 15: 4, 16: 4, 17: 5,
            18: 5, 19: 5, 20: 5
        }
        
        # Third-casters (e.g., Eldritch Knight Fighter, Arcane Trickster Rogue)
        third_caster_progression = {
            1: 0, 2: 0, 3: 1, 4: 1, 5: 1, 6: 1, 7: 2, 8: 2, 9: 2,
            10: 2, 11: 2, 12: 2, 13: 3, 14: 3, 15: 3, 16: 3, 17: 3,
            18: 3, 19: 4, 20: 4
        }
        
        class_name_lower = class_name.lower()
        
        # Full casters
        if class_name_lower in ["bard", "cleric", "druid", "sorcerer", "wizard", "warlock"]:
            return full_caster_progression.get(character_level, 0)
        
        # Half casters
        elif class_name_lower in ["paladin", "ranger", "artificer"]:
            return half_caster_progression.get(character_level, 0)
        
        # Third casters
        elif class_name_lower in ["eldritch knight", "arcane trickster"]:
            return third_caster_progression.get(character_level, 0)
        
        # Default for unknown classes
        return 0