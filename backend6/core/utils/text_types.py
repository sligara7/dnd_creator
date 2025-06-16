"""
Text Processing Type Definitions for D&D Creative Content Framework.

Defines text formatting styles, content types, and text analysis categories
for enhanced text processing with cultural awareness and character generation focus.
"""

from enum import Enum, auto
from typing import Tuple


class EnhancedTextStyle(Enum):
    """Enhanced text formatting styles with cultural awareness."""
    PLAIN = "plain"
    TITLE_CASE = "title"
    UPPER_CASE = "upper"
    LOWER_CASE = "lower"
    SENTENCE_CASE = "sentence"
    CAMEL_CASE = "camel"
    SNAKE_CASE = "snake"
    KEBAB_CASE = "kebab"
    # Cultural formatting styles
    CULTURAL_TRADITIONAL = "cultural_traditional"
    CULTURAL_MODERN = "cultural_modern"
    FANTASY_ARCHAIC = "fantasy_archaic"
    GAMING_FRIENDLY = "gaming_friendly"
    
    @property
    def gaming_friendliness(self) -> float:
        """How gaming-friendly this formatting style is (0.0 to 1.0)."""
        scores = {
            self.PLAIN: 0.8,
            self.TITLE_CASE: 0.9,
            self.UPPER_CASE: 0.6,
            self.LOWER_CASE: 0.7,
            self.SENTENCE_CASE: 0.8,
            self.CAMEL_CASE: 0.4,
            self.SNAKE_CASE: 0.3,
            self.KEBAB_CASE: 0.3,
            self.CULTURAL_TRADITIONAL: 0.7,
            self.CULTURAL_MODERN: 0.8,
            self.FANTASY_ARCHAIC: 0.6,
            self.GAMING_FRIENDLY: 1.0
        }
        return scores.get(self, 0.5)


class EnhancedContentType(Enum):
    """Enhanced types of D&D content for processing with cultural context."""
    # Character-related content
    CHARACTER_NAME = "character_name"
    CHARACTER_NICKNAME = "character_nickname"
    CHARACTER_TITLE = "character_title"
    CHARACTER_EPITHET = "character_epithet"
    
    # Location content
    PLACE_NAME = "place_name"
    SETTLEMENT_NAME = "settlement_name"
    GEOGRAPHIC_FEATURE = "geographic_feature"
    
    # Item and equipment content
    ITEM_NAME = "item_name"
    WEAPON_NAME = "weapon_name"
    ARTIFACT_NAME = "artifact_name"
    
    # Magical content
    SPELL_NAME = "spell_name"
    ABILITY_NAME = "ability_name"
    RITUAL_NAME = "ritual_name"
    
    # Character background content
    PERSONALITY_TRAIT = "personality_trait"
    IDEAL = "ideal"
    BOND = "bond"
    FLAW = "flaw"
    MOTIVATION = "motivation"
    FEAR = "fear"
    
    # Narrative content
    BACKGROUND_STORY = "background_story"
    CHARACTER_HISTORY = "character_history"
    CULTURAL_BACKGROUND = "cultural_background"
    
    # Physical descriptions
    PHYSICAL_DESCRIPTION = "physical_description"
    CLOTHING_DESCRIPTION = "clothing_description"
    EQUIPMENT_DESCRIPTION = "equipment_description"
    
    # Cultural content
    CULTURAL_TRADITION = "cultural_tradition"
    CULTURAL_VALUE = "cultural_value"
    CULTURAL_CUSTOM = "cultural_custom"
    CULTURAL_CONFLICT = "cultural_conflict"
    CULTURAL_MYSTERY = "cultural_mystery"
    
    # Gaming utility content
    PRONUNCIATION_GUIDE = "pronunciation_guide"
    GAMING_NOTES = "gaming_notes"
    CHARACTER_HOOK = "character_hook"
    
    @property
    def is_character_focused(self) -> bool:
        """Whether this content type is focused on character creation."""
        character_types = {
            self.CHARACTER_NAME, self.CHARACTER_NICKNAME, self.CHARACTER_TITLE,
            self.CHARACTER_EPITHET, self.PERSONALITY_TRAIT, self.IDEAL,
            self.BOND, self.FLAW, self.MOTIVATION, self.FEAR,
            self.BACKGROUND_STORY, self.CHARACTER_HISTORY, self.CHARACTER_HOOK
        }
        return self in character_types
    
    @property
    def max_length(self) -> int:
        """Get maximum recommended length for this content type."""
        lengths = {
            self.CHARACTER_NAME: 50,
            self.CHARACTER_NICKNAME: 30,
            self.CHARACTER_TITLE: 80,
            self.CHARACTER_EPITHET: 60,
            self.PERSONALITY_TRAIT: 200,
            self.BACKGROUND_STORY: 2000,
            self.PHYSICAL_DESCRIPTION: 500,
            self.CULTURAL_TRADITION: 300,
            self.PRONUNCIATION_GUIDE: 100,
            self.GAMING_NOTES: 300,
            self.CHARACTER_HOOK: 150
        }
        return lengths.get(self, 500)
    
    @property
    def gaming_priority(self) -> str:
        """Get gaming utility priority level."""
        priorities = {
            self.CHARACTER_NAME: "critical",
            self.CHARACTER_NICKNAME: "high",
            self.PERSONALITY_TRAIT: "high",
            self.BACKGROUND_STORY: "medium",
            self.PRONUNCIATION_GUIDE: "critical",
            self.GAMING_NOTES: "high",
            self.CHARACTER_HOOK: "high"
        }
        return priorities.get(self, "medium")


class TextAnalysisCategory(Enum):
    """Categories for enhanced text analysis with gaming focus."""
    READABILITY = "readability"
    COMPLEXITY = "complexity"
    FANTASY_CONTENT = "fantasy_content"
    CULTURAL_CONTENT = "cultural_content"
    CHARACTER_POTENTIAL = "character_potential"
    GAMING_UTILITY = "gaming_utility"
    ROLEPLAY_POTENTIAL = "roleplay_potential"
    NARRATIVE_DEPTH = "narrative_depth"
    
    @property
    def analysis_weight(self) -> float:
        """Weight for this analysis category in overall scoring."""
        weights = {
            self.READABILITY: 0.15,
            self.COMPLEXITY: 0.10,
            self.FANTASY_CONTENT: 0.15,
            self.CULTURAL_CONTENT: 0.15,
            self.CHARACTER_POTENTIAL: 0.20,  # High weight for character focus
            self.GAMING_UTILITY: 0.15,
            self.ROLEPLAY_POTENTIAL: 0.10
        }
        return weights.get(self, 0.10)