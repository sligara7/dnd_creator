# Update the DOMAIN_COMPONENTS to reflect actual implementation status
DOMAIN_COMPONENTS = {
    "abstractions": {
        "implemented": ["AbstractContentValidator"],  # Only if actually implemented
        "missing": ["AbstractCharacterClass", "AbstractSpecies", "AbstractEquipment", 
                   "AbstractWeapon", "AbstractArmor", "AbstractSpell", "AbstractFeat"]
    },
    "entities": {
        "implemented": ["CharacterConcept", "ContentCollection"],  # Based on file evidence
        "missing": ["Character", "GeneratedContent"]
    },
    "value_objects": {
        "implemented": ["ValidationResult", "BalanceMetrics"],  # Inferred from usage
        "missing": ["ContentMetadata", "GenerationConstraints", "ThematicElements"]
    },
    "utilities": {
        "implemented": ["balance_calculator", "content_utils", "naming_validator", 
                       "mechanical_parser", "rule_checker"],  # Based on file evidence
        "missing": []
    },
    "enums": {
        "implemented": ["content_types", "validation_types", "dnd_constants"],
        "missing": ["generation_methods", "mechanical_category"]
    },
    "exceptions": {
        "implemented": ["generation_errors", "validation_errors", "rule_violation_errors"],
        "missing": []
    }
}