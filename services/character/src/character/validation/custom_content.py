"""Custom content validation rules.

This module provides validation rules for custom character content,
including custom races, classes, feats, and other game elements.
"""

from typing import Dict, Any, List
from ..core.validation import (
    ValidationResult,
    Validator,
    required_fields,
    field_type,
    field_length,
    field_range,
    field_choices,
)
from ..models.custom_content import CustomContent
from ..models.character import (
    Race,
    Class,
    Feature,
    Background,
)
from ..models.enums import (
    AbilityType, 
    ContentType,
    ApprovalStatus,
    ContentCategory,
)

def validate_custom_content(
    content: CustomContent,
    content_type: str,
) -> ValidationResult:
    """Validate custom content against balance guidelines.
    
    Args:
        content: Content to validate
        content_type: Type of content
        
    Returns:
        Validation result
    """
    result = ValidationResult()
    
    # Basic validation
    if not content:
        result.add_error("Content is required")
        return result
        
    # Common validation
    common = validate_common_fields(content)
    result.merge(common)
    if not result.valid:
        return result
        
    # Type-specific validation
    if content_type == "race":
        race = validate_custom_race(content)
        result.merge(race)
        
    elif content_type == "class":
        class_ = validate_custom_class(content)
        result.merge(class_)
        
    elif content_type == "background":
        background = validate_custom_background(content)
        result.merge(background)
        
    elif content_type == "feat":
        feat = validate_custom_feat(content)
        result.merge(feat)
        
    else:
        result.add_error(f"Unknown content type: {content_type}")
        
    return result

def validate_common_fields(content: CustomContent) -> ValidationResult:
    """Validate fields common to all custom content.
    
    Args:
        content: Content to validate
        
    Returns:
        Validation result
    """
    # Required fields
    validator = Validator([
        required_fields([
            "name",
            "description",
            "content_type",
            "category",
        ]),
        field_length("name", max_len=100),
        field_length("description", min_len=50, max_len=2000),
        field_choices("content_type", [t.value for t in ContentType]),
        field_choices("category", [c.value for c in ContentCategory]),
    ])
    
    result = validator.validate(content)
    
    # Theme tags
    if len(content.theme_tags) > 5:
        result.add_warning("Large number of theme tags")
        
    # Mechanics tags
    if len(content.mechanics_tags) > 5:
        result.add_warning("Large number of mechanics tags")
        
    return result

def validate_custom_race(content: CustomContent) -> ValidationResult:
    """Validate custom race content.
    
    Args:
        content: Race content to validate
        
    Returns:
        Validation result
    """
    result = ValidationResult()
    
    # Basic structure
    properties = content.properties or {}
    if not all(k in properties for k in ["size", "speed", "ability_bonuses"]):
        result.add_error(
            "Race must specify size, speed, and ability bonuses"
        )
        return result
        
    # Ability score bonuses
    total_bonus = sum(properties["ability_bonuses"].values())
    if total_bonus > 4:
        result.add_error("Total ability score bonuses cannot exceed +4")
        
    # Speed
    speed = properties.get("speed", 0)
    if speed < 25 or speed > 35:
        result.add_warning("Unusual movement speed value")
        
    # Traits
    traits = properties.get("traits", [])
    if len(traits) > 3:
        result.add_warning("Large number of racial traits")
        
    for trait in traits:
        if len(trait.get("description", "")) > 500:
            result.add_warning("Very long trait description")
            
    return result

def validate_custom_class(content: CustomContent) -> ValidationResult:
    """Validate custom class content.
    
    Args:
        content: Class content to validate
        
    Returns:
        Validation result
    """
    result = ValidationResult()
    
    # Basic structure
    properties = content.properties or {}
    if not all(k in properties for k in ["hit_dice", "proficiencies", "features"]):
        result.add_error(
            "Class must specify hit dice, proficiencies, and features"
        )
        return result
        
    # Hit dice
    hit_dice = properties["hit_dice"]
    if hit_dice not in ["d6", "d8", "d10", "d12"]:
        result.add_error("Invalid hit dice")
        
    # Proficiencies
    proficiencies = properties["proficiencies"]
    if len(proficiencies) > 6:
        result.add_warning("Large number of proficiencies")
        
    # Features
    features = properties["features"]
    if len(features) > 3:
        result.add_warning("Large number of 1st level features")
        
    for feature in features:
        if not feature.get("level"):
            result.add_error("Features must specify level granted")
            
        if len(feature.get("description", "")) > 500:
            result.add_warning("Very long feature description")
            
    return result

def validate_custom_background(content: CustomContent) -> ValidationResult:
    """Validate custom background content.
    
    Args:
        content: Background content to validate
        
    Returns:
        Validation result
    """
    result = ValidationResult()
    
    # Basic structure
    properties = content.properties or {}
    if not all(k in properties for k in [
        "skill_proficiencies",
        "tool_proficiencies",
        "languages",
        "equipment",
        "feature",
    ]):
        result.add_error(
            "Background must specify proficiencies, languages, "
            "equipment, and feature"
        )
        return result
        
    # Skill proficiencies
    skills = properties["skill_proficiencies"]
    if len(skills) > 2:
        result.add_error("Background cannot grant more than 2 skill proficiencies")
        
    # Tool proficiencies
    tools = properties["tool_proficiencies"]
    if len(tools) > 2:
        result.add_warning("Unusual number of tool proficiencies")
        
    # Languages
    languages = properties["languages"]
    if len(languages) > 2:
        result.add_warning("Unusual number of languages")
        
    # Equipment
    equipment = properties["equipment"]
    if len(equipment) > 5:
        result.add_warning("Large amount of starting equipment")
        
    # Feature
    feature = properties["feature"]
    if len(feature.get("description", "")) > 500:
        result.add_warning("Very long feature description")
        
    return result

def validate_custom_feat(content: CustomContent) -> ValidationResult:
    """Validate custom feat content.
    
    Args:
        content: Feat content to validate
        
    Returns:
        Validation result
    """
    result = ValidationResult()
    
    # Basic structure
    properties = content.properties or {}
    if not all(k in properties for k in ["benefits", "prerequisites"]):
        result.add_error(
            "Feat must specify benefits and prerequisites"
        )
        return result
        
    # Benefits
    benefits = properties["benefits"]
    if not benefits:
        result.add_error("Feat must grant at least one benefit")
        
    if len(benefits) > 3:
        result.add_warning("Large number of feat benefits")
        
    # Ability score increases
    asi = properties.get("ability_score_increase", {})
    total_increase = sum(asi.values())
    if total_increase > 2:
        result.add_error("Feat cannot grant more than +2 total to ability scores")
        
    # Prerequisites
    prerequisites = properties["prerequisites"]
    if len(prerequisites) > 2:
        result.add_warning("Complex prerequisites may limit feat accessibility")
        
    return result
