# infrastructure/data/character_state_repository.py
class CharacterStateRepository:
    """Repository for persisting character state."""
    
    def save_state(self, character_id: str, state: CharacterState) -> None:
        """Save character state to storage."""
        pass
    
    def load_state(self, character_id: str) -> CharacterState:
        """Load character state from storage."""
        pass