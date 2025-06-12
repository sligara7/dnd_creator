# Alignment value object

from dataclasses import dataclass

@dataclass(frozen=True)
class Alignment:
    """Value object representing character alignment."""
    
    ethical: str  # Lawful, Neutral, Chaotic
    moral: str    # Good, Neutral, Evil
    
    def __post_init__(self):
        valid_ethical = {"Lawful", "Neutral", "Chaotic"}
        valid_moral = {"Good", "Neutral", "Evil"}
        
        if self.ethical not in valid_ethical:
            raise ValueError(f"Invalid ethical alignment: {self.ethical}")
        if self.moral not in valid_moral:
            raise ValueError(f"Invalid moral alignment: {self.moral}")
    
    def __str__(self) -> str:
        if self.ethical == "Neutral" and self.moral == "Neutral":
            return "True Neutral"
        return f"{self.ethical} {self.moral}"
    
    @property
    def is_good(self) -> bool:
        return self.moral == "Good"
    
    @property
    def is_evil(self) -> bool:
        return self.moral == "Evil"
    
    @property
    def is_lawful(self) -> bool:
        return self.ethical == "Lawful"
    
    @property
    def is_chaotic(self) -> bool:
        return self.ethical == "Chaotic"