"""
Content Optimization Use Case

Central optimizer for balancing generated content and ensuring D&D rule compliance.
This use case handles mechanical balance analysis, power level optimization, and
rule validation for all generated content types.
"""

from typing import Dict, Any, List, Optional, Union
import logging

from ...core.entities.character import Character
from ...core.entities.generated_content import GeneratedContent
from ...core.value_objects.validation_result import ValidationResult
from ...core.value_objects.generation_constraints import GenerationConstraints
from ...domain.services.balance_validator import BalanceValidatorService
from ...domain.services.content_validation_service import ContentValidationService
from ...domain.services.multiclass_engine import MulticlassEngine
from ...domain.repositories.character_repository import CharacterRepository
from ...infrastructure.llm.balance_llm_service import BalanceLLMService
from ...infrastructure.validation.balance_analyzer import BalanceAnalyzer
from ..dtos.content_dto import (
    OptimizationRequest, 
    OptimizationResponse, 
    BalanceAnalysisRequest,
    BalanceAnalysisResponse
)

logger = logging.getLogger(__name__)

class ContentOptimizerUseCase:
    """
    Central use case for content optimization and balance validation.
    
    Handles:
    - Generated content balance optimization
    - D&D rule compliance validation
    - Power level analysis and adjustment
    - Multiclass compatibility optimization
    - Statistical balance analysis
    """
    
    def __init__(self,
                 balance_validator: BalanceValidatorService,
                 content_validator: ContentValidationService,
                 multiclass_engine: MulticlassEngine,
                 balance_llm: BalanceLLMService,
                 balance_analyzer: BalanceAnalyzer,
                 character_repository: CharacterRepository):
        self.balance_validator = balance_validator
        self.content_validator = content_validator
        self.multiclass_engine = multiclass_engine
        self.balance_llm = balance_llm
        self.balance_analyzer = balance_analyzer
        self.character_repository = character_repository
    
    def optimize_generated_content(self, request: OptimizationRequest) -> OptimizationResponse:
        """
        Optimize generated content for balance and rule compliance.
        
        Args:
            request: Content optimization request
            
        Returns:
            OptimizationResponse with optimized content and analysis
        """
        try:
            # 1. Validate content against D&D rules
            rule_validation = self._validate_content_rules(
                request.content, request.content_type
            )
            
            # 2. Analyze mechanical balance
            balance_analysis = self._analyze_content_balance(
                request.content, request.content_type, request.context
            )
            
            # 3. Generate optimization recommendations
            optimization_recommendations = self._generate_optimization_recommendations(
                request.content, rule_validation, balance_analysis
            )
            
            # 4. Apply optimizations if requested
            optimized_content = request.content
            if request.apply_optimizations:
                optimized_content = self._apply_optimizations(
                    request.content, optimization_recommendations
                )
            
            # 5. Validate multiclass compatibility if applicable
            multiclass_compatibility = self._validate_multiclass_compatibility(
                optimized_content, request.content_type
            )
            
            # 6. Generate statistical comparison
            statistical_analysis = self._generate_statistical_analysis(
                optimized_content, request.content_type
            )
            
            return OptimizationResponse(
                success=True,
                original_content=request.content,
                optimized_content=optimized_content,
                rule_validation=rule_validation,
                balance_analysis=balance_analysis,
                optimization_recommendations=optimization_recommendations,
                multiclass_compatibility=multiclass_compatibility,
                statistical_analysis=statistical_analysis,
                optimization_confidence=self._calculate_optimization_confidence(
                    rule_validation, balance_analysis
                )
            )
            
        except Exception as e:
            logger.error(f"Content optimization failed: {e}")
            return OptimizationResponse(
                success=False,
                errors=[f"Optimization failed: {str(e)}"]
            )
    
    def analyze_content_balance(self, request: BalanceAnalysisRequest) -> BalanceAnalysisResponse:
        """
        Perform comprehensive balance analysis on content.
        
        Args:
            request: Balance analysis request
            
        Returns:
            BalanceAnalysisResponse with detailed balance metrics
        """
        try:
            # 1. Statistical power level analysis
            power_analysis = self.balance_analyzer.analyze_power_level(
                request.content, request.content_type
            )
            
            # 2. Comparative analysis with PHB content
            comparative_analysis = self.balance_analyzer.compare_with_official_content(
                request.content, request.content_type
            )
            
            # 3. Mechanical complexity analysis
            complexity_analysis = self.balance_analyzer.analyze_mechanical_complexity(
                request.content
            )
            
            # 4. LLM-assisted balance assessment
            llm_assessment = self.balance_llm.assess_content_balance(
                request.content, request.content_type, request.context
            )
            
            # 5. Generate balance recommendations
            balance_recommendations = self._generate_balance_recommendations(
                power_analysis, comparative_analysis, complexity_analysis, llm_assessment
            )
            
            return BalanceAnalysisResponse(
                success=True,
                content_id=request.content.get("id", "unknown"),
                power_analysis=power_analysis,
                comparative_analysis=comparative_analysis,
                complexity_analysis=complexity_analysis,
                llm_assessment=llm_assessment,
                balance_recommendations=balance_recommendations,
                overall_balance_score=self._calculate_overall_balance_score(
                    power_analysis, comparative_analysis, complexity_analysis
                )
            )
            
        except Exception as e:
            logger.error(f"Balance analysis failed: {e}")
            return BalanceAnalysisResponse(
                success=False,
                errors=[f"Balance analysis failed: {str(e)}"]
            )
    
    def optimize_character_build(self, character_id: str, 
                               optimization_goals: List[str]) -> Dict[str, Any]:
        """
        Optimize an existing character build for specific goals.
        
        Args:
            character_id: Character to optimize
            optimization_goals: Goals for optimization (e.g., "combat", "versatility")
            
        Returns:
            Optimization suggestions and analysis
        """
        try:
            character = self.character_repository.get_by_id(character_id)
            
            # 1. Analyze current character build
            current_analysis = self._analyze_character_build(character)
            
            # 2. Generate optimization suggestions based on goals
            optimization_suggestions = self._generate_character_optimizations(
                character, optimization_goals, current_analysis
            )
            
            # 3. Validate optimization suggestions
            suggestion_validation = self._validate_optimization_suggestions(
                character, optimization_suggestions
            )
            
            # 4. Calculate optimization impact
            impact_analysis = self._calculate_optimization_impact(
                character, optimization_suggestions
            )
            
            return {
                "success": True,
                "character_id": character_id,
                "current_analysis": current_analysis,
                "optimization_suggestions": optimization_suggestions,
                "suggestion_validation": suggestion_validation,
                "impact_analysis": impact_analysis,
                "implementation_priority": self._prioritize_optimizations(
                    optimization_suggestions, impact_analysis
                )
            }
            
        except Exception as e:
            logger.error(f"Character build optimization failed: {e}")
            return {
                "success": False,
                "errors": [f"Character optimization failed: {str(e)}"]
            }
    
    def validate_content_integration(self, content: Dict[str, Any], 
                                   content_type: str,
                                   target_character: Optional[Character] = None) -> Dict[str, Any]:
        """
        Validate how content integrates with existing D&D systems.
        
        Args:
            content: Content to validate
            content_type: Type of content (species, class, etc.)
            target_character: Optional target character for integration testing
            
        Returns:
            Integration validation results
        """
        try:
            # 1. Rule compliance validation
            rule_compliance = self.content_validator.validate_content_rules(
                content, content_type
            )
            
            # 2. System integration validation
            system_integration = self.content_validator.validate_system_integration(
                content, content_type
            )
            
            # 3. Character integration validation if target provided
            character_integration = None
            if target_character:
                character_integration = self.content_validator.validate_character_integration(
                    content, content_type, target_character
                )
            
            # 4. Multiclass integration validation
            multiclass_integration = self.multiclass_engine.validate_content_multiclass_compatibility(
                content, content_type
            )
            
            return {
                "success": True,
                "rule_compliance": rule_compliance,
                "system_integration": system_integration,
                "character_integration": character_integration,
                "multiclass_integration": multiclass_integration,
                "overall_integration_score": self._calculate_integration_score(
                    rule_compliance, system_integration, multiclass_integration
                )
            }
            
        except Exception as e:
            logger.error(f"Content integration validation failed: {e}")
            return {
                "success": False,
                "errors": [f"Integration validation failed: {str(e)}"]
            }
    
    # === Private Helper Methods ===
    
    def _validate_content_rules(self, content: Dict[str, Any], 
                              content_type: str) -> ValidationResult:
        """Validate content against D&D rules."""
        if content_type == "species":
            return self.content_validator.validate_species_rules(content)
        elif content_type == "class":
            return self.content_validator.validate_class_rules(content)
        elif content_type == "equipment":
            return self.content_validator.validate_equipment_rules(content)
        elif content_type == "spell":
            return self.content_validator.validate_spell_rules(content)
        elif content_type == "feat":
            return self.content_validator.validate_feat_rules(content)
        else:
            raise ValueError(f"Unknown content type: {content_type}")
    
    def _analyze_content_balance(self, content: Dict[str, Any], 
                               content_type: str,
                               context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze mechanical balance of content."""
        return self.balance_validator.analyze_content_balance(
            content, content_type, context
        )
    
    def _generate_optimization_recommendations(self, 
                                             content: Dict[str, Any],
                                             rule_validation: ValidationResult,
                                             balance_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate optimization recommendations based on validation and analysis."""
        recommendations = []
        
        # Add rule compliance recommendations
        for issue in rule_validation.issues:
            if issue.severity == "error":
                recommendations.append({
                    "type": "rule_compliance",
                    "priority": "high",
                    "description": issue.message,
                    "suggested_fix": issue.suggested_fix
                })
        
        # Add balance recommendations
        if balance_analysis.get("power_level", 0) > 1.2:  # 20% above average
            recommendations.append({
                "type": "power_reduction",
                "priority": "medium",
                "description": "Content appears overpowered compared to PHB options",
                "suggested_fix": "Reduce numerical bonuses or limit usage frequency"
            })
        elif balance_analysis.get("power_level", 0) < 0.8:  # 20% below average
            recommendations.append({
                "type": "power_increase",
                "priority": "low",
                "description": "Content appears underpowered compared to PHB options",
                "suggested_fix": "Increase numerical bonuses or add utility features"
            })
        
        return recommendations
    
    def _apply_optimizations(self, content: Dict[str, Any], 
                           recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply optimization recommendations to content."""
        optimized_content = content.copy()
        
        for recommendation in recommendations:
            if recommendation["type"] == "power_reduction":
                optimized_content = self._reduce_content_power(optimized_content)
            elif recommendation["type"] == "power_increase":
                optimized_content = self._increase_content_power(optimized_content)
            elif recommendation["type"] == "rule_compliance":
                optimized_content = self._fix_rule_compliance(
                    optimized_content, recommendation
                )
        
        return optimized_content
    
    def _validate_multiclass_compatibility(self, content: Dict[str, Any], 
                                         content_type: str) -> Dict[str, Any]:
        """Validate multiclass compatibility for content."""
        if content_type == "class":
            return self.multiclass_engine.validate_class_multiclass_compatibility(content)
        elif content_type == "species":
            return self.multiclass_engine.validate_species_multiclass_compatibility(content)
        else:
            return {"compatible": True, "notes": "Not applicable for this content type"}
    
    def _generate_statistical_analysis(self, content: Dict[str, Any], 
                                     content_type: str) -> Dict[str, Any]:
        """Generate statistical analysis of content."""
        return self.balance_analyzer.generate_statistical_comparison(
            content, content_type
        )
    
    def _calculate_optimization_confidence(self, rule_validation: ValidationResult,
                                         balance_analysis: Dict[str, Any]) -> float:
        """Calculate confidence score for optimizations."""
        rule_score = 1.0 if rule_validation.is_valid else 0.5
        balance_score = min(1.0, max(0.0, 1.0 - abs(balance_analysis.get("power_level", 1.0) - 1.0)))
        
        return (rule_score + balance_score) / 2.0
    
    def _generate_balance_recommendations(self, *analyses) -> List[Dict[str, Any]]:
        """Generate balance recommendations from multiple analyses."""
        recommendations = []
        
        # Combine insights from all analyses
        for analysis in analyses:
            if isinstance(analysis, dict) and "recommendations" in analysis:
                recommendations.extend(analysis["recommendations"])
        
        # Remove duplicates and prioritize
        unique_recommendations = []
        seen_descriptions = set()
        
        for rec in recommendations:
            if rec["description"] not in seen_descriptions:
                unique_recommendations.append(rec)
                seen_descriptions.add(rec["description"])
        
        return sorted(unique_recommendations, key=lambda x: x.get("priority", "low"))
    
    def _calculate_overall_balance_score(self, *analyses) -> float:
        """Calculate overall balance score from multiple analyses."""
        scores = []
        
        for analysis in analyses:
            if isinstance(analysis, dict) and "balance_score" in analysis:
                scores.append(analysis["balance_score"])
        
        return sum(scores) / len(scores) if scores else 0.5
    
    def _analyze_character_build(self, character: Character) -> Dict[str, Any]:
        """Analyze current character build strengths and weaknesses."""
        return {
            "combat_effectiveness": self.balance_analyzer.analyze_combat_effectiveness(character),
            "versatility_score": self.balance_analyzer.analyze_versatility(character),
            "thematic_consistency": self.balance_analyzer.analyze_thematic_consistency(character),
            "optimization_potential": self.balance_analyzer.analyze_optimization_potential(character)
        }
    
    def _generate_character_optimizations(self, character: Character,
                                        goals: List[str],
                                        current_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate character optimization suggestions."""
        suggestions = []
        
        for goal in goals:
            if goal == "combat":
                combat_suggestions = self._generate_combat_optimizations(character, current_analysis)
                suggestions.extend(combat_suggestions)
            elif goal == "versatility":
                versatility_suggestions = self._generate_versatility_optimizations(character, current_analysis)
                suggestions.extend(versatility_suggestions)
            elif goal == "thematic":
                thematic_suggestions = self._generate_thematic_optimizations(character, current_analysis)
                suggestions.extend(thematic_suggestions)
        
        return suggestions
    
    def _validate_optimization_suggestions(self, character: Character,
                                         suggestions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate optimization suggestions for feasibility."""
        valid_suggestions = []
        invalid_suggestions = []
        
        for suggestion in suggestions:
            if self._is_suggestion_valid(character, suggestion):
                valid_suggestions.append(suggestion)
            else:
                invalid_suggestions.append(suggestion)
        
        return {
            "valid_suggestions": valid_suggestions,
            "invalid_suggestions": invalid_suggestions,
            "validation_summary": f"{len(valid_suggestions)}/{len(suggestions)} suggestions are valid"
        }
    
    def _calculate_optimization_impact(self, character: Character,
                                     suggestions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate the impact of optimization suggestions."""
        return {
            "combat_impact": self._calculate_combat_impact(character, suggestions),
            "versatility_impact": self._calculate_versatility_impact(character, suggestions),
            "complexity_impact": self._calculate_complexity_impact(character, suggestions),
            "thematic_impact": self._calculate_thematic_impact(character, suggestions)
        }
    
    def _prioritize_optimizations(self, suggestions: List[Dict[str, Any]],
                                impact_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Prioritize optimization suggestions by impact and feasibility."""
        prioritized = []
        
        for suggestion in suggestions:
            priority_score = self._calculate_suggestion_priority(suggestion, impact_analysis)
            suggestion["priority_score"] = priority_score
            prioritized.append(suggestion)
        
        return sorted(prioritized, key=lambda x: x["priority_score"], reverse=True)
    
    def _calculate_integration_score(self, *validations) -> float:
        """Calculate overall integration score."""
        scores = []
        
        for validation in validations:
            if validation and isinstance(validation, dict):
                if "score" in validation:
                    scores.append(validation["score"])
                elif "is_valid" in validation:
                    scores.append(1.0 if validation["is_valid"] else 0.0)
        
        return sum(scores) / len(scores) if scores else 0.5
    
    # Additional helper methods would be implemented here...
    def _reduce_content_power(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Reduce power level of content."""
        # Implementation would depend on content type
        return content
    
    def _increase_content_power(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Increase power level of content."""
        # Implementation would depend on content type
        return content
    
    def _fix_rule_compliance(self, content: Dict[str, Any], 
                           recommendation: Dict[str, Any]) -> Dict[str, Any]:
        """Fix rule compliance issues."""
        # Implementation would depend on specific issue
        return content
    
    def _generate_combat_optimizations(self, character: Character,
                                     analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate combat-focused optimizations."""
        return []  # Implementation would analyze combat capabilities
    
    def _generate_versatility_optimizations(self, character: Character,
                                          analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate versatility-focused optimizations."""
        return []  # Implementation would analyze skill coverage
    
    def _generate_thematic_optimizations(self, character: Character,
                                       analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate thematic consistency optimizations."""
        return []  # Implementation would analyze thematic alignment
    
    def _is_suggestion_valid(self, character: Character, 
                           suggestion: Dict[str, Any]) -> bool:
        """Check if optimization suggestion is valid."""
        return True  # Implementation would validate against character state
    
    def _calculate_combat_impact(self, character: Character,
                               suggestions: List[Dict[str, Any]]) -> float:
        """Calculate combat effectiveness impact."""
        return 0.0  # Implementation would calculate DPR/survivability changes
    
    def _calculate_versatility_impact(self, character: Character,
                                    suggestions: List[Dict[str, Any]]) -> float:
        """Calculate versatility impact."""
        return 0.0  # Implementation would calculate skill/utility changes
    
    def _calculate_complexity_impact(self, character: Character,
                                   suggestions: List[Dict[str, Any]]) -> float:
        """Calculate complexity impact."""
        return 0.0  # Implementation would calculate decision complexity changes
    
    def _calculate_thematic_impact(self, character: Character,
                                 suggestions: List[Dict[str, Any]]) -> float:
        """Calculate thematic consistency impact."""
        return 0.0  # Implementation would calculate thematic alignment changes
    
    def _calculate_suggestion_priority(self, suggestion: Dict[str, Any],
                                     impact_analysis: Dict[str, Any]) -> float:
        """Calculate priority score for suggestion."""
        return 0.5  # Implementation would weight impact vs complexity