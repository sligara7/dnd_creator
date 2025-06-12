"""
Iterative Content Refinement Workflow

Workflow orchestrator for improving generated content through iterative feedback,
validation, and optimization cycles. This implements the feedback-driven improvement
process while maintaining the background-driven, rule-compliant philosophy.
"""

from typing import Dict, Any, List, Optional, Tuple
import logging

from ..use_cases.generate_content import GenerateContentUseCase
from ..use_cases.validate_content import ValidateContentUseCase
from ..use_cases.manage_character import ManageCharacterUseCase
from ..use_cases.integration_manager import IntegrationManagerUseCase
from ..dtos.content_dto import (
    ContentGenerationRequest,
    ContentValidationRequest,
    ContentAnalysisRequest,
    IntegrationRequest
)
from ..dtos.character_dto import (
    CharacterValidationRequest,
    CharacterOptimizationSuggestion
)
from ...core.entities.character_concept import CharacterConcept
from ...core.value_objects.validation_result import ValidationResult
from ...infrastructure.llm.feedback_llm_service import FeedbackLLMService

logger = logging.getLogger(__name__)

class IterativeRefinementWorkflow:
    """
    Orchestrates iterative improvement of generated content and characters.
    
    This workflow implements feedback-driven refinement cycles that:
    1. Start from character concepts (background-driven)
    2. Apply rule validation at each iteration (rule-compliant)
    3. Handle all content types uniformly (modular)
    4. Use LLM assistance for creative improvements (LLM-assisted)
    5. Maintain clean separation of concerns (clean architecture)
    """
    
    def __init__(self,
                 content_generator: GenerateContentUseCase,
                 content_validator: ValidateContentUseCase,
                 character_manager: ManageCharacterUseCase,
                 integration_manager: IntegrationManagerUseCase,
                 feedback_llm: FeedbackLLMService):
        self.content_generator = content_generator
        self.content_validator = content_validator
        self.character_manager = character_manager
        self.integration_manager = integration_manager
        self.feedback_llm = feedback_llm
    
    def refine_generated_content(self, content: Dict[str, Any],
                               content_type: str,
                               character_concept: CharacterConcept,
                               feedback: List[str],
                               max_iterations: int = 3) -> Dict[str, Any]:
        """
        Iteratively refine generated content based on feedback.
        
        Args:
            content: Original generated content
            content_type: Type of content being refined
            character_concept: Originating character concept
            feedback: List of feedback points for improvement
            max_iterations: Maximum refinement iterations
            
        Returns:
            Refined content with improvement history
        """
        try:
            refinement_history = []
            current_content = content.copy()
            current_iteration = 0
            
            while current_iteration < max_iterations:
                # 1. Validate current content
                validation_request = ContentValidationRequest(
                    content=current_content,
                    content_type=content_type,
                    character_concept=character_concept,
                    include_llm_analysis=True
                )
                
                validation_result = self.content_validator.validate_generated_content(
                    validation_request
                )
                
                # 2. Analyze improvement opportunities
                improvement_analysis = self._analyze_improvement_opportunities(
                    current_content, content_type, validation_result, feedback
                )
                
                # 3. Check if further refinement is needed
                if self._is_refinement_complete(validation_result, improvement_analysis):
                    break
                
                # 4. Generate refinement suggestions using LLM
                refinement_suggestions = self.feedback_llm.generate_refinement_suggestions(
                    current_content, content_type, character_concept, 
                    validation_result, feedback
                )
                
                # 5. Apply refinements
                refined_content = self._apply_content_refinements(
                    current_content, content_type, refinement_suggestions
                )
                
                # 6. Record iteration history
                iteration_record = {
                    "iteration": current_iteration + 1,
                    "validation_score": validation_result.overall_score,
                    "improvements_applied": refinement_suggestions,
                    "content_delta": self._calculate_content_delta(current_content, refined_content)
                }
                refinement_history.append(iteration_record)
                
                current_content = refined_content
                current_iteration += 1
            
            # Final validation
            final_validation = self.content_validator.validate_generated_content(
                ContentValidationRequest(
                    content=current_content,
                    content_type=content_type,
                    character_concept=character_concept,
                    include_llm_analysis=True
                )
            )
            
            return {
                "success": True,
                "refined_content": current_content,
                "refinement_history": refinement_history,
                "final_validation": final_validation,
                "improvement_metrics": self._calculate_improvement_metrics(
                    content, current_content, refinement_history
                ),
                "iterations_completed": current_iteration
            }
            
        except Exception as e:
            logger.error(f"Content refinement failed: {e}")
            return {
                "success": False,
                "errors": [f"Refinement failed: {str(e)}"]
            }
    
    def optimize_character_build(self, character_id: str,
                               optimization_goals: List[str],
                               constraints: Dict[str, Any] = None,
                               max_iterations: int = 3) -> Dict[str, Any]:
        """
        Iteratively optimize character build through refinement cycles.
        
        Args:
            character_id: Character to optimize
            optimization_goals: Optimization objectives
            constraints: Optimization constraints
            max_iterations: Maximum optimization iterations
            
        Returns:
            Optimization results with improvement history
        """
        try:
            optimization_history = []
            current_iteration = 0
            
            while current_iteration < max_iterations:
                # 1. Analyze current build
                build_analysis = self.integration_manager.optimize_character_build(
                    character_id, optimization_goals
                )
                
                if not build_analysis.get("success"):
                    break
                
                # 2. Generate optimization suggestions
                optimization_suggestions = self._generate_character_optimization_suggestions(
                    character_id, build_analysis, optimization_goals, constraints
                )
                
                # 3. Check if optimization is complete
                if self._is_optimization_complete(build_analysis, optimization_suggestions):
                    break
                
                # 4. Apply selected optimizations
                applied_optimizations = self._apply_character_optimizations(
                    character_id, optimization_suggestions
                )
                
                # 5. Record iteration
                iteration_record = {
                    "iteration": current_iteration + 1,
                    "optimization_score": build_analysis.get("optimization_potential", 0.0),
                    "optimizations_applied": applied_optimizations,
                    "improvement_metrics": self._calculate_character_improvement_metrics(
                        character_id, applied_optimizations
                    )
                }
                optimization_history.append(iteration_record)
                
                current_iteration += 1
            
            # Final analysis
            final_analysis = self.integration_manager.optimize_character_build(
                character_id, optimization_goals
            )
            
            return {
                "success": True,
                "character_id": character_id,
                "optimization_history": optimization_history,
                "final_analysis": final_analysis,
                "optimization_summary": self._generate_optimization_summary(
                    optimization_history, final_analysis
                ),
                "iterations_completed": current_iteration
            }
            
        except Exception as e:
            logger.error(f"Character optimization failed: {e}")
            return {
                "success": False,
                "errors": [f"Optimization failed: {str(e)}"]
            }
    
    def refine_content_suite(self, content_suite: Dict[str, Any],
                           character_concept: CharacterConcept,
                           suite_feedback: Dict[str, List[str]],
                           max_iterations: int = 2) -> Dict[str, Any]:
        """
        Iteratively refine an entire content suite for coherence and quality.
        
        Args:
            content_suite: Dictionary of content_type -> content
            character_concept: Originating character concept
            suite_feedback: Feedback for each content type
            max_iterations: Maximum refinement iterations
            
        Returns:
            Refined content suite with coherence analysis
        """
        try:
            suite_refinement_history = []
            current_suite = content_suite.copy()
            current_iteration = 0
            
            while current_iteration < max_iterations:
                # 1. Validate suite coherence
                suite_validation = self.content_validator.validate_content_suite(
                    current_suite, character_concept.to_dict()
                )
                
                # 2. Analyze cross-content improvements
                cross_content_analysis = self._analyze_suite_improvement_opportunities(
                    current_suite, suite_validation, suite_feedback
                )
                
                # 3. Check if refinement is complete
                if self._is_suite_refinement_complete(suite_validation, cross_content_analysis):
                    break
                
                # 4. Refine individual content pieces
                refined_suite = {}
                suite_improvements = {}
                
                for content_type, content in current_suite.items():
                    content_feedback = suite_feedback.get(content_type, [])
                    
                    # Add cross-content feedback
                    cross_feedback = cross_content_analysis.get(content_type, [])
                    combined_feedback = content_feedback + cross_feedback
                    
                    if combined_feedback:
                        refinement_result = self.refine_generated_content(
                            content, content_type, character_concept,
                            combined_feedback, max_iterations=1
                        )
                        
                        if refinement_result["success"]:
                            refined_suite[content_type] = refinement_result["refined_content"]
                            suite_improvements[content_type] = refinement_result["improvement_metrics"]
                        else:
                            refined_suite[content_type] = content
                    else:
                        refined_suite[content_type] = content
                
                # 5. Record suite iteration
                iteration_record = {
                    "iteration": current_iteration + 1,
                    "suite_coherence_score": suite_validation.get("coherence_validation", {}).get("score", 0.0),
                    "content_improvements": suite_improvements,
                    "cross_content_analysis": cross_content_analysis
                }
                suite_refinement_history.append(iteration_record)
                
                current_suite = refined_suite
                current_iteration += 1
            
            # Final suite validation
            final_suite_validation = self.content_validator.validate_content_suite(
                current_suite, character_concept.to_dict()
            )
            
            return {
                "success": True,
                "refined_content_suite": current_suite,
                "suite_refinement_history": suite_refinement_history,
                "final_suite_validation": final_suite_validation,
                "suite_improvement_metrics": self._calculate_suite_improvement_metrics(
                    content_suite, current_suite, suite_refinement_history
                ),
                "iterations_completed": current_iteration
            }
            
        except Exception as e:
            logger.error(f"Content suite refinement failed: {e}")
            return {
                "success": False,
                "errors": [f"Suite refinement failed: {str(e)}"]
            }
    
    def iterative_character_development(self, character_concept_description: str,
                                      development_goals: List[str],
                                      max_iterations: int = 3) -> Dict[str, Any]:
        """
        Complete iterative character development from concept to optimized build.
        
        Args:
            character_concept_description: Initial character concept
            development_goals: Development objectives
            max_iterations: Maximum development iterations
            
        Returns:
            Complete character development results
        """
        try:
            development_history = []
            current_iteration = 0
            
            # 1. Initial character creation
            from ..dtos.character_dto import CharacterCreationRequest
            creation_request = CharacterCreationRequest(
                background_description=character_concept_description,
                apply_custom_content=True
            )
            
            character_result = self.character_manager.create_character(creation_request)
            
            if not character_result.success:
                return {
                    "success": False,
                    "stage": "initial_creation",
                    "errors": character_result.errors
                }
            
            character_id = character_result.character.id
            
            while current_iteration < max_iterations:
                # 2. Analyze character against development goals
                development_analysis = self._analyze_character_development_potential(
                    character_id, development_goals
                )
                
                # 3. Check if development is complete
                if self._is_character_development_complete(development_analysis):
                    break
                
                # 4. Generate development recommendations
                development_recommendations = self._generate_character_development_recommendations(
                    character_id, development_analysis, development_goals
                )
                
                # 5. Apply development changes
                applied_developments = self._apply_character_developments(
                    character_id, development_recommendations
                )
                
                # 6. Record development iteration
                iteration_record = {
                    "iteration": current_iteration + 1,
                    "development_analysis": development_analysis,
                    "developments_applied": applied_developments,
                    "character_progression": self._capture_character_progression_snapshot(character_id)
                }
                development_history.append(iteration_record)
                
                current_iteration += 1
            
            # Final character analysis
            final_analysis = self.character_manager.analyze_character(
                from ..dtos.character_dto import CharacterAnalysisRequest(
                    character_id=character_id,
                    analysis_types=["comprehensive", "optimization", "thematic_consistency"]
                )
            )
            
            return {
                "success": True,
                "developed_character_id": character_id,
                "development_history": development_history,
                "final_character_analysis": final_analysis.analysis_results if final_analysis.success else None,
                "development_summary": self._generate_development_summary(
                    development_history, final_analysis
                ),
                "iterations_completed": current_iteration
            }
            
        except Exception as e:
            logger.error(f"Iterative character development failed: {e}")
            return {
                "success": False,
                "errors": [f"Character development failed: {str(e)}"]
            }
    
    # === Private Helper Methods ===
    
    def _analyze_improvement_opportunities(self, content: Dict[str, Any],
                                         content_type: str,
                                         validation_result: Any,
                                         feedback: List[str]) -> Dict[str, Any]:
        """Analyze opportunities for content improvement."""
        opportunities = {
            "rule_compliance": [],
            "balance_adjustments": [],
            "thematic_enhancements": [],
            "creative_improvements": []
        }
        
        # Analyze validation issues
        if hasattr(validation_result, 'rule_validation') and validation_result.rule_validation:
            if not validation_result.rule_validation.is_valid:
                opportunities["rule_compliance"] = validation_result.rule_validation.issues
        
        # Analyze balance issues
        if hasattr(validation_result, 'balance_validation') and validation_result.balance_validation:
            if validation_result.balance_validation.score < 0.7:
                opportunities["balance_adjustments"] = validation_result.balance_validation.issues
        
        # Analyze feedback for thematic and creative opportunities
        for feedback_item in feedback:
            if "theme" in feedback_item.lower() or "story" in feedback_item.lower():
                opportunities["thematic_enhancements"].append(feedback_item)
            else:
                opportunities["creative_improvements"].append(feedback_item)
        
        return opportunities
    
    def _is_refinement_complete(self, validation_result: Any,
                              improvement_analysis: Dict[str, Any]) -> bool:
        """Check if content refinement is complete."""
        # Consider refinement complete if validation passes and no critical improvements
        validation_passed = (hasattr(validation_result, 'is_valid') and 
                           validation_result.is_valid and 
                           validation_result.overall_score >= 0.8)
        
        critical_improvements = (
            len(improvement_analysis.get("rule_compliance", [])) == 0 and
            len(improvement_analysis.get("balance_adjustments", [])) == 0
        )
        
        return validation_passed and critical_improvements
    
    def _apply_content_refinements(self, content: Dict[str, Any],
                                 content_type: str,
                                 refinement_suggestions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply refinement suggestions to content."""
        refined_content = content.copy()
        
        for suggestion in refinement_suggestions:
            if suggestion["type"] == "rule_fix":
                refined_content = self._apply_rule_fix(refined_content, suggestion)
            elif suggestion["type"] == "balance_adjustment":
                refined_content = self._apply_balance_adjustment(refined_content, suggestion)
            elif suggestion["type"] == "thematic_enhancement":
                refined_content = self._apply_thematic_enhancement(refined_content, suggestion)
            elif suggestion["type"] == "creative_improvement":
                refined_content = self._apply_creative_improvement(refined_content, suggestion)
        
        return refined_content
    
    def _calculate_content_delta(self, original: Dict[str, Any],
                               refined: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate differences between original and refined content."""
        delta = {
            "fields_changed": [],
            "values_added": [],
            "values_removed": [],
            "structural_changes": []
        }
        
        # Simple delta calculation - would be more sophisticated in practice
        for key in original.keys():
            if key not in refined:
                delta["values_removed"].append(key)
            elif original[key] != refined.get(key):
                delta["fields_changed"].append(key)
        
        for key in refined.keys():
            if key not in original:
                delta["values_added"].append(key)
        
        return delta
    
    def _calculate_improvement_metrics(self, original: Dict[str, Any],
                                     refined: Dict[str, Any],
                                     history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate improvement metrics from refinement process."""
        if not history:
            return {"improvement_score": 0.0, "iterations_needed": 0}
        
        initial_score = history[0].get("validation_score", 0.0)
        final_score = history[-1].get("validation_score", 0.0)
        
        return {
            "improvement_score": final_score - initial_score,
            "iterations_needed": len(history),
            "convergence_rate": (final_score - initial_score) / len(history)
        }
    
    def _generate_character_optimization_suggestions(self, character_id: str,
                                                   build_analysis: Dict[str, Any],
                                                   goals: List[str],
                                                   constraints: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate character optimization suggestions."""
        suggestions = []
        
        recommendations = build_analysis.get("recommendations", [])
        
        for rec in recommendations:
            if self._suggestion_meets_constraints(rec, constraints):
                suggestions.append({
                    "type": rec.get("type", "optimization"),
                    "description": rec.get("description", ""),
                    "priority": rec.get("priority", "medium"),
                    "implementation": rec.get("suggested_action", "")
                })
        
        return suggestions
    
    def _is_optimization_complete(self, build_analysis: Dict[str, Any],
                                suggestions: List[Dict[str, Any]]) -> bool:
        """Check if character optimization is complete."""
        optimization_potential = build_analysis.get("optimization_potential", 0.0)
        high_priority_suggestions = [s for s in suggestions if s.get("priority") == "high"]
        
        return optimization_potential >= 0.9 or len(high_priority_suggestions) == 0
    
    def _apply_character_optimizations(self, character_id: str,
                                     suggestions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply character optimization suggestions."""
        applied_optimizations = []
        
        for suggestion in suggestions:
            # Apply optimization based on type
            if suggestion["type"] == "feat_optimization":
                result = self._apply_feat_optimization(character_id, suggestion)
            elif suggestion["type"] == "equipment_optimization":
                result = self._apply_equipment_optimization(character_id, suggestion)
            elif suggestion["type"] == "spell_optimization":
                result = self._apply_spell_optimization(character_id, suggestion)
            else:
                result = {"applied": False, "reason": "Unknown optimization type"}
            
            if result.get("applied"):
                applied_optimizations.append({
                    "suggestion": suggestion,
                    "result": result
                })
        
        return applied_optimizations
    
    # Additional helper methods for suite refinement
    def _analyze_suite_improvement_opportunities(self, suite: Dict[str, Any],
                                               validation: Dict[str, Any],
                                               feedback: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """Analyze improvement opportunities across content suite."""
        cross_content_feedback = {}
        
        # Analyze coherence issues
        coherence_validation = validation.get("coherence_validation", {})
        if not coherence_validation.get("is_valid", True):
            for content_type in suite.keys():
                cross_content_feedback[content_type] = [
                    "Improve thematic coherence with other content types"
                ]
        
        # Analyze compatibility issues
        compatibility_validation = validation.get("compatibility_validation", {})
        if not compatibility_validation.get("is_valid", True):
            compatibility_issues = compatibility_validation.get("issues", [])
            for issue in compatibility_issues:
                affected_types = self._extract_affected_content_types(issue)
                for content_type in affected_types:
                    if content_type not in cross_content_feedback:
                        cross_content_feedback[content_type] = []
                    cross_content_feedback[content_type].append(f"Address compatibility: {issue}")
        
        return cross_content_feedback
    
    def _is_suite_refinement_complete(self, validation: Dict[str, Any],
                                    analysis: Dict[str, List[str]]) -> bool:
        """Check if suite refinement is complete."""
        suite_valid = validation.get("overall_suite_valid", False)
        no_critical_issues = all(len(issues) == 0 for issues in analysis.values())
        
        return suite_valid and no_critical_issues
    
    # Character development helper methods
    def _analyze_character_development_potential(self, character_id: str,
                                               goals: List[str]) -> Dict[str, Any]:
        """Analyze character's development potential."""
        # Implementation would analyze character against development goals
        return {
            "development_score": 0.7,
            "goal_alignment": {goal: 0.6 for goal in goals},
            "development_opportunities": []
        }
    
    def _is_character_development_complete(self, analysis: Dict[str, Any]) -> bool:
        """Check if character development is complete."""
        development_score = analysis.get("development_score", 0.0)
        return development_score >= 0.9
    
    # Placeholder implementations for various helper methods
    def _suggestion_meets_constraints(self, suggestion: Dict[str, Any],
                                    constraints: Dict[str, Any]) -> bool:
        """Check if suggestion meets optimization constraints."""
        return True  # Simplified implementation
    
    def _apply_rule_fix(self, content: Dict[str, Any], suggestion: Dict[str, Any]) -> Dict[str, Any]:
        """Apply rule compliance fix."""
        return content  # Placeholder
    
    def _apply_balance_adjustment(self, content: Dict[str, Any], suggestion: Dict[str, Any]) -> Dict[str, Any]:
        """Apply balance adjustment."""
        return content  # Placeholder
    
    def _apply_thematic_enhancement(self, content: Dict[str, Any], suggestion: Dict[str, Any]) -> Dict[str, Any]:
        """Apply thematic enhancement."""
        return content  # Placeholder
    
    def _apply_creative_improvement(self, content: Dict[str, Any], suggestion: Dict[str, Any]) -> Dict[str, Any]:
        """Apply creative improvement."""
        return content  # Placeholder
    
    def _calculate_character_improvement_metrics(self, character_id: str,
                                               optimizations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate character improvement metrics."""
        return {"improvement_score": 0.1}  # Placeholder
    
    def _generate_optimization_summary(self, history: List[Dict[str, Any]],
                                     final_analysis: Dict[str, Any]) -> str:
        """Generate optimization summary."""
        return f"Optimization completed in {len(history)} iterations"  # Placeholder
    
    def _apply_feat_optimization(self, character_id: str, suggestion: Dict[str, Any]) -> Dict[str, Any]:
        """Apply feat optimization."""
        return {"applied": True}  # Placeholder
    
    def _apply_equipment_optimization(self, character_id: str, suggestion: Dict[str, Any]) -> Dict[str, Any]:
        """Apply equipment optimization."""
        return {"applied": True}  # Placeholder
    
    def _apply_spell_optimization(self, character_id: str, suggestion: Dict[str, Any]) -> Dict[str, Any]:
        """Apply spell optimization."""
        return {"applied": True}  # Placeholder
    
    def _extract_affected_content_types(self, issue: str) -> List[str]:
        """Extract affected content types from compatibility issue."""
        return []  # Placeholder
    
    def _calculate_suite_improvement_metrics(self, original: Dict[str, Any],
                                           refined: Dict[str, Any],
                                           history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate suite improvement metrics."""
        return {"suite_improvement_score": 0.1}  # Placeholder
    
    def _generate_character_development_recommendations(self, character_id: str,
                                                      analysis: Dict[str, Any],
                                                      goals: List[str]) -> List[Dict[str, Any]]:
        """Generate character development recommendations."""
        return []  # Placeholder
    
    def _apply_character_developments(self, character_id: str,
                                    recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply character development recommendations."""
        return []  # Placeholder
    
    def _capture_character_progression_snapshot(self, character_id: str) -> Dict[str, Any]:
        """Capture character progression snapshot."""
        return {"level": 1, "snapshot_timestamp": "2024-01-01"}  # Placeholder
    
    def _generate_development_summary(self, history: List[Dict[str, Any]],
                                    final_analysis: Any) -> str:
        """Generate character development summary."""
        return f"Character development completed in {len(history)} iterations"  # Placeholder