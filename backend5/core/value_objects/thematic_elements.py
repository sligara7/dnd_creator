from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum


class ThemeCategory(Enum):
    """Categories for organizing themes."""
    CULTURAL = "cultural"
    PERSONALITY = "personality"
    AESTHETIC = "aesthetic"
    MECHANICAL = "mechanical"
    NARRATIVE = "narrative"
    SETTING = "setting"


@dataclass(frozen=True)
class ThematicElements:
    """
    Value object representing thematic elements that drive content generation.
    
    This supports the Creative Content Framework's background-driven approach
    by organizing and weighting thematic concepts.
    """
    
    # === PRIMARY THEMES ===
    primary_themes: List[str] = field(default_factory=list)
    secondary_themes: List[str] = field(default_factory=list)
    
    # === CATEGORIZED THEMES ===
    themes_by_category: Dict[ThemeCategory, List[str]] = field(default_factory=dict)
    
    # === CULTURAL ELEMENTS ===
    cultural_background: str = ""
    traditions: List[str] = field(default_factory=list)
    values: List[str] = field(default_factory=list)
    taboos: List[str] = field(default_factory=list)
    
    # === AESTHETIC ELEMENTS ===
    visual_themes: List[str] = field(default_factory=list)
    color_palette: List[str] = field(default_factory=list)
    material_preferences: List[str] = field(default_factory=list)
    style_descriptors: List[str] = field(default_factory=list)
    
    # === NARRATIVE ELEMENTS ===
    story_archetypes: List[str] = field(default_factory=list)
    conflict_types: List[str] = field(default_factory=list)
    motivations: List[str] = field(default_factory=list)
    
    # === MECHANICAL THEMES ===
    preferred_mechanics: List[str] = field(default_factory=list)
    avoided_mechanics: List[str] = field(default_factory=list)
    complexity_preference: str = "moderate"
    
    # === WEIGHTING ===
    theme_weights: Dict[str, float] = field(default_factory=dict)  # Theme importance (0.0 to 1.0)
    
    def __post_init__(self):
        """Initialize theme categorization on creation."""
        # Ensure all theme categories exist
        for category in ThemeCategory:
            if category not in self.themes_by_category:
                object.__setattr__(self, 'themes_by_category', 
                                 {**self.themes_by_category, category: []})
    
    @property
    def all_themes(self) -> List[str]:
        """Get all themes combined."""
        themes = self.primary_themes + self.secondary_themes
        for theme_list in self.themes_by_category.values():
            themes.extend(theme_list)
        return list(set(themes))  # Remove duplicates
    
    @property
    def weighted_themes(self) -> Dict[str, float]:
        """Get themes with their weights, defaulting unweighted themes to 0.5."""
        weights = {}
        for theme in self.all_themes:
            if theme in self.theme_weights:
                weights[theme] = self.theme_weights[theme]
            elif theme in self.primary_themes:
                weights[theme] = 1.0  # Primary themes get max weight
            elif theme in self.secondary_themes:
                weights[theme] = 0.7  # Secondary themes get high weight
            else:
                weights[theme] = 0.5  # Default weight
        return weights
    
    @property
    def dominant_themes(self) -> List[str]:
        """Get themes with highest weights."""
        weighted = self.weighted_themes
        sorted_themes = sorted(weighted.items(), key=lambda x: x[1], reverse=True)
        return [theme for theme, weight in sorted_themes[:5]]  # Top 5 themes
    
    def get_theme_weight(self, theme: str) -> float:
        """Get weight for a specific theme."""
        return self.weighted_themes.get(theme, 0.0)
    
    def get_themes_by_category(self, category: ThemeCategory) -> List[str]:
        """Get themes in a specific category."""
        return self.themes_by_category.get(category, [])
    
    def has_theme(self, theme: str, min_weight: float = 0.0) -> bool:
        """Check if a theme is present with minimum weight."""
        theme_weight = self.get_theme_weight(theme)
        return theme_weight >= min_weight
    
    def get_cultural_keywords(self) -> List[str]:
        """Extract cultural keywords for content generation."""
        keywords = []
        
        # From cultural background
        if self.cultural_background:
            keywords.extend(self.cultural_background.lower().split())
        
        # From traditions and values
        keywords.extend([t.lower() for t in self.traditions])
        keywords.extend([v.lower() for v in self.values])
        
        # From cultural themes
        cultural_themes = self.get_themes_by_category(ThemeCategory.CULTURAL)
        keywords.extend([t.lower() for t in cultural_themes])
        
        # Filter out common words and short words
        stop_words = {"the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        filtered = [word for word in keywords if len(word) > 3 and word not in stop_words]
        
        return list(set(filtered))  # Remove duplicates
    
    def get_aesthetic_guide(self) -> Dict[str, List[str]]:
        """Get aesthetic guidance for content generation."""
        return {
            "visual_themes": self.visual_themes,
            "colors": self.color_palette,
            "materials": self.material_preferences,
            "style": self.style_descriptors,
            "aesthetic_themes": self.get_themes_by_category(ThemeCategory.AESTHETIC)
        }
    
    def get_narrative_hooks(self) -> Dict[str, List[str]]:
        """Get narrative elements for story-driven content."""
        return {
            "archetypes": self.story_archetypes,
            "conflicts": self.conflict_types,
            "motivations": self.motivations,
            "narrative_themes": self.get_themes_by_category(ThemeCategory.NARRATIVE)
        }
    
    def calculate_theme_compatibility(self, other_themes: List[str]) -> float:
        """Calculate compatibility with another set of themes (0.0 to 1.0)."""
        if not other_themes:
            return 0.5  # Neutral compatibility
        
        our_themes = set(theme.lower() for theme in self.all_themes)
        their_themes = set(theme.lower() for theme in other_themes)
        
        # Calculate Jaccard similarity
        intersection = our_themes & their_themes
        union = our_themes | their_themes
        
        if not union:
            return 0.5  # Neutral if no themes
        
        base_compatibility = len(intersection) / len(union)
        
        # Weight by theme importance
        weighted_matches = sum(
            self.get_theme_weight(theme) 
            for theme in intersection
        )
        max_possible_weight = sum(self.weighted_themes.values())
        
        if max_possible_weight > 0:
            weight_factor = weighted_matches / max_possible_weight
            return (base_compatibility + weight_factor) / 2
        
        return base_compatibility
    
    def get_content_generation_context(self) -> Dict[str, Any]:
        """Get structured context for content generation."""
        return {
            "dominant_themes": self.dominant_themes,
            "cultural_context": {
                "background": self.cultural_background,
                "traditions": self.traditions,
                "values": self.values,
                "taboos": self.taboos,
                "keywords": self.get_cultural_keywords()
            },
            "aesthetic_guide": self.get_aesthetic_guide(),
            "narrative_elements": self.get_narrative_hooks(),
            "mechanical_preferences": {
                "preferred": self.preferred_mechanics,
                "avoided": self.avoided_mechanics,
                "complexity": self.complexity_preference
            },
            "theme_weights": self.weighted_themes,
            "categories": {
                category.value: themes 
                for category, themes in self.themes_by_category.items()
                if themes
            }
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "primary_themes": self.primary_themes,
            "secondary_themes": self.secondary_themes,
            "themes_by_category": {
                category.value: themes 
                for category, themes in self.themes_by_category.items()
            },
            "cultural_background": self.cultural_background,
            "traditions": self.traditions,
            "values": self.values,
            "taboos": self.taboos,
            "visual_themes": self.visual_themes,
            "color_palette": self.color_palette,
            "material_preferences": self.material_preferences,
            "style_descriptors": self.style_descriptors,
            "story_archetypes": self.story_archetypes,
            "conflict_types": self.conflict_types,
            "motivations": self.motivations,
            "preferred_mechanics": self.preferred_mechanics,
            "avoided_mechanics": self.avoided_mechanics,
            "complexity_preference": self.complexity_preference,
            "theme_weights": self.theme_weights
        }
    
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

class ThemeCategory(Enum):
    """Categories for organizing themes."""
    MAGICAL = "magical"
    MARTIAL = "martial"
    CULTURAL = "cultural" 
    ENVIRONMENTAL = "environmental"
    SUPERNATURAL = "supernatural"

@dataclass(frozen=True)
class ThematicElements:
    """Immutable thematic elements for content generation."""
    primary_themes: List[str]
    theme_keywords: List[str]
    cultural_elements: List[str]
    power_level: float = 1.0
    theme_categories: List[ThemeCategory] = None
    
    def __post_init__(self):
        if self.theme_categories is None:
            object.__setattr__(self, 'theme_categories', self._categorize_themes())
    
    def _categorize_themes(self) -> List[ThemeCategory]:
        """Categorize themes automatically."""
        categories = []
        magical_themes = {'arcane', 'divine', 'elemental', 'celestial', 'infernal'}
        martial_themes = {'martial', 'military', 'warrior'}
        cultural_themes = {'noble', 'urban', 'nomadic', 'scholarly'}
        environmental_themes = {'nature', 'aquatic', 'aerial'}
        supernatural_themes = {'shadow', 'celestial', 'infernal'}
        
        for theme in self.primary_themes:
            if theme in magical_themes:
                categories.append(ThemeCategory.MAGICAL)
            elif theme in martial_themes:
                categories.append(ThemeCategory.MARTIAL)
            elif theme in cultural_themes:
                categories.append(ThemeCategory.CULTURAL)
            elif theme in environmental_themes:
                categories.append(ThemeCategory.ENVIRONMENTAL)
            elif theme in supernatural_themes:
                categories.append(ThemeCategory.SUPERNATURAL)
        
        return list(set(categories))
    
    def get_dominant_category(self) -> Optional[ThemeCategory]:
        """Get the most prominent theme category."""
        return self.theme_categories[0] if self.theme_categories else None