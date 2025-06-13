"""
Background Concept Analysis Use Case

Central processor for analyzing character background concepts and generating
thematic content recommendations. This is the entry point for the creative
content generation pipeline.
"""

from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import re
import hashlib
import logging

from core.entities import CharacterConcept
from core.value_objects import ThematicElements
from core.enums import ContentType, Ability, Skill

logger = logging.getLogger(__name__)


@dataclass
class ConceptAnalysisRequest:
    """Request for concept analysis."""
    raw_concept: str
    character_name: Optional[str] = None
    target_level: int = 1
    preferred_content_types: Optional[List[ContentType]] = None
    analysis_depth: str = "standard"  # "basic", "standard", "deep"
    include_mechanical_suggestions: bool = True
    
    def __post_init__(self):
        """Validate request data."""
        if self.target_level < 1 or self.target_level > 20:
            raise ValueError("Target level must be between 1 and 20")
        
        if self.preferred_content_types is None:
            self.preferred_content_types = []


@dataclass
class ConceptAnalysisResponse:
    """Response from concept analysis."""
    success: bool
    processed_concept: Optional[CharacterConcept] = None
    thematic_elements: Optional[ThematicElements] = None
    recommended_content_types: List[ContentType] = field(default_factory=list)
    cultural_insights: Dict[str, Any] = field(default_factory=dict)
    mechanical_suggestions: Dict[str, Any] = field(default_factory=dict)
    generation_roadmap: Dict[str, Any] = field(default_factory=dict)
    feasibility_analysis: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    processing_metadata: Dict[str, Any] = field(default_factory=dict)


class ThemeExtractor:
    """Handles theme extraction from concept text with enhanced pattern matching."""
    
    # Comprehensive theme patterns with weighted keywords and context
    THEME_PATTERNS = {
        'arcane': {
            'keywords': ['magic', 'wizard', 'arcane', 'spell', 'mystical', 'enchantment', 'sorcery', 'incantation', 'weave', 'mana'],
            'weight': 1.0,
            'category': 'magical',
            'power_indicator': 'high'
        },
        'divine': {
            'keywords': ['god', 'divine', 'holy', 'sacred', 'temple', 'priest', 'cleric', 'deity', 'blessed', 'faith'],
            'weight': 1.0,
            'category': 'magical',
            'power_indicator': 'high'
        },
        'nature': {
            'keywords': ['forest', 'wild', 'nature', 'druid', 'ranger', 'beast', 'plant', 'grove', 'wilderness', 'primal'],
            'weight': 1.0,
            'category': 'environmental',
            'power_indicator': 'medium'
        },
        'martial': {
            'keywords': ['warrior', 'fighter', 'sword', 'battle', 'combat', 'military', 'weapon', 'armor', 'tactics', 'discipline'],
            'weight': 1.0,
            'category': 'combat',
            'power_indicator': 'medium'
        },
        'shadow': {
            'keywords': ['shadow', 'dark', 'stealth', 'rogue', 'assassin', 'hidden', 'sneak', 'infiltrate', 'espionage', 'secrets'],
            'weight': 1.0,
            'category': 'stealth',
            'power_indicator': 'medium'
        },
        'elemental': {
            'keywords': ['fire', 'water', 'earth', 'air', 'storm', 'lightning', 'ice', 'flame', 'frost', 'tempest'],
            'weight': 1.2,
            'category': 'magical',
            'power_indicator': 'high'
        },
        'celestial': {
            'keywords': ['angel', 'celestial', 'light', 'radiant', 'heaven', 'aasimar', 'divine light', 'seraph', 'holy warrior'],
            'weight': 1.3,
            'category': 'supernatural',
            'power_indicator': 'very_high'
        },
        'infernal': {
            'keywords': ['demon', 'devil', 'hell', 'fiend', 'infernal', 'tiefling', 'damned', 'cursed', 'pact', 'corruption'],
            'weight': 1.3,
            'category': 'supernatural',
            'power_indicator': 'very_high'
        },
        'scholarly': {
            'keywords': ['scholar', 'study', 'knowledge', 'book', 'library', 'research', 'academic', 'learned', 'sage', 'lore'],
            'weight': 0.9,
            'category': 'intellectual',
            'power_indicator': 'low'
        },
        'urban': {
            'keywords': ['city', 'urban', 'guild', 'merchant', 'noble', 'street', 'civilization', 'society', 'politics', 'trade'],
            'weight': 0.8,
            'category': 'social',
            'power_indicator': 'low'
        },
        'nomadic': {
            'keywords': ['nomad', 'wanderer', 'travel', 'caravan', 'desert', 'steppe', 'journey', 'roam', 'exile', 'vagrant'],
            'weight': 0.9,
            'category': 'cultural',
            'power_indicator': 'low'
        },
        'aquatic': {
            'keywords': ['sea', 'ocean', 'water', 'sailor', 'pirate', 'mer', 'triton', 'waves', 'depths', 'maritime'],
            'weight': 1.1,
            'category': 'environmental',
            'power_indicator': 'medium'
        },
        'aerial': {
            'keywords': ['sky', 'flying', 'wind', 'aarakocra', 'air', 'cloud', 'storm', 'soar', 'heights', 'wings'],
            'weight': 1.1,
            'category': 'environmental',
            'power_indicator': 'medium'
        }
    }
    
    def extract_themes(self, text: str) -> Tuple[List[str], List[str], Dict[str, float]]:
        """
        Extract themes from text with enhanced analysis.
        
        Returns:
            Tuple of (primary_themes, theme_keywords, theme_scores)
        """
        text_lower = text.lower()
        theme_scores = {}
        all_keywords = []
        
        for theme, data in self.THEME_PATTERNS.items():
            keywords = data['keywords']
            weight = data['weight']
            score = 0
            found_keywords = []
            
            for keyword in keywords:
                if keyword in text_lower:
                    # Count occurrences with context weighting
                    count = text_lower.count(keyword)
                    context_bonus = self._calculate_context_bonus(text_lower, keyword)
                    weighted_score = count * weight * (1 + context_bonus)
                    score += weighted_score
                    found_keywords.extend([keyword] * count)
            
            if score > 0:
                theme_scores[theme] = score
                all_keywords.extend(found_keywords)
        
        # Sort themes by score and select primary themes
        sorted_themes = sorted(theme_scores.items(), key=lambda x: x[1], reverse=True)
        primary_themes = [theme for theme, score in sorted_themes if score >= 1.0]
        
        return primary_themes, list(set(all_keywords)), dict(sorted_themes)
    
    def _calculate_context_bonus(self, text: str, keyword: str) -> float:
        """Calculate bonus based on keyword context."""
        bonus = 0.0
        
        # Check for intensifying words near the keyword
        intensifiers = ['powerful', 'ancient', 'legendary', 'master', 'great', 'mighty']
        for intensifier in intensifiers:
            if intensifier in text and abs(text.find(intensifier) - text.find(keyword)) < 50:
                bonus += 0.2
        
        # Check for descriptive context
        if len(text.split(keyword)) > 2:  # Multiple mentions
            bonus += 0.1
        
        return min(bonus, 0.5)  # Cap bonus at 0.5


class CulturalAnalyzer:
    """Enhanced cultural element analysis with deeper pattern recognition."""
    
    CULTURAL_PATTERNS = {
        'noble': {
            'indicators': ['noble', 'aristocrat', 'lord', 'lady', 'court', 'palace', 'heir', 'dynasty', 'royal', 'highborn'],
            'backgrounds': ['Noble', 'Guild Artisan'],
            'skills': ['Persuasion', 'History', 'Insight'],
            'naming': ['aristocratic', 'formal', 'titled'],
            'power_level_modifier': 0.1,
            'complexity': 'medium'
        },
        'commoner': {
            'indicators': ['peasant', 'farmer', 'commoner', 'village', 'rural', 'humble', 'simple', 'working', 'laborer'],
            'backgrounds': ['Folk Hero', 'Hermit'],
            'skills': ['Animal Handling', 'Survival', 'Athletics'],
            'naming': ['simple', 'regional', 'occupational'],
            'power_level_modifier': -0.1,
            'complexity': 'low'
        },
        'outlaw': {
            'indicators': ['outlaw', 'bandit', 'criminal', 'thief', 'fugitive', 'wanted', 'exile', 'rogue', 'scoundrel'],
            'backgrounds': ['Criminal', 'Outlander', 'Charlatan'],
            'skills': ['Deception', 'Stealth', 'Sleight of Hand'],
            'naming': ['aliases', 'coded', 'street'],
            'power_level_modifier': 0.0,
            'complexity': 'medium'
        },
        'military': {
            'indicators': ['soldier', 'guard', 'army', 'military', 'veteran', 'commander', 'officer', 'knight', 'mercenary'],
            'backgrounds': ['Soldier', 'Folk Hero'],
            'skills': ['Athletics', 'Intimidation', 'Survival'],
            'naming': ['rank-based', 'honor-based'],
            'power_level_modifier': 0.2,
            'complexity': 'medium'
        },
        'religious': {
            'indicators': ['monk', 'priest', 'acolyte', 'temple', 'monastery', 'faithful', 'devoted', 'pilgrim', 'crusader'],
            'backgrounds': ['Acolyte', 'Hermit'],
            'skills': ['Religion', 'Insight', 'Medicine'],
            'naming': ['virtue-based', 'divine-inspired'],
            'power_level_modifier': 0.1,
            'complexity': 'high'
        },
        'academic': {
            'indicators': ['scholar', 'sage', 'professor', 'university', 'academy', 'researcher', 'student', 'philosopher'],
            'backgrounds': ['Sage', 'Cloistered Scholar'],
            'skills': ['History', 'Arcana', 'Investigation'],
            'naming': ['scholarly', 'classical'],
            'power_level_modifier': 0.0,
            'complexity': 'high'
        },
        'artisan': {
            'indicators': ['craftsman', 'smith', 'artisan', 'guild', 'workshop', 'maker', 'builder', 'engineer'],
            'backgrounds': ['Guild Artisan', 'Folk Hero'],
            'skills': ['Sleight of Hand', 'Investigation', 'Athletics'],
            'naming': ['craft-related', 'guild-traditional'],
            'power_level_modifier': 0.0,
            'complexity': 'medium'
        },
        'entertainer': {
            'indicators': ['bard', 'musician', 'performer', 'actor', 'dancer', 'storyteller', 'artist', 'minstrel'],
            'backgrounds': ['Entertainer', 'Guild Artisan'],
            'skills': ['Performance', 'Persuasion', 'Deception'],
            'naming': ['stage names', 'artistic'],
            'power_level_modifier': 0.0,
            'complexity': 'medium'
        }
    }
    
    def analyze_cultural_elements(self, text: str) -> Dict[str, Any]:
        """Enhanced cultural analysis with complexity assessment."""
        text_lower = text.lower()
        detected_cultures = []
        culture_scores = {}
        cultural_complexity = 0
        
        for culture, data in self.CULTURAL_PATTERNS.items():
            score = 0
            matches = []
            
            for indicator in data['indicators']:
                if indicator in text_lower:
                    count = text_lower.count(indicator)
                    score += count
                    matches.append(indicator)
            
            if score > 0:
                detected_cultures.append(culture)
                culture_scores[culture] = score
                
                # Add to complexity based on cultural sophistication
                complexity_map = {'low': 1, 'medium': 2, 'high': 3}
                cultural_complexity += complexity_map.get(data['complexity'], 1)
        
        return {
            'elements': detected_cultures,
            'scores': culture_scores,
            'dominant': max(culture_scores.items(), key=lambda x: x[1])[0] if culture_scores else None,
            'complexity_score': cultural_complexity,
            'multi_cultural': len(detected_cultures) > 1
        }


class PowerLevelCalculator:
    """Enhanced power level calculation with multiple factors."""
    
    POWER_KEYWORDS = {
        'legendary': 2.5,
        'ancient': 2.2,
        'master': 1.8,
        'powerful': 1.5,
        'experienced': 1.3,
        'skilled': 1.2,
        'trained': 1.1,
        'apprentice': 0.9,
        'novice': 0.8,
        'young': 0.7,
        'beginning': 0.6
    }
    
    CONTEXT_MODIFIERS = {
        'chosen': 1.3,
        'blessed': 1.2,
        'cursed': 1.2,
        'prophesied': 1.4,
        'heir': 1.1,
        'exile': 0.9,
        'student': 0.8,
        'champion': 1.3
    }
    
    def calculate_power_level(self, raw_concept: str, themes: List[str], 
                            theme_scores: Dict[str, float]) -> float:
        """Calculate estimated power level with enhanced analysis."""
        base_power = 1.0
        concept_lower = raw_concept.lower()
        
        # Apply primary keyword modifiers
        power_multiplier = self._get_power_keyword_multiplier(concept_lower)
        base_power *= power_multiplier
        
        # Apply context modifiers
        context_multiplier = self._get_context_multiplier(concept_lower)
        base_power *= context_multiplier
        
        # Theme complexity modifier
        theme_complexity = self._calculate_theme_complexity(themes, theme_scores)
        base_power *= theme_complexity
        
        # Length and detail modifier (more detailed concepts tend to be more powerful)
        detail_modifier = self._calculate_detail_modifier(raw_concept)
        base_power *= detail_modifier
        
        # Cap and validate the power level
        return self._validate_power_level(base_power)
    
    def _get_power_keyword_multiplier(self, text: str) -> float:
        """Get multiplier from power-indicating keywords."""
        for keyword, multiplier in self.POWER_KEYWORDS.items():
            if keyword in text:
                return multiplier
        return 1.0
    
    def _get_context_multiplier(self, text: str) -> float:
        """Get multiplier from contextual keywords."""
        multiplier = 1.0
        for keyword, mod in self.CONTEXT_MODIFIERS.items():
            if keyword in text:
                multiplier *= mod
                break  # Only apply first found context
        return multiplier
    
    def _calculate_theme_complexity(self, themes: List[str], theme_scores: Dict[str, float]) -> float:
        """Calculate complexity modifier based on themes."""
        theme_count = len(themes)
        
        if theme_count == 0:
            return 0.8
        elif theme_count == 1:
            return 1.0
        elif theme_count == 2:
            return 1.1
        elif theme_count == 3:
            return 1.2
        else:
            return 1.3  # Multiple themes indicate complexity
    
    def _calculate_detail_modifier(self, concept: str) -> float:
        """Calculate modifier based on concept detail level."""
        word_count = len(concept.split())
        
        if word_count < 10:
            return 0.9  # Too brief
        elif word_count < 30:
            return 1.0  # Standard
        elif word_count < 100:
            return 1.1  # Detailed
        else:
            return 1.2  # Very detailed
    
    def _validate_power_level(self, power_level: float) -> float:
        """Validate and cap power level."""
        return max(0.3, min(power_level, 3.0))


class MechanicalSuggestionEngine:
    """Enhanced mechanical suggestion engine with deeper analysis."""
    
    def __init__(self):
        self.ability_mappings = self._initialize_ability_mappings()
        self.skill_mappings = self._initialize_skill_mappings()
        self.equipment_mappings = self._initialize_equipment_mappings()
        self.class_mappings = self._initialize_class_mappings()
    
    def _initialize_ability_mappings(self) -> Dict[str, List[str]]:
        """Initialize theme to ability mappings with priorities."""
        return {
            'arcane': ['Intelligence', 'Wisdom'],
            'divine': ['Wisdom', 'Charisma'],
            'martial': ['Strength', 'Constitution'],
            'nature': ['Wisdom', 'Constitution'],
            'shadow': ['Dexterity', 'Intelligence'],
            'scholarly': ['Intelligence', 'Wisdom'],
            'elemental': ['Constitution', 'Charisma'],
            'celestial': ['Charisma', 'Wisdom'],
            'infernal': ['Charisma', 'Constitution'],
            'urban': ['Charisma', 'Intelligence'],
            'nomadic': ['Constitution', 'Wisdom'],
            'aquatic': ['Constitution', 'Strength'],
            'aerial': ['Dexterity', 'Constitution']
        }
    
    def _initialize_skill_mappings(self) -> Dict[str, List[str]]:
        """Initialize theme to skill mappings."""
        return {
            'arcane': ['Arcana', 'Investigation', 'History'],
            'divine': ['Religion', 'Insight', 'Medicine'],
            'martial': ['Athletics', 'Intimidation', 'Survival'],
            'nature': ['Nature', 'Survival', 'Animal Handling'],
            'shadow': ['Stealth', 'Sleight of Hand', 'Deception'],
            'scholarly': ['History', 'Investigation', 'Arcana'],
            'elemental': ['Arcana', 'Nature', 'Survival'],
            'celestial': ['Religion', 'Medicine', 'Insight'],
            'infernal': ['Deception', 'Intimidation', 'Arcana'],
            'urban': ['Persuasion', 'Deception', 'Insight'],
            'nomadic': ['Survival', 'Animal Handling', 'Nature'],
            'aquatic': ['Athletics', 'Survival', 'Nature'],
            'aerial': ['Acrobatics', 'Perception', 'Survival']
        }
    
    def _initialize_equipment_mappings(self) -> Dict[str, List[str]]:
        """Initialize theme to equipment mappings."""
        return {
            'arcane': ['staff', 'robes', 'spellbook', 'component_pouch', 'crystal_focus'],
            'divine': ['holy_symbol', 'mace', 'chain_mail', 'shield', 'prayer_book'],
            'martial': ['sword', 'armor', 'shield', 'weapon_variety', 'military_pack'],
            'nature': ['bow', 'leather_armor', 'survival_gear', 'herbalism_kit', 'druidcraft_focus'],
            'shadow': ['dagger', 'dark_clothing', 'thieves_tools', 'poison', 'disguise_kit'],
            'scholarly': ['books', 'writing_materials', 'magnifying_glass', 'ink', 'scholar_pack'],
            'elemental': ['elemental_focus', 'protective_gear', 'specialized_tools', 'wand']
        }
    
    def _initialize_class_mappings(self) -> Dict[str, List[str]]:
        """Initialize theme to class mappings."""
        return {
            'arcane': ['Wizard', 'Sorcerer', 'Artificer'],
            'divine': ['Cleric', 'Paladin', 'Divine Soul Sorcerer'],
            'martial': ['Fighter', 'Barbarian', 'Paladin'],
            'nature': ['Druid', 'Ranger', 'Circle of Stars Druid'],
            'shadow': ['Rogue', 'Warlock', 'Shadow Monk'],
            'scholarly': ['Wizard', 'Artificer', 'Knowledge Cleric']
        }
    
    def generate_suggestions(self, themes: List[str], cultures: List[str], 
                           target_level: int, power_level: float) -> Dict[str, Any]:
        """Generate comprehensive mechanical suggestions with power level consideration."""
        suggestions = {
            'ability_priorities': self._suggest_abilities(themes),
            'recommended_skills': self._suggest_skills(themes, cultures),
            'equipment_themes': self._suggest_equipment(themes),
            'spell_schools': self._suggest_spell_schools(themes),
            'feat_categories': self._suggest_feat_categories(themes),
            'class_recommendations': self._suggest_classes(themes, power_level),
            'multiclass_options': self._suggest_multiclass(themes),
            'level_progression': self._suggest_progression(themes, target_level),
            'power_scaling': self._suggest_power_scaling(power_level, target_level)
        }
        
        return suggestions
    
    def _suggest_classes(self, themes: List[str], power_level: float) -> List[Dict[str, Any]]:
        """Suggest classes with fit scores."""
        class_suggestions = []
        
        for theme in themes:
            if theme in self.class_mappings:
                for class_name in self.class_mappings[theme]:
                    fit_score = self._calculate_class_fit(class_name, themes, power_level)
                    class_suggestions.append({
                        'class': class_name,
                        'theme_source': theme,
                        'fit_score': fit_score,
                        'power_compatibility': self._assess_power_compatibility(class_name, power_level)
                    })
        
        # Sort by fit score
        return sorted(class_suggestions, key=lambda x: x['fit_score'], reverse=True)
    
    def _calculate_class_fit(self, class_name: str, themes: List[str], power_level: float) -> float:
        """Calculate how well a class fits the themes and power level."""
        base_fit = 0.5
        
        # Theme alignment bonus
        theme_bonus = 0.0
        for theme in themes:
            if theme in self.class_mappings and class_name in self.class_mappings[theme]:
                theme_bonus += 0.3
        
        # Power level compatibility
        power_bonus = self._get_class_power_bonus(class_name, power_level)
        
        return min(base_fit + theme_bonus + power_bonus, 1.0)
    
    def _get_class_power_bonus(self, class_name: str, power_level: float) -> float:
        """Get power level compatibility bonus for class."""
        high_power_classes = ['Wizard', 'Sorcerer', 'Warlock', 'Cleric']
        medium_power_classes = ['Fighter', 'Ranger', 'Paladin', 'Artificer']
        
        if power_level > 2.0 and class_name in high_power_classes:
            return 0.2
        elif 1.5 <= power_level <= 2.0 and class_name in medium_power_classes:
            return 0.2
        elif power_level < 1.5 and class_name not in high_power_classes:
            return 0.1
        
        return 0.0
    
    def _assess_power_compatibility(self, class_name: str, power_level: float) -> str:
        """Assess power compatibility rating."""
        if power_level > 2.5:
            return "requires_careful_balancing"
        elif power_level > 2.0:
            return "high_power_suitable"
        elif power_level > 1.5:
            return "well_matched"
        else:
            return "standard_power"
    
    def _suggest_power_scaling(self, power_level: float, target_level: int) -> Dict[str, Any]:
        """Suggest power scaling approach."""
        return {
            'scaling_approach': self._determine_scaling_approach(power_level),
            'milestone_levels': self._suggest_milestone_levels(target_level),
            'power_gates': self._suggest_power_gates(power_level),
            'balance_considerations': self._get_balance_considerations(power_level)
        }
    
    def _determine_scaling_approach(self, power_level: float) -> str:
        """Determine appropriate scaling approach."""
        if power_level > 2.5:
            return "gradual_unlock"
        elif power_level > 2.0:
            return "milestone_based"
        elif power_level > 1.5:
            return "standard_progression"
        else:
            return "accelerated_growth"
    
    def _suggest_milestone_levels(self, target_level: int) -> List[int]:
        """Suggest key milestone levels."""
        milestones = [1, 3, 5, 11, 17]
        return [level for level in milestones if level <= target_level]
    
    def _suggest_power_gates(self, power_level: float) -> List[str]:
        """Suggest power gating mechanisms."""
        if power_level > 2.0:
            return ["narrative_triggers", "item_dependency", "mentor_approval"]
        else:
            return ["level_requirements", "story_progression"]
    
    def _get_balance_considerations(self, power_level: float) -> List[str]:
        """Get balance considerations for the power level."""
        considerations = ["maintain_party_balance", "respect_action_economy"]
        
        if power_level > 2.0:
            considerations.extend([
                "limit_at_will_abilities",
                "add_meaningful_costs",
                "provide_counterplay_options"
            ])
        
        return considerations
    
    # ... (继续使用原有的其他方法，但简化实现)
    
    def _suggest_abilities(self, themes: List[str]) -> List[str]:
        """Suggest ability score priorities."""
        priorities = []
        for theme in themes:
            if theme in self.ability_mappings:
                priorities.extend(self.ability_mappings[theme])
        return list(dict.fromkeys(priorities))
    
    def _suggest_skills(self, themes: List[str], cultures: List[str]) -> List[str]:
        """Suggest skills based on themes and culture."""
        skills = []
        
        for theme in themes:
            if theme in self.skill_mappings:
                skills.extend(self.skill_mappings[theme])
        
        return list(set(skills))
    
    def _suggest_equipment(self, themes: List[str]) -> List[str]:
        """Suggest equipment themes."""
        equipment = []
        for theme in themes:
            if theme in self.equipment_mappings:
                equipment.extend(self.equipment_mappings[theme])
        return list(set(equipment))
    
    def _suggest_spell_schools(self, themes: List[str]) -> List[str]:
        """Suggest spell schools based on themes."""
        school_map = {
            'arcane': ['Evocation', 'Transmutation'],
            'divine': ['Abjuration', 'Divination'],
            'nature': ['Transmutation', 'Conjuration'],
            'shadow': ['Illusion', 'Necromancy'],
            'elemental': ['Evocation', 'Transmutation'],
            'celestial': ['Abjuration', 'Evocation'],
            'infernal': ['Necromancy', 'Enchantment']
        }
        
        schools = []
        for theme in themes:
            if theme in school_map:
                schools.extend(school_map[theme])
        return list(set(schools))
    
    def _suggest_feat_categories(self, themes: List[str]) -> List[str]:
        """Suggest feat categories."""
        feat_map = {
            'arcane': ['Magic', 'Ritual'],
            'divine': ['Divine', 'Healing'],
            'martial': ['Fighting', 'Weapon'],
            'nature': ['Nature', 'Survival'],
            'shadow': ['Stealth', 'Skill'],
            'scholarly': ['Skill', 'Knowledge']
        }
        
        categories = []
        for theme in themes:
            if theme in feat_map:
                categories.extend(feat_map[theme])
        return list(set(categories))
    
    def _suggest_multiclass(self, themes: List[str]) -> List[str]:
        """Suggest multiclass options."""
        classes = []
        for theme in themes:
            if theme in self.class_mappings:
                classes.extend(self.class_mappings[theme])
        return list(set(classes))
    
    def _suggest_progression(self, themes: List[str], target_level: int) -> Dict[str, Any]:
        """Suggest level progression considerations."""
        return {
            'early_focus': themes[:2] if len(themes) >= 2 else themes,
            'mid_level_expansion': themes[2:4] if len(themes) > 2 else [],
            'high_level_mastery': themes[:1] if themes else [],
            'multiclass_timing': max(3, target_level // 2) if len(themes) > 2 else None
        }


class ConceptProcessorUseCase:
    """
    Enhanced concept processor with comprehensive analysis capabilities.
    
    Combines multiple analysis engines to provide deep insight into character
    concepts and generate detailed recommendations for content creation.
    """
    
    def __init__(self):
        self.theme_extractor = ThemeExtractor()
        self.cultural_analyzer = CulturalAnalyzer()
        self.power_calculator = PowerLevelCalculator()
        self.mechanical_engine = MechanicalSuggestionEngine()
    
    async def execute(self, request: ConceptAnalysisRequest) -> ConceptAnalysisResponse:
        """
        Process and analyze a character background concept with comprehensive analysis.
        
        Args:
            request: Concept analysis request
            
        Returns:
            Detailed concept analysis response
        """
        start_time = datetime.now()
        response = ConceptAnalysisResponse(success=False, errors=[], warnings=[])
        
        try:
            logger.info(f"Starting concept analysis for: {request.character_name or 'Unnamed'}")
            
            # Step 1: Validate input
            validation_errors = self._validate_request(request)
            if validation_errors:
                response.errors.extend(validation_errors)
                return response
            
            # Step 2: Extract thematic elements
            thematic_elements = self._extract_thematic_elements(request.raw_concept)
            
            # Step 3: Analyze cultural elements
            cultural_analysis = self.cultural_analyzer.analyze_cultural_elements(request.raw_concept)
            cultural_insights = self._build_cultural_insights(cultural_analysis, thematic_elements)
            
            # Step 4: Generate mechanical suggestions
            mechanical_suggestions = {}
            if request.include_mechanical_suggestions:
                mechanical_suggestions = self.mechanical_engine.generate_suggestions(
                    thematic_elements.primary_themes,
                    cultural_analysis['elements'],
                    request.target_level,
                    thematic_elements.power_level
                )
            
            # Step 5: Create generation roadmap
            generation_roadmap = self._create_generation_roadmap(
                thematic_elements, cultural_analysis, request.target_level
            )
            
            # Step 6: Assess feasibility
            feasibility_analysis = self._assess_feasibility(
                thematic_elements, cultural_analysis, request.target_level
            )
            
            # Step 7: Recommend content types
            recommended_content_types = self._recommend_content_types(
                thematic_elements, 
                request.preferred_content_types
            )
            
            # Step 8: Create processed concept
            processed_concept = self._create_character_concept(
                request, thematic_elements, recommended_content_types
            )
            
            # Build successful response
            response.success = True
            response.processed_concept = processed_concept
            response.thematic_elements = thematic_elements
            response.recommended_content_types = recommended_content_types
            response.cultural_insights = cultural_insights
            response.mechanical_suggestions = mechanical_suggestions
            response.generation_roadmap = generation_roadmap
            response.feasibility_analysis = feasibility_analysis
            response.processing_metadata = {
                'processing_time': (datetime.now() - start_time).total_seconds(),
                'analysis_depth': request.analysis_depth,
                'theme_count': len(thematic_elements.primary_themes),
                'cultural_complexity': cultural_analysis.get('complexity_score', 0),
                'power_level': thematic_elements.power_level,
                'concept_hash': hashlib.md5(request.raw_concept.encode()).hexdigest()[:8]
            }
            
            # Add warnings for edge cases
            self._add_warnings(response, thematic_elements, cultural_analysis)
            
            logger.info(f"Concept analysis completed successfully for: {processed_concept.concept_name}")
            
        except Exception as e:
            logger.error(f"Concept processing failed: {e}", exc_info=True)
            response.errors.append(f"Concept processing failed: {str(e)}")
        
        return response
    
    def _validate_request(self, request: ConceptAnalysisRequest) -> List[str]:
        """Validate the analysis request with enhanced checks."""
        errors = []
        
        if not request.raw_concept or len(request.raw_concept.strip()) < 10:
            errors.append("Concept must be at least 10 characters long")
        
        if len(request.raw_concept) > 5000:
            errors.append("Concept too long (maximum 5000 characters)")
        
        if request.target_level < 1 or request.target_level > 20:
            errors.append("Target level must be between 1 and 20")
        
        if request.analysis_depth not in ['basic', 'standard', 'deep']:
            errors.append("Analysis depth must be 'basic', 'standard', or 'deep'")
        
        return errors
    
    def _extract_thematic_elements(self, raw_concept: str) -> ThematicElements:
        """Extract comprehensive thematic elements from raw concept text."""
        primary_themes, theme_keywords, theme_scores = self.theme_extractor.extract_themes(raw_concept)
        
        # Extract cultural elements
        cultural_analysis = self.cultural_analyzer.analyze_cultural_elements(raw_concept)
        cultural_elements = cultural_analysis['elements']
        
        # Calculate power level
        power_level = self.power_calculator.calculate_power_level(
            raw_concept, primary_themes, theme_scores
        )
        
        return ThematicElements(
            primary_themes=primary_themes,
            theme_keywords=theme_keywords,
            cultural_elements=cultural_elements,
            power_level=power_level
        )
    
    def _build_cultural_insights(self, cultural_analysis: Dict[str, Any], 
                               themes: ThematicElements) -> Dict[str, Any]:
        """Build comprehensive cultural insights."""
        return {
            'dominant_culture': cultural_analysis['dominant'] or 'generic',
            'cultural_complexity': cultural_analysis.get('complexity_score', 0),
            'multi_cultural': cultural_analysis.get('multi_cultural', False),
            'theme_cultural_alignment': self._assess_alignment(themes),
            'suggested_backgrounds': self._get_background_suggestions(cultural_analysis['elements']),
            'naming_conventions': self._get_naming_suggestions(cultural_analysis['elements']),
            'language_suggestions': self._get_language_suggestions(themes.primary_themes),
            'cultural_scores': cultural_analysis['scores'],
            'integration_opportunities': self._identify_integration_opportunities(
                themes.primary_themes, cultural_analysis['elements']
            )
        }
    
    def _create_generation_roadmap(self, themes: ThematicElements, 
                                 cultural_analysis: Dict[str, Any],
                                 target_level: int) -> Dict[str, Any]:
        """Create comprehensive generation roadmap."""
        return {
            'generation_priority': self._determine_generation_priority(themes),
            'content_dependencies': self._map_content_dependencies(themes),
            'theme_integration_strategy': self._plan_theme_integration(themes),
            'cultural_integration_points': self._identify_cultural_integration_points(cultural_analysis),
            'power_scaling_plan': self._create_power_scaling_plan(themes.power_level, target_level),
            'balance_checkpoints': self._define_balance_checkpoints(themes),
            'creative_constraints': self._define_creative_constraints(themes, cultural_analysis)
        }
    
    def _assess_feasibility(self, themes: ThematicElements,
                          cultural_analysis: Dict[str, Any],
                          target_level: int) -> Dict[str, Any]:
        """Assess concept feasibility within D&D framework."""
        return {
            'overall_feasibility': self._calculate_overall_feasibility(themes),
            'rule_compliance_score': self._assess_rule_compliance(themes),
            'balance_feasibility': self._assess_balance_feasibility(themes.power_level),
            'implementation_complexity': self._assess_implementation_complexity(themes, cultural_analysis),
            'required_customizations': self._identify_required_customizations(themes),
            'potential_conflicts': self._identify_potential_conflicts(themes),
            'mitigation_strategies': self._suggest_mitigation_strategies(themes)
        }
    
    # Helper methods for roadmap and feasibility assessment
    def _determine_generation_priority(self, themes: ThematicElements) -> List[str]:
        """Determine content generation priority order."""
        priorities = ['species', 'class', 'equipment', 'spells', 'feats']
        
        # Adjust based on theme strength
        if 'celestial' in themes.primary_themes or 'infernal' in themes.primary_themes:
            priorities = ['species', 'class', 'spells', 'equipment', 'feats']
        elif any(theme in ['arcane', 'divine'] for theme in themes.primary_themes):
            priorities = ['class', 'spells', 'species', 'equipment', 'feats']
        elif 'martial' in themes.primary_themes:
            priorities = ['class', 'equipment', 'species', 'feats', 'spells']
        
        return priorities
    
    def _map_content_dependencies(self, themes: ThematicElements) -> Dict[str, List[str]]:
        """Map dependencies between content types."""
        dependencies = {
            'class_features': ['species_traits'],
            'equipment': ['class_proficiencies', 'cultural_context'],
            'spells': ['class_spellcasting', 'theme_schools'],
            'feats': ['species_abilities', 'class_features']
        }
        
        # Add theme-specific dependencies
        if 'elemental' in themes.primary_themes:
            dependencies['equipment'].append('elemental_affinity')
            dependencies['spells'].append('elemental_theme')
        
        return dependencies
    
    def _calculate_overall_feasibility(self, themes: ThematicElements) -> float:
        """Calculate overall concept feasibility score."""
        base_feasibility = 0.8
        
        # Reduce feasibility for very high power concepts
        if themes.power_level > 2.5:
            base_feasibility -= 0.3
        elif themes.power_level > 2.0:
            base_feasibility -= 0.1
        
        # Reduce feasibility for too many themes
        if len(themes.primary_themes) > 4:
            base_feasibility -= 0.2
        
        # Increase feasibility for well-balanced concepts
        if 1.2 <= themes.power_level <= 1.8 and 2 <= len(themes.primary_themes) <= 3:
            base_feasibility += 0.1
        
        return max(0.0, min(base_feasibility, 1.0))
    
    # ... (其他辅助方法的实现)
    
    def _assess_alignment(self, themes: ThematicElements) -> str:
        """Assess theme-culture alignment."""
        if not themes.cultural_elements or not themes.primary_themes:
            return "neutral"
        
        ratio = len(themes.cultural_elements) / len(themes.primary_themes)
        if 0.8 <= ratio <= 1.2:
            return "well_aligned"
        elif ratio > 1.2:
            return "culture_heavy"
        else:
            return "theme_heavy"
    
    def _get_background_suggestions(self, cultural_elements: List[str]) -> List[str]:
        """Get D&D background suggestions."""
        suggestions = []
        for culture in cultural_elements:
            if culture in self.cultural_analyzer.CULTURAL_PATTERNS:
                suggestions.extend(self.cultural_analyzer.CULTURAL_PATTERNS[culture]['backgrounds'])
        return list(set(suggestions))
    
    def _get_naming_suggestions(self, cultural_elements: List[str]) -> List[str]:
        """Get naming convention suggestions."""
        suggestions = []
        for culture in cultural_elements:
            if culture in self.cultural_analyzer.CULTURAL_PATTERNS:
                suggestions.extend(self.cultural_analyzer.CULTURAL_PATTERNS[culture]['naming'])
        return list(set(suggestions)) or ['generic']
    
    def _get_language_suggestions(self, themes: List[str]) -> List[str]:
        """Get language suggestions based on themes."""
        language_map = {
            'arcane': ['Draconic'],
            'divine': ['Celestial'],
            'nature': ['Sylvan', 'Druidic'],
            'infernal': ['Infernal'],
            'celestial': ['Celestial'],
            'elemental': ['Primordial'],
            'shadow': ['Undercommon'],
            'scholarly': ['multiple languages']
        }
        
        suggestions = []
        for theme in themes:
            if theme in language_map:
                suggestions.extend(language_map[theme])
        
        return list(set(suggestions)) or ['Common']
    
    def _identify_integration_opportunities(self, themes: List[str], 
                                         cultural_elements: List[str]) -> List[str]:
        """Identify opportunities for theme-culture integration."""
        opportunities = []
        
        if 'scholarly' in themes and 'academic' in cultural_elements:
            opportunities.append('magical_research_tradition')
        
        if 'divine' in themes and 'religious' in cultural_elements:
            opportunities.append('unique_religious_practices')
        
        if 'martial' in themes and 'military' in cultural_elements:
            opportunities.append('specialized_combat_techniques')
        
        return opportunities
    
    def _recommend_content_types(self, themes: ThematicElements, 
                               preferred: Optional[List[ContentType]]) -> List[ContentType]:
        """Recommend content types based on enhanced analysis."""
        recommendations = []
        
        # Species recommendations
        unique_heritage_themes = {'celestial', 'infernal', 'elemental', 'aquatic', 'aerial'}
        if (len(themes.primary_themes) > 2 or 
            any(theme in unique_heritage_themes for theme in themes.primary_themes)):
            recommendations.append(ContentType.SPECIES)
        
        # Class recommendations
        if len(themes.primary_themes) >= 2:
            recommendations.append(ContentType.CHARACTER_CLASS)
        
        # Equipment recommendations
        equipment_themes = {'martial', 'artisan', 'elemental', 'shadow'}
        if any(theme in equipment_themes for theme in themes.primary_themes):
            recommendations.append(ContentType.EQUIPMENT)
        
        # Spell recommendations
        magical_themes = {'arcane', 'divine', 'elemental', 'celestial', 'nature'}
        if any(theme in magical_themes for theme in themes.primary_themes):
            recommendations.append(ContentType.SPELL)
        
        # Feat recommendations (always include for specialized characters)
        if themes.primary_themes:
            recommendations.append(ContentType.FEAT)
        
        # Filter by preferences if specified
        if preferred:
            recommendations = [ct for ct in recommendations if ct in preferred]
        
        return recommendations
    
    def _create_character_concept(self, request: ConceptAnalysisRequest, 
                                themes: ThematicElements, 
                                content_types: List[ContentType]) -> CharacterConcept:
        """Create the processed character concept."""
        concept_hash = hashlib.md5(request.raw_concept.encode()).hexdigest()[:8]
        
        return CharacterConcept(
            concept_id=f"concept_{concept_hash}",
            concept_name=request.character_name or self._generate_concept_name(themes),
            background_story=request.raw_concept,
            thematic_elements=themes,
            target_level=request.target_level,
            recommended_content_types=content_types,
            processing_metadata={
                'analysis_timestamp': datetime.now(),
                'analysis_depth': request.analysis_depth,
                'theme_extraction_version': '2.0'
            }
        )
    
    def _generate_concept_name(self, themes: ThematicElements) -> str:
        """Generate a concept name based on themes."""
        if not themes.primary_themes:
            return "Generic Adventurer"
        
        primary = themes.primary_themes[0].title()
        if len(themes.primary_themes) > 1:
            secondary = themes.primary_themes[1].title()
            return f"{primary} {secondary} Practitioner"
        else:
            return f"{primary} Adept"
    
    def _add_warnings(self, response: ConceptAnalysisResponse, 
                     themes: ThematicElements, cultural_analysis: Dict[str, Any]):
        """Add comprehensive warnings for potential issues."""
        if not themes.primary_themes:
            response.warnings.append("No clear themes detected - concept may be too generic")
        
        if len(themes.primary_themes) > 4:
            response.warnings.append("Many themes detected - concept may be too complex for balanced implementation")
        
        if not cultural_analysis['elements']:
            response.warnings.append("No cultural background detected - consider adding cultural context")
        
        if themes.power_level > 2.5:
            response.warnings.append("Very high power level detected - will require careful balancing")
        
        if themes.power_level < 0.7:
            response.warnings.append("Low power level detected - may need enhancement to be engaging")
        
        if cultural_analysis.get('multi_cultural', False):
            response.warnings.append("Multiple cultural elements detected - ensure coherent integration")
        
        # Theme-specific warnings
        conflicting_themes = [
            (['celestial', 'infernal'], "Celestial and infernal themes may conflict"),
            (['nature', 'urban'], "Nature and urban themes may be difficult to integrate"),
            (['shadow', 'divine'], "Shadow and divine themes require careful balance")
        ]
        
        for theme_pair, warning in conflicting_themes:
            if all(theme in themes.primary_themes for theme in theme_pair):
                response.warnings.append(warning)