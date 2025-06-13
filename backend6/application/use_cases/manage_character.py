"""
Unified Character Management Use Case

Central orchestrator for all character-related operations including creation,
modification, validation, state management, and analysis. This consolidates
character workflows while maintaining the background-driven creative philosophy.
"""

from typing import Dict, Any, List, Optional, Union
import logging

from ...core.entities.character import Character
from ...core.entities.character_concept import CharacterConcept
from ...core.value_objects.validation_result import ValidationResult
from ...core.value_objects.character_state import CharacterState
from ...domain.services.character_builder import CharacterBuilderService
from ...domain.services.character_state_service import CharacterStateService
from ...domain.services.character_stats_service import CharacterStatsService
from ...domain.services.character_utility_service import CharacterUtilityService
from ...domain.services.validation_engine import CharacterValidationEngine
from ...domain.services.multiclass_engine import MulticlassEngine
from ...domain.services.character_progression_service import CharacterProgressionService
from ...domain.repositories.character_repository import CharacterRepository
from ...infrastructure.llm.character_llm_service import CharacterLLMService
from ...infrastructure.data.character_storage import CharacterStorage
from ..dtos.character_dto import (
    CharacterCreationRequest,
    CharacterCreationResponse,
    CharacterModificationRequest,
    CharacterModificationResponse,
    CharacterValidationRequest,
    CharacterValidationResponse,
    CharacterStateRequest,
    CharacterStateResponse,
    CharacterAnalysisRequest,
    CharacterAnalysisResponse,
    MulticlassRequest,
    MulticlassResponse
)

logger = logging.getLogger(__name__)

class ManageCharacterUseCase:
    """
    Unified use case for all character management operations.
    
    This consolidates character creation, modification, validation, state management,
    and analysis into a single orchestrator that maintains the background-driven
    creative philosophy while ensuring D&D rule compliance.
    """
    
    def __init__(self,
                 character_builder: CharacterBuilderService,
                 character_state_service: CharacterStateService,
                 character_stats_service: CharacterStatsService,
                 character_utility_service: CharacterUtilityService,
                 validation_engine: CharacterValidationEngine,
                 multiclass_engine: MulticlassEngine,
                 progression_service: CharacterProgressionService,
                 character_repository: CharacterRepository,
                 character_llm: CharacterLLMService,
                 character_storage: CharacterStorage):
        self.character_builder = character_builder
        self.character_state_service = character_state_service
        self.character_stats_service = character_stats_service
        self.character_utility_service = character_utility_service
        self.validation_engine = validation_engine
        self.multiclass_engine = multiclass_engine
        self.progression_service = progression_service
        self.character_repository = character_repository
        self.character_llm = character_llm
        self.character_storage = character_storage
    
    def create_character(self, request: CharacterCreationRequest) -> CharacterCreationResponse:
        """
        Create a new character from background concept.
        
        Args:
            request: Character creation request with concept and preferences
            
        Returns:
            CharacterCreationResponse with created character
        """
        try:
            # 1. Analyze character concept for creative direction
            if request.background_description:
                enhanced_concept = self.character_llm.enhance_character_concept(
                    request.background_description, request.preferences
                )
            else:
                enhanced_concept = request.character_concept
            
            # 2. Create base character from concept
            character = self.character_builder.create_character_from_concept(
                enhanced_concept, request.creation_options
            )
            
            # 3. Apply background-driven customizations
            if request.apply_custom_content:
                character = self._apply_concept_driven_customizations(
                    character, enhanced_concept
                )
            
            # 4. Handle progression if multi-level creation
            if request.target_level > 1:
                progression_plan = self.progression_service.plan_progression_from_concept(
                    character, enhanced_concept, request.target_level
                )
                character = self.progression_service.apply_progression_plan(
                    character, progression_plan
                )
            
            # 5. Validate created character
            validation_result = self.validation_engine.validate_character_comprehensive(
                character, {"creation_context": request.creation_options}
            )
            
            # 6. Save character
            saved_character = self.character_repository.save(character)
            
            return CharacterCreationResponse(
                success=True,
                character=saved_character,
                character_concept=enhanced_concept,
                validation_result=validation_result,
                creation_metadata=self._create_character_metadata(
                    request, enhanced_concept, validation_result
                )
            )
            
        except Exception as e:
            logger.error(f"Character creation failed: {e}")
            return CharacterCreationResponse(
                success=False,
                errors=[f"Character creation failed: {str(e)}"]
            )
    
    def create_multiclass_character(self, request: MulticlassRequest) -> MulticlassResponse:
        """
        Create optimized multiclass character from concept.
        
        Args:
            request: Multiclass creation request
            
        Returns:
            MulticlassResponse with multiclass character
        """
        try:
            # 1. Validate multiclass feasibility from concept
            feasibility_analysis = self.multiclass_engine.analyze_multiclass_feasibility(
                request.character_concept, request.class_combination
            )
            
            if not feasibility_analysis["feasible"]:
                return MulticlassResponse(
                    success=False,
                    errors=feasibility_analysis["blocking_issues"]
                )
            
            # 2. Calculate optimal progression based on concept themes
            progression_plan = self.multiclass_engine.plan_thematic_multiclass_progression(
                request.character_concept, request.class_combination, request.target_level
            )
            
            # 3. Build multiclass character
            multiclass_character = self._build_multiclass_character_from_concept(
                request.character_concept, progression_plan
            )
            
            # 4. Optimize feature interactions
            feature_optimization = self.multiclass_engine.optimize_multiclass_features(
                multiclass_character, request.optimization_goals
            )
            
            # 5. Calculate spellcasting progression if applicable
            spellcasting_progression = None
            if self._has_spellcasting_classes(request.class_combination):
                spellcasting_progression = self.multiclass_engine.calculate_spellcasting_progression(
                    multiclass_character
                )
            
            # 6. Validate multiclass build
            validation_result = self.validation_engine.validate_multiclass_character(
                multiclass_character
            )
            
            # 7. Save character
            saved_character = self.character_repository.save(multiclass_character)
            
            return MulticlassResponse(
                success=True,
                character=saved_character,
                progression_plan=progression_plan,
                feature_optimization=feature_optimization,
                spellcasting_progression=spellcasting_progression,
                validation_result=validation_result,
                feasibility_analysis=feasibility_analysis
            )
            
        except Exception as e:
            logger.error(f"Multiclass character creation failed: {e}")
            return MulticlassResponse(
                success=False,
                errors=[f"Multiclass creation failed: {str(e)}"]
            )
    
    def modify_character(self, request: CharacterModificationRequest) -> CharacterModificationResponse:
        """
        Modify existing character while maintaining thematic consistency.
        
        Args:
            request: Character modification request
            
        Returns:
            CharacterModificationResponse with modified character
        """
        try:
            character = self.character_repository.get_by_id(request.character_id)
            
            # Track changes for validation
            modification_log = []
            
            # Apply modifications by type
            if request.modification_type == "level_up":
                character, level_changes = self._handle_level_progression(
                    character, request.modification_data
                )
                modification_log.extend(level_changes)
                
            elif request.modification_type == "respec":
                character, respec_changes = self._handle_character_respec(
                    character, request.modification_data
                )
                modification_log.extend(respec_changes)
                
            elif request.modification_type == "equipment_change":
                character, equipment_changes = self._handle_equipment_modification(
                    character, request.modification_data
                )
                modification_log.extend(equipment_changes)
                
            elif request.modification_type == "feat_change":
                character, feat_changes = self._handle_feat_modification(
                    character, request.modification_data
                )
                modification_log.extend(feat_changes)
                
            elif request.modification_type == "custom_content_integration":
                character, content_changes = self._handle_custom_content_integration(
                    character, request.modification_data
                )
                modification_log.extend(content_changes)
            
            # Validate modifications
            validation_result = self.validation_engine.validate_character_modifications(
                character, modification_log
            )
            
            # Save modified character
            saved_character = self.character_repository.save(character)
            
            return CharacterModificationResponse(
                success=True,
                character=saved_character,
                modifications_applied=modification_log,
                validation_result=validation_result
            )
            
        except Exception as e:
            logger.error(f"Character modification failed: {e}")
            return CharacterModificationResponse(
                success=False,
                errors=[f"Modification failed: {str(e)}"]
            )
    
    def validate_character(self, request: CharacterValidationRequest) -> CharacterValidationResponse:
        """
        Comprehensive character validation.
        
        Args:
            request: Validation request
            
        Returns:
            CharacterValidationResponse with validation results
        """
        try:
            character = self.character_repository.get_by_id(request.character_id)
            
            # Perform validation based on type
            if request.validation_type == "comprehensive":
                validation_result = self.validation_engine.validate_character_comprehensive(
                    character, request.context
                )
                
            elif request.validation_type == "creation_step":
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
                
            elif request.validation_type == "thematic_consistency":
                validation_result = self.validation_engine.validate_thematic_consistency(
                    character
                )
                
            else:
                raise ValueError(f"Unknown validation type: {request.validation_type}")
            
            # Generate validation report
            validation_report = self.validation_engine.generate_validation_report(
                validation_result
            )
            
            # Generate improvement suggestions if needed
            improvement_suggestions = []
            if not validation_result.is_valid:
                improvement_suggestions = self._generate_improvement_suggestions(
                    character, validation_result
                )
            
            return CharacterValidationResponse(
                success=True,
                character_id=request.character_id,
                validation_type=request.validation_type,
                validation_result=validation_result,
                validation_report=validation_report,
                improvement_suggestions=improvement_suggestions
            )
            
        except Exception as e:
            logger.error(f"Character validation failed: {e}")
            return CharacterValidationResponse(
                success=False,
                errors=[f"Validation failed: {str(e)}"]
            )
    
    def manage_character_state(self, request: CharacterStateRequest) -> CharacterStateResponse:
        """
        Manage character state during gameplay.
        
        Args:
            request: Character state management request
            
        Returns:
            CharacterStateResponse with state changes
        """
        try:
            character = self.character_repository.get_by_id(request.character_id)
            state_changes = []
            
            # Apply state operations
            if request.operation == "take_damage":
                damage_result = self.character_state_service.apply_damage(
                    character, request.operation_data["damage"],
                    request.operation_data.get("damage_type")
                )
                state_changes.append(damage_result)
                
            elif request.operation == "heal":
                healing_result = self.character_state_service.apply_healing(
                    character, request.operation_data["healing"],
                    request.operation_data.get("healing_type", "normal")
                )
                state_changes.append(healing_result)
                
            elif request.operation == "rest":
                rest_result = self.character_state_service.take_rest(
                    character, request.operation_data["rest_type"],
                    request.operation_data.get("options", {})
                )
                state_changes.append(rest_result)
                
            elif request.operation == "use_resource":
                resource_result = self.character_state_service.use_resource(
                    character, request.operation_data["resource_type"],
                    request.operation_data.get("amount", 1)
                )
                state_changes.append(resource_result)
                
            elif request.operation == "cast_spell":
                spell_result = self.character_state_service.cast_spell(
                    character, request.operation_data["spell"],
                    request.operation_data.get("spell_level"),
                    request.operation_data.get("options", {})
                )
                state_changes.append(spell_result)
            
            # Save updated character
            saved_character = self.character_repository.save(character)
            
            return CharacterStateResponse(
                success=True,
                character=saved_character,
                state_changes=state_changes,
                current_state=character.get_current_state()
            )
            
        except Exception as e:
            logger.error(f"Character state management failed: {e}")
            return CharacterStateResponse(
                success=False,
                errors=[f"State management failed: {str(e)}"]
            )
    
    def analyze_character(self, request: CharacterAnalysisRequest) -> CharacterAnalysisResponse:
        """
        Comprehensive character analysis and statistics.
        
        Args:
            request: Character analysis request
            
        Returns:
            CharacterAnalysisResponse with analysis results
        """
        try:
            character = self.character_repository.get_by_id(request.character_id)
            
            # Perform analysis based on type
            analysis_results = {}
            
            if "comprehensive" in request.analysis_types:
                comprehensive_stats = self.character_stats_service.calculate_comprehensive_stats(
                    character
                )
                analysis_results["comprehensive"] = comprehensive_stats
                
            if "combat" in request.analysis_types:
                combat_analysis = self.character_stats_service.calculate_combat_statistics(
                    character
                )
                analysis_results["combat"] = combat_analysis
                
            if "skills" in request.analysis_types:
                skill_analysis = self.character_stats_service.calculate_skill_analysis(
                    character
                )
                analysis_results["skills"] = skill_analysis
                
            if "optimization" in request.analysis_types:
                optimization_analysis = self.character_stats_service.analyze_optimization_potential(
                    character
                )
                analysis_results["optimization"] = optimization_analysis
                
            if "thematic_consistency" in request.analysis_types:
                thematic_analysis = self.character_stats_service.analyze_thematic_consistency(
                    character
                )
                analysis_results["thematic_consistency"] = thematic_analysis
            
            # Generate summary
            analysis_summary = self._generate_analysis_summary(
                character, analysis_results
            )
            
            return CharacterAnalysisResponse(
                success=True,
                character_id=request.character_id,
                character_name=character.name,
                analysis_results=analysis_results,
                analysis_summary=analysis_summary
            )
            
        except Exception as e:
            logger.error(f"Character analysis failed: {e}")
            return CharacterAnalysisResponse(
                success=False,
                errors=[f"Analysis failed: {str(e)}"]
            )
    
    def manage_character_utilities(self, character_id: str, 
                                 operation: str, 
                                 operation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle character utility operations (save, clone, export, etc.).
        
        Args:
            character_id: Character to operate on
            operation: Utility operation to perform
            operation_data: Operation-specific data
            
        Returns:
            Result of utility operation
        """
        try:
            character = self.character_repository.get_by_id(character_id)
            
            if operation == "save_to_file":
                filepath = self.character_storage.save_character(
                    character, operation_data.get("filename")
                )
                return {
                    "success": True,
                    "message": f"Character saved to {filepath}",
                    "filepath": filepath
                }
                
            elif operation == "clone":
                cloned_character = self.character_utility_service.clone_character(
                    character, operation_data.get("new_name")
                )
                saved_clone = self.character_repository.save(cloned_character)
                return {
                    "success": True,
                    "message": "Character cloned successfully",
                    "cloned_character_id": saved_clone.id
                }
                
            elif operation == "export":
                exported_data = self.character_utility_service.export_character(
                    character, operation_data.get("format", "json")
                )
                return {
                    "success": True,
                    "message": "Character exported successfully",
                    "exported_data": exported_data
                }
                
            elif operation == "compare":
                other_character_id = operation_data["other_character_id"]
                other_character = self.character_repository.get_by_id(other_character_id)
                comparison = self.character_utility_service.compare_characters(
                    character, other_character
                )
                return {
                    "success": True,
                    "comparison": comparison
                }
                
            else:
                raise ValueError(f"Unknown utility operation: {operation}")
                
        except Exception as e:
            logger.error(f"Character utility operation failed: {e}")
            return {
                "success": False,
                "errors": [f"Utility operation failed: {str(e)}"]
            }
    
    # === Private Helper Methods ===
    
    def _apply_concept_driven_customizations(self, character: Character,
                                           concept: CharacterConcept) -> Character:
        """Apply customizations based on character concept."""
        # Use LLM to identify concept-driven customization opportunities
        customization_suggestions = self.character_llm.suggest_concept_customizations(
            character, concept
        )
        
        # Apply approved customizations
        for suggestion in customization_suggestions:
            if suggestion["auto_apply"]:
                character = self.character_builder.apply_customization(
                    character, suggestion
                )
        
        return character
    
    def _build_multiclass_character_from_concept(self, concept: CharacterConcept,
                                               progression_plan: Dict[str, Any]) -> Character:
        """Build multiclass character following concept-driven progression."""
        # Create base character from concept
        character = self.character_builder.create_character_from_concept(concept)
        
        # Apply multiclass progression
        for level_data in progression_plan["progression"]:
            character = self.character_builder.apply_multiclass_level(
                character, level_data
            )
        
        return character
    
    def _has_spellcasting_classes(self, class_combination: List[str]) -> bool:
        """Check if any classes have spellcasting."""
        spellcasting_classes = {
            "Artificer", "Bard", "Cleric", "Druid", "Paladin", 
            "Ranger", "Sorcerer", "Warlock", "Wizard"
        }
        return any(cls in spellcasting_classes for cls in class_combination)
    
    def _handle_level_progression(self, character: Character,
                                modification_data: Dict[str, Any]) -> tuple:
        """Handle character level progression."""
        progression_choices = modification_data.get("choices", {})
        new_level = modification_data["target_level"]
        
        # Apply level progression
        level_results = self.progression_service.apply_level_progression(
            character, new_level, progression_choices
        )
        
        modification_log = [{
            "type": "level_up",
            "from_level": character.level,
            "to_level": new_level,
            "changes": level_results
        }]
        
        return character, modification_log
    
    def _handle_character_respec(self, character: Character,
                               modification_data: Dict[str, Any]) -> tuple:
        """Handle character respecialization."""
        respec_options = modification_data.get("respec_options", {})
        
        # Apply respec changes
        respec_results = self.character_utility_service.respec_character(
            character, respec_options
        )
        
        modification_log = [{
            "type": "respec",
            "changes": respec_results
        }]
        
        return character, modification_log
    
    def _handle_equipment_modification(self, character: Character,
                                     modification_data: Dict[str, Any]) -> tuple:
        """Handle equipment modifications."""
        equipment_changes = modification_data.get("equipment_changes", [])
        
        # Apply equipment changes
        equipment_results = []
        for change in equipment_changes:
            result = self.character_builder.modify_equipment(character, change)
            equipment_results.append(result)
        
        modification_log = [{
            "type": "equipment_change",
            "changes": equipment_results
        }]
        
        return character, modification_log
    
    def _handle_feat_modification(self, character: Character,
                                modification_data: Dict[str, Any]) -> tuple:
        """Handle feat modifications."""
        feat_changes = modification_data.get("feat_changes", [])
        
        # Apply feat changes
        feat_results = []
        for change in feat_changes:
            result = self.character_builder.modify_feat(character, change)
            feat_results.append(result)
        
        modification_log = [{
            "type": "feat_change",
            "changes": feat_results
        }]
        
        return character, modification_log
    
    def _handle_custom_content_integration(self, character: Character,
                                         modification_data: Dict[str, Any]) -> tuple:
        """Handle custom content integration."""
        custom_content = modification_data.get("custom_content", [])
        
        # Apply custom content
        content_results = []
        for content in custom_content:
            result = self.character_builder.integrate_custom_content(character, content)
            content_results.append(result)
        
        modification_log = [{
            "type": "custom_content_integration",
            "changes": content_results
        }]
        
        return character, modification_log
    
    def _generate_improvement_suggestions(self, character: Character,
                                        validation_result: ValidationResult) -> List[Dict[str, Any]]:
        """Generate character improvement suggestions."""
        suggestions = []
        
        for issue in validation_result.issues:
            if issue.severity == "error":
                suggestions.append({
                    "type": "error_fix",
                    "priority": "high",
                    "description": issue.message,
                    "suggested_action": issue.suggested_fix
                })
            elif issue.severity == "warning":
                suggestions.append({
                    "type": "optimization",
                    "priority": "medium", 
                    "description": issue.message,
                    "suggested_action": issue.suggested_fix
                })
        
        return suggestions
    
    def _create_character_metadata(self, request: CharacterCreationRequest,
                                 concept: CharacterConcept,
                                 validation: ValidationResult) -> Dict[str, Any]:
        """Create metadata for character creation."""
        return {
            "creation_timestamp": "2024-01-01T00:00:00Z",  # Would use actual timestamp
            "creation_method": "concept_driven" if request.background_description else "standard",
            "source_concept": concept.background_description if concept else None,
            "validation_passed": validation.is_valid,
            "custom_content_applied": request.apply_custom_content,
            "target_level": request.target_level
        }
    
    def _generate_analysis_summary(self, character: Character,
                                 analysis_results: Dict[str, Any]) -> str:
        """Generate human-readable analysis summary."""
        summaries = []
        
        if "comprehensive" in analysis_results:
            stats = analysis_results["comprehensive"]
            summaries.append(f"Level {character.level} {character.species} {character.character_class}")
            summaries.append(f"AC: {stats.armor_class}, HP: {stats.hit_points}")
            
        if "combat" in analysis_results:
            combat = analysis_results["combat"]
            summaries.append(f"Combat Rating: {combat.get('combat_rating', 'N/A')}")
            
        if "skills" in analysis_results:
            skills = analysis_results["skills"]
            top_skills = sorted(skills.get("skill_modifiers", {}).items(), 
                              key=lambda x: x[1], reverse=True)[:3]
            summaries.append(f"Top Skills: {', '.join([skill for skill, _ in top_skills])}")
        
        return " | ".join(summaries)