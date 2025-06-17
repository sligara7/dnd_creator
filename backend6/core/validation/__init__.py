# 3. Validation Framework Restructure
# /core/validation/validators/
# Purpose: Split validation into focused validators

# ability_score_validator.py
# Class: AbilityScoreValidator
# Content: Validates ability scores, modifiers, ASI rules
# class_level_validator.py
# Class: ClassLevelValidator
# Content: Validates class levels, multiclassing prerequisites, subclass requirements
# equipment_validator.py
# Class: EquipmentValidator
# Content: Validates weapons, armor, proficiencies, attunement
# spellcasting_validator.py
# Class: SpellcastingValidator
# Content: Validates spell slots, known spells, casting abilities
# character_identity_validator.py
# Class: CharacterIdentityValidator
# Content: Validates species, background, alignment, personality
# validation
# Purpose: Validation orchestration and results

# validation_result.py
# Class: ValidationResult
# Class: ValidationSummary
# Content: Structured validation result containers
# character_validator.py
# Class: CharacterValidator
# Content: Orchestrates all validators, provides unified validation interface
# validation_decorators.py
# Content: All validation decorators (@validate_name, @validate_spell, etc.)