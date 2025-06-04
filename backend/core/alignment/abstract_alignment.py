from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union, Any, Tuple

class AbstractAlignment(ABC):
    """
    Abstract base class for handling character alignments in D&D 5e (2024 Edition).
    
    Alignments in D&D describe a character's moral and ethical outlook:
    - Law vs. Chaos (ethical axis): Attitude toward order, tradition, and rules
    - Good vs. Evil (moral axis): Attitude toward others' well-being and dignity
    
    The nine classic alignments are combinations of:
    - Lawful Good (LG): Organized compassion, honor-bound to help others
    - Neutral Good (NG): Pure altruism without preference for order or freedom
    - Chaotic Good (CG): Kindness through independence and freedom
    - Lawful Neutral (LN): Order and organization without moral judgment
    - True Neutral (N): Balance or ambivalence to moral/ethical extremes
    - Chaotic Neutral (CN): Freedom from both society's restrictions and moral expectations
    - Lawful Evil (LE): Structured and methodical in harming others or society
    - Neutral Evil (NE): Selfishness without particular attachment to freedom or laws
    - Chaotic Evil (CE): Destruction of both order and others' well-being
    
    Note: 2024 rules emphasize alignment as a guideline rather than a restriction.
    """
    
    # Ethical axis options (Law vs. Chaos)
    ETHICAL_AXIS = ["lawful", "neutral", "chaotic"]
    
    # Moral axis options (Good vs. Evil)
    MORAL_AXIS = ["good", "neutral", "evil"]
    
    # Special case: True Neutral is represented as just "neutral"
    NEUTRAL_NEUTRAL = "neutral"
    
    def __init__(self, ethical: str = "neutral", moral: str = "neutral"):
        """
        Initialize an alignment object.
        
        Args:
            ethical: Position on the Law-Chaos axis ("lawful", "neutral", "chaotic")
            moral: Position on the Good-Evil axis ("good", "neutral", "evil")
        """
        ethical = ethical.lower()
        moral = moral.lower()
        
        if not self.validate_alignment_components(ethical, moral):
            raise ValueError(f"Invalid alignment components: {ethical} {moral}")
            
        self.ethical = ethical
        self.moral = moral
    
    @abstractmethod
    def get_all_alignments(self) -> List[Tuple[str, str]]:
        """
        Return a list of all available alignments.
        
        Returns:
            List[Tuple[str, str]]: List of tuples (ethical, moral) representing all alignments
        """
        pass
        
    @abstractmethod
    def get_alignment_description(self, ethical: str, moral: str) -> str:
        """
        Get a description of what an alignment means.
        
        Args:
            ethical: Position on the Law-Chaos axis
            moral: Position on the Good-Evil axis
            
        Returns:
            str: Description of the alignment
        """
        pass
        
    @abstractmethod
    def validate_alignment(self, ethical: str, moral: str) -> bool:
        """
        Check if an alignment is valid.
        
        Args:
            ethical: Position on the Law-Chaos axis
            moral: Position on the Good-Evil axis
            
        Returns:
            bool: True if valid, False otherwise
        """
        pass
        
    @abstractmethod
    def get_alignment_roleplay_suggestions(self, ethical: str, moral: str) -> Dict[str, Any]:
        """
        Provide roleplay guidance based on alignment.
        
        Args:
            ethical: Position on the Law-Chaos axis
            moral: Position on the Good-Evil axis
            
        Returns:
            Dict[str, Any]: Dictionary containing roleplay suggestions
        """
        pass
        
    def validate_alignment_components(self, ethical: str, moral: str) -> bool:
        """
        Validate individual alignment components.
        
        Args:
            ethical: Position on the Law-Chaos axis
            moral: Position on the Good-Evil axis
            
        Returns:
            bool: True if components are valid, False otherwise
        """
        # Special case for True Neutral
        if ethical == moral == "neutral":
            return True
            
        return ethical in self.ETHICAL_AXIS and moral in self.MORAL_AXIS
        
    @abstractmethod
    def is_compatible_with_deity(self, ethical: str, moral: str, deity_alignment: Tuple[str, str]) -> bool:
        """
        Check if an alignment is compatible with a deity's alignment.
        
        Args:
            ethical: Position on the Law-Chaos axis
            moral: Position on the Good-Evil axis
            deity_alignment: Tuple (ethical, moral) representing deity's alignment
            
        Returns:
            bool: True if compatible, False otherwise
        """
        pass
        
    @abstractmethod
    def is_compatible_with_class(self, ethical: str, moral: str, class_name: str) -> bool:
        """
        Check if an alignment is compatible with a character class.
        
        Args:
            ethical: Position on the Law-Chaos axis
            moral: Position on the Good-Evil axis
            class_name: Name of the character class
            
        Returns:
            bool: True if compatible, False otherwise
        """
        pass
        
    @abstractmethod
    def get_common_behaviors(self, ethical: str, moral: str) -> Dict[str, List[str]]:
        """
        Get lists of common behaviors for an alignment.
        
        Args:
            ethical: Position on the Law-Chaos axis
            moral: Position on the Good-Evil axis
            
        Returns:
            Dict[str, List[str]]: Dictionary with typical behaviors
        """
        pass
        
    @abstractmethod
    def suggest_alignment_shift(self, ethical: str, moral: str, action_description: str) -> Optional[Tuple[str, str]]:
        """
        Suggest potential alignment shift based on character actions.
        
        Args:
            ethical: Current position on the Law-Chaos axis
            moral: Current position on the Good-Evil axis
            action_description: Description of the character's action
            
        Returns:
            Optional[Tuple[str, str]]: Suggested new alignment, or None if no shift
        """
        pass
    
    def __str__(self) -> str:
        """
        String representation of alignment.
        
        Returns:
            str: Formatted alignment string
        """
        # Special case for True Neutral
        if self.ethical == "neutral" and self.moral == "neutral":
            return "True Neutral"
            
        return f"{self.ethical.capitalize()} {self.moral.capitalize()}"
        
    def __eq__(self, other) -> bool:
        """
        Equality comparison.
        
        Args:
            other: Another alignment to compare with
            
        Returns:
            bool: True if alignments are the same
        """
        if not isinstance(other, AbstractAlignment):
            return False
            
        return self.ethical == other.ethical and self.moral == other.moral
        
    def to_dict(self) -> Dict[str, str]:
        """
        Convert alignment to dictionary.
        
        Returns:
            Dict[str, str]: Dictionary representation of alignment
        """
        return {
            "ethical": self.ethical,
            "moral": self.moral,
            "description": self.get_alignment_description(self.ethical, self.moral)
        }