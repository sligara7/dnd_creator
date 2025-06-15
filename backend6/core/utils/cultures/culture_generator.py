"""
Core Culture Generation Logic.

Pure functions for culture generation operations without external dependencies.
Follows Clean Architecture principles by maintaining infrastructure independence
and focusing on core business logic for AI-powered culture generation.

This module provides:
- Culture template creation and validation
- Culture data structure manipulation
- Pure functional approach to culture processing
- No side effects or external dependencies
- Educational focus on cultural authenticity
"""

from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
import re
from enum import Enum

# Import core types (inward dependencies only)
from ...enums.culture_types import (
    CultureGenerationType,
    CultureAuthenticityLevel,
    CultureCreativityLevel,
    CultureSourceType,
    CultureComplexityLevel,
    CultureNamingStructure,
    CultureGenderSystem,
    CultureLinguisticFamily,
    CultureTemporalPeriod,
    CultureValidationCategory,
    CultureValidationSeverity
)
from ...exceptions.culture import (
    CultureGenerationError,
    CultureValidationError,
    CultureStructureError
)
from ..validation.culture_validator import ValidationResult


@dataclass(frozen=True)
class BaseCulture:
    """
    Immutable base culture template structure.
    
    Represents the fundamental structure of any generated culture,
    ensuring consistency across different culture types and sources.
    """
    name: str
    description: str
    authenticity_level: CultureAuthenticityLevel
    source_type: CultureSourceType
    complexity_level: CultureComplexityLevel
    
    # Core cultural elements
    naming_structure: CultureNamingStructure
    gender_system: CultureGenderSystem
    linguistic_family: CultureLinguisticFamily
    temporal_period: CultureTemporalPeriod
    
    # Cultural content
    male_names: List[str] = field(default_factory=list)
    female_names: List[str] = field(default_factory=list)
    neutral_names: List[str] = field(default_factory=list)
    family_names: List[str] = field(default_factory=list)
    titles: List[str] = field(default_factory=list)
    epithets: List[str] = field(default_factory=list)
    
    # Extended cultural data
    cultural_traits: Dict[str, Any] = field(default_factory=dict)
    linguistic_patterns: Dict[str, str] = field(default_factory=dict)
    historical_context: Dict[str, str] = field(default_factory=dict)
    
    # Metadata
    generation_metadata: Dict[str, Any] = field(default_factory=dict)
    validation_notes: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate culture structure on creation."""
        if not self.name or not self.name.strip():
            raise CultureStructureError("Culture name cannot be empty")
        
        if not self.description or not self.description.strip():
            raise CultureStructureError("Culture description cannot be empty")


@dataclass(frozen=True)
class CultureGenerationSpec:
    """
    Immutable specification for culture generation.
    
    Defines all parameters needed for generating a culture,
    ensuring consistent input validation and processing.
    """
    cultural_reference: str
    generation_type: CultureGenerationType
    authenticity_level: CultureAuthenticityLevel
    creativity_level: CultureCreativityLevel
    source_type: CultureSourceType
    complexity_level: CultureComplexityLevel
    
    # Optional constraints
    required_elements: List[str] = field(default_factory=list)
    forbidden_elements: List[str] = field(default_factory=list)
    naming_preferences: Dict[str, Any] = field(default_factory=dict)
    cultural_constraints: Dict[str, Any] = field(default_factory=dict)
    
    # Quality requirements
    minimum_names_per_category: int = 20
    minimum_titles: int = 10
    require_linguistic_patterns: bool = True
    require_historical_context: bool = True


class CultureGenerator:
    """
    Core culture generation utilities.
    
    Pure functional approach to culture generation with no external dependencies.
    All methods are static or pure functions that produce consistent results
    for the same inputs without side effects.
    
    Maintains Clean Architecture principles:
    - No infrastructure dependencies
    - Pure business logic
    - Immutable data structures
    - Deterministic operations
    """
    
    @staticmethod
    def create_culture_template(
        spec: CultureGenerationSpec,
        base_data: Optional[Dict[str, Any]] = None
    ) -> BaseCulture:
        """
        Create a culture template from generation specification.
        
        Pure function that transforms a culture generation spec into
        a structured culture template without side effects.
        
        Args:
            spec: Culture generation specification
            base_data: Optional base culture data to build upon
            
        Returns:
            Immutable BaseCulture template
            
        Raises:
            CultureGenerationError: If template creation fails
            CultureStructureError: If resulting structure is invalid
            
        Example:
            >>> spec = CultureGenerationSpec(
            ...     cultural_reference="Ancient Norse seafaring culture",
            ...     generation_type=CultureGenerationType.CUSTOM,
            ...     authenticity_level=CultureAuthenticityLevel.HIGH,
            ...     creativity_level=CultureCreativityLevel.BALANCED,
            ...     source_type=CultureSourceType.HISTORICAL,
            ...     complexity_level=CultureComplexityLevel.DETAILED
            ... )
            >>> culture = CultureGenerator.create_culture_template(spec)
            >>> print(culture.name)
        """
        try:
            # Extract cultural name from reference
            culture_name = CultureGenerator._extract_culture_name(spec.cultural_reference)
            
            # Generate base description
            description = CultureGenerator._generate_culture_description(spec)
            
            # Determine cultural systems based on source and authenticity
            naming_structure = CultureGenerator._determine_naming_structure(spec)
            gender_system = CultureGenerator._determine_gender_system(spec)
            linguistic_family = CultureGenerator._determine_linguistic_family(spec)
            temporal_period = CultureGenerator._determine_temporal_period(spec)
            
            # Initialize cultural content based on complexity
            initial_content = CultureGenerator._initialize_cultural_content(spec)
            
            # Merge with base data if provided
            if base_data:
                initial_content = CultureGenerator._merge_with_base_data(initial_content, base_data)
            
            # Create generation metadata
            metadata = {
                'generation_type': spec.generation_type.name,
                'authenticity_level': spec.authenticity_level.name,
                'creativity_level': spec.creativity_level.name,
                'source_type': spec.source_type.name,
                'complexity_level': spec.complexity_level.name,
                'cultural_reference': spec.cultural_reference,
                'generated_timestamp': None,  # Will be set by calling service
                'expected_elements': spec.complexity_level.expected_elements
            }
            
            return BaseCulture(
                name=culture_name,
                description=description,
                authenticity_level=spec.authenticity_level,
                source_type=spec.source_type,
                complexity_level=spec.complexity_level,
                naming_structure=naming_structure,
                gender_system=gender_system,
                linguistic_family=linguistic_family,
                temporal_period=temporal_period,
                male_names=initial_content.get('male_names', []),
                female_names=initial_content.get('female_names', []),
                neutral_names=initial_content.get('neutral_names', []),
                family_names=initial_content.get('family_names', []),
                titles=initial_content.get('titles', []),
                epithets=initial_content.get('epithets', []),
                cultural_traits=initial_content.get('cultural_traits', {}),
                linguistic_patterns=initial_content.get('linguistic_patterns', {}),
                historical_context=initial_content.get('historical_context', {}),
                generation_metadata=metadata,
                validation_notes=[]
            )
            
        except Exception as e:
            raise CultureGenerationError(f"Failed to create culture template: {str(e)}") from e
    
    @staticmethod
    def validate_culture_structure(culture_data: Dict[str, Any]) -> ValidationResult:
        """
        Validate culture data structure and completeness.
        
        Pure function that analyzes culture data for structural integrity,
        required elements, and consistency without side effects.
        
        Args:
            culture_data: Culture data dictionary to validate
            
        Returns:
            ValidationResult with detailed validation information
            
        Example:
            >>> culture_dict = culture.to_dict()
            >>> result = CultureGenerator.validate_culture_structure(culture_dict)
            >>> print(f"Valid: {result.is_valid}, Issues: {len(result.issues)}")
        """
        issues = []
        warnings = []
        metadata = {'validation_categories': []}
        
        try:
            # Validate required fields
            required_fields = [
                'name', 'description', 'authenticity_level', 'source_type',
                'complexity_level', 'naming_structure', 'gender_system',
                'linguistic_family', 'temporal_period'
            ]
            
            missing_fields = [field for field in required_fields if field not in culture_data]
            if missing_fields:
                issues.extend([f"Missing required field: {field}" for field in missing_fields])
            
            # Validate cultural content based on complexity level
            if 'complexity_level' in culture_data:
                complexity_validation = CultureGenerator._validate_complexity_requirements(culture_data)
                issues.extend(complexity_validation['issues'])
                warnings.extend(complexity_validation['warnings'])
                metadata['validation_categories'].append('complexity')
            
            # Validate naming consistency
            naming_validation = CultureGenerator._validate_naming_consistency(culture_data)
            issues.extend(naming_validation['issues'])
            warnings.extend(naming_validation['warnings'])
            metadata['validation_categories'].append('naming')
            
            # Validate authenticity requirements
            if 'authenticity_level' in culture_data:
                authenticity_validation = CultureGenerator._validate_authenticity_requirements(culture_data)
                issues.extend(authenticity_validation['issues'])
                warnings.extend(authenticity_validation['warnings'])
                metadata['validation_categories'].append('authenticity')
            
            # Validate linguistic patterns
            linguistic_validation = CultureGenerator._validate_linguistic_patterns(culture_data)
            issues.extend(linguistic_validation['issues'])
            warnings.extend(linguistic_validation['warnings'])
            metadata['validation_categories'].append('linguistic')
            
            # Determine overall validation status
            is_valid = len(issues) == 0
            severity = CultureValidationSeverity.CRITICAL if issues else (
                CultureValidationSeverity.MEDIUM if warnings else CultureValidationSeverity.INFO
            )
            
            return ValidationResult(
                is_valid=is_valid,
                severity=severity,
                issues=issues,
                warnings=warnings,
                metadata=metadata
            )
            
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                severity=CultureValidationSeverity.CRITICAL,
                issues=[f"Validation error: {str(e)}"],
                warnings=[],
                metadata={'error': str(e)}
            )
    
    @staticmethod
    def merge_culture_data(
        base: Dict[str, Any], 
        additions: Dict[str, Any],
        merge_strategy: str = 'append'
    ) -> Dict[str, Any]:
        """
        Merge two culture data dictionaries.
        
        Pure function that combines culture data from different sources
        while preserving data integrity and consistency.
        
        Args:
            base: Base culture data dictionary
            additions: Additional culture data to merge
            merge_strategy: Strategy for merging ('append', 'replace', 'smart')
            
        Returns:
            New dictionary with merged culture data
            
        Raises:
            CultureStructureError: If merge operation would create invalid structure
            
        Example:
            >>> base_culture = {'male_names': ['Erik', 'Olaf']}
            >>> additions = {'male_names': ['Magnus', 'Thor']}
            >>> merged = CultureGenerator.merge_culture_data(base_culture, additions)
            >>> print(len(merged['male_names']))  # 4
        """
        if not isinstance(base, dict) or not isinstance(additions, dict):
            raise CultureStructureError("Both base and additions must be dictionaries")
        
        # Create deep copy to avoid mutations
        result = CultureGenerator._deep_copy_dict(base)
        
        try:
            for key, value in additions.items():
                if key not in result:
                    # New key, add directly
                    result[key] = CultureGenerator._deep_copy_value(value)
                else:
                    # Existing key, apply merge strategy
                    result[key] = CultureGenerator._merge_values(
                        result[key], value, merge_strategy, key
                    )
            
            # Validate merged result
            validation_result = CultureGenerator.validate_culture_structure(result)
            if not validation_result.is_valid:
                critical_issues = [issue for issue in validation_result.issues 
                                 if 'critical' in issue.lower()]
                if critical_issues:
                    raise CultureStructureError(f"Merge created invalid structure: {critical_issues[0]}")
            
            return result
            
        except Exception as e:
            if isinstance(e, CultureStructureError):
                raise
            raise CultureStructureError(f"Failed to merge culture data: {str(e)}") from e
    
    @staticmethod
    def extract_cultural_elements(text: str) -> Dict[str, List[str]]:
        """
        Extract cultural elements from descriptive text.
        
        Pure function that analyzes text for cultural references,
        names, and other cultural elements using pattern matching.
        
        Args:
            text: Text to analyze for cultural elements
            
        Returns:
            Dictionary of extracted cultural elements by category
            
        Example:
            >>> text = "The Norse seafarers Erik and Olaf sailed with Thor's blessing"
            >>> elements = CultureGenerator.extract_cultural_elements(text)
            >>> print(elements['possible_names'])  # ['Erik', 'Olaf', 'Thor']
        """
        elements = {
            'possible_names': [],
            'cultural_references': [],
            'titles_epithets': [],
            'locations': [],
            'concepts': [],
            'linguistic_patterns': []
        }
        
        try:
            # Extract potential names (capitalized words)
            name_pattern = r'\b[A-Z][a-z]+\b'
            potential_names = re.findall(name_pattern, text)
            elements['possible_names'] = list(set(potential_names))
            
            # Extract cultural references (common cultural keywords)
            cultural_keywords = [
                'culture', 'tradition', 'custom', 'heritage', 'ancestry',
                'tribe', 'clan', 'people', 'folk', 'nation', 'kingdom',
                'ancient', 'medieval', 'classical', 'traditional'
            ]
            
            for keyword in cultural_keywords:
                if keyword.lower() in text.lower():
                    # Extract context around the keyword
                    context_pattern = rf'\b\w+\s+{re.escape(keyword)}\b|\b{re.escape(keyword)}\s+\w+\b'
                    contexts = re.findall(context_pattern, text, re.IGNORECASE)
                    elements['cultural_references'].extend(contexts)
            
            # Extract titles and epithets (words following 'the')
            title_pattern = r'\bthe\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
            titles = re.findall(title_pattern, text)
            elements['titles_epithets'] = list(set(titles))
            
            # Extract location references
            location_keywords = [
                'from', 'of', 'in', 'at', 'near', 'beyond', 'across',
                'land', 'realm', 'kingdom', 'territory', 'region'
            ]
            
            for keyword in location_keywords:
                location_pattern = rf'{re.escape(keyword)}\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
                locations = re.findall(location_pattern, text, re.IGNORECASE)
                elements['locations'].extend(locations)
            
            # Identify linguistic patterns
            patterns = []
            
            # Common prefixes/suffixes
            if re.search(r'\b\w*son\b', text, re.IGNORECASE):
                patterns.append('patronymic_son')
            if re.search(r'\b\w*sen\b', text, re.IGNORECASE):
                patterns.append('patronymic_sen')
            if re.search(r'\b\w*dottir\b', text, re.IGNORECASE):
                patterns.append('patronymic_dottir')
            
            # Common linguistic families
            if re.search(r'\b(mac|mc)\w+', text, re.IGNORECASE):
                patterns.append('celtic_patronymic')
            if re.search(r'\b\w*ovich\b|\b\w*ovna\b', text, re.IGNORECASE):
                patterns.append('slavic_patronymic')
            
            elements['linguistic_patterns'] = patterns
            
            # Clean up and deduplicate
            for key in elements:
                if isinstance(elements[key], list):
                    elements[key] = list(set(filter(None, elements[key])))
            
            return elements
            
        except Exception as e:
            # Return empty elements on error rather than failing
            return {
                'possible_names': [],
                'cultural_references': [],
                'titles_epithets': [],
                'locations': [],
                'concepts': [],
                'linguistic_patterns': [],
                'extraction_error': str(e)
            }
    
    @staticmethod
    def calculate_culture_complexity_score(culture_data: Dict[str, Any]) -> float:
        """
        Calculate complexity score for culture data.
        
        Pure function that analyzes culture data to determine its
        richness and completeness as a numerical score.
        
        Args:
            culture_data: Culture data to analyze
            
        Returns:
            Complexity score from 0.0 to 1.0
            
        Example:
            >>> score = CultureGenerator.calculate_culture_complexity_score(culture_dict)
            >>> print(f"Complexity: {score:.2f}")
        """
        if not culture_data:
            return 0.0
        
        score = 0.0
        max_score = 0.0
        
        # Core required elements (40% of total score)
        core_elements = ['name', 'description', 'naming_structure', 'gender_system']
        core_weight = 0.4
        core_present = sum(1 for element in core_elements if element in culture_data)
        score += (core_present / len(core_elements)) * core_weight
        max_score += core_weight
        
        # Cultural content (35% of total score)
        content_categories = ['male_names', 'female_names', 'family_names', 'titles', 'epithets']
        content_weight = 0.35
        content_score = 0.0
        
        for category in content_categories:
            if category in culture_data and isinstance(culture_data[category], list):
                category_score = min(len(culture_data[category]) / 20, 1.0)  # Max at 20 items
                content_score += category_score / len(content_categories)
        
        score += content_score * content_weight
        max_score += content_weight
        
        # Extended data (25% of total score)
        extended_elements = ['cultural_traits', 'linguistic_patterns', 'historical_context']
        extended_weight = 0.25
        extended_score = 0.0
        
        for element in extended_elements:
            if element in culture_data and culture_data[element]:
                if isinstance(culture_data[element], dict):
                    element_score = min(len(culture_data[element]) / 5, 1.0)  # Max at 5 items
                    extended_score += element_score / len(extended_elements)
                else:
                    extended_score += 1.0 / len(extended_elements)
        
        score += extended_score * extended_weight
        max_score += extended_weight
        
        return min(score / max_score if max_score > 0 else 0.0, 1.0)
    
    @staticmethod
    def generate_culture_summary(culture: BaseCulture) -> str:
        """
        Generate a human-readable summary of a culture.
        
        Pure function that creates descriptive text summary
        of culture characteristics and content.
        
        Args:
            culture: BaseCulture to summarize
            
        Returns:
            Human-readable culture summary
            
        Example:
            >>> summary = CultureGenerator.generate_culture_summary(norse_culture)
            >>> print(summary)
        """
        summary_parts = []
        
        # Basic information
        summary_parts.append(f"**{culture.name}**")
        summary_parts.append(culture.description)
        summary_parts.append("")
        
        # Cultural characteristics
        summary_parts.append("**Cultural Characteristics:**")
        summary_parts.append(f"- Authenticity Level: {culture.authenticity_level.name.title()}")
        summary_parts.append(f"- Source Type: {culture.source_type.name.replace('_', ' ').title()}")
        summary_parts.append(f"- Complexity: {culture.complexity_level.name.title()}")
        summary_parts.append(f"- Naming Structure: {culture.naming_structure.name.replace('_', ' ').title()}")
        summary_parts.append(f"- Gender System: {culture.gender_system.name.replace('_', ' ').title()}")
        summary_parts.append(f"- Linguistic Family: {culture.linguistic_family.name.replace('_', ' ').title()}")
        summary_parts.append(f"- Time Period: {culture.temporal_period.name.replace('_', ' ').title()}")
        summary_parts.append("")
        
        # Name categories with counts
        name_info = []
        if culture.male_names:
            name_info.append(f"Male names: {len(culture.male_names)}")
        if culture.female_names:
            name_info.append(f"Female names: {len(culture.female_names)}")
        if culture.neutral_names:
            name_info.append(f"Neutral names: {len(culture.neutral_names)}")
        if culture.family_names:
            name_info.append(f"Family names: {len(culture.family_names)}")
        if culture.titles:
            name_info.append(f"Titles: {len(culture.titles)}")
        if culture.epithets:
            name_info.append(f"Epithets: {len(culture.epithets)}")
        
        if name_info:
            summary_parts.append("**Available Names:**")
            summary_parts.extend([f"- {info}" for info in name_info])
            summary_parts.append("")
        
        # Cultural traits
        if culture.cultural_traits:
            summary_parts.append("**Cultural Traits:**")
            for trait, value in culture.cultural_traits.items():
                summary_parts.append(f"- {trait.replace('_', ' ').title()}: {value}")
            summary_parts.append("")
        
        # Linguistic patterns
        if culture.linguistic_patterns:
            summary_parts.append("**Linguistic Patterns:**")
            for pattern, description in culture.linguistic_patterns.items():
                summary_parts.append(f"- {pattern.replace('_', ' ').title()}: {description}")
            summary_parts.append("")
        
        # Historical context
        if culture.historical_context:
            summary_parts.append("**Historical Context:**")
            for context, description in culture.historical_context.items():
                summary_parts.append(f"- {context.replace('_', ' ').title()}: {description}")
            summary_parts.append("")
        
        # Generation metadata
        if culture.generation_metadata:
            complexity_score = CultureGenerator.calculate_culture_complexity_score(
                CultureGenerator._culture_to_dict(culture)
            )
            summary_parts.append("**Generation Info:**")
            summary_parts.append(f"- Complexity Score: {complexity_score:.2f}")
            summary_parts.append(f"- Expected Elements: {culture.generation_metadata.get('expected_elements', 'Unknown')}")
            
            if culture.validation_notes:
                summary_parts.append(f"- Validation Notes: {len(culture.validation_notes)} notes")
        
        return "\n".join(summary_parts)
    
    # ============================================================================
    # PRIVATE HELPER METHODS (Pure Functions)
    # ============================================================================
    
    @staticmethod
    def _extract_culture_name(cultural_reference: str) -> str:
        """Extract a culture name from the cultural reference."""
        # Remove common descriptive words
        descriptive_words = ['ancient', 'medieval', 'traditional', 'modern', 'classic']
        words = cultural_reference.split()
        
        # Filter out descriptive words and common terms
        culture_words = [
            word for word in words 
            if word.lower() not in descriptive_words and 
            word.lower() not in ['culture', 'people', 'society', 'civilization']
        ]
        
        if culture_words:
            return ' '.join(culture_words[:2]).title()  # Take first 2 significant words
        else:
            return cultural_reference.split()[0].title()  # Fallback to first word
    
    @staticmethod
    def _generate_culture_description(spec: CultureGenerationSpec) -> str:
        """Generate a basic culture description from specification."""
        authenticity_desc = {
            CultureAuthenticityLevel.ACADEMIC: "rigorously researched",
            CultureAuthenticityLevel.HIGH: "historically accurate",
            CultureAuthenticityLevel.MODERATE: "culturally respectful",
            CultureAuthenticityLevel.CREATIVE: "creatively interpreted",
            CultureAuthenticityLevel.FANTASY: "fantasy-adapted",
            CultureAuthenticityLevel.NONE: "imaginatively created"
        }
        
        complexity_desc = {
            CultureComplexityLevel.SIMPLE: "basic cultural elements",
            CultureComplexityLevel.STANDARD: "standard cultural depth",
            CultureComplexityLevel.DETAILED: "rich cultural detail",
            CultureComplexityLevel.COMPREHENSIVE: "comprehensive cultural system",
            CultureComplexityLevel.SCHOLARLY: "scholarly cultural analysis"
        }
        
        auth_text = authenticity_desc.get(spec.authenticity_level, "culturally generated")
        complexity_text = complexity_desc.get(spec.complexity_level, "cultural elements")
        
        return f"A {auth_text} culture with {complexity_text}, generated from: {spec.cultural_reference}"
    
    @staticmethod
    def _determine_naming_structure(spec: CultureGenerationSpec) -> CultureNamingStructure:
        """Determine appropriate naming structure based on cultural reference."""
        reference_lower = spec.cultural_reference.lower()
        
        # Pattern matching for common naming structures
        if any(term in reference_lower for term in ['norse', 'viking', 'scandinavian', 'nordic']):
            return CultureNamingStructure.PATRONYMIC
        elif any(term in reference_lower for term in ['chinese', 'japanese', 'korean', 'asian']):
            return CultureNamingStructure.FAMILY_GIVEN
        elif any(term in reference_lower for term in ['celtic', 'irish', 'scottish', 'welsh']):
            return CultureNamingStructure.CLAN_INDIVIDUAL
        elif any(term in reference_lower for term in ['noble', 'royal', 'aristocratic', 'medieval']):
            return CultureNamingStructure.TITLE_NAME
        elif any(term in reference_lower for term in ['tribal', 'shamanic', 'indigenous']):
            return CultureNamingStructure.DESCRIPTIVE
        else:
            return CultureNamingStructure.GIVEN_FAMILY  # Default Western structure
    
    @staticmethod
    def _determine_gender_system(spec: CultureGenerationSpec) -> CultureGenderSystem:
        """Determine appropriate gender system based on specification."""
        # Default to binary for most historical cultures
        if spec.authenticity_level in [CultureAuthenticityLevel.ACADEMIC, CultureAuthenticityLevel.HIGH]:
            return CultureGenderSystem.BINARY
        elif spec.creativity_level == CultureCreativityLevel.EXPERIMENTAL:
            return CultureGenderSystem.FLUID
        else:
            return CultureGenderSystem.BINARY
    
    @staticmethod
    def _determine_linguistic_family(spec: CultureGenerationSpec) -> CultureLinguisticFamily:
        """Determine linguistic family from cultural reference."""
        reference_lower = spec.cultural_reference.lower()
        
        # Pattern matching for linguistic families
        if any(term in reference_lower for term in ['norse', 'viking', 'scandinavian', 'nordic', 'germanic']):
            return CultureLinguisticFamily.INDO_EUROPEAN
        elif any(term in reference_lower for term in ['chinese', 'tibetan', 'sino']):
            return CultureLinguisticFamily.SINO_TIBETAN
        elif any(term in reference_lower for term in ['arabic', 'hebrew', 'egyptian']):
            return CultureLinguisticFamily.AFROASIATIC
        elif any(term in reference_lower for term in ['polynesian', 'hawaiian', 'maori']):
            return CultureLinguisticFamily.AUSTRONESIAN
        elif any(term in reference_lower for term in ['turkic', 'mongolian']):
            return CultureLinguisticFamily.ALTAIC
        elif any(term in reference_lower for term in ['fantasy', 'tolkien', 'constructed']):
            return CultureLinguisticFamily.CONSTRUCTED
        else:
            return CultureLinguisticFamily.INDO_EUROPEAN  # Default
    
    @staticmethod
    def _determine_temporal_period(spec: CultureGenerationSpec) -> CultureTemporalPeriod:
        """Determine temporal period from cultural reference."""
        reference_lower = spec.cultural_reference.lower()
        
        # Pattern matching for time periods
        if any(term in reference_lower for term in ['ancient', 'archaic', 'prehistoric']):
            return CultureTemporalPeriod.ANCIENT
        elif any(term in reference_lower for term in ['medieval', 'middle ages', 'feudal']):
            return CultureTemporalPeriod.MEDIEVAL
        elif any(term in reference_lower for term in ['renaissance', 'early modern']):
            return CultureTemporalPeriod.RENAISSANCE
        elif any(term in reference_lower for term in ['industrial', 'victorian']):
            return CultureTemporalPeriod.INDUSTRIAL
        elif any(term in reference_lower for term in ['modern', 'contemporary', 'current']):
            return CultureTemporalPeriod.MODERN
        elif any(term in reference_lower for term in ['futuristic', 'sci-fi', 'future']):
            return CultureTemporalPeriod.FUTURISTIC
        elif any(term in reference_lower for term in ['mythological', 'legendary', 'mythic']):
            return CultureTemporalPeriod.MYTHOLOGICAL
        else:
            return CultureTemporalPeriod.TIMELESS  # Default
    
    @staticmethod
    def _initialize_cultural_content(spec: CultureGenerationSpec) -> Dict[str, Any]:
        """Initialize cultural content based on complexity level."""
        content = {
            'male_names': [],
            'female_names': [],
            'neutral_names': [],
            'family_names': [],
            'titles': [],
            'epithets': [],
            'cultural_traits': {},
            'linguistic_patterns': {},
            'historical_context': {}
        }
        
        # Set expected content based on complexity
        expected_elements = spec.complexity_level.expected_elements
        
        if expected_elements >= 150:  # Standard and above
            content['cultural_traits'] = {
                'naming_conventions': 'To be determined by AI generation',
                'social_structure': 'To be determined by AI generation'
            }
        
        if expected_elements >= 300:  # Detailed and above
            content['linguistic_patterns'] = {
                'name_patterns': 'To be determined by AI generation',
                'title_structure': 'To be determined by AI generation'
            }
        
        if expected_elements >= 500:  # Comprehensive and above
            content['historical_context'] = {
                'time_period': 'To be determined by AI generation',
                'cultural_background': 'To be determined by AI generation'
            }
        
        return content
    
    @staticmethod
    def _merge_with_base_data(content: Dict[str, Any], base_data: Dict[str, Any]) -> Dict[str, Any]:
        """Merge initialized content with base data."""
        for key, value in base_data.items():
            if key in content:
                if isinstance(content[key], list) and isinstance(value, list):
                    content[key] = list(set(content[key] + value))  # Merge and deduplicate
                elif isinstance(content[key], dict) and isinstance(value, dict):
                    content[key].update(value)
                else:
                    content[key] = value
            else:
                content[key] = value
        
        return content
    
    @staticmethod
    def _validate_complexity_requirements(culture_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate that culture meets complexity requirements."""
        issues = []
        warnings = []
        
        complexity_level = culture_data.get('complexity_level')
        if not complexity_level:
            return {'issues': ['Complexity level not specified'], 'warnings': []}
        
        if hasattr(complexity_level, 'expected_elements'):
            expected = complexity_level.expected_elements
            
            # Count actual elements
            actual_count = 0
            name_categories = ['male_names', 'female_names', 'neutral_names', 'family_names', 'titles', 'epithets']
            
            for category in name_categories:
                if category in culture_data and isinstance(culture_data[category], list):
                    actual_count += len(culture_data[category])
            
            if actual_count < expected * 0.5:  # Less than 50% of expected
                issues.append(f"Insufficient content: {actual_count} elements vs {expected} expected")
            elif actual_count < expected * 0.8:  # Less than 80% of expected
                warnings.append(f"Below expected content: {actual_count} elements vs {expected} expected")
        
        return {'issues': issues, 'warnings': warnings}
    
    @staticmethod
    def _validate_naming_consistency(culture_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate naming consistency within culture."""
        issues = []
        warnings = []
        
        name_categories = ['male_names', 'female_names', 'neutral_names', 'family_names']
        
        for category in name_categories:
            if category in culture_data and isinstance(culture_data[category], list):
                names = culture_data[category]
                
                # Check for duplicates
                if len(names) != len(set(names)):
                    issues.append(f"Duplicate names found in {category}")
                
                # Check for empty or invalid names
                invalid_names = [name for name in names if not name or not isinstance(name, str) or not name.strip()]
                if invalid_names:
                    issues.append(f"Invalid names found in {category}: {len(invalid_names)} invalid entries")
        
        return {'issues': issues, 'warnings': warnings}
    
    @staticmethod
    def _validate_authenticity_requirements(culture_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate authenticity requirements."""
        issues = []
        warnings = []
        
        authenticity_level = culture_data.get('authenticity_level')
        if not authenticity_level:
            return {'issues': ['Authenticity level not specified'], 'warnings': []}
        
        # High authenticity cultures should have historical context
        if authenticity_level in ['ACADEMIC', 'HIGH'] and hasattr(authenticity_level, 'name'):
            if authenticity_level.name in ['ACADEMIC', 'HIGH']:
                if not culture_data.get('historical_context'):
                    warnings.append("High authenticity culture should include historical context")
                
                if not culture_data.get('linguistic_patterns'):
                    warnings.append("High authenticity culture should include linguistic patterns")
        
        return {'issues': issues, 'warnings': warnings}
    
    @staticmethod
    def _validate_linguistic_patterns(culture_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate linguistic patterns and consistency."""
        issues = []
        warnings = []
        
        linguistic_patterns = culture_data.get('linguistic_patterns', {})
        if not isinstance(linguistic_patterns, dict):
            issues.append("Linguistic patterns must be a dictionary")
            return {'issues': issues, 'warnings': warnings}
        
        # Check for pattern consistency with names
        naming_structure = culture_data.get('naming_structure')
        if naming_structure and hasattr(naming_structure, 'name'):
            structure_name = naming_structure.name
            
            # Validate that naming structure matches available names
            if structure_name == 'PATRONYMIC':
                male_names = culture_data.get('male_names', [])
                if male_names and not any('son' in name.lower() or 'sen' in name.lower() for name in male_names):
                    warnings.append("Patronymic structure but no patronymic names found")
        
        return {'issues': issues, 'warnings': warnings}
    
    @staticmethod
    def _merge_values(base_value: Any, new_value: Any, strategy: str, key: str) -> Any:
        """Merge two values based on strategy."""
        if strategy == 'replace':
            return CultureGenerator._deep_copy_value(new_value)
        elif strategy == 'append' and isinstance(base_value, list) and isinstance(new_value, list):
            return base_value + new_value
        elif strategy == 'smart':
            if isinstance(base_value, list) and isinstance(new_value, list):
                # Merge lists and deduplicate
                return list(set(base_value + new_value))
            elif isinstance(base_value, dict) and isinstance(new_value, dict):
                # Merge dictionaries
                merged = CultureGenerator._deep_copy_dict(base_value)
                merged.update(new_value)
                return merged
            else:
                return CultureGenerator._deep_copy_value(new_value)
        else:
            return CultureGenerator._deep_copy_value(new_value)
    
    @staticmethod
    def _deep_copy_dict(original: Dict[str, Any]) -> Dict[str, Any]:
        """Create a deep copy of a dictionary."""
        result = {}
        for key, value in original.items():
            result[key] = CultureGenerator._deep_copy_value(value)
        return result
    
    @staticmethod
    def _deep_copy_value(value: Any) -> Any:
        """Create a deep copy of a value."""
        if isinstance(value, dict):
            return CultureGenerator._deep_copy_dict(value)
        elif isinstance(value, list):
            return [CultureGenerator._deep_copy_value(item) for item in value]
        else:
            return value
    
    @staticmethod
    def _culture_to_dict(culture: BaseCulture) -> Dict[str, Any]:
        """Convert BaseCulture to dictionary for analysis."""
        return {
            'name': culture.name,
            'description': culture.description,
            'authenticity_level': culture.authenticity_level,
            'source_type': culture.source_type,
            'complexity_level': culture.complexity_level,
            'naming_structure': culture.naming_structure,
            'gender_system': culture.gender_system,
            'linguistic_family': culture.linguistic_family,
            'temporal_period': culture.temporal_period,
            'male_names': culture.male_names,
            'female_names': culture.female_names,
            'neutral_names': culture.neutral_names,
            'family_names': culture.family_names,
            'titles': culture.titles,
            'epithets': culture.epithets,
            'cultural_traits': culture.cultural_traits,
            'linguistic_patterns': culture.linguistic_patterns,
            'historical_context': culture.historical_context,
            'generation_metadata': culture.generation_metadata,
            'validation_notes': culture.validation_notes
        }


# ============================================================================
# UTILITY FUNCTIONS (Pure Functions)
# ============================================================================

def create_culture_spec(
    cultural_reference: str,
    authenticity_level: CultureAuthenticityLevel = CultureAuthenticityLevel.MODERATE,
    creativity_level: CultureCreativityLevel = CultureCreativityLevel.BALANCED,
    complexity_level: CultureComplexityLevel = CultureComplexityLevel.STANDARD
) -> CultureGenerationSpec:
    """
    Create a culture generation specification with sensible defaults.
    
    Pure function for creating culture specs with intelligent defaults
    based on the cultural reference provided.
    
    Args:
        cultural_reference: Description of culture to generate
        authenticity_level: Desired authenticity level
        creativity_level: Desired creativity level
        complexity_level: Desired complexity level
        
    Returns:
        Configured CultureGenerationSpec
        
    Example:
        >>> spec = create_culture_spec("Ancient Norse seafaring culture")
        >>> culture = CultureGenerator.create_culture_template(spec)
    """
    # Determine source type from reference
    reference_lower = cultural_reference.lower()
    
    if any(term in reference_lower for term in ['ancient', 'historical', 'real', 'actual']):
        source_type = CultureSourceType.HISTORICAL
    elif any(term in reference_lower for term in ['myth', 'legend', 'folklore', 'saga']):
        source_type = CultureSourceType.MYTHOLOGICAL
    elif any(term in reference_lower for term in ['fantasy', 'fictional', 'imaginary']):
        source_type = CultureSourceType.LITERARY
    elif any(term in reference_lower for term in ['language', 'linguistic', 'dialect']):
        source_type = CultureSourceType.LINGUISTIC
    else:
        source_type = CultureSourceType.HISTORICAL  # Default
    
    return CultureGenerationSpec(
        cultural_reference=cultural_reference,
        generation_type=CultureGenerationType.CUSTOM,
        authenticity_level=authenticity_level,
        creativity_level=creativity_level,
        source_type=source_type,
        complexity_level=complexity_level
    )


def validate_culture_spec(spec: CultureGenerationSpec) -> List[str]:
    """
    Validate a culture generation specification.
    
    Pure function that checks specification validity.
    
    Args:
        spec: Culture generation specification to validate
        
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    if not spec.cultural_reference or not spec.cultural_reference.strip():
        errors.append("Cultural reference cannot be empty")
    
    if len(spec.cultural_reference) < 5:
        errors.append("Cultural reference must be at least 5 characters")
    
    if len(spec.cultural_reference) > 500:
        errors.append("Cultural reference must be less than 500 characters")
    
    # Check for problematic combinations
    if (spec.authenticity_level == CultureAuthenticityLevel.ACADEMIC and 
        spec.creativity_level == CultureCreativityLevel.EXPERIMENTAL):
        errors.append("Academic authenticity conflicts with experimental creativity")
    
    return errors


def get_recommended_complexity(
    authenticity_level: CultureAuthenticityLevel,
    creativity_level: CultureCreativityLevel
) -> CultureComplexityLevel:
    """
    Get recommended complexity level based on authenticity and creativity.
    
    Pure function that provides intelligent complexity recommendations.
    
    Args:
        authenticity_level: Desired authenticity level
        creativity_level: Desired creativity level
        
    Returns:
        Recommended complexity level
    """
    if authenticity_level == CultureAuthenticityLevel.ACADEMIC:
        return CultureComplexityLevel.SCHOLARLY
    elif authenticity_level == CultureAuthenticityLevel.HIGH:
        return CultureComplexityLevel.COMPREHENSIVE
    elif creativity_level == CultureCreativityLevel.EXPERIMENTAL:
        return CultureComplexityLevel.DETAILED
    else:
        return CultureComplexityLevel.STANDARD


# ============================================================================
# MODULE METADATA
# ============================================================================

__version__ = "1.0.0"
__description__ = "Core Culture Generation Logic for Clean Architecture"

# Clean Architecture compliance metadata
CLEAN_ARCHITECTURE_COMPLIANCE = {
    "layer": "core/utils/cultures",
    "dependencies": [
        "typing", "dataclasses", "re", "enum",
        "../../enums/culture_types", "../../exceptions/culture", "../validation/culture_validator"
    ],
    "dependents": ["domain/services", "application/use_cases"],
    "infrastructure_independent": True,
    "pure_functions": True,
    "side_effects": "none",
    "focuses_on": "Core culture generation business logic",
    "immutable_data": True,
    "stateless_operations": True
}

# Usage examples in docstring
"""
Usage Examples:

1. Create and generate culture:
   >>> spec = create_culture_spec("Ancient Norse seafaring culture")
   >>> culture = CultureGenerator.create_culture_template(spec)
   >>> print(culture.name)

2. Validate culture structure:
   >>> culture_dict = CultureGenerator._culture_to_dict(culture)
   >>> result = CultureGenerator.validate_culture_structure(culture_dict)
   >>> print(f"Valid: {result.is_valid}")

3. Merge culture data:
   >>> base_data = {'male_names': ['Erik', 'Olaf']}
   >>> additions = {'male_names': ['Magnus'], 'titles': ['Jarl']}
   >>> merged = CultureGenerator.merge_culture_data(base_data, additions)

4. Extract cultural elements:
   >>> text = "The Norse hero Erik Bloodaxe sailed with Odin's blessing"
   >>> elements = CultureGenerator.extract_cultural_elements(text)
   >>> print(elements['possible_names'])

5. Calculate complexity:
   >>> score = CultureGenerator.calculate_culture_complexity_score(culture_dict)
   >>> print(f"Complexity: {score:.2f}")

6. Generate summary:
   >>> summary = CultureGenerator.generate_culture_summary(culture)
   >>> print(summary)
"""