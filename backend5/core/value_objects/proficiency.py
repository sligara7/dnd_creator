# ProficiencyLevel enum

from enum import Enum

class ProficiencyLevel(Enum):
    """Enumeration for proficiency levels in D&D 5e."""
    NONE = 0
    PROFICIENT = 1
    EXPERT = 2
    
    def __str__(self) -> str:
        """String representation of proficiency level."""
        return self.name.title()
    
    @property
    def multiplier(self) -> int:
        """Get the proficiency bonus multiplier for this level."""
        return self.value
    
    @classmethod
    def from_string(cls, value: str) -> 'ProficiencyLevel':
        """Create ProficiencyLevel from string."""
        value_map = {
            'none': cls.NONE,
            'proficient': cls.PROFICIENT,
            'expert': cls.EXPERT,
            'expertise': cls.EXPERT  # Alternative name
        }
        return value_map.get(value.lower(), cls.NONE)