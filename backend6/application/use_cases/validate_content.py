"""
Unified Content Validation Use Case

Central orchestrator for all D&D content and character validation workflows.
This consolidates validation for generated content, characters, multiclass builds,
and system integration while maintaining rule compliance and creative flexibility.
"""

from typing import Dict, Any, List, Optional, Union
import logging

from ...core.entities.character import Character
from ...core.entities.generated_content import GeneratedContent
from ...core.value_objects.validation_result import ValidationResult
from ...core.value_objects.multiclass_result import MulticlassResult
from ...domain.services.validation_engine import CharacterValidationEngine
from ...domain.services.content_validation_service import ContentValidationService
from ...domain.services.balance_validator import BalanceValidatorService
from ...domain.services.multiclass_engine import MulticlassEngine
from ...domain.services.character_stats_service import CharacterStatsService
from ...domain.repositories.character_repository import CharacterRepository
from ...domain.repositories.content_repository import ContentRepository
from ...infrastructure.validation.rule_engine import RuleEngine
from ...infrastructure.validation.balance_analyzer import BalanceAnalyzer
from ...infrastructure.llm.balance_llm_service import BalanceLLMService
from ..dtos.content_dto import (
    ContentValidationRequest,
    ContentValidationResponse,
    CharacterValidationRequest,
    CharacterValidationResponse,
    MulticlassValidationRequest,
    MulticlassValidationResponse,
    SystemValidationRequest,
    SystemValidationResponse
)

logger = logging.getLogger(__name__)

class ValidateContentUseCase:
    """
    Unified use case for all validation workflows.
    
    This consolidates content validation, character validation, multiclass validation,
    and system integration validation into a single orchestrator that maintains
    D&D rule compliance while supporting creative content generation.
    """
    
    def __init__(self,
                 validation_engine: CharacterValidationEngine,
                 content_validator: ContentValidationService,
                 balance_validator: BalanceValidatorService,
                 multiclass_engine: MulticlassEngine,
                 character_stats_service: CharacterStatsService,
                 character_repository: CharacterRepository,
                 content_repository: ContentRepository,
                 rule_engine: RuleEngine,
                 balance_analyzer: BalanceAnalyzer,
                 balance_llm: BalanceLLMService):
        self.validation_engine = validation_engine
        self.content_validator = content_validator
        self.balance_validator = balance_validator
        self.multiclass_engine = multiclass_engine
        self.character_stats_service = character_stats_service
        self.character_repository = character_repository
        self.content_repository = content_repository
        self.rule_engine = rule_engine
        self.balance_analyzer = balance_analyzer
        self.balance_llm = balance_llm
    
    def validate_generated_content(self, request: ContentValidationRequest) -> ContentValidationResponse:
        """
        Validate generated content for D&D rule compliance and balance.
        
        Args:
            request: Content validation request
            
        Returns:
            ContentValidationResponse with comprehensive validation results
        """
        try:
            # 1. Rule compliance validation
            rule_validation = self._validate_content_rules(
                request.content, request.content_type
            )
            
            # 2. Balance validation using statistical analysis
            balance_validation = self._validate_content_balance(
                request.content, request.content_type, request.context
            )
            
            # 3. LLM-assisted validation for creative elements
            if request.include_llm_analysis:
                llm_validation = self.balance_llm.validate_content_creativity(
                    request.content, request.content_type, request.context
                )
            else:
                llm_validation = None
            
            # 4. Thematic consistency validation if concept provided
            thematic_validation = None
            if request.character_concept:
                thematic_validation = self._validate_thematic_consistency(
                    request.content, request.content_type, request.character_concept
                )
            
            # 5. System integration validation
            integration_validation = self._validate_system_integration(
                request.content, request.content_type
            )
            
            # 6. Generate comprehensive validation report
            validation_report = self._generate_content_validation_report(
                rule_validation, balance_validation, llm_validation, 
                thematic_validation, integration_validation
            )
            
            # 7. Calculate overall validation score
            overall_score = self._calculate_content_validation_score(
                rule_validation, balance_validation, integration_validation
            )
            
            return ContentValidationResponse(
                success=True,
                content_type=request.content_type,
                rule_validation=rule_validation,
                balance_validation=balance_validation,
                llm_validation=llm_validation,
                thematic_validation=thematic_validation,
                integration_validation=integration_validation,
                validation_report=validation_report,
                overall_score=overall_score,
                is_valid=overall_score >= 0.7  # Configurable threshold
            )
            
        except Exception as e:
            logger.error(f"Content validation failed: {e}")
            return ContentValidationResponse(
                success=False,
                errors=[f"Content validation failed: {str(e)}"]
            )
    
    def validate_character(self, request: CharacterValidationRequest) -> CharacterValidationResponse:
        """
        Comprehensive character validation with multiple analysis types.
        
        Args:
            request: Character validation request
            
        Returns:
            CharacterValidationResponse with validation results and analysis
        """
        try:
            character = self.character_repository.get_by_id(request.character_id)
            
            # Perform validation based on type
            validation_results = {}
            
            if "comprehensive" in request.validation_types:
                comprehensive_result = self.validation_engine.validate_character_comprehensive(
                    character, request.context
                )
                validation_results["comprehensive"] = comprehensive_result
            
            if "creation_step" in request.validation_types:
                step_result = self.validation_engine.validate_character_creation_step(
                    character, request.step_name, request.context
                )
                validation_results["creation_step"] = step_result
            
            if "optimization" in request.validation_types:
                optimization_result = self.validation_engine.validate_character_optimization(
                    character
                )
                validation_results["optimization"] = optimization_result
            
            if "balance" in request.validation_types:
                balance_result = self._validate_character_balance(character)
                validation_results["balance"] = balance_result
            
            if "thematic_consistency" in request.validation_types:
                thematic_result = self._validate_character_thematic_consistency(character)
                validation_results["thematic_consistency"] = thematic_result
            
            # Generate character statistics for context
            character_stats = None
            if request.include_statistics:
                character_stats = self.character_stats_service.calculate_comprehensive_stats(
                    character
                )
            
            # Generate improvement suggestions
            improvement_suggestions = self._generate_character_improvement_suggestions(
                character, validation_results
            )
            
            # Create validation summary
            validation_summary = self._create_character_validation_summary(
                character, validation_results
            )
            
            return CharacterValidationResponse(
                success=True,
                character_id=request.character_id,
                character_name=character.name,
                validation_results=validation_results,
                character_statistics=character_stats,
                improvement_suggestions=improvement_suggestions,
                validation_summary=validation_summary,
                overall_valid=self._is_character_overall_valid(validation_results)
            )
            
        except Exception as e:
            logger.error(f"Character validation failed: {e}")
            return CharacterValidationResponse(
                success=False,
                errors=[f"Character validation failed: {str(e)}"]
            )
    
    def validate_multiclass_build(self, request: MulticlassValidationRequest) -> MulticlassValidationResponse:
        """
        Validate multiclass character builds for rule compliance and optimization.
        
        Args:
            request: Multiclass validation request
            
        Returns:
            MulticlassValidationResponse with multiclass-specific validation
        """
        try:
            character = self.character_repository.get_by_id(request.character_id)
            
            # 1. Validate multiclass prerequisites
            prerequisite_validation = self.multiclass_engine.validate_multiclass_prerequisites(
                character, request.target_classes if request.target_classes else None
            )
            
            # 2. Validate feature interactions
            feature_interaction_validation = self.multiclass_engine.validate_feature_interactions(
                character
            )
            
            # 3. Validate spellcasting progression if applicable
            spellcasting_validation = None
            if self._character_has_spellcasting(character):
                spellcasting_validation = self.multiclass_engine.validate_spellcasting_progression(
                    character
                )
            
            # 4. Analyze multiclass optimization
            optimization_analysis = self.multiclass_engine.analyze_multiclass_optimization(
                character, request.optimization_goals
            )
            
            # 5. Generate multiclass recommendations
            multiclass_recommendations = self._generate_multiclass_recommendations(
                character, prerequisite_validation, feature_interaction_validation, 
                optimization_analysis
            )
            
            return MulticlassValidationResponse(
                success=True,
                character_id=request.character_id,
                prerequisite_validation=prerequisite_validation,
                feature_interaction_validation=feature_interaction_validation,
                spellcasting_validation=spellcasting_validation,
                optimization_analysis=optimization_analysis,
                multiclass_recommendations=multiclass_recommendations,
                is_valid_multiclass=prerequisite_validation.is_valid and 
                                  feature_interaction_validation.is_valid
            )
            
        except Exception as e:
            logger.error(f"Multiclass validation failed: {e}")
            return MulticlassValidationResponse(
                success=False,
                errors=[f"Multiclass validation failed: {str(e)}"]
            )
    
    def validate_system_integration(self, request: SystemValidationRequest) -> SystemValidationResponse:
        """
        Validate integration between different system components.
        
        Args:
            request: System validation request
            
        Returns:
            SystemValidationResponse with integration validation results
        """
        try:
            validation_results = {}
            
            # Validate different integration scenarios
            if "content_character_integration" in request.validation_scopes:
                content_char_validation = self._validate_content_character_integration(
                    request.content, request.character_id
                )
                validation_results["content_character_integration"] = content_char_validation
            
            if "multiclass_integration" in request.validation_scopes:
                multiclass_integration = self._validate_multiclass_system_integration(
                    request.character_id, request.integration_context
                )
                validation_results["multiclass_integration"] = multiclass_integration
            
            if "custom_content_integration" in request.validation_scopes:
                custom_integration = self._validate_custom_content_integration(
                    request.custom_content, request.integration_context
                )
                validation_results["custom_content_integration"] = custom_integration
            
            if "rule_system_compliance" in request.validation_scopes:
                rule_compliance = self._validate_rule_system_compliance(
                    request.system_components
                )
                validation_results["rule_system_compliance"] = rule_compliance
            
            # Generate integration report
            integration_report = self._generate_system_integration_report(
                validation_results
            )
            
            return SystemValidationResponse(
                success=True,
                validation_results=validation_results,
                integration_report=integration_report,
                overall_integration_valid=self._is_system_integration_valid(validation_results)
            )
            
        except Exception as e:
            logger.error(f"System validation failed: {e}")
            return SystemValidationResponse(
                success=False,
                errors=[f"System validation failed: {str(e)}"]
            )
    
    def validate_content_suite(self, content_suite: Dict[str, Any], 
                             character_concept: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Validate a complete content suite for coherence and compatibility.
        
        Args:
            content_suite: Dictionary of content types and their definitions
            character_concept: Optional character concept for thematic validation
            
        Returns:
            Validation results for the entire content suite
        """
        try:
            suite_validation_results = {}
            
            # Validate each content type individually
            for content_type, content in content_suite.items():
                content_request = ContentValidationRequest(
                    content=content,
                    content_type=content_type,
                    character_concept=character_concept,
                    include_llm_analysis=True
                )
                
                content_validation = self.validate_generated_content(content_request)
                suite_validation_results[content_type] = content_validation
            
            # Validate suite coherence
            coherence_validation = self._validate_suite_coherence(
                content_suite, character_concept
            )
            
            # Validate cross-content compatibility
            compatibility_validation = self._validate_cross_content_compatibility(
                content_suite
            )
            
            return {
                "success": True,
                "individual_validations": suite_validation_results,
                "coherence_validation": coherence_validation,
                "compatibility_validation": compatibility_validation,
                "overall_suite_valid": self._is_content_suite_valid(
                    suite_validation_results, coherence_validation, compatibility_validation
                )
            }
            
        except Exception as e:
            logger.error(f"Content suite validation failed: {e}")
            return {
                "success": False,
                "errors": [f"Suite validation failed: {str(e)}"]
            }
    
    # === Private Helper Methods ===
    
    def _validate_content_rules(self, content: Dict[str, Any], 
                              content_type: str) -> ValidationResult:
        """Validate content against D&D 2024 rules."""
        return self.rule_engine.validate_content_rules(content, content_type)
    
    def _validate_content_balance(self, content: Dict[str, Any],
                                content_type: str,
                                context: Dict[str, Any]) -> ValidationResult:
        """Validate content balance using statistical analysis."""
        balance_analysis = self.balance_analyzer.analyze_content_balance(
            content, content_type
        )
        
        return ValidationResult(
            is_valid=balance_analysis["balanced"],
            issues=balance_analysis.get("issues", []),
            score=balance_analysis.get("balance_score", 0.5)
        )
    
    def _validate_thematic_consistency(self, content: Dict[str, Any],
                                     content_type: str,
                                     character_concept: Dict[str, Any]) -> ValidationResult:
        """Validate thematic consistency with character concept."""
        # Extract themes from content and concept
        content_themes = self._extract_content_themes(content, content_type)
        concept_themes = self._extract_concept_themes(character_concept)
        
        # Calculate thematic alignment
        alignment_score = self._calculate_thematic_alignment(content_themes, concept_themes)
        
        return ValidationResult(
            is_valid=alignment_score >= 0.7,
            score=alignment_score,
            metadata={"content_themes": content_themes, "concept_themes": concept_themes}
        )
    
    def _validate_system_integration(self, content: Dict[str, Any],
                                   content_type: str) -> ValidationResult:
        """Validate integration with existing D&D systems."""
        integration_issues = []
        
        # Check for system conflicts
        conflicts = self.rule_engine.check_system_conflicts(content, content_type)
        integration_issues.extend(conflicts)
        
        # Check multiclass compatibility
        multiclass_compatibility = self.multiclass_engine.check_content_multiclass_compatibility(
            content, content_type
        )
        if not multiclass_compatibility["compatible"]:
            integration_issues.extend(multiclass_compatibility["issues"])
        
        return ValidationResult(
            is_valid=len(integration_issues) == 0,
            issues=integration_issues,
            metadata={"multiclass_compatibility": multiclass_compatibility}
        )
    
    def _validate_character_balance(self, character: Character) -> ValidationResult:
        """Validate character balance against standard metrics."""
        balance_analysis = self.balance_analyzer.analyze_character_balance(character)
        
        return ValidationResult(
            is_valid=balance_analysis["balanced"],
            score=balance_analysis["balance_score"],
            issues=balance_analysis.get("issues", []),
            metadata=balance_analysis
        )
    
    def _validate_character_thematic_consistency(self, character: Character) -> ValidationResult:
        """Validate character's thematic consistency."""
        # Analyze character for thematic elements
        character_themes = self._extract_character_themes(character)
        
        # Check for thematic conflicts
        thematic_conflicts = self._find_thematic_conflicts(character_themes)
        
        # Calculate consistency score
        consistency_score = self._calculate_thematic_consistency_score(character_themes)
        
        return ValidationResult(
            is_valid=len(thematic_conflicts) == 0 and consistency_score >= 0.7,
            score=consistency_score,
            issues=thematic_conflicts,
            metadata={"themes": character_themes}
        )
    
    def _character_has_spellcasting(self, character: Character) -> bool:
        """Check if character has spellcasting capabilities."""
        spellcasting_classes = {
            "Artificer", "Bard", "Cleric", "Druid", "Paladin",
            "Ranger", "Sorcerer", "Warlock", "Wizard"
        }
        
        # Check primary class and multiclass
        if hasattr(character, 'classes'):
            return any(cls.name in spellcasting_classes for cls in character.classes)
        else:
            return character.character_class in spellcasting_classes
    
    def _generate_content_validation_report(self, *validations) -> str:
        """Generate comprehensive validation report for content."""
        report_sections = []
        
        for validation in validations:
            if validation and isinstance(validation, ValidationResult):
                if validation.is_valid:
                    report_sections.append("✅ Validation passed")
                else:
                    report_sections.append(f"❌ Issues found: {len(validation.issues)}")
        
        return " | ".join(report_sections)
    
    def _calculate_content_validation_score(self, *validations) -> float:
        """Calculate overall content validation score."""
        scores = []
        
        for validation in validations:
            if validation and isinstance(validation, ValidationResult):
                scores.append(validation.score if hasattr(validation, 'score') else 
                            (1.0 if validation.is_valid else 0.0))
        
        return sum(scores) / len(scores) if scores else 0.5
    
    def _generate_character_improvement_suggestions(self, character: Character,
                                                  validation_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate character improvement suggestions based on validation results."""
        suggestions = []
        
        for validation_type, result in validation_results.items():
            if hasattr(result, 'issues') and result.issues:
                for issue in result.issues:
                    suggestions.append({
                        "type": validation_type,
                        "issue": issue.message if hasattr(issue, 'message') else str(issue),
                        "suggestion": issue.suggested_fix if hasattr(issue, 'suggested_fix') else 
                                    "Review and correct this issue",
                        "priority": issue.severity if hasattr(issue, 'severity') else "medium"
                    })
        
        return suggestions
    
    def _create_character_validation_summary(self, character: Character,
                                           validation_results: Dict[str, Any]) -> str:
        """Create human-readable validation summary."""
        summary_parts = [f"Character: {character.name}"]
        
        valid_count = sum(1 for result in validation_results.values() 
                         if hasattr(result, 'is_valid') and result.is_valid)
        total_count = len(validation_results)
        
        summary_parts.append(f"Validations: {valid_count}/{total_count} passed")
        
        return " | ".join(summary_parts)
    
    def _is_character_overall_valid(self, validation_results: Dict[str, Any]) -> bool:
        """Determine if character is overall valid."""
        critical_validations = ["comprehensive", "balance"]
        
        for validation_type in critical_validations:
            if validation_type in validation_results:
                result = validation_results[validation_type]
                if hasattr(result, 'is_valid') and not result.is_valid:
                    return False
        
        return True
    
    def _generate_multiclass_recommendations(self, character: Character,
                                           *validation_results) -> List[Dict[str, Any]]:
        """Generate multiclass-specific recommendations."""
        recommendations = []
        
        for result in validation_results:
            if result and hasattr(result, 'issues'):
                for issue in result.issues:
                    recommendations.append({
                        "type": "multiclass_optimization",
                        "description": issue.message if hasattr(issue, 'message') else str(issue),
                        "action": issue.suggested_fix if hasattr(issue, 'suggested_fix') else 
                                "Consider alternative multiclass progression"
                    })
        
        return recommendations
    
    def _validate_content_character_integration(self, content: Dict[str, Any],
                                              character_id: str) -> ValidationResult:
        """Validate content integration with specific character."""
        character = self.character_repository.get_by_id(character_id)
        
        # Check compatibility
        compatibility_issues = self.content_validator.check_character_content_compatibility(
            character, content
        )
        
        return ValidationResult(
            is_valid=len(compatibility_issues) == 0,
            issues=compatibility_issues
        )
    
    def _validate_multiclass_system_integration(self, character_id: str,
                                              context: Dict[str, Any]) -> ValidationResult:
        """Validate multiclass integration with system."""
        character = self.character_repository.get_by_id(character_id)
        
        integration_result = self.multiclass_engine.validate_system_integration(
            character, context
        )
        
        return integration_result
    
    def _validate_custom_content_integration(self, custom_content: List[Dict[str, Any]],
                                           context: Dict[str, Any]) -> ValidationResult:
        """Validate custom content integration."""
        integration_issues = []
        
        for content in custom_content:
            content_issues = self.content_validator.validate_custom_content_integration(
                content, context
            )
            integration_issues.extend(content_issues)
        
        return ValidationResult(
            is_valid=len(integration_issues) == 0,
            issues=integration_issues
        )
    
    def _validate_rule_system_compliance(self, system_components: List[str]) -> ValidationResult:
        """Validate rule system compliance."""
        compliance_issues = []
        
        for component in system_components:
            component_issues = self.rule_engine.validate_system_component(component)
            compliance_issues.extend(component_issues)
        
        return ValidationResult(
            is_valid=len(compliance_issues) == 0,
            issues=compliance_issues
        )
    
    def _generate_system_integration_report(self, validation_results: Dict[str, Any]) -> str:
        """Generate system integration report."""
        report_parts = []
        
        for scope, result in validation_results.items():
            if hasattr(result, 'is_valid'):
                status = "✅" if result.is_valid else "❌"
                report_parts.append(f"{scope}: {status}")
        
        return " | ".join(report_parts)
    
    def _is_system_integration_valid(self, validation_results: Dict[str, Any]) -> bool:
        """Check if system integration is overall valid."""
        return all(result.is_valid for result in validation_results.values() 
                  if hasattr(result, 'is_valid'))
    
    def _validate_suite_coherence(self, content_suite: Dict[str, Any],
                                character_concept: Optional[Dict[str, Any]]) -> ValidationResult:
        """Validate coherence across content suite."""
        coherence_issues = []
        
        # Check thematic coherence if concept provided
        if character_concept:
            suite_themes = self._extract_suite_themes(content_suite)
            concept_themes = self._extract_concept_themes(character_concept)
            
            coherence_score = self._calculate_thematic_alignment(suite_themes, concept_themes)
            
            if coherence_score < 0.7:
                coherence_issues.append("Suite themes not well aligned with character concept")
        
        return ValidationResult(
            is_valid=len(coherence_issues) == 0,
            score=coherence_score if character_concept else 1.0,
            issues=coherence_issues
        )
    
    def _validate_cross_content_compatibility(self, content_suite: Dict[str, Any]) -> ValidationResult:
        """Validate compatibility between different content types in suite."""
        compatibility_issues = []
        
        # Check for mechanical conflicts between content types
        for content_type, content in content_suite.items():
            for other_type, other_content in content_suite.items():
                if content_type != other_type:
                    conflicts = self.content_validator.check_content_conflicts(
                        content, content_type, other_content, other_type
                    )
                    compatibility_issues.extend(conflicts)
        
        return ValidationResult(
            is_valid=len(compatibility_issues) == 0,
            issues=compatibility_issues
        )
    
    def _is_content_suite_valid(self, individual_validations: Dict[str, Any],
                              coherence_validation: ValidationResult,
                              compatibility_validation: ValidationResult) -> bool:
        """Check if entire content suite is valid."""
        # All individual validations must pass
        individual_valid = all(
            validation.is_valid for validation in individual_validations.values()
            if hasattr(validation, 'is_valid')
        )
        
        return (individual_valid and 
                coherence_validation.is_valid and 
                compatibility_validation.is_valid)
    
    # Additional helper methods for theme extraction and analysis
    def _extract_content_themes(self, content: Dict[str, Any], content_type: str) -> List[str]:
        """Extract themes from content."""
        # Implementation would analyze content structure for thematic elements
        return []
    
    def _extract_concept_themes(self, character_concept: Dict[str, Any]) -> List[str]:
        """Extract themes from character concept."""
        # Implementation would analyze concept for thematic elements
        return []
    
    def _extract_character_themes(self, character: Character) -> List[str]:
        """Extract themes from character."""
        # Implementation would analyze character for thematic elements
        return []
    
    def _extract_suite_themes(self, content_suite: Dict[str, Any]) -> List[str]:
        """Extract themes from content suite."""
        # Implementation would analyze suite for common themes
        return []
    
    def _calculate_thematic_alignment(self, themes1: List[str], themes2: List[str]) -> float:
        """Calculate alignment score between two theme sets."""
        if not themes1 or not themes2:
            return 0.5
        
        common_themes = set(themes1) & set(themes2)
        total_themes = set(themes1) | set(themes2)
        
        return len(common_themes) / len(total_themes) if total_themes else 0.5
    
    def _find_thematic_conflicts(self, themes: List[str]) -> List[str]:
        """Find conflicts within theme set."""
        # Implementation would identify contradictory themes
        return []
    
    def _calculate_thematic_consistency_score(self, themes: List[str]) -> float:
        """Calculate thematic consistency score."""
        # Implementation would analyze theme coherence
        return 0.8

# update with the following code snippet 
from typing import Dict, Any
from ..dto.requests import CharacterValidationRequest
from ..dto.responses import CharacterValidationResponse
from ...domain.services.validation_coordinator import ValidationCoordinator

class ValidateCharacterUseCase:
    """Clean character validation without legacy dependencies."""
    
    def __init__(self, validation_coordinator: ValidationCoordinator):
        self.validation_coordinator = validation_coordinator
    
    def execute(self, request: CharacterValidationRequest) -> CharacterValidationResponse:
        """Execute character validation using D&D 5e framework."""
        try:
            # Validate using coordinator
            validation_result = self.validation_coordinator.validate_character(
                request.character_data
            )
            
            return CharacterValidationResponse(
                success=validation_result.valid,
                validation_result=validation_result.to_dict(),
                summary=self._generate_summary(validation_result),
                recommendations=validation_result.recommendations
            )
        except Exception as e:
            return CharacterValidationResponse(
                success=False,
                errors=[f"Validation failed: {str(e)}"],
                summary="Validation system error"
            )
    
    def execute_step_validation(self, step_name: str, character_data: Dict[str, Any]) -> CharacterValidationResponse:
        """Execute step-specific validation."""
        try:
            validation_result = self.validation_coordinator.validate_creation_step(
                step_name, character_data
            )
            
            return CharacterValidationResponse(
                success=validation_result.valid,
                validation_result=validation_result.to_dict(),
                summary=self._generate_summary(validation_result),
                step_name=step_name
            )
        except Exception as e:
            return CharacterValidationResponse(
                success=False,
                errors=[f"Step validation failed: {str(e)}"],
                summary=f"Step {step_name} validation error"
            )
    
    def _generate_summary(self, result: ValidationResult) -> str:
        """Generate human-readable summary."""
        if result.valid:
            return f"✅ Character validation passed - D&D 5e compliant"
        else:
            issues = len(result.issues)
            warnings = len(result.warnings)
            return f"❌ Character validation failed: {issues} issues, {warnings} warnings"