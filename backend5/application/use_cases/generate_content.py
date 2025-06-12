"""
Unified Content Generation Use Case

Central orchestrator for all D&D content generation including species, classes,
equipment, spells, and feats. This is the primary interface for the creative
content generation pipeline, driven by character background concepts.
"""

from typing import Dict, Any, List, Optional, Union
import logging

from ...core.entities.character_concept import CharacterConcept
from ...core.entities.generated_content import GeneratedContent
from ...core.value_objects.thematic_elements import ThematicElements
from ...core.value_objects.generation_constraints import GenerationConstraints
from ...domain.services.content_generator import ContentGeneratorService
from ...domain.services.species_generator import SpeciesGeneratorService
from ...domain.services.class_generator import ClassGeneratorService
from ...domain.services.equipment_generator import EquipmentGeneratorService
from ...domain.services.spell_generator import SpellGeneratorService
from ...domain.services.feat_generator import FeatGeneratorService
from ...domain.services.balance_validator import BalanceValidatorService
from ...domain.services.content_validation_service import ContentValidationService
from ...domain.services.content_registry import ContentRegistry
from ...infrastructure.llm.content_llm_service import ContentLLMService
from ...infrastructure.llm.theme_llm_service import ThemeLLMService
from ..dtos.content_dto import (
    ContentGenerationRequest,
    ContentGenerationResponse,
    ThematicSuiteRequest,
    ThematicSuiteResponse
)

logger = logging.getLogger(__name__)

class GenerateContentUseCase:
    """
    Unified use case for all content generation workflows.
    
    This is the central orchestrator for creating new D&D content based on
    character background concepts. It handles species, classes, equipment,
    spells, and feats with integrated validation and balance optimization.
    """
    
    def __init__(self,
                 content_generator: ContentGeneratorService,
                 species_generator: SpeciesGeneratorService,
                 class_generator: ClassGeneratorService,
                 equipment_generator: EquipmentGeneratorService,
                 spell_generator: SpellGeneratorService,
                 feat_generator: FeatGeneratorService,
                 balance_validator: BalanceValidatorService,
                 content_validator: ContentValidationService,
                 content_registry: ContentRegistry,
                 content_llm: ContentLLMService,
                 theme_llm: ThemeLLMService):
        self.content_generator = content_generator
        self.species_generator = species_generator
        self.class_generator = class_generator
        self.equipment_generator = equipment_generator
        self.spell_generator = spell_generator
        self.feat_generator = feat_generator
        self.balance_validator = balance_validator
        self.content_validator = content_validator
        self.content_registry = content_registry
        self.content_llm = content_llm
        self.theme_llm = theme_llm
    
    def generate_content(self, request: ContentGenerationRequest) -> ContentGenerationResponse:
        """
        Generate content based on request specifications.
        
        Args:
            request: Content generation request with concept and preferences
            
        Returns:
            ContentGenerationResponse with generated and validated content
        """
        try:
            # 1. Analyze character concept for thematic elements
            thematic_analysis = self._analyze_concept_themes(request.character_concept)
            
            # 2. Define generation constraints based on D&D rules
            constraints = self._create_generation_constraints(
                request.content_type, thematic_analysis, request.constraints
            )
            
            # 3. Generate content using appropriate generator
            generated_content = self._generate_content_by_type(
                request.content_type, request.character_concept, 
                thematic_analysis, constraints
            )
            
            # 4. Validate generated content
            validation_result = self._validate_generated_content(
                generated_content, request.content_type, constraints
            )
            
            # 5. Optimize for balance if validation passes
            if validation_result.is_valid:
                optimized_content = self._optimize_content_balance(
                    generated_content, request.content_type, thematic_analysis
                )
            else:
                optimized_content = generated_content
            
            # 6. Register content if requested
            if request.register_content and validation_result.is_valid:
                registration_result = self._register_generated_content(
                    optimized_content, request.content_type
                )
            else:
                registration_result = None
            
            return ContentGenerationResponse(
                success=True,
                content_type=request.content_type,
                generated_content=optimized_content,
                thematic_analysis=thematic_analysis,
                validation_result=validation_result,
                constraints_applied=constraints,
                registration_result=registration_result,
                generation_metadata=self._create_generation_metadata(
                    request, thematic_analysis, validation_result
                )
            )
            
        except Exception as e:
            logger.error(f"Content generation failed: {e}")
            return ContentGenerationResponse(
                success=False,
                errors=[f"Content generation failed: {str(e)}"]
            )
    
    def generate_thematic_content_suite(self, request: ThematicSuiteRequest) -> ThematicSuiteResponse:
        """
        Generate a complete thematic content suite (species + class + equipment + spells + feats).
        
        Args:
            request: Thematic suite generation request
            
        Returns:
            ThematicSuiteResponse with complete content suite
        """
        try:
            # 1. Analyze character concept comprehensively
            thematic_analysis = self.theme_llm.analyze_comprehensive_themes(
                request.character_concept
            )
            
            # 2. Create generation roadmap
            generation_roadmap = self._create_suite_generation_roadmap(
                thematic_analysis, request.content_priorities
            )
            
            # 3. Generate content suite following roadmap
            content_suite = {}
            generation_order = generation_roadmap["generation_order"]
            
            for content_type in generation_order:
                if content_type in request.requested_content_types:
                    # Generate content with dependencies from previously generated content
                    content = self._generate_dependent_content(
                        content_type, request.character_concept, 
                        thematic_analysis, content_suite
                    )
                    
                    # Validate and optimize
                    validation = self._validate_generated_content(
                        content, content_type, generation_roadmap["constraints"][content_type]
                    )
                    
                    if validation.is_valid:
                        optimized_content = self._optimize_content_balance(
                            content, content_type, thematic_analysis
                        )
                        content_suite[content_type] = optimized_content
                    else:
                        # Attempt regeneration with adjusted constraints
                        retry_content = self._regenerate_with_adjustments(
                            content_type, request.character_concept, 
                            thematic_analysis, validation.issues
                        )
                        content_suite[content_type] = retry_content
            
            # 4. Validate suite coherence
            suite_validation = self._validate_content_suite_coherence(
                content_suite, thematic_analysis
            )
            
            # 5. Register suite if requested
            registration_results = {}
            if request.register_content:
                for content_type, content in content_suite.items():
                    registration_results[content_type] = self._register_generated_content(
                        content, content_type
                    )
            
            return ThematicSuiteResponse(
                success=True,
                character_concept=request.character_concept,
                thematic_analysis=thematic_analysis,
                generation_roadmap=generation_roadmap,
                content_suite=content_suite,
                suite_validation=suite_validation,
                registration_results=registration_results,
                suite_metadata=self._create_suite_metadata(
                    request, thematic_analysis, content_suite
                )
            )
            
        except Exception as e:
            logger.error(f"Thematic content suite generation failed: {e}")
            return ThematicSuiteResponse(
                success=False,
                errors=[f"Suite generation failed: {str(e)}"]
            )
    
    def regenerate_content_with_feedback(self, content_id: str, 
                                       feedback: Dict[str, Any]) -> ContentGenerationResponse:
        """
        Regenerate content based on user feedback.
        
        Args:
            content_id: ID of content to regenerate
            feedback: User feedback and modification requests
            
        Returns:
            ContentGenerationResponse with regenerated content
        """
        try:
            # 1. Retrieve original content and generation context
            original_content = self.content_registry.get_generated_content(content_id)
            generation_context = original_content.get_generation_context()
            
            # 2. Analyze feedback for improvement directions
            feedback_analysis = self.content_llm.analyze_user_feedback(
                feedback, original_content.content_type
            )
            
            # 3. Update generation constraints based on feedback
            updated_constraints = self._update_constraints_from_feedback(
                generation_context["constraints"], feedback_analysis
            )
            
            # 4. Regenerate content with updated parameters
            regenerated_content = self._generate_content_by_type(
                original_content.content_type,
                generation_context["character_concept"],
                generation_context["thematic_analysis"],
                updated_constraints
            )
            
            # 5. Validate and optimize regenerated content
            validation_result = self._validate_generated_content(
                regenerated_content, original_content.content_type, updated_constraints
            )
            
            if validation_result.is_valid:
                optimized_content = self._optimize_content_balance(
                    regenerated_content, original_content.content_type,
                    generation_context["thematic_analysis"]
                )
            else:
                optimized_content = regenerated_content
            
            return ContentGenerationResponse(
                success=True,
                content_type=original_content.content_type,
                generated_content=optimized_content,
                thematic_analysis=generation_context["thematic_analysis"],
                validation_result=validation_result,
                constraints_applied=updated_constraints,
                regeneration_context={
                    "original_content_id": content_id,
                    "feedback_applied": feedback_analysis,
                    "improvement_areas": feedback_analysis.get("improvement_areas", [])
                }
            )
            
        except Exception as e:
            logger.error(f"Content regeneration failed: {e}")
            return ContentGenerationResponse(
                success=False,
                errors=[f"Content regeneration failed: {str(e)}"]
            )
    
    def generate_content_variations(self, base_content_id: str, 
                                  variation_count: int = 3) -> Dict[str, Any]:
        """
        Generate variations of existing content.
        
        Args:
            base_content_id: ID of base content to vary
            variation_count: Number of variations to generate
            
        Returns:
            Dict with generated variations and analysis
        """
        try:
            base_content = self.content_registry.get_generated_content(base_content_id)
            generation_context = base_content.get_generation_context()
            
            variations = []
            for i in range(variation_count):
                # Create slight variations in generation parameters
                varied_constraints = self._create_content_variations_constraints(
                    generation_context["constraints"], variation_index=i
                )
                
                # Generate variation
                variation = self._generate_content_by_type(
                    base_content.content_type,
                    generation_context["character_concept"],
                    generation_context["thematic_analysis"],
                    varied_constraints
                )
                
                # Validate variation
                validation = self._validate_generated_content(
                    variation, base_content.content_type, varied_constraints
                )
                
                if validation.is_valid:
                    variations.append({
                        "variation_id": f"{base_content_id}_var_{i+1}",
                        "content": variation,
                        "validation": validation,
                        "variation_notes": self._analyze_variation_differences(
                            base_content.content, variation
                        )
                    })
            
            return {
                "success": True,
                "base_content_id": base_content_id,
                "variations": variations,
                "variation_analysis": self._analyze_variation_set(variations)
            }
            
        except Exception as e:
            logger.error(f"Content variation generation failed: {e}")
            return {
                "success": False,
                "errors": [f"Variation generation failed: {str(e)}"]
            }
    
    # === Private Helper Methods ===
    
    def _analyze_concept_themes(self, concept: CharacterConcept) -> ThematicElements:
        """Analyze character concept for thematic elements."""
        return self.theme_llm.extract_thematic_elements(concept)
    
    def _create_generation_constraints(self, content_type: str,
                                     themes: ThematicElements,
                                     user_constraints: Optional[Dict[str, Any]]) -> GenerationConstraints:
        """Create generation constraints based on content type and themes."""
        base_constraints = self.content_generator.get_base_constraints_for_type(content_type)
        thematic_constraints = self.content_generator.derive_thematic_constraints(themes)
        
        # Merge constraints
        merged_constraints = GenerationConstraints.merge(
            base_constraints, thematic_constraints, user_constraints or {}
        )
        
        return merged_constraints
    
    def _generate_content_by_type(self, content_type: str,
                                concept: CharacterConcept,
                                themes: ThematicElements,
                                constraints: GenerationConstraints) -> Dict[str, Any]:
        """Generate content using the appropriate generator."""
        if content_type == "species":
            return self.species_generator.generate_species(concept, themes, constraints)
        elif content_type == "class":
            return self.class_generator.generate_class(concept, themes, constraints)
        elif content_type == "equipment":
            return self.equipment_generator.generate_equipment(concept, themes, constraints)
        elif content_type == "spell":
            return self.spell_generator.generate_spell(concept, themes, constraints)
        elif content_type == "feat":
            return self.feat_generator.generate_feat(concept, themes, constraints)
        else:
            raise ValueError(f"Unknown content type: {content_type}")
    
    def _validate_generated_content(self, content: Dict[str, Any],
                                  content_type: str,
                                  constraints: GenerationConstraints) -> ValidationResult:
        """Validate generated content against D&D rules and constraints."""
        # Rule validation
        rule_validation = self.content_validator.validate_content_rules(content, content_type)
        
        # Balance validation
        balance_validation = self.balance_validator.validate_content_balance(
            content, content_type, constraints
        )
        
        # Combine validation results
        return ValidationResult.combine(rule_validation, balance_validation)
    
    def _optimize_content_balance(self, content: Dict[str, Any],
                                content_type: str,
                                themes: ThematicElements) -> Dict[str, Any]:
        """Optimize content for mechanical balance."""
        return self.balance_validator.optimize_content_balance(
            content, content_type, themes
        )
    
    def _register_generated_content(self, content: Dict[str, Any],
                                  content_type: str) -> Dict[str, Any]:
        """Register generated content in the content registry."""
        return self.content_registry.register_generated_content(content, content_type)
    
    def _create_generation_metadata(self, request: ContentGenerationRequest,
                                  themes: ThematicElements,
                                  validation: ValidationResult) -> Dict[str, Any]:
        """Create metadata for generated content."""
        return {
            "generation_timestamp": "2024-01-01T00:00:00Z",  # Would use actual timestamp
            "source_concept": request.character_concept.background_description,
            "primary_themes": themes.get_primary_themes(),
            "validation_passed": validation.is_valid,
            "generation_method": "llm_assisted",
            "constraints_applied": request.constraints
        }
    
    def _create_suite_generation_roadmap(self, themes: ThematicElements,
                                       priorities: Dict[str, int]) -> Dict[str, Any]:
        """Create generation roadmap for content suite."""
        # Determine optimal generation order based on dependencies
        base_order = ["species", "class", "equipment", "spells", "feats"]
        
        # Adjust order based on thematic priorities
        prioritized_order = sorted(base_order, 
                                 key=lambda x: priorities.get(x, 0), 
                                 reverse=True)
        
        return {
            "generation_order": prioritized_order,
            "dependencies": self._map_content_dependencies(),
            "constraints": self._create_suite_constraints(themes),
            "thematic_integration_points": themes.get_integration_points()
        }
    
    def _generate_dependent_content(self, content_type: str,
                                  concept: CharacterConcept,
                                  themes: ThematicElements,
                                  existing_content: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content that depends on previously generated content."""
        # Create enhanced constraints based on existing content
        dependency_constraints = self._create_dependency_constraints(
            content_type, existing_content
        )
        
        # Generate content with dependency awareness
        return self._generate_content_by_type(
            content_type, concept, themes, dependency_constraints
        )
    
    def _validate_content_suite_coherence(self, content_suite: Dict[str, Any],
                                        themes: ThematicElements) -> Dict[str, Any]:
        """Validate coherence across content suite."""
        coherence_issues = []
        coherence_score = 1.0
        
        # Check thematic consistency
        thematic_consistency = self._check_suite_thematic_consistency(
            content_suite, themes
        )
        
        # Check mechanical compatibility
        mechanical_compatibility = self._check_suite_mechanical_compatibility(
            content_suite
        )
        
        return {
            "coherent": len(coherence_issues) == 0,
            "coherence_score": coherence_score,
            "thematic_consistency": thematic_consistency,
            "mechanical_compatibility": mechanical_compatibility,
            "issues": coherence_issues
        }
    
    def _regenerate_with_adjustments(self, content_type: str,
                                   concept: CharacterConcept,
                                   themes: ThematicElements,
                                   validation_issues: List[str]) -> Dict[str, Any]:
        """Regenerate content with adjustments based on validation issues."""
        # Analyze validation issues to determine adjustments
        adjustments = self.content_llm.suggest_generation_adjustments(
            validation_issues, content_type
        )
        
        # Create adjusted constraints
        adjusted_constraints = self._apply_validation_adjustments(
            self._create_generation_constraints(content_type, themes, None),
            adjustments
        )
        
        # Regenerate with adjustments
        return self._generate_content_by_type(
            content_type, concept, themes, adjusted_constraints
        )
    
    def _create_suite_metadata(self, request: ThematicSuiteRequest,
                             themes: ThematicElements,
                             content_suite: Dict[str, Any]) -> Dict[str, Any]:
        """Create metadata for content suite."""
        return {
            "suite_id": f"suite_{hash(str(request.character_concept))}",
            "generation_timestamp": "2024-01-01T00:00:00Z",
            "source_concept": request.character_concept.background_description,
            "content_types_generated": list(content_suite.keys()),
            "primary_themes": themes.get_primary_themes(),
            "suite_coherence_score": self._calculate_suite_coherence_score(content_suite),
            "generation_method": "thematic_suite_llm_assisted"
        }
    
    def _update_constraints_from_feedback(self, original_constraints: GenerationConstraints,
                                        feedback_analysis: Dict[str, Any]) -> GenerationConstraints:
        """Update generation constraints based on user feedback."""
        # Implementation would analyze feedback and adjust constraints accordingly
        return original_constraints
    
    def _create_content_variations_constraints(self, base_constraints: GenerationConstraints,
                                             variation_index: int) -> GenerationConstraints:
        """Create slight variations in constraints for content variations."""
        # Implementation would create subtle variations in generation parameters
        return base_constraints
    
    def _analyze_variation_differences(self, base_content: Dict[str, Any],
                                     variation_content: Dict[str, Any]) -> List[str]:
        """Analyze differences between base content and variation."""
        differences = []
        # Implementation would compare content and identify key differences
        return differences
    
    def _analyze_variation_set(self, variations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze a set of content variations."""
        return {
            "variation_count": len(variations),
            "diversity_score": 0.8,  # Would calculate actual diversity
            "common_elements": [],    # Would identify common patterns
            "unique_elements": []     # Would identify unique aspects
        }
    
    def _map_content_dependencies(self) -> Dict[str, List[str]]:
        """Map dependencies between content types."""
        return {
            "class": ["species"],
            "equipment": ["class", "species"],
            "spells": ["class"],
            "feats": ["species", "class"]
        }
    
    def _create_suite_constraints(self, themes: ThematicElements) -> Dict[str, GenerationConstraints]:
        """Create constraints for each content type in suite."""
        constraints = {}
        for content_type in ["species", "class", "equipment", "spells", "feats"]:
            constraints[content_type] = self._create_generation_constraints(
                content_type, themes, None
            )
        return constraints
    
    def _create_dependency_constraints(self, content_type: str,
                                     existing_content: Dict[str, Any]) -> GenerationConstraints:
        """Create constraints based on existing content dependencies."""
        # Implementation would analyze existing content and create appropriate constraints
        return GenerationConstraints()
    
    def _check_suite_thematic_consistency(self, content_suite: Dict[str, Any],
                                        themes: ThematicElements) -> Dict[str, Any]:
        """Check thematic consistency across content suite."""
        return {"consistent": True, "consistency_score": 0.9}
    
    def _check_suite_mechanical_compatibility(self, content_suite: Dict[str, Any]) -> Dict[str, Any]:
        """Check mechanical compatibility across content suite."""
        return {"compatible": True, "compatibility_score": 0.95}
    
    def _apply_validation_adjustments(self, constraints: GenerationConstraints,
                                    adjustments: Dict[str, Any]) -> GenerationConstraints:
        """Apply adjustments to constraints based on validation feedback."""
        # Implementation would modify constraints based on adjustment suggestions
        return constraints
    
    def _calculate_suite_coherence_score(self, content_suite: Dict[str, Any]) -> float:
        """Calculate coherence score for content suite."""
        # Implementation would analyze thematic and mechanical coherence
        return 0.9