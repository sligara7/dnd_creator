"""
Essential D&D Integration Exception Types

Streamlined integration-related exception handling following backend7 architecture.
Based on crude_functional.py patterns and essential-only philosophy.
"""

from typing import Optional, Dict, Any, List
from .base import DnDCharacterCreatorError

# ============ SYSTEM INTEGRATION EXCEPTIONS ============

class ServiceIntegrationError(DnDCharacterCreatorError):
    """External service integration failures."""
    
    def __init__(self, service_name: str, operation: str, integration_error: str, **kwargs):
        message = f"Service integration failed: {service_name} {operation} - {integration_error}"
        details = {
            "service_name": service_name,
            "operation": operation,
            "integration_error": integration_error,
            **kwargs
        }
        super().__init__(message, details)
        self.service_name = service_name
        self.operation = operation
        self.integration_error = integration_error

class APIConnectionError(DnDCharacterCreatorError):
    """API connection and communication failures."""
    
    def __init__(self, api_endpoint: str, connection_error: str, **kwargs):
        message = f"API connection failed: {api_endpoint} - {connection_error}"
        details = {
            "api_endpoint": api_endpoint,
            "connection_error": connection_error,
            **kwargs
        }
        super().__init__(message, details)
        self.api_endpoint = api_endpoint
        self.connection_error = connection_error

class AuthenticationError(DnDCharacterCreatorError):
    """Authentication failures with external services."""
    
    def __init__(self, service: str, auth_method: str, auth_error: str, **kwargs):
        message = f"Authentication failed: {service} via {auth_method} - {auth_error}"
        details = {
            "service": service,
            "auth_method": auth_method,
            "auth_error": auth_error,
            **kwargs
        }
        super().__init__(message, details)
        self.service = service
        self.auth_method = auth_method

# ============ DATA INTEGRATION EXCEPTIONS ============

class DataSyncError(DnDCharacterCreatorError):
    """Data synchronization failures between systems."""
    
    def __init__(self, source_system: str, target_system: str, sync_error: str, **kwargs):
        message = f"Data sync failed: {source_system} -> {target_system} - {sync_error}"
        details = {
            "source_system": source_system,
            "target_system": target_system,
            "sync_error": sync_error,
            **kwargs
        }
        super().__init__(message, details)
        self.source_system = source_system
        self.target_system = target_system

class DataFormatMismatchError(DnDCharacterCreatorError):
    """Data format incompatibility between systems."""
    
    def __init__(self, expected_format: str, received_format: str, data_type: str, **kwargs):
        message = f"Data format mismatch for {data_type}: expected {expected_format}, got {received_format}"
        details = {
            "expected_format": expected_format,
            "received_format": received_format,
            "data_type": data_type,
            **kwargs
        }
        super().__init__(message, details)
        self.expected_format = expected_format
        self.received_format = received_format
        self.data_type = data_type

class VersionMismatchError(DnDCharacterCreatorError):
    """Version compatibility issues between systems."""
    
    def __init__(self, system_name: str, current_version: str, required_version: str, **kwargs):
        message = f"Version mismatch: {system_name} v{current_version}, requires v{required_version}"
        details = {
            "system_name": system_name,
            "current_version": current_version,
            "required_version": required_version,
            **kwargs
        }
        super().__init__(message, details)
        self.system_name = system_name
        self.current_version = current_version
        self.required_version = required_version

# ============ WORKFLOW INTEGRATION EXCEPTIONS ============

class WorkflowInterruptionError(DnDCharacterCreatorError):
    """Workflow interruption due to integration issues."""
    
    def __init__(self, workflow_stage: str, interruption_cause: str, **kwargs):
        message = f"Workflow interrupted at {workflow_stage}: {interruption_cause}"
        details = {
            "workflow_stage": workflow_stage,
            "interruption_cause": interruption_cause,
            **kwargs
        }
        super().__init__(message, details)
        self.workflow_stage = workflow_stage
        self.interruption_cause = interruption_cause

class StateTransitionError(DnDCharacterCreatorError):
    """Invalid state transitions during integration."""
    
    def __init__(self, current_state: str, attempted_state: str, transition_error: str, **kwargs):
        message = f"State transition failed: {current_state} -> {attempted_state} - {transition_error}"
        details = {
            "current_state": current_state,
            "attempted_state": attempted_state,
            "transition_error": transition_error,
            **kwargs
        }
        super().__init__(message, details)
        self.current_state = current_state
        self.attempted_state = attempted_state

# ============ DEPENDENCY INTEGRATION EXCEPTIONS ============

class DependencyError(DnDCharacterCreatorError):
    """Missing or incompatible dependencies."""
    
    def __init__(self, dependency_name: str, dependency_issue: str, **kwargs):
        message = f"Dependency error: {dependency_name} - {dependency_issue}"
        details = {
            "dependency_name": dependency_name,
            "dependency_issue": dependency_issue,
            **kwargs
        }
        super().__init__(message, details)
        self.dependency_name = dependency_name
        self.dependency_issue = dependency_issue

class ModuleImportError(DnDCharacterCreatorError):
    """Module import failures during integration."""
    
    def __init__(self, module_name: str, import_error: str, **kwargs):
        message = f"Module import failed: {module_name} - {import_error}"
        details = {
            "module_name": module_name,
            "import_error": import_error,
            **kwargs
        }
        super().__init__(message, details)
        self.module_name = module_name
        self.import_error = import_error

# ============ UTILITY FUNCTIONS ============

def create_service_integration_error(service: str, operation: str, error: str) -> ServiceIntegrationError:
    """Factory function for service integration errors."""
    return ServiceIntegrationError(service, operation, error)

def create_api_connection_error(endpoint: str, error: str) -> APIConnectionError:
    """Factory function for API connection errors."""
    return APIConnectionError(endpoint, error)

def create_data_sync_error(source: str, target: str, error: str) -> DataSyncError:
    """Factory function for data sync errors."""
    return DataSyncError(source, target, error)

def is_retryable_integration_error(error: DnDCharacterCreatorError) -> bool:
    """Check if integration error can be retried."""
    retryable_types = [
        APIConnectionError,
        DataSyncError,
        WorkflowInterruptionError
    ]
    return any(isinstance(error, error_type) for error_type in retryable_types)

def requires_system_admin(error: DnDCharacterCreatorError) -> bool:
    """Check if integration error requires system administrator intervention."""
    admin_types = [
        DependencyError,
        ModuleImportError,
        VersionMismatchError,
        AuthenticationError
    ]
    return any(isinstance(error, error_type) for error_type in admin_types)

def get_integration_error_severity(error: DnDCharacterCreatorError) -> str:
    """Get integration error severity level."""
    severity_map = {
        ServiceIntegrationError: "error",
        APIConnectionError: "error",
        AuthenticationError: "critical",
        DataSyncError: "error",
        DataFormatMismatchError: "error",
        VersionMismatchError: "critical",
        WorkflowInterruptionError: "warning",
        StateTransitionError: "error",
        DependencyError: "critical",
        ModuleImportError: "critical"
    }
    return severity_map.get(type(error), "error")

def is_configuration_issue(error: DnDCharacterCreatorError) -> bool:
    """Check if integration error is due to configuration issues."""
    config_types = [
        AuthenticationError,
        VersionMismatchError,
        DependencyError
    ]
    return any(isinstance(error, error_type) for error_type in config_types)

# ============ ESSENTIAL EXPORTS ============

__all__ = [
    # System integration exceptions
    'ServiceIntegrationError',
    'APIConnectionError',
    'AuthenticationError',
    
    # Data integration exceptions
    'DataSyncError',
    'DataFormatMismatchError',
    'VersionMismatchError',
    
    # Workflow integration exceptions
    'WorkflowInterruptionError',
    'StateTransitionError',
    
    # Dependency integration exceptions
    'DependencyError',
    'ModuleImportError',
    
    # Utility functions
    'create_service_integration_error',
    'create_api_connection_error',
    'create_data_sync_error',
    'is_retryable_integration_error',
    'requires_system_admin',
    'get_integration_error_severity',
    'is_configuration_issue',
]

# ============ MODULE METADATA ============

__version__ = '1.0.0'
__description__ = 'Essential D&D integration exception handling'
__author__ = 'D&D Character Creator Backend7'

# Backend7 architecture compliance
BACKEND7_COMPLIANCE = {
    "layer": "core/exceptions",
    "focus": "integration_error_handling_only",
    "line_target": 150,
    "dependencies": ["base"],
    "philosophy": "crude_functional_inspired_simple_integration_exceptions"
}