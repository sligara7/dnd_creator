from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from ..enums.content_types import ContentType, ContentSource
from ..enums.dnd_constants import Ability
from ..value_objects.thematic_elements import ThematicElements


@dataclass
class CharacterConcept:
    """
    Entity representing a background-driven character concept for content generation.
    
    This is the heart of the Creative Content Framework - it captures the player's
    vision for their character and drives the generation of thematically consistent
    content including species, classes, equipment, spells, and feats.
    
    The concept follows Clean Architecture principles by being a pure domain entity
    that contains rich data about the character's identity, background, and goals.
    """
    
    # === CORE IDENTITY ===
    concept_name: str = ""
    player_vision: str = ""  # Player's description of their character concept
    background_story: str = ""
    
    # === THEMATIC ELEMENTS ===
    primary_themes: List[str] = field(default_factory=list)  # ["nature", "protection", "mystery"]
    secondary_themes: List[str] = field(default_factory=list)  # ["scholar", "wanderer"]
    cultural_background: str = ""  # Cultural/societal origin
    personality_traits: List[str] = field(default_factory=list)
    ideals: List[str] = field(default_factory=list)
    bonds: List[str] = field(default_factory=list)
    flaws: List[str] = field(default_factory=list)
    
    # === MECHANICAL PREFERENCES ===
    preferred_role: str = ""  # "striker", "defender", "controller", "support", "utility"
    combat_style: str = ""  # "melee", "ranged", "spellcaster", "hybrid"
    complexity_preference: str = "moderate"  # "simple", "moderate", "complex"
    power_level: str = "standard"  # "low", "standard", "high"
    
    # === ABILITY PREFERENCES ===
    primary_abilities: List[Ability] = field(default_factory=list)
    secondary_abilities: List[Ability] = field(default_factory=list)
    dump_stats: List[Ability] = field(default_factory=list)  # Abilities player doesn't prioritize
    
    # === CONTENT GENERATION HINTS ===
    species_preferences: Dict[str, Any] = field(default_factory=dict)
    class_preferences: Dict[str, Any] = field(default_factory=dict)
    equipment_preferences: Dict[str, Any] = field(default_factory=dict)
    spell_preferences: Dict[str, Any] = field(default_factory=dict)
    feat_preferences: Dict[str, Any] = field(default_factory=dict)
    
    # === CAMPAIGN CONTEXT ===
    campaign_setting: str = ""  # Campaign world/setting
    starting_level: int = 1
    campaign_themes: List[str] = field(default_factory=list)  # Campaign-specific themes
    party_role: str = ""  # Role within the adventuring party
    
    # === GENERATION CONSTRAINTS ===
    allowed_sources: List[ContentSource] = field(default_factory=lambda: [ContentSource.CORE_RULES, ContentSource.GENERATED])
    forbidden_elements: List[str] = field(default_factory=list)  # Things to avoid
    required_elements: List[str] = field(default_factory=list)  # Things that must be included
    
    # === METADATA ===
    created_at: datetime = field(default_factory=datetime.now)
    last_modified: datetime = field(default_factory=datetime.now)
    created_by: str = ""  # Player or DM name
    version: str = "1.0"
    
    # === COMPUTED PROPERTIES ===
    
    @property
    def all_themes(self) -> List[str]:
        """Get all themes combined."""
        return self.primary_themes + self.secondary_themes + self.campaign_themes
    
    @property
    def thematic_elements(self) -> ThematicElements:
        """Get structured thematic elements for content generation."""
        return ThematicElements(
            primary_themes=self.primary_themes,
            secondary_themes=self.secondary_themes,
            cultural_elements=self._extract_cultural_keywords(),
            personality_keywords=self._extract_personality_keywords(),
            mechanical_preferences=self._get_mechanical_preferences()
        )
    
    @property
    def generation_priority(self) -> Dict[ContentType, int]:
        """Get priority order for content generation."""
        # Default priority: species first, then class, then supporting content
        return {
            ContentType.SPECIES: 1,
            ContentType.CHARACTER_CLASS: 2,
            ContentType.BACKGROUND: 3,
            ContentType.EQUIPMENT: 4,
            ContentType.FEAT: 5,
            ContentType.SPELL: 6
        }
    
    # === ANALYSIS METHODS ===
    
    def get_theme_keywords(self) -> List[str]:
        """Extract keywords from all thematic elements."""
        keywords = []
        
        # Extract from themes
        keywords.extend(self.all_themes)
        
        # Extract from background story
        background_words = self.background_story.lower().split()
        important_words = [
            word for word in background_words 
            if len(word) > 4 and word not in ["from", "with", "that", "their", "would", "have", "been"]
        ]
        keywords.extend(important_words[:10])  # Limit to prevent noise
        
        # Extract from personality traits
        for trait in self.personality_traits:
            trait_words = trait.lower().split()
            keywords.extend([word for word in trait_words if len(word) > 3])
        
        return list(set(keywords))  # Remove duplicates
    
    def get_cultural_elements(self) -> List[str]:
        """Extract cultural elements for content generation."""
        cultural_keywords = []
        
        if self.cultural_background:
            cultural_keywords.extend(self.cultural_background.lower().split())
        
        if self.campaign_setting:
            cultural_keywords.extend(self.campaign_setting.lower().split())
        
        return [word for word in cultural_keywords if len(word) > 3]
    
    def get_mechanical_constraints(self) -> Dict[str, Any]:
        """Get mechanical constraints for content generation."""
        return {
            "power_level": self.power_level,
            "complexity": self.complexity_preference,
            "primary_abilities": [ability.value for ability in self.primary_abilities],
            "combat_style": self.combat_style,
            "preferred_role": self.preferred_role,
            "starting_level": self.starting_level
        }
    
    def analyze_content_needs(self) -> Dict[ContentType, Dict[str, Any]]:
        """Analyze what content needs to be generated based on the concept."""
        needs = {}
        
        # Species needs
        if not self.species_preferences.get("specific_species"):
            needs[ContentType.SPECIES] = {
                "generate": True,
                "themes": self.primary_themes,
                "cultural_background": self.cultural_background,
                "ability_preferences": self.primary_abilities
            }
        
        # Class needs
        if not self.class_preferences.get("specific_class"):
            needs[ContentType.CHARACTER_CLASS] = {
                "generate": True,
                "role": self.preferred_role,
                "combat_style": self.combat_style,
                "themes": self.primary_themes,
                "complexity": self.complexity_preference
            }
        
        # Equipment needs
        needs[ContentType.EQUIPMENT] = {
            "generate": True,
            "combat_style": self.combat_style,
            "themes": self.all_themes,
            "cultural_elements": self.get_cultural_elements()
        }
        
        # Spell needs (if spellcaster)
        if self.combat_style in ["spellcaster", "hybrid"]:
            needs[ContentType.SPELL] = {
                "generate": True,
                "themes": self.primary_themes,
                "spell_preferences": self.spell_preferences
            }
        
        # Feat needs
        needs[ContentType.FEAT] = {
            "generate": True,
            "role": self.preferred_role,
            "themes": self.secondary_themes,
            "ability_focus": self.primary_abilities
        }
        
        return needs
    
    def validate_concept_completeness(self) -> List[str]:
        """Validate that concept has enough information for generation."""
        issues = []
        
        if not self.concept_name:
            issues.append("Concept needs a name")
        
        if not self.primary_themes:
            issues.append("At least one primary theme is required")
        
        if not self.preferred_role:
            issues.append("Preferred role should be specified")
        
        if not self.primary_abilities:
            issues.append("At least one primary ability preference is needed")
        
        if len(self.background_story) < 50:
            issues.append("Background story should be more detailed for better generation")
        
        return issues
    
    def get_generation_context(self) -> Dict[str, Any]:
        """Get context information for content generators."""
        return {
            "concept_name": self.concept_name,
            "themes": self.all_themes,
            "cultural_background": self.cultural_background,
            "mechanical_preferences": self.get_mechanical_constraints(),
            "personality": {
                "traits": self.personality_traits,
                "ideals": self.ideals,
                "bonds": self.bonds,
                "flaws": self.flaws
            },
            "campaign_context": {
                "setting": self.campaign_setting,
                "themes": self.campaign_themes,
                "starting_level": self.starting_level
            },
            "constraints": {
                "allowed_sources": [source.value for source in self.allowed_sources],
                "forbidden_elements": self.forbidden_elements,
                "required_elements": self.required_elements
            }
        }
    
    # === MUTATION METHODS ===
    
    def add_theme(self, theme: str, is_primary: bool = False) -> None:
        """Add a theme to the concept."""
        if is_primary and theme not in self.primary_themes:
            self.primary_themes.append(theme)
        elif not is_primary and theme not in self.secondary_themes:
            self.secondary_themes.append(theme)
        self.last_modified = datetime.now()
    
    def update_preferences(self, content_type: ContentType, preferences: Dict[str, Any]) -> None:
        """Update preferences for a specific content type."""
        if content_type == ContentType.SPECIES:
            self.species_preferences.update(preferences)
        elif content_type == ContentType.CHARACTER_CLASS:
            self.class_preferences.update(preferences)
        elif content_type == ContentType.EQUIPMENT:
            self.equipment_preferences.update(preferences)
        elif content_type == ContentType.SPELL:
            self.spell_preferences.update(preferences)
        elif content_type == ContentType.FEAT:
            self.feat_preferences.update(preferences)
        
        self.last_modified = datetime.now()
    
    def set_campaign_context(self, setting: str, themes: List[str], starting_level: int = 1) -> None:
        """Set campaign context information."""
        self.campaign_setting = setting
        self.campaign_themes = themes
        self.starting_level = starting_level
        self.last_modified = datetime.now()
    
    # === UTILITY METHODS ===
    
    def _extract_cultural_keywords(self) -> List[str]:
        """Extract cultural keywords from background."""
        keywords = []
        if self.cultural_background:
            keywords.extend(self.cultural_background.lower().split())
        return [word for word in keywords if len(word) > 3]
    
    def _extract_personality_keywords(self) -> List[str]:
        """Extract personality keywords from traits."""
        keywords = []
        for trait in self.personality_traits + self.ideals:
            words = trait.lower().split()
            keywords.extend([word for word in words if len(word) > 3])
        return list(set(keywords))
    
    def _get_mechanical_preferences(self) -> Dict[str, Any]:
        """Get structured mechanical preferences."""
        return {
            "role": self.preferred_role,
            "combat_style": self.combat_style,
            "complexity": self.complexity_preference,
            "power_level": self.power_level,
            "primary_abilities": [ability.value for ability in self.primary_abilities]
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert concept to dictionary representation."""
        return {
            "concept_name": self.concept_name,
            "player_vision": self.player_vision,
            "background_story": self.background_story,
            "primary_themes": self.primary_themes,
            "secondary_themes": self.secondary_themes,
            "cultural_background": self.cultural_background,
            "personality_traits": self.personality_traits,
            "ideals": self.ideals,
            "bonds": self.bonds,
            "flaws": self.flaws,
            "preferred_role": self.preferred_role,
            "combat_style": self.combat_style,
            "complexity_preference": self.complexity_preference,
            "power_level": self.power_level,
            "primary_abilities": [ability.value for ability in self.primary_abilities],
            "secondary_abilities": [ability.value for ability in self.secondary_abilities],
            "dump_stats": [ability.value for ability in self.dump_stats],
            "campaign_setting": self.campaign_setting,
            "starting_level": self.starting_level,
            "campaign_themes": self.campaign_themes,
            "party_role": self.party_role,
            "allowed_sources": [source.value for source in self.allowed_sources],
            "forbidden_elements": self.forbidden_elements,
            "required_elements": self.required_elements,
            "created_at": self.created_at.isoformat(),
            "last_modified": self.last_modified.isoformat(),
            "created_by": self.created_by,
            "version": self.version
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CharacterConcept':
        """Create concept from dictionary data."""
        concept = cls()
        concept.concept_name = data.get("concept_name", "")
        concept.player_vision = data.get("player_vision", "")
        concept.background_story = data.get("background_story", "")
        concept.primary_themes = data.get("primary_themes", [])
        concept.secondary_themes = data.get("secondary_themes", [])
        concept.cultural_background = data.get("cultural_background", "")
        concept.personality_traits = data.get("personality_traits", [])
        concept.ideals = data.get("ideals", [])
        concept.bonds = data.get("bonds", [])
        concept.flaws = data.get("flaws", [])
        concept.preferred_role = data.get("preferred_role", "")
        concept.combat_style = data.get("combat_style", "")
        concept.complexity_preference = data.get("complexity_preference", "moderate")
        concept.power_level = data.get("power_level", "standard")
        
        # Convert ability strings back to Ability enums
        concept.primary_abilities = [
            Ability(ability) for ability in data.get("primary_abilities", [])
        ]
        concept.secondary_abilities = [
            Ability(ability) for ability in data.get("secondary_abilities", [])
        ]
        concept.dump_stats = [
            Ability(ability) for ability in data.get("dump_stats", [])
        ]
        
        concept.campaign_setting = data.get("campaign_setting", "")
        concept.starting_level = data.get("starting_level", 1)
        concept.campaign_themes = data.get("campaign_themes", [])
        concept.party_role = data.get("party_role", "")
        
        # Convert source strings back to ContentSource enums
        concept.allowed_sources = [
            ContentSource(source) for source in data.get("allowed_sources", ["core_rules", "generated"])
        ]
        concept.forbidden_elements = data.get("forbidden_elements", [])
        concept.required_elements = data.get("required_elements", [])
        
        if "created_at" in data:
            concept.created_at = datetime.fromisoformat(data["created_at"])
        if "last_modified" in data:
            concept.last_modified = datetime.fromisoformat(data["last_modified"])
        
        concept.created_by = data.get("created_by", "")
        concept.version = data.get("version", "1.0")
        
        return concept
    
    def __str__(self) -> str:
        """String representation of concept."""
        themes_str = ", ".join(self.primary_themes[:3])  # Show first 3 themes
        return f"Character Concept: {self.concept_name} ({themes_str})"
    
    def __repr__(self) -> str:
        """Developer representation of concept."""
        return f"CharacterConcept(name='{self.concept_name}', themes={len(self.all_themes)}, role='{self.preferred_role}')"