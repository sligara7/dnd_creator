# infrastructure/validation/character_validator.py  
class CharacterValidationService:
    """Validates character data against D&D rules."""
    
    def validate_character_data(self, character: Character) -> ValidationResult:
        """Validate complete character (from validate_character_json)."""
        # Logic from original validation methods
        pass
    
    def validate_equipment_choices(self, equipment: Dict[str, Any]) -> ValidationResult:
        """Validate equipment selections."""
        # Logic from equipment validation in original
        pass
    
    def validate_spell_choices(self, spells: Dict[str, Any], 
                             character: Character) -> ValidationResult:
        """Validate spell selections."""
        # Logic from spell validation in original
        pass