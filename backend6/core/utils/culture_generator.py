"""
Simple Culture Generator for D&D Character Creation.

MINIMAL VERSION: Focused on character creation with optional cultural enhancement.
Culture features are simple suggestions that enhance but never restrict creativity.

Philosophy:
- Character creation comes first
- Culture enhances but never restricts
- Simple, clean generation
- Creative freedom is paramount
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import re

# ============================================================================
# MINIMAL IMPORTS - Only what we need for character creation
# ============================================================================

# Optional culture support - graceful fallback if not available
try:
    from ..enums.culture_types import CultureAuthenticityLevel
    CULTURE_SUPPORT = True
except ImportError:
    class CultureAuthenticityLevel:
        CREATIVE = "creative"
        GAMING = "gaming"
    CULTURE_SUPPORT = False

from ..exceptions.culture import CultureError


# ============================================================================
# SIMPLE CULTURE DATACLASS - Character Focused
# ============================================================================

@dataclass(frozen=True)
class CharacterCulture:
    """Simple culture structure focused on character creation."""
    
    # Essential elements
    name: str = "Unique Culture"
    description: str = "A culture perfect for character backgrounds"
    
    # Character names (the most important part)
    male_names: List[str] = field(default_factory=list)
    female_names: List[str] = field(default_factory=list)
    unisex_names: List[str] = field(default_factory=list)
    family_names: List[str] = field(default_factory=list)
    
    # Optional character background support
    personality_traits: List[str] = field(default_factory=list)
    background_hooks: List[str] = field(default_factory=list)
    cultural_values: List[str] = field(default_factory=list)
    
    # Gaming utility
    pronunciation_notes: List[str] = field(default_factory=list)
    gaming_tips: List[str] = field(default_factory=list)
    
    # Optional metadata (simple)
    authenticity_level: Optional[str] = "creative"  # creative, gaming, fantasy
    character_ready: bool = True
    
    def get_all_names(self) -> List[str]:
        """Get all names for character creation."""
        return (self.male_names + self.female_names + 
                self.unisex_names + self.family_names)
    
    def get_random_name(self, gender: Optional[str] = None) -> Optional[str]:
        """Get a random name for character creation."""
        import random
        
        if gender == "male" and self.male_names:
            return random.choice(self.male_names)
        elif gender == "female" and self.female_names:
            return random.choice(self.female_names)
        elif self.unisex_names:
            return random.choice(self.unisex_names)
        
        all_names = self.get_all_names()
        return random.choice(all_names) if all_names else None
    
    def get_character_inspiration(self) -> Dict[str, List[str]]:
        """Get character creation inspiration."""
        return {
            'personality_traits': self.personality_traits,
            'background_hooks': self.background_hooks,
            'cultural_values': self.cultural_values
        }


# ============================================================================
# SIMPLE CULTURE GENERATOR - No Complexity 
# ============================================================================

class SimpleCultureGenerator:
    """Simple culture generator focused on character creation."""
    
    @staticmethod
    def create_character_culture(cultural_reference: str, 
                               gaming_friendly: bool = True) -> CharacterCulture:
        """
        Create a simple culture for character creation.
        
        Args:
            cultural_reference: What culture to inspire (e.g., "Celtic", "Norse")
            gaming_friendly: Make it gaming table friendly
            
        Returns:
            CharacterCulture ready for character creation
        """
        try:
            # Generate basic culture info
            culture_name = SimpleCultureGenerator._generate_culture_name(cultural_reference)
            description = SimpleCultureGenerator._generate_description(culture_name)
            
            # Generate character names (most important part)
            names = SimpleCultureGenerator._generate_character_names(cultural_reference, gaming_friendly)
            
            # Generate optional character support
            traits = SimpleCultureGenerator._generate_personality_traits(cultural_reference)
            hooks = SimpleCultureGenerator._generate_background_hooks(culture_name)
            values = SimpleCultureGenerator._generate_cultural_values(cultural_reference)
            
            # Generate gaming support
            pronunciation = SimpleCultureGenerator._generate_pronunciation_notes(names, gaming_friendly)
            tips = SimpleCultureGenerator._generate_gaming_tips(culture_name)
            
            return CharacterCulture(
                name=culture_name,
                description=description,
                male_names=names.get('male', []),
                female_names=names.get('female', []),
                unisex_names=names.get('unisex', []),
                family_names=names.get('family', []),
                personality_traits=traits,
                background_hooks=hooks,
                cultural_values=values,
                pronunciation_notes=pronunciation,
                gaming_tips=tips,
                authenticity_level="gaming" if gaming_friendly else "creative",
                character_ready=True
            )
            
        except Exception as e:
            # Always return something usable for character creation
            return SimpleCultureGenerator._create_fallback_culture(cultural_reference, str(e))
    
    @staticmethod
    def enhance_for_gaming(culture: CharacterCulture) -> CharacterCulture:
        """Make culture more gaming-table friendly."""
        # Simplify names that are hard to pronounce
        simplified_names = {
            'male': SimpleCultureGenerator._simplify_names(culture.male_names),
            'female': SimpleCultureGenerator._simplify_names(culture.female_names),
            'unisex': SimpleCultureGenerator._simplify_names(culture.unisex_names),
            'family': SimpleCultureGenerator._simplify_names(culture.family_names)
        }
        
        # Add gaming tips
        enhanced_tips = list(culture.gaming_tips)
        enhanced_tips.extend([
            "Names simplified for easy pronunciation",
            "Perfect for any character class or background",
            "Cultural elements are optional character inspiration"
        ])
        
        return CharacterCulture(
            name=culture.name,
            description=culture.description + " (Gaming Enhanced)",
            male_names=simplified_names['male'],
            female_names=simplified_names['female'],
            unisex_names=simplified_names['unisex'],
            family_names=simplified_names['family'],
            personality_traits=culture.personality_traits,
            background_hooks=culture.background_hooks,
            cultural_values=culture.cultural_values,
            pronunciation_notes=culture.pronunciation_notes,
            gaming_tips=enhanced_tips,
            authenticity_level="gaming",
            character_ready=True
        )
    
    @staticmethod
    def validate_for_character_creation(culture: CharacterCulture) -> tuple[bool, List[str]]:
        """
        Simple validation - always supportive, never restrictive.
        
        Returns:
            (is_usable, helpful_suggestions)
        """
        suggestions = []
        
        # Check if we have names (most important)
        total_names = len(culture.get_all_names())
        if total_names == 0:
            suggestions.append("Consider adding some character names for players to choose from")
        elif total_names < 5:
            suggestions.append("Adding more name options would give players better variety")
        
        # Check background support
        if not culture.background_hooks:
            suggestions.append("Character background hooks help players create backstories")
        
        if not culture.personality_traits:
            suggestions.append("Personality traits can inspire character development")
        
        # Always usable - suggestions are just helpful
        if not suggestions:
            suggestions.append("Culture looks great for character creation!")
        
        return True, suggestions  # Always True - we support creativity
    
    # ============================================================================
    # SIMPLE HELPER METHODS - No Complexity
    # ============================================================================
    
    @staticmethod
    def _generate_culture_name(cultural_reference: str) -> str:
        """Generate simple culture name."""
        # Clean up the reference
        clean_ref = re.sub(r'[^a-zA-Z\s]', '', cultural_reference).strip()
        words = clean_ref.split()
        
        if len(words) >= 1:
            return f"{words[0].title()} Folk"
        return "Unique Folk"
    
    @staticmethod
    def _generate_description(culture_name: str) -> str:
        """Generate simple description."""
        return f"The {culture_name} are known for their unique traditions and make excellent character backgrounds for any adventure."
    
    @staticmethod
    def _generate_character_names(cultural_reference: str, gaming_friendly: bool) -> Dict[str, List[str]]:
        """Generate character names based on cultural reference."""
        ref_lower = cultural_reference.lower()
        
        # Simple name generation based on cultural hints
        if 'celtic' in ref_lower or 'irish' in ref_lower:
            return SimpleCultureGenerator._generate_celtic_names(gaming_friendly)
        elif 'norse' in ref_lower or 'viking' in ref_lower:
            return SimpleCultureGenerator._generate_norse_names(gaming_friendly)
        elif 'greek' in ref_lower or 'hellenic' in ref_lower:
            return SimpleCultureGenerator._generate_greek_names(gaming_friendly)
        elif 'roman' in ref_lower or 'latin' in ref_lower:
            return SimpleCultureGenerator._generate_roman_names(gaming_friendly)
        elif 'japanese' in ref_lower:
            return SimpleCultureGenerator._generate_japanese_names(gaming_friendly)
        elif 'arabic' in ref_lower or 'persian' in ref_lower:
            return SimpleCultureGenerator._generate_arabic_names(gaming_friendly)
        else:
            return SimpleCultureGenerator._generate_fantasy_names(gaming_friendly)
    
    @staticmethod
    def _generate_celtic_names(gaming_friendly: bool) -> Dict[str, List[str]]:
        """Generate Celtic-inspired names."""
        if gaming_friendly:
            return {
                'male': ['Aiden', 'Bran', 'Cian', 'Finn', 'Kael', 'Liam', 'Owen', 'Sean'],
                'female': ['Aria', 'Brenna', 'Ciara', 'Fiona', 'Maeve', 'Nora', 'Seren', 'Tara'],
                'unisex': ['Avery', 'Casey', 'Devon', 'Quinn', 'Rowan', 'Sage'],
                'family': ['MacBride', 'OConnor', 'Sullivan', 'Murphy', 'Kelly', 'Walsh']
            }
        else:
            return {
                'male': ['Aedan', 'Braichgoch', 'Cináed', 'Fionntan', 'Niall'],
                'female': ['Áine', 'Brigid', 'Deirdre', 'Gráinne', 'Siobhán'],
                'unisex': ['Aodh', 'Bláithín', 'Caoimhe'],
                'family': ['Ó Briain', 'Mac Carthaigh', 'Ó Súilleabháin']
            }
    
    @staticmethod
    def _generate_norse_names(gaming_friendly: bool) -> Dict[str, List[str]]:
        """Generate Norse-inspired names."""
        if gaming_friendly:
            return {
                'male': ['Bjorn', 'Erik', 'Gunnar', 'Hakan', 'Leif', 'Magnus', 'Olaf', 'Ragnar'],
                'female': ['Astrid', 'Brynhild', 'Freydis', 'Helga', 'Ingrid', 'Kara', 'Sigrid', 'Thora'],
                'unisex': ['Ari', 'Einar', 'Rune', 'Skye', 'Storm'],
                'family': ['Erikson', 'Bjornsson', 'Ragnarsdottir', 'Magnusson', 'Thorsson']
            }
        else:
            return {
                'male': ['Bjørn', 'Gunnarr', 'Hákon', 'Ragnarr', 'Þórr'],
                'female': ['Brynhildr', 'Guðrún', 'Sigríðr', 'Þóra'],
                'unisex': ['Einarr', 'Ragnhildr'],
                'family': ['Eriksson', 'Björnsson', 'Ragnarsdóttir']
            }
    
    @staticmethod
    def _generate_greek_names(gaming_friendly: bool) -> Dict[str, List[str]]:
        """Generate Greek-inspired names."""
        if gaming_friendly:
            return {
                'male': ['Alex', 'Damon', 'Hector', 'Jason', 'Leo', 'Nico', 'Theo', 'Zander'],
                'female': ['Aria', 'Chloe', 'Elena', 'Iris', 'Kira', 'Lyra', 'Nyx', 'Zoe'],
                'unisex': ['Ariel', 'Chris', 'Jordan', 'Phoenix', 'River'],
                'family': ['Alexios', 'Dimitrios', 'Kostas', 'Stavros', 'Yannis']
            }
        else:
            return {
                'male': ['Alexandros', 'Dionysios', 'Hektor', 'Iason', 'Leonidas'],
                'female': ['Ariadne', 'Kassandra', 'Penelope', 'Persephone'],
                'unisex': ['Artemis', 'Chrysanthos'],
                'family': ['Alexandrou', 'Dimitriou', 'Konstantinou']
            }
    
    @staticmethod
    def _generate_roman_names(gaming_friendly: bool) -> Dict[str, List[str]]:
        """Generate Roman-inspired names."""
        if gaming_friendly:
            return {
                'male': ['Adrian', 'Caesar', 'Felix', 'Julius', 'Marcus', 'Rex', 'Titus', 'Victor'],
                'female': ['Aria', 'Clara', 'Julia', 'Luna', 'Maxima', 'Nova', 'Vera', 'Victoria'],
                'unisex': ['Adrian', 'Alex', 'Sage', 'Val'],
                'family': ['Augustus', 'Cassius', 'Maximus', 'Octavius', 'Severus']
            }
        else:
            return {
                'male': ['Gaius', 'Lucius', 'Marcus', 'Quintus', 'Titus'],
                'female': ['Claudia', 'Cornelia', 'Livia', 'Octavia'],
                'unisex': ['Aurelius', 'Valentinus'],
                'family': ['Antonius', 'Claudius', 'Cornelius', 'Flavius']
            }
    
    @staticmethod
    def _generate_japanese_names(gaming_friendly: bool) -> Dict[str, List[str]]:
        """Generate Japanese-inspired names."""
        if gaming_friendly:
            return {
                'male': ['Aki', 'Hiro', 'Kai', 'Ken', 'Ren', 'Ryu', 'Tai', 'Yuki'],
                'female': ['Akira', 'Hana', 'Kira', 'Mai', 'Mika', 'Rika', 'Saki', 'Yuki'],
                'unisex': ['Akira', 'Haru', 'Nori', 'Sora', 'Yuki'],
                'family': ['Hayashi', 'Kimura', 'Nakamura', 'Sato', 'Tanaka']
            }
        else:
            return {
                'male': ['Akihiko', 'Hiroshi', 'Kazuki', 'Takeshi'],
                'female': ['Akiko', 'Hanako', 'Michiko', 'Yuriko'],
                'unisex': ['Akira', 'Haruka', 'Yukiko'],
                'family': ['Hayashi', 'Kimura', 'Nakamura', 'Watanabe']
            }
    
    @staticmethod
    def _generate_arabic_names(gaming_friendly: bool) -> Dict[str, List[str]]:
        """Generate Arabic-inspired names."""
        if gaming_friendly:
            return {
                'male': ['Ali', 'Amir', 'Farid', 'Hassan', 'Karim', 'Omar', 'Saif', 'Zain'],
                'female': ['Aria', 'Farah', 'Layla', 'Maya', 'Nia', 'Sara', 'Zara', 'Zina'],
                'unisex': ['Ariel', 'Noor', 'Rami', 'Sami'],
                'family': ['Alawi', 'Farouk', 'Hassan', 'Malik', 'Rahman']
            }
        else:
            return {
                'male': ['Abdullah', 'Ahmad', 'Hassan', 'Muhammad', 'Yusuf'],
                'female': ['Aisha', 'Fatima', 'Khadija', 'Maryam', 'Zaynab'],
                'unisex': ['Nur', 'Rahim'],
                'family': ['Al-Rashid', 'Ibn Ahmad', 'Al-Hassan']
            }
    
    @staticmethod
    def _generate_fantasy_names(gaming_friendly: bool) -> Dict[str, List[str]]:
        """Generate generic fantasy names."""
        return {
            'male': ['Aeron', 'Brix', 'Cael', 'Dain', 'Eris', 'Finn', 'Gale', 'Hawk'],
            'female': ['Aria', 'Bryn', 'Cora', 'Dawn', 'Echo', 'Faye', 'Gwen', 'Hope'],
            'unisex': ['Ash', 'Blaze', 'Sage', 'Sky', 'Storm', 'Vale', 'Wren', 'Zara'],
            'family': ['Brightblade', 'Stormwind', 'Goldleaf', 'Ironforge', 'Moonwhisper']
        }
    
    @staticmethod
    def _generate_personality_traits(cultural_reference: str) -> List[str]:
        """Generate simple personality traits."""
        ref_lower = cultural_reference.lower()
        
        base_traits = [
            "Values honor and loyalty",
            "Protective of family and friends", 
            "Curious about other cultures",
            "Skilled in traditional crafts",
            "Respects nature and ancestors"
        ]
        
        # Add culture-specific traits
        if 'celtic' in ref_lower:
            base_traits.append("Connected to nature and music")
        elif 'norse' in ref_lower:
            base_traits.append("Brave and adventurous spirit")
        elif 'greek' in ref_lower:
            base_traits.append("Appreciates philosophy and debate")
        elif 'roman' in ref_lower:
            base_traits.append("Values discipline and order")
        elif 'japanese' in ref_lower:
            base_traits.append("Emphasizes harmony and respect")
        elif 'arabic' in ref_lower:
            base_traits.append("Values hospitality and wisdom")
        
        return base_traits[:4]  # Keep it simple
    
    @staticmethod
    def _generate_background_hooks(culture_name: str) -> List[str]:
        """Generate simple background hooks."""
        return [
            f"A member of the {culture_name} seeking to prove themselves",
            f"Someone who left the {culture_name} to pursue adventure",
            f"A keeper of {culture_name} traditions in a foreign land",
            f"An outcast from {culture_name} looking for redemption",
            f"A bridge-builder between the {culture_name} and other peoples"
        ]
    
    @staticmethod
    def _generate_cultural_values(cultural_reference: str) -> List[str]:
        """Generate simple cultural values."""
        return [
            "Community over individual gain",
            "Courage in the face of adversity", 
            "Wisdom passed down through generations",
            "Respect for all living things",
            "The importance of keeping one's word"
        ]
    
    @staticmethod
    def _generate_pronunciation_notes(names: Dict[str, List[str]], gaming_friendly: bool) -> List[str]:
        """Generate pronunciation notes."""
        if gaming_friendly:
            return [
                "All names chosen for easy pronunciation at gaming tables",
                "No difficult consonant clusters or silent letters",
                "Alternative spellings available if needed"
            ]
        else:
            return [
                "Some names may require pronunciation practice",
                "Feel free to use simplified versions for gaming",
                "Focus on the character, not perfect pronunciation"
            ]
    
    @staticmethod
    def _generate_gaming_tips(culture_name: str) -> List[str]:
        """Generate gaming tips."""
        return [
            f"Use {culture_name} names for quick character creation",
            "Cultural traits can inspire character personality",
            "Background hooks provide ready-made character stories",
            "Feel free to adapt cultural elements to fit your character concept"
        ]
    
    @staticmethod
    def _simplify_names(names: List[str]) -> List[str]:
        """Simplify names for gaming use."""
        simplified = []
        for name in names:
            # Remove apostrophes and simplify difficult combinations
            simple_name = name.replace("'", "").replace("'", "")
            
            # Replace difficult consonant clusters
            simple_name = re.sub(r'sch', 'sh', simple_name)
            simple_name = re.sub(r'tch', 'ch', simple_name)
            simple_name = re.sub(r'pht', 'ft', simple_name)
            
            simplified.append(simple_name)
        
        return simplified
    
    @staticmethod
    def _create_fallback_culture(cultural_reference: str, error: str) -> CharacterCulture:
        """Create a fallback culture when generation fails."""
        return CharacterCulture(
            name="Creative Folk",
            description="A unique culture perfect for character creation",
            male_names=['Aeron', 'Brix', 'Cael', 'Dain'],
            female_names=['Aria', 'Bryn', 'Cora', 'Echo'],
            unisex_names=['Ash', 'Sage', 'Sky', 'Vale'],
            family_names=['Brightblade', 'Stormwind', 'Goldleaf'],
            personality_traits=[
                "Values creativity and freedom",
                "Adaptable to new situations",
                "Loyal to friends and family"
            ],
            background_hooks=[
                "A creative individual seeking their place in the world",
                "Someone who brings unique perspectives to any group",
                "A person with mysterious origins and untold potential"
            ],
            cultural_values=[
                "Creative expression is valued",
                "Everyone deserves respect and freedom",
                "Adventure leads to growth"
            ],
            gaming_tips=[
                f"Created as fallback for '{cultural_reference}'",
                "Perfect for any character concept",
                "Customize as needed for your character"
            ],
            authenticity_level="creative",
            character_ready=True
        )


# ============================================================================
# UTILITY FUNCTIONS - Simple and Helpful
# ============================================================================

def create_character_culture(cultural_reference: str, gaming_friendly: bool = True) -> CharacterCulture:
    """
    Create a culture for character creation.
    
    Args:
        cultural_reference: Culture to inspire (e.g., "Celtic", "Norse")
        gaming_friendly: Make it gaming table friendly
        
    Returns:
        CharacterCulture ready for character creation
    """
    return SimpleCultureGenerator.create_character_culture(cultural_reference, gaming_friendly)


def get_culture_names(culture: CharacterCulture, gender: Optional[str] = None, count: int = 5) -> List[str]:
    """
    Get names from culture for character creation.
    
    Args:
        culture: CharacterCulture to get names from
        gender: 'male', 'female', or None for all
        count: Number of names to return
        
    Returns:
        List of names for character creation
    """
    if gender == 'male':
        names = culture.male_names
    elif gender == 'female':
        names = culture.female_names
    else:
        names = culture.get_all_names()
    
    # Return up to count names
    return names[:count] if len(names) >= count else names


def get_character_inspiration(culture: CharacterCulture) -> Dict[str, List[str]]:
    """
    Get character creation inspiration from culture.
    
    Args:
        culture: CharacterCulture to get inspiration from
        
    Returns:
        Dictionary with character inspiration elements
    """
    return culture.get_character_inspiration()


def is_culture_ready(culture: CharacterCulture) -> bool:
    """
    Check if culture is ready for character creation.
    
    Args:
        culture: CharacterCulture to check
        
    Returns:
        True if ready (always True - we support creativity)
    """
    return culture.character_ready


# ============================================================================
# EXPORTS - Keep it Simple
# ============================================================================

__all__ = [
    # Core classes
    "CharacterCulture",
    "SimpleCultureGenerator",
    
    # Utility functions
    "create_character_culture",
    "get_culture_names", 
    "get_character_inspiration",
    "is_culture_ready"
]

# ============================================================================
# MODULE INFO
# ============================================================================

__version__ = "1.0.0"
__description__ = "Simple Culture Generator for D&D Character Creation - Culture Enhances, Never Restricts"