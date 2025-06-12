from typing import List, Dict, Any
from ...core.entities.character import Character
from ...core.value_objects.validation_result import ValidationIssue, ValidationSeverity

class ValidationRules:
    """D&D 5e validation rules implementation."""
    
    def validate_class_requirements(self, character: Character, class_name: str, level: int) -> List[ValidationIssue]:
        """Validate class-specific requirements."""
        issues = []
        
        # Class-specific validation logic
        class_validators = {
            "Wizard": self._validate_wizard_requirements,
            "Cleric": self._validate_cleric_requirements,
            "Fighter": self._validate_fighter_requirements,
            # ... more classes
        }
        
        validator = class_validators.get(class_name)
        if validator:
            issues.extend(validator(character, level))
        
        return issues
    
    def validate_species_requirements(self, character: Character, species: str) -> List[ValidationIssue]:
        """Validate species-specific requirements."""
        issues = []
        
        # Species-specific validation logic
        species_validators = {
            "Human": self._validate_human_requirements,
            "Elf": self._validate_elf_requirements,
            "Dwarf": self._validate_dwarf_requirements,
            # ... more species
        }
        
        validator = species_validators.get(species)
        if validator:
            issues.extend(validator(character))
        
        return issues
    
    def validate_multiclass_prerequisites(self, character: Character, class_name: str) -> List[ValidationIssue]:
        """Validate multiclass prerequisites."""
        issues = []
        
        # Multiclass ability score requirements
        multiclass_requirements = {
            "Barbarian": {"strength": 13},
            "Bard": {"charisma": 13},
            "Cleric": {"wisdom": 13},
            "Druid": {"wisdom": 13},
            "Fighter": {"strength": 13, "dexterity": 13},  # Either/or
            "Monk": {"dexterity": 13, "wisdom": 13},
            "Paladin": {"strength": 13, "charisma": 13},
            "Ranger": {"dexterity": 13, "wisdom": 13},
            "Rogue": {"dexterity": 13},
            "Sorcerer": {"charisma": 13},
            "Warlock": {"charisma": 13},
            "Wizard": {"intelligence": 13}
        }
        
        requirements = multiclass_requirements.get(class_name, {})
        for ability, min_score in requirements.items():
            if character.get_ability_score_value(ability) < min_score:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code="MULTICLASS_PREREQUISITE",
                    message=f"Multiclass into {class_name} requires {ability.title()} {min_score}+",
                    field=ability,
                    suggested_fix=f"Increase {ability} to at least {min_score}"
                ))
        
        return issues
    
    def validate_point_buy_scores(self, character: Character) -> List[ValidationIssue]:
        """Validate point buy ability scores."""
        issues = []
        
        # Point buy validation logic
        total_cost = 0
        point_costs = {8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 13: 5, 14: 7, 15: 9}
        
        for ability in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
            score = character.get_ability_score_value(ability)
            base_score = score  # Would need to separate racial bonuses
            
            if base_score < 8 or base_score > 15:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code="INVALID_POINT_BUY_SCORE",
                    message=f"Point buy {ability} base score ({base_score}) must be 8-15",
                    field=ability
                ))
            else:
                total_cost += point_costs.get(base_score, 0)
        
        if total_cost > 27:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                code="POINT_BUY_OVERSPENT",
                message=f"Point buy total ({total_cost}) exceeds 27 points",
                suggested_fix="Reduce ability scores to stay within 27 points"
            ))
        
        return issues
    
    # === Class-specific validators ===
    
    def _validate_wizard_requirements(self, character: Character, level: int) -> List[ValidationIssue]:
        """Validate Wizard-specific requirements."""
        issues = []
        
        # Wizards need spellbook
        if not any("spellbook" in str(item).lower() for item in character.equipment):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                code="MISSING_SPELLBOOK",
                message="Wizard needs a spellbook",
                suggested_fix="Add spellbook to equipment"
            ))
        
        return issues
    
    def _validate_cleric_requirements(self, character: Character, level: int) -> List[ValidationIssue]:
        """Validate Cleric-specific requirements."""
        issues = []
        
        # Clerics need holy symbol
        if not any("holy symbol" in str(item).lower() for item in character.equipment):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                code="MISSING_HOLY_SYMBOL",
                message="Cleric needs a holy symbol",
                suggested_fix="Add holy symbol to equipment"
            ))
        
        return issues
    
    def _validate_fighter_requirements(self, character: Character, level: int) -> List[ValidationIssue]:
        """Validate Fighter-specific requirements."""
        issues = []
        # Fighter-specific validation
        return issues
    
    # === Species-specific validators ===
    
    def _validate_human_requirements(self, character: Character) -> List[ValidationIssue]:
        """Validate Human-specific requirements."""
        issues = []
        # Human-specific validation
        return issues
    
    def _validate_elf_requirements(self, character: Character) -> List[ValidationIssue]:
        """Validate Elf-specific requirements."""
        issues = []
        # Elf-specific validation
        return issues
    
    def _validate_dwarf_requirements(self, character: Character) -> List[ValidationIssue]:
        """Validate Dwarf-specific requirements."""
        issues = []
        # Dwarf-specific validation
        return issues