from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional

class AbstractAlignment(ABC):
    """
    Abstract base class defining the interface for character alignments in D&D 5e (2024 Edition).
    
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
    
    Note: 2024 rules emphasize alignment as a guideline rather than a restriction,
    with no mechanical penalties for alignment choices or changes.
    """
    
    # Ethical axis options (Law vs. Chaos)
    ETHICAL_AXIS = ["lawful", "neutral", "chaotic"]
    
    # Moral axis options (Good vs. Evil)
    MORAL_AXIS = ["good", "neutral", "evil"]
    
    # Special case: True Neutral is represented as just "neutral"
    NEUTRAL_NEUTRAL = "neutral"
    
    @abstractmethod
    def get_all_alignments(self) -> List[Tuple[str, str]]:
        """
        Return a list of all available alignments according to the rules.
        
        Returns:
            List[Tuple[str, str]]: List of tuples (ethical, moral) representing all valid alignments
        """
        pass
        
    @abstractmethod
    def get_alignment_description(self, ethical: str, moral: str) -> str:
        """
        Get the official description of what an alignment represents.
        
        Args:
            ethical: Position on the Law-Chaos axis
            moral: Position on the Good-Evil axis
            
        Returns:
            str: Official description of the alignment
        """
        pass
        
    @abstractmethod
    def validate_alignment(self, ethical: str, moral: str) -> bool:
        """
        Check if an alignment is valid according to the rules.
        
        Args:
            ethical: Position on the Law-Chaos axis
            moral: Position on the Good-Evil axis
            
        Returns:
            bool: True if valid, False otherwise
        """
        pass
    
    @abstractmethod
    def is_compatible_with_deity(self, ethical: str, moral: str, deity_alignment: Tuple[str, str]) -> bool:
        """
        Check if an alignment is compatible with a deity's alignment.
        
        Per 2024 rules, certain deities may have alignment preferences or requirements.
        
        Args:
            ethical: Position on the Law-Chaos axis
            moral: Position on the Good-Evil axis
            deity_alignment: Tuple (ethical, moral) representing deity's alignment
            
        Returns:
            bool: True if compatible, False otherwise
        """
        pass