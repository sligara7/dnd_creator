"""
Validation Constants

Constants used for validating generated content against D&D 5e rules
and content quality standards.
"""

# Rule compliance levels
RULE_COMPLIANCE_LEVELS = {
    "strict": "Must follow all official rules exactly",
    "standard": "Follows rules with minor acceptable variations",
    "flexible": "Maintains spirit of rules with creative interpretation",
    "homebrew": "Custom rules allowed with clear documentation"
}

# Validation severity levels
VALIDATION_SEVERITIES = [
    "info", "warning", "error", "critical"
]

# Content requirements by type
CONTENT_REQUIREMENTS = {
    "species": {
        "mandatory": ["name", "size", "speed", "languages"],
        "optional": ["traits", "ability_score_increase", "proficiencies"],
        "mechanical": ["size_category", "base_speed"]
    },
    "class": {
        "mandatory": ["name", "hit_die", "primary_ability", "saving_throws"],
        "optional": ["multiclass_requirements", "spellcasting"],
        "mechanical": ["hit_points", "proficiencies", "features"]
    },
    "spell": {
        "mandatory": ["name", "level", "school", "casting_time", "range", "duration"],
        "optional": ["components", "ritual", "concentration"],
        "mechanical": ["damage", "save_dc", "spell_attack"]
    },
    "equipment": {
        "mandatory": ["name", "type", "cost", "weight"],
        "optional": ["properties", "damage", "armor_class"],
        "mechanical": ["item_properties", "usage_restrictions"]
    },
    "feat": {
        "mandatory": ["name", "description", "benefit"],
        "optional": ["prerequisites", "repeatable"],
        "mechanical": ["ability_improvements", "feature_grants"]
    }
}

# Mandatory fields for all content
MANDATORY_FIELDS = ["name", "description", "type"]

# Optional but recommended fields
OPTIONAL_FIELDS = ["flavor_text", "example_usage", "design_notes"]