"""
Character Export Templates and VTT Format Specifications.

This module contains all templates and format specifications for exporting D&D
characters to various Virtual Tabletop (VTT) platforms and standard formats.
These templates ensure consistent, accurate character data representation across
different gaming platforms.

Following Clean Architecture principles, these templates are:
- Infrastructure-independent (define data structure, not implementation)
- Focused on D&D character representation standards
- Modular and extensible for new VTT platforms
- Aligned with the export functionality described in the README
"""

from typing import Dict, List, Any, Optional, Union
from ..enums.export_formats import ExportFormat, VTTPlatform, CharacterSheetType, OutputLayout
from ..enums.content_types import ContentType
from ..enums.game_mechanics import AbilityScore, Skill, SavingThrow


# ============ UNIVERSAL CHARACTER SHEET STRUCTURE ============

# Base character sheet structure that all exports derive from
UNIVERSAL_CHARACTER_TEMPLATE: Dict[str, Any] = {
    "character_info": {
        "name": "",
        "level": 1,
        "species": "",
        "character_class": "",
        "subclass": "",
        "background": "",
        "alignment": "",
        "experience_points": 0
    },
    "ability_scores": {
        "strength": {"score": 10, "modifier": 0, "saving_throw": 0},
        "dexterity": {"score": 10, "modifier": 0, "saving_throw": 0},
        "constitution": {"score": 10, "modifier": 0, "saving_throw": 0},
        "intelligence": {"score": 10, "modifier": 0, "saving_throw": 0},
        "wisdom": {"score": 10, "modifier": 0, "saving_throw": 0},
        "charisma": {"score": 10, "modifier": 0, "saving_throw": 0}
    },
    "combat_stats": {
        "armor_class": 10,
        "hit_points": {"current": 0, "maximum": 0, "temporary": 0},
        "hit_dice": {"total": "", "current": ""},
        "speed": {"walking": 30, "flying": 0, "swimming": 0, "climbing": 0},
        "proficiency_bonus": 2,
        "passive_perception": 10
    },
    "skills": {
        "acrobatics": {"modifier": 0, "proficient": False, "expertise": False},
        "animal_handling": {"modifier": 0, "proficient": False, "expertise": False},
        "arcana": {"modifier": 0, "proficient": False, "expertise": False},
        "athletics": {"modifier": 0, "proficient": False, "expertise": False},
        "deception": {"modifier": 0, "proficient": False, "expertise": False},
        "history": {"modifier": 0, "proficient": False, "expertise": False},
        "insight": {"modifier": 0, "proficient": False, "expertise": False},
        "intimidation": {"modifier": 0, "proficient": False, "expertise": False},
        "investigation": {"modifier": 0, "proficient": False, "expertise": False},
        "medicine": {"modifier": 0, "proficient": False, "expertise": False},
        "nature": {"modifier": 0, "proficient": False, "expertise": False},
        "perception": {"modifier": 0, "proficient": False, "expertise": False},
        "performance": {"modifier": 0, "proficient": False, "expertise": False},
        "persuasion": {"modifier": 0, "proficient": False, "expertise": False},
        "religion": {"modifier": 0, "proficient": False, "expertise": False},
        "sleight_of_hand": {"modifier": 0, "proficient": False, "expertise": False},
        "stealth": {"modifier": 0, "proficient": False, "expertise": False},
        "survival": {"modifier": 0, "proficient": False, "expertise": False}
    },
    "proficiencies": {
        "armor": [],
        "weapons": [],
        "tools": [],
        "languages": [],
        "saving_throws": []
    },
    "equipment": {
        "weapons": [],
        "armor": [],
        "shields": [],
        "items": [],
        "currency": {"cp": 0, "sp": 0, "ep": 0, "gp": 0, "pp": 0}
    },
    "spellcasting": {
        "spellcasting_class": "",
        "spellcasting_ability": "",
        "spell_save_dc": 8,
        "spell_attack_bonus": 0,
        "spell_slots": {
            "1st": {"total": 0, "used": 0},
            "2nd": {"total": 0, "used": 0},
            "3rd": {"total": 0, "used": 0},
            "4th": {"total": 0, "used": 0},
            "5th": {"total": 0, "used": 0},
            "6th": {"total": 0, "used": 0},
            "7th": {"total": 0, "used": 0},
            "8th": {"total": 0, "used": 0},
            "9th": {"total": 0, "used": 0}
        },
        "spells_known": [],
        "cantrips_known": []
    },
    "class_features": [],
    "species_traits": [],
    "feats": [],
    "custom_content": [],
    "background_feature": {},
    "personality": {
        "traits": [],
        "ideals": [],
        "bonds": [],
        "flaws": []
    },
    "notes": {
        "character_backstory": "",
        "allies_organizations": "",
        "additional_features": "",
        "treasure": ""
    }
}

# ============ VTT PLATFORM TEMPLATES ============

# D&D Beyond format template
DND_BEYOND_TEMPLATE: Dict[str, Any] = {
    "character": {
        "name": "{character_info.name}",
        "level": "{character_info.level}",
        "race": "{character_info.species}",
        "class": "{character_info.character_class}",
        "subclass": "{character_info.subclass}",
        "background": "{character_info.background}",
        "alignment": "{character_info.alignment}",
        "experiencePoints": "{character_info.experience_points}",
        "hitPointMax": "{combat_stats.hit_points.maximum}",
        "hitPointCurrent": "{combat_stats.hit_points.current}",
        "armorClass": "{combat_stats.armor_class}",
        "speed": "{combat_stats.speed.walking}",
        "proficiencyBonus": "{combat_stats.proficiency_bonus}",
        "abilities": [
            {
                "id": 1,
                "name": "Strength",
                "value": "{ability_scores.strength.score}",
                "modifier": "{ability_scores.strength.modifier}",
                "savingThrowProficiency": False
            }
            # ... other abilities
        ],
        "skills": [
            {
                "name": "Acrobatics",
                "modifier": "{skills.acrobatics.modifier}",
                "proficient": "{skills.acrobatics.proficient}",
                "expertise": "{skills.acrobatics.expertise}"
            }
            # ... other skills
        ],
        "inventory": "{equipment}",
        "spells": "{spellcasting}",
        "features": "{class_features}",
        "traits": "{species_traits}"
    }
}

# Roll20 format template
ROLL20_TEMPLATE: Dict[str, Any] = {
    "schema_version": 2,
    "type": "character",
    "character": {
        "name": "{character_info.name}",
        "avatar": "",
        "bio": "{notes.character_backstory}",
        "gmnotes": "",
        "archived": False,
        "inplayerjournals": "",
        "controlledby": "",
        "attribs": [
            {"name": "character_name", "current": "{character_info.name}"},
            {"name": "class_display", "current": "{character_info.character_class}"},
            {"name": "race", "current": "{character_info.species}"},
            {"name": "background", "current": "{character_info.background}"},
            {"name": "alignment", "current": "{character_info.alignment}"},
            {"name": "level", "current": "{character_info.level}"},
            {"name": "experience", "current": "{character_info.experience_points}"},
            {"name": "strength", "current": "{ability_scores.strength.score}"},
            {"name": "dexterity", "current": "{ability_scores.dexterity.score}"},
            {"name": "constitution", "current": "{ability_scores.constitution.score}"},
            {"name": "intelligence", "current": "{ability_scores.intelligence.score}"},
            {"name": "wisdom", "current": "{ability_scores.wisdom.score}"},
            {"name": "charisma", "current": "{ability_scores.charisma.score}"},
            {"name": "hp", "current": "{combat_stats.hit_points.current}"},
            {"name": "hp", "max": "{combat_stats.hit_points.maximum}"},
            {"name": "ac", "current": "{combat_stats.armor_class}"},
            {"name": "speed", "current": "{combat_stats.speed.walking}"},
            {"name": "pb", "current": "{combat_stats.proficiency_bonus}"}
        ],
        "abilities": []
    }
}

# Fantasy Grounds format template
FANTASY_GROUNDS_TEMPLATE: Dict[str, Any] = {
    "character": {
        "name": {"type": "string", "value": "{character_info.name}"},
        "level": {"type": "number", "value": "{character_info.level}"},
        "race": {"type": "string", "value": "{character_info.species}"},
        "classes": {
            "class1": {
                "name": {"type": "string", "value": "{character_info.character_class}"},
                "level": {"type": "number", "value": "{character_info.level}"},
                "subclass": {"type": "string", "value": "{character_info.subclass}"}
            }
        },
        "background": {"type": "string", "value": "{character_info.background}"},
        "alignment": {"type": "string", "value": "{character_info.alignment}"},
        "abilities": {
            "strength": {
                "score": {"type": "number", "value": "{ability_scores.strength.score}"},
                "bonus": {"type": "number", "value": "{ability_scores.strength.modifier}"}
            }
            # ... other abilities
        },
        "hp": {
            "total": {"type": "number", "value": "{combat_stats.hit_points.maximum}"},
            "wounds": {"type": "number", "value": 0}
        },
        "ac": {
            "total": {"type": "number", "value": "{combat_stats.armor_class}"}
        },
        "skills": {},
        "inventory": {},
        "spells": {}
    }
}

# Foundry VTT format template
FOUNDRY_VTT_TEMPLATE: Dict[str, Any] = {
    "name": "{character_info.name}",
    "type": "character",
    "data": {
        "attributes": {
            "hp": {
                "value": "{combat_stats.hit_points.current}",
                "max": "{combat_stats.hit_points.maximum}",
                "temp": "{combat_stats.hit_points.temporary}"
            },
            "ac": {
                "value": "{combat_stats.armor_class}"
            },
            "movement": {
                "walk": "{combat_stats.speed.walking}",
                "fly": "{combat_stats.speed.flying}",
                "swim": "{combat_stats.speed.swimming}",
                "climb": "{combat_stats.speed.climbing}"
            },
            "prof": "{combat_stats.proficiency_bonus}"
        },
        "abilities": {
            "str": {
                "value": "{ability_scores.strength.score}",
                "mod": "{ability_scores.strength.modifier}",
                "save": "{ability_scores.strength.saving_throw}",
                "proficient": 0
            }
            # ... other abilities
        },
        "skills": {
            "acr": {
                "value": "{skills.acrobatics.modifier}",
                "proficient": 0,
                "ability": "dex"
            }
            # ... other skills
        },
        "details": {
            "biography": {
                "value": "{notes.character_backstory}"
            },
            "alignment": "{character_info.alignment}",
            "race": "{character_info.species}",
            "background": "{character_info.background}",
            "class": "{character_info.character_class}",
            "level": {
                "value": "{character_info.level}"
            },
            "xp": {
                "value": "{character_info.experience_points}"
            }
        },
        "traits": {
            "weaponProf": {
                "value": "{proficiencies.weapons}"
            },
            "armorProf": {
                "value": "{proficiencies.armor}"
            },
            "toolProf": {
                "value": "{proficiencies.tools}"
            },
            "languages": {
                "value": "{proficiencies.languages}"
            }
        },
        "spells": "{spellcasting}",
        "currency": "{equipment.currency}"
    },
    "items": "{equipment}",
    "effects": [],
    "flags": {},
    "token": {}
}

# ============ STANDARD FORMAT TEMPLATES ============

# PDF character sheet template
PDF_CHARACTER_SHEET_TEMPLATE: Dict[str, Any] = {
    "template_type": "official_character_sheet",
    "version": "5e_2024",
    "fields": {
        # Page 1 - Character Information
        "CharacterName": "{character_info.name}",
        "ClassLevel": "{character_info.character_class} {character_info.level}",
        "Background": "{character_info.background}",
        "PlayerName": "",
        "Race": "{character_info.species}",
        "Alignment": "{character_info.alignment}",
        "ExperiencePoints": "{character_info.experience_points}",
        
        # Ability Scores
        "STR": "{ability_scores.strength.score}",
        "STRmod": "{ability_scores.strength.modifier}",
        "DEX": "{ability_scores.dexterity.score}",
        "DEXmod": "{ability_scores.dexterity.modifier}",
        "CON": "{ability_scores.constitution.score}",
        "CONmod": "{ability_scores.constitution.modifier}",
        "INT": "{ability_scores.intelligence.score}",
        "INTmod": "{ability_scores.intelligence.modifier}",
        "WIS": "{ability_scores.wisdom.score}",
        "WISmod": "{ability_scores.wisdom.modifier}",
        "CHA": "{ability_scores.charisma.score}",
        "CHAmod": "{ability_scores.charisma.modifier}",
        
        # Saving Throws
        "ST Strength": "{ability_scores.strength.saving_throw}",
        "ST Dexterity": "{ability_scores.dexterity.saving_throw}",
        "ST Constitution": "{ability_scores.constitution.saving_throw}",
        "ST Intelligence": "{ability_scores.intelligence.saving_throw}",
        "ST Wisdom": "{ability_scores.wisdom.saving_throw}",
        "ST Charisma": "{ability_scores.charisma.saving_throw}",
        
        # Skills
        "Acrobatics": "{skills.acrobatics.modifier}",
        "Animal Handling": "{skills.animal_handling.modifier}",
        "Arcana": "{skills.arcana.modifier}",
        "Athletics": "{skills.athletics.modifier}",
        "Deception": "{skills.deception.modifier}",
        "History": "{skills.history.modifier}",
        "Insight": "{skills.insight.modifier}",
        "Intimidation": "{skills.intimidation.modifier}",
        "Investigation": "{skills.investigation.modifier}",
        "Medicine": "{skills.medicine.modifier}",
        "Nature": "{skills.nature.modifier}",
        "Perception": "{skills.perception.modifier}",
        "Performance": "{skills.performance.modifier}",
        "Persuasion": "{skills.persuasion.modifier}",
        "Religion": "{skills.religion.modifier}",
        "Sleight of Hand": "{skills.sleight_of_hand.modifier}",
        "Stealth": "{skills.stealth.modifier}",
        "Survival": "{skills.survival.modifier}",
        
        # Combat Stats
        "AC": "{combat_stats.armor_class}",
        "Initiative": "{ability_scores.dexterity.modifier}",
        "Speed": "{combat_stats.speed.walking}",
        "HPMax": "{combat_stats.hit_points.maximum}",
        "HPCurrent": "{combat_stats.hit_points.current}",
        "HPTemp": "{combat_stats.hit_points.temporary}",
        "HD": "{combat_stats.hit_dice.total}",
        "HDRemaining": "{combat_stats.hit_dice.current}",
        "ProfBonus": "{combat_stats.proficiency_bonus}",
        "Passive Perception": "{combat_stats.passive_perception}"
    },
    "dynamic_sections": {
        "attacks_spellcasting": "{weapons_and_attacks}",
        "equipment": "{equipment}",
        "other_proficiencies": "{proficiencies}",
        "features_traits": "{class_features_and_traits}",
        "spells": "{spellcasting_section}"
    }
}

# JSON export template
JSON_EXPORT_TEMPLATE: Dict[str, Any] = {
    "export_metadata": {
        "format": "json",
        "version": "2.0",
        "created_by": "D&D Character Creator Backend6",
        "export_date": "",
        "character_version": "1.0"
    },
    "character_data": "{complete_character_data}",
    "custom_content": "{custom_content_data}",
    "progression_data": "{level_progression_data}",
    "export_options": {
        "include_progression": True,
        "include_custom_content": True,
        "include_metadata": True,
        "compact_format": False
    }
}

# ============ LAYOUT TEMPLATES ============

# Different layout options for character sheets
LAYOUT_TEMPLATES: Dict[OutputLayout, Dict[str, Any]] = {
    OutputLayout.STANDARD: {
        "description": "Standard D&D character sheet layout",
        "sections": [
            "character_info",
            "ability_scores",
            "skills",
            "combat_stats",
            "equipment",
            "spellcasting",
            "features_traits",
            "background_personality"
        ],
        "formatting": {
            "columns": 2,
            "font_size": "normal",
            "include_descriptions": True,
            "compact_skills": False
        }
    },
    
    OutputLayout.COMPACT: {
        "description": "Condensed layout for quick reference",
        "sections": [
            "character_info",
            "ability_scores",
            "combat_stats",
            "key_features",
            "equipment_summary"
        ],
        "formatting": {
            "columns": 3,
            "font_size": "small",
            "include_descriptions": False,
            "compact_skills": True
        }
    },
    
    OutputLayout.DETAILED: {
        "description": "Comprehensive layout with full details",
        "sections": [
            "character_info",
            "ability_scores",
            "skills_detailed",
            "combat_stats_detailed",
            "equipment_detailed",
            "spellcasting_detailed",
            "features_traits_detailed",
            "background_personality_detailed",
            "progression_notes",
            "custom_content_detailed"
        ],
        "formatting": {
            "columns": 1,
            "font_size": "normal",
            "include_descriptions": True,
            "include_examples": True,
            "include_mechanics": True
        }
    },
    
    OutputLayout.PLAYER_FRIENDLY: {
        "description": "Optimized for player use at the table",
        "sections": [
            "character_summary",
            "quick_stats",
            "actions_combat",
            "spells_quick_reference",
            "equipment_ready",
            "roleplay_reminders"
        ],
        "formatting": {
            "columns": 2,
            "font_size": "large",
            "highlight_important": True,
            "include_quick_reference": True
        }
    },
    
    OutputLayout.DM_REFERENCE: {
        "description": "Focused on information DMs need",
        "sections": [
            "character_summary",
            "combat_capabilities",
            "spellcasting_summary",
            "social_interaction_info",
            "character_motivations",
            "mechanical_interactions"
        ],
        "formatting": {
            "columns": 2,
            "font_size": "normal",
            "highlight_mechanics": True,
            "include_dm_notes": True
        }
    }
}

# ============ VTT PLATFORM SPECIFICATIONS ============

# Technical specifications for each VTT platform
VTT_PLATFORM_SPECS: Dict[VTTPlatform, Dict[str, Any]] = {
    VTTPlatform.DND_BEYOND: {
        "file_format": "json",
        "api_version": "2.0",
        "character_limit": None,
        "supported_features": [
            "full_character_sheet",
            "spellcasting",
            "custom_content",
            "character_builder_integration"
        ],
        "import_method": "api_upload",
        "export_template": "DND_BEYOND_TEMPLATE",
        "validation_required": True,
        "custom_content_support": "limited"
    },
    
    VTTPlatform.ROLL20: {
        "file_format": "json",
        "api_version": "1.0",
        "character_limit": None,
        "supported_features": [
            "character_sheet",
            "token_setup",
            "macro_integration",
            "handout_creation"
        ],
        "import_method": "json_import",
        "export_template": "ROLL20_TEMPLATE",
        "validation_required": False,
        "custom_content_support": "full"
    },
    
    VTTPlatform.FANTASY_GROUNDS: {
        "file_format": "xml",
        "api_version": "4.0",
        "character_limit": None,
        "supported_features": [
            "full_character_sheet",
            "automated_calculations",
            "spell_integration",
            "equipment_automation"
        ],
        "import_method": "file_import",
        "export_template": "FANTASY_GROUNDS_TEMPLATE",
        "validation_required": True,
        "custom_content_support": "full"
    },
    
    VTTPlatform.FOUNDRY_VTT: {
        "file_format": "json",
        "api_version": "10.0",
        "character_limit": None,
        "supported_features": [
            "actor_creation",
            "item_integration",
            "automation_support",
            "module_compatibility"
        ],
        "import_method": "actor_import",
        "export_template": "FOUNDRY_VTT_TEMPLATE",
        "validation_required": False,
        "custom_content_support": "full"
    },
    
    VTTPlatform.OWLBEAR_RODEO: {
        "file_format": "json",
        "api_version": "2.0",
        "character_limit": None,
        "supported_features": [
            "character_tokens",
            "stat_blocks",
            "initiative_tracking"
        ],
        "import_method": "json_import",
        "export_template": "simple_stat_block",
        "validation_required": False,
        "custom_content_support": "basic"
    }
}

# ============ CONTENT EXPORT TEMPLATES ============

# Templates for exporting custom content separately
CUSTOM_CONTENT_TEMPLATES: Dict[ContentType, Dict[str, Any]] = {
    ContentType.SPECIES: {
        "template_name": "species_export",
        "format": {
            "name": "{name}",
            "description": "{description}",
            "creature_type": "{creature_type}",
            "size": "{size}",
            "speed": "{speed}",
            "traits": "{traits}",
            "languages": "{languages}",
            "balance_notes": "{balance_analysis}"
        },
        "required_fields": ["name", "traits", "creature_type"],
        "export_formats": ["json", "markdown", "pdf"]
    },
    
    ContentType.SPELL: {
        "template_name": "spell_export",
        "format": {
            "name": "{name}",
            "level": "{level}",
            "school": "{school}",
            "casting_time": "{casting_time}",
            "range": "{range}",
            "duration": "{duration}",
            "components": "{components}",
            "description": "{description}",
            "at_higher_levels": "{upcast_effects}",
            "spell_lists": "{available_to_classes}"
        },
        "required_fields": ["name", "level", "school", "description"],
        "export_formats": ["json", "markdown", "spell_card"]
    },
    
    ContentType.FEAT: {
        "template_name": "feat_export",
        "format": {
            "name": "{name}",
            "feat_type": "{feat_type}",
            "prerequisites": "{prerequisites}",
            "benefits": "{mechanical_benefits}",
            "description": "{description}",
            "design_notes": "{balance_rationale}"
        },
        "required_fields": ["name", "benefits", "description"],
        "export_formats": ["json", "markdown", "reference_card"]
    }
}

# ============ PROGRESSION EXPORT TEMPLATES ============

# Templates for exporting character progression data
PROGRESSION_EXPORT_TEMPLATE: Dict[str, Any] = {
    "character_id": "{character_id}",
    "progression_type": "{progression_type}",
    "levels": {
        "level_{level}": {
            "character_sheet": "{level_character_sheet}",
            "new_features": "{features_gained}",
            "asi_feat_choice": "{asi_or_feat_selection}",
            "spell_changes": "{spell_progression}",
            "milestone_notes": "{level_milestone}"
        }
    },
    "thematic_evolution": {
        "tier_1_local_hero": "{tier_1_narrative}",
        "tier_2_regional_champion": "{tier_2_narrative}",
        "tier_3_world_shaper": "{tier_3_narrative}",
        "tier_4_cosmic_force": "{tier_4_narrative}"
    },
    "build_guide": {
        "optimization_notes": "{mechanical_optimization}",
        "tactical_advice": "{combat_tactics}",
        "roleplay_evolution": "{character_development}",
        "multiclass_considerations": "{multiclass_options}"
    }
}

# ============ HELPER FUNCTIONS FOR TEMPLATE MANAGEMENT ============

def get_export_template(platform: VTTPlatform) -> Dict[str, Any]:
    """Get the export template for a specific VTT platform."""
    template_name = VTT_PLATFORM_SPECS.get(platform, {}).get("export_template", "")
    
    templates = {
        "DND_BEYOND_TEMPLATE": DND_BEYOND_TEMPLATE,
        "ROLL20_TEMPLATE": ROLL20_TEMPLATE,
        "FANTASY_GROUNDS_TEMPLATE": FANTASY_GROUNDS_TEMPLATE,
        "FOUNDRY_VTT_TEMPLATE": FOUNDRY_VTT_TEMPLATE
    }
    
    return templates.get(template_name, UNIVERSAL_CHARACTER_TEMPLATE)

def get_layout_template(layout: OutputLayout) -> Dict[str, Any]:
    """Get the layout configuration for a specific output layout."""
    return LAYOUT_TEMPLATES.get(layout, LAYOUT_TEMPLATES[OutputLayout.STANDARD])

def get_content_export_template(content_type: ContentType) -> Dict[str, Any]:
    """Get the export template for custom content of a specific type."""
    return CUSTOM_CONTENT_TEMPLATES.get(content_type, {})

def get_platform_specs(platform: VTTPlatform) -> Dict[str, Any]:
    """Get technical specifications for a VTT platform."""
    return VTT_PLATFORM_SPECS.get(platform, {})

def validate_export_data(data: Dict[str, Any], template: Dict[str, Any]) -> List[str]:
    """
    Validate that export data contains all required fields for a template.
    
    Args:
        data: The character data to export
        template: The export template to validate against
        
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    def check_template_fields(template_section: Any, data_section: Any, path: str = ""):
        if isinstance(template_section, dict):
            for key, value in template_section.items():
                current_path = f"{path}.{key}" if path else key
                
                if isinstance(value, str) and value.startswith("{") and value.endswith("}"):
                    # This is a template field reference
                    field_path = value[1:-1]  # Remove braces
                    if not check_field_exists(data, field_path):
                        errors.append(f"Missing required field: {field_path} (needed for {current_path})")
                elif isinstance(value, dict):
                    data_value = data_section.get(key, {}) if isinstance(data_section, dict) else {}
                    check_template_fields(value, data_value, current_path)
                elif isinstance(value, list):
                    # Handle list templates
                    pass  # Could add list validation here
    
    def check_field_exists(data: Dict[str, Any], field_path: str) -> bool:
        """Check if a nested field exists in the data."""
        try:
            parts = field_path.split('.')
            current = data
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return False
            return True
        except (KeyError, TypeError):
            return False
    
    check_template_fields(template, data)
    return errors

def format_template_string(template_str: str, data: Dict[str, Any]) -> str:
    """
    Format a template string with data, handling nested field references.
    
    Args:
        template_str: Template string with {field.subfield} references
        data: Data dictionary to pull values from
        
    Returns:
        Formatted string with values substituted
    """
    import re
    
    def replace_field(match):
        field_path = match.group(1)
        try:
            parts = field_path.split('.')
            current = data
            for part in parts:
                current = current[part]
            return str(current)
        except (KeyError, TypeError):
            return f"[MISSING: {field_path}]"
    
    # Replace all {field.path} references
    return re.sub(r'\{([^}]+)\}', replace_field, template_str)

def get_supported_export_formats() -> Dict[VTTPlatform, List[str]]:
    """Get all supported export formats organized by platform."""
    formats = {}
    for platform, specs in VTT_PLATFORM_SPECS.items():
        formats[platform] = specs.get("supported_features", [])
    return formats

def get_export_requirements(platform: VTTPlatform) -> Dict[str, Any]:
    """Get export requirements and limitations for a platform."""
    specs = VTT_PLATFORM_SPECS.get(platform, {})
    return {
        "file_format": specs.get("file_format", "json"),
        "validation_required": specs.get("validation_required", False),
        "custom_content_support": specs.get("custom_content_support", "basic"),
        "character_limit": specs.get("character_limit"),
        "import_method": specs.get("import_method", "file_import")
    }

# ============ MODULE METADATA ============

__version__ = '2.0.0'
__description__ = 'Character export templates and VTT format specifications'
__author__ = 'D&D Character Creator Backend6'

# Clean Architecture compliance metadata
CLEAN_ARCHITECTURE_COMPLIANCE = {
    "layer": "core/constants",
    "dependencies": ["core/enums"],
    "dependents": ["domain/services", "infrastructure/export_services"],
    "infrastructure_independent": True,
    "focuses_on": "Character data representation standards"
}

# Export template statistics
EXPORT_STATISTICS = {
    "vtt_platforms_supported": len(VTT_PLATFORM_SPECS),
    "layout_options": len(LAYOUT_TEMPLATES),
    "content_types_exportable": len(CUSTOM_CONTENT_TEMPLATES),
    "total_templates": (
        len(VTT_PLATFORM_SPECS) + 
        len(LAYOUT_TEMPLATES) + 
        len(CUSTOM_CONTENT_TEMPLATES) + 
        2  # PDF and JSON templates
    )
}