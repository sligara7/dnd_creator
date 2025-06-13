"""
Content Generation Constants

Constants specific to the content generation process.
These define the parameters and constraints for creating D&D content.
"""

# Power level ranges for generated content
POWER_LEVEL_RANGES = {
    "very_low": {"min": 0.1, "max": 0.4, "description": "Utility or flavor content"},
    "low": {"min": 0.4, "max": 0.7, "description": "Standard low-level content"},
    "medium": {"min": 0.7, "max": 1.3, "description": "Balanced content"},
    "high": {"min": 1.3, "max": 2.0, "description": "Powerful but controlled"},
    "very_high": {"min": 2.0, "max": 3.0, "description": "Requires careful balance"}
}

# Thematic categories for content
THEME_CATEGORIES = {
    "magical": ["arcane", "divine", "elemental", "celestial", "infernal"],
    "martial": ["warrior", "tactical", "weapon_master", "guardian"],
    "natural": ["nature", "primal", "beast", "wilderness"],
    "social": ["urban", "noble", "merchant", "entertainer"],
    "mysterious": ["shadow", "occult", "forbidden", "ancient"],
    "technological": ["artificer", "mechanical", "alchemical"]
}

# Cultural archetypes
CULTURAL_ARCHETYPES = {
    "noble": {
        "traits": ["refined", "educated", "privileged"],
        "naming": "formal_titles",
        "backgrounds": ["Noble", "Guild Artisan"]
    },
    "commoner": {
        "traits": ["practical", "hardworking", "humble"],
        "naming": "occupational",
        "backgrounds": ["Folk Hero", "Hermit"]
    },
    "military": {
        "traits": ["disciplined", "loyal", "tactical"],
        "naming": "rank_based",
        "backgrounds": ["Soldier"]
    },
    "scholarly": {
        "traits": ["learned", "curious", "methodical"],
        "naming": "academic",
        "backgrounds": ["Sage", "Cloistered Scholar"]
    },
    "outlaw": {
        "traits": ["independent", "cunning", "rebellious"],
        "naming": "aliases",
        "backgrounds": ["Criminal", "Outlander"]
    }
}

# Naming convention patterns
NAMING_CONVENTIONS = {
    "fantasy_standard": {
        "patterns": ["consonant_vowel", "compound_words", "descriptive"],
        "syllable_range": (2, 4)
    },
    "cultural_specific": {
        "patterns": ["cultural_roots", "historical_reference"],
        "syllable_range": (1, 5)
    },
    "thematic": {
        "patterns": ["theme_descriptive", "power_indicative"],
        "syllable_range": (2, 3)
    }
}

# Content rarity levels
RARITY_LEVELS = [
    "Common", "Uncommon", "Rare", "Very Rare", "Legendary", "Artifact"
]

# Generation complexity levels
GENERATION_COMPLEXITY_LEVELS = {
    "simple": {"features": 1, "interactions": 0, "dependencies": 0},
    "moderate": {"features": 2, "interactions": 1, "dependencies": 1},
    "complex": {"features": 3, "interactions": 2, "dependencies": 2},
    "advanced": {"features": 4, "interactions": 3, "dependencies": 3}
}