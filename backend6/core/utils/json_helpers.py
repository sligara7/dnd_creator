"""
Character sheet JSON utilities and validation for D&D Creative Content Framework.

This module provides pure utility functions for:
- Character sheet JSON structure validation
- VTT platform compatibility formatting
- JSON schema validation and enforcement
- Character data serialization/deserialization
- Export format transformation utilities

Supports all VTT platforms mentioned in README.md:
- Roll20, FoundryVTT, D&D Beyond, Fantasy Grounds, Encounter+
"""

import json
import json5  # For enhanced JSON parsing with comments and trailing commas
from typing import Dict, Any, List, Optional, Union, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
import re
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class JSONValidationError(Exception):
    """JSON validation specific error."""
    def __init__(self, message: str, field_path: str = None, validation_type: str = None):
        super().__init__(message)
        self.field_path = field_path
        self.validation_type = validation_type
        self.message = message


class VTTFormat(Enum):
    """Supported VTT export formats."""
    STANDARD = "standard"
    ROLL20 = "roll20"
    FOUNDRY_VTT = "foundry"
    DND_BEYOND = "dndbeyond"
    FANTASY_GROUNDS = "fantasy_grounds"
    ENCOUNTER_PLUS = "encounter_plus"


@dataclass
class JSONValidationResult:
    """Result of JSON validation operation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    missing_fields: List[str]
    invalid_fields: List[str]
    vtt_compatibility: Dict[VTTFormat, bool]


# ============================================================================
# CHARACTER SHEET JSON SCHEMA VALIDATION
# ============================================================================

# Core character sheet schema based on README.md examples
CHARACTER_SHEET_SCHEMA = {
    "type": "object",
    "required": [
        "character_info", "ability_scores", "classes", "level", "hit_points",
        "armor_class", "proficiency_bonus", "saving_throws", "skills",
        "combat_stats", "spells", "equipment", "features", "personality"
    ],
    "properties": {
        "character_info": {
            "type": "object",
            "required": ["name", "species", "background", "alignment"],
            "properties": {
                "name": {"type": "string", "minLength": 1},
                "species": {"type": "string", "minLength": 1},
                "background": {"type": "string", "minLength": 1},
                "alignment": {"type": "string", "minLength": 1},
                "concept": {"type": "string"}
            }
        },
        "ability_scores": {
            "type": "object",
            "required": ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"],
            "properties": {
                "strength": {"type": "integer", "minimum": 1, "maximum": 30},
                "dexterity": {"type": "integer", "minimum": 1, "maximum": 30},
                "constitution": {"type": "integer", "minimum": 1, "maximum": 30},
                "intelligence": {"type": "integer", "minimum": 1, "maximum": 30},
                "wisdom": {"type": "integer", "minimum": 1, "maximum": 30},
                "charisma": {"type": "integer", "minimum": 1, "maximum": 30}
            }
        },
        "classes": {
            "type": "object",
            "minProperties": 1,
            "patternProperties": {
                "^[a-zA-Z ]+$": {"type": "integer", "minimum": 1, "maximum": 20}
            }
        },
        "level": {"type": "integer", "minimum": 1, "maximum": 20},
        "hit_points": {
            "type": "object",
            "required": ["current", "maximum"],
            "properties": {
                "current": {"type": "integer", "minimum": 0},
                "maximum": {"type": "integer", "minimum": 1},
                "temporary": {"type": "integer", "minimum": 0}
            }
        },
        "armor_class": {"type": "integer", "minimum": 1},
        "proficiency_bonus": {"type": "integer", "minimum": 2, "maximum": 6},
        "saving_throws": {
            "type": "object",
            "required": ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"],
            "properties": {
                "strength": {"type": "integer"},
                "dexterity": {"type": "integer"},
                "constitution": {"type": "integer"},
                "intelligence": {"type": "integer"},
                "wisdom": {"type": "integer"},
                "charisma": {"type": "integer"}
            }
        },
        "skills": {"type": "object"},
        "combat_stats": {
            "type": "object",
            "required": ["initiative", "speed"],
            "properties": {
                "initiative": {"type": "integer"},
                "speed": {"type": "integer", "minimum": 0}
            }
        },
        "spells": {
            "type": "object",
            "properties": {
                "spell_attack_bonus": {"type": "integer"},
                "spell_save_dc": {"type": "integer"},
                "spell_slots": {"type": "object"},
                "spells_known": {"type": "array"}
            }
        },
        "equipment": {
            "type": "object",
            "properties": {
                "weapons": {"type": "array"},
                "armor": {"type": "array"},
                "gear": {"type": "array"},
                "signature_equipment": {"type": "array"}
            }
        },
        "features": {
            "type": "object",
            "properties": {
                "species_traits": {"type": "array"},
                "class_features": {"type": "array"},
                "custom_features": {"type": "array"}
            }
        },
        "personality": {
            "type": "object",
            "properties": {
                "traits": {"type": "array"},
                "ideals": {"type": "array"},
                "bonds": {"type": "array"},
                "flaws": {"type": "array"}
            }
        }
    }
}

# VTT-specific field requirements
VTT_REQUIREMENTS = {
    VTTFormat.ROLL20: {
        "required_fields": ["character_info.name", "ability_scores", "classes", "level"],
        "field_mappings": {
            "character_info.name": "name",
            "armor_class": "ac",
            "hit_points.current": "hp",
            "hit_points.maximum": "hp_max"
        },
        "max_name_length": 50,
        "supports_custom_content": True
    },
    VTTFormat.FOUNDRY_VTT: {
        "required_fields": ["character_info", "ability_scores", "classes", "level", "hit_points"],
        "field_mappings": {
            "character_info": "data.details",
            "ability_scores": "data.abilities",
            "hit_points": "data.attributes.hp"
        },
        "max_name_length": 100,
        "supports_custom_content": True
    },
    VTTFormat.DND_BEYOND: {
        "required_fields": ["character_info", "ability_scores", "classes", "level", "species"],
        "field_mappings": {
            "species": "race",
            "classes": "class"
        },
        "max_name_length": 30,
        "supports_custom_content": False
    },
    VTTFormat.FANTASY_GROUNDS: {
        "required_fields": ["character_info.name", "ability_scores", "classes"],
        "field_mappings": {},
        "max_name_length": 40,
        "supports_custom_content": True
    },
    VTTFormat.ENCOUNTER_PLUS: {
        "required_fields": ["character_info", "ability_scores", "level"],
        "field_mappings": {},
        "max_name_length": 60,
        "supports_custom_content": True
    }
}


# ============================================================================
# CORE JSON UTILITIES
# ============================================================================

def safe_json_load(file_path: Union[str, Path], use_json5: bool = False) -> Optional[Dict[str, Any]]:
    """
    Safely load JSON from file with enhanced error handling.
    
    Args:
        file_path: Path to JSON file
        use_json5: Whether to use json5 for enhanced parsing
        
    Returns:
        Parsed JSON data or None if failed
        
    Raises:
        JSONValidationError: If JSON is invalid
    """
    try:
        file_path = Path(file_path)
        if not file_path.exists():
            raise JSONValidationError(f"JSON file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if use_json5:
            return json5.loads(content)
        else:
            return json.loads(content)
            
    except json.JSONDecodeError as e:
        raise JSONValidationError(
            f"Invalid JSON in {file_path}: {e.msg} at line {e.lineno}, column {e.colno}",
            validation_type="json_syntax"
        )
    except json5.JSONDecodeError as e:
        raise JSONValidationError(
            f"Invalid JSON5 in {file_path}: {str(e)}",
            validation_type="json5_syntax"
        )
    except Exception as e:
        raise JSONValidationError(f"Failed to load JSON from {file_path}: {str(e)}")


def safe_json_save(data: Dict[str, Any], file_path: Union[str, Path], 
                   pretty: bool = True, ensure_ascii: bool = False) -> bool:
    """
    Safely save data to JSON file with formatting.
    
    Args:
        data: Data to save
        file_path: Output file path
        pretty: Whether to format JSON with indentation
        ensure_ascii: Whether to escape non-ASCII characters
        
    Returns:
        True if successful, False otherwise
        
    Raises:
        JSONValidationError: If data cannot be serialized
    """
    try:
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Ensure data is JSON serializable
        json.dumps(data, ensure_ascii=ensure_ascii)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(data, f, indent=2, ensure_ascii=ensure_ascii, separators=(',', ': '))
            else:
                json.dump(data, f, ensure_ascii=ensure_ascii)
                
        return True
        
    except TypeError as e:
        raise JSONValidationError(f"Data not JSON serializable: {str(e)}")
    except Exception as e:
        raise JSONValidationError(f"Failed to save JSON to {file_path}: {str(e)}")


def deep_merge_json(base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two JSON objects, with update taking precedence.
    
    Args:
        base: Base JSON object
        update: Update JSON object
        
    Returns:
        Merged JSON object
    """
    result = base.copy()
    
    for key, value in update.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_json(result[key], value)
        else:
            result[key] = value
            
    return result


def extract_json_paths(data: Dict[str, Any], prefix: str = "") -> List[str]:
    """
    Extract all JSON paths from a nested dictionary.
    
    Args:
        data: JSON data
        prefix: Path prefix
        
    Returns:
        List of all JSON paths
    """
    paths = []
    
    for key, value in data.items():
        current_path = f"{prefix}.{key}" if prefix else key
        paths.append(current_path)
        
        if isinstance(value, dict):
            paths.extend(extract_json_paths(value, current_path))
        elif isinstance(value, list) and value and isinstance(value[0], dict):
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    paths.extend(extract_json_paths(item, f"{current_path}[{i}]"))
                    
    return paths


def get_json_value_by_path(data: Dict[str, Any], path: str) -> Any:
    """
    Get value from JSON using dot notation path.
    
    Args:
        data: JSON data
        path: Dot notation path (e.g., "character_info.name")
        
    Returns:
        Value at path or None if not found
    """
    try:
        keys = path.split('.')
        current = data
        
        for key in keys:
            if '[' in key and ']' in key:
                # Handle array indexing
                array_key, index_str = key.split('[')
                index = int(index_str.rstrip(']'))
                current = current[array_key][index]
            else:
                current = current[key]
                
        return current
        
    except (KeyError, IndexError, TypeError, ValueError):
        return None


def set_json_value_by_path(data: Dict[str, Any], path: str, value: Any) -> bool:
    """
    Set value in JSON using dot notation path.
    
    Args:
        data: JSON data to modify
        path: Dot notation path
        value: Value to set
        
    Returns:
        True if successful, False otherwise
    """
    try:
        keys = path.split('.')
        current = data
        
        # Navigate to parent
        for key in keys[:-1]:
            if '[' in key and ']' in key:
                array_key, index_str = key.split('[')
                index = int(index_str.rstrip(']'))
                current = current[array_key][index]
            else:
                if key not in current:
                    current[key] = {}
                current = current[key]
        
        # Set final value
        final_key = keys[-1]
        if '[' in final_key and ']' in final_key:
            array_key, index_str = final_key.split('[')
            index = int(index_str.rstrip(']'))
            if array_key not in current:
                current[array_key] = []
            while len(current[array_key]) <= index:
                current[array_key].append(None)
            current[array_key][index] = value
        else:
            current[final_key] = value
            
        return True
        
    except (KeyError, IndexError, TypeError, ValueError):
        return False


# ============================================================================
# CHARACTER SHEET VALIDATION
# ============================================================================

def validate_character_sheet(character_data: Dict[str, Any]) -> JSONValidationResult:
    """
    Validate character sheet JSON against D&D schema.
    
    Args:
        character_data: Character sheet data
        
    Returns:
        Validation result with detailed feedback
    """
    errors = []
    warnings = []
    missing_fields = []
    invalid_fields = []
    
    # Check required top-level fields
    schema = CHARACTER_SHEET_SCHEMA
    required_fields = schema.get("required", [])
    
    for field in required_fields:
        if field not in character_data:
            missing_fields.append(field)
            errors.append(f"Missing required field: {field}")
    
    # Validate character_info
    if "character_info" in character_data:
        char_info = character_data["character_info"]
        if not isinstance(char_info, dict):
            invalid_fields.append("character_info")
            errors.append("character_info must be an object")
        else:
            for req_field in ["name", "species", "background", "alignment"]:
                if req_field not in char_info or not char_info[req_field]:
                    missing_fields.append(f"character_info.{req_field}")
                    errors.append(f"Missing required character info: {req_field}")
    
    # Validate ability scores
    if "ability_scores" in character_data:
        abilities = character_data["ability_scores"]
        if not isinstance(abilities, dict):
            invalid_fields.append("ability_scores")
            errors.append("ability_scores must be an object")
        else:
            required_abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
            for ability in required_abilities:
                if ability not in abilities:
                    missing_fields.append(f"ability_scores.{ability}")
                    errors.append(f"Missing ability score: {ability}")
                elif not isinstance(abilities[ability], int) or abilities[ability] < 1 or abilities[ability] > 30:
                    invalid_fields.append(f"ability_scores.{ability}")
                    errors.append(f"Invalid {ability} score: {abilities[ability]} (must be 1-30)")
    
    # Validate level
    if "level" in character_data:
        level = character_data["level"]
        if not isinstance(level, int) or level < 1 or level > 20:
            invalid_fields.append("level")
            errors.append(f"Invalid level: {level} (must be 1-20)")
    
    # Validate classes
    if "classes" in character_data:
        classes = character_data["classes"]
        if not isinstance(classes, dict):
            invalid_fields.append("classes")
            errors.append("classes must be an object")
        elif not classes:
            missing_fields.append("classes")
            errors.append("Character must have at least one class")
        else:
            total_class_levels = sum(classes.values())
            character_level = character_data.get("level", 1)
            if total_class_levels != character_level:
                warnings.append(f"Class levels ({total_class_levels}) don't match character level ({character_level})")
    
    # Validate hit points
    if "hit_points" in character_data:
        hp = character_data["hit_points"]
        if not isinstance(hp, dict):
            invalid_fields.append("hit_points")
            errors.append("hit_points must be an object")
        else:
            if "maximum" not in hp or not isinstance(hp["maximum"], int) or hp["maximum"] < 1:
                invalid_fields.append("hit_points.maximum")
                errors.append("hit_points.maximum must be a positive integer")
            if "current" not in hp or not isinstance(hp["current"], int) or hp["current"] < 0:
                invalid_fields.append("hit_points.current")
                errors.append("hit_points.current must be a non-negative integer")
            if hp.get("current", 0) > hp.get("maximum", 0):
                warnings.append("Current HP exceeds maximum HP")
    
    # Check VTT compatibility
    vtt_compatibility = {}
    for vtt_format in VTTFormat:
        vtt_compatibility[vtt_format] = check_vtt_compatibility(character_data, vtt_format)
    
    return JSONValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        missing_fields=missing_fields,
        invalid_fields=invalid_fields,
        vtt_compatibility=vtt_compatibility
    )


def check_vtt_compatibility(character_data: Dict[str, Any], vtt_format: VTTFormat) -> bool:
    """
    Check if character data is compatible with specific VTT format.
    
    Args:
        character_data: Character sheet data
        vtt_format: Target VTT format
        
    Returns:
        True if compatible, False otherwise
    """
    if vtt_format not in VTT_REQUIREMENTS:
        return False
    
    requirements = VTT_REQUIREMENTS[vtt_format]
    
    # Check required fields
    for field_path in requirements["required_fields"]:
        if get_json_value_by_path(character_data, field_path) is None:
            return False
    
    # Check name length
    name = get_json_value_by_path(character_data, "character_info.name")
    if name and len(name) > requirements["max_name_length"]:
        return False
    
    # Check custom content support
    if not requirements["supports_custom_content"]:
        # Check for custom content indicators
        species = get_json_value_by_path(character_data, "character_info.species")
        if species and any(indicator in species.lower() for indicator in ["custom", "variant", "homebrew"]):
            return False
        
        classes = character_data.get("classes", {})
        for class_name in classes.keys():
            if any(indicator in class_name.lower() for indicator in ["custom", "variant", "homebrew"]):
                return False
    
    return True


def get_validation_summary(validation_result: JSONValidationResult) -> str:
    """
    Generate human-readable validation summary.
    
    Args:
        validation_result: Validation result
        
    Returns:
        Formatted summary string
    """
    summary = []
    
    if validation_result.is_valid:
        summary.append("✅ Character sheet is valid")
    else:
        summary.append("❌ Character sheet has validation errors")
    
    if validation_result.errors:
        summary.append(f"\n🚫 Errors ({len(validation_result.errors)}):")
        for error in validation_result.errors:
            summary.append(f"  - {error}")
    
    if validation_result.warnings:
        summary.append(f"\n⚠️  Warnings ({len(validation_result.warnings)}):")
        for warning in validation_result.warnings:
            summary.append(f"  - {warning}")
    
    # VTT Compatibility
    compatible_vtts = [vtt.value for vtt, compat in validation_result.vtt_compatibility.items() if compat]
    incompatible_vtts = [vtt.value for vtt, compat in validation_result.vtt_compatibility.items() if not compat]
    
    if compatible_vtts:
        summary.append(f"\n✅ Compatible VTTs: {', '.join(compatible_vtts)}")
    if incompatible_vtts:
        summary.append(f"\n❌ Incompatible VTTs: {', '.join(incompatible_vtts)}")
    
    return "\n".join(summary)


# ============================================================================
# VTT FORMAT CONVERSION
# ============================================================================

def convert_to_vtt_format(character_data: Dict[str, Any], vtt_format: VTTFormat) -> Dict[str, Any]:
    """
    Convert character data to VTT-specific format.
    
    Args:
        character_data: Source character data
        vtt_format: Target VTT format
        
    Returns:
        Converted character data
        
    Raises:
        JSONValidationError: If conversion fails
    """
    if vtt_format not in VTT_REQUIREMENTS:
        raise JSONValidationError(f"Unsupported VTT format: {vtt_format}")
    
    requirements = VTT_REQUIREMENTS[vtt_format]
    converted_data = character_data.copy()
    
    # Apply field mappings
    for source_path, target_path in requirements["field_mappings"].items():
        source_value = get_json_value_by_path(character_data, source_path)
        if source_value is not None:
            set_json_value_by_path(converted_data, target_path, source_value)
    
    # Format-specific transformations
    if vtt_format == VTTFormat.ROLL20:
        converted_data = _convert_to_roll20_format(converted_data)
    elif vtt_format == VTTFormat.FOUNDRY_VTT:
        converted_data = _convert_to_foundry_format(converted_data)
    elif vtt_format == VTTFormat.DND_BEYOND:
        converted_data = _convert_to_dndbeyond_format(converted_data)
    elif vtt_format == VTTFormat.FANTASY_GROUNDS:
        converted_data = _convert_to_fantasy_grounds_format(converted_data)
    elif vtt_format == VTTFormat.ENCOUNTER_PLUS:
        converted_data = _convert_to_encounter_plus_format(converted_data)
    
    return converted_data


def _convert_to_roll20_format(character_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert to Roll20-specific format."""
    converted = character_data.copy()
    
    # Roll20 expects specific field names
    if "armor_class" in converted:
        converted["ac"] = converted.pop("armor_class")
    
    if "hit_points" in converted:
        hp = converted.pop("hit_points")
        converted["hp"] = hp.get("current", 0)
        converted["hp_max"] = hp.get("maximum", 0)
    
    # Flatten ability scores for Roll20
    if "ability_scores" in converted:
        abilities = converted["ability_scores"]
        for ability, score in abilities.items():
            converted[f"{ability}_score"] = score
            converted[f"{ability}_mod"] = (score - 10) // 2
    
    return converted


def _convert_to_foundry_format(character_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert to FoundryVTT-specific format."""
    converted = {
        "name": get_json_value_by_path(character_data, "character_info.name"),
        "type": "character",
        "data": {
            "details": character_data.get("character_info", {}),
            "abilities": {},
            "attributes": {
                "hp": character_data.get("hit_points", {}),
                "ac": {"value": character_data.get("armor_class", 10)}
            },
            "skills": character_data.get("skills", {}),
            "spells": character_data.get("spells", {}),
            "traits": character_data.get("features", {})
        }
    }
    
    # Convert ability scores to Foundry format
    abilities = character_data.get("ability_scores", {})
    for ability, score in abilities.items():
        converted["data"]["abilities"][ability] = {
            "value": score,
            "mod": (score - 10) // 2
        }
    
    return converted


def _convert_to_dndbeyond_format(character_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert to D&D Beyond-specific format."""
    converted = character_data.copy()
    
    # D&D Beyond uses "race" instead of "species"
    if "character_info" in converted and "species" in converted["character_info"]:
        converted["character_info"]["race"] = converted["character_info"].pop("species")
    
    # Remove custom content if present (D&D Beyond doesn't support it)
    if "features" in converted:
        features = converted["features"]
        if "custom_features" in features:
            features.pop("custom_features")
    
    return converted


def _convert_to_fantasy_grounds_format(character_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert to Fantasy Grounds-specific format."""
    # Fantasy Grounds uses XML, but we'll structure for XML conversion
    converted = {
        "character": {
            "name": get_json_value_by_path(character_data, "character_info.name"),
            "class": character_data.get("classes", {}),
            "level": character_data.get("level", 1),
            "abilities": character_data.get("ability_scores", {}),
            "hp": character_data.get("hit_points", {}),
            "ac": character_data.get("armor_class", 10)
        }
    }
    
    return converted


def _convert_to_encounter_plus_format(character_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert to Encounter+ specific format."""
    converted = character_data.copy()
    
    # Encounter+ specific formatting
    if "character_info" in converted:
        char_info = converted["character_info"]
        converted["characterName"] = char_info.get("name", "")
        converted["characterRace"] = char_info.get("species", "")
        converted["characterClass"] = list(character_data.get("classes", {}).keys())[0] if character_data.get("classes") else ""
    
    return converted


# ============================================================================
# PROGRESSION FILE UTILITIES
# ============================================================================

def create_progression_file(character_name: str, level_sheets: Dict[int, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Create complete progression file from individual level sheets.
    
    Args:
        character_name: Character name
        level_sheets: Dictionary mapping levels to character sheets
        
    Returns:
        Complete progression file structure
    """
    progression = {
        "character_name": character_name,
        "progression_type": "complete",
        "levels": {},
        "tier_progression": {},
        "thematic_evolution": {},
        "milestones": {},
        "summary": {
            "total_levels": len(level_sheets),
            "level_range": f"1-{max(level_sheets.keys()) if level_sheets else 1}",
            "classes": {},
            "custom_content_used": []
        }
    }
    
    # Process each level
    for level, sheet in sorted(level_sheets.items()):
        progression["levels"][str(level)] = sheet
        
        # Track classes
        classes = sheet.get("classes", {})
        for class_name, class_level in classes.items():
            if class_name not in progression["summary"]["classes"]:
                progression["summary"]["classes"][class_name] = {"first_level": level, "levels": []}
            progression["summary"]["classes"][class_name]["levels"].append(level)
        
        # Track custom content
        features = sheet.get("features", {})
        if "custom_features" in features:
            for feature in features["custom_features"]:
                if feature.get("name") not in progression["summary"]["custom_content_used"]:
                    progression["summary"]["custom_content_used"].append(feature.get("name"))
    
    # Add tier progression (based on README.md examples)
    if level_sheets:
        max_level = max(level_sheets.keys())
        if max_level >= 5:
            progression["tier_progression"]["tier_1"] = "Establishing heroic identity"
        if max_level >= 11:
            progression["tier_progression"]["tier_2"] = "Embracing heroic responsibility"
        if max_level >= 17:
            progression["tier_progression"]["tier_3"] = "Ascending to legendary status"
        if max_level >= 20:
            progression["tier_progression"]["tier_4"] = "Achieving ultimate power"
    
    return progression


def extract_level_from_filename(filename: str) -> Optional[int]:
    """
    Extract level number from character sheet filename.
    
    Args:
        filename: Character sheet filename
        
    Returns:
        Level number or None if not found
    """
    # Pattern: character_name_level_XX.json
    pattern = r'_level_(\d{2})\.json$'
    match = re.search(pattern, filename)
    if match:
        return int(match.group(1))
    
    # Alternative pattern: character_name_lvl_X.json
    pattern = r'_lvl_(\d+)\.json$'
    match = re.search(pattern, filename)
    if match:
        return int(match.group(1))
    
    return None


def generate_level_filename(character_name: str, level: int, vtt_format: VTTFormat = VTTFormat.STANDARD) -> str:
    """
    Generate standardized filename for character sheet.
    
    Args:
        character_name: Character name
        level: Character level
        vtt_format: Target VTT format
        
    Returns:
        Standardized filename
    """
    # Sanitize character name for filename
    safe_name = re.sub(r'[^\w\-_\.]', '_', character_name.lower())
    safe_name = re.sub(r'_+', '_', safe_name).strip('_')
    
    # Format level with zero padding
    level_str = f"{level:02d}"
    
    # Add VTT suffix if not standard
    if vtt_format != VTTFormat.STANDARD:
        return f"{safe_name}_level_{level_str}_{vtt_format.value}.json"
    else:
        return f"{safe_name}_level_{level_str}.json"


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def clean_json_for_export(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Clean JSON data for export by removing null values and empty objects.
    
    Args:
        data: JSON data to clean
        
    Returns:
        Cleaned JSON data
    """
    if isinstance(data, dict):
        cleaned = {}
        for key, value in data.items():
            if value is not None:
                cleaned_value = clean_json_for_export(value)
                if cleaned_value != {} and cleaned_value != []:
                    cleaned[key] = cleaned_value
        return cleaned
    elif isinstance(data, list):
        return [clean_json_for_export(item) for item in data if item is not None]
    else:
        return data


def calculate_json_size(data: Dict[str, Any]) -> Tuple[int, str]:
    """
    Calculate JSON size in bytes and human-readable format.
    
    Args:
        data: JSON data
        
    Returns:
        Tuple of (bytes, human_readable_string)
    """
    json_str = json.dumps(data, separators=(',', ':'))
    size_bytes = len(json_str.encode('utf-8'))
    
    # Convert to human readable
    if size_bytes < 1024:
        size_str = f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        size_str = f"{size_bytes / 1024:.1f} KB"
    else:
        size_str = f"{size_bytes / (1024 * 1024):.1f} MB"
    
    return size_bytes, size_str


def validate_json_against_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
    """
    Simple JSON schema validation.
    
    Args:
        data: JSON data to validate
        schema: JSON schema
        
    Returns:
        List of validation errors
    """
    errors = []
    
    # This is a simplified schema validator
    # For production, consider using jsonschema library
    
    if schema.get("type") == "object":
        if not isinstance(data, dict):
            errors.append(f"Expected object, got {type(data).__name__}")
            return errors
        
        # Check required fields
        required = schema.get("required", [])
        for field in required:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        # Check properties
        properties = schema.get("properties", {})
        for field, field_schema in properties.items():
            if field in data:
                field_errors = validate_json_against_schema(data[field], field_schema)
                errors.extend([f"{field}.{err}" for err in field_errors])
    
    elif schema.get("type") == "integer":
        if not isinstance(data, int):
            errors.append(f"Expected integer, got {type(data).__name__}")
        else:
            minimum = schema.get("minimum")
            maximum = schema.get("maximum")
            if minimum is not None and data < minimum:
                errors.append(f"Value {data} below minimum {minimum}")
            if maximum is not None and data > maximum:
                errors.append(f"Value {data} above maximum {maximum}")
    
    elif schema.get("type") == "string":
        if not isinstance(data, str):
            errors.append(f"Expected string, got {type(data).__name__}")
        else:
            min_length = schema.get("minLength")
            if min_length is not None and len(data) < min_length:
                errors.append(f"String too short: {len(data)} < {min_length}")
    
    return errors


# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================

def export_character_sheets(character_data: Dict[str, Any], output_dir: Union[str, Path], 
                          formats: List[VTTFormat] = None) -> Dict[str, str]:
    """
    Export character sheets in multiple formats.
    
    Args:
        character_data: Character data
        output_dir: Output directory
        formats: List of VTT formats to export
        
    Returns:
        Dictionary mapping format names to file paths
    """
    if formats is None:
        formats = [VTTFormat.STANDARD]
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    exported_files = {}
    character_name = get_json_value_by_path(character_data, "character_info.name") or "unnamed_character"
    level = character_data.get("level", 1)
    
    for vtt_format in formats:
        try:
            # Convert to format
            converted_data = convert_to_vtt_format(character_data, vtt_format)
            
            # Generate filename
            filename = generate_level_filename(character_name, level, vtt_format)
            file_path = output_dir / filename
            
            # Save file
            if safe_json_save(converted_data, file_path):
                exported_files[vtt_format.value] = str(file_path)
                logger.info(f"Exported {vtt_format.value} format to {file_path}")
            else:
                logger.error(f"Failed to export {vtt_format.value} format")
                
        except Exception as e:
            logger.error(f"Error exporting {vtt_format.value} format: {e}")
    
    return exported_files


def batch_validate_character_sheets(sheet_directory: Union[str, Path]) -> Dict[str, JSONValidationResult]:
    """
    Validate all character sheets in a directory.
    
    Args:
        sheet_directory: Directory containing character sheets
        
    Returns:
        Dictionary mapping filenames to validation results
    """
    sheet_directory = Path(sheet_directory)
    results = {}
    
    if not sheet_directory.exists():
        logger.error(f"Directory does not exist: {sheet_directory}")
        return results
    
    # Find all JSON files
    json_files = list(sheet_directory.glob("*.json"))
    
    for json_file in json_files:
        try:
            character_data = safe_json_load(json_file)
            if character_data:
                validation_result = validate_character_sheet(character_data)
                results[json_file.name] = validation_result
                
                if not validation_result.is_valid:
                    logger.warning(f"Validation errors in {json_file.name}: {len(validation_result.errors)} errors")
            else:
                logger.error(f"Could not load {json_file.name}")
                
        except Exception as e:
            logger.error(f"Error validating {json_file.name}: {e}")
    
    return results


# ============================================================================
# MAIN UTILITY FUNCTIONS
# ============================================================================

def get_supported_vtt_formats() -> List[str]:
    """Get list of supported VTT format names."""
    return [fmt.value for fmt in VTTFormat]


def is_valid_character_sheet(character_data: Dict[str, Any]) -> bool:
    """Quick validation check for character sheet."""
    try:
        result = validate_character_sheet(character_data)
        return result.is_valid
    except Exception:
        return False


def get_character_summary(character_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate character summary from sheet data.
    
    Args:
        character_data: Character sheet data
        
    Returns:
        Summary information
    """
    return {
        "name": get_json_value_by_path(character_data, "character_info.name"),
        "species": get_json_value_by_path(character_data, "character_info.species"),
        "classes": character_data.get("classes", {}),
        "level": character_data.get("level", 1),
        "hp": character_data.get("hit_points", {}).get("maximum", 0),
        "ac": character_data.get("armor_class", 10),
        "has_custom_content": bool(
            character_data.get("features", {}).get("custom_features") or
            any("custom" in str(class_name).lower() for class_name in character_data.get("classes", {}).keys())
        )
    }