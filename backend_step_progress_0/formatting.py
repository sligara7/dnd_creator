"""
Character Formatting System - Refactored and Cleaned

This module provides comprehensive formatting and display utilities for D&D characters.
It integrates with the cleaned backend modules to generate formatted output for
character sheets, summaries, and detailed breakdowns.

Dependencies: All cleaned backend modules
"""

from typing import Dict, Any, List, Optional, Union
import logging

# Import from cleaned modules
from character_models import CharacterCore, CharacterState, CharacterSheet
from core_models import AbilityScore, ProficiencyLevel, AbilityScoreSource
from custom_content_models import ContentRegistry
from ability_management import AdvancedAbilityManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# CHARACTER FORMATTER CLASS
# ============================================================================

class CharacterFormatter:
    """Comprehensive character formatting and display utilities."""
    
    def __init__(self, content_registry: ContentRegistry = None):
        self.content_registry = content_registry or ContentRegistry()
    
    # ========================================================================
    # MAIN FORMATTING METHODS
    # ========================================================================
    
    def format_character_sheet(self, character_core: CharacterCore, 
                              character_state: CharacterState = None,
                              include_detailed_breakdown: bool = True) -> str:
        """Format a complete character sheet."""
        
        output = []
        
        # Header
        output.append(self._format_character_header(character_core))
        output.append("")
        
        # Basic info
        output.append(self._format_basic_info(character_core))
        output.append("")
        
        # Ability scores
        if include_detailed_breakdown:
            output.append(self.format_ability_scores_detailed(character_core))
        else:
            output.append(self.format_ability_scores_simple(character_core))
        output.append("")
        
        # Class progression
        if len(character_core.character_classes) > 1:
            output.append(self.format_multiclass_progression(character_core))
            output.append("")
        
        # Skills and proficiencies
        output.append(self._format_skills_and_proficiencies(character_core))
        output.append("")
        
        # Equipment
        output.append(self._format_equipment_summary(character_core))
        output.append("")
        
        # Features and traits
        output.append(self._format_features_summary(character_core))
        
        return "\n".join(output)
    
    def format_character_summary(self, character_core: CharacterCore) -> str:
        """Format a concise character summary."""
        
        output = []
        
        # Name and basic info
        total_level = sum(character_core.character_classes.values())
        class_summary = self._format_class_summary(character_core.character_classes)
        
        output.append(f"🎲 {character_core.name}")
        output.append(f"   {character_core.race} {class_summary}")
        output.append(f"   Level {total_level} • Background: {character_core.background}")
        output.append("")
        
        # Quick ability scores
        abilities = []
        for ability_name in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
            ability_score = getattr(character_core, ability_name)
            modifier = ability_score.modifier
            mod_str = f"+{modifier}" if modifier >= 0 else str(modifier)
            abilities.append(f"{ability_name[:3].upper()}: {ability_score.total_score} ({mod_str})")
        
        output.append("Ability Scores:")
        output.append("   " + " | ".join(abilities[:3]))
        output.append("   " + " | ".join(abilities[3:]))
        
        return "\n".join(output)
    
    # ========================================================================
    # ABILITY SCORE FORMATTING
    # ========================================================================
    
    def format_ability_scores_detailed(self, character_core: CharacterCore) -> str:
        """Format detailed ability scores showing all sources of bonuses."""
        
        output = []
        output.append("ABILITY SCORES (DETAILED)")
        output.append("=" * 26)
        
        for ability_name in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
            ability_score: AbilityScore = getattr(character_core, ability_name)
            
            modifier = ability_score.modifier
            mod_str = f"+{modifier}" if modifier >= 0 else str(modifier)
            
            output.append(f"{ability_name.capitalize():12} {ability_score.total_score:2} ({mod_str})")
            
            # Show breakdown of sources
            breakdown = [f"Base: {ability_score.base_score}"]
            
            for source in AbilityScoreSource:
                improvements = ability_score.improvements.get(source, [])
                if improvements:
                    total_from_source = sum(imp["amount"] for imp in improvements)
                    if total_from_source > 0:
                        source_name = source.value.replace("_", " ").title()
                        breakdown.append(f"{source_name}: +{total_from_source}")
            
            if len(breakdown) > 1:
                output.append(f"             ({', '.join(breakdown)})")
            
            # Show recent improvements
            all_improvements = []
            for source, improvements in ability_score.improvements.items():
                for imp in improvements:
                    imp_copy = imp.copy()
                    imp_copy["source"] = source.value
                    all_improvements.append(imp_copy)
            
            # Sort by level gained and show last few
            all_improvements.sort(key=lambda x: x.get("level_gained", 0))
            recent_improvements = all_improvements[-2:]  # Last 2 improvements
            
            if recent_improvements:
                output.append("             Recent:")
                for imp in recent_improvements:
                    level = imp.get("level_gained", 0)
                    amount = imp.get("amount", 0)
                    desc = imp.get("description", "")
                    if level > 0:
                        output.append(f"               Level {level}: +{amount} ({desc})")
                    else:
                        output.append(f"               +{amount} ({desc})")
        
        return "\n".join(output)
    
    def format_ability_scores_simple(self, character_core: CharacterCore) -> str:
        """Format simple ability scores display."""
        
        output = []
        output.append("ABILITY SCORES")
        output.append("=" * 14)
        
        for ability_name in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
            ability_score: AbilityScore = getattr(character_core, ability_name)
            modifier = ability_score.modifier
            mod_str = f"+{modifier}" if modifier >= 0 else str(modifier)
            
            output.append(f"{ability_name.capitalize():12} {ability_score.total_score:2} ({mod_str})")
        
        return "\n".join(output)
    
    # ========================================================================
    # CLASS AND LEVEL FORMATTING
    # ========================================================================
    
    def format_multiclass_progression(self, character_core: CharacterCore) -> str:
        """Format multiclass progression details."""
        
        classes = character_core.character_classes
        if len(classes) <= 1:
            return ""
        
        output = []
        output.append("MULTICLASS PROGRESSION")
        output.append("=" * 21)
        
        total_level = sum(classes.values())
        output.append(f"Total Character Level: {total_level}")
        output.append("")
        
        output.append("CLASS LEVELS")
        output.append("-" * 12)
        for class_name, class_level in classes.items():
            percentage = (class_level / total_level) * 100
            output.append(f"{class_name:12} {class_level:2} ({percentage:4.1f}%)")
        
        return "\n".join(output)
    
    def format_asi_progression(self, character_core: CharacterCore, 
                             asi_manager = None) -> str:
        """Format ASI progression and opportunities."""
        
        if not asi_manager:
            from core_models import ASIManager
            asi_manager = ASIManager()
        
        output = []
        output.append("ABILITY SCORE IMPROVEMENTS")
        output.append("=" * 26)
        
        asi_info = asi_manager.calculate_available_asis(character_core.character_classes)
        
        output.append(f"Total Available: {asi_info.get('total_available', 0)}")
        output.append(f"Used: {asi_info.get('total_used', 0)}")
        output.append(f"Remaining: {asi_info.get('remaining', 0)}")
        output.append("")
        
        # Show ASI progression
        asis = asi_info.get("asis", [])
        if asis:
            output.append("ASI PROGRESSION")
            output.append("-" * 15)
            
            for asi in asis:
                class_name = asi["class"]
                class_level = asi["class_level"]
                char_level = asi["character_level"]
                used = asi["used"]
                
                status = "✓" if used else "○"
                output.append(f"{status} Level {char_level} ({class_name} {class_level})")
                
                if used and "improvement" in asi:
                    imp = asi["improvement"]
                    improvements = imp.get("improvements", {})
                    imp_str = ", ".join([f"{ability} +{bonus}" for ability, bonus in improvements.items()])
                    output.append(f"    Applied: {imp_str}")
        
        return "\n".join(output)
    
    # ========================================================================
    # EQUIPMENT FORMATTING
    # ========================================================================
    
    def format_equipment_details(self, character_core: CharacterCore) -> str:
        """Format detailed equipment information."""
        
        output = []
        output.append("EQUIPMENT")
        output.append("=" * 9)
        
        # Armor
        if hasattr(character_core, 'armor') and character_core.armor:
            output.append("ARMOR")
            output.append("-" * 5)
            output.append(self._format_armor_details(character_core.armor))
            output.append("")
        
        # Weapons
        if hasattr(character_core, 'weapons') and character_core.weapons:
            output.append("WEAPONS")
            output.append("-" * 7)
            for weapon in character_core.weapons:
                output.append(self._format_weapon_details(weapon))
            output.append("")
        
        # Other equipment
        if hasattr(character_core, 'equipment') and character_core.equipment:
            output.append("OTHER EQUIPMENT")
            output.append("-" * 15)
            for item in character_core.equipment:
                if isinstance(item, dict):
                    name = item.get("name", "Unknown Item")
                    quantity = item.get("quantity", 1)
                    output.append(f"• {name}" + (f" (x{quantity})" if quantity > 1 else ""))
                else:
                    output.append(f"• {item}")
        
        return "\n".join(output)
    
    def _format_armor_details(self, armor_data: Union[str, Dict[str, Any]]) -> str:
        """Format armor details."""
        
        if isinstance(armor_data, str):
            return f"• {armor_data}"
        
        name = armor_data.get("name", "Unknown Armor")
        ac = armor_data.get("ac", "?")
        armor_type = armor_data.get("type", "")
        
        details = [f"AC {ac}"]
        if armor_type:
            details.append(armor_type)
        
        stealth_disadvantage = armor_data.get("stealth_disadvantage", False)
        if stealth_disadvantage:
            details.append("Stealth Disadvantage")
        
        return f"• {name} ({', '.join(details)})"
    
    def _format_weapon_details(self, weapon_data: Union[str, Dict[str, Any]]) -> str:
        """Format weapon details."""
        
        if isinstance(weapon_data, str):
            return f"• {weapon_data}"
        
        name = weapon_data.get("name", "Unknown Weapon")
        damage = weapon_data.get("damage", "1d4")
        properties = weapon_data.get("properties", [])
        
        details = [damage]
        if properties:
            details.extend(properties)
        
        return f"• {name} ({', '.join(details)})"
    
    # ========================================================================
    # FEATURES AND TRAITS FORMATTING
    # ========================================================================
    
    def format_species_features(self, character_core: CharacterCore) -> str:
        """Format species/race features."""
        
        output = []
        output.append(f"{character_core.race.upper()} FEATURES")
        output.append("=" * (len(character_core.race) + 9))
        
        # This would integrate with a race/species feature system
        # For now, show basic racial traits
        output.append("• Racial traits and features would be displayed here")
        output.append("• Speed, size, languages, special abilities")
        output.append("• Resistance, immunity, and other traits")
        
        return "\n".join(output)
    
    def format_class_features(self, character_core: CharacterCore) -> str:
        """Format class features by level."""
        
        output = []
        output.append("CLASS FEATURES")
        output.append("=" * 13)
        
        for class_name, class_level in character_core.character_classes.items():
            output.append(f"{class_name.upper()} LEVEL {class_level}")
            output.append("-" * (len(class_name) + 7 + len(str(class_level))))
            
            # This would integrate with a class feature system
            output.append(f"• Level 1-{class_level} features for {class_name}")
            output.append("• Hit points, proficiencies, class abilities")
            output.append("• Subclass features and progression")
            output.append("")
        
        return "\n".join(output)
    
    # ========================================================================
    # CUSTOM CONTENT FORMATTING
    # ========================================================================
    
    def format_custom_content(self, custom_content: Dict[str, Any]) -> str:
        """Format custom content section."""
        
        if not custom_content:
            return ""
        
        output = []
        output.append("CUSTOM CONTENT")
        output.append("=" * 14)
        
        # Custom species
        if "species" in custom_content:
            species_data = custom_content["species"]
            output.append("CUSTOM SPECIES")
            output.append("-" * 14)
            output.append(f"Name: {species_data.get('name', 'Unknown')}")
            output.append(f"Size: {species_data.get('size', 'Medium')}")
            output.append(f"Speed: {species_data.get('speed', 30)} feet")
            
            traits = species_data.get("traits", [])
            if traits:
                output.append("Traits:")
                for trait in traits:
                    output.append(f"• {trait}")
            output.append("")
        
        # Custom background
        if "background" in custom_content:
            bg_data = custom_content["background"]
            output.append("CUSTOM BACKGROUND")
            output.append("-" * 17)
            output.append(f"Name: {bg_data.get('name', 'Unknown')}")
            output.append(f"Description: {bg_data.get('description', 'N/A')}")
            
            skills = bg_data.get("skill_proficiencies", [])
            if skills:
                output.append(f"Skill Proficiencies: {', '.join(skills)}")
            output.append("")
        
        # Custom class
        if "class" in custom_content:
            class_data = custom_content["class"]
            output.append("CUSTOM CLASS")
            output.append("-" * 12)
            output.append(f"Name: {class_data.get('name', 'Unknown')}")
            output.append(f"Hit Die: d{class_data.get('hit_die', 8)}")
            output.append(f"Description: {class_data.get('description', 'N/A')}")
            output.append("")
        
        return "\n".join(output)
    
    # ========================================================================
    # BACKSTORY FORMATTING
    # ========================================================================
    
    def format_backstory(self, backstory: str, character_core: CharacterCore = None) -> str:
        """Format character backstory with optional character context."""
        
        output = []
        
        if character_core:
            output.append(f"BACKSTORY: {character_core.name}")
            output.append("=" * (len(character_core.name) + 11))
        else:
            output.append("CHARACTER BACKSTORY")
            output.append("=" * 19)
        
        output.append("")
        
        # Format backstory text with proper wrapping
        if backstory:
            paragraphs = backstory.split('\n\n')
            for paragraph in paragraphs:
                # Simple text wrapping at approximately 80 characters
                words = paragraph.split()
                line = ""
                for word in words:
                    if len(line + " " + word) <= 80:
                        line += (" " + word) if line else word
                    else:
                        if line:
                            output.append(line)
                        line = word
                if line:
                    output.append(line)
                output.append("")
        else:
            output.append("No backstory available.")
            output.append("")
        
        return "\n".join(output)
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _format_character_header(self, character_core: CharacterCore) -> str:
        """Format character header with name and basic info."""
        
        total_level = sum(character_core.character_classes.values())
        class_summary = self._format_class_summary(character_core.character_classes)
        
        header = f"{character_core.name} - Level {total_level} {character_core.race} {class_summary}"
        return header + "\n" + "=" * len(header)
    
    def _format_basic_info(self, character_core: CharacterCore) -> str:
        """Format basic character information."""
        
        output = []
        output.append("BASIC INFORMATION")
        output.append("-" * 17)
        output.append(f"Name: {character_core.name}")
        output.append(f"Race: {character_core.race}")
        output.append(f"Background: {character_core.background}")
        
        total_level = sum(character_core.character_classes.values())
        output.append(f"Total Level: {total_level}")
        
        if len(character_core.character_classes) > 1:
            output.append("Classes:")
            for class_name, class_level in character_core.character_classes.items():
                output.append(f"  {class_name}: {class_level}")
        else:
            class_name, class_level = next(iter(character_core.character_classes.items()))
            output.append(f"Class: {class_name} (Level {class_level})")
        
        return "\n".join(output)
    
    def _format_class_summary(self, character_classes: Dict[str, int]) -> str:
        """Format class summary for display."""
        
        if len(character_classes) == 1:
            class_name, level = next(iter(character_classes.items()))
            return f"{class_name}"
        else:
            class_parts = []
            for class_name, level in character_classes.items():
                class_parts.append(f"{class_name} {level}")
            return " / ".join(class_parts)
    
    def _format_skills_and_proficiencies(self, character_core: CharacterCore) -> str:
        """Format skills and proficiencies section."""
        
        output = []
        output.append("SKILLS & PROFICIENCIES")
        output.append("-" * 21)
        
        # This would integrate with a proper skill system
        output.append("• Skill proficiencies would be calculated here")
        output.append("• Saving throw proficiencies")
        output.append("• Tool and language proficiencies")
        
        return "\n".join(output)
    
    def _format_equipment_summary(self, character_core: CharacterCore) -> str:
        """Format equipment summary."""
        
        output = []
        output.append("EQUIPMENT SUMMARY")
        output.append("-" * 17)
        
        # Basic equipment display
        if hasattr(character_core, 'armor') and character_core.armor:
            output.append(f"Armor: {character_core.armor}")
        
        if hasattr(character_core, 'weapons') and character_core.weapons:
            weapon_names = []
            for weapon in character_core.weapons:
                if isinstance(weapon, dict):
                    weapon_names.append(weapon.get("name", "Unknown"))
                else:
                    weapon_names.append(str(weapon))
            output.append(f"Weapons: {', '.join(weapon_names)}")
        
        return "\n".join(output)
    
    def _format_features_summary(self, character_core: CharacterCore) -> str:
        """Format features summary."""
        
        output = []
        output.append("FEATURES SUMMARY")
        output.append("-" * 16)
        
        output.append("• Racial features and traits")
        output.append("• Class features and abilities")
        output.append("• Background features")
        
        return "\n".join(output)

# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def format_character(character_core: CharacterCore, 
                    format_type: str = "sheet",
                    **kwargs) -> str:
    """Convenience function to format a character."""
    
    formatter = CharacterFormatter()
    
    if format_type == "sheet":
        return formatter.format_character_sheet(character_core, **kwargs)
    elif format_type == "summary":
        return formatter.format_character_summary(character_core)
    elif format_type == "abilities":
        return formatter.format_ability_scores_detailed(character_core)
    elif format_type == "equipment":
        return formatter.format_equipment_details(character_core)
    else:
        raise ValueError(f"Unknown format type: {format_type}")

def format_creation_result(creation_result, format_type: str = "summary") -> str:
    """Format a character creation result."""
    
    if not creation_result.success:
        return f"❌ Character creation failed: {creation_result.error}"
    
    formatter = CharacterFormatter()
    
    # Extract character data
    character_data = creation_result.data
    if "core" in character_data:
        # This is from CharacterCreator
        core_data = character_data["core"]
        backstory = character_data.get("backstory", "")
        custom_content = character_data.get("custom_content", {})
        
        # Reconstruct CharacterCore (simplified)
        from character_models import CharacterCore
        from core_models import AbilityScore
        
        character_core = CharacterCore(core_data["name"])
        character_core.race = core_data.get("race", "Human")
        character_core.background = core_data.get("background", "Folk Hero")
        character_core.character_classes = core_data.get("character_classes", {"Fighter": 1})
        
        # Set ability scores
        ability_scores = core_data.get("ability_scores", {})
        for ability_name, score in ability_scores.items():
            if hasattr(character_core, ability_name):
                setattr(character_core, ability_name, AbilityScore(score))
        
        output = []
        
        if format_type == "full":
            output.append(formatter.format_character_sheet(character_core))
            output.append("\n")
            if backstory:
                output.append(formatter.format_backstory(backstory, character_core))
                output.append("\n")
            if custom_content:
                output.append(formatter.format_custom_content(custom_content))
        else:
            output.append(formatter.format_character_summary(character_core))
            
        if creation_result.warnings:
            output.append("\n⚠️  Warnings:")
            for warning in creation_result.warnings:
                output.append(f"   • {warning}")
        
        return "\n".join(output)
    
    else:
        return "Unable to format result: unexpected data structure"

# ============================================================================
# MODULE SUMMARY
# ============================================================================
"""
REFACTORED FORMATTING MODULE

This module has been completely refactored from a collection of standalone functions
into a comprehensive class-based formatting system:

MAIN CLASS:
- CharacterFormatter: Comprehensive formatting for all character aspects

KEY METHODS:
- format_character_sheet(): Complete character sheet formatting  
- format_character_summary(): Concise character overview
- format_ability_scores_detailed(): Detailed ability score breakdown
- format_multiclass_progression(): Multiclass level progression
- format_equipment_details(): Equipment and gear formatting
- format_species_features(): Race/species feature display
- format_class_features(): Class feature progression
- format_custom_content(): Custom content display
- format_backstory(): Character backstory formatting

CONVENIENCE FUNCTIONS:
- format_character(): Quick character formatting
- format_creation_result(): Format character creation results

INTEGRATION:
- Works with CharacterCore, CharacterState, CharacterSheet
- Uses AbilityScore, ASIManager for detailed breakdowns
- Integrates with custom content system
- Supports all refactored backend modules

REMOVED:
- Duplicate formatting functions
- Hardcoded character data assumptions
- Legacy formatting patterns
- Unused utility functions

The formatting system now provides a clean, extensible way to display
character information in various formats for different use cases.
"""
