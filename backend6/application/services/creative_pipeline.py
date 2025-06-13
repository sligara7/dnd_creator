"""
Creative Generation Pipeline

Central workflow orchestrator for the complete D&D content creation pipeline.
This implements the background-driven, rule-compliant, LLM-assisted creative
philosophy outlined in the README. All content generation flows through this
unified pipeline while maintaining clean architecture principles.
"""

from typing import Dict, Any, List, Optional
import logging

from ..use_cases.generate_content import GenerateContentUseCase
from ..use_cases.validate_content import ValidateContentUseCase
from ..use_cases.manage_character import ManageCharacterUseCase
from ..use_cases.integration_manager import IntegrationManagerUseCase
from ..dtos.content_dto import (
    ContentGenerationRequest,
    ThematicSuiteRequest,
    ContentValidationRequest,
    IntegrationRequest
)
from ..dtos.character_dto import (
    CharacterCreationRequest,
    MulticlassRequest,
    CharacterAnalysisRequest
)
from ...core.entities.character_concept import CharacterConcept
from ...core.value_objects.thematic_elements import ThematicElements
from ...infrastructure.llm.concept_llm_service import ConceptLLMService

logger = logging.getLogger(__name__)

class CreativePipeline:
    """
    Central orchestrator for the complete D&D content creation pipeline.
    
    This pipeline implements the unified creative generation philosophy:
    1. Background-driven content creation starting from character concepts
    2. Rule-compliant generation with integrated validation
    3. LLM-assisted creative enhancement throughout
    4. Modular content handling supporting all D&D content types
    5. Clean architecture with proper dependency management
    """
    
    def __init__(self,
                 content_generator: GenerateContentUseCase,
                 content_validator: ValidateContentUseCase,
                 character_manager: ManageCharacterUseCase,
                 integration_manager: IntegrationManagerUseCase,
                 concept_llm: ConceptLLMService):
        self.content_generator = content_generator
        self.content_validator = content_validator
        self.character_manager = character_manager
        self.integration_manager = integration_manager
        self.concept_llm = concept_llm
    
    def create_character_from_concept(self, background_description: str,
                                    creation_options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Complete character creation pipeline from background concept.
        
        Args:
            background_description: Natural language character description
            creation_options: Optional creation preferences
            
        Returns:
            Complete character creation results with validation and analysis
        """
        try:
            # 1. Enhance concept using LLM
            enhanced_concept = self.concept_llm.enhance_character_concept(
                background_description, creation_options or {}
            )
            
            # 2. Create character from enhanced concept
            creation_request = CharacterCreationRequest(
                background_description=background_description,
                creation_options=creation_options or {},
                apply_custom_content=True
            )
            
            character_result = self.character_manager.create_character(creation_request)
            
            if not character_result.success:
                return {
                    "success": False,
                    "stage": "character_creation",
                    "errors": character_result.errors
                }
            
            # 3. Generate custom content suite if requested
            custom_content_suite = None
            if creation_options and creation_options.get("generate_custom_content"):
                suite_request = ThematicSuiteRequest(
                    character_concept=enhanced_concept,
                    requested_content_types=creation_options.get("content_types", 
                                                               ["equipment", "spells"]),
                    register_content=True
                )
                
                suite_result = self.content_generator.generate_thematic_content_suite(suite_request)
                if suite_result.success:
                    custom_content_suite = suite_result.content_suite
            
            # 4. Perform character analysis
            analysis_request = CharacterAnalysisRequest(
                character_id=character_result.character.id,
                analysis_types=["comprehensive", "optimization", "thematic_consistency"]
            )
            
            analysis_result = self.character_manager.analyze_character(analysis_request)
            
            return {
                "success": True,
                "character": character_result.character,
                "enhanced_concept": enhanced_concept,
                "custom_content_suite": custom_content_suite,
                "character_analysis": analysis_result.analysis_results if analysis_result.success else None,
                "pipeline_metadata": {
                    "creation_method": "concept_driven_pipeline",
                    "custom_content_generated": custom_content_suite is not None,
                    "analysis_completed": analysis_result.success
                }
            }
            
        except Exception as e:
            logger.error(f"Character creation pipeline failed: {e}")
            return {
                "success": False,
                "stage": "pipeline_orchestration",
                "errors": [f"Pipeline failed: {str(e)}"]
            }
    
    def create_multiclass_character_from_concept(self, background_description: str,
                                               class_combination: List[str],
                                               target_level: int = 20,
                                               optimization_goals: List[str] = None) -> Dict[str, Any]:
        """
        Complete multiclass character creation pipeline from concept.
        
        Args:
            background_description: Character concept description
            class_combination: Desired class combination
            target_level: Target character level
            optimization_goals: Optimization objectives
            
        Returns:
            Complete multiclass character with optimization analysis
        """
        try:
            # 1. Enhance concept for multiclass optimization
            enhanced_concept = self.concept_llm.enhance_multiclass_concept(
                background_description, class_combination, optimization_goals or []
            )
            
            # 2. Create multiclass character
            multiclass_request = MulticlassRequest(
                character_concept=enhanced_concept,
                class_combination=class_combination,
                target_level=target_level,
                optimization_goals=optimization_goals or ["versatility", "thematic_consistency"]
            )
            
            multiclass_result = self.character_manager.create_multiclass_character(multiclass_request)
            
            if not multiclass_result.success:
                return {
                    "success": False,
                    "stage": "multiclass_creation",
                    "errors": multiclass_result.errors
                }
            
            # 3. Validate multiclass build
            validation_request = ContentValidationRequest(
                content=multiclass_result.character.to_dict(),
                content_type="multiclass_character",
                character_concept=enhanced_concept,
                include_llm_analysis=True
            )
            
            validation_result = self.content_validator.validate_generated_content(validation_request)
            
            # 4. Generate optimization recommendations
            optimization_analysis = self.integration_manager.optimize_character_build(
                multiclass_result.character.id, optimization_goals or []
            )
            
            return {
                "success": True,
                "multiclass_character": multiclass_result.character,
                "progression_plan": multiclass_result.progression_plan,
                "feature_optimization": multiclass_result.feature_optimization,
                "validation_result": validation_result,
                "optimization_analysis": optimization_analysis,
                "pipeline_metadata": {
                    "creation_method": "multiclass_concept_pipeline",
                    "optimization_score": multiclass_result.feasibility_analysis.get("optimization_score", 0.0)
                }
            }
            
        except Exception as e:
            logger.error(f"Multiclass creation pipeline failed: {e}")
            return {
                "success": False,
                "stage": "multiclass_pipeline",
                "errors": [f"Multiclass pipeline failed: {str(e)}"]
            }
    
    def generate_content_suite_from_concept(self, background_description: str,
                                          content_types: List[str],
                                          generation_options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate complete content suite from character concept.
        
        Args:
            background_description: Character concept description
            content_types: Types of content to generate
            generation_options: Generation preferences and constraints
            
        Returns:
            Complete validated content suite with integration analysis
        """
        try:
            # 1. Analyze concept for thematic elements
            concept_analysis = self.concept_llm.analyze_concept_themes(
                background_description, content_types
            )
            
            # 2. Generate thematic content suite
            suite_request = ThematicSuiteRequest(
                character_concept=concept_analysis["enhanced_concept"],
                requested_content_types=content_types,
                content_priorities=generation_options.get("priorities", {}),
                register_content=generation_options.get("register_content", False)
            )
            
            suite_result = self.content_generator.generate_thematic_content_suite(suite_request)
            
            if not suite_result.success:
                return {
                    "success": False,
                    "stage": "content_generation",
                    "errors": suite_result.errors
                }
            
            # 3. Validate content suite coherence
            suite_validation = self.content_validator.validate_content_suite(
                suite_result.content_suite, concept_analysis["enhanced_concept"].to_dict()
            )
            
            # 4. Test integration compatibility
            integration_results = {}
            for content_type, content in suite_result.content_suite.items():
                integration_request = IntegrationRequest(
                    content=content,
                    content_type=content_type,
                    target_systems=["dnd_2024", "multiclass_compatible"],
                    test_multiclass_compatibility=True
                )
                
                integration_result = self.integration_manager.integrate_generated_content(
                    integration_request
                )
                integration_results[content_type] = integration_result
            
            return {
                "success": True,
                "content_suite": suite_result.content_suite,
                "thematic_analysis": suite_result.thematic_analysis,
                "suite_validation": suite_validation,
                "integration_results": integration_results,
                "generation_roadmap": suite_result.generation_roadmap,
                "pipeline_metadata": {
                    "generation_method": "thematic_suite_pipeline",
                    "coherence_score": suite_validation.get("coherence_validation", {}).get("score", 0.0),
                    "integration_success_rate": self._calculate_integration_success_rate(integration_results)
                }
            }
            
        except Exception as e:
            logger.error(f"Content suite generation pipeline failed: {e}")
            return {
                "success": False,
                "stage": "content_suite_pipeline",
                "errors": [f"Content suite pipeline failed: {str(e)}"]
            }
    
    def generate_single_content_from_concept(self, background_description: str,
                                           content_type: str,
                                           generation_constraints: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate single piece of content from character concept.
        
        Args:
            background_description: Character concept description
            content_type: Type of content to generate
            generation_constraints: Optional generation constraints
            
        Returns:
            Generated and validated content with integration analysis
        """
        try:
            # 1. Create character concept
            enhanced_concept = self.concept_llm.create_character_concept_from_description(
                background_description, {"target_content_type": content_type}
            )
            
            # 2. Generate content
            generation_request = ContentGenerationRequest(
                character_concept=enhanced_concept,
                content_type=content_type,
                constraints=generation_constraints,
                register_content=True
            )
            
            generation_result = self.content_generator.generate_content(generation_request)
            
            if not generation_result.success:
                return {
                    "success": False,
                    "stage": "content_generation",
                    "errors": generation_result.errors
                }
            
            # 3. Comprehensive validation
            validation_request = ContentValidationRequest(
                content=generation_result.generated_content,
                content_type=content_type,
                character_concept=enhanced_concept,
                include_llm_analysis=True
            )
            
            validation_result = self.content_validator.validate_generated_content(validation_request)
            
            # 4. Integration testing
            integration_request = IntegrationRequest(
                content=generation_result.generated_content,
                content_type=content_type,
                target_systems=["dnd_2024"],
                test_multiclass_compatibility=True,
                register_on_success=True
            )
            
            integration_result = self.integration_manager.integrate_generated_content(
                integration_request
            )
            
            return {
                "success": True,
                "content_type": content_type,
                "generated_content": generation_result.generated_content,
                "thematic_analysis": generation_result.thematic_analysis,
                "validation_result": validation_result,
                "integration_result": integration_result,
                "pipeline_metadata": {
                    "generation_method": "single_content_pipeline",
                    "validation_score": validation_result.overall_score,
                    "integration_score": integration_result.integration_score
                }
            }
            
        except Exception as e:
            logger.error(f"Single content generation pipeline failed: {e}")
            return {
                "success": False,
                "stage": "single_content_pipeline",
                "errors": [f"Single content pipeline failed: {str(e)}"]
            }
    
    def optimize_existing_character(self, character_id: str,
                                  optimization_goals: List[str],
                                  include_custom_content: bool = True) -> Dict[str, Any]:
        """
        Optimize existing character with potential custom content generation.
        
        Args:
            character_id: ID of character to optimize
            optimization_goals: Optimization objectives
            include_custom_content: Whether to generate custom content for optimization
            
        Returns:
            Optimization analysis with generated content recommendations
        """
        try:
            # 1. Analyze current character
            analysis_request = CharacterAnalysisRequest(
                character_id=character_id,
                analysis_types=["comprehensive", "optimization", "thematic_consistency"]
            )
            
            current_analysis = self.character_manager.analyze_character(analysis_request)
            
            if not current_analysis.success:
                return {
                    "success": False,
                    "stage": "character_analysis",
                    "errors": current_analysis.errors
                }
            
            # 2. Generate optimization recommendations
            optimization_analysis = self.integration_manager.optimize_character_build(
                character_id, optimization_goals
            )
            
            # 3. Generate custom content for optimization if requested
            custom_content_recommendations = None
            if include_custom_content and optimization_analysis.get("success"):
                # Extract character concept from analysis
                character_themes = current_analysis.analysis_results.get("thematic_consistency", {})
                
                if character_themes:
                    # Generate targeted content for optimization gaps
                    content_suggestions = self._identify_content_optimization_opportunities(
                        optimization_analysis, character_themes
                    )
                    
                    custom_content_recommendations = {}
                    for content_type in content_suggestions:
                        content_request = ContentGenerationRequest(
                            character_concept=self._create_concept_from_themes(character_themes),
                            content_type=content_type,
                            constraints={"optimization_target": optimization_goals},
                            register_content=False
                        )
                        
                        content_result = self.content_generator.generate_content(content_request)
                        if content_result.success:
                            custom_content_recommendations[content_type] = content_result.generated_content
            
            return {
                "success": True,
                "character_id": character_id,
                "current_analysis": current_analysis.analysis_results,
                "optimization_analysis": optimization_analysis,
                "custom_content_recommendations": custom_content_recommendations,
                "pipeline_metadata": {
                    "optimization_method": "analysis_driven_pipeline",
                    "optimization_potential": optimization_analysis.get("optimization_potential", 0.0),
                    "custom_content_generated": custom_content_recommendations is not None
                }
            }
            
        except Exception as e:
            logger.error(f"Character optimization pipeline failed: {e}")
            return {
                "success": False,
                "stage": "optimization_pipeline",
                "errors": [f"Optimization pipeline failed: {str(e)}"]
            }
    
    # === Private Helper Methods ===
    
    def _calculate_integration_success_rate(self, integration_results: Dict[str, Any]) -> float:
        """Calculate success rate of content integration."""
        if not integration_results:
            return 0.0
        
        successful_integrations = sum(
            1 for result in integration_results.values() 
            if result.success and result.integration_score >= 0.7
        )
        
        return successful_integrations / len(integration_results)
    
    def _identify_content_optimization_opportunities(self, optimization_analysis: Dict[str, Any],
                                                   character_themes: Dict[str, Any]) -> List[str]:
        """Identify content types that could help with optimization."""
        opportunities = []
        
        recommendations = optimization_analysis.get("recommendations", [])
        
        for rec in recommendations:
            if rec.get("type") == "equipment_optimization":
                opportunities.append("equipment")
            elif rec.get("type") == "spell_optimization":
                opportunities.append("spell")
            elif rec.get("type") == "feat_optimization":
                opportunities.append("feat")
        
        return list(set(opportunities))
    
    def _create_concept_from_themes(self, themes: Dict[str, Any]) -> CharacterConcept:
        """Create a character concept from thematic analysis."""
        # Implementation would create a CharacterConcept from theme analysis
        # This is a simplified placeholder
        return CharacterConcept(
            background_description="Character optimization concept",
            thematic_elements=ThematicElements(
                primary_themes=themes.get("themes", []),
                aesthetic_elements=themes.get("aesthetic_elements", [])
            )
        )

class PipelineOrchestrator:
    """
    High-level orchestrator for multiple pipeline operations.
    
    Coordinates complex workflows that involve multiple pipeline stages
    and manages dependencies between different creative generation processes.
    """
    
    def __init__(self, creative_pipeline: CreativePipeline):
        self.pipeline = creative_pipeline
    
    def create_campaign_content_package(self, campaign_concept: str,
                                      character_concepts: List[str],
                                      content_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create complete content package for a campaign.
        
        Args:
            campaign_concept: Overall campaign theme and concept
            character_concepts: List of character concept descriptions
            content_requirements: Required content types and constraints
            
        Returns:
            Complete campaign content package
        """
        try:
            campaign_package = {
                "campaign_concept": campaign_concept,
                "characters": [],
                "shared_content": {},
                "campaign_metadata": {}
            }
            
            # Create characters from concepts
            for concept in character_concepts:
                character_result = self.pipeline.create_character_from_concept(
                    concept, content_requirements.get("character_options", {})
                )
                
                if character_result["success"]:
                    campaign_package["characters"].append(character_result)
            
            # Generate shared campaign content
            if content_requirements.get("shared_content_types"):
                shared_content_result = self.pipeline.generate_content_suite_from_concept(
                    campaign_concept,
                    content_requirements["shared_content_types"],
                    content_requirements.get("shared_content_options", {})
                )
                
                if shared_content_result["success"]:
                    campaign_package["shared_content"] = shared_content_result["content_suite"]
            
            campaign_package["success"] = True
            return campaign_package
            
        except Exception as e:
            logger.error(f"Campaign package creation failed: {e}")
            return {
                "success": False,
                "errors": [f"Campaign package creation failed: {str(e)}"]
            }
    
    def batch_content_generation(self, generation_requests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process multiple content generation requests in batch.
        
        Args:
            generation_requests: List of content generation specifications
            
        Returns:
            Batch processing results
        """
        try:
            batch_results = {
                "success": True,
                "results": [],
                "summary": {
                    "total_requests": len(generation_requests),
                    "successful_generations": 0,
                    "failed_generations": 0
                }
            }
            
            for request in generation_requests:
                if request["type"] == "single_content":
                    result = self.pipeline.generate_single_content_from_concept(
                        request["concept"], request["content_type"], 
                        request.get("constraints", {})
                    )
                elif request["type"] == "content_suite":
                    result = self.pipeline.generate_content_suite_from_concept(
                        request["concept"], request["content_types"],
                        request.get("options", {})
                    )
                else:
                    result = {"success": False, "errors": [f"Unknown request type: {request['type']}"]}
                
                batch_results["results"].append(result)
                
                if result["success"]:
                    batch_results["summary"]["successful_generations"] += 1
                else:
                    batch_results["summary"]["failed_generations"] += 1
            
            return batch_results
            
        except Exception as e:
            logger.error(f"Batch content generation failed: {e}")
            return {
                "success": False,
                "errors": [f"Batch processing failed: {str(e)}"]
            }