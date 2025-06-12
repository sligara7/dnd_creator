from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple

class RuleEngine(ABC):
    """Base interface for all rule engines."""
    
    @abstractmethod
    def validate(self, data: Any) -> Tuple[bool, List[str]]:
        """Validate data against rules."""
        pass

class CharacterRule(RuleEngine):
    """Base class for character-related rules."""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def add_error(self, message: str) -> None:
        """Add validation error."""
        self.errors.append(message)
    
    def add_warning(self, message: str) -> None:
        """Add validation warning."""
        self.warnings.append(message)
    
    def reset(self) -> None:
        """Reset validation state."""
        self.errors.clear()
        self.warnings.clear()