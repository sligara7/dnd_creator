"""
Culture Validation System - Creative Quality Assurance for Character Generation.

Validates generated cultures for creative quality, gaming usability, and character
background support. Focuses on enhancing creative freedom rather than limiting it.
Follows Clean Architecture principles with pure functions and immutable data.

This module provides:
- Creative quality assessment (not rigid authenticity checking)
- Gaming usability optimization
- Character background support validation
- Name generation quality assurance
- Pure functional validation with constructive feedback
- Creative freedom preservation with helpful suggestions
"""

from typing import Dict, List, Optional, Set, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import re
from collections import Counter

# Import core types (inward dependencies only)
from ...enums.culture_types import (
    CultureValidationCategory,
    CultureValidationSeverity,
    CultureAuthenticityLevel,
    CultureNamingStructure,
    CultureGenderSystem,
    CultureLinguisticFamily,
    CultureSourceType
)
from ...exceptions.culture import (
    CultureValidationError,
    CultureStructureError
)


class ValidationIssueType(Enum):
    """Types of validation issues focused on creative support."""
    CREATIVE_OPPORTUNITY = "creative_opportunity"
    GAMING_ENHANCEMENT = "gaming_enhancement"
    CHARACTER_BACKGROUND_GAP = "character_background_gap"
    NAME_GENERATION_ISSUE = "name_generation_issue"
    USABILITY_IMPROVEMENT = "usability_improvement"
    CREATIVE_CONSISTENCY = "creative_consistency"
    PLAYER_EXPERIENCE = "player_experience"
    BACKGROUND_DEPTH = "background_depth"
    CREATIVE_POTENTIAL = "creative_potential"
    GENERATION_QUALITY = "generation_quality"


class CreativeValidationFocus(Enum):
    """Focus areas for creative validation."""
    CHARACTER_BACKGROUNDS = "character_backgrounds"
    NAME_GENERATION = "name_generation"
    GAMING_EXPERIENCE = "gaming_experience"
    CREATIVE_FREEDOM = "creative_freedom"
    PLAYER_USABILITY = "player_usability"
    STORY_POTENTIAL = "story_potential"


@dataclass(frozen=True)
class CreativeValidationIssue:
    """
    Immutable validation issue focused on creative enhancement.
    
    Represents opportunities for improvement rather than rigid problems.
    """
    issue_type: ValidationIssueType
    severity: CultureValidationSeverity
    category: CultureValidationCategory
    message: str
    context: str = ""
    affected_items: List[str] = field(default_factory=list)
    creative_suggestions: List[str] = field(default_factory=list)
    character_impact: str = ""  # How this affects character generation
    
    def __post_init__(self):
        """Validate issue structure on creation."""
        if not self.message:
            raise CultureValidationError("Validation issue message cannot be empty")


@dataclass(frozen=True)
class CreativeValidationResult:
    """
    Immutable validation result focused on creative support.
    
    Contains quality assessment and creative enhancement suggestions
    rather than pass/fail determinations.
    """
    is_usable: bool  # Changed from is_valid - cultures are almost always usable
    creative_quality_score: float      # 0.0 to 1.0 - how good for creative use
    gaming_usability_score: float      # 0.0 to 1.0 - how good for gaming
    character_support_score: float     # 0.0 to 1.0 - how well supports character backgrounds
    name_generation_score: float       # 0.0 to 1.0 - quality of name generation
    
    creative_opportunities: List[CreativeValidationIssue] = field(default_factory=list)
    suggestions: List[CreativeValidationIssue] = field(default_factory=list)
    enhancements: List[str] = field(default_factory=list)
    
    # Analysis focused on creative support
    name_analysis: Dict[str, Any] = field(default_factory=dict)
    character_background_analysis: Dict[str, Any] = field(default_factory=dict)
    gaming_analysis: Dict[str, Any] = field(default_factory=dict)
    creative_potential_analysis: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    validation_timestamp: Optional[str] = None
    validator_version: str = "1.0.0"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate result structure on creation."""
        scores = [self.creative_quality_score, self.gaming_usability_score, 
                 self.character_support_score, self.name_generation_score]
        for score in scores:
            if not (0.0 <= score <= 1.0):
                raise CultureValidationError("All scores must be between 0.0 and 1.0")


class CreativeCultureValidator:
    """
    Creative culture validation system focused on enabling character generation.
    
    Provides static methods for assessing culture quality for creative character
    generation rather than enforcing rigid authenticity requirements.
    
    All methods are pure functions that enhance creativity rather than limit it.
    """
    
    # ============================================================================
    # MAIN CREATIVE VALIDATION METHODS (Pure Functions)
    # ============================================================================
    
    @staticmethod
    def validate_for_character_generation(culture_data: Dict[str, Any]) -> CreativeValidationResult:
        """
        Validate culture for character generation support.
        
        Pure function that assesses how well a culture supports character
        background generation and creative storytelling.
        
        Args:
            culture_data: Dictionary containing culture information
            
        Returns:
            CreativeValidationResult with character generation analysis
            
        Example:
            >>> culture_data = {
            ...     'name': 'Skyborne Merchants',
            ...     'male_names': ['Zephyr', 'Gale', 'Storm'],
            ...     'female_names': ['Aria', 'Breeze', 'Tempest'],
            ...     'cultural_traits': {'focus': 'aerial trade', 'values': 'freedom'}
            ... }
            >>> result = CreativeCultureValidator.validate_for_character_generation(culture_data)
            >>> print(f"Character support: {result.character_support_score:.2f}")
        """
        if not culture_data or not isinstance(culture_data, dict):
            raise CultureValidationError("Culture data must be a non-empty dictionary")
        
        try:
            # Focus on character generation support
            name_assessment = CreativeCultureValidator.assess_name_generation_quality(culture_data)
            background_assessment = CreativeCultureValidator.assess_character_background_support(culture_data)
            gaming_assessment = CreativeCultureValidator.assess_gaming_usability(culture_data)
            creative_assessment = CreativeCultureValidator.assess_creative_potential(culture_data)
            
            # Collect all creative opportunities and suggestions
            all_opportunities = []
            all_suggestions = []
            all_enhancements = []
            
            assessments = [name_assessment, background_assessment, gaming_assessment, creative_assessment]
            
            for assessment in assessments:
                all_opportunities.extend(assessment.creative_opportunities)
                all_suggestions.extend(assessment.suggestions)
                all_enhancements.extend(assessment.enhancements)
            
            # Calculate overall scores
            creative_quality = creative_assessment.creative_quality_score
            gaming_usability = gaming_assessment.gaming_usability_score
            character_support = background_assessment.character_support_score
            name_generation = name_assessment.name_generation_score
            
            # Determine if culture is usable (almost always yes unless completely empty)
            is_usable = CreativeCultureValidator._has_minimum_content(culture_data)
            
            return CreativeValidationResult(
                is_usable=is_usable,
                creative_quality_score=creative_quality,
                gaming_usability_score=gaming_usability,
                character_support_score=character_support,
                name_generation_score=name_generation,
                creative_opportunities=all_opportunities,
                suggestions=all_suggestions,
                enhancements=list(set(all_enhancements)),  # Deduplicate
                name_analysis=name_assessment.name_analysis,
                character_background_analysis=background_assessment.character_background_analysis,
                gaming_analysis=gaming_assessment.gaming_analysis,
                creative_potential_analysis=creative_assessment.creative_potential_analysis,
                metadata={
                    'validation_focus': 'character_generation',
                    'total_names': CreativeCultureValidator._count_total_names(culture_data),
                    'creative_elements': CreativeCultureValidator._count_creative_elements(culture_data)
                }
            )
            
        except Exception as e:
            if isinstance(e, CultureValidationError):
                raise
            raise CultureValidationError(f"Creative validation failed: {str(e)}") from e
    
    @staticmethod
    def assess_name_generation_quality(culture_data: Dict[str, Any]) -> CreativeValidationResult:
        """
        Assess quality of names for character generation.
        
        Pure function that evaluates name diversity, creativity, and
        character generation potential rather than authenticity.
        
        Args:
            culture_data: Dictionary containing name lists
            
        Returns:
            CreativeValidationResult focused on name generation quality
        """
        opportunities = []
        suggestions = []
        enhancements = []
        
        name_analysis = {
            'total_names': 0,
            'name_diversity': 0.0,
            'creative_uniqueness': 0.0,
            'character_fit_potential': 0.0,
            'pronunciation_accessibility': 0.0,
            'memorable_factor': 0.0,
            'categories_available': []
        }
        
        try:
            # Analyze name categories
            name_categories = ['male_names', 'female_names', 'neutral_names', 
                              'family_names', 'titles', 'epithets']
            
            all_names = []
            available_categories = []
            
            for category in name_categories:
                if category in culture_data and isinstance(culture_data[category], list):
                    names = culture_data[category]
                    if names:
                        available_categories.append(category)
                        all_names.extend(names)
            
            name_analysis['total_names'] = len(all_names)
            name_analysis['categories_available'] = available_categories
            
            if all_names:
                # Assess creative qualities
                name_analysis['name_diversity'] = CreativeCultureValidator._assess_name_diversity(all_names)
                name_analysis['creative_uniqueness'] = CreativeCultureValidator._assess_creative_uniqueness(all_names)
                name_analysis['character_fit_potential'] = CreativeCultureValidator._assess_character_fit_potential(all_names)
                name_analysis['pronunciation_accessibility'] = CreativeCultureValidator._assess_pronunciation_accessibility(all_names)
                name_analysis['memorable_factor'] = CreativeCultureValidator._assess_memorable_factor(all_names)
                
                # Generate creative suggestions
                if name_analysis['name_diversity'] < 0.7:
                    suggestions.append(CreativeValidationIssue(
                        issue_type=ValidationIssueType.CREATIVE_OPPORTUNITY,
                        severity=CultureValidationSeverity.LOW,
                        category=CultureValidationCategory.CREATIVITY,
                        message="Names could be more diverse for richer character options",
                        creative_suggestions=["Add names with different syllable patterns", "Include names with varied cultural flavors"],
                        character_impact="More diverse names provide players with more character personality options"
                    ))
                
                if len(available_categories) < 4:
                    enhancements.append("Consider adding more name categories (titles, epithets, etc.) for richer character backgrounds")
                
                # Calculate overall name generation score
                name_generation_score = (
                    name_analysis['name_diversity'] * 0.25 +
                    name_analysis['creative_uniqueness'] * 0.25 +
                    name_analysis['character_fit_potential'] * 0.25 +
                    name_analysis['memorable_factor'] * 0.25
                )
            else:
                # No names available
                opportunities.append(CreativeValidationIssue(
                    issue_type=ValidationIssueType.NAME_GENERATION_ISSUE,
                    severity=CultureValidationSeverity.HIGH,
                    category=CultureValidationCategory.COMPLETENESS,
                    message="No names available for character generation",
                    creative_suggestions=["Add at least male and female names for basic character generation"],
                    character_impact="Players need names to create characters with this cultural background"
                ))
                name_generation_score = 0.0
            
            return CreativeValidationResult(
                is_usable=len(all_names) > 0,
                creative_quality_score=name_generation_score,
                gaming_usability_score=name_analysis.get('pronunciation_accessibility', 0.5),
                character_support_score=name_analysis.get('character_fit_potential', 0.5),
                name_generation_score=name_generation_score,
                creative_opportunities=opportunities,
                suggestions=suggestions,
                enhancements=enhancements,
                name_analysis=name_analysis
            )
            
        except Exception as e:
            raise CultureValidationError(f"Name generation assessment failed: {str(e)}") from e
    
    @staticmethod
    def assess_character_background_support(culture_data: Dict[str, Any]) -> CreativeValidationResult:
        """
        Assess how well culture supports character background creation.
        
        Pure function that evaluates cultural elements for character
        backstory and personality development potential.
        
        Args:
            culture_data: Dictionary containing cultural information
            
        Returns:
            CreativeValidationResult focused on character background support
        """
        opportunities = []
        suggestions = []
        enhancements = []
        
        background_analysis = {
            'cultural_depth': 0.0,
            'character_hook_potential': 0.0,
            'background_variety': 0.0,
            'story_integration_ease': 0.0,
            'roleplay_inspiration': 0.0,
            'background_elements': []
        }
        
        try:
            # Check for character background elements
            background_elements = []
            
            if 'cultural_traits' in culture_data:
                background_elements.append('cultural_traits')
                background_analysis['cultural_depth'] += 0.3
            
            if 'social_structure' in culture_data or 'hierarchy' in culture_data:
                background_elements.append('social_structure')
                background_analysis['cultural_depth'] += 0.2
            
            if 'traditions' in culture_data or 'customs' in culture_data:
                background_elements.append('traditions')
                background_analysis['cultural_depth'] += 0.2
            
            if 'values' in culture_data or 'beliefs' in culture_data:
                background_elements.append('values')
                background_analysis['cultural_depth'] += 0.2
            
            if 'occupations' in culture_data or 'professions' in culture_data:
                background_elements.append('occupations')
                background_analysis['background_variety'] += 0.3
            
            if 'geographical_context' in culture_data or 'environment' in culture_data:
                background_elements.append('geography')
                background_analysis['story_integration_ease'] += 0.2
            
            background_analysis['background_elements'] = background_elements
            
            # Assess character hook potential
            if 'conflicts' in culture_data or 'challenges' in culture_data:
                background_analysis['character_hook_potential'] += 0.4
            if 'relationships' in culture_data or 'alliances' in culture_data:
                background_analysis['character_hook_potential'] += 0.3
            if 'mysteries' in culture_data or 'secrets' in culture_data:
                background_analysis['character_hook_potential'] += 0.3
            
            # Assess roleplay inspiration
            description_quality = CreativeCultureValidator._assess_description_quality(culture_data)
            background_analysis['roleplay_inspiration'] = description_quality
            
            # Generate creative suggestions based on gaps
            if background_analysis['cultural_depth'] < 0.5:
                suggestions.append(CreativeValidationIssue(
                    issue_type=ValidationIssueType.CHARACTER_BACKGROUND_GAP,
                    severity=CultureValidationSeverity.LOW,
                    category=CultureValidationCategory.CREATIVITY,
                    message="Culture could use more depth for character backgrounds",
                    creative_suggestions=[
                        "Add cultural traits or values that characters can embody",
                        "Include social customs that affect character behavior",
                        "Describe cultural practices that create character motivations"
                    ],
                    character_impact="Richer cultural details give players more material for character development"
                ))
            
            if background_analysis['character_hook_potential'] < 0.3:
                enhancements.append("Add cultural conflicts or challenges that create character story hooks")
            
            if not background_elements:
                opportunities.append(CreativeValidationIssue(
                    issue_type=ValidationIssueType.CREATIVE_POTENTIAL,
                    severity=CultureValidationSeverity.MEDIUM,
                    category=CultureValidationCategory.CREATIVITY,
                    message="Culture has great potential for character background development",
                    creative_suggestions=[
                        "Add cultural traits to inspire character personalities",
                        "Include traditional occupations for character backgrounds",
                        "Describe cultural values that drive character motivations"
                    ],
                    character_impact="These elements would provide rich material for character creation"
                ))
            
            # Calculate character support score
            character_support_score = (
                background_analysis['cultural_depth'] * 0.3 +
                background_analysis['character_hook_potential'] * 0.25 +
                background_analysis['background_variety'] * 0.25 +
                background_analysis['roleplay_inspiration'] * 0.2
            )
            
            return CreativeValidationResult(
                is_usable=True,  # Culture is always usable for character backgrounds
                creative_quality_score=character_support_score,
                gaming_usability_score=background_analysis['story_integration_ease'],
                character_support_score=character_support_score,
                name_generation_score=0.5,  # Not the focus of this assessment
                creative_opportunities=opportunities,
                suggestions=suggestions,
                enhancements=enhancements,
                character_background_analysis=background_analysis,
                metadata={'background_elements_found': len(background_elements)}
            )
            
        except Exception as e:
            raise CultureValidationError(f"Character background assessment failed: {str(e)}") from e
    
    @staticmethod
    def assess_gaming_usability(culture_data: Dict[str, Any]) -> CreativeValidationResult:
        """
        Assess culture's usability for tabletop gaming.
        
        Pure function that evaluates practical gaming concerns while
        maintaining creative freedom and encouraging enhancement.
        
        Args:
            culture_data: Dictionary containing culture data
            
        Returns:
            CreativeValidationResult focused on gaming usability
        """
        opportunities = []
        suggestions = []
        enhancements = []
        
        gaming_analysis = {
            'table_friendliness': 0.0,
            'dm_usability': 0.0,
            'player_accessibility': 0.0,
            'session_integration': 0.0,
            'reference_ease': 0.0,
            'gaming_aids': []
        }
        
        try:
            # Assess name usability for gaming
            all_names = CreativeCultureValidator._collect_all_names(culture_data)
            
            if all_names:
                # Gaming-specific name analysis
                pronunciation_score = CreativeCultureValidator._assess_gaming_pronunciation(all_names)
                length_score = CreativeCultureValidator._assess_gaming_name_length(all_names)
                distinctiveness_score = CreativeCultureValidator._assess_name_distinctiveness(all_names)
                
                gaming_analysis['table_friendliness'] = (pronunciation_score + length_score + distinctiveness_score) / 3
                
                # Suggest improvements if needed
                if pronunciation_score < 0.6:
                    suggestions.append(CreativeValidationIssue(
                        issue_type=ValidationIssueType.GAMING_ENHANCEMENT,
                        severity=CultureValidationSeverity.LOW,
                        category=CultureValidationCategory.USABILITY,
                        message="Some names might be challenging to pronounce during play",
                        creative_suggestions=[
                            "Consider adding phonetic guides for complex names",
                            "Include simpler nickname variants",
                            "Add pronunciation tips in parentheses"
                        ],
                        character_impact="Easier names help players stay immersed in character roleplay"
                    ))
                
                if length_score < 0.7:
                    enhancements.append("Consider shorter name variants for quicker table reference")
            
            # Check for gaming aids
            gaming_aids = []
            if 'pronunciation_guide' in culture_data:
                gaming_aids.append('pronunciation_guide')
                gaming_analysis['reference_ease'] += 0.3
            
            if 'quick_reference' in culture_data or 'summary' in culture_data:
                gaming_aids.append('quick_reference')
                gaming_analysis['dm_usability'] += 0.3
            
            if 'naming_examples' in culture_data:
                gaming_aids.append('naming_examples')
                gaming_analysis['dm_usability'] += 0.2
            
            if 'character_integration' in culture_data:
                gaming_aids.append('character_integration')
                gaming_analysis['session_integration'] += 0.4
            
            gaming_analysis['gaming_aids'] = gaming_aids
            
            # Suggest useful gaming enhancements
            if not gaming_aids:
                opportunities.append(CreativeValidationIssue(
                    issue_type=ValidationIssueType.GAMING_ENHANCEMENT,
                    severity=CultureValidationSeverity.LOW,
                    category=CultureValidationCategory.USABILITY,
                    message="Culture could benefit from gaming convenience features",
                    creative_suggestions=[
                        "Add a quick reference summary for DMs",
                        "Include example character concepts",
                        "Provide naming pattern examples for improvisation"
                    ],
                    character_impact="Gaming aids help DMs and players use the culture more effectively"
                ))
            
            # Calculate gaming usability score
            gaming_score = (
                gaming_analysis['table_friendliness'] * 0.3 +
                gaming_analysis['dm_usability'] * 0.25 +
                gaming_analysis['player_accessibility'] * 0.25 +
                gaming_analysis['reference_ease'] * 0.2
            )
            
            return CreativeValidationResult(
                is_usable=True,  # Almost all cultures are usable for gaming
                creative_quality_score=gaming_score,
                gaming_usability_score=gaming_score,
                character_support_score=gaming_analysis['session_integration'],
                name_generation_score=gaming_analysis['table_friendliness'],
                creative_opportunities=opportunities,
                suggestions=suggestions,
                enhancements=enhancements,
                gaming_analysis=gaming_analysis,
                metadata={'gaming_aids_count': len(gaming_aids)}
            )
            
        except Exception as e:
            raise CultureValidationError(f"Gaming usability assessment failed: {str(e)}") from e
    
    @staticmethod
    def assess_creative_potential(culture_data: Dict[str, Any]) -> CreativeValidationResult:
        """
        Assess the creative potential and storytelling value of a culture.
        
        Pure function that evaluates how well a culture inspires creativity
        and supports diverse character concepts and storylines.
        
        Args:
            culture_data: Dictionary containing culture data
            
        Returns:
            CreativeValidationResult focused on creative potential
        """
        opportunities = []
        suggestions = []
        enhancements = []
        
        creative_analysis = {
            'inspiration_factor': 0.0,
            'concept_diversity': 0.0,
            'storytelling_hooks': 0.0,
            'creative_flexibility': 0.0,
            'uniqueness_factor': 0.0,
            'creative_elements': []
        }
        
        try:
            # Assess creative elements
            creative_elements = []
            
            # Check for inspiring cultural elements
            if 'unique_features' in culture_data or 'distinctive_traits' in culture_data:
                creative_elements.append('unique_features')
                creative_analysis['uniqueness_factor'] += 0.4
            
            if 'mysteries' in culture_data or 'legends' in culture_data:
                creative_elements.append('mysteries')
                creative_analysis['storytelling_hooks'] += 0.3
            
            if 'conflicts' in culture_data or 'tensions' in culture_data:
                creative_elements.append('conflicts')
                creative_analysis['storytelling_hooks'] += 0.3
            
            if 'philosophy' in culture_data or 'worldview' in culture_data:
                creative_elements.append('philosophy')
                creative_analysis['concept_diversity'] += 0.3
            
            if 'arts' in culture_data or 'crafts' in culture_data:
                creative_elements.append('arts')
                creative_analysis['concept_diversity'] += 0.2
            
            if 'magic_relation' in culture_data or 'supernatural' in culture_data:
                creative_elements.append('supernatural')
                creative_analysis['inspiration_factor'] += 0.3
            
            creative_analysis['creative_elements'] = creative_elements
            
            # Assess naming creativity
            all_names = CreativeCultureValidator._collect_all_names(culture_data)
            if all_names:
                naming_creativity = CreativeCultureValidator._assess_naming_creativity(all_names)
                creative_analysis['inspiration_factor'] += naming_creativity * 0.3
            
            # Assess flexibility for different character types
            flexibility_score = CreativeCultureValidator._assess_character_concept_flexibility(culture_data)
            creative_analysis['creative_flexibility'] = flexibility_score
            
            # Generate creative enhancement suggestions
            if creative_analysis['storytelling_hooks'] < 0.3:
                suggestions.append(CreativeValidationIssue(
                    issue_type=ValidationIssueType.CREATIVE_OPPORTUNITY,
                    severity=CultureValidationSeverity.LOW,
                    category=CultureValidationCategory.CREATIVITY,
                    message="Culture has potential for more storytelling hooks",
                    creative_suggestions=[
                        "Add cultural mysteries or legends for character backstories",
                        "Include internal conflicts that create character motivations",
                        "Describe unique cultural practices that spark adventure ideas"
                    ],
                    character_impact="Story hooks give characters interesting backgrounds and motivations"
                ))
            
            if creative_analysis['concept_diversity'] < 0.4:
                enhancements.append("Consider adding diverse cultural roles and perspectives for varied character concepts")
            
            if not creative_elements:
                opportunities.append(CreativeValidationIssue(
                    issue_type=ValidationIssueType.CREATIVE_POTENTIAL,
                    severity=CultureValidationSeverity.LOW,
                    category=CultureValidationCategory.CREATIVITY,
                    message="Culture shows great potential for creative enhancement",
                    creative_suggestions=[
                        "Add unique cultural features that make characters interesting",
                        "Include cultural values that create character motivations",
                        "Describe cultural practices that inspire character concepts"
                    ],
                    character_impact="Creative elements help players develop unique and memorable characters"
                ))
            
            # Calculate overall creative potential score
            creative_quality_score = (
                creative_analysis['inspiration_factor'] * 0.25 +
                creative_analysis['concept_diversity'] * 0.25 +
                creative_analysis['storytelling_hooks'] * 0.25 +
                creative_analysis['creative_flexibility'] * 0.25
            )
            
            return CreativeValidationResult(
                is_usable=True,  # All cultures have creative potential
                creative_quality_score=creative_quality_score,
                gaming_usability_score=creative_analysis['creative_flexibility'],
                character_support_score=creative_analysis['concept_diversity'],
                name_generation_score=creative_analysis['inspiration_factor'],
                creative_opportunities=opportunities,
                suggestions=suggestions,
                enhancements=enhancements,
                creative_potential_analysis=creative_analysis,
                metadata={'creative_elements_count': len(creative_elements)}
            )
            
        except Exception as e:
            raise CultureValidationError(f"Creative potential assessment failed: {str(e)}") from e
    
    # ============================================================================
    # PRIVATE HELPER METHODS (Pure Functions)
    # ============================================================================
    
    @staticmethod
    def _has_minimum_content(culture_data: Dict[str, Any]) -> bool:
        """Check if culture has minimum content to be usable."""
        # Very permissive - almost any content makes a culture usable
        return (
            bool(culture_data.get('name')) or
            bool(CreativeCultureValidator._collect_all_names(culture_data)) or
            bool(culture_data.get('description')) or
            bool(culture_data.get('cultural_traits'))
        )
    
    @staticmethod
    def _collect_all_names(culture_data: Dict[str, Any]) -> List[str]:
        """Collect all names from all categories."""
        all_names = []
        name_categories = ['male_names', 'female_names', 'neutral_names', 
                          'family_names', 'titles', 'epithets']
        
        for category in name_categories:
            if category in culture_data and isinstance(culture_data[category], list):
                all_names.extend([name for name in culture_data[category] if name and name.strip()])
        
        return all_names
    
    @staticmethod
    def _count_total_names(culture_data: Dict[str, Any]) -> int:
        """Count total names across all categories."""
        return len(CreativeCultureValidator._collect_all_names(culture_data))
    
    @staticmethod
    def _count_creative_elements(culture_data: Dict[str, Any]) -> int:
        """Count creative elements that support character generation."""
        creative_keys = [
            'cultural_traits', 'traditions', 'values', 'beliefs', 'customs',
            'social_structure', 'occupations', 'arts', 'philosophy', 'mysteries',
            'conflicts', 'unique_features', 'geographical_context'
        ]
        
        return sum(1 for key in creative_keys if key in culture_data and culture_data[key])
    
    @staticmethod
    def _assess_name_diversity(names: List[str]) -> float:
        """Assess diversity of names for character generation."""
        if not names or len(names) < 2:
            return 0.5  # Neutral score for insufficient data
        
        # Check various diversity factors
        diversity_score = 0.0
        
        # Length diversity
        lengths = [len(name) for name in names]
        length_variance = len(set(lengths)) / len(names) if names else 0
        diversity_score += min(1.0, length_variance * 2) * 0.3
        
        # Starting letter diversity
        first_letters = [name[0].lower() for name in names if name]
        letter_variance = len(set(first_letters)) / len(first_letters) if first_letters else 0
        diversity_score += min(1.0, letter_variance * 1.5) * 0.3
        
        # Phonetic pattern diversity
        vowel_patterns = []
        for name in names:
            vowel_count = len(re.findall(r'[aeiou]', name.lower()))
            consonant_count = len(name) - vowel_count
            if consonant_count > 0:
                vowel_patterns.append(vowel_count / len(name))
        
        if vowel_patterns:
            pattern_variance = len(set([round(p, 1) for p in vowel_patterns])) / len(vowel_patterns)
            diversity_score += min(1.0, pattern_variance * 2) * 0.4
        
        return min(1.0, diversity_score)
    
    @staticmethod
    def _assess_creative_uniqueness(names: List[str]) -> float:
        """Assess creative uniqueness of names."""
        if not names:
            return 0.5
        
        uniqueness_score = 0.0
        
        # Check for creative name patterns
        creative_patterns = 0
        
        for name in names:
            # Bonus for interesting combinations
            if re.search(r'[aeiou]{2,}', name.lower()):  # Vowel clusters
                creative_patterns += 1
            if re.search(r'[bcdfghjklmnpqrstvwxyz]{2,}', name.lower()):  # Consonant clusters
                creative_patterns += 1
            if "'" in name or "-" in name:  # Apostrophes or hyphens
                creative_patterns += 1
            if any(char.isupper() for char in name[1:]):  # Internal capitals
                creative_patterns += 1
        
        uniqueness_score = min(1.0, creative_patterns / len(names))
        
        return uniqueness_score
    
    @staticmethod
    def _assess_character_fit_potential(names: List[str]) -> float:
        """Assess how well names fit various character archetypes."""
        if not names:
            return 0.5
        
        # Names should be versatile for different character types
        fit_score = 0.0
        
        # Check for range of name "feels"
        strong_names = sum(1 for name in names if any(sound in name.lower() 
                          for sound in ['or', 'ar', 'ur', 'th', 'gr', 'kr']))
        elegant_names = sum(1 for name in names if any(sound in name.lower() 
                           for sound in ['el', 'ir', 'al', 'ian', 'ara', 'iel']))
        mystical_names = sum(1 for name in names if any(sound in name.lower() 
                            for sound in ['ys', 'th', 'ae', 'ix', 'yn', 'vel']))
        
        # Good distribution across archetypes
        archetype_coverage = sum(1 for count in [strong_names, elegant_names, mystical_names] if count > 0)
        fit_score = archetype_coverage / 3.0
        
        return fit_score
    
    @staticmethod
    def _assess_pronunciation_accessibility(names: List[str]) -> float:
        """Assess how accessible names are for pronunciation."""
        if not names:
            return 0.5
        
        accessibility_score = 0.0
        accessible_count = 0
        
        for name in names:
            name_score = 1.0
            
            # Penalize very complex pronunciations
            if re.search(r'[xqz]', name.lower()):
                name_score -= 0.2
            if re.search(r'[bcdfghjklmnpqrstvwxyz]{4,}', name.lower()):
                name_score -= 0.3
            if len(name) > 12:
                name_score -= 0.2
            
            # Bonus for clear pronunciation patterns
            if re.match(r'^[A-Z][a-z]+$', name):
                name_score += 0.1
            
            if name_score >= 0.6:
                accessible_count += 1
        
        accessibility_score = accessible_count / len(names)
        return accessibility_score
    
    @staticmethod
    def _assess_memorable_factor(names: List[str]) -> float:
        """Assess how memorable names are for gaming."""
        if not names:
            return 0.5
        
        memorable_score = 0.0
        
        for name in names:
            score = 0.5  # Base memorability
            
            # Bonus for distinctive features
            if len(set(name.lower())) / len(name) > 0.7:  # High unique letter ratio
                score += 0.2
            if 4 <= len(name) <= 8:  # Good length for memory
                score += 0.2
            if name[0] != name[-1]:  # Different start/end
                score += 0.1
            
            memorable_score += min(1.0, score)
        
        return memorable_score / len(names)
    
    @staticmethod
    def _assess_description_quality(culture_data: Dict[str, Any]) -> float:
        """Assess quality of cultural descriptions for roleplay inspiration."""
        description_score = 0.0
        
        # Check for various description elements
        description_elements = ['description', 'cultural_context', 'background']
        
        for element in description_elements:
            if element in culture_data and culture_data[element]:
                desc = culture_data[element]
                if isinstance(desc, str) and len(desc.split()) > 10:
                    description_score += 0.3
        
        # Check for specific inspiring elements
        inspiring_elements = ['values', 'beliefs', 'traditions', 'customs', 'philosophy']
        for element in inspiring_elements:
            if element in culture_data and culture_data[element]:
                description_score += 0.1
        
        return min(1.0, description_score)
    
    @staticmethod
    def _assess_gaming_pronunciation(names: List[str]) -> float:
        """Assess pronunciation difficulty specifically for gaming context."""
        if not names:
            return 0.5
        
        easy_count = 0
        
        for name in names:
            # Gaming-friendly criteria (more lenient than strict linguistics)
            is_easy = True
            
            # Only penalize truly difficult patterns
            if re.search(r'[bcdfghjklmnpqrstvwxyz]{4,}', name.lower()):
                is_easy = False
            if len(name) > 15:
                is_easy = False
            
            if is_easy:
                easy_count += 1
        
        return easy_count / len(names)
    
    @staticmethod
    def _assess_gaming_name_length(names: List[str]) -> float:
        """Assess name length suitability for gaming."""
        if not names:
            return 0.5
        
        good_length_count = 0
        
        for name in names:
            # Gaming-friendly length (quite permissive)
            if 3 <= len(name) <= 12:
                good_length_count += 1
        
        return good_length_count / len(names)
    
    @staticmethod
    def _assess_name_distinctiveness(names: List[str]) -> float:
        """Assess how distinctive names are from each other."""
        if not names or len(names) < 2:
            return 1.0
        
        distinctive_count = 0
        
        for i, name in enumerate(names):
            is_distinctive = True
            
            for j, other_name in enumerate(names):
                if i != j:
                    # Check for problematic similarities
                    if name.lower().startswith(other_name.lower()[:3]) and len(other_name) > 3:
                        is_distinctive = False
                    if other_name.lower().startswith(name.lower()[:3]) and len(name) > 3:
                        is_distinctive = False
            
            if is_distinctive:
                distinctive_count += 1
        
        return distinctive_count / len(names)
    
    @staticmethod
    def _assess_naming_creativity(names: List[str]) -> float:
        """Assess creativity in naming patterns."""
        if not names:
            return 0.5
        
        creativity_score = 0.0
        
        # Look for creative elements
        creative_elements = 0
        
        for name in names:
            if "'" in name:  # Apostrophes suggest interesting phonetics
                creative_elements += 1
            if "-" in name:  # Compound names
                creative_elements += 1
            if any(char.isupper() for char in name[1:]):  # Internal capitals
                creative_elements += 1
            if re.search(r'[aeiou]{2,}', name.lower()):  # Interesting vowel patterns
                creative_elements += 1
        
        creativity_score = min(1.0, creative_elements / len(names))
        
        return creativity_score
    
    @staticmethod
    def _assess_character_concept_flexibility(culture_data: Dict[str, Any]) -> float:
        """Assess how flexible culture is for different character concepts."""
        flexibility_score = 0.5  # Base flexibility
        
        # Check for elements that support diverse character concepts
        if 'occupations' in culture_data or 'professions' in culture_data:
            flexibility_score += 0.2
        
        if 'social_structure' in culture_data:
            flexibility_score += 0.15
        
        if 'values' in culture_data or 'beliefs' in culture_data:
            flexibility_score += 0.15
        
        # Check for conflicting or overly rigid elements
        restrictive_elements = ['strict_hierarchy', 'rigid_roles', 'forbidden_practices']
        restriction_count = sum(1 for element in restrictive_elements if element in culture_data)
        
        if restriction_count > 0:
            flexibility_score -= restriction_count * 0.1
        
        return max(0.0, min(1.0, flexibility_score))


# ============================================================================
# UTILITY FUNCTIONS (Pure Functions)
# ============================================================================

def validate_for_character_creation(culture_data: Dict[str, Any]) -> CreativeValidationResult:
    """
    Convenience function for character creation validation.
    
    Pure function that focuses on character generation support.
    
    Args:
        culture_data: Dictionary containing culture information
        
    Returns:
        CreativeValidationResult optimized for character creation
    """
    return CreativeCultureValidator.validate_for_character_generation(culture_data)


def quick_gaming_assessment(culture_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Quick assessment of gaming usability.
    
    Pure function for rapid gaming suitability check.
    
    Args:
        culture_data: Dictionary containing culture information
        
    Returns:
        Dictionary with gaming assessment summary
    """
    result = CreativeCultureValidator.assess_gaming_usability(culture_data)
    
    return {
        'gaming_ready': result.gaming_usability_score >= 0.6,
        'usability_score': result.gaming_usability_score,
        'main_suggestions': [suggestion.message for suggestion in result.suggestions[:3]],
        'enhancements': result.enhancements[:3],
        'name_count': len(CreativeCultureValidator._collect_all_names(culture_data))
    }


def assess_creative_value(culture_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Assess creative value for character generation.
    
    Pure function focused on creative potential assessment.
    
    Args:
        culture_data: Dictionary containing culture information
        
    Returns:
        Dictionary with creative value analysis
    """
    result = CreativeCultureValidator.assess_creative_potential(culture_data)
    
    return {
        'creative_score': result.creative_quality_score,
        'character_support': result.character_support_score,
        'inspiration_level': 'high' if result.creative_quality_score >= 0.7 else 
                           'medium' if result.creative_quality_score >= 0.4 else 'growing',
        'creative_opportunities': [opp.message for opp in result.creative_opportunities],
        'enhancement_suggestions': result.enhancements
    }


def get_character_generation_readiness(culture_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get comprehensive readiness assessment for character generation.
    
    Pure function that provides overall readiness for character creation.
    
    Args:
        culture_data: Dictionary containing culture information
        
    Returns:
        Dictionary with readiness assessment
    """
    result = CreativeCultureValidator.validate_for_character_generation(culture_data)
    
    return {
        'ready_for_characters': result.is_usable and result.character_support_score >= 0.3,
        'character_support_score': result.character_support_score,
        'name_generation_score': result.name_generation_score,
        'creative_quality_score': result.creative_quality_score,
        'gaming_usability_score': result.gaming_usability_score,
        'top_suggestions': [sugg.message for sugg in result.suggestions[:5]],
        'character_impact_notes': [
            sugg.character_impact for sugg in result.suggestions 
            if sugg.character_impact
        ][:3]
    }


# ============================================================================
# MODULE METADATA
# ============================================================================

__version__ = "1.0.0"
__description__ = "Creative Culture Validation System for Character Generation"

# Clean Architecture compliance metadata
CLEAN_ARCHITECTURE_COMPLIANCE = {
    "layer": "core/utils/validation",
    "dependencies": [
        "typing", "dataclasses", "enum", "re", "collections",
        "../../enums/culture_types", "../../exceptions/culture"
    ],
    "dependents": ["domain/services", "application/use_cases", "core/utils/cultures"],
    "infrastructure_independent": True,
    "pure_functions": True,  
    "side_effects": "none",
    "focuses_on": "Creative culture quality assessment for character generation",
    "immutable_data": True,
    "stateless_operations": True,
    "creative_focus": True,
    "character_generation_optimized": True
}

# Creative validation philosophy
CREATIVE_VALIDATION_PHILOSOPHY = {
    "primary_goal": "Enable and enhance creative character generation",
    "approach": "Supportive assessment rather than restrictive validation",
    "focus_areas": [
        "Character background support",
        "Gaming usability optimization", 
        "Creative inspiration enhancement",
        "Name generation quality",
        "Player experience improvement"
    ],
    "principles": [
        "Almost all cultures are usable for character generation",
        "Provide constructive suggestions rather than rigid requirements",
        "Focus on creative potential and enhancement opportunities",
        "Support diverse character concepts and backgrounds",
        "Maintain creative freedom while offering quality improvements"
    ]
}

# Usage examples focused on character generation
"""
Usage Examples for Character Generation:

1. Validate culture for character creation:
   >>> result = validate_for_character_creation(culture_data)
   >>> print(f"Character ready: {result.character_support_score:.2f}")

2. Quick gaming assessment:
   >>> assessment = quick_gaming_assessment(culture_data)
   >>> print(f"Gaming ready: {assessment['gaming_ready']}")

3. Assess creative value:
   >>> creative_value = assess_creative_value(culture_data)
   >>> print(f"Creative score: {creative_value['creative_score']:.2f}")

4. Check character generation readiness:
   >>> readiness = get_character_generation_readiness(culture_data)
   >>> print(f"Ready for characters: {readiness['ready_for_characters']}")

5. Focus on specific aspects:
   >>> name_result = CreativeCultureValidator.assess_name_generation_quality(culture_data)
   >>> background_result = CreativeCultureValidator.assess_character_background_support(culture_data)
   >>> gaming_result = CreativeCultureValidator.assess_gaming_usability(culture_data)
"""