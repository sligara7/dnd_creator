"""
Enhanced Creative Culture Validation System - Character Generation Quality Assurance.

COMPLETELY REFACTORED: Full integration with enhanced culture_types enums
following CREATIVE_VALIDATION_APPROACH philosophy.

Validates generated cultures for creative quality, gaming usability, and character
background support with complete enum integration. Focuses on enhancing creative 
freedom rather than limiting it, with constructive suggestions over rigid requirements.

Enhanced Features:
- Complete integration with all new culture_types enums
- Enhancement category targeting and priority assessment
- Gaming utility optimization throughout validation
- Preset-based validation support
- Constructive validation with enum-based enhancement suggestions
- Creative freedom enablement with character generation focus
- Character readiness assessment with enum scoring

Follows Clean Architecture principles with pure functions and immutable data.

This module provides:
- Creative quality assessment with enum-based scoring
- Gaming usability optimization with enum recommendations  
- Character background support validation with enhancement categories
- Name generation quality assurance with enum-based improvements
- Pure functional validation with constructive feedback using enum priorities
- Creative freedom preservation with helpful enum-based suggestions
"""

from typing import Dict, List, Optional, Set, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import re
from collections import Counter
from datetime import datetime

# Enhanced import of core types with complete enum integration
from ...enums.culture_types import (
    # Core validation enums (enhanced)
    CultureValidationCategory,
    CultureValidationSeverity,
    
    # Core culture generation enums
    CultureGenerationType,
    CultureAuthenticityLevel,
    CultureCreativityLevel,
    CultureSourceType,
    CultureComplexityLevel,
    
    # Enhancement and status enums (NEW)
    CultureEnhancementCategory,
    CultureEnhancementPriority,
    CultureGenerationStatus,
    
    # Cultural structure enums
    CultureNamingStructure,
    CultureGenderSystem,
    CultureLinguisticFamily,
    CultureTemporalPeriod,
    
    # Enhanced utility functions (NEW)
    suggest_creative_culture_enhancements,
    calculate_character_generation_score,
    get_character_generation_recommendations,
    
    # Preset configurations and compliance (NEW)
    CHARACTER_CULTURE_PRESETS,
    CREATIVE_VALIDATION_APPROACH_COMPLIANCE as ENUM_COMPLIANCE
)

from ...exceptions.culture import (
    CultureValidationError,
    CultureStructureError
)


# ============================================================================
# ENHANCED VALIDATION ENUMS AND TYPES
# ============================================================================

class EnhancedValidationIssueType(Enum):
    """Enhanced validation issue types with enum integration focus."""
    CREATIVE_OPPORTUNITY = "creative_opportunity"
    GAMING_ENHANCEMENT = "gaming_enhancement"
    CHARACTER_BACKGROUND_GAP = "character_background_gap"
    NAME_GENERATION_ENHANCEMENT = "name_generation_enhancement"
    USABILITY_IMPROVEMENT = "usability_improvement"
    CREATIVE_CONSISTENCY = "creative_consistency"
    PLAYER_EXPERIENCE = "player_experience"
    BACKGROUND_DEPTH = "background_depth"
    CREATIVE_POTENTIAL = "creative_potential"
    GENERATION_QUALITY = "generation_quality"
    
    # NEW: Enum-based enhancement types
    ENHANCEMENT_CATEGORY_OPPORTUNITY = "enhancement_category_opportunity"
    PRESET_COMPATIBILITY_IMPROVEMENT = "preset_compatibility_improvement"
    ENUM_SCORING_ENHANCEMENT = "enum_scoring_enhancement"
    CHARACTER_GENERATION_OPTIMIZATION = "character_generation_optimization"


class EnhancedCreativeValidationFocus(Enum):
    """Enhanced focus areas for creative validation with enum integration."""
    CHARACTER_BACKGROUNDS = "character_backgrounds"
    NAME_GENERATION = "name_generation"
    GAMING_EXPERIENCE = "gaming_experience"
    CREATIVE_FREEDOM = "creative_freedom"
    PLAYER_USABILITY = "player_usability"
    STORY_POTENTIAL = "story_potential"
    
    # NEW: Enum-based focus areas
    ENHANCEMENT_CATEGORY_TARGETING = "enhancement_category_targeting"
    PRESET_SYSTEM_INTEGRATION = "preset_system_integration"
    ENUM_BASED_SCORING = "enum_based_scoring"
    CHARACTER_GENERATION_READINESS = "character_generation_readiness"


@dataclass(frozen=True)
class EnhancedCreativeValidationIssue:
    """
    Enhanced validation issue with complete enum integration.
    
    UPDATED: Represents opportunities for improvement with enum-based
    enhancement suggestions and character generation focus.
    """
    issue_type: EnhancedValidationIssueType
    severity: CultureValidationSeverity
    category: CultureValidationCategory
    message: str
    context: str = ""
    affected_items: List[str] = field(default_factory=list)
    creative_suggestions: List[str] = field(default_factory=list)
    character_impact: str = ""
    
    # NEW: Enhanced enum-based fields
    target_enhancement_categories: List[CultureEnhancementCategory] = field(default_factory=list)
    enhancement_priority: CultureEnhancementPriority = CultureEnhancementPriority.NARRATIVE_HELPFUL
    enum_based_recommendations: List[str] = field(default_factory=list)
    preset_compatibility_notes: List[str] = field(default_factory=list)
    character_generation_impact: str = ""
    
    def __post_init__(self):
        """Enhanced validation with enum integration."""
        if not self.message:
            raise CultureValidationError("Validation issue message cannot be empty")
        
        # Auto-generate enum-based enhancement categories if not provided
        if not self.target_enhancement_categories:
            auto_categories = []
            
            if self.issue_type == EnhancedValidationIssueType.NAME_GENERATION_ENHANCEMENT:
                auto_categories.append(CultureEnhancementCategory.CHARACTER_NAMES)
            elif self.issue_type == EnhancedValidationIssueType.CHARACTER_BACKGROUND_GAP:
                auto_categories.extend([
                    CultureEnhancementCategory.BACKGROUND_HOOKS,
                    CultureEnhancementCategory.CULTURAL_TRAITS
                ])
            elif self.issue_type == EnhancedValidationIssueType.GAMING_ENHANCEMENT:
                auto_categories.append(CultureEnhancementCategory.GAMING_UTILITY)
            
            if auto_categories:
                object.__setattr__(self, 'target_enhancement_categories', auto_categories)


@dataclass(frozen=True)
class EnhancedCreativeValidationResult:
    """
    Enhanced validation result with complete enum integration.
    
    UPDATED: Contains quality assessment and enum-based enhancement suggestions
    with character generation focus and preset compatibility analysis.
    """
    is_usable: bool  # Almost always True - cultures are usable for character generation
    creative_quality_score: float      # 0.0 to 1.0 - enhanced with enum scoring
    gaming_usability_score: float      # 0.0 to 1.0 - gaming table optimization
    character_support_score: float     # 0.0 to 1.0 - character background support
    name_generation_score: float       # 0.0 to 1.0 - name quality for characters
    
    # NEW: Enhanced enum-based scoring
    calculated_generation_score: Optional[float] = None  # From calculate_character_generation_score()
    enum_scoring_breakdown: Dict[str, float] = field(default_factory=dict)
    
    # Enhanced validation results
    creative_opportunities: List[EnhancedCreativeValidationIssue] = field(default_factory=list)
    suggestions: List[EnhancedCreativeValidationIssue] = field(default_factory=list)
    enhancements: List[str] = field(default_factory=list)
    
    # NEW: Enum-based enhancement recommendations
    identified_enhancement_categories: List[CultureEnhancementCategory] = field(default_factory=list)
    prioritized_enhancements: List[Tuple[str, CultureEnhancementPriority]] = field(default_factory=list)
    enum_based_recommendations: List[str] = field(default_factory=list)
    
    # Enhanced analysis with enum integration
    name_analysis: Dict[str, Any] = field(default_factory=dict)
    character_background_analysis: Dict[str, Any] = field(default_factory=dict)
    gaming_analysis: Dict[str, Any] = field(default_factory=dict)
    creative_potential_analysis: Dict[str, Any] = field(default_factory=dict)
    
    # NEW: Enum-based analysis results
    enum_assessment_results: Dict[str, Any] = field(default_factory=dict)
    preset_compatibility_analysis: Dict[str, Any] = field(default_factory=dict)
    character_generation_readiness: Dict[str, Any] = field(default_factory=dict)
    
    # Enhanced metadata
    validation_timestamp: Optional[str] = None
    validator_version: str = "3.0.0"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # NEW: Validation compliance tracking
    creative_validation_approach_compliant: bool = True
    character_generation_optimized: bool = True
    
    def __post_init__(self):
        """Enhanced validation with enum integration."""
        scores = [self.creative_quality_score, self.gaming_usability_score, 
                 self.character_support_score, self.name_generation_score]
        for score in scores:
            if not (0.0 <= score <= 1.0):
                raise CultureValidationError("All scores must be between 0.0 and 1.0")
        
        # Auto-set timestamp if not provided
        if not self.validation_timestamp:
            object.__setattr__(self, 'validation_timestamp', datetime.now().isoformat())
    
    # NEW: Enhanced methods using enum capabilities
    def get_critical_enhancements(self) -> List[str]:
        """Get high-priority enhancement suggestions."""
        return [
            suggestion for suggestion, priority in self.prioritized_enhancements
            if priority.should_prioritize
        ]
    
    def get_character_generation_readiness_percentage(self) -> int:
        """Get character generation readiness as percentage."""
        base_score = (
            self.character_support_score * 0.4 +
            self.name_generation_score * 0.3 +
            self.gaming_usability_score * 0.3
        )
        return int(base_score * 100)
    
    def is_preset_compatible(self, preset_name: str) -> bool:
        """Check compatibility with specific preset."""
        preset_analysis = self.preset_compatibility_analysis.get(preset_name, {})
        return preset_analysis.get('compatible', True)  # Default to compatible
    
    def get_top_enhancement_categories(self, limit: int = 3) -> List[CultureEnhancementCategory]:
        """Get top enhancement categories by priority."""
        category_priorities = {}
        for category in self.identified_enhancement_categories:
            # Find highest priority for this category
            category_priorities[category] = max(
                (priority for _, priority in self.prioritized_enhancements 
                 for issue in self.suggestions 
                 if category in issue.target_enhancement_categories),
                default=CultureEnhancementPriority.NARRATIVE_HELPFUL
            )
        
        # Sort by priority and return top categories
        sorted_categories = sorted(
            category_priorities.items(),
            key=lambda x: x[1].priority_score,
            reverse=True
        )
        
        return [category for category, _ in sorted_categories[:limit]]


# ============================================================================
# ENHANCED CREATIVE CULTURE VALIDATOR
# ============================================================================

class EnhancedCreativeCultureValidator:
    """
    Enhanced creative culture validation system with complete enum integration.
    
    COMPLETELY REFACTORED: Focuses on enabling character generation with
    complete enum integration and CREATIVE_VALIDATION_APPROACH compliance.
    
    Provides static methods for assessing culture quality for creative character
    generation with enum-based enhancement suggestions and preset compatibility.
    
    All methods are pure functions that enhance creativity rather than limit it.
    """
    
    # ============================================================================
    # MAIN ENHANCED VALIDATION METHODS (Pure Functions with Enum Integration)
    # ============================================================================
    
    @staticmethod
    def validate_for_character_generation_enhanced(
        culture_data: Dict[str, Any],
        target_preset: Optional[str] = None,
        enhancement_focus: List[CultureEnhancementCategory] = None
    ) -> EnhancedCreativeValidationResult:
        """
        Enhanced validation for character generation with complete enum integration.
        
        UPDATED: Pure function that assesses culture for character generation
        with enum-based scoring, enhancement category targeting, and preset compatibility.
        
        Args:
            culture_data: Dictionary containing culture information
            target_preset: Optional preset name for compatibility assessment
            enhancement_focus: Specific enhancement categories to focus on
            
        Returns:
            EnhancedCreativeValidationResult with enum-based analysis
            
        Example:
            >>> culture_data = {
            ...     'name': 'Skyborne Merchants',
            ...     'male_names': ['Zephyr', 'Gale', 'Storm'],
            ...     'female_names': ['Aria', 'Breeze', 'Tempest'],
            ...     'cultural_traits': {'focus': 'aerial trade', 'values': 'freedom'}
            ... }
            >>> result = EnhancedCreativeCultureValidator.validate_for_character_generation_enhanced(
            ...     culture_data,
            ...     target_preset="gaming_optimized",
            ...     enhancement_focus=[CultureEnhancementCategory.CHARACTER_NAMES, CultureEnhancementCategory.GAMING_UTILITY]
            ... )
            >>> print(f"Character support: {result.character_support_score:.2f}")
            >>> print(f"Generation score: {result.calculated_generation_score:.2f}")
        """
        if not culture_data or not isinstance(culture_data, dict):
            raise CultureValidationError("Culture data must be a non-empty dictionary")
        
        try:
            # Enhanced assessment with enum integration
            name_assessment = EnhancedCreativeCultureValidator.assess_name_generation_quality_enhanced(
                culture_data, enhancement_focus
            )
            background_assessment = EnhancedCreativeCultureValidator.assess_character_background_support_enhanced(
                culture_data, enhancement_focus
            )
            gaming_assessment = EnhancedCreativeCultureValidator.assess_gaming_usability_enhanced(
                culture_data, enhancement_focus
            )
            creative_assessment = EnhancedCreativeCultureValidator.assess_creative_potential_enhanced(
                culture_data, enhancement_focus
            )
            
            # NEW: Enum-based assessment
            enum_assessment = EnhancedCreativeCultureValidator.assess_enum_compatibility(culture_data)
            preset_assessment = EnhancedCreativeCultureValidator.assess_preset_compatibility(
                culture_data, target_preset
            )
            
            # Collect all enhanced opportunities and suggestions
            all_opportunities = []
            all_suggestions = []
            all_enhancements = []
            all_enhancement_categories = []
            all_prioritized_enhancements = []
            
            assessments = [name_assessment, background_assessment, gaming_assessment, 
                          creative_assessment, enum_assessment, preset_assessment]
            
            for assessment in assessments:
                all_opportunities.extend(assessment.creative_opportunities)
                all_suggestions.extend(assessment.suggestions)
                all_enhancements.extend(assessment.enhancements)
                all_enhancement_categories.extend(assessment.identified_enhancement_categories)
                all_prioritized_enhancements.extend(assessment.prioritized_enhancements)
            
            # Calculate enhanced scores
            creative_quality = creative_assessment.creative_quality_score
            gaming_usability = gaming_assessment.gaming_usability_score
            character_support = background_assessment.character_support_score
            name_generation = name_assessment.name_generation_score
            
            # NEW: Calculate enum-based generation score
            inferred_authenticity = EnhancedCreativeCultureValidator._infer_authenticity_level(culture_data)
            inferred_creativity = EnhancedCreativeCultureValidator._infer_creativity_level(culture_data)
            inferred_complexity = EnhancedCreativeCultureValidator._infer_complexity_level(culture_data)
            
            calculated_score = calculate_character_generation_score(
                inferred_authenticity, inferred_creativity, inferred_complexity
            )
            
            # NEW: Enhanced enum scoring breakdown
            enum_scoring_breakdown = {
                'authenticity_contribution': inferred_authenticity.character_support_score,
                'complexity_contribution': inferred_complexity.character_creation_readiness,
                'gaming_utility_score': inferred_authenticity.gaming_utility_score,
                'creative_freedom_score': inferred_creativity.creative_freedom_percentage / 100,
                'calculated_generation_score': calculated_score
            }
            
            # NEW: Generate enum-based recommendations
            enum_recommendations = get_character_generation_recommendations(
                inferred_authenticity, inferred_creativity, inferred_complexity
            )
            
            # Determine if culture is usable (almost always yes)
            is_usable = EnhancedCreativeCultureValidator._has_minimum_content_enhanced(culture_data)
            
            # NEW: Assess character generation readiness
            readiness_assessment = {
                'basic_usability': is_usable,
                'character_support_adequate': character_support >= 0.3,
                'name_generation_adequate': name_generation >= 0.3,
                'gaming_ready': gaming_usability >= 0.5,
                'creative_potential_good': creative_quality >= 0.4,
                'overall_readiness_percentage': int((character_support + name_generation + gaming_usability) / 3 * 100)
            }
            
            return EnhancedCreativeValidationResult(
                is_usable=is_usable,
                creative_quality_score=creative_quality,
                gaming_usability_score=gaming_usability,
                character_support_score=character_support,
                name_generation_score=name_generation,
                calculated_generation_score=calculated_score,
                enum_scoring_breakdown=enum_scoring_breakdown,
                creative_opportunities=all_opportunities,
                suggestions=all_suggestions,
                enhancements=list(set(all_enhancements)),
                identified_enhancement_categories=list(set(all_enhancement_categories)),
                prioritized_enhancements=all_prioritized_enhancements,
                enum_based_recommendations=enum_recommendations,
                name_analysis=name_assessment.name_analysis,
                character_background_analysis=background_assessment.character_background_analysis,
                gaming_analysis=gaming_assessment.gaming_analysis,
                creative_potential_analysis=creative_assessment.creative_potential_analysis,
                enum_assessment_results=enum_assessment.enum_assessment_results,
                preset_compatibility_analysis=preset_assessment.preset_compatibility_analysis,
                character_generation_readiness=readiness_assessment,
                metadata={
                    'validation_focus': 'enhanced_character_generation',
                    'enum_integration_complete': True,
                    'total_names': EnhancedCreativeCultureValidator._count_total_names(culture_data),
                    'creative_elements': EnhancedCreativeCultureValidator._count_creative_elements(culture_data),
                    'target_preset': target_preset,
                    'enhancement_focus': [cat.value for cat in enhancement_focus] if enhancement_focus else [],
                    'inferred_authenticity': inferred_authenticity.value,
                    'inferred_creativity': inferred_creativity.value,
                    'inferred_complexity': inferred_complexity.value
                },
                creative_validation_approach_compliant=True,
                character_generation_optimized=True
            )
            
        except Exception as e:
            if isinstance(e, CultureValidationError):
                raise
            raise CultureValidationError(f"Enhanced creative validation failed: {str(e)}") from e
    
    @staticmethod
    def assess_name_generation_quality_enhanced(
        culture_data: Dict[str, Any],
        enhancement_focus: List[CultureEnhancementCategory] = None
    ) -> EnhancedCreativeValidationResult:
        """
        Enhanced assessment of name generation quality with enum integration.
        
        UPDATED: Evaluates name diversity, creativity, and character generation
        potential with enum-based enhancement suggestions.
        
        Args:
            culture_data: Dictionary containing name lists
            enhancement_focus: Specific enhancement categories to focus on
            
        Returns:
            EnhancedCreativeValidationResult focused on name generation quality
        """
        opportunities = []
        suggestions = []
        enhancements = []
        enhancement_categories = []
        prioritized_enhancements = []
        
        name_analysis = {
            'total_names': 0,
            'name_diversity': 0.0,
            'creative_uniqueness': 0.0,
            'character_fit_potential': 0.0,
            'pronunciation_accessibility': 0.0,
            'memorable_factor': 0.0,
            'gaming_table_usability': 0.0,  # NEW
            'categories_available': [],
            'enum_compatibility_score': 0.0  # NEW
        }
        
        try:
            # Enhanced name analysis with enum focus
            name_categories = ['male_names', 'female_names', 'neutral_names', 
                              'family_names', 'titles', 'epithets', 'creative_names']
            
            all_names = []
            available_categories = []
            
            for category in name_categories:
                if category in culture_data and isinstance(culture_data[category], list):
                    names = culture_data[category]
                    if names:
                        available_categories.append(category)
                        all_names.extend([name for name in names if name and name.strip()])
            
            name_analysis['total_names'] = len(all_names)
            name_analysis['categories_available'] = available_categories
            
            if all_names:
                # Enhanced assessment with enum integration
                name_analysis['name_diversity'] = EnhancedCreativeCultureValidator._assess_name_diversity_enhanced(all_names)
                name_analysis['creative_uniqueness'] = EnhancedCreativeCultureValidator._assess_creative_uniqueness_enhanced(all_names)
                name_analysis['character_fit_potential'] = EnhancedCreativeCultureValidator._assess_character_fit_potential_enhanced(all_names)
                name_analysis['pronunciation_accessibility'] = EnhancedCreativeCultureValidator._assess_pronunciation_accessibility_enhanced(all_names)
                name_analysis['memorable_factor'] = EnhancedCreativeCultureValidator._assess_memorable_factor_enhanced(all_names)
                name_analysis['gaming_table_usability'] = EnhancedCreativeCultureValidator._assess_gaming_table_usability(all_names)
                name_analysis['enum_compatibility_score'] = EnhancedCreativeCultureValidator._assess_name_enum_compatibility(all_names, culture_data)
                
                # Generate enhanced suggestions with enum integration
                if name_analysis['name_diversity'] < 0.7:
                    suggestions.append(EnhancedCreativeValidationIssue(
                        issue_type=EnhancedValidationIssueType.NAME_GENERATION_ENHANCEMENT,
                        severity=CultureValidationSeverity.LOW,
                        category=CultureValidationCategory.CREATIVITY,
                        message="Names could be more diverse for richer character options",
                        creative_suggestions=[
                            "Add names with different syllable patterns", 
                            "Include names with varied cultural flavors",
                            "Consider names suitable for different character archetypes"
                        ],
                        character_impact="More diverse names provide players with more character personality options",
                        target_enhancement_categories=[CultureEnhancementCategory.CHARACTER_NAMES],
                        enhancement_priority=CultureEnhancementPriority.CHARACTER_IMPORTANT,
                        enum_based_recommendations=[
                            "Use CultureNamingStructure.FLEXIBLE for varied patterns",
                            "Consider CultureComplexityLevel.CHARACTER_RICH for more options"
                        ],
                        character_generation_impact="Diverse names support multiple character archetypes and concepts"
                    ))
                    enhancement_categories.append(CultureEnhancementCategory.CHARACTER_NAMES)
                    prioritized_enhancements.append(
                        ("Increase name diversity for character options", CultureEnhancementPriority.CHARACTER_IMPORTANT)
                    )
                
                if name_analysis['gaming_table_usability'] < 0.6:
                    suggestions.append(EnhancedCreativeValidationIssue(
                        issue_type=EnhancedValidationIssueType.GAMING_ENHANCEMENT,
                        severity=CultureValidationSeverity.LOW,
                        category=CultureValidationCategory.GAMING_UTILITY,
                        message="Names could be optimized for gaming table use",
                        creative_suggestions=[
                            "Add shorter nickname variants for quick reference",
                            "Include pronunciation guides for complex names",
                            "Consider syllable patterns that are easy to remember"
                        ],
                        character_impact="Gaming-friendly names improve table flow and player immersion",
                        target_enhancement_categories=[CultureEnhancementCategory.GAMING_UTILITY, CultureEnhancementCategory.PRONUNCIATION],
                        enhancement_priority=CultureEnhancementPriority.GAMING_ESSENTIAL,
                        enum_based_recommendations=[
                            "Target CultureNamingStructure.GAMING_FRIENDLY",
                            "Focus on CultureComplexityLevel.GAMING_READY"
                        ],
                        character_generation_impact="Gaming-optimized names enhance table experience"
                    ))
                    enhancement_categories.extend([CultureEnhancementCategory.GAMING_UTILITY, CultureEnhancementCategory.PRONUNCIATION])
                    prioritized_enhancements.append(
                        ("Optimize names for gaming table usability", CultureEnhancementPriority.GAMING_ESSENTIAL)
                    )
                
                if len(available_categories) < 4:
                    enhancements.append("Consider adding more name categories (titles, epithets, neutral names) for richer character backgrounds")
                    enhancement_categories.append(CultureEnhancementCategory.CHARACTER_NAMES)
                
                # Calculate enhanced name generation score
                name_generation_score = (
                    name_analysis['name_diversity'] * 0.2 +
                    name_analysis['creative_uniqueness'] * 0.2 +
                    name_analysis['character_fit_potential'] * 0.25 +
                    name_analysis['memorable_factor'] * 0.15 +
                    name_analysis['gaming_table_usability'] * 0.2
                )
            else:
                # No names available - critical enhancement opportunity
                opportunities.append(EnhancedCreativeValidationIssue(
                    issue_type=EnhancedValidationIssueType.NAME_GENERATION_ENHANCEMENT,
                    severity=CultureValidationSeverity.HIGH,
                    category=CultureValidationCategory.COMPLETENESS,
                    message="No names available for character generation",
                    creative_suggestions=[
                        "Add at least male and female names for basic character generation",
                        "Include family names for character lineage",
                        "Consider neutral names for inclusive character options"
                    ],
                    character_impact="Players need names to create characters with this cultural background",
                    target_enhancement_categories=[CultureEnhancementCategory.CHARACTER_NAMES],
                    enhancement_priority=CultureEnhancementPriority.CHARACTER_CRITICAL,
                    enum_based_recommendations=[
                        "Start with CultureComplexityLevel.BASIC for essential names",
                        "Use CultureNamingStructure.SIMPLE for initial development"
                    ],
                    character_generation_impact="Names are essential for character creation"
                ))
                enhancement_categories.append(CultureEnhancementCategory.CHARACTER_NAMES)
                prioritized_enhancements.append(
                    ("Add essential character names", CultureEnhancementPriority.CHARACTER_CRITICAL)
                )
                name_generation_score = 0.0
            
            return EnhancedCreativeValidationResult(
                is_usable=len(all_names) > 0,
                creative_quality_score=name_generation_score,
                gaming_usability_score=name_analysis.get('gaming_table_usability', 0.5),
                character_support_score=name_analysis.get('character_fit_potential', 0.5),
                name_generation_score=name_generation_score,
                creative_opportunities=opportunities,
                suggestions=suggestions,
                enhancements=enhancements,
                identified_enhancement_categories=list(set(enhancement_categories)),
                prioritized_enhancements=prioritized_enhancements,
                name_analysis=name_analysis,
                enum_assessment_results={
                    'name_enum_compatibility': name_analysis.get('enum_compatibility_score', 0.5),
                    'gaming_optimization_level': name_analysis.get('gaming_table_usability', 0.5),
                    'character_archetype_support': name_analysis.get('character_fit_potential', 0.5)
                }
            )
            
        except Exception as e:
            raise CultureValidationError(f"Enhanced name generation assessment failed: {str(e)}") from e
    
    @staticmethod
    def assess_character_background_support_enhanced(
        culture_data: Dict[str, Any],
        enhancement_focus: List[CultureEnhancementCategory] = None
    ) -> EnhancedCreativeValidationResult:
        """
        Enhanced assessment of character background support with enum integration.
        
        UPDATED: Evaluates cultural elements for character backstory and personality
        development with enum-based enhancement suggestions.
        
        Args:
            culture_data: Dictionary containing cultural information
            enhancement_focus: Specific enhancement categories to focus on
            
        Returns:
            EnhancedCreativeValidationResult focused on character background support
        """
        opportunities = []
        suggestions = []
        enhancements = []
        enhancement_categories = []
        prioritized_enhancements = []
        
        background_analysis = {
            'cultural_depth': 0.0,
            'character_hook_potential': 0.0,
            'background_variety': 0.0,
            'story_integration_ease': 0.0,
            'roleplay_inspiration': 0.0,
            'background_elements': [],
            'enum_enhancement_compatibility': 0.0,  # NEW
            'character_archetype_support': 0.0,     # NEW
            'gaming_integration_score': 0.0         # NEW
        }
        
        try:
            # Enhanced character background element analysis
            background_elements = []
            character_hooks = 0
            
            # Core cultural elements
            if 'cultural_traits' in culture_data:
                background_elements.append('cultural_traits')
                background_analysis['cultural_depth'] += 0.25
                character_hooks += 1
            
            if 'character_hooks' in culture_data and culture_data['character_hooks']:
                background_elements.append('character_hooks')
                background_analysis['character_hook_potential'] += 0.4
                character_hooks += 2
            
            if 'social_structure' in culture_data or 'hierarchy' in culture_data:
                background_elements.append('social_structure')
                background_analysis['cultural_depth'] += 0.2
                background_analysis['character_hook_potential'] += 0.1
            
            if 'traditions' in culture_data or 'customs' in culture_data:
                background_elements.append('traditions')
                background_analysis['cultural_depth'] += 0.2
                background_analysis['roleplay_inspiration'] += 0.2
            
            if 'values' in culture_data or 'beliefs' in culture_data:
                background_elements.append('values')
                background_analysis['cultural_depth'] += 0.2
                background_analysis['roleplay_inspiration'] += 0.2
            
            if 'occupations' in culture_data or 'professions' in culture_data:
                background_elements.append('occupations')
                background_analysis['background_variety'] += 0.3
                background_analysis['character_archetype_support'] += 0.3
            
            if 'geographical_context' in culture_data or 'environment' in culture_data:
                background_elements.append('geography')
                background_analysis['story_integration_ease'] += 0.2
                background_analysis['gaming_integration_score'] += 0.2
            
            # NEW: Gaming-specific elements
            if 'gaming_notes' in culture_data and culture_data['gaming_notes']:
                background_elements.append('gaming_notes')
                background_analysis['gaming_integration_score'] += 0.3
            
            background_analysis['background_elements'] = background_elements
            
            # Enhanced character hook assessment
            if 'conflicts' in culture_data or 'challenges' in culture_data:
                background_analysis['character_hook_potential'] += 0.3
                character_hooks += 1
            if 'relationships' in culture_data or 'alliances' in culture_data:
                background_analysis['character_hook_potential'] += 0.2
            if 'mysteries' in culture_data or 'secrets' in culture_data:
                background_analysis['character_hook_potential'] += 0.3
                character_hooks += 1
            
            # Enhanced roleplay inspiration assessment
            description_quality = EnhancedCreativeCultureValidator._assess_description_quality_enhanced(culture_data)
            background_analysis['roleplay_inspiration'] += description_quality * 0.5
            
            # NEW: Enum enhancement compatibility assessment
            background_analysis['enum_enhancement_compatibility'] = EnhancedCreativeCultureValidator._assess_background_enum_compatibility(culture_data)
            
            # Generate enhanced suggestions with enum integration
            if background_analysis['cultural_depth'] < 0.5:
                suggestions.append(EnhancedCreativeValidationIssue(
                    issue_type=EnhancedValidationIssueType.CHARACTER_BACKGROUND_GAP,
                    severity=CultureValidationSeverity.LOW,
                    category=CultureValidationCategory.CREATIVITY,
                    message="Culture could use more depth for character backgrounds",
                    creative_suggestions=[
                        "Add cultural traits or values that characters can embody",
                        "Include social customs that affect character behavior",
                        "Describe cultural practices that create character motivations",
                        "Add occupational roles that inspire character concepts"
                    ],
                    character_impact="Richer cultural details give players more material for character development",
                    target_enhancement_categories=[
                        CultureEnhancementCategory.CULTURAL_TRAITS,
                        CultureEnhancementCategory.BACKGROUND_HOOKS
                    ],
                    enhancement_priority=CultureEnhancementPriority.CHARACTER_IMPORTANT,
                    enum_based_recommendations=[
                        "Consider CultureComplexityLevel.CHARACTER_RICH for deeper elements",
                        "Use CultureSourceType.CHARACTER_ARCHETYPAL for inspiration"
                    ],
                    character_generation_impact="Cultural depth provides foundation for diverse character concepts"
                ))
                enhancement_categories.extend([
                    CultureEnhancementCategory.CULTURAL_TRAITS,
                    CultureEnhancementCategory.BACKGROUND_HOOKS
                ])
                prioritized_enhancements.append(
                    ("Add cultural depth for character backgrounds", CultureEnhancementPriority.CHARACTER_IMPORTANT)
                )
            
            if character_hooks < 2:
                suggestions.append(EnhancedCreativeValidationIssue(
                    issue_type=EnhancedValidationIssueType.CHARACTER_BACKGROUND_GAP,
                    severity=CultureValidationSeverity.MEDIUM,
                    category=CultureValidationCategory.CHARACTER_SUPPORT,
                    message="Culture needs more character hooks for backstory development",
                    creative_suggestions=[
                        "Add specific character hooks that connect to cultural elements",
                        "Include cultural conflicts that create character motivations",
                        "Describe cultural mysteries that inspire character goals",
                        "Add relationship dynamics that affect character development"
                    ],
                    character_impact="Character hooks provide players with ready-made backstory elements",
                    target_enhancement_categories=[CultureEnhancementCategory.BACKGROUND_HOOKS],
                    enhancement_priority=CultureEnhancementPriority.CHARACTER_ESSENTIAL,
                    enum_based_recommendations=[
                        "Focus on CultureEnhancementCategory.BACKGROUND_HOOKS",
                        "Target CultureComplexityLevel.NARRATIVE_RICH"
                    ],
                    character_generation_impact="Character hooks are essential for compelling backstories"
                ))
                enhancement_categories.append(CultureEnhancementCategory.BACKGROUND_HOOKS)
                prioritized_enhancements.append(
                    ("Add character hooks for backstory development", CultureEnhancementPriority.CHARACTER_ESSENTIAL)
                )
            
            if background_analysis['gaming_integration_score'] < 0.3:
                enhancements.append("Add gaming notes to help DMs integrate this culture into campaigns")
                enhancement_categories.append(CultureEnhancementCategory.GAMING_UTILITY)
                prioritized_enhancements.append(
                    ("Improve gaming integration", CultureEnhancementPriority.GAMING_HELPFUL)
                )
            
            if not background_elements:
                opportunities.append(EnhancedCreativeValidationIssue(
                    issue_type=EnhancedValidationIssueType.CREATIVE_POTENTIAL,
                    severity=CultureValidationSeverity.MEDIUM,
                    category=CultureValidationCategory.CREATIVITY,
                    message="Culture has great potential for character background development",
                    creative_suggestions=[
                        "Add cultural traits to inspire character personalities",
                        "Include traditional occupations for character backgrounds",
                        "Describe cultural values that drive character motivations",
                        "Add social structures that create character relationships"
                    ],
                    character_impact="These elements would provide rich material for character creation",
                    target_enhancement_categories=[
                        CultureEnhancementCategory.CULTURAL_TRAITS,
                        CultureEnhancementCategory.BACKGROUND_HOOKS,
                        CultureEnhancementCategory.CHARACTER_MOTIVATIONS
                    ],
                    enhancement_priority=CultureEnhancementPriority.CHARACTER_IMPORTANT,
                    enum_based_recommendations=[
                        "Start with CultureComplexityLevel.BASIC and expand",
                        "Consider CultureSourceType.CREATIVE_ORIGINAL for unique elements"
                    ],
                    character_generation_impact="Rich background elements enable diverse character concepts"
                ))
                enhancement_categories.extend([
                    CultureEnhancementCategory.CULTURAL_TRAITS,
                    CultureEnhancementCategory.BACKGROUND_HOOKS,
                    CultureEnhancementCategory.CHARACTER_MOTIVATIONS
                ])
            
            # Calculate enhanced character support score
            character_support_score = (
                background_analysis['cultural_depth'] * 0.25 +
                background_analysis['character_hook_potential'] * 0.3 +
                background_analysis['background_variety'] * 0.2 +
                background_analysis['roleplay_inspiration'] * 0.15 +
                background_analysis['gaming_integration_score'] * 0.1
            )
            
            return EnhancedCreativeValidationResult(
                is_usable=True,  # Culture is always usable for character backgrounds
                creative_quality_score=character_support_score,
                gaming_usability_score=background_analysis['gaming_integration_score'],
                character_support_score=character_support_score,
                name_generation_score=0.5,  # Not the focus of this assessment
                creative_opportunities=opportunities,
                suggestions=suggestions,
                enhancements=enhancements,
                identified_enhancement_categories=list(set(enhancement_categories)),
                prioritized_enhancements=prioritized_enhancements,
                character_background_analysis=background_analysis,
                enum_assessment_results={
                    'background_enum_compatibility': background_analysis['enum_enhancement_compatibility'],
                    'character_archetype_support': background_analysis['character_archetype_support'],
                    'gaming_integration_level': background_analysis['gaming_integration_score']
                },
                metadata={'background_elements_found': len(background_elements), 'character_hooks_count': character_hooks}
            )
            
        except Exception as e:
            raise CultureValidationError(f"Enhanced character background assessment failed: {str(e)}") from e
    
    @staticmethod
    def assess_gaming_usability_enhanced(
        culture_data: Dict[str, Any],
        enhancement_focus: List[CultureEnhancementCategory] = None
    ) -> EnhancedCreativeValidationResult:
        """
        Enhanced assessment of gaming usability with enum integration.
        
        UPDATED: Evaluates practical gaming concerns with enum-based optimization
        while maintaining creative freedom and encouraging enhancement.
        
        Args:
            culture_data: Dictionary containing culture data
            enhancement_focus: Specific enhancement categories to focus on
            
        Returns:
            EnhancedCreativeValidationResult focused on gaming usability
        """
        opportunities = []
        suggestions = []
        enhancements = []
        enhancement_categories = []
        prioritized_enhancements = []
        
        gaming_analysis = {
            'table_friendliness': 0.0,
            'dm_usability': 0.0,
            'player_accessibility': 0.0,
            'session_integration': 0.0,
            'reference_ease': 0.0,
            'gaming_aids': [],
            'pronunciation_optimization': 0.0,  # NEW
            'character_creation_efficiency': 0.0,  # NEW
            'campaign_integration_score': 0.0,     # NEW
            'enum_gaming_compatibility': 0.0       # NEW
        }
        
        try:
            # Enhanced gaming-specific analysis
            all_names = EnhancedCreativeCultureValidator._collect_all_names(culture_data)
            
            if all_names:
                # Enhanced gaming-specific name analysis
                pronunciation_score = EnhancedCreativeCultureValidator._assess_gaming_pronunciation_enhanced(all_names)
                length_score = EnhancedCreativeCultureValidator._assess_gaming_name_length_enhanced(all_names)
                distinctiveness_score = EnhancedCreativeCultureValidator._assess_name_distinctiveness_enhanced(all_names)
                memorability_score = EnhancedCreativeCultureValidator._assess_gaming_memorability(all_names)
                
                gaming_analysis['table_friendliness'] = (
                    pronunciation_score * 0.3 + length_score * 0.25 + 
                    distinctiveness_score * 0.25 + memorability_score * 0.2
                )
                gaming_analysis['pronunciation_optimization'] = pronunciation_score
                
                # Enhanced suggestions for gaming optimization
                if pronunciation_score < 0.6:
                    suggestions.append(EnhancedCreativeValidationIssue(
                        issue_type=EnhancedValidationIssueType.GAMING_ENHANCEMENT,
                        severity=CultureValidationSeverity.LOW,
                        category=CultureValidationCategory.GAMING_UTILITY,
                        message="Some names might be challenging to pronounce during play",
                        creative_suggestions=[
                            "Consider adding phonetic guides for complex names",
                            "Include simpler nickname variants for table use",
                            "Add pronunciation tips in parentheses",
                            "Consider syllable patterns common in gaming"
                        ],
                        character_impact="Easier names help players stay immersed in character roleplay",
                        target_enhancement_categories=[
                            CultureEnhancementCategory.PRONUNCIATION,
                            CultureEnhancementCategory.GAMING_UTILITY
                        ],
                        enhancement_priority=CultureEnhancementPriority.GAMING_ESSENTIAL,
                        enum_based_recommendations=[
                            "Target CultureNamingStructure.GAMING_FRIENDLY",
                            "Consider CultureComplexityLevel.GAMING_READY"
                        ],
                        character_generation_impact="Pronunciation ease improves table flow and player engagement"
                    ))
                    enhancement_categories.extend([
                        CultureEnhancementCategory.PRONUNCIATION,
                        CultureEnhancementCategory.GAMING_UTILITY
                    ])
                    prioritized_enhancements.append(
                        ("Optimize name pronunciation for gaming", CultureEnhancementPriority.GAMING_ESSENTIAL)
                    )
                
                if length_score < 0.7:
                    enhancements.append("Consider shorter name variants for quicker table reference")
                    enhancement_categories.append(CultureEnhancementCategory.GAMING_UTILITY)
            
            # Enhanced gaming aids assessment
            gaming_aids = []
            
            if 'pronunciation_guide' in culture_data and culture_data['pronunciation_guide']:
                gaming_aids.append('pronunciation_guide')
                gaming_analysis['reference_ease'] += 0.25
            
            if 'gaming_notes' in culture_data and culture_data['gaming_notes']:
                gaming_aids.append('gaming_notes')
                gaming_analysis['dm_usability'] += 0.3
                gaming_analysis['campaign_integration_score'] += 0.3
            
            if 'quick_reference' in culture_data or 'summary' in culture_data:
                gaming_aids.append('quick_reference')
                gaming_analysis['dm_usability'] += 0.3
                gaming_analysis['reference_ease'] += 0.2
            
            if 'naming_examples' in culture_data and culture_data['naming_examples']:
                gaming_aids.append('naming_examples')
                gaming_analysis['dm_usability'] += 0.2
                gaming_analysis['character_creation_efficiency'] += 0.3
            
            if 'character_integration' in culture_data or 'character_hooks' in culture_data:
                gaming_aids.append('character_integration')
                gaming_analysis['session_integration'] += 0.4
                gaming_analysis['character_creation_efficiency'] += 0.2
            
            gaming_analysis['gaming_aids'] = gaming_aids
            
            # NEW: Enhanced enum gaming compatibility assessment
            gaming_analysis['enum_gaming_compatibility'] = EnhancedCreativeCultureValidator._assess_gaming_enum_compatibility(culture_data)
            
            # Enhanced gaming enhancement suggestions
            if not gaming_aids or len(gaming_aids) < 2:
                opportunities.append(EnhancedCreativeValidationIssue(
                    issue_type=EnhancedValidationIssueType.GAMING_ENHANCEMENT,
                    severity=CultureValidationSeverity.LOW,
                    category=CultureValidationCategory.GAMING_UTILITY,
                    message="Culture could benefit from gaming convenience features",
                    creative_suggestions=[
                        "Add a quick reference summary for DMs",
                        "Include example character concepts with cultural backgrounds",
                        "Provide naming pattern examples for improvisation",
                        "Add gaming notes for campaign integration",
                        "Include pronunciation guides for complex terms"
                    ],
                    character_impact="Gaming aids help DMs and players use the culture more effectively",
                    target_enhancement_categories=[CultureEnhancementCategory.GAMING_UTILITY],
                    enhancement_priority=CultureEnhancementPriority.GAMING_HELPFUL,
                    enum_based_recommendations=[
                        "Focus on CultureComplexityLevel.GAMING_READY",
                        "Consider CultureEnhancementCategory.GAMING_UTILITY priority"
                    ],
                    character_generation_impact="Gaming utilities improve table experience and character creation efficiency"
                ))
                enhancement_categories.append(CultureEnhancementCategory.GAMING_UTILITY)
                prioritized_enhancements.append(
                    ("Add gaming convenience features", CultureEnhancementPriority.GAMING_HELPFUL)
                )
            
            if gaming_analysis['character_creation_efficiency'] < 0.4:
                suggestions.append(EnhancedCreativeValidationIssue(
                    issue_type=EnhancedValidationIssueType.CHARACTER_GENERATION_OPTIMIZATION,
                    severity=CultureValidationSeverity.LOW,
                    category=CultureValidationCategory.CHARACTER_SUPPORT,
                    message="Culture could better support efficient character creation",
                    creative_suggestions=[
                        "Add example character archetypes for quick inspiration",
                        "Include ready-to-use character background elements",
                        "Provide cultural motivation examples for character development",
                        "Add social role examples for character positioning"
                    ],
                    character_impact="Efficient character creation tools help players develop characters quickly",
                    target_enhancement_categories=[
                        CultureEnhancementCategory.CHARACTER_HOOKS,
                        CultureEnhancementCategory.GAMING_UTILITY
                    ],
                    enhancement_priority=CultureEnhancementPriority.CHARACTER_HELPFUL,
                    enum_based_recommendations=[
                        "Target CultureComplexityLevel.CHARACTER_RICH",
                        "Use CultureEnhancementCategory.CHARACTER_HOOKS"
                    ],
                    character_generation_impact="Character creation efficiency improves player experience"
                ))
                enhancement_categories.extend([
                    CultureEnhancementCategory.CHARACTER_HOOKS,
                    CultureEnhancementCategory.GAMING_UTILITY
                ])
            
            # Calculate enhanced gaming usability score
            gaming_score = (
                gaming_analysis['table_friendliness'] * 0.25 +
                gaming_analysis['dm_usability'] * 0.2 +
                gaming_analysis['player_accessibility'] * 0.2 +
                gaming_analysis['reference_ease'] * 0.15 +
                gaming_analysis['character_creation_efficiency'] * 0.2
            )
            
            return EnhancedCreativeValidationResult(
                is_usable=True,  # Almost all cultures are usable for gaming
                creative_quality_score=gaming_score,
                gaming_usability_score=gaming_score,
                character_support_score=gaming_analysis['character_creation_efficiency'],
                name_generation_score=gaming_analysis['table_friendliness'],
                creative_opportunities=opportunities,
                suggestions=suggestions,
                enhancements=enhancements,
                identified_enhancement_categories=list(set(enhancement_categories)),
                prioritized_enhancements=prioritized_enhancements,
                gaming_analysis=gaming_analysis,
                enum_assessment_results={
                    'gaming_enum_compatibility': gaming_analysis['enum_gaming_compatibility'],
                    'pronunciation_optimization': gaming_analysis['pronunciation_optimization'],
                    'character_creation_efficiency': gaming_analysis['character_creation_efficiency']
                },
                metadata={'gaming_aids_count': len(gaming_aids)}
            )
            
        except Exception as e:
            raise CultureValidationError(f"Enhanced gaming usability assessment failed: {str(e)}") from e
    
    @staticmethod
    def assess_creative_potential_enhanced(
        culture_data: Dict[str, Any],
        enhancement_focus: List[CultureEnhancementCategory] = None
    ) -> EnhancedCreativeValidationResult:
        """
        Enhanced assessment of creative potential with enum integration.
        
        UPDATED: Evaluates how well culture inspires creativity with enum-based
        enhancement suggestions and character generation focus.
        
        Args:
            culture_data: Dictionary containing culture data
            enhancement_focus: Specific enhancement categories to focus on
            
        Returns:
            EnhancedCreativeValidationResult focused on creative potential
        """
        opportunities = []
        suggestions = []
        enhancements = []
        enhancement_categories = []
        prioritized_enhancements = []
        
        creative_analysis = {
            'inspiration_factor': 0.0,
            'concept_diversity': 0.0,
            'storytelling_hooks': 0.0,
            'creative_flexibility': 0.0,
            'uniqueness_factor': 0.0,
            'creative_elements': [],
            'character_archetype_support': 0.0,  # NEW
            'narrative_depth_potential': 0.0,    # NEW
            'creative_freedom_score': 0.0,       # NEW
            'enum_creative_compatibility': 0.0   # NEW
        }
        
        try:
            # Enhanced creative elements assessment
            creative_elements = []
            narrative_hooks = 0
            
            # Core creative elements
            if 'unique_features' in culture_data or 'distinctive_traits' in culture_data:
                creative_elements.append('unique_features')
                creative_analysis['uniqueness_factor'] += 0.4
                creative_analysis['inspiration_factor'] += 0.2
            
            if 'mysteries' in culture_data or 'legends' in culture_data:
                creative_elements.append('mysteries')
                creative_analysis['storytelling_hooks'] += 0.3
                narrative_hooks += 1
            
            if 'conflicts' in culture_data or 'tensions' in culture_data:
                creative_elements.append('conflicts')
                creative_analysis['storytelling_hooks'] += 0.3
                narrative_hooks += 1
            
            if 'philosophy' in culture_data or 'worldview' in culture_data:
                creative_elements.append('philosophy')
                creative_analysis['concept_diversity'] += 0.3
                creative_analysis['narrative_depth_potential'] += 0.2
            
            if 'arts' in culture_data or 'crafts' in culture_data:
                creative_elements.append('arts')
                creative_analysis['concept_diversity'] += 0.2
                creative_analysis['character_archetype_support'] += 0.2
            
            if 'magic_relation' in culture_data or 'supernatural' in culture_data:
                creative_elements.append('supernatural')
                creative_analysis['inspiration_factor'] += 0.3
                creative_analysis['uniqueness_factor'] += 0.2
            
            # NEW: Character-focused creative elements
            if 'character_archetypes' in culture_data:
                creative_elements.append('character_archetypes')
                creative_analysis['character_archetype_support'] += 0.4
            
            if 'cultural_motivations' in culture_data:
                creative_elements.append('cultural_motivations')
                creative_analysis['concept_diversity'] += 0.3
            
            creative_analysis['creative_elements'] = creative_elements
            
            # Enhanced naming creativity assessment
            all_names = EnhancedCreativeCultureValidator._collect_all_names(culture_data)
            if all_names:
                naming_creativity = EnhancedCreativeCultureValidator._assess_naming_creativity_enhanced(all_names)
                creative_analysis['inspiration_factor'] += naming_creativity * 0.3
            
            # Enhanced flexibility assessment
            flexibility_score = EnhancedCreativeCultureValidator._assess_character_concept_flexibility_enhanced(culture_data)
            creative_analysis['creative_flexibility'] = flexibility_score
            
            # NEW: Creative freedom assessment
            creative_analysis['creative_freedom_score'] = EnhancedCreativeCultureValidator._assess_creative_freedom_potential(culture_data)
            
            # NEW: Enum creative compatibility
            creative_analysis['enum_creative_compatibility'] = EnhancedCreativeCultureValidator._assess_creative_enum_compatibility(culture_data)
            
            # Enhanced creative enhancement suggestions
            if creative_analysis['storytelling_hooks'] < 0.4:
                suggestions.append(EnhancedCreativeValidationIssue(
                    issue_type=EnhancedValidationIssueType.CREATIVE_OPPORTUNITY,
                    severity=CultureValidationSeverity.LOW,
                    category=CultureValidationCategory.CREATIVITY,
                    message="Culture has potential for more storytelling hooks",
                    creative_suggestions=[
                        "Add cultural mysteries or legends for character backstories",
                        "Include internal conflicts that create character motivations",
                        "Describe unique cultural practices that spark adventure ideas",
                        "Add cultural tensions that generate character drama",
                        "Include philosophical dilemmas that challenge characters"
                    ],
                    character_impact="Story hooks give characters interesting backgrounds and motivations",
                    target_enhancement_categories=[
                        CultureEnhancementCategory.NARRATIVE_DEPTH,
                        CultureEnhancementCategory.CHARACTER_MOTIVATIONS
                    ],
                    enhancement_priority=CultureEnhancementPriority.NARRATIVE_HELPFUL,
                    enum_based_recommendations=[
                        "Consider CultureComplexityLevel.NARRATIVE_RICH for story elements",
                        "Use CultureSourceType.CREATIVE_MYTHOLOGICAL for inspiration"
                    ],
                    character_generation_impact="Storytelling elements provide rich foundation for character development"
                ))
                enhancement_categories.extend([
                    CultureEnhancementCategory.NARRATIVE_DEPTH,
                    CultureEnhancementCategory.CHARACTER_MOTIVATIONS
                ])
                prioritized_enhancements.append(
                    ("Add storytelling hooks for character narratives", CultureEnhancementPriority.NARRATIVE_HELPFUL)
                )
            
            if creative_analysis['character_archetype_support'] < 0.4:
                suggestions.append(EnhancedCreativeValidationIssue(
                    issue_type=EnhancedValidationIssueType.CHARACTER_GENERATION_OPTIMIZATION,
                    severity=CultureValidationSeverity.LOW,
                    category=CultureValidationCategory.CHARACTER_SUPPORT,
                    message="Culture could better support diverse character archetypes",
                    creative_suggestions=[
                        "Add examples of different character roles within the culture",
                        "Include diverse occupational or social roles",
                        "Describe how different personality types fit into the culture",
                        "Add cultural paths that support various character classes",
                        "Include generational or social differences for character variety"
                    ],
                    character_impact="Archetype support helps players create diverse characters from the same culture",
                    target_enhancement_categories=[
                        CultureEnhancementCategory.CHARACTER_MOTIVATIONS,
                        CultureEnhancementCategory.ROLEPLAY_ELEMENTS
                    ],
                    enhancement_priority=CultureEnhancementPriority.CHARACTER_HELPFUL,
                    enum_based_recommendations=[
                        "Target CultureComplexityLevel.CHARACTER_RICH",
                        "Consider CultureSourceType.CHARACTER_ARCHETYPAL"
                    ],
                    character_generation_impact="Archetype diversity enables varied character concepts from one culture"
                ))
                enhancement_categories.extend([
                    CultureEnhancementCategory.CHARACTER_MOTIVATIONS,
                    CultureEnhancementCategory.ROLEPLAY_ELEMENTS
                ])
            
            if creative_analysis['concept_diversity'] < 0.4:
                enhancements.append("Consider adding diverse cultural roles and perspectives for varied character concepts")
                enhancement_categories.append(CultureEnhancementCategory.ROLEPLAY_ELEMENTS)
                prioritized_enhancements.append(
                    ("Increase concept diversity", CultureEnhancementPriority.CHARACTER_HELPFUL)
                )
            
            if not creative_elements or len(creative_elements) < 3:
                opportunities.append(EnhancedCreativeValidationIssue(
                    issue_type=EnhancedValidationIssueType.CREATIVE_POTENTIAL,
                    severity=CultureValidationSeverity.LOW,
                    category=CultureValidationCategory.CREATIVITY,
                    message="Culture shows great potential for creative enhancement",
                    creative_suggestions=[
                        "Add unique cultural features that make characters interesting",
                        "Include cultural values that create character motivations",
                        "Describe cultural practices that inspire character concepts",
                        "Add artistic or craft traditions for character backgrounds",
                        "Include philosophical or spiritual elements for character depth"
                    ],
                    character_impact="Creative elements help players develop unique and memorable characters",
                    target_enhancement_categories=[
                        CultureEnhancementCategory.CULTURAL_TRAITS,
                        CultureEnhancementCategory.ROLEPLAY_ELEMENTS,
                        CultureEnhancementCategory.NARRATIVE_DEPTH
                    ],
                    enhancement_priority=CultureEnhancementPriority.CHARACTER_IMPORTANT,
                    enum_based_recommendations=[
                        "Start with CultureComplexityLevel.BASIC and expand gradually",
                        "Consider CultureSourceType.CREATIVE_ORIGINAL for unique elements"
                    ],
                    character_generation_impact="Rich creative elements enable unique character concepts and development"
                ))
                enhancement_categories.extend([
                    CultureEnhancementCategory.CULTURAL_TRAITS,
                    CultureEnhancementCategory.ROLEPLAY_ELEMENTS,
                    CultureEnhancementCategory.NARRATIVE_DEPTH
                ])
            
            # Calculate enhanced creative potential score
            creative_quality_score = (
                creative_analysis['inspiration_factor'] * 0.2 +
                creative_analysis['concept_diversity'] * 0.2 +
                creative_analysis['storytelling_hooks'] * 0.2 +
                creative_analysis['creative_flexibility'] * 0.2 +
                creative_analysis['character_archetype_support'] * 0.2
            )
            
            return EnhancedCreativeValidationResult(
                is_usable=True,  # All cultures have creative potential
                creative_quality_score=creative_quality_score,
                gaming_usability_score=creative_analysis['creative_flexibility'],
                character_support_score=creative_analysis['character_archetype_support'],
                name_generation_score=creative_analysis['inspiration_factor'],
                creative_opportunities=opportunities,
                suggestions=suggestions,
                enhancements=enhancements,
                identified_enhancement_categories=list(set(enhancement_categories)),
                prioritized_enhancements=prioritized_enhancements,
                creative_potential_analysis=creative_analysis,
                enum_assessment_results={
                    'creative_enum_compatibility': creative_analysis['enum_creative_compatibility'],
                    'creative_freedom_score': creative_analysis['creative_freedom_score'],
                    'narrative_depth_potential': creative_analysis['narrative_depth_potential']
                },
                metadata={
                    'creative_elements_count': len(creative_elements),
                    'narrative_hooks_count': narrative_hooks
                }
            )
            
        except Exception as e:
            raise CultureValidationError(f"Enhanced creative potential assessment failed: {str(e)}") from e
    
    # ============================================================================
    # NEW: ENUM-BASED ASSESSMENT METHODS
    # ============================================================================
    
    @staticmethod
    def assess_enum_compatibility(culture_data: Dict[str, Any]) -> EnhancedCreativeValidationResult:
        """
        Assess culture compatibility with enhanced enum system.
        
        NEW: Evaluates how well culture aligns with enhanced enum capabilities
        and identifies opportunities for enum-based improvements.
        
        Args:
            culture_data: Dictionary containing culture information
            
        Returns:
            EnhancedCreativeValidationResult focused on enum compatibility
        """
        opportunities = []
        suggestions = []
        enhancements = []
        enhancement_categories = []
        prioritized_enhancements = []
        
        enum_assessment = {
            'enum_integration_score': 0.0,
            'enhancement_category_coverage': 0.0,
            'preset_system_readiness': 0.0,
            'character_generation_optimization': 0.0,
            'creative_validation_compliance': 0.0,
            'detected_enum_patterns': [],
            'missing_enum_opportunities': [],
            'compatibility_breakdown': {}
        }
        
        try:
            # Assess enum pattern detection
            detected_patterns = []
            
            # Check for naming structure patterns
            all_names = EnhancedCreativeCultureValidator._collect_all_names(culture_data)
            if all_names:
                inferred_naming = EnhancedCreativeCultureValidator._infer_naming_structure(all_names)
                detected_patterns.append(f"naming_structure:{inferred_naming.value}")
                enum_assessment['enum_integration_score'] += 0.2
            
            # Check for complexity indicators
            complexity_level = EnhancedCreativeCultureValidator._infer_complexity_level(culture_data)
            detected_patterns.append(f"complexity_level:{complexity_level.value}")
            enum_assessment['character_generation_optimization'] = complexity_level.character_creation_readiness
            
            # Check for authenticity indicators
            authenticity_level = EnhancedCreativeCultureValidator._infer_authenticity_level(culture_data)
            detected_patterns.append(f"authenticity_level:{authenticity_level.value}")
            enum_assessment['enum_integration_score'] += authenticity_level.gaming_utility_score * 0.3
            
            # Check for creativity indicators
            creativity_level = EnhancedCreativeCultureValidator._infer_creativity_level(culture_data)
            detected_patterns.append(f"creativity_level:{creativity_level.value}")
            enum_assessment['creative_validation_compliance'] = creativity_level.creative_freedom_percentage / 100
            
            enum_assessment['detected_enum_patterns'] = detected_patterns
            
            # Assess enhancement category coverage
            covered_categories = []
            missing_opportunities = []
            
            # Check character names coverage
            if all_names:
                covered_categories.append(CultureEnhancementCategory.CHARACTER_NAMES)
            else:
                missing_opportunities.append("character_names_missing")
                suggestions.append(EnhancedCreativeValidationIssue(
                    issue_type=EnhancedValidationIssueType.ENHANCEMENT_CATEGORY_OPPORTUNITY,
                    severity=CultureValidationSeverity.HIGH,
                    category=CultureValidationCategory.COMPLETENESS,
                    message="Culture missing character names for enum optimization",
                    creative_suggestions=[
                        "Add basic male and female names to enable enum-based name generation",
                        "Include family names for enhanced character lineage support",
                        "Consider neutral names for inclusive character options"
                    ],
                    character_impact="Names are essential for enum-based character generation",
                    target_enhancement_categories=[CultureEnhancementCategory.CHARACTER_NAMES],
                    enhancement_priority=CultureEnhancementPriority.CHARACTER_CRITICAL,
                    enum_based_recommendations=[
                        "Start with CultureNamingStructure.SIMPLE",
                        "Target CultureComplexityLevel.BASIC for initial development"
                    ],
                    character_generation_impact="Essential for enum-based character name generation"
                ))
                enhancement_categories.append(CultureEnhancementCategory.CHARACTER_NAMES)
                prioritized_enhancements.append(
                    ("Add character names for enum compatibility", CultureEnhancementPriority.CHARACTER_CRITICAL)
                )
            
            # Check cultural traits coverage
            if 'cultural_traits' in culture_data or 'values' in culture_data or 'beliefs' in culture_data:
                covered_categories.append(CultureEnhancementCategory.CULTURAL_TRAITS)
            else:
                missing_opportunities.append("cultural_traits_missing")
                enhancements.append("Add cultural traits to enhance enum-based character background generation")
                enhancement_categories.append(CultureEnhancementCategory.CULTURAL_TRAITS)
            
            # Check background hooks coverage
            if 'character_hooks' in culture_data or 'conflicts' in culture_data or 'mysteries' in culture_data:
                covered_categories.append(CultureEnhancementCategory.BACKGROUND_HOOKS)
            else:
                missing_opportunities.append("background_hooks_missing")
                enhancement_categories.append(CultureEnhancementCategory.BACKGROUND_HOOKS)
            
            # Check gaming utility coverage
            gaming_elements = ['gaming_notes', 'pronunciation_guide', 'quick_reference', 'naming_examples']
            if any(elem in culture_data for elem in gaming_elements):
                covered_categories.append(CultureEnhancementCategory.GAMING_UTILITY)
            else:
                missing_opportunities.append("gaming_utility_missing")
                opportunities.append(EnhancedCreativeValidationIssue(
                    issue_type=EnhancedValidationIssueType.ENUM_SCORING_ENHANCEMENT,
                    severity=CultureValidationSeverity.LOW,
                    category=CultureValidationCategory.GAMING_UTILITY,
                    message="Culture could benefit from gaming utility enhancements for better enum integration",
                    creative_suggestions=[
                        "Add gaming notes for DM convenience",
                        "Include pronunciation guides for complex names",
                        "Provide quick reference summaries for table use"
                    ],
                    character_impact="Gaming utilities improve enum-based table experience",
                    target_enhancement_categories=[CultureEnhancementCategory.GAMING_UTILITY],
                    enhancement_priority=CultureEnhancementPriority.GAMING_HELPFUL,
                    enum_based_recommendations=[
                        "Focus on CultureComplexityLevel.GAMING_READY",
                        "Consider CultureNamingStructure.GAMING_FRIENDLY"
                    ],
                    character_generation_impact="Enhanced gaming integration improves enum utilization"
                ))
                enhancement_categories.append(CultureEnhancementCategory.GAMING_UTILITY)
            
            enum_assessment['missing_enum_opportunities'] = missing_opportunities
            enum_assessment['enhancement_category_coverage'] = len(covered_categories) / len(CultureEnhancementCategory) if CultureEnhancementCategory else 0.5
            
            # Assess preset system readiness
            preset_readiness_score = 0.0
            if all_names and len(all_names) >= 10:
                preset_readiness_score += 0.3
            if 'cultural_traits' in culture_data:
                preset_readiness_score += 0.25
            if any(elem in culture_data for elem in gaming_elements):
                preset_readiness_score += 0.25
            if 'character_hooks' in culture_data:
                preset_readiness_score += 0.2
            
            enum_assessment['preset_system_readiness'] = preset_readiness_score
            
            # Calculate overall enum compatibility score
            enum_compatibility_score = (
                enum_assessment['enum_integration_score'] * 0.3 +
                enum_assessment['enhancement_category_coverage'] * 0.25 +
                enum_assessment['preset_system_readiness'] * 0.25 +
                enum_assessment['character_generation_optimization'] * 0.2
            )
            
            # Generate comprehensive compatibility breakdown
            enum_assessment['compatibility_breakdown'] = {
                'naming_compatibility': EnhancedCreativeCultureValidator._assess_name_enum_compatibility(all_names, culture_data) if all_names else 0.0,
                'complexity_alignment': complexity_level.character_creation_readiness,
                'authenticity_gaming_score': authenticity_level.gaming_utility_score,
                'creativity_freedom_score': creativity_level.creative_freedom_percentage / 100,
                'enhancement_opportunities': len(missing_opportunities),
                'covered_categories_count': len(covered_categories),
                'total_categories_available': len(CultureEnhancementCategory) if CultureEnhancementCategory else 10
            }
            
            return EnhancedCreativeValidationResult(
                is_usable=True,  # Enum compatibility doesn't affect basic usability
                creative_quality_score=enum_compatibility_score,
                gaming_usability_score=enum_assessment['preset_system_readiness'],
                character_support_score=enum_assessment['character_generation_optimization'],
                name_generation_score=enum_assessment['enum_integration_score'],
                creative_opportunities=opportunities,
                suggestions=suggestions,
                enhancements=enhancements,
                identified_enhancement_categories=list(set(enhancement_categories)),
                prioritized_enhancements=prioritized_enhancements,
                enum_assessment_results=enum_assessment,
                metadata={
                    'enum_focus': 'compatibility_assessment',
                    'detected_patterns_count': len(detected_patterns),
                    'missing_opportunities_count': len(missing_opportunities),
                    'covered_categories_count': len(covered_categories)
                }
            )
            
        except Exception as e:
            raise CultureValidationError(f"Enum compatibility assessment failed: {str(e)}") from e
    
    @staticmethod
    def assess_preset_compatibility(
        culture_data: Dict[str, Any], 
        target_preset: Optional[str] = None
    ) -> EnhancedCreativeValidationResult:
        """
        Assess culture compatibility with character culture presets.
        
        NEW: Evaluates how well culture works with predefined presets
        and suggests improvements for better preset integration.
        
        Args:
            culture_data: Dictionary containing culture information
            target_preset: Optional specific preset to assess against
            
        Returns:
            EnhancedCreativeValidationResult focused on preset compatibility
        """
        opportunities = []
        suggestions = []
        enhancements = []
        enhancement_categories = []
        prioritized_enhancements = []
        
        preset_analysis = {
            'overall_preset_compatibility': 0.0,
            'specific_preset_scores': {},
            'recommended_presets': [],
            'preset_optimization_suggestions': [],
            'character_generation_readiness_by_preset': {}
        }
        
        try:
            # Get available presets from CHARACTER_CULTURE_PRESETS
            available_presets = list(CHARACTER_CULTURE_PRESETS.keys()) if CHARACTER_CULTURE_PRESETS else [
                'gaming_optimized', 'creative_focused', 'character_rich', 'narrative_deep', 'table_friendly'
            ]
            
            preset_scores = {}
            
            for preset_name in available_presets:
                preset_config = CHARACTER_CULTURE_PRESETS.get(preset_name, {}) if CHARACTER_CULTURE_PRESETS else {}
                
                # Assess compatibility with this preset
                compatibility_score = EnhancedCreativeCultureValidator._assess_single_preset_compatibility(
                    culture_data, preset_name, preset_config
                )
                preset_scores[preset_name] = compatibility_score
                
                # Generate readiness assessment for this preset
                preset_analysis['character_generation_readiness_by_preset'][preset_name] = {
                    'compatibility_score': compatibility_score,
                    'ready_for_use': compatibility_score >= 0.6,
                    'enhancement_needed': compatibility_score < 0.8,
                    'critical_issues': compatibility_score < 0.4
                }
            
            preset_analysis['specific_preset_scores'] = preset_scores
            
            # Determine overall compatibility and recommendations
            if preset_scores:
                preset_analysis['overall_preset_compatibility'] = sum(preset_scores.values()) / len(preset_scores)
                
                # Find best matching presets
                sorted_presets = sorted(preset_scores.items(), key=lambda x: x[1], reverse=True)
                preset_analysis['recommended_presets'] = [name for name, score in sorted_presets[:3] if score >= 0.5]
            
            # Focus on target preset if specified
            if target_preset and target_preset in preset_scores:
                target_score = preset_scores[target_preset]
                
                if target_score < 0.6:
                    suggestions.append(EnhancedCreativeValidationIssue(
                        issue_type=EnhancedValidationIssueType.PRESET_COMPATIBILITY_IMPROVEMENT,
                        severity=CultureValidationSeverity.MEDIUM,
                        category=CultureValidationCategory.CHARACTER_SUPPORT,
                        message=f"Culture needs improvements for {target_preset} preset compatibility",
                        creative_suggestions=EnhancedCreativeCultureValidator._get_preset_improvement_suggestions(target_preset),
                        character_impact=f"Better {target_preset} compatibility improves character generation experience",
                        target_enhancement_categories=EnhancedCreativeCultureValidator._get_preset_enhancement_categories(target_preset),
                        enhancement_priority=CultureEnhancementPriority.CHARACTER_IMPORTANT,
                        enum_based_recommendations=[
                            f"Optimize for {target_preset} preset requirements",
                            "Focus on preset-specific enhancement categories"
                        ],
                        preset_compatibility_notes=[f"Target preset: {target_preset}", f"Current score: {target_score:.2f}"],
                        character_generation_impact=f"Improved {target_preset} compatibility enhances character creation workflow"
                    ))
                    enhancement_categories.extend(EnhancedCreativeCultureValidator._get_preset_enhancement_categories(target_preset))
                    prioritized_enhancements.append(
                        (f"Improve {target_preset} preset compatibility", CultureEnhancementPriority.CHARACTER_IMPORTANT)
                    )
            
            # General preset optimization suggestions
            if preset_analysis['overall_preset_compatibility'] < 0.7:
                opportunities.append(EnhancedCreativeValidationIssue(
                    issue_type=EnhancedValidationIssueType.PRESET_COMPATIBILITY_IMPROVEMENT,
                    severity=CultureValidationSeverity.LOW,
                    category=CultureValidationCategory.GAMING_UTILITY,
                    message="Culture could benefit from preset system optimization",
                    creative_suggestions=[
                        "Add elements that work well across multiple presets",
                        "Include gaming conveniences for table-friendly presets",
                        "Enhance creative elements for creative-focused presets",
                        "Add character hooks for character-rich presets"
                    ],
                    character_impact="Better preset compatibility improves culture versatility",
                    target_enhancement_categories=[
                        CultureEnhancementCategory.GAMING_UTILITY,
                        CultureEnhancementCategory.CHARACTER_NAMES,
                        CultureEnhancementCategory.BACKGROUND_HOOKS
                    ],
                    enhancement_priority=CultureEnhancementPriority.GAMING_HELPFUL,
                    enum_based_recommendations=[
                        "Consider CultureComplexityLevel.GAMING_READY for broad compatibility",
                        "Use CultureNamingStructure.FLEXIBLE for preset versatility"
                    ],
                    character_generation_impact="Preset optimization improves culture utility across different play styles"
                ))
                enhancement_categories.extend([
                    CultureEnhancementCategory.GAMING_UTILITY,
                    CultureEnhancementCategory.CHARACTER_NAMES,
                    CultureEnhancementCategory.BACKGROUND_HOOKS
                ])
            
            # Generate preset optimization suggestions
            preset_analysis['preset_optimization_suggestions'] = [
                f"Best fit presets: {', '.join(preset_analysis['recommended_presets'])}",
                f"Overall compatibility: {preset_analysis['overall_preset_compatibility']:.1%}",
                "Consider adding gaming utilities for better table-friendly preset support",
                "Enhance character hooks for improved character-rich preset compatibility"
            ]
            
            return EnhancedCreativeValidationResult(
                is_usable=True,  # Preset compatibility doesn't affect basic usability
                creative_quality_score=preset_analysis['overall_preset_compatibility'],
                gaming_usability_score=preset_scores.get('gaming_optimized', 0.5),
                character_support_score=preset_scores.get('character_rich', 0.5),
                name_generation_score=preset_scores.get('table_friendly', 0.5),
                creative_opportunities=opportunities,
                suggestions=suggestions,
                enhancements=enhancements,
                identified_enhancement_categories=list(set(enhancement_categories)),
                prioritized_enhancements=prioritized_enhancements,
                preset_compatibility_analysis=preset_analysis,
                metadata={
                    'preset_focus': 'compatibility_assessment',
                    'target_preset': target_preset,
                    'presets_evaluated': len(preset_scores),
                    'recommended_presets_count': len(preset_analysis['recommended_presets'])
                }
            )
            
        except Exception as e:
            raise CultureValidationError(f"Preset compatibility assessment failed: {str(e)}") from e
    
    # ============================================================================
    # ENHANCED UTILITY METHODS (Pure Functions with Enum Integration)
    # ============================================================================
    
    @staticmethod
    def _infer_authenticity_level(culture_data: Dict[str, Any]) -> CultureAuthenticityLevel:
        """Infer authenticity level from culture data patterns."""
        try:
            # Check for historical/mythological references
            historical_indicators = ['history', 'historical', 'ancient', 'traditional', 'mythology', 'legend']
            creative_indicators = ['fantasy', 'magical', 'invented', 'original', 'creative', 'unique']
            
            text_content = str(culture_data).lower()
            
            historical_score = sum(1 for indicator in historical_indicators if indicator in text_content)
            creative_score = sum(1 for indicator in creative_indicators if indicator in text_content)
            
            # Check naming patterns for authenticity clues
            all_names = EnhancedCreativeCultureValidator._collect_all_names(culture_data)
            if all_names:
                # Simple heuristic: names with common Earth language patterns suggest historical inspiration
                earth_patterns = ['an', 'en', 'on', 'ar', 'er', 'ir', 'al', 'el', 'il']
                pattern_matches = sum(1 for name in all_names for pattern in earth_patterns if pattern in name.lower())
                pattern_ratio = pattern_matches / len(all_names) if all_names else 0
                
                if pattern_ratio > 0.7:
                    historical_score += 2
                elif pattern_ratio < 0.3:
                    creative_score += 2
            
            # Determine authenticity level
            if historical_score > creative_score + 2:
                return CultureAuthenticityLevel.HISTORICAL_INSPIRED
            elif creative_score > historical_score + 2:
                return CultureAuthenticityLevel.CREATIVE_ORIGINAL
            elif 'myth' in text_content or 'legend' in text_content:
                return CultureAuthenticityLevel.MYTHOLOGICAL_BASED
            else:
                return CultureAuthenticityLevel.CREATIVE_BLEND
                
        except Exception:
            return CultureAuthenticityLevel.CREATIVE_BLEND
    
    @staticmethod
    def _infer_creativity_level(culture_data: Dict[str, Any]) -> CultureCreativityLevel:
        """Infer creativity level from culture data patterns."""
        try:
            creativity_score = 0
            
            # Check for creative elements
            creative_elements = ['unique', 'original', 'innovative', 'creative', 'imaginative', 'fantasy']
            text_content = str(culture_data).lower()
            creativity_score += sum(1 for element in creative_elements if element in text_content)
            
            # Check for unique features
            if 'unique_features' in culture_data or 'distinctive_traits' in culture_data:
                creativity_score += 2
            
            # Check for magical/supernatural elements
            if 'magic' in text_content or 'supernatural' in text_content:
                creativity_score += 2
            
            # Check naming creativity
            all_names = EnhancedCreativeCultureValidator._collect_all_names(culture_data)
            if all_names:
                unique_patterns = len(set(name[:2] for name in all_names if len(name) >= 2))
                if unique_patterns > len(all_names) * 0.5:
                    creativity_score += 1
            
            # Determine creativity level
            if creativity_score >= 6:
                return CultureCreativityLevel.HIGHLY_CREATIVE
            elif creativity_score >= 4:
                return CultureCreativityLevel.CREATIVELY_ENHANCED
            elif creativity_score >= 2:
                return CultureCreativityLevel.MODERATELY_CREATIVE
            else:
                return CultureCreativityLevel.TRADITIONALLY_GROUNDED
                
        except Exception:
            return CultureCreativityLevel.MODERATELY_CREATIVE
    
    @staticmethod
    def _infer_complexity_level(culture_data: Dict[str, Any]) -> CultureComplexityLevel:
        """Infer complexity level from culture data patterns."""
        try:
            complexity_score = 0
            
            # Count major cultural elements
            major_elements = [
                'cultural_traits', 'social_structure', 'traditions', 'customs', 'values', 'beliefs',
                'occupations', 'professions', 'conflicts', 'mysteries', 'character_hooks',
                'geographical_context', 'environment', 'arts', 'crafts', 'philosophy'
            ]
            
            complexity_score += sum(1 for element in major_elements if element in culture_data)
            
            # Count name categories
            name_categories = ['male_names', 'female_names', 'neutral_names', 'family_names', 'titles', 'epithets']
            name_category_count = sum(1 for cat in name_categories if cat in culture_data and culture_data[cat])
            complexity_score += name_category_count
            
            # Check for gaming elements
            gaming_elements = ['gaming_notes', 'pronunciation_guide', 'quick_reference']
            complexity_score += sum(1 for element in gaming_elements if element in culture_data)
            
            # Determine complexity level
            if complexity_score >= 15:
                return CultureComplexityLevel.COMPREHENSIVE
            elif complexity_score >= 12:
                return CultureComplexityLevel.NARRATIVE_RICH
            elif complexity_score >= 9:
                return CultureComplexityLevel.CHARACTER_RICH
            elif complexity_score >= 6:
                return CultureComplexityLevel.GAMING_READY
            elif complexity_score >= 3:
                return CultureComplexityLevel.MODERATE
            else:
                return CultureComplexityLevel.BASIC
                
        except Exception:
            return CultureComplexityLevel.MODERATE
    
    @staticmethod
    def _infer_naming_structure(names: List[str]) -> CultureNamingStructure:
        """Infer naming structure from name patterns."""
        if not names:
            return CultureNamingStructure.SIMPLE
        
        try:
            # Analyze patterns
            avg_length = sum(len(name) for name in names) / len(names)
            syllable_count = sum(len([c for c in name if c.lower() in 'aeiou']) for name in names) / len(names)
            
            # Check for complexity indicators
            has_apostrophes = any("'" in name for name in names)
            has_hyphens = any("-" in name for name in names)
            has_long_names = any(len(name) > 12 for name in names)
            
            # Determine structure
            if has_apostrophes and has_hyphens:
                return CultureNamingStructure.COMPLEX
            elif avg_length > 8 and syllable_count > 3:
                return CultureNamingStructure.ELABORATE
            elif has_long_names or syllable_count > 2.5:
                return CultureNamingStructure.FLEXIBLE
            elif all(len(name) <= 8 and syllable_count <= 2 for name in names):
                return CultureNamingStructure.GAMING_FRIENDLY
            else:
                return CultureNamingStructure.SIMPLE
                
        except Exception:
            return CultureNamingStructure.SIMPLE
    
    @staticmethod
    def _has_minimum_content_enhanced(culture_data: Dict[str, Any]) -> bool:
        """Enhanced check for minimum usable content."""
        if not culture_data:
            return False
        
        # Check for at least one name or cultural element
        name_categories = ['male_names', 'female_names', 'neutral_names', 'family_names']
        has_names = any(culture_data.get(cat) for cat in name_categories)
        
        cultural_elements = ['cultural_traits', 'description', 'values', 'traditions']
        has_cultural_content = any(culture_data.get(element) for element in cultural_elements)
        
        return has_names or has_cultural_content
    
    @staticmethod
    def _collect_all_names(culture_data: Dict[str, Any]) -> List[str]:
        """Collect all names from culture data."""
        all_names = []
        name_categories = ['male_names', 'female_names', 'neutral_names', 'family_names', 'titles', 'epithets']
        
        for category in name_categories:
            if category in culture_data and isinstance(culture_data[category], list):
                all_names.extend([name for name in culture_data[category] if name and name.strip()])
        
        return all_names
    
    @staticmethod
    def _count_total_names(culture_data: Dict[str, Any]) -> int:
        """Count total names in culture data."""
        return len(EnhancedCreativeCultureValidator._collect_all_names(culture_data))
    
    @staticmethod
    def _count_creative_elements(culture_data: Dict[str, Any]) -> int:
        """Count creative/cultural elements in culture data."""
        creative_elements = [
            'cultural_traits', 'unique_features', 'traditions', 'customs', 'values', 'beliefs',
            'mysteries', 'legends', 'conflicts', 'character_hooks', 'arts', 'crafts', 'philosophy'
        ]
        return sum(1 for element in creative_elements if element in culture_data and culture_data[element])
    
    # ============================================================================
    # ENHANCED ASSESSMENT HELPER METHODS (Pure Functions)
    # ============================================================================
    
    @staticmethod
    def _assess_name_diversity_enhanced(names: List[str]) -> float:
        """Enhanced assessment of name diversity."""
        if not names:
            return 0.0
        
        # Check syllable diversity
        syllable_patterns = set()
        for name in names:
            vowels = [i for i, c in enumerate(name.lower()) if c in 'aeiou']
            pattern = len(vowels)  # Simple syllable count approximation
            syllable_patterns.add(pattern)
        
        # Check starting letters diversity
        starting_letters = set(name[0].lower() for name in names if name)
        
        # Check length diversity
        lengths = set(len(name) for name in names)
        
        # Calculate diversity score
        syllable_diversity = len(syllable_patterns) / max(len(set(range(1, 6))), 1)  # Normalize to 1-5 syllables
        letter_diversity = len(starting_letters) / min(26, len(names))  # Normalize to available letters
        length_diversity = len(lengths) / max(len(names), 5)  # Normalize to reasonable range
        
        return min(1.0, (syllable_diversity + letter_diversity + length_diversity) / 3)
    
    @staticmethod
    def _assess_creative_uniqueness_enhanced(names: List[str]) -> float:
        """Enhanced assessment of creative uniqueness in names."""
        if not names:
            return 0.0
        
        # Check for common fantasy name patterns
        common_patterns = ['ar', 'er', 'an', 'en', 'el', 'al', 'or', 'on']
        unique_score = 0.0
        
        for name in names:
            name_lower = name.lower()
            pattern_matches = sum(1 for pattern in common_patterns if pattern in name_lower)
            if pattern_matches <= 1:  # Less common patterns suggest more uniqueness
                unique_score += 1
        
        return unique_score / len(names) if names else 0.0
    
    @staticmethod
    def _assess_character_fit_potential_enhanced(names: List[str]) -> float:
        """Enhanced assessment of how well names fit character concepts."""
        if not names:
            return 0.0
        
        # Check for diverse character archetype support
        archetype_patterns = {
            'warrior': ['ar', 'or', 'ax', 'ex'],
            'mage': ['el', 'al', 'is', 'us'],
            'rogue': ['yn', 'in', 'ix', 'ax'],
            'noble': ['an', 'en', 'ia', 'ara']
        }
        
        archetype_coverage = 0
        for archetype, patterns in archetype_patterns.items():
            if any(any(pattern in name.lower() for pattern in patterns) for name in names):
                archetype_coverage += 1
        
        return archetype_coverage / len(archetype_patterns)
    
    @staticmethod
    def _assess_pronunciation_accessibility_enhanced(names: List[str]) -> float:
        """Enhanced assessment of pronunciation accessibility."""
        if not names:
            return 0.0
        
        accessible_count = 0
        for name in names:
            # Simple heuristics for pronunciation difficulty
            consonant_clusters = 0
            apostrophes = name.count("'")
            length = len(name)
            
            # Check for consonant clusters
            for i in range(len(name) - 1):
                if name[i].lower() not in 'aeiou' and name[i + 1].lower() not in 'aeiou':
                    consonant_clusters += 1
            
            # Score based on accessibility factors
            if consonant_clusters <= 2 and apostrophes <= 1 and length <= 10:
                accessible_count += 1
        
        return accessible_count / len(names)
    
    @staticmethod
    def _assess_memorable_factor_enhanced(names: List[str]) -> float:
        """Enhanced assessment of name memorability."""
        if not names:
            return 0.0
        
        memorable_count = 0
        for name in names:
            # Factors that make names memorable
            has_rhythm = len([c for c in name.lower() if c in 'aeiou']) >= 2  # At least 2 vowels
            reasonable_length = 4 <= len(name) <= 9  # Sweet spot for memorability
            distinctive_start = name[0].upper() != 'A'  # Not starting with most common letter
            
            if sum([has_rhythm, reasonable_length, distinctive_start]) >= 2:
                memorable_count += 1
        
        return memorable_count / len(names)
    
    @staticmethod
    def _assess_gaming_table_usability(names: List[str]) -> float:
        """Assess names for gaming table usability."""
        if not names:
            return 0.0
        
        usable_count = 0
        for name in names:
            # Gaming table friendly factors
            short_enough = len(name) <= 8  # Easy to say quickly
            pronounceable = not any(cluster in name.lower() for cluster in ['tch', 'sch', 'pht', 'xth'])
            no_complex_punctuation = name.count("'") <= 1 and '-' not in name
            
            if sum([short_enough, pronounceable, no_complex_punctuation]) >= 2:
                usable_count += 1
        
        return usable_count / len(names)
    
    @staticmethod
    def _assess_name_enum_compatibility(names: List[str], culture_data: Dict[str, Any]) -> float:
        """Assess name compatibility with enum-based systems."""
        if not names:
            return 0.0
        
        # Check compatibility with different naming structures
        inferred_structure = EnhancedCreativeCultureValidator._infer_naming_structure(names)
        base_score = 0.5  # Default compatibility
        
        # Bonus for gaming-friendly structures
        if inferred_structure == CultureNamingStructure.GAMING_FRIENDLY:
            base_score += 0.3
        elif inferred_structure == CultureNamingStructure.SIMPLE:
            base_score += 0.2
        elif inferred_structure == CultureNamingStructure.FLEXIBLE:
            base_score += 0.1
        
        # Check for diverse name categories
        name_categories = ['male_names', 'female_names', 'neutral_names', 'family_names']
        category_count = sum(1 for cat in name_categories if cat in culture_data and culture_data[cat])
        category_bonus = min(0.2, category_count * 0.05)
        
        return min(1.0, base_score + category_bonus)
    
    @staticmethod
    def _assess_gaming_pronunciation_enhanced(names: List[str]) -> float:
        """Enhanced gaming-specific pronunciation assessment."""
        if not names:
            return 0.0
        
        gaming_friendly_count = 0
        for name in names:
            # Gaming-specific pronunciation factors
            short_syllables = len([c for c in name.lower() if c in 'aeiou']) <= 3
            no_silent_letters = 'gh' not in name.lower() and 'ph' not in name.lower()
            common_sounds = not any(combo in name.lower() for combo in ['zh', 'ch', 'th', 'sh'])
            
            if sum([short_syllables, no_silent_letters, common_sounds]) >= 2:
                gaming_friendly_count += 1
        
        return gaming_friendly_count / len(names)
    
    @staticmethod
    def _assess_gaming_name_length_enhanced(names: List[str]) -> float:
        """Enhanced gaming-specific name length assessment."""
        if not names:
            return 0.0
        
        optimal_length_count = 0
        for name in names:
            # Optimal length for gaming (4-7 characters)
            if 4 <= len(name) <= 7:
                optimal_length_count += 1
            elif 3 <= len(name) <= 9:  # Acceptable range
                optimal_length_count += 0.5
        
        return optimal_length_count / len(names)
    
    @staticmethod
    def _assess_name_distinctiveness_enhanced(names: List[str]) -> float:
        """Enhanced assessment of name distinctiveness."""
        if not names or len(names) == 1:
            return 1.0
        
        # Check for sufficient differences between names
        distinctive_pairs = 0
        total_pairs = 0
        
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                total_pairs += 1
                name1, name2 = names[i], names[j]
                
                # Calculate similarity (simple edit distance approximation)
                if len(name1) != len(name2) or name1[:2] != name2[:2] or name1[-2:] != name2[-2:]:
                    distinctive_pairs += 1
                elif sum(c1 != c2 for c1, c2 in zip(name1, name2)) >= 2:
                    distinctive_pairs += 1
        
        return distinctive_pairs / total_pairs if total_pairs > 0 else 1.0
    
    @staticmethod
    def _assess_gaming_memorability(names: List[str]) -> float:
        """Assess name memorability for gaming contexts."""
        if not names:
            return 0.0
        
        memorable_count = 0
        for name in names:
            # Gaming memorability factors
            strong_consonants = sum(1 for c in name.lower() if c in 'kgdtbp')  # Hard sounds
            clear_vowels = sum(1 for c in name.lower() if c in 'aeo')  # Clear vowel sounds
            good_rhythm = 2 <= len([c for c in name.lower() if c in 'aeiou']) <= 3
            
            memorability_score = sum([
                strong_consonants >= 1,
                clear_vowels >= 1,
                good_rhythm,
                4 <= len(name) <= 8
            ])
            
            if memorability_score >= 3:
                memorable_count += 1
        
        return memorable_count / len(names)
    
    @staticmethod
    def _assess_description_quality_enhanced(culture_data: Dict[str, Any]) -> float:
        """Enhanced assessment of description quality."""
        description_elements = ['description', 'cultural_traits', 'traditions', 'customs', 'values']
        quality_score = 0.0
        
        for element in description_elements:
            if element in culture_data and culture_data[element]:
                content = str(culture_data[element])
                # Simple quality metrics
                if len(content) > 50:  # Substantial content
                    quality_score += 0.2
                if any(word in content.lower() for word in ['character', 'personality', 'behavior']):
                    quality_score += 0.1  # Character-relevant content
        
        return min(1.0, quality_score)
    
    @staticmethod
    def _assess_background_enum_compatibility(culture_data: Dict[str, Any]) -> float:
        """Assess background elements compatibility with enum enhancements."""
        background_elements = [
            'cultural_traits', 'character_hooks', 'social_structure', 'traditions',
            'values', 'occupations', 'conflicts', 'mysteries'
        ]
        
        present_elements = sum(1 for element in background_elements if element in culture_data and culture_data[element])
        return present_elements / len(background_elements)
    
    @staticmethod
    def _assess_gaming_enum_compatibility(culture_data: Dict[str, Any]) -> float:
        """Assess gaming elements compatibility with enum enhancements."""
        gaming_elements = [
            'gaming_notes', 'pronunciation_guide', 'quick_reference', 'naming_examples',
            'character_integration', 'dm_notes', 'table_friendly_features'
        ]
        
        present_elements = sum(1 for element in gaming_elements if element in culture_data and culture_data[element])
        base_score = present_elements / len(gaming_elements)
        
        # Bonus for gaming-friendly names
        all_names = EnhancedCreativeCultureValidator._collect_all_names(culture_data)
        if all_names:
            gaming_name_score = EnhancedCreativeCultureValidator._assess_gaming_table_usability(all_names)
            return min(1.0, base_score + gaming_name_score * 0.3)
        
        return base_score
    
    @staticmethod
    def _assess_naming_creativity_enhanced(names: List[str]) -> float:
        """Enhanced assessment of naming creativity."""
        if not names:
            return 0.0
        
        creativity_factors = {
            'unique_combinations': 0,
            'varied_patterns': 0,
            'creative_elements': 0
        }
        
        # Check for unique letter combinations
        combinations = set()
        for name in names:
            for i in range(len(name) - 1):
                combinations.add(name[i:i+2].lower())
        creativity_factors['unique_combinations'] = min(1.0, len(combinations) / (len(names) * 2))
        
        # Check for varied patterns
        patterns = set()
        for name in names:
            vowel_pattern = ''.join('V' if c.lower() in 'aeiou' else 'C' for c in name)
            patterns.add(vowel_pattern[:4])  # First 4 characters pattern
        creativity_factors['varied_patterns'] = min(1.0, len(patterns) / len(names))
        
        # Check for creative elements (apostrophes, unique sounds, etc.)
        creative_count = sum(1 for name in names if any(char in name for char in "''-") or any(combo in name.lower() for combo in ['ae', 'ei', 'ou', 'ya', 'xe']))
        creativity_factors['creative_elements'] = creative_count / len(names)
        
        return sum(creativity_factors.values()) / len(creativity_factors)
    
    @staticmethod
    def _assess_character_concept_flexibility_enhanced(culture_data: Dict[str, Any]) -> float:
        """Enhanced assessment of character concept flexibility."""
        flexibility_score = 0.0
        
        # Check for diverse occupational options
        if 'occupations' in culture_data or 'professions' in culture_data:
            flexibility_score += 0.3
        
        # Check for varied social roles
        if 'social_structure' in culture_data or 'hierarchy' in culture_data:
            flexibility_score += 0.2
        
        # Check for character archetypes
        if 'character_archetypes' in culture_data:
            flexibility_score += 0.3
        
        # Check for diverse values/motivations
        values_elements = ['values', 'beliefs', 'cultural_motivations', 'philosophy']
        if any(element in culture_data for element in values_elements):
            flexibility_score += 0.2
        
        return min(1.0, flexibility_score)
    
    @staticmethod
    def _assess_creative_freedom_potential(culture_data: Dict[str, Any]) -> float:
        """Assess potential for creative freedom in character development."""
        freedom_score = 0.0
        
        # Flexible cultural elements that don't constrain character concepts
        flexible_elements = ['traditions', 'customs', 'arts', 'crafts', 'philosophy']
        constraining_elements = ['strict_hierarchy', 'rigid_rules', 'forbidden_practices']
        
        flexible_count = sum(1 for element in flexible_elements if element in culture_data and culture_data[element])
        constraining_count = sum(1 for element in constraining_elements if element in culture_data and culture_data[element])
        
        freedom_score = (flexible_count * 0.2) - (constraining_count * 0.1)
        
        # Check for open-ended character hooks
        if 'character_hooks' in culture_data:
            hooks = culture_data['character_hooks']
            if isinstance(hooks, list) and len(hooks) > 3:
                freedom_score += 0.2
        
        return max(0.0, min(1.0, freedom_score))
    
    @staticmethod
    def _assess_creative_enum_compatibility(culture_data: Dict[str, Any]) -> float:
        """Assess creative elements compatibility with enum enhancements."""
        creative_elements = [
            'unique_features', 'distinctive_traits', 'mysteries', 'legends', 'conflicts',
            'philosophy', 'arts', 'crafts', 'character_archetypes', 'cultural_motivations'
        ]
        
        present_elements = sum(1 for element in creative_elements if element in culture_data and culture_data[element])
        base_score = present_elements / len(creative_elements)
        
        # Bonus for creative naming
        all_names = EnhancedCreativeCultureValidator._collect_all_names(culture_data)
        if all_names:
            naming_creativity = EnhancedCreativeCultureValidator._assess_naming_creativity_enhanced(all_names)
            return min(1.0, base_score + naming_creativity * 0.2)
        
        return base_score
    
    @staticmethod
    def _assess_single_preset_compatibility(
        culture_data: Dict[str, Any], 
        preset_name: str, 
        preset_config: Dict[str, Any]
    ) -> float:
        """Assess compatibility with a single preset configuration."""
        compatibility_score = 0.5  # Base compatibility
        
        # Gaming-optimized preset requirements
        if 'gaming' in preset_name.lower():
            all_names = EnhancedCreativeCultureValidator._collect_all_names(culture_data)
            if all_names:
                gaming_score = EnhancedCreativeCultureValidator._assess_gaming_table_usability(all_names)
                compatibility_score += gaming_score * 0.3
            
            gaming_elements = ['gaming_notes', 'pronunciation_guide', 'quick_reference']
            gaming_element_count = sum(1 for element in gaming_elements if element in culture_data)
            compatibility_score += (gaming_element_count / len(gaming_elements)) * 0.2
        
        # Character-rich preset requirements
        if 'character' in preset_name.lower():
            character_elements = ['character_hooks', 'cultural_traits', 'occupations', 'social_structure']
            character_element_count = sum(1 for element in character_elements if element in culture_data and culture_data[element])
            compatibility_score += (character_element_count / len(character_elements)) * 0.3
        
        # Creative-focused preset requirements
        if 'creative' in preset_name.lower():
            creative_elements = ['unique_features', 'mysteries', 'arts', 'philosophy']
            creative_element_count = sum(1 for element in creative_elements if element in culture_data and culture_data[element])
            compatibility_score += (creative_element_count / len(creative_elements)) * 0.3
        
        # Narrative-deep preset requirements
        if 'narrative' in preset_name.lower():
            narrative_elements = ['legends', 'history', 'conflicts', 'mysteries', 'character_hooks']
            narrative_element_count = sum(1 for element in narrative_elements if element in culture_data and culture_data[element])
            compatibility_score += (narrative_element_count / len(narrative_elements)) * 0.3
        
        return min(1.0, compatibility_score)
    
    @staticmethod
    def _get_preset_improvement_suggestions(preset_name: str) -> List[str]:
        """Get improvement suggestions for specific preset compatibility."""
        suggestions = []
        
        if 'gaming' in preset_name.lower():
            suggestions.extend([
                "Add gaming notes for DM convenience",
                "Include pronunciation guides for complex names",
                "Provide quick reference summaries",
                "Optimize names for table-friendly pronunciation"
            ])
        
        if 'character' in preset_name.lower():
            suggestions.extend([
                "Add more character hooks for backstory development",
                "Include diverse occupational roles",
                "Expand cultural traits for character personality inspiration",
                "Add social structure elements for character positioning"
            ])
        
        if 'creative' in preset_name.lower():
            suggestions.extend([
                "Add unique cultural features",
                "Include mysterious elements for intrigue",
                "Expand artistic and craft traditions",
                "Add philosophical elements for depth"
            ])
        
        if 'narrative' in preset_name.lower():
            suggestions.extend([
                "Add cultural legends and myths",
                "Include historical elements",
                "Expand internal conflicts for story hooks",
                "Add mysterious elements for campaign integration"
            ])
        
        return suggestions[:4]  # Limit to 4 suggestions
    
    @staticmethod
    def _get_preset_enhancement_categories(preset_name: str) -> List[CultureEnhancementCategory]:
        """Get relevant enhancement categories for preset optimization."""
        categories = []
        
        if 'gaming' in preset_name.lower():
            categories.extend([
                CultureEnhancementCategory.GAMING_UTILITY,
                CultureEnhancementCategory.PRONUNCIATION
            ])
        
        if 'character' in preset_name.lower():
            categories.extend([
                CultureEnhancementCategory.CHARACTER_NAMES,
                CultureEnhancementCategory.BACKGROUND_HOOKS,
                CultureEnhancementCategory.CHARACTER_MOTIVATIONS
            ])
        
        if 'creative' in preset_name.lower():
            categories.extend([
                CultureEnhancementCategory.CULTURAL_TRAITS,
                CultureEnhancementCategory.ROLEPLAY_ELEMENTS
            ])
        
        if 'narrative' in preset_name.lower():
            categories.extend([
                CultureEnhancementCategory.NARRATIVE_DEPTH,
                CultureEnhancementCategory.BACKGROUND_HOOKS
            ])
        
        return list(set(categories))  # Remove duplicates


# ============================================================================
# CONVENIENCE FUNCTIONS FOR EXTERNAL USE
# ============================================================================

def validate_culture_for_characters(
    culture_data: Dict[str, Any],
    target_preset: Optional[str] = None,
    focus_areas: List[CultureEnhancementCategory] = None
) -> EnhancedCreativeValidationResult:
    """
    Convenience function for enhanced culture validation.
    
    This is the main entry point for validating cultures with complete
    enum integration and character generation focus.
    
    Args:
        culture_data: Dictionary containing culture information
        target_preset: Optional preset to optimize for
        focus_areas: Specific enhancement categories to focus on
        
    Returns:
        EnhancedCreativeValidationResult with comprehensive analysis
        
    Example:
        >>> result = validate_culture_for_characters(
        ...     culture_data={'name': 'Test Culture', 'male_names': ['Aiden', 'Bren']},
        ...     target_preset='gaming_optimized',
        ...     focus_areas=[CultureEnhancementCategory.CHARACTER_NAMES]
        ... )
        >>> print(f"Usable: {result.is_usable}")
        >>> print(f"Character support: {result.character_support_score:.2f}")
    """
    return EnhancedCreativeCultureValidator.validate_for_character_generation_enhanced(
        culture_data, target_preset, focus_areas
    )


def quick_culture_assessment(culture_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Quick assessment function for basic culture validation.
    
    Returns essential metrics without detailed enhancement suggestions.
    
    Args:
        culture_data: Dictionary containing culture information
        
    Returns:
        Dictionary with basic assessment metrics
    """
    try:
        result = EnhancedCreativeCultureValidator.validate_for_character_generation_enhanced(culture_data)
        
        return {
            'is_usable': result.is_usable,
            'character_generation_readiness': result.get_character_generation_readiness_percentage(),
            'creative_quality': result.creative_quality_score,
            'gaming_usability': result.gaming_usability_score,
            'character_support': result.character_support_score,
            'name_generation': result.name_generation_score,
            'calculated_generation_score': result.calculated_generation_score,
            'top_enhancements': result.get_critical_enhancements()[:3],
            'validation_compliant': result.creative_validation_approach_compliant
        }
        
    except Exception as e:
        return {
            'is_usable': False,
            'error': str(e),
            'character_generation_readiness': 0,
            'validation_compliant': False
        }


def get_culture_enhancement_suggestions(
    culture_data: Dict[str, Any],
    max_suggestions: int = 5
) -> List[Dict[str, Any]]:
    """
    Get prioritized enhancement suggestions for culture improvement.
    
    Args:
        culture_data: Dictionary containing culture information
        max_suggestions: Maximum number of suggestions to return
        
    Returns:
        List of enhancement suggestion dictionaries
    """
    try:
        result = EnhancedCreativeCultureValidator.validate_for_character_generation_enhanced(culture_data)
        
        suggestions = []
        
        # Add high-priority suggestions first
        for suggestion in result.suggestions[:max_suggestions]:
            suggestions.append({
                'type': suggestion.issue_type.value,
                'priority': suggestion.enhancement_priority.value,
                'message': suggestion.message,
                'creative_suggestions': suggestion.creative_suggestions,
                'character_impact': suggestion.character_impact,
                'categories': [cat.value for cat in suggestion.target_enhancement_categories],
                'enum_recommendations': suggestion.enum_based_recommendations
            })
        
        return suggestions
        
    except Exception as e:
        return [{'error': f"Enhancement suggestion generation failed: {str(e)}"}]