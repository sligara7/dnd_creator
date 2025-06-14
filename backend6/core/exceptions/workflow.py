"""
Application Workflow and Use Case Exceptions for the D&D Creative Content Framework.

This module defines exceptions related to application workflow failures, use case
execution errors, business process violations, and application service coordination
issues. These exceptions represent business rule violations and failure states in
the application workflow and use case orchestration domain.

Following Clean Architecture principles, these exceptions are:
- Infrastructure-independent (don't depend on specific framework implementations)
- Focused on D&D application workflow and use case business rules
- Designed for proper error handling and recovery strategies
- Aligned with the use case execution and business process workflow
"""

from typing import Dict, List, Optional, Any, Union, Type
from datetime import datetime, timedelta
from enum import Enum
from ..enums.workflow_types import WorkflowState, WorkflowTransition, UseCaseStatus, ProcessPriority
from ..enums.content_types import ContentType
from ..enums.validation_types import ValidationSeverity
from .base import DnDFrameworkError, ValidationError, BusinessRuleError


# ============ BASE WORKFLOW EXCEPTIONS ============

class WorkflowError(DnDFrameworkError):
    """Base exception for all application workflow and use case errors."""
    
    def __init__(
        self,
        message: str,
        workflow_name: Optional[str] = None,
        workflow_state: Optional[WorkflowState] = None,
        workflow_context: Optional[Dict[str, Any]] = None,
        execution_stage: Optional[str] = None,
        workflow_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.workflow_name = workflow_name
        self.workflow_state = workflow_state
        self.workflow_context = workflow_context or {}
        self.execution_stage = execution_stage
        self.workflow_id = workflow_id
    
    def _generate_error_code(self) -> str:
        """Generate workflow-specific error code."""
        base_code = "WFL"
        workflow_code = self.workflow_name[:3].upper() if self.workflow_name else "GEN"
        timestamp_code = str(int(self.timestamp.timestamp()))[-6:]
        return f"{base_code}_{workflow_code}_{timestamp_code}"
    
    def get_category(self) -> str:
        """Workflow error category."""
        return "workflow"
    
    def is_retryable(self) -> bool:
        """Most workflow errors are retryable."""
        return True
    
    def should_fail_fast(self) -> bool:
        """Workflow errors don't fail fast by default."""
        return False
    
    def __str__(self) -> str:
        parts = [super().__str__()]
        
        if self.workflow_name:
            parts.append(f"Workflow: {self.workflow_name}")
        
        if self.workflow_state:
            parts.append(f"State: {self.workflow_state.value}")
        
        if self.execution_stage:
            parts.append(f"Stage: {self.execution_stage}")
        
        if self.workflow_id:
            parts.append(f"ID: {self.workflow_id}")
        
        return " | ".join(parts)


class UseCaseError(WorkflowError):
    """Base exception for use case execution failures."""
    
    def __init__(
        self,
        message: str,
        use_case_name: Optional[str] = None,
        use_case_status: Optional[UseCaseStatus] = None,
        input_parameters: Optional[Dict[str, Any]] = None,
        execution_context: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(
            message,
            workflow_name=use_case_name,
            workflow_context=execution_context,
            **kwargs
        )
        self.use_case_name = use_case_name
        self.use_case_status = use_case_status
        self.input_parameters = input_parameters or {}
        self.execution_context = execution_context or {}
    
    def get_category(self) -> str:
        return "use_case"
    
    def __str__(self) -> str:
        parts = [super().__str__()]
        
        if self.use_case_status:
            parts.append(f"Status: {self.use_case_status.value}")
        
        return " | ".join(parts)


# ============ USE CASE EXECUTION EXCEPTIONS ============

class UseCaseExecutionError(UseCaseError):
    """Exception for use case execution failures."""
    
    def __init__(
        self,
        use_case_name: str,
        execution_issue: str,
        failed_step: Optional[str] = None,
        step_number: Optional[int] = None,
        total_steps: Optional[int] = None,
        partial_results: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        message = f"Use case '{use_case_name}' execution failed: {execution_issue}"
        if failed_step:
            message += f" at step '{failed_step}'"
            if step_number and total_steps:
                message += f" ({step_number}/{total_steps})"
        
        super().__init__(
            message,
            use_case_name=use_case_name,
            use_case_status=UseCaseStatus.FAILED,
            execution_stage=failed_step,
            **kwargs
        )
        self.execution_issue = execution_issue
        self.failed_step = failed_step
        self.step_number = step_number
        self.total_steps = total_steps
        self.partial_results = partial_results or {}
    
    def get_category(self) -> str:
        return "use_case_execution"


class UseCaseValidationError(UseCaseError, ValidationError):
    """Exception for use case input validation failures."""
    
    def __init__(
        self,
        use_case_name: str,
        validation_issue: str,
        invalid_parameters: Optional[List[str]] = None,
        parameter_constraints: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        message = f"Use case '{use_case_name}' validation failed: {validation_issue}"
        
        # Initialize ValidationError
        ValidationError.__init__(
            self,
            message,
            field_name="input_parameters",
            field_value=kwargs.get('input_parameters'),
            **kwargs
        )
        
        # Initialize UseCaseError attributes manually to avoid multiple inheritance issues
        self.use_case_name = use_case_name
        self.use_case_status = UseCaseStatus.VALIDATION_FAILED
        self.input_parameters = kwargs.get('input_parameters', {})
        self.execution_context = kwargs.get('execution_context', {})
        
        self.validation_issue = validation_issue
        self.invalid_parameters = invalid_parameters or []
        self.parameter_constraints = parameter_constraints or {}
    
    def get_category(self) -> str:
        return "use_case_validation"
    
    def should_fail_fast(self) -> bool:
        """Validation errors should fail fast."""
        return True


class UseCasePreconditionError(UseCaseError):
    """Exception for use case precondition failures."""
    
    def __init__(
        self,
        use_case_name: str,
        precondition_issue: str,
        failed_preconditions: List[str],
        system_state: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        message = f"Use case '{use_case_name}' precondition failed: {precondition_issue}"
        super().__init__(
            message,
            use_case_name=use_case_name,
            use_case_status=UseCaseStatus.PRECONDITION_FAILED,
            **kwargs
        )
        self.precondition_issue = precondition_issue
        self.failed_preconditions = failed_preconditions
        self.system_state = system_state or {}
    
    def get_category(self) -> str:
        return "use_case_precondition"
    
    def should_fail_fast(self) -> bool:
        """Precondition failures should fail fast."""
        return True


class UseCasePostconditionError(UseCaseError):
    """Exception for use case postcondition failures."""
    
    def __init__(
        self,
        use_case_name: str,
        postcondition_issue: str,
        failed_postconditions: List[str],
        execution_results: Optional[Dict[str, Any]] = None,
        expected_state: Optional[Dict[str, Any]] = None,
        actual_state: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        message = f"Use case '{use_case_name}' postcondition failed: {postcondition_issue}"
        super().__init__(
            message,
            use_case_name=use_case_name,
            use_case_status=UseCaseStatus.POSTCONDITION_FAILED,
            **kwargs
        )
        self.postcondition_issue = postcondition_issue
        self.failed_postconditions = failed_postconditions
        self.execution_results = execution_results or {}
        self.expected_state = expected_state or {}
        self.actual_state = actual_state or {}
    
    def get_category(self) -> str:
        return "use_case_postcondition"


class UseCaseTimeoutError(UseCaseError):
    """Exception for use case execution timeouts."""
    
    def __init__(
        self,
        use_case_name: str,
        timeout_duration: float,
        current_step: Optional[str] = None,
        completed_steps: Optional[List[str]] = None,
        **kwargs
    ):
        message = f"Use case '{use_case_name}' timed out after {timeout_duration} seconds"
        if current_step:
            message += f" during step '{current_step}'"
        
        super().__init__(
            message,
            use_case_name=use_case_name,
            use_case_status=UseCaseStatus.TIMED_OUT,
            execution_stage=current_step,
            **kwargs
        )
        self.timeout_duration = timeout_duration
        self.current_step = current_step
        self.completed_steps = completed_steps or []
    
    def get_category(self) -> str:
        return "use_case_timeout"
    
    def is_retryable(self) -> bool:
        """Timeout errors are generally retryable."""
        return True


class UseCaseDependencyError(UseCaseError):
    """Exception for use case dependency failures."""
    
    def __init__(
        self,
        use_case_name: str,
        dependency_issue: str,
        failed_dependencies: List[str],
        dependency_context: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        message = f"Use case '{use_case_name}' dependency failed: {dependency_issue}"
        super().__init__(
            message,
            use_case_name=use_case_name,
            use_case_status=UseCaseStatus.DEPENDENCY_FAILED,
            **kwargs
        )
        self.dependency_issue = dependency_issue
        self.failed_dependencies = failed_dependencies
        self.dependency_context = dependency_context or {}
    
    def get_category(self) -> str:
        return "use_case_dependency"


# ============ CHARACTER WORKFLOW EXCEPTIONS ============

class CharacterWorkflowError(WorkflowError):
    """Exception for character-related workflow failures."""
    
    def __init__(
        self,
        character_id: str,
        workflow_issue: str,
        character_name: Optional[str] = None,
        owner_id: Optional[str] = None,
        workflow_stage: Optional[str] = None,
        **kwargs
    ):
        message = f"Character workflow failed for {character_name or character_id}: {workflow_issue}"
        super().__init__(
            message,
            workflow_name="character_workflow",
            execution_stage=workflow_stage,
            **kwargs
        )
        self.character_id = character_id
        self.character_name = character_name
        self.owner_id = owner_id
        self.workflow_issue = workflow_issue
    
    def get_category(self) -> str:
        return "character_workflow"


class CharacterCreationWorkflowError(CharacterWorkflowError):
    """Exception for character creation workflow failures."""
    
    def __init__(
        self,
        creation_issue: str,
        character_data: Optional[Dict[str, Any]] = None,
        creation_step: Optional[str] = None,
        validation_errors: Optional[List[str]] = None,
        **kwargs
    ):
        character_name = character_data.get('name', 'Unknown') if character_data else 'Unknown'
        super().__init__(
            character_id="pending",
            character_name=character_name,
            workflow_issue=f"Character creation failed: {creation_issue}",
            workflow_stage=creation_step,
            **kwargs
        )
        self.creation_issue = creation_issue
        self.character_data = character_data or {}
        self.creation_step = creation_step
        self.validation_errors = validation_errors or []
    
    def get_category(self) -> str:
        return "character_creation_workflow"


class CharacterUpdateWorkflowError(CharacterWorkflowError):
    """Exception for character update workflow failures."""
    
    def __init__(
        self,
        character_id: str,
        update_issue: str,
        update_data: Optional[Dict[str, Any]] = None,
        conflicting_changes: Optional[List[str]] = None,
        **kwargs
    ):
        super().__init__(
            character_id=character_id,
            workflow_issue=f"Character update failed: {update_issue}",
            workflow_stage="update",
            **kwargs
        )
        self.update_issue = update_issue
        self.update_data = update_data or {}
        self.conflicting_changes = conflicting_changes or []
    
    def get_category(self) -> str:
        return "character_update_workflow"


class CharacterLevelUpWorkflowError(CharacterWorkflowError):
    """Exception for character level-up workflow failures."""
    
    def __init__(
        self,
        character_id: str,
        level_up_issue: str,
        current_level: Optional[int] = None,
        target_level: Optional[int] = None,
        level_up_choices: Optional[Dict[str, Any]] = None,
        missing_choices: Optional[List[str]] = None,
        **kwargs
    ):
        message = f"Level-up failed: {level_up_issue}"
        if current_level and target_level:
            message += f" (from level {current_level} to {target_level})"
        
        super().__init__(
            character_id=character_id,
            workflow_issue=message,
            workflow_stage="level_up",
            **kwargs
        )
        self.level_up_issue = level_up_issue
        self.current_level = current_level
        self.target_level = target_level
        self.level_up_choices = level_up_choices or {}
        self.missing_choices = missing_choices or []
    
    def get_category(self) -> str:
        return "character_level_up_workflow"


class CharacterValidationWorkflowError(CharacterWorkflowError):
    """Exception for character validation workflow failures."""
    
    def __init__(
        self,
        character_id: str,
        validation_issue: str,
        validation_errors: List[str],
        character_state: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(
            character_id=character_id,
            workflow_issue=f"Character validation failed: {validation_issue}",
            workflow_stage="validation",
            **kwargs
        )
        self.validation_issue = validation_issue
        self.validation_errors = validation_errors
        self.character_state = character_state or {}
    
    def get_category(self) -> str:
        return "character_validation_workflow"
    
    def should_fail_fast(self) -> bool:
        """Validation workflow errors should fail fast."""
        return True


# ============ CAMPAIGN WORKFLOW EXCEPTIONS ============

class CampaignWorkflowError(WorkflowError):
    """Exception for campaign-related workflow failures."""
    
    def __init__(
        self,
        campaign_id: str,
        workflow_issue: str,
        campaign_name: Optional[str] = None,
        dm_id: Optional[str] = None,
        workflow_stage: Optional[str] = None,
        **kwargs
    ):
        message = f"Campaign workflow failed for {campaign_name or campaign_id}: {workflow_issue}"
        super().__init__(
            message,
            workflow_name="campaign_workflow",
            execution_stage=workflow_stage,
            **kwargs
        )
        self.campaign_id = campaign_id
        self.campaign_name = campaign_name
        self.dm_id = dm_id
        self.workflow_issue = workflow_issue
    
    def get_category(self) -> str:
        return "campaign_workflow"


class CampaignCreationWorkflowError(CampaignWorkflowError):
    """Exception for campaign creation workflow failures."""
    
    def __init__(
        self,
        creation_issue: str,
        campaign_data: Optional[Dict[str, Any]] = None,
        creation_step: Optional[str] = None,
        **kwargs
    ):
        campaign_name = campaign_data.get('name', 'Unknown') if campaign_data else 'Unknown'
        super().__init__(
            campaign_id="pending",
            campaign_name=campaign_name,
            workflow_issue=f"Campaign creation failed: {creation_issue}",
            workflow_stage=creation_step,
            **kwargs
        )
        self.creation_issue = creation_issue
        self.campaign_data = campaign_data or {}
        self.creation_step = creation_step
    
    def get_category(self) -> str:
        return "campaign_creation_workflow"


class PlayerInvitationWorkflowError(CampaignWorkflowError):
    """Exception for player invitation workflow failures."""
    
    def __init__(
        self,
        campaign_id: str,
        invitation_issue: str,
        invited_player: Optional[str] = None,
        invitation_method: Optional[str] = None,
        invitation_status: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            campaign_id=campaign_id,
            workflow_issue=f"Player invitation failed: {invitation_issue}",
            workflow_stage="player_invitation",
            **kwargs
        )
        self.invitation_issue = invitation_issue
        self.invited_player = invited_player
        self.invitation_method = invitation_method
        self.invitation_status = invitation_status
    
    def get_category(self) -> str:
        return "player_invitation_workflow"


class CampaignSessionWorkflowError(CampaignWorkflowError):
    """Exception for campaign session workflow failures."""
    
    def __init__(
        self,
        campaign_id: str,
        session_issue: str,
        session_id: Optional[str] = None,
        session_phase: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            campaign_id=campaign_id,
            workflow_issue=f"Session workflow failed: {session_issue}",
            workflow_stage=session_phase,
            **kwargs
        )
        self.session_issue = session_issue
        self.session_id = session_id
        self.session_phase = session_phase
    
    def get_category(self) -> str:
        return "campaign_session_workflow"


# ============ BUSINESS PROCESS EXCEPTIONS ============

class BusinessProcessError(WorkflowError, BusinessRuleError):
    """Exception for business process violations."""
    
    def __init__(
        self,
        process_name: str,
        process_violation: str,
        business_rules: Optional[List[str]] = None,
        process_context: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        message = f"Business process '{process_name}' violated: {process_violation}"
        
        # Initialize BusinessRuleError
        BusinessRuleError.__init__(
            self,
            rule_type="business_process",
            rule_description=process_violation,
            violation_context=process_context,
            **kwargs
        )
        
        # Initialize WorkflowError attributes manually
        self.workflow_name = process_name
        self.workflow_context = process_context or {}
        
        self.process_name = process_name
        self.process_violation = process_violation
        self.business_rules = business_rules or []
    
    def get_category(self) -> str:
        return "business_process"
    
    def should_fail_fast(self) -> bool:
        """Business process violations should fail fast."""
        return True


class CharacterBusinessRuleError(BusinessProcessError):
    """Exception for character-specific business rule violations."""
    
    def __init__(
        self,
        character_id: str,
        rule_violation: str,
        violated_rules: List[str],
        character_state: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(
            process_name="character_business_rules",
            process_violation=f"Character {character_id} rule violation: {rule_violation}",
            business_rules=violated_rules,
            process_context=character_state,
            **kwargs
        )
        self.character_id = character_id
        self.rule_violation = rule_violation
        self.violated_rules = violated_rules
        self.character_state = character_state or {}
    
    def get_category(self) -> str:
        return "character_business_rule"


class CampaignBusinessRuleError(BusinessProcessError):
    """Exception for campaign-specific business rule violations."""
    
    def __init__(
        self,
        campaign_id: str,
        rule_violation: str,
        violated_rules: List[str],
        campaign_state: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(
            process_name="campaign_business_rules",
            process_violation=f"Campaign {campaign_id} rule violation: {rule_violation}",
            business_rules=violated_rules,
            process_context=campaign_state,
            **kwargs
        )
        self.campaign_id = campaign_id
        self.rule_violation = rule_violation
        self.violated_rules = violated_rules
        self.campaign_state = campaign_state or {}
    
    def get_category(self) -> str:
        return "campaign_business_rule"


class ContentCreationBusinessRuleError(BusinessProcessError):
    """Exception for content creation business rule violations."""
    
    def __init__(
        self,
        content_type: ContentType,
        rule_violation: str,
        violated_rules: List[str],
        content_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(
            process_name="content_creation_business_rules",
            process_violation=f"Content creation rule violation for {content_type.value}: {rule_violation}",
            business_rules=violated_rules,
            process_context=content_data,
            **kwargs
        )
        self.content_type = content_type
        self.rule_violation = rule_violation
        self.violated_rules = violated_rules
        self.content_data = content_data or {}
    
    def get_category(self) -> str:
        return "content_creation_business_rule"


# ============ APPLICATION SERVICE EXCEPTIONS ============

class ApplicationServiceError(WorkflowError):
    """Exception for application service coordination failures."""
    
    def __init__(
        self,
        service_name: str,
        service_issue: str,
        service_method: Optional[str] = None,
        service_context: Optional[Dict[str, Any]] = None,
        dependent_services: Optional[List[str]] = None,
        **kwargs
    ):
        message = f"Application service '{service_name}' failed: {service_issue}"
        if service_method:
            message += f" in method '{service_method}'"
        
        super().__init__(
            message,
            workflow_name=f"{service_name}_service",
            workflow_context=service_context,
            **kwargs
        )
        self.service_name = service_name
        self.service_issue = service_issue
        self.service_method = service_method
        self.service_context = service_context or {}
        self.dependent_services = dependent_services or []
    
    def get_category(self) -> str:
        return "application_service"


class ServiceCoordinationError(ApplicationServiceError):
    """Exception for service coordination failures."""
    
    def __init__(
        self,
        coordination_issue: str,
        involved_services: List[str],
        coordination_context: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        message = f"Service coordination failed: {coordination_issue}"
        super().__init__(
            service_name="coordination_service",
            service_issue=coordination_issue,
            service_context=coordination_context,
            dependent_services=involved_services,
            **kwargs
        )
        self.coordination_issue = coordination_issue
        self.involved_services = involved_services
        self.coordination_context = coordination_context or {}
    
    def get_category(self) -> str:
        return "service_coordination"


class ServiceDependencyError(ApplicationServiceError):
    """Exception for service dependency failures."""
    
    def __init__(
        self,
        service_name: str,
        dependency_issue: str,
        failed_dependency: str,
        dependency_error: Optional[Exception] = None,
        **kwargs
    ):
        service_issue = f"Dependency '{failed_dependency}' failed: {dependency_issue}"
        super().__init__(
            service_name=service_name,
            service_issue=service_issue,
            dependent_services=[failed_dependency],
            **kwargs
        )
        self.dependency_issue = dependency_issue
        self.failed_dependency = failed_dependency
        self.dependency_error = dependency_error
    
    def get_category(self) -> str:
        return "service_dependency"


class ServiceConfigurationError(ApplicationServiceError):
    """Exception for service configuration failures."""
    
    def __init__(
        self,
        service_name: str,
        config_issue: str,
        config_key: Optional[str] = None,
        config_value: Optional[Any] = None,
        **kwargs
    ):
        service_issue = f"Configuration error: {config_issue}"
        if config_key:
            service_issue += f" (key: {config_key})"
        
        super().__init__(
            service_name=service_name,
            service_issue=service_issue,
            **kwargs
        )
        self.config_issue = config_issue
        self.config_key = config_key
        self.config_value = config_value
    
    def get_category(self) -> str:
        return "service_configuration"
    
    def should_fail_fast(self) -> bool:
        """Configuration errors should fail fast."""
        return True


# ============ WORKFLOW STATE MANAGEMENT EXCEPTIONS ============

class WorkflowStateError(WorkflowError):
    """Exception for workflow state management failures."""
    
    def __init__(
        self,
        workflow_name: str,
        state_issue: str,
        current_state: Optional[WorkflowState] = None,
        target_state: Optional[WorkflowState] = None,
        invalid_transition: Optional[WorkflowTransition] = None,
        **kwargs
    ):
        message = f"Workflow '{workflow_name}' state error: {state_issue}"
        if current_state and target_state:
            message += f" (from {current_state.value} to {target_state.value})"
        
        super().__init__(
            message,
            workflow_name=workflow_name,
            workflow_state=current_state,
            **kwargs
        )
        self.state_issue = state_issue
        self.current_state = current_state
        self.target_state = target_state
        self.invalid_transition = invalid_transition
    
    def get_category(self) -> str:
        return "workflow_state"


class InvalidWorkflowTransitionError(WorkflowStateError):
    """Exception for invalid workflow transitions."""
    
    def __init__(
        self,
        workflow_name: str,
        current_state: WorkflowState,
        attempted_transition: WorkflowTransition,
        valid_transitions: Optional[List[WorkflowTransition]] = None,
        **kwargs
    ):
        state_issue = f"Invalid transition '{attempted_transition.value}' from state '{current_state.value}'"
        if valid_transitions:
            valid_names = [t.value for t in valid_transitions]
            state_issue += f" (valid: {', '.join(valid_names)})"
        
        super().__init__(
            workflow_name=workflow_name,
            state_issue=state_issue,
            current_state=current_state,
            invalid_transition=attempted_transition,
            **kwargs
        )
        self.attempted_transition = attempted_transition
        self.valid_transitions = valid_transitions or []
    
    def get_category(self) -> str:
        return "invalid_workflow_transition"
    
    def should_fail_fast(self) -> bool:
        """Invalid transitions should fail fast."""
        return True


class WorkflowStateCorruptionError(WorkflowStateError):
    """Exception for workflow state corruption."""
    
    def __init__(
        self,
        workflow_name: str,
        corruption_issue: str,
        corrupted_fields: List[str],
        expected_state: Optional[Dict[str, Any]] = None,
        actual_state: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        state_issue = f"State corruption detected: {corruption_issue}"
        super().__init__(
            workflow_name=workflow_name,
            state_issue=state_issue,
            **kwargs
        )
        self.corruption_issue = corruption_issue
        self.corrupted_fields = corrupted_fields
        self.expected_state = expected_state or {}
        self.actual_state = actual_state or {}
    
    def get_category(self) -> str:
        return "workflow_state_corruption"
    
    def should_fail_fast(self) -> bool:
        """State corruption should fail fast."""
        return True


# ============ WORKFLOW ORCHESTRATION EXCEPTIONS ============

class WorkflowOrchestrationError(WorkflowError):
    """Exception for workflow orchestration failures."""
    
    def __init__(
        self,
        orchestration_issue: str,
        involved_workflows: List[str],
        orchestration_context: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        message = f"Workflow orchestration failed: {orchestration_issue}"
        super().__init__(
            message,
            workflow_name="orchestration",
            workflow_context=orchestration_context,
            **kwargs
        )
        self.orchestration_issue = orchestration_issue
        self.involved_workflows = involved_workflows
        self.orchestration_context = orchestration_context or {}
    
    def get_category(self) -> str:
        return "workflow_orchestration"


class ParallelWorkflowError(WorkflowOrchestrationError):
    """Exception for parallel workflow execution failures."""
    
    def __init__(
        self,
        parallel_issue: str,
        successful_workflows: List[str],
        failed_workflows: List[str],
        workflow_results: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        all_workflows = successful_workflows + failed_workflows
        orchestration_issue = f"Parallel execution failed: {parallel_issue} ({len(failed_workflows)}/{len(all_workflows)} workflows failed)"
        
        super().__init__(
            orchestration_issue=orchestration_issue,
            involved_workflows=all_workflows,
            orchestration_context=workflow_results,
            **kwargs
        )
        self.parallel_issue = parallel_issue
        self.successful_workflows = successful_workflows
        self.failed_workflows = failed_workflows
        self.workflow_results = workflow_results or {}
    
    def get_category(self) -> str:
        return "parallel_workflow"
    
    def is_retryable(self) -> bool:
        """Parallel workflows might be retryable if some succeeded."""
        return len(self.successful_workflows) > 0


class WorkflowCompensationError(WorkflowOrchestrationError):
    """Exception for workflow compensation failures."""
    
    def __init__(
        self,
        compensation_issue: str,
        original_workflow: str,
        compensation_actions: List[str],
        failed_compensations: Optional[List[str]] = None,
        **kwargs
    ):
        orchestration_issue = f"Compensation failed for '{original_workflow}': {compensation_issue}"
        super().__init__(
            orchestration_issue=orchestration_issue,
            involved_workflows=[original_workflow],
            **kwargs
        )
        self.compensation_issue = compensation_issue
        self.original_workflow = original_workflow
        self.compensation_actions = compensation_actions
        self.failed_compensations = failed_compensations or []
    
    def get_category(self) -> str:
        return "workflow_compensation"
    
    def should_fail_fast(self) -> bool:
        """Compensation failures should fail fast."""
        return True


# ============ UTILITY FUNCTIONS FOR WORKFLOW EXCEPTION HANDLING ============

def categorize_workflow_error(error: Exception) -> str:
    """
    Categorize a workflow error for handling and routing.
    
    Args:
        error: The exception to categorize
        
    Returns:
        Error category string
    """
    if isinstance(error, UseCaseExecutionError):
        return "use_case_execution"
    elif isinstance(error, UseCaseValidationError):
        return "use_case_validation"
    elif isinstance(error, CharacterWorkflowError):
        return "character_workflow"
    elif isinstance(error, CampaignWorkflowError):
        return "campaign_workflow"
    elif isinstance(error, BusinessProcessError):
        return "business_process"
    elif isinstance(error, ApplicationServiceError):
        return "application_service"
    elif isinstance(error, WorkflowStateError):
        return "workflow_state"
    elif isinstance(error, WorkflowOrchestrationError):
        return "workflow_orchestration"
    elif isinstance(error, UseCaseError):
        return "use_case"
    elif isinstance(error, WorkflowError):
        return "workflow"
    else:
        return "unknown"


def is_retryable_workflow_error(error: WorkflowError) -> bool:
    """
    Determine if a workflow error is retryable.
    
    Args:
        error: The workflow error to check
        
    Returns:
        True if the error might succeed on retry
    """
    # Timeout errors are retryable
    if isinstance(error, UseCaseTimeoutError):
        return True
    
    # Dependency errors might be retryable
    if isinstance(error, (UseCaseDependencyError, ServiceDependencyError)):
        return True
    
    # Parallel workflows with partial success are retryable
    if isinstance(error, ParallelWorkflowError):
        return len(error.successful_workflows) > 0
    
    # Validation errors are not retryable
    if isinstance(error, (UseCaseValidationError, CharacterValidationWorkflowError)):
        return False
    
    # Precondition failures are not retryable
    if isinstance(error, UseCasePreconditionError):
        return False
    
    # Business rule violations are not retryable
    if isinstance(error, BusinessProcessError):
        return False
    
    # Configuration errors are not retryable
    if isinstance(error, ServiceConfigurationError):
        return False
    
    # State corruption is not retryable
    if isinstance(error, WorkflowStateCorruptionError):
        return False
    
    # Invalid transitions are not retryable
    if isinstance(error, InvalidWorkflowTransitionError):
        return False
    
    # Compensation failures are not retryable
    if isinstance(error, WorkflowCompensationError):
        return False
    
    # Most other workflow errors are retryable
    return error.is_retryable()


def get_workflow_retry_delay(error: WorkflowError) -> Optional[int]:
    """
    Get recommended retry delay for workflow errors.
    
    Args:
        error: The workflow error
        
    Returns:
        Recommended delay in seconds, or None if not retryable
    """
    if not is_retryable_workflow_error(error):
        return None
    
    if isinstance(error, UseCaseTimeoutError):
        # Use half the original timeout as delay
        return int(error.timeout_duration * 0.5)
    
    if isinstance(error, ServiceDependencyError):
        # Longer delay for service dependencies
        return 30
    
    if isinstance(error, UseCaseDependencyError):
        # Medium delay for use case dependencies
        return 15
    
    if isinstance(error, ParallelWorkflowError):
        # Short delay for parallel workflow retries
        return 5
    
    # Default retry delay
    return 10


def get_workflow_recovery_suggestions(error: WorkflowError) -> List[str]:
    """
    Generate recovery suggestions for workflow errors.
    
    Args:
        error: The workflow error to analyze
        
    Returns:
        List of recovery suggestions
    """
    suggestions = list(error.recovery_suggestions)
    
    if isinstance(error, UseCaseValidationError):
        suggestions.extend([
            "Validate input parameters before execution",
            "Check parameter types and constraints",
            "Review use case documentation"
        ])
        if error.invalid_parameters:
            suggestions.extend([f"Fix parameter: {param}" for param in error.invalid_parameters[:3]])
    
    elif isinstance(error, UseCasePreconditionError):
        suggestions.extend([
            "Ensure system is in correct state",
            "Check prerequisite conditions",
            "Review use case preconditions"
        ])
        if error.failed_preconditions:
            suggestions.extend([f"Satisfy precondition: {pre}" for pre in error.failed_preconditions[:3]])
    
    elif isinstance(error, UseCaseTimeoutError):
        suggestions.extend([
            f"Increase timeout from {error.timeout_duration} seconds",
            "Break operation into smaller steps",
            "Optimize slow operations",
            "Check system performance"
        ])
    
    elif isinstance(error, CharacterCreationWorkflowError):
        suggestions.extend([
            "Complete all required character information",
            "Validate character build rules",
            "Check for conflicting character options"
        ])
        if error.validation_errors:
            suggestions.extend([f"Fix validation: {err}" for err in error.validation_errors[:3]])
    
    elif isinstance(error, CharacterLevelUpWorkflowError):
        suggestions.extend([
            "Select all required level-up choices",
            "Verify level progression rules",
            "Check class requirements"
        ])
        if error.missing_choices:
            suggestions.extend([f"Make choice: {choice}" for choice in error.missing_choices[:3]])
    
    elif isinstance(error, CampaignCreationWorkflowError):
        suggestions.extend([
            "Complete campaign setup information",
            "Verify DM permissions",
            "Check campaign rules configuration"
        ])
    
    elif isinstance(error, BusinessProcessError):
        suggestions.extend([
            "Review business rule requirements",
            "Check data consistency",
            "Validate business logic"
        ])
        if error.business_rules:
            suggestions.extend([f"Review rule: {rule}" for rule in error.business_rules[:3]])
    
    elif isinstance(error, ServiceDependencyError):
        suggestions.extend([
            f"Check {error.failed_dependency} service status",
            "Verify service configuration",
            "Review service dependencies",
            "Implement fallback mechanisms"
        ])
    
    elif isinstance(error, InvalidWorkflowTransitionError):
        suggestions.extend([
            f"Use valid transition from {error.current_state.value}",
            "Check workflow state requirements",
            "Review transition rules"
        ])
        if error.valid_transitions:
            valid_names = [t.value for t in error.valid_transitions[:3]]
            suggestions.extend([f"Try transition: {name}" for name in valid_names])
    
    elif isinstance(error, WorkflowStateCorruptionError):
        suggestions.extend([
            "Reset workflow to known good state",
            "Restore from backup if available",
            "Reinitialize workflow state",
            "Contact system administrator"
        ])
        if error.corrupted_fields:
            suggestions.extend([f"Repair field: {field}" for field in error.corrupted_fields[:3]])
    
    elif isinstance(error, ParallelWorkflowError):
        suggestions.extend([
            f"Retry {len(error.failed_workflows)} failed workflows",
            "Check individual workflow failures",
            "Consider sequential execution"
        ])
        if error.failed_workflows:
            suggestions.extend([f"Check workflow: {wf}" for wf in error.failed_workflows[:3]])
    
    return suggestions


def create_workflow_error_context(
    operation: str,
    workflow_name: Optional[str] = None,
    workflow_stage: Optional[str] = None,
    entity_id: Optional[str] = None,
    additional_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create standardized error context for workflow operations.
    
    Args:
        operation: Name of the workflow operation
        workflow_name: Name of the workflow
        workflow_stage: Current stage of execution
        entity_id: ID of the entity being processed
        additional_context: Additional context information
        
    Returns:
        Context dictionary for error reporting
    """
    context = {
        "operation": operation,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if workflow_name:
        context["workflow_name"] = workflow_name
    
    if workflow_stage:
        context["workflow_stage"] = workflow_stage
    
    if entity_id:
        context["entity_id"] = entity_id
    
    if additional_context:
        context.update(additional_context)
    
    return context


def validate_workflow_preconditions(
    workflow_name: str,
    preconditions: Dict[str, Any],
    system_state: Dict[str, Any]
) -> List[str]:
    """
    Validate workflow preconditions.
    
    Args:
        workflow_name: Name of the workflow
        preconditions: Required preconditions
        system_state: Current system state
        
    Returns:
        List of failed preconditions (empty if all satisfied)
    """
    failed_preconditions = []
    
    for condition_name, required_value in preconditions.items():
        if condition_name not in system_state:
            failed_preconditions.append(f"Missing state: {condition_name}")
        elif system_state[condition_name] != required_value:
            failed_preconditions.append(
                f"Invalid state: {condition_name}={system_state[condition_name]}, expected {required_value}"
            )
    
    return failed_preconditions


def validate_workflow_postconditions(
    workflow_name: str,
    postconditions: Dict[str, Any],
    execution_results: Dict[str, Any],
    system_state: Dict[str, Any]
) -> List[str]:
    """
    Validate workflow postconditions.
    
    Args:
        workflow_name: Name of the workflow
        postconditions: Required postconditions
        execution_results: Results of workflow execution
        system_state: Current system state after execution
        
    Returns:
        List of failed postconditions (empty if all satisfied)
    """
    failed_postconditions = []
    
    for condition_name, expected_value in postconditions.items():
        # Check in execution results first
        if condition_name in execution_results:
            actual_value = execution_results[condition_name]
        # Then check in system state
        elif condition_name in system_state:
            actual_value = system_state[condition_name]
        else:
            failed_postconditions.append(f"Missing postcondition result: {condition_name}")
            continue
        
        if actual_value != expected_value:
            failed_postconditions.append(
                f"Postcondition failed: {condition_name}={actual_value}, expected {expected_value}"
            )
    
    return failed_postconditions


def analyze_workflow_failure(error: WorkflowError) -> Dict[str, Any]:
    """
    Analyze workflow failure and provide detailed information.
    
    Args:
        error: The workflow error to analyze
        
    Returns:
        Analysis dictionary with failure details
    """
    analysis = {
        "failure_type": "unknown",
        "severity": "medium",
        "is_recoverable": True,
        "recovery_strategy": "retry",
        "suggested_actions": []
    }
    
    if isinstance(error, UseCaseValidationError):
        analysis.update({
            "failure_type": "validation",
            "severity": "high",
            "is_recoverable": False,
            "recovery_strategy": "fix_input",
            "suggested_actions": [
                "Validate input parameters",
                "Check parameter constraints",
                "Review use case documentation"
            ],
            "invalid_parameters": error.invalid_parameters
        })
    
    elif isinstance(error, UseCaseTimeoutError):
        analysis.update({
            "failure_type": "timeout",
            "severity": "medium",
            "is_recoverable": True,
            "recovery_strategy": "retry_with_optimization",
            "suggested_actions": [
                "Increase timeout duration",
                "Optimize slow operations",
                "Break into smaller steps"
            ],
            "timeout_duration": error.timeout_duration,
            "completed_steps": error.completed_steps
        })
    
    elif isinstance(error, BusinessProcessError):
        analysis.update({
            "failure_type": "business_rule_violation",
            "severity": "high",
            "is_recoverable": False,
            "recovery_strategy": "fix_business_logic",
            "suggested_actions": [
                "Review business rules",
                "Check data consistency",
                "Validate business logic"
            ],
            "violated_rules": error.business_rules
        })
    
    elif isinstance(error, WorkflowStateCorruptionError):
        analysis.update({
            "failure_type": "state_corruption",
            "severity": "critical",
            "is_recoverable": False,
            "recovery_strategy": "reset_state",
            "suggested_actions": [
                "Reset workflow state",
                "Restore from backup",
                "Contact administrator"
            ],
            "corrupted_fields": error.corrupted_fields
        })
    
    elif isinstance(error, ServiceDependencyError):
        analysis.update({
            "failure_type": "dependency_failure",
            "severity": "high",
            "is_recoverable": True,
            "recovery_strategy": "fix_dependency",
            "suggested_actions": [
                "Check service availability",
                "Verify service configuration",
                "Implement fallback"
            ],
            "failed_dependency": error.failed_dependency
        })
    
    return analysis


# ============ MODULE METADATA ============

__version__ = '2.0.0'
__description__ = 'Application workflow and use case exceptions for D&D Creative Content Framework'
__author__ = 'D&D Character Creator Backend6'

# Clean Architecture compliance metadata
CLEAN_ARCHITECTURE_COMPLIANCE = {
    "layer": "core/exceptions",
    "dependencies": ["core/enums", "core/exceptions/base"],
    "dependents": ["domain/services", "application/use_cases", "infrastructure"],
    "infrastructure_independent": True,
    "focuses_on": "D&D application workflow and use case business rules"
}

# Exception statistics
EXCEPTION_STATISTICS = {
    "base_workflow_exceptions": 2,
    "use_case_exceptions": 6,
    "character_workflow_exceptions": 4,
    "campaign_workflow_exceptions": 3,
    "business_process_exceptions": 3,
    "application_service_exceptions": 4,
    "workflow_state_exceptions": 3,
    "workflow_orchestration_exceptions": 3,
    "total_exception_types": 28,
    "utility_functions": 8
}