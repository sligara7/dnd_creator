# AbilityScore value object

from typing import Dict, Optional

class AbilityScore:
    """
    Value object representing a D&D ability score with its component values.
    
    This is immutable and represents the complete calculation of an ability score
    including base score, bonuses, and modifiers.
    """
    
    def __init__(self, base_score: int = 10):
        if not isinstance(base_score, int) or base_score < 1 or base_score > 30:
            raise ValueError(f"Base score must be an integer between 1 and 30, got {base_score}")
        
        self._base_score: int = base_score
        self._bonus: int = 0
        self._set_score: Optional[int] = None
        self._stacking_bonuses: Dict[str, int] = {}
    
    @property
    def base_score(self) -> int:
        """The base ability score."""
        return self._base_score
    
    @property
    def bonus(self) -> int:
        """Additional bonus to the ability score."""
        return self._bonus
    
    @property
    def set_score(self) -> Optional[int]:
        """Score set by magical effects (overrides calculation)."""
        return self._set_score
    
    @property
    def stacking_bonuses(self) -> Dict[str, int]:
        """Named bonuses that stack with other bonuses."""
        return self._stacking_bonuses.copy()
    
    @property
    def total_score(self) -> int:
        """Calculate the total ability score."""
        if self._set_score is not None:
            return max(1, min(30, self._set_score))
        
        total = self._base_score + self._bonus + sum(self._stacking_bonuses.values())
        return max(1, min(30, total))
    
    @property
    def modifier(self) -> int:
        """Calculate the ability modifier."""
        return (self.total_score - 10) // 2
    
    def add_bonus(self, amount: int) -> 'AbilityScore':
        """Return new AbilityScore with additional bonus."""
        new_score = AbilityScore(self._base_score)
        new_score._bonus = self._bonus + amount
        new_score._set_score = self._set_score
        new_score._stacking_bonuses = self._stacking_bonuses.copy()
        return new_score
    
    def add_stacking_bonus(self, source: str, amount: int) -> 'AbilityScore':
        """Return new AbilityScore with additional stacking bonus."""
        new_score = AbilityScore(self._base_score)
        new_score._bonus = self._bonus
        new_score._set_score = self._set_score
        new_score._stacking_bonuses = self._stacking_bonuses.copy()
        new_score._stacking_bonuses[source] = amount
        return new_score
    
    def set_score_override(self, score: int) -> 'AbilityScore':
        """Return new AbilityScore with set score override."""
        new_score = AbilityScore(self._base_score)
        new_score._bonus = self._bonus
        new_score._set_score = score
        new_score._stacking_bonuses = self._stacking_bonuses.copy()
        return new_score
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, AbilityScore):
            return False
        return (self._base_score == other._base_score and
                self._bonus == other._bonus and
                self._set_score == other._set_score and
                self._stacking_bonuses == other._stacking_bonuses)
    
    def __str__(self) -> str:
        modifier_str = f"+{self.modifier}" if self.modifier >= 0 else str(self.modifier)
        return f"{self.total_score} ({modifier_str})"
    
    def __repr__(self) -> str:
        return f"AbilityScore(base={self._base_score}, total={self.total_score}, modifier={self.modifier})"