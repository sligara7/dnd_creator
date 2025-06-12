"""
D&D Rule Integration Manager Use Case

Central manager for integrating generated content with existing D&D systems.
Handles rule compliance, system compatibility, multiclass integration, and
character build validation within the D&D 2024 framework.
"""

from typing import Dict, Any, List, Optional, Union
import logging

from ...core.entities.character import Character
from ...core.entities.generated_content import GeneratedContent
from ...core.value_objects.validation_result import ValidationResult
from ...core.value_objects.multiclass_result import MulticlassResult
from ...domain.services.multiclass_engine import MulticlassEngine
from ...domain.services.character_builder import CharacterBuilderService
from ...domain.services.validation_engine import CharacterValidationEngine
from ...domain.services.content_validation_service import ContentValidationService
from ...domain.services.character_state_service import CharacterStateService
from ...domain.services.content_registry import ContentRegistry
from ...domain.repositories.character_repository import CharacterRepository
from ...infrastructure.validation.rule_engine import RuleEngine
from ...infrastructure.validation.integration_tester import IntegrationTester
from ..dtos.content_dto import (
    IntegrationRequest,
    IntegrationResponse,
    ValidationRequest,
    ValidationResponse,
    MulticlassRequest,
    MulticlassResponse
)

logger = logging.getLogger(__name__)

class IntegrationManagerUseCase:
    """
    Central use case for D&D rule integration and system compatibility.
    
    Handles:
    - Generated content integration with official D&D rules
    - Multiclass character creation and optimization
    - Character build validation and suggestions
    - System compatibility testing
    - Rule compliance verification
    """
    
    def __init__(self,
                 multiclass_engine: MulticlassEngine,
                 character_builder: CharacterBuilderService,
                 validation_engine: CharacterValidationEngine,
                 content_validator: ContentValidationService,
                 character_state_service: CharacterStateService,
                 content_registry: ContentRegistry,
                 character_repository: CharacterRepository,
                 rule_engine: RuleEngine,
                 integration_tester: IntegrationTester):
        self.multiclass_engine = multiclass_engine
        self.character_builder = character_builder
        self.validation_engine = validation_engine
        self.content_validator = content_validator
        self.character_state_service = character_state_service
        self.content_registry = content_registry
        self.character_repository = character_repository
        self.rule_engine = rule_engine
        self.integration_tester = integration_tester
    
    def integrate_generated_content(self, request: IntegrationRequest) -> IntegrationResponse:
        """
        Integrate generated content with existing D&D systems.
        
        Args:
            request: Integration request with content and target system
            
        Returns:
            IntegrationResponse with integration results and compatibility analysis
        """
        try:
            # 1. Validate content against D&D rules
            rule_validation = self._validate_content_rules(
                request.content, request.content_type
            )
            
            # 2. Test system integration compatibility
            system_compatibility = self._test_system_compatibility(
                request.content, request.content_type, request.target_systems
            )
            
            # 3. Analyze multiclass integration if applicable
            multiclass_integration = None
            if request.test_multiclass_compatibility:
                multiclass_integration = self._analyze_multiclass_integration(
                    request.content, request.content_type
                )
            
            # 4. Test character integration if target character provided
            character_integration = None
            if request.target_character_id:
                character_integration = self._test_character_integration(
                    request.content, request.content_type, request.target_character_id
                )
            
            # 5. Generate integration recommendations
            integration_recommendations = self._generate_integration_recommendations(
                rule_validation, system_compatibility, multiclass_integration, character_integration
            )
            
            # 6. Register content if integration is successful
            registration_result = None
            if request.register_on_success and self._is_integration_successful(
                rule_validation, system_compatibility
            ):
                registration_result = self._register_integrated_content(
                    request.content, request.content_type
                )
            
            return IntegrationResponse(
                success=True,
                content_type=request.content_type,
                rule_validation=rule_validation,
                system_compatibility=system_compatibility,
                multiclass_integration=multiclass_integration,
                character_integration=character_integration,
                integration_recommendations=integration_recommendations,
                registration_result=registration_result,
                integration_score=self._calculate_integration_score(
                    rule_validation, system_compatibility, multiclass_integration
                )
            )
            
        except Exception as e:
            logger.error(f"Content integration failed: {e}")
            return IntegrationResponse(
                success=False,
                errors=[f"Integration failed: {str(e)}"]
            )
    
    def create_multiclass_character(self, request: MulticlassRequest) -> MulticlassResponse:
        """
        Create and optimize multiclass character builds.
        
        Args:
            request: Multiclass creation request
            
        Returns:
            MulticlassResponse with optimized multiclass character
        """
        try:
            # 1. Validate multiclass prerequisites
            prerequisite_validation = self.multiclass_engine.validate_multiclass_prerequisites(
                request.character_concept, request.class_combination
            )
            
            if not prerequisite_validation.is_valid:
                return MulticlassResponse(
                    success=False,
                    errors=prerequisite_validation.errors
                )
            
            # 2. Calculate optimal level progression
            level_progression = self.multiclass_engine.calculate_optimal_progression(
                request.character_concept, request.class_combination, request.target_level
            )
            
            # 3. Build multiclass character
            multiclass_character = self._build_multiclass_character(
                request.character_concept, level_progression
            )
            
            # 4. Calculate multiclass features and interactions
            feature_interactions = self.multiclass_engine.analyze_feature_interactions(
                multiclass_character
            )
            
            # 5. Optimize spellcasting progression if applicable
            spellcasting_progression = None
            if self._has_spellcasting_classes(request.class_combination):
                spellcasting_progression = self.multiclass_engine.optimize_spellcasting_progression(
                    multiclass_character
                )
            
            # 6. Generate build recommendations
            build_recommendations = self._generate_multiclass_recommendations(
                multiclass_character, feature_interactions, request.optimization_goals
            )
            
            # 7. Save character if requested
            saved_character = None
            if request.save_character:
                saved_character = self.character_repository.save(multiclass_character)
            
            return MulticlassResponse(
                success=True,
                character=multiclass_character,
                level_progression=level_progression,
                feature_interactions=feature_interactions,
                spellcasting_progression=spellcasting_progression,
                build_recommendations=build_recommendations,
                saved_character_id=saved_character.id if saved_character else None,
                multiclass_score=self._calculate_multiclass_effectiveness_score(
                    multiclass_character, request.optimization_goals
                )
            )
            
        except Exception as e:
            logger.error(f"Multiclass character creation failed: {e}")
            return MulticlassResponse(
                success=False,
                errors=[f"Multiclass creation failed: {str(e)}"]
            )
    
    def validate_character_build(self, request: ValidationRequest) -> ValidationResponse:
        """
        Comprehensive character build validation.
        
        Args:
            request: Validation request
            
        Returns:
            ValidationResponse with detailed validation results
        """
        try:
            character = self.character_repository.get_by_id(request.character_id)
            
            # 1. Perform requested validation type
            if request.validation_type == "comprehensive":
                validation_result = self.validation_engine.validate_character_comprehensive(
                    character, request.context
                )
            elif request.validation_type == "step":
                validation_result = self.validation_engine.validate_character_creation_step(
                    character, request.step_name, request.context
                )
            elif request.validation_type == "optimization":
                validation_result = self.validation_engine.validate_character_optimization(
                    character
                )
            elif request.validation_type == "multiclass":
                validation_result = self.validation_engine.validate_multiclass_character(
                    character
                )
            else:
                raise ValueError(f"Unknown validation type: {request.validation_type}")
            
            # 2. Generate validation report
            validation_report = self.validation_engine.generate_validation_report(
                validation_result
            )
            
            # 3. Provide improvement suggestions if validation failed
            improvement_suggestions = []
            if not validation_result.is_valid:
                improvement_suggestions = self._generate_character_improvement_suggestions(
                    character, validation_result
                )
            
            return ValidationResponse(
                success=True,
                character_id=request.character_id,
                validation_type=request.validation_type,
                validation_result=validation_result,
                validation_report=validation_report,
                improvement_suggestions=improvement_suggestions,
                overall_score=self._calculate_character_build_score(character, validation_result)
            )
            
        except Exception as e:
            logger.error(f"Character validation failed: {e}")
            return ValidationResponse(
                success=False,
                errors=[f"Validation failed: {str(e)}"]
            )
    
    def manage_character_state(self, character_id: str, 
                             state_changes: Dict[str, Any]) -> Dict[str, Any]:
        """
        Manage character state changes (damage, rest, resource usage).
        
        Args:
            character_id: Character to modify
            state_changes: State changes to apply
            
        Returns:
            Result of state management operations
        """
        try:
            character = self.character_repository.get_by_id(character_id)
            
            # Apply state changes
            state_results = {}
            
            if "damage" in state_changes:
                damage_result = self.character_state_service.apply_damage(
                    character, state_changes["damage"]
                )
                state_results["damage"] = damage_result
            
            if "healing" in state_changes:
                healing_result = self.character_state_service.apply_healing(
                    character, state_changes["healing"]
                )
                state_results["healing"] = healing_result
            
            if "rest" in state_changes:
                rest_result = self.character_state_service.take_rest(
                    character, state_changes["rest"]["type"], 
                    state_changes["rest"].get("options", {})
                )
                state_results["rest"] = rest_result
            
            if "resource_usage" in state_changes:
                resource_result = self.character_state_service.use_resources(
                    character, state_changes["resource_usage"]
                )
                state_results["resource_usage"] = resource_result
            
            # Save updated character
            self.character_repository.save(character)
            
            return {
                "success": True,
                "character_id": character_id,
                "state_results": state_results,
                "current_state": character.get_current_state()
            }
            
        except Exception as e:
            logger.error(f"Character state management failed: {e}")
            return {
                "success": False,
                "errors": [f"State management failed: {str(e)}"]
            }
    
    def optimize_character_build(self, character_id: str, 
                               optimization_goals: List[str]) -> Dict[str, Any]:
        """
        Optimize existing character build for specific goals.
        
        Args:
            character_id: Character to optimize
            optimization_goals: Optimization targets (e.g., "damage", "survivability")
            
        Returns:
            Optimization analysis and recommendations
        """
        try:
            character = self.character_repository.get_by_id(character_id)
            
            # 1. Analyze current build
            build_analysis = self._analyze_character_build(character)
            
            # 2. Generate optimization recommendations
            optimization_recommendations = self._generate_build_optimizations(
                character, optimization_goals, build_analysis
            )
            
            # 3. Simulate optimization outcomes
            optimization_simulations = self._simulate_build_optimizations(
                character, optimization_recommendations
            )
            
            # 4. Rank recommendations by effectiveness
            ranked_recommendations = self._rank_optimization_recommendations(
                optimization_recommendations, optimization_simulations
            )
            
            return {
                "success": True,
                "character_id": character_id,
                "current_build_analysis": build_analysis,
                "optimization_goals": optimization_goals,
                "recommendations": ranked_recommendations,
                "simulations": optimization_simulations,
                "optimization_potential": self._calculate_optimization_potential(
                    build_analysis, ranked_recommendations
                )
            }
            
        except Exception as e:
            logger.error(f"Character build optimization failed: {e}")
            return {
                "success": False,
                "errors": [f"Build optimization failed: {str(e)}"]
            }
    
    # === Private Helper Methods ===
    
    def _validate_content_rules(self, content: Dict[str, Any], 
                              content_type: str) -> ValidationResult:
        """Validate content against D&D 2024 rules."""
        return self.rule_engine.validate_content_rules(content, content_type)
    
    def _test_system_compatibility(self, content: Dict[str, Any],
                                 content_type: str,
                                 target_systems: List[str]) -> Dict[str, Any]:
        """Test compatibility with existing D&D systems."""
        compatibility_results = {}
        
        for system in target_systems:
            compatibility_results[system] = self.integration_tester.test_system_compatibility(
                content, content_type, system
            )
        
        return {
            "overall_compatible": all(result["compatible"] for result in compatibility_results.values()),
            "system_results": compatibility_results,
            "compatibility_score": self._calculate_compatibility_score(compatibility_results)
        }
    
    def _analyze_multiclass_integration(self, content: Dict[str, Any],
                                      content_type: str) -> Dict[str, Any]:
        """Analyze multiclass integration compatibility."""
        if content_type == "class":
            return self.multiclass_engine.analyze_class_multiclass_compatibility(content)
        elif content_type == "species":
            return self.multiclass_engine.analyze_species_multiclass_compatibility(content)
        else:
            return {"compatible": True, "notes": "Not applicable for this content type"}
    
    def _test_character_integration(self, content: Dict[str, Any],
                                  content_type: str,
                                  character_id: str) -> Dict[str, Any]:
        """Test integration with specific character."""
        character = self.character_repository.get_by_id(character_id)
        return self.integration_tester.test_character_integration(
            content, content_type, character
        )
    
    def _generate_integration_recommendations(self, *validation_results) -> List[Dict[str, Any]]:
        """Generate recommendations based on integration analysis."""
        recommendations = []
        
        for result in validation_results:
            if result and isinstance(result, dict):
                if "recommendations" in result:
                    recommendations.extend(result["recommendations"])
        
        # Remove duplicates and prioritize
        unique_recommendations = []
        seen = set()
        
        for rec in recommendations:
            rec_key = (rec.get("type", ""), rec.get("description", ""))
            if rec_key not in seen:
                unique_recommendations.append(rec)
                seen.add(rec_key)
        
        return sorted(unique_recommendations, key=lambda x: x.get("priority", "medium"))
    
    def _is_integration_successful(self, rule_validation: ValidationResult,
                                 system_compatibility: Dict[str, Any]) -> bool:
        """Check if integration is successful."""
        return (rule_validation.is_valid and 
                system_compatibility.get("overall_compatible", False))
    
    def _register_integrated_content(self, content: Dict[str, Any],
                                   content_type: str) -> Dict[str, Any]:
        """Register successfully integrated content."""
        return self.content_registry.register_content(content, content_type)
    
    def _calculate_integration_score(self, *validation_results) -> float:
        """Calculate overall integration score."""
        scores = []
        
        for result in validation_results:
            if result and isinstance(result, dict):
                if "score" in result:
                    scores.append(result["score"])
                elif "is_valid" in result:
                    scores.append(1.0 if result["is_valid"] else 0.0)
        
        return sum(scores) / len(scores) if scores else 0.5
    
    def _build_multiclass_character(self, concept: Dict[str, Any],
                                  progression: List[Dict[str, Any]]) -> Character:
        """Build character following multiclass progression."""
        # Start with base character
        character = self.character_builder.create_base_character(concept)
        
        # Apply progression level by level
        for level_data in progression:
            character = self.character_builder.apply_level_progression(
                character, level_data
            )
        
        return character
    
    def _has_spellcasting_classes(self, class_combination: List[str]) -> bool:
        """Check if any classes in combination have spellcasting."""
        spellcasting_classes = [
            "Artificer", "Bard", "Cleric", "Druid", "Paladin", 
            "Ranger", "Sorcerer", "Warlock", "Wizard"
        ]
        return any(cls in spellcasting_classes for cls in class_combination)
    
    def _generate_multiclass_recommendations(self, character: Character,
                                           feature_interactions: Dict[str, Any],
                                           goals: List[str]) -> List[Dict[str, Any]]:
        """Generate multiclass build recommendations."""
        recommendations = []
        
        # Analyze feature synergies
        if feature_interactions.get("synergies"):
            for synergy in feature_interactions["synergies"]:
                recommendations.append({
                    "type": "synergy_optimization",
                    "description": f"Optimize {synergy['features']} synergy",
                    "impact": synergy["impact"],
                    "priority": "high" if synergy["impact"] > 0.7 else "medium"
                })
        
        # Goal-specific recommendations
        for goal in goals:
            goal_recommendations = self._generate_goal_specific_recommendations(
                character, goal
            )
            recommendations.extend(goal_recommendations)
        
        return recommendations
    
    def _calculate_multiclass_effectiveness_score(self, character: Character,
                                                goals: List[str]) -> float:
        """Calculate multiclass build effectiveness."""
        # Implementation would analyze character effectiveness against goals
        return 0.8  # Placeholder
    
    def _generate_character_improvement_suggestions(self, character: Character,
                                                  validation_result: ValidationResult) -> List[Dict[str, Any]]:
        """Generate suggestions for character improvement."""
        suggestions = []
        
        for issue in validation_result.issues:
            if issue.severity == "error":
                suggestions.append({
                    "type": "error_fix",
                    "description": issue.message,
                    "suggested_action": issue.suggested_fix,
                    "priority": "high"
                })
            elif issue.severity == "warning":
                suggestions.append({
                    "type": "optimization",
                    "description": issue.message,
                    "suggested_action": issue.suggested_fix,
                    "priority": "medium"
                })
        
        return suggestions
    
    def _calculate_character_build_score(self, character: Character,
                                       validation_result: ValidationResult) -> float:
        """Calculate overall character build score."""
        base_score = 1.0 if validation_result.is_valid else 0.5
        
        # Adjust based on warnings and optimizations
        warning_penalty = len(validation_result.warnings) * 0.05
        optimization_bonus = validation_result.optimization_score * 0.3
        
        return min(1.0, max(0.0, base_score - warning_penalty + optimization_bonus))
    
    def _analyze_character_build(self, character: Character) -> Dict[str, Any]:
        """Analyze character build strengths and weaknesses."""
        return {
            "combat_effectiveness": self._analyze_combat_effectiveness(character),
            "versatility_score": self._analyze_versatility(character),
            "survivability": self._analyze_survivability(character),
            "utility_coverage": self._analyze_utility_coverage(character),
            "thematic_consistency": self._analyze_thematic_consistency(character)
        }
    
    def _generate_build_optimizations(self, character: Character,
                                    goals: List[str],
                                    analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate build optimization recommendations."""
        optimizations = []
        
        for goal in goals:
            if goal == "damage" and analysis["combat_effectiveness"] < 0.7:
                optimizations.append({
                    "type": "damage_optimization",
                    "description": "Improve damage output through feat/spell selection",
                    "expected_improvement": 0.2,
                    "difficulty": "medium"
                })
            elif goal == "survivability" and analysis["survivability"] < 0.7:
                optimizations.append({
                    "type": "survivability_optimization", 
                    "description": "Improve survivability through AC/HP optimization",
                    "expected_improvement": 0.25,
                    "difficulty": "easy"
                })
        
        return optimizations
    
    def _simulate_build_optimizations(self, character: Character,
                                    recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Simulate outcomes of build optimizations."""
        simulations = {}
        
        for rec in recommendations:
            # Simulate the optimization
            simulated_improvement = rec.get("expected_improvement", 0.1)
            simulations[rec["type"]] = {
                "estimated_improvement": simulated_improvement,
                "confidence": 0.8,
                "trade_offs": []
            }
        
        return simulations
    
    def _rank_optimization_recommendations(self, recommendations: List[Dict[str, Any]],
                                         simulations: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Rank recommendations by effectiveness."""
        for rec in recommendations:
            sim_data = simulations.get(rec["type"], {})
            rec["effectiveness_score"] = (
                sim_data.get("estimated_improvement", 0.1) * 
                sim_data.get("confidence", 0.5)
            )
        
        return sorted(recommendations, key=lambda x: x["effectiveness_score"], reverse=True)
    
    def _calculate_optimization_potential(self, analysis: Dict[str, Any],
                                        recommendations: List[Dict[str, Any]]) -> float:
        """Calculate optimization potential."""
        current_effectiveness = sum(analysis.values()) / len(analysis)
        potential_improvement = sum(
            rec.get("effectiveness_score", 0.1) for rec in recommendations
        )
        
        return min(1.0, current_effectiveness + potential_improvement)
    
    # Additional helper methods...
    def _calculate_compatibility_score(self, compatibility_results: Dict[str, Any]) -> float:
        """Calculate compatibility score."""
        scores = [result.get("score", 0.5) for result in compatibility_results.values()]
        return sum(scores) / len(scores) if scores else 0.5
    
    def _generate_goal_specific_recommendations(self, character: Character,
                                              goal: str) -> List[Dict[str, Any]]:
        """Generate recommendations for specific optimization goals."""
        return []  # Implementation would depend on specific goals
    
    def _analyze_combat_effectiveness(self, character: Character) -> float:
        """Analyze combat effectiveness."""
        return 0.75  # Placeholder implementation
    
    def _analyze_versatility(self, character: Character) -> float:
        """Analyze character versatility."""
        return 0.8  # Placeholder implementation
    
    def _analyze_survivability(self, character: Character) -> float:
        """Analyze character survivability."""
        return 0.7  # Placeholder implementation
    
    def _analyze_utility_coverage(self, character: Character) -> float:
        """Analyze utility coverage."""
        return 0.6  # Placeholder implementation
    
    def _analyze_thematic_consistency(self, character: Character) -> float:
        """Analyze thematic consistency."""
        return 0.85  # Placeholder implementation