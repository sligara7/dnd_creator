# filepath: /home/ajs7/dnd_tools/dnd_char_creator/backend5/domain/content/classes/wizard.py
class Wizard(AbstractCharacterClass):
    """Concrete implementation of the Wizard class."""
    
    @property
    def class_name(self) -> str:
        return "Wizard"
    
    @property
    def hit_die(self) -> int:
        return 6
    
    @property
    def primary_ability(self) -> List[str]:
        return ["intelligence"]
    
    @property
    def saving_throw_proficiencies(self) -> List[str]:
        return ["intelligence", "wisdom"]
    
    def get_spellcasting_progression(self, level: int) -> Optional[Dict[str, Any]]:
        """Wizard full spellcasting progression."""
        spell_slots = {
            1: {1: 2},
            2: {1: 3},
            3: {1: 4, 2: 2},
            4: {1: 4, 2: 3},
            5: {1: 4, 2: 3, 3: 2},
            # ... full progression table
        }
        
        return {
            "spellcasting_ability": "intelligence",
            "spell_slots": spell_slots.get(level, {}),
            "spells_known": self._calculate_spells_known(level),
            "cantrips_known": self._calculate_cantrips_known(level),
            "ritual_casting": True,
            "spellbook": True
        }
    
    def validate_multiclass_prerequisites(self, character: Character) -> List[str]:
        """Validate Wizard multiclass prerequisites."""
        errors = []
        
        int_score = character.get_ability_score_value("intelligence")
        if int_score < 13:
            errors.append("Multiclass into Wizard requires Intelligence 13")
        
        return errors