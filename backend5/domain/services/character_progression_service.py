# domain/services/character_progression.py
class CharacterProgressionService:
    """Handles character level progression and advancement."""
    
    def create_progression_to_level(self, base_character: Character, 
                                  target_level: int, description: str) -> List[Character]:
        """Create full progression (from create_character_with_progression)."""
        # Logic from original progression methods
        pass
    
    def level_up_character(self, character: Character, new_class: str = None) -> Character:
        """Level up a character by one level."""
        # Logic from level-up portions of original methods
        pass
    
    def calculate_level_up_changes(self, character: Character, 
                                 target_level: int) -> Dict[str, Any]:
        """Calculate mechanical changes for level up."""
        # Logic from _merge_level_up_changes method
        pass