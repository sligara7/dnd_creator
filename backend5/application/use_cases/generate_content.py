"""
Unified Content Generation Use Case

Central orchestrator for all D&D content generation workflows. This module provides
the primary interface for generating species, classes, equipment, spells, and feats
based on character background concepts with integrated validation and balance optimization.
"""

from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor

from core.entities import CharacterConcept, GeneratedContent, ContentCollection
from core.value_objects import GenerationConstraints, ThematicElements, ValidationResult, BalanceMetrics
from core.enums import ContentType, GenerationMethod, ValidationSeverity
from core.services import ContentGeneratorService, BalanceAnalyzerService
from core.exceptions import GenerationError, ValidationError, ContentGenerationTimeoutError
from .concept_processor import ConceptProcessorUseCase, ConceptAnalysisRequest

logger = logging.getLogger(__name__)


class GenerationPriority(Enum):
    """Priority levels for content generation."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ContentGenerationRequest:
    """Enhanced request for content generation."""
    concept: CharacterConcept
    content_types: List[ContentType]
    constraints: Optional[GenerationConstraints] = None
    generation_method: GenerationMethod = GenerationMethod.CONCEPT_DRIVEN
    require_balance_validation: bool = True
    max_alternatives: int = 1
    priority: GenerationPriority = GenerationPriority.NORMAL
    timeout_seconds: int = 300
    enable_iterative_refinement: bool = True
    target_quality_threshold: float = 0.8
    
    def __post_init__(self):
        """Validate request parameters."""
        if not self.concept or not self.concept.background_story:
            raise ValueError("Valid character concept with background story required")
        
        if not self.content_types:
            raise ValueError("At least one content type must be specified")
        
        if self.max_alternatives < 1:
            raise ValueError("Max alternatives must be at least 1")


@dataclass
class ContentGenerationResponse:
    """Enhanced response from content generation."""
    success: bool
    generated_collection: Optional[ContentCollection] = None
    validation_results: Dict[str, ValidationResult] = field(default_factory=dict)
    balance_analysis: Dict[str, BalanceMetrics] = field(default_factory=dict)
    alternatives: List[ContentCollection] = field(default_factory=list)
    generation_metadata: Dict[str, Any] = field(default_factory=dict)
    quality_scores: Dict[str, float] = field(default_factory=dict)
    iteration_history: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    processing_time: float = 0.0
    
    @property
    def overall_quality_score(self) -> float:
        """Calculate overall quality score."""
        if not self.quality_scores:
            return 0.0
        return sum(self.quality_scores.values()) / len(self.quality_scores)
    
    @property
    def is_high_quality(self) -> bool:
        """Check if generation meets high quality threshold."""
        return self.overall_quality_score >= 0.8


@dataclass
class GenerationContext:
    """Context for content generation operations."""
    request: ContentGenerationRequest
    thematic_analysis: ThematicElements
    generation_plan: Dict[str, Any]
    dependency_graph: Dict[str, List[str]]
    quality_thresholds: Dict[str, float]
    
    def get_generation_order(self) -> List[ContentType]:
        """Get optimal content generation order based on dependencies."""
        return self.generation_plan.get('generation_order', self.request.content_types)


class ContentGenerationOrchestrator:
    """Orchestrates complex content generation workflows."""
    
    def __init__(self, content_generator: ContentGeneratorService,
                 balance_analyzer: BalanceAnalyzerService,
                 concept_processor: ConceptProcessorUseCase):
        self.content_generator = content_generator
        self.balance_analyzer = balance_analyzer
        self.concept_processor = concept_processor
        self.generation_history: Dict[str, List[Dict[str, Any]]] = {}
    
    async def generate_with_context(self, context: GenerationContext) -> ContentGenerationResponse:
        """Generate content with full context and orchestration."""
        start_time = datetime.now()
        response = ContentGenerationResponse(success=False)
        
        try:
            # Initialize response metadata
            response.generation_metadata = {
                'start_time': start_time,
                'generation_method': context.request.generation_method.value,
                'content_types': [ct.value for ct in context.request.content_types],
                'concept_id': context.request.concept.concept_id
            }
            
            # Generate content following dependency order
            generated_items = {}
            generation_order = context.get_generation_order()
            
            for content_type in generation_order:
                logger.info(f"Generating {content_type.value} content")
                
                # Generate content with dependencies
                content_result = await self._generate_single_content_type(
                    content_type, context, generated_items
                )
                
                if content_result.success:
                    generated_items[content_type] = content_result.content
                    response.quality_scores[content_type.value] = content_result.quality_score
                    response.iteration_history.extend(content_result.iterations)
                else:
                    response.errors.extend(content_result.errors)
                    if content_type in context.generation_plan.get('critical_content', []):
                        # Critical content failed - abort generation
                        response.errors.append(f"Critical content {content_type.value} generation failed")
                        return response
            
            # Create content collection
            if generated_items:
                collection = self._create_content_collection(
                    context.request.concept, generated_items, context.thematic_analysis
                )
                response.generated_collection = collection
                
                # Perform collection-level validation
                collection_validation = await self._validate_content_collection(
                    collection, context
                )
                response.validation_results = collection_validation
                
                # Perform balance analysis
                if context.request.require_balance_validation:
                    balance_results = await self._analyze_collection_balance(
                        collection, context
                    )
                    response.balance_analysis = balance_results
                
                # Generate alternatives if requested
                if context.request.max_alternatives > 1:
                    alternatives = await self._generate_alternatives(
                        context, generated_items, collection
                    )
                    response.alternatives = alternatives
                
                response.success = True
            
            # Record processing time
            response.processing_time = (datetime.now() - start_time).total_seconds()
            
            # Add final warnings
            self._add_generation_warnings(response, context)
            
        except asyncio.TimeoutError:
            response.errors.append(f"Generation timed out after {context.request.timeout_seconds} seconds")
        except Exception as e:
            logger.error(f"Content generation failed: {e}", exc_info=True)
            response.errors.append(f"Generation failed: {str(e)}")
        
        return response
    
    async def _generate_single_content_type(self, content_type: ContentType,
                                          context: GenerationContext,
                                          existing_content: Dict[ContentType, Any]) -> 'SingleContentResult':
        """Generate content for a single content type with refinement."""
        result = SingleContentResult(content_type=content_type)
        
        try:
            # Create generation constraints
            constraints = self._create_content_constraints(
                content_type, context, existing_content
            )
            
            # Initial generation attempt
            content = await self._generate_content_by_type(
                content_type, context.request.concept, 
                context.thematic_analysis, constraints
            )
            
            # Validate and refine if enabled
            if context.request.enable_iterative_refinement:
                refined_result = await self._refine_content_iteratively(
                    content, content_type, context, constraints
                )
                result.content = refined_result.content
                result.quality_score = refined_result.quality_score
                result.iterations = refined_result.iterations
            else:
                # Single validation
                validation = await self._validate_single_content(
                    content, content_type, constraints
                )
                quality_score = self._calculate_content_quality_score(
                    content, validation, content_type
                )
                
                result.content = content
                result.quality_score = quality_score
                result.iterations = [{'iteration': 1, 'quality_score': quality_score}]
            
            result.success = True
            
        except Exception as e:
            logger.error(f"Failed to generate {content_type.value}: {e}")
            result.errors.append(f"Generation failed: {str(e)}")
        
        return result
    
    async def _refine_content_iteratively(self, initial_content: Dict[str, Any],
                                        content_type: ContentType,
                                        context: GenerationContext,
                                        constraints: GenerationConstraints) -> 'RefinementResult':
        """Iteratively refine content until quality threshold is met."""
        current_content = initial_content
        iterations = []
        max_iterations = 5
        target_quality = context.quality_thresholds.get(content_type.value, 0.8)
        
        for iteration in range(1, max_iterations + 1):
            # Validate current content
            validation = await self._validate_single_content(
                current_content, content_type, constraints
            )
            
            quality_score = self._calculate_content_quality_score(
                current_content, validation, content_type
            )
            
            iterations.append({
                'iteration': iteration,
                'quality_score': quality_score,
                'validation_issues': len(validation.issues) if hasattr(validation, 'issues') else 0
            })
            
            # Check if quality threshold is met
            if quality_score >= target_quality:
                logger.info(f"Quality threshold reached for {content_type.value} after {iteration} iterations")
                break
            
            # Generate refinement suggestions
            if hasattr(validation, 'issues') and validation.issues:
                refinement_suggestions = self._generate_refinement_suggestions(
                    validation.issues, content_type
                )
                
                # Apply refinements
                refined_content = await self._apply_content_refinements(
                    current_content, refinement_suggestions, content_type, context
                )
                
                if refined_content:
                    current_content = refined_content
            else:
                # No clear improvement path
                logger.warning(f"No clear refinement path for {content_type.value} at iteration {iteration}")
                break
        
        return RefinementResult(
            content=current_content,
            quality_score=quality_score,
            iterations=iterations
        )
    
    async def _generate_content_by_type(self, content_type: ContentType,
                                      concept: CharacterConcept,
                                      themes: ThematicElements,
                                      constraints: GenerationConstraints) -> Dict[str, Any]:
        """Generate content using appropriate specialized generator."""
        generation_params = {
            'concept': concept,
            'themes': themes,
            'constraints': constraints,
            'generation_method': 'theme_driven'
        }
        
        if content_type == ContentType.SPECIES:
            return await self.content_generator.generate_species(**generation_params)
        elif content_type == ContentType.CHARACTER_CLASS:
            return await self.content_generator.generate_character_class(**generation_params)
        elif content_type == ContentType.EQUIPMENT:
            return await self.content_generator.generate_equipment(**generation_params)
        elif content_type == ContentType.SPELL:
            return await self.content_generator.generate_spell(**generation_params)
        elif content_type == ContentType.FEAT:
            return await self.content_generator.generate_feat(**generation_params)
        else:
            raise GenerationError(f"Unsupported content type: {content_type.value}")
    
    def _create_content_constraints(self, content_type: ContentType,
                                  context: GenerationContext,
                                  existing_content: Dict[ContentType, Any]) -> GenerationConstraints:
        """Create content-specific constraints with dependencies."""
        base_constraints = context.request.constraints or GenerationConstraints()
        
        # Add dependency constraints
        dependency_constraints = self._derive_dependency_constraints(
            content_type, existing_content, context.dependency_graph
        )
        
        # Add thematic constraints
        thematic_constraints = self._derive_thematic_constraints(
            content_type, context.thematic_analysis
        )
        
        # Merge all constraints
        return GenerationConstraints.merge(
            base_constraints, dependency_constraints, thematic_constraints
        )
    
    def _derive_dependency_constraints(self, content_type: ContentType,
                                     existing_content: Dict[ContentType, Any],
                                     dependency_graph: Dict[str, List[str]]) -> GenerationConstraints:
        """Derive constraints based on existing content dependencies."""
        constraints = GenerationConstraints()
        
        # Get dependencies for this content type
        dependencies = dependency_graph.get(content_type.value, [])
        
        for dep_type_name in dependencies:
            try:
                dep_type = ContentType(dep_type_name)
                if dep_type in existing_content:
                    dep_content = existing_content[dep_type]
                    # Extract relevant constraints from dependent content
                    dep_constraints = self._extract_constraints_from_content(dep_content, dep_type)
                    constraints = GenerationConstraints.merge(constraints, dep_constraints)
            except ValueError:
                logger.warning(f"Unknown dependency content type: {dep_type_name}")
        
        return constraints
    
    def _derive_thematic_constraints(self, content_type: ContentType,
                                   themes: ThematicElements) -> GenerationConstraints:
        """Derive constraints based on thematic elements."""
        constraints = GenerationConstraints()
        
        # Map themes to content-specific constraints
        theme_mappings = {
            ContentType.SPECIES: self._map_species_theme_constraints,
            ContentType.CHARACTER_CLASS: self._map_class_theme_constraints,
            ContentType.EQUIPMENT: self._map_equipment_theme_constraints,
            ContentType.SPELL: self._map_spell_theme_constraints,
            ContentType.FEAT: self._map_feat_theme_constraints
        }
        
        mapper = theme_mappings.get(content_type)
        if mapper:
            return mapper(themes)
        
        return constraints
    
    # Theme constraint mapping methods
    def _map_species_theme_constraints(self, themes: ThematicElements) -> GenerationConstraints:
        """Map themes to species-specific constraints."""
        constraints = GenerationConstraints()
        
        if 'celestial' in themes.primary_themes:
            constraints.add_constraint('heritage', 'celestial')
            constraints.add_constraint('alignment_tendency', 'good')
        
        if 'infernal' in themes.primary_themes:
            constraints.add_constraint('heritage', 'fiendish')
            constraints.add_constraint('resistance_type', 'fire')
        
        if 'elemental' in themes.primary_themes:
            constraints.add_constraint('elemental_affinity', themes.primary_themes[0])
        
        return constraints
    
    def _map_class_theme_constraints(self, themes: ThematicElements) -> GenerationConstraints:
        """Map themes to class-specific constraints."""
        constraints = GenerationConstraints()
        
        magic_themes = ['arcane', 'divine', 'elemental', 'nature']
        if any(theme in magic_themes for theme in themes.primary_themes):
            constraints.add_constraint('spellcasting', True)
            
        if 'martial' in themes.primary_themes:
            constraints.add_constraint('combat_focus', 'melee')
            constraints.add_constraint('hit_die', 'd10')
        
        return constraints
    
    def _map_equipment_theme_constraints(self, themes: ThematicElements) -> GenerationConstraints:
        """Map themes to equipment-specific constraints."""
        constraints = GenerationConstraints()
        
        if 'shadow' in themes.primary_themes:
            constraints.add_constraint('equipment_style', 'stealth')
            constraints.add_constraint('color_scheme', 'dark')
        
        if 'celestial' in themes.primary_themes:
            constraints.add_constraint('material_type', 'blessed')
            constraints.add_constraint('damage_type', 'radiant')
        
        return constraints
    
    def _map_spell_theme_constraints(self, themes: ThematicElements) -> GenerationConstraints:
        """Map themes to spell-specific constraints."""
        constraints = GenerationConstraints()
        
        theme_school_mapping = {
            'arcane': 'evocation',
            'divine': 'abjuration',
            'nature': 'transmutation',
            'shadow': 'illusion',
            'elemental': 'evocation'
        }
        
        for theme in themes.primary_themes:
            if theme in theme_school_mapping:
                constraints.add_constraint('preferred_school', theme_school_mapping[theme])
                break
        
        return constraints
    
    def _map_feat_theme_constraints(self, themes: ThematicElements) -> GenerationConstraints:
        """Map themes to feat-specific constraints."""
        constraints = GenerationConstraints()
        
        if 'martial' in themes.primary_themes:
            constraints.add_constraint('feat_category', 'combat')
        
        if 'scholarly' in themes.primary_themes:
            constraints.add_constraint('feat_category', 'skill')
        
        return constraints
    
    def _extract_constraints_from_content(self, content: Dict[str, Any],
                                        content_type: ContentType) -> GenerationConstraints:
        """Extract constraints from existing content."""
        constraints = GenerationConstraints()
        
        # Extract type-specific constraints
        if content_type == ContentType.SPECIES:
            if 'abilities' in content:
                constraints.add_constraint('species_abilities', content['abilities'])
            if 'size' in content:
                constraints.add_constraint('size_compatibility', content['size'])
        
        elif content_type == ContentType.CHARACTER_CLASS:
            if 'spellcasting' in content:
                constraints.add_constraint('spellcasting_available', True)
            if 'primary_ability' in content:
                constraints.add_constraint('primary_ability', content['primary_ability'])
        
        return constraints
    
    async def _validate_single_content(self, content: Dict[str, Any],
                                     content_type: ContentType,
                                     constraints: GenerationConstraints) -> ValidationResult:
        """Validate a single piece of generated content."""
        # Delegate to content generator's validation system
        return await self.content_generator.validate_content(content, content_type, constraints)
    
    def _calculate_content_quality_score(self, content: Dict[str, Any],
                                       validation: ValidationResult,
                                       content_type: ContentType) -> float:
        """Calculate quality score for generated content."""
        base_score = 1.0
        
        # Reduce score for validation issues
        if hasattr(validation, 'issues'):
            error_count = sum(1 for issue in validation.issues if issue.severity == ValidationSeverity.ERROR)
            warning_count = sum(1 for issue in validation.issues if issue.severity == ValidationSeverity.WARNING)
            
            base_score -= (error_count * 0.3) + (warning_count * 0.1)
        
        # Add score for content richness
        richness_bonus = self._calculate_content_richness_bonus(content, content_type)
        base_score += richness_bonus
        
        # Add score for thematic consistency
        thematic_bonus = self._calculate_thematic_consistency_bonus(content, content_type)
        base_score += thematic_bonus
        
        return max(0.0, min(base_score, 1.0))
    
    def _calculate_content_richness_bonus(self, content: Dict[str, Any],
                                        content_type: ContentType) -> float:
        """Calculate bonus for content richness and detail."""
        bonus = 0.0
        
        # Check for detailed descriptions
        if content.get('description') and len(content['description']) > 100:
            bonus += 0.1
        
        # Check for mechanical depth
        if content_type == ContentType.CHARACTER_CLASS:
            if len(content.get('features', [])) >= 3:
                bonus += 0.1
        elif content_type == ContentType.SPECIES:
            if len(content.get('traits', [])) >= 2:
                bonus += 0.1
        
        return min(bonus, 0.2)
    
    def _calculate_thematic_consistency_bonus(self, content: Dict[str, Any],
                                           content_type: ContentType) -> float:
        """Calculate bonus for thematic consistency."""
        # Placeholder - would analyze content for thematic alignment
        return 0.05
    
    def _generate_refinement_suggestions(self, issues: List[Any],
                                       content_type: ContentType) -> List[str]:
        """Generate suggestions for content refinement based on validation issues."""
        suggestions = []
        
        for issue in issues:
            if hasattr(issue, 'issue_type'):
                if issue.issue_type == 'balance':
                    suggestions.append('reduce_power_level')
                elif issue.issue_type == 'rules':
                    suggestions.append('fix_rule_violation')
                elif issue.issue_type == 'theme':
                    suggestions.append('improve_thematic_consistency')
        
        return suggestions
    
    async def _apply_content_refinements(self, content: Dict[str, Any],
                                       suggestions: List[str],
                                       content_type: ContentType,
                                       context: GenerationContext) -> Optional[Dict[str, Any]]:
        """Apply refinement suggestions to content."""
        try:
            # Create refinement parameters
            refinement_params = {
                'original_content': content,
                'suggestions': suggestions,
                'content_type': content_type,
                'concept': context.request.concept
            }
            
            # Apply refinements through content generator
            return await self.content_generator.refine_content(**refinement_params)
        
        except Exception as e:
            logger.warning(f"Failed to apply refinements: {e}")
            return None
    
    def _create_content_collection(self, concept: CharacterConcept,
                                 generated_items: Dict[ContentType, Any],
                                 themes: ThematicElements) -> ContentCollection:
        """Create a content collection from generated items."""
        collection_id = f"gen_{concept.concept_id}_{int(datetime.now().timestamp())}"
        
        # Convert to GeneratedContent objects
        content_objects = {}
        for content_type, content_data in generated_items.items():
            generated_content = GeneratedContent(
                content_id=f"{collection_id}_{content_type.value}",
                content_type=content_type,
                name=content_data.get('name', f"Generated {content_type.value}"),
                content_data=content_data,
                source_concept_id=concept.concept_id,
                themes=themes.primary_themes
            )
            
            if content_type not in content_objects:
                content_objects[content_type] = []
            content_objects[content_type].append(generated_content)
        
        return ContentCollection(
            collection_id=collection_id,
            name=f"Generated Content for {concept.concept_name}",
            description=f"Complete content suite generated from concept: {concept.concept_name}",
            content_items=content_objects,
            primary_themes=themes.primary_themes,
            creation_metadata={
                'source_concept': concept.concept_id,
                'generation_timestamp': datetime.now(),
                'generation_method': 'orchestrated_theme_driven'
            }
        )
    
    async def _validate_content_collection(self, collection: ContentCollection,
                                         context: GenerationContext) -> Dict[str, ValidationResult]:
        """Validate the entire content collection for coherence."""
        validation_results = {}
        
        # Validate individual items
        for content_type, items in collection.content_items.items():
            for item in items:
                validation = await self._validate_single_content(
                    item.content_data, content_type, 
                    self._create_content_constraints(content_type, context, {})
                )
                validation_results[item.content_id] = validation
        
        # Validate collection coherence
        coherence_validation = await self._validate_collection_coherence(collection)
        validation_results['collection_coherence'] = coherence_validation
        
        return validation_results
    
    async def _validate_collection_coherence(self, collection: ContentCollection) -> ValidationResult:
        """Validate coherence across the entire collection."""
        issues = []
        
        # Check thematic consistency
        all_themes = set()
        for items in collection.content_items.values():
            for item in items:
                all_themes.update(item.themes)
        
        if len(all_themes) > len(collection.primary_themes) * 2:
            issues.append("Collection contains too many disparate themes")
        
        # Check mechanical compatibility
        # (Would implement detailed compatibility checks)
        
        return ValidationResult(
            is_valid=len(issues) == 0,
            issues=issues,
            validation_type='collection_coherence'
        )
    
    async def _analyze_collection_balance(self, collection: ContentCollection,
                                        context: GenerationContext) -> Dict[str, BalanceMetrics]:
        """Analyze balance for the entire collection."""
        return await self.balance_analyzer.analyze_collection_balance(collection)
    
    async def _generate_alternatives(self, context: GenerationContext,
                                   base_content: Dict[ContentType, Any],
                                   base_collection: ContentCollection) -> List[ContentCollection]:
        """Generate alternative content collections."""
        alternatives = []
        
        try:
            for i in range(context.request.max_alternatives - 1):
                # Create variation in generation approach
                varied_context = self._create_variation_context(context, i)
                
                # Generate alternative content
                alt_response = await self.generate_with_context(varied_context)
                
                if alt_response.success and alt_response.generated_collection:
                    alternatives.append(alt_response.generated_collection)
        
        except Exception as e:
            logger.warning(f"Failed to generate alternatives: {e}")
        
        return alternatives
    
    def _create_variation_context(self, base_context: GenerationContext,
                                variation_index: int) -> GenerationContext:
        """Create a variation of the generation context."""
        # Create slight variations in constraints or approach
        varied_request = ContentGenerationRequest(
            concept=base_context.request.concept,
            content_types=base_context.request.content_types,
            constraints=base_context.request.constraints,
            generation_method=base_context.request.generation_method,
            require_balance_validation=base_context.request.require_balance_validation,
            max_alternatives=1,  # Don't generate alternatives of alternatives
            enable_iterative_refinement=False  # Use different approach for variations
        )
        
        # Vary quality thresholds slightly
        varied_thresholds = base_context.quality_thresholds.copy()
        for content_type in varied_thresholds:
            varied_thresholds[content_type] *= (0.9 + (variation_index * 0.05))
        
        return GenerationContext(
            request=varied_request,
            thematic_analysis=base_context.thematic_analysis,
            generation_plan=base_context.generation_plan,
            dependency_graph=base_context.dependency_graph,
            quality_thresholds=varied_thresholds
        )
    
    def _add_generation_warnings(self, response: ContentGenerationResponse,
                               context: GenerationContext):
        """Add warnings based on generation results."""
        if response.overall_quality_score < 0.6:
            response.warnings.append("Generated content quality is below recommended threshold")
        
        if len(response.errors) > 0:
            response.warnings.append("Some content generation failed - collection may be incomplete")
        
        if context.request.enable_iterative_refinement and not response.iteration_history:
            response.warnings.append("Iterative refinement was requested but not performed")


# Helper classes for internal operations
@dataclass
class SingleContentResult:
    """Result from single content type generation."""
    content_type: ContentType
    success: bool = False
    content: Optional[Dict[str, Any]] = None
    quality_score: float = 0.0
    iterations: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


@dataclass 
class RefinementResult:
    """Result from iterative content refinement."""
    content: Dict[str, Any]
    quality_score: float
    iterations: List[Dict[str, Any]]


class GenerateContentUseCase:
    """
    Primary use case interface for content generation workflows.
    
    This class provides a simplified interface to the ContentGenerationOrchestrator
    for common generation scenarios while maintaining access to advanced features.
    """
    
    def __init__(self, content_generator: ContentGeneratorService,
                 balance_analyzer: BalanceAnalyzerService,
                 concept_processor: ConceptProcessorUseCase):
        self.orchestrator = ContentGenerationOrchestrator(
            content_generator, balance_analyzer, concept_processor
        )
        self.concept_processor = concept_processor
    
    async def execute(self, request: ContentGenerationRequest) -> ContentGenerationResponse:
        """
        Execute content generation with comprehensive orchestration.
        
        Args:
            request: Content generation request
            
        Returns:
            Content generation response with generated content and analysis
        """
        try:
            # Ensure concept is fully analyzed
            if not hasattr(request.concept, 'thematic_elements') or not request.concept.thematic_elements:
                analysis_request = ConceptAnalysisRequest(
                    raw_concept=request.concept.background_story,
                    character_name=request.concept.concept_name,
                    target_level=getattr(request.concept, 'target_level', 1),
                    preferred_content_types=request.content_types
                )
                
                analysis_response = await self.concept_processor.execute(analysis_request)
                if not analysis_response.success:
                    return ContentGenerationResponse(
                        success=False,
                        errors=[f"Concept analysis failed: {'; '.join(analysis_response.errors)}"]
                    )
                
                request.concept = analysis_response.processed_concept
            
            # Create generation context
            context = self._create_generation_context(request)
            
            # Execute orchestrated generation
            return await self.orchestrator.generate_with_context(context)
        
        except Exception as e:
            logger.error(f"Content generation use case failed: {e}", exc_info=True)
            return ContentGenerationResponse(
                success=False,
                errors=[f"Generation failed: {str(e)}"]
            )
    
    def _create_generation_context(self, request: ContentGenerationRequest) -> GenerationContext:
        """Create generation context from request."""
        # Create generation plan
        generation_plan = self._create_generation_plan(request)
        
        # Create dependency graph
        dependency_graph = self._create_dependency_graph(request.content_types)
        
        # Set quality thresholds
        quality_thresholds = {
            content_type.value: request.target_quality_threshold
            for content_type in request.content_types
        }
        
        return GenerationContext(
            request=request,
            thematic_analysis=request.concept.thematic_elements,
            generation_plan=generation_plan,
            dependency_graph=dependency_graph,
            quality_thresholds=quality_thresholds
        )
    
    def _create_generation_plan(self, request: ContentGenerationRequest) -> Dict[str, Any]:
        """Create generation plan based on request."""
        # Determine optimal generation order
        order_priorities = {
            ContentType.SPECIES: 1,
            ContentType.CHARACTER_CLASS: 2,
            ContentType.FEAT: 3,
            ContentType.SPELL: 4,
            ContentType.EQUIPMENT: 5
        }
        
        generation_order = sorted(
            request.content_types,
            key=lambda ct: order_priorities.get(ct, 999)
        )
        
        return {
            'generation_order': generation_order,
            'critical_content': [ContentType.SPECIES, ContentType.CHARACTER_CLASS],
            'optional_content': [ContentType.EQUIPMENT],
            'parallel_generation': False  # Sequential for dependency management
        }
    
    def _create_dependency_graph(self, content_types: List[ContentType]) -> Dict[str, List[str]]:
        """Create dependency graph for content types."""
        dependencies = {
            ContentType.CHARACTER_CLASS.value: [ContentType.SPECIES.value],
            ContentType.FEAT.value: [ContentType.SPECIES.value, ContentType.CHARACTER_CLASS.value],
            ContentType.SPELL.value: [ContentType.CHARACTER_CLASS.value],
            ContentType.EQUIPMENT.value: [ContentType.CHARACTER_CLASS.value]
        }
        
        # Filter to only include requested content types
        requested_type_names = {ct.value for ct in content_types}
        filtered_dependencies = {}
        
        for content_type, deps in dependencies.items():
            if content_type in requested_type_names:
                filtered_deps = [dep for dep in deps if dep in requested_type_names]
                filtered_dependencies[content_type] = filtered_deps
        
        return filtered_dependencies


# Specialized use case classes for common scenarios
class GenerateSpeciesUseCase:
    """Specialized use case for species generation."""
    
    def __init__(self, generate_content_use_case: GenerateContentUseCase):
        self.generate_content = generate_content_use_case
    
    async def execute(self, concept: CharacterConcept, 
                     constraints: Optional[GenerationConstraints] = None) -> ContentGenerationResponse:
        """Generate species from concept."""
        request = ContentGenerationRequest(
            concept=concept,
            content_types=[ContentType.SPECIES],
            constraints=constraints,
            enable_iterative_refinement=True,
            target_quality_threshold=0.85
        )
        return await self.generate_content.execute(request)


class GenerateClassUseCase:
    """Specialized use case for class generation."""
    
    def __init__(self, generate_content_use_case: GenerateContentUseCase):
        self.generate_content = generate_content_use_case
    
    async def execute(self, concept: CharacterConcept, 
                     constraints: Optional[GenerationConstraints] = None) -> ContentGenerationResponse:
        """Generate class from concept."""
        request = ContentGenerationRequest(
            concept=concept,
            content_types=[ContentType.CHARACTER_CLASS],
            constraints=constraints,
            enable_iterative_refinement=True,
            target_quality_threshold=0.9  # Classes need high quality
        )
        return await self.generate_content.execute(request)


class GenerateEquipmentUseCase:
    """Specialized use case for equipment generation."""
    
    def __init__(self, generate_content_use_case: GenerateContentUseCase):
        self.generate_content = generate_content_use_case
    
    async def execute(self, concept: CharacterConcept, 
                     constraints: Optional[GenerationConstraints] = None) -> ContentGenerationResponse:
        """Generate equipment from concept."""
        request = ContentGenerationRequest(
            concept=concept,
            content_types=[ContentType.EQUIPMENT],
            constraints=constraints,
            max_alternatives=2,  # Equipment can have more variations
            target_quality_threshold=0.75
        )
        return await self.generate_content.execute(request)


class GenerateSpellSuiteUseCase:
    """Specialized use case for spell generation."""
    
    def __init__(self, generate_content_use_case: GenerateContentUseCase):
        self.generate_content = generate_content_use_case
    
    async def execute(self, concept: CharacterConcept, 
                     constraints: Optional[GenerationConstraints] = None) -> ContentGenerationResponse:
        """Generate spell suite from concept."""
        request = ContentGenerationRequest(
            concept=concept,
            content_types=[ContentType.SPELL],
            constraints=constraints,
            max_alternatives=3,  # Generate multiple spell options
            enable_iterative_refinement=True,
            target_quality_threshold=0.8
        )
        return await self.generate_content.execute(request)


class GenerateCompleteCharacterUseCase:
    """Generate complete character with all custom content."""
    
    def __init__(self, generate_content_use_case: GenerateContentUseCase):
        self.generate_content = generate_content_use_case
    
    async def execute(self, concept: CharacterConcept, 
                     constraints: Optional[GenerationConstraints] = None) -> ContentGenerationResponse:
        """Generate complete character content suite."""
        request = ContentGenerationRequest(
            concept=concept,
            content_types=[
                ContentType.SPECIES,
                ContentType.CHARACTER_CLASS,
                ContentType.EQUIPMENT,
                ContentType.SPELL,
                ContentType.FEAT
            ],
            constraints=constraints,
            max_alternatives=2,
            enable_iterative_refinement=True,
            target_quality_threshold=0.8,
            timeout_seconds=600,  # Longer timeout for complete generation
            priority=GenerationPriority.HIGH
        )
        return await self.generate_content.execute(request)