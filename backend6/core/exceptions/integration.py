"""
Integration and External Service Exceptions for the D&D Creative Content Framework.

This module defines exceptions related to external service failures, API integration
issues, third-party service connectivity problems, and data synchronization errors.
These exceptions represent business rule violations and failure states in the
integration and external service communication domain.

Following Clean Architecture principles, these exceptions are:
- Infrastructure-independent (don't depend on specific API implementations)
- Focused on D&D integration and external service business rules
- Designed for proper error handling and recovery strategies
- Aligned with the external service integration and data synchronization workflow
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from ..enums.integration_types import IntegrationType, ServiceProvider, IntegrationStatus, SynchronizationMode
from ..enums.validation_types import ValidationSeverity
from ..enums.content_types import ContentType
from .base import DnDFrameworkError, ValidationError


# ============ BASE INTEGRATION EXCEPTIONS ============

class IntegrationError(DnDFrameworkError):
    """Base exception for all integration and external service errors."""
    
    def __init__(
        self,
        message: str,
        service_name: Optional[str] = None,
        integration_type: Optional[IntegrationType] = None,
        service_provider: Optional[ServiceProvider] = None,
        request_id: Optional[str] = None,
        endpoint: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.service_name = service_name
        self.integration_type = integration_type
        self.service_provider = service_provider
        self.request_id = request_id
        self.endpoint = endpoint
    
    def _generate_error_code(self) -> str:
        """Generate integration-specific error code."""
        base_code = "INT"
        service_code = self.service_provider.value[:3].upper() if self.service_provider else "GEN"
        timestamp_code = str(int(self.timestamp.timestamp()))[-6:]
        return f"{base_code}_{service_code}_{timestamp_code}"
    
    def get_category(self) -> str:
        """Integration error category."""
        return "integration"
    
    def is_retryable(self) -> bool:
        """Most integration errors are retryable."""
        return True
    
    def should_fail_fast(self) -> bool:
        """Integration errors don't fail fast by default."""
        return False
    
    def __str__(self) -> str:
        parts = [super().__str__()]
        
        if self.service_name:
            parts.append(f"Service: {self.service_name}")
        
        if self.integration_type:
            parts.append(f"Type: {self.integration_type.value}")
        
        if self.request_id:
            parts.append(f"Request: {self.request_id}")
        
        return " | ".join(parts)


class ExternalServiceError(IntegrationError):
    """Base exception for external service communication failures."""
    
    def __init__(
        self,
        message: str,
        service_endpoint: Optional[str] = None,
        response_code: Optional[int] = None,
        response_body: Optional[str] = None,
        request_data: Optional[Dict[str, Any]] = None,
        service_metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(message, endpoint=service_endpoint, **kwargs)
        self.service_endpoint = service_endpoint
        self.response_code = response_code
        self.response_body = response_body
        self.request_data = request_data or {}
        self.service_metadata = service_metadata or {}
    
    def get_category(self) -> str:
        return "external_service"
    
    def __str__(self) -> str:
        parts = [super().__str__()]
        
        if self.response_code:
            parts.append(f"Status: {self.response_code}")
        
        if self.service_endpoint:
            parts.append(f"Endpoint: {self.service_endpoint}")
        
        return " | ".join(parts)


# ============ API INTEGRATION EXCEPTIONS ============

class APIConnectionError(ExternalServiceError):
    """Exception for API connection failures."""
    
    def __init__(
        self,
        api_name: str,
        connection_issue: str,
        host: Optional[str] = None,
        port: Optional[int] = None,
        timeout_duration: Optional[float] = None,
        retry_count: Optional[int] = None,
        **kwargs
    ):
        message = f"API connection failed to {api_name}: {connection_issue}"
        if host:
            message += f" (host: {host}"
            if port:
                message += f":{port}"
            message += ")"
        
        super().__init__(
            message,
            service_name=api_name,
            integration_type=IntegrationType.REST_API,
            **kwargs
        )
        self.api_name = api_name
        self.connection_issue = connection_issue
        self.host = host
        self.port = port
        self.timeout_duration = timeout_duration
        self.retry_count = retry_count or 0
    
    def get_category(self) -> str:
        return "api_connection"
    
    def is_retryable(self) -> bool:
        """Connection errors are generally retryable."""
        return True


class APIAuthenticationError(ExternalServiceError):
    """Exception for API authentication failures."""
    
    def __init__(
        self,
        api_name: str,
        auth_issue: str,
        auth_method: Optional[str] = None,
        auth_scope: Optional[List[str]] = None,
        token_expired: bool = False,
        **kwargs
    ):
        message = f"API authentication failed for {api_name}: {auth_issue}"
        if auth_method:
            message += f" (method: {auth_method})"
        
        super().__init__(
            message,
            service_name=api_name,
            integration_type=IntegrationType.REST_API,
            **kwargs
        )
        self.api_name = api_name
        self.auth_issue = auth_issue
        self.auth_method = auth_method
        self.auth_scope = auth_scope or []
        self.token_expired = token_expired
    
    def get_category(self) -> str:
        return "api_authentication"
    
    def is_retryable(self) -> bool:
        """Authentication errors might be retryable if token can be refreshed."""
        return self.token_expired
    
    def should_fail_fast(self) -> bool:
        """Permanent auth failures should fail fast."""
        return not self.token_expired


class APIRateLimitError(ExternalServiceError):
    """Exception for API rate limit exceeded."""
    
    def __init__(
        self,
        api_name: str,
        rate_limit_type: str,
        current_usage: int,
        limit: int,
        reset_time: Optional[datetime] = None,
        retry_after_seconds: Optional[int] = None,
        **kwargs
    ):
        message = f"API rate limit exceeded for {api_name}: {current_usage}/{limit} {rate_limit_type}"
        if retry_after_seconds:
            message += f" (retry after {retry_after_seconds}s)"
        
        super().__init__(
            message,
            service_name=api_name,
            integration_type=IntegrationType.REST_API,
            response_code=429,
            **kwargs
        )
        self.api_name = api_name
        self.rate_limit_type = rate_limit_type
        self.current_usage = current_usage
        self.limit = limit
        self.reset_time = reset_time
        self.retry_after_seconds = retry_after_seconds
    
    def get_category(self) -> str:
        return "api_rate_limit"
    
    def is_retryable(self) -> bool:
        """Rate limit errors are retryable after waiting."""
        return True


class APIResponseError(ExternalServiceError):
    """Exception for API response format or content errors."""
    
    def __init__(
        self,
        api_name: str,
        response_issue: str,
        expected_format: Optional[str] = None,
        actual_format: Optional[str] = None,
        validation_errors: Optional[List[str]] = None,
        **kwargs
    ):
        message = f"API response error from {api_name}: {response_issue}"
        if expected_format and actual_format:
            message += f" (expected: {expected_format}, got: {actual_format})"
        
        super().__init__(
            message,
            service_name=api_name,
            integration_type=IntegrationType.REST_API,
            **kwargs
        )
        self.api_name = api_name
        self.response_issue = response_issue
        self.expected_format = expected_format
        self.actual_format = actual_format
        self.validation_errors = validation_errors or []
    
    def get_category(self) -> str:
        return "api_response"


class APIVersionError(ExternalServiceError):
    """Exception for API version compatibility issues."""
    
    def __init__(
        self,
        api_name: str,
        version_issue: str,
        required_version: Optional[str] = None,
        current_version: Optional[str] = None,
        supported_versions: Optional[List[str]] = None,
        **kwargs
    ):
        message = f"API version compatibility issue with {api_name}: {version_issue}"
        if required_version and current_version:
            message += f" (required: {required_version}, current: {current_version})"
        
        super().__init__(
            message,
            service_name=api_name,
            integration_type=IntegrationType.REST_API,
            **kwargs
        )
        self.api_name = api_name
        self.version_issue = version_issue
        self.required_version = required_version
        self.current_version = current_version
        self.supported_versions = supported_versions or []
    
    def get_category(self) -> str:
        return "api_version"
    
    def should_fail_fast(self) -> bool:
        """Version incompatibility should fail fast."""
        return True


# ============ D&D SERVICE PROVIDER EXCEPTIONS ============

class DNDBeyondIntegrationError(ExternalServiceError):
    """Exception for D&D Beyond API integration failures."""
    
    def __init__(
        self,
        integration_issue: str,
        character_id: Optional[str] = None,
        campaign_id: Optional[str] = None,
        dndbeyond_limitations: Optional[List[str]] = None,
        **kwargs
    ):
        message = f"D&D Beyond integration failed: {integration_issue}"
        super().__init__(
            message,
            service_name="D&D Beyond",
            service_provider=ServiceProvider.DND_BEYOND,
            integration_type=IntegrationType.REST_API,
            **kwargs
        )
        self.integration_issue = integration_issue
        self.character_id = character_id
        self.campaign_id = campaign_id
        self.dndbeyond_limitations = dndbeyond_limitations or []
    
    def get_category(self) -> str:
        return "dndbeyond_integration"


class Roll20IntegrationError(ExternalServiceError):
    """Exception for Roll20 API integration failures."""
    
    def __init__(
        self,
        integration_issue: str,
        campaign_id: Optional[str] = None,
        character_sheet_id: Optional[str] = None,
        roll20_limitations: Optional[List[str]] = None,
        **kwargs
    ):
        message = f"Roll20 integration failed: {integration_issue}"
        super().__init__(
            message,
            service_name="Roll20",
            service_provider=ServiceProvider.ROLL20,
            integration_type=IntegrationType.REST_API,
            **kwargs
        )
        self.integration_issue = integration_issue
        self.campaign_id = campaign_id
        self.character_sheet_id = character_sheet_id
        self.roll20_limitations = roll20_limitations or []
    
    def get_category(self) -> str:
        return "roll20_integration"


class FantasyGroundsIntegrationError(ExternalServiceError):
    """Exception for Fantasy Grounds integration failures."""
    
    def __init__(
        self,
        integration_issue: str,
        module_name: Optional[str] = None,
        ruleset_version: Optional[str] = None,
        fg_limitations: Optional[List[str]] = None,
        **kwargs
    ):
        message = f"Fantasy Grounds integration failed: {integration_issue}"
        super().__init__(
            message,
            service_name="Fantasy Grounds",
            service_provider=ServiceProvider.FANTASY_GROUNDS,
            integration_type=IntegrationType.FILE_IMPORT,
            **kwargs
        )
        self.integration_issue = integration_issue
        self.module_name = module_name
        self.ruleset_version = ruleset_version
        self.fg_limitations = fg_limitations or []
    
    def get_category(self) -> str:
        return "fantasy_grounds_integration"


class FoundryVTTIntegrationError(ExternalServiceError):
    """Exception for Foundry VTT integration failures."""
    
    def __init__(
        self,
        integration_issue: str,
        world_id: Optional[str] = None,
        system_version: Optional[str] = None,
        module_conflicts: Optional[List[str]] = None,
        **kwargs
    ):
        message = f"Foundry VTT integration failed: {integration_issue}"
        super().__init__(
            message,
            service_name="Foundry VTT",
            service_provider=ServiceProvider.FOUNDRY_VTT,
            integration_type=IntegrationType.REST_API,
            **kwargs
        )
        self.integration_issue = integration_issue
        self.world_id = world_id
        self.system_version = system_version
        self.module_conflicts = module_conflicts or []
    
    def get_category(self) -> str:
        return "foundry_vtt_integration"


# ============ DATA SYNCHRONIZATION EXCEPTIONS ============

class DataSynchronizationError(IntegrationError):
    """Exception for data synchronization failures."""
    
    def __init__(
        self,
        sync_issue: str,
        source_system: str,
        target_system: str,
        sync_mode: Optional[SynchronizationMode] = None,
        conflicting_data: Optional[Dict[str, Any]] = None,
        sync_metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        message = f"Data synchronization failed from {source_system} to {target_system}: {sync_issue}"
        super().__init__(
            message,
            integration_type=IntegrationType.DATA_SYNC,
            **kwargs
        )
        self.sync_issue = sync_issue
        self.source_system = source_system
        self.target_system = target_system
        self.sync_mode = sync_mode
        self.conflicting_data = conflicting_data or {}
        self.sync_metadata = sync_metadata or {}
    
    def get_category(self) -> str:
        return "data_synchronization"


class DataConflictError(DataSynchronizationError):
    """Exception for data conflicts during synchronization."""
    
    def __init__(
        self,
        conflict_type: str,
        conflicting_fields: List[str],
        source_values: Dict[str, Any],
        target_values: Dict[str, Any],
        last_modified_source: Optional[datetime] = None,
        last_modified_target: Optional[datetime] = None,
        **kwargs
    ):
        conflict_summary = f"{conflict_type} conflict in fields: {', '.join(conflicting_fields)}"
        super().__init__(
            sync_issue=conflict_summary,
            conflicting_data={
                "source": source_values,
                "target": target_values,
                "conflicting_fields": conflicting_fields
            },
            **kwargs
        )
        self.conflict_type = conflict_type
        self.conflicting_fields = conflicting_fields
        self.source_values = source_values
        self.target_values = target_values
        self.last_modified_source = last_modified_source
        self.last_modified_target = last_modified_target
    
    def get_category(self) -> str:
        return "data_conflict"
    
    def should_fail_fast(self) -> bool:
        """Data conflicts might need immediate resolution."""
        critical_conflicts = ["character_deletion", "critical_data_loss", "ownership_change"]
        return self.conflict_type in critical_conflicts


class CharacterSyncError(DataSynchronizationError):
    """Exception for character data synchronization failures."""
    
    def __init__(
        self,
        character_name: str,
        character_id: Optional[str] = None,
        sync_issue: str = "synchronization failed",
        missing_fields: Optional[List[str]] = None,
        transformation_errors: Optional[List[str]] = None,
        **kwargs
    ):
        message = f"Character synchronization failed for '{character_name}': {sync_issue}"
        super().__init__(
            sync_issue=message,
            **kwargs
        )
        self.character_name = character_name
        self.character_id = character_id
        self.missing_fields = missing_fields or []
        self.transformation_errors = transformation_errors or []
    
    def get_category(self) -> str:
        return "character_sync"


class CampaignSyncError(DataSynchronizationError):
    """Exception for campaign data synchronization failures."""
    
    def __init__(
        self,
        campaign_name: str,
        campaign_id: Optional[str] = None,
        sync_issue: str = "synchronization failed",
        player_conflicts: Optional[List[str]] = None,
        permission_issues: Optional[List[str]] = None,
        **kwargs
    ):
        message = f"Campaign synchronization failed for '{campaign_name}': {sync_issue}"
        super().__init__(
            sync_issue=message,
            **kwargs
        )
        self.campaign_name = campaign_name
        self.campaign_id = campaign_id
        self.player_conflicts = player_conflicts or []
        self.permission_issues = permission_issues or []
    
    def get_category(self) -> str:
        return "campaign_sync"


# ============ WEBHOOK AND REAL-TIME INTEGRATION EXCEPTIONS ============

class WebhookError(IntegrationError):
    """Exception for webhook integration failures."""
    
    def __init__(
        self,
        webhook_url: str,
        webhook_issue: str,
        event_type: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
        response_status: Optional[int] = None,
        **kwargs
    ):
        message = f"Webhook failed for {webhook_url}: {webhook_issue}"
        if event_type:
            message += f" (event: {event_type})"
        
        super().__init__(
            message,
            integration_type=IntegrationType.WEBHOOK,
            endpoint=webhook_url,
            **kwargs
        )
        self.webhook_url = webhook_url
        self.webhook_issue = webhook_issue
        self.event_type = event_type
        self.payload = payload or {}
        self.response_status = response_status
    
    def get_category(self) -> str:
        return "webhook"
    
    def is_retryable(self) -> bool:
        """Webhooks are retryable unless it's a client error."""
        if self.response_status:
            # 4xx errors are generally not retryable, 5xx are
            return not (400 <= self.response_status < 500)
        return True


class WebSocketError(IntegrationError):
    """Exception for WebSocket connection failures."""
    
    def __init__(
        self,
        websocket_url: str,
        websocket_issue: str,
        connection_state: Optional[str] = None,
        last_message: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        message = f"WebSocket failed for {websocket_url}: {websocket_issue}"
        if connection_state:
            message += f" (state: {connection_state})"
        
        super().__init__(
            message,
            integration_type=IntegrationType.WEBSOCKET,
            endpoint=websocket_url,
            **kwargs
        )
        self.websocket_url = websocket_url
        self.websocket_issue = websocket_issue
        self.connection_state = connection_state
        self.last_message = last_message or {}
    
    def get_category(self) -> str:
        return "websocket"
    
    def is_retryable(self) -> bool:
        """WebSocket errors are generally retryable."""
        return True


class RealTimeUpdateError(IntegrationError):
    """Exception for real-time update failures."""
    
    def __init__(
        self,
        update_type: str,
        update_issue: str,
        affected_entities: Optional[List[str]] = None,
        update_payload: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        message = f"Real-time update failed for {update_type}: {update_issue}"
        if affected_entities:
            message += f" (affects: {', '.join(affected_entities)})"
        
        super().__init__(
            message,
            integration_type=IntegrationType.REAL_TIME,
            **kwargs
        )
        self.update_type = update_type
        self.update_issue = update_issue
        self.affected_entities = affected_entities or []
        self.update_payload = update_payload or {}
    
    def get_category(self) -> str:
        return "real_time_update"


# ============ THIRD-PARTY SERVICE EXCEPTIONS ============

class ThirdPartyServiceError(ExternalServiceError):
    """Exception for third-party service integration failures."""
    
    def __init__(
        self,
        service_name: str,
        service_issue: str,
        service_type: Optional[str] = None,
        service_version: Optional[str] = None,
        dependency_issues: Optional[List[str]] = None,
        **kwargs
    ):
        message = f"Third-party service '{service_name}' failed: {service_issue}"
        if service_type:
            message += f" (type: {service_type})"
        
        super().__init__(
            message,
            service_name=service_name,
            integration_type=IntegrationType.THIRD_PARTY,
            **kwargs
        )
        self.service_issue = service_issue
        self.service_type = service_type
        self.service_version = service_version
        self.dependency_issues = dependency_issues or []
    
    def get_category(self) -> str:
        return "third_party_service"


class CloudServiceError(ThirdPartyServiceError):
    """Exception for cloud service integration failures."""
    
    def __init__(
        self,
        cloud_provider: str,
        service_name: str,
        cloud_issue: str,
        region: Optional[str] = None,
        availability_zone: Optional[str] = None,
        **kwargs
    ):
        message = f"Cloud service failure: {cloud_provider} {service_name} - {cloud_issue}"
        if region:
            message += f" (region: {region})"
        
        super().__init__(
            service_name=f"{cloud_provider} {service_name}",
            service_issue=cloud_issue,
            service_type="cloud",
            **kwargs
        )
        self.cloud_provider = cloud_provider
        self.cloud_issue = cloud_issue
        self.region = region
        self.availability_zone = availability_zone
    
    def get_category(self) -> str:
        return "cloud_service"


class DatabaseServiceError(ThirdPartyServiceError):
    """Exception for database service integration failures."""
    
    def __init__(
        self,
        database_type: str,
        database_issue: str,
        connection_string: Optional[str] = None,
        query_context: Optional[str] = None,
        **kwargs
    ):
        message = f"Database service failure: {database_type} - {database_issue}"
        
        super().__init__(
            service_name=database_type,
            service_issue=database_issue,
            service_type="database",
            **kwargs
        )
        self.database_type = database_type
        self.database_issue = database_issue
        self.connection_string = connection_string
        self.query_context = query_context
    
    def get_category(self) -> str:
        return "database_service"


# ============ INTEGRATION CONFIGURATION EXCEPTIONS ============

class IntegrationConfigError(IntegrationError):
    """Exception for integration configuration errors."""
    
    def __init__(
        self,
        config_issue: str,
        config_key: Optional[str] = None,
        config_value: Optional[Any] = None,
        required_configs: Optional[List[str]] = None,
        **kwargs
    ):
        message = f"Integration configuration error: {config_issue}"
        if config_key:
            message += f" (key: {config_key})"
        
        super().__init__(
            message,
            integration_type=IntegrationType.CONFIGURATION,
            **kwargs
        )
        self.config_issue = config_issue
        self.config_key = config_key
        self.config_value = config_value
        self.required_configs = required_configs or []
    
    def get_category(self) -> str:
        return "integration_config"
    
    def should_fail_fast(self) -> bool:
        """Configuration errors should fail fast."""
        return True


class ServiceDiscoveryError(IntegrationError):
    """Exception for service discovery failures."""
    
    def __init__(
        self,
        service_name: str,
        discovery_issue: str,
        service_registry: Optional[str] = None,
        available_services: Optional[List[str]] = None,
        **kwargs
    ):
        message = f"Service discovery failed for '{service_name}': {discovery_issue}"
        if service_registry:
            message += f" (registry: {service_registry})"
        
        super().__init__(
            message,
            service_name=service_name,
            integration_type=IntegrationType.SERVICE_DISCOVERY,
            **kwargs
        )
        self.discovery_issue = discovery_issue
        self.service_registry = service_registry
        self.available_services = available_services or []
    
    def get_category(self) -> str:
        return "service_discovery"


class CircuitBreakerError(IntegrationError):
    """Exception for circuit breaker activation."""
    
    def __init__(
        self,
        service_name: str,
        circuit_state: str,
        failure_count: int,
        failure_threshold: int,
        reset_timeout: Optional[timedelta] = None,
        **kwargs
    ):
        message = f"Circuit breaker {circuit_state} for '{service_name}' ({failure_count}/{failure_threshold} failures)"
        if reset_timeout:
            message += f" (reset in {reset_timeout.total_seconds()}s)"
        
        super().__init__(
            message,
            service_name=service_name,
            integration_type=IntegrationType.CIRCUIT_BREAKER,
            **kwargs
        )
        self.circuit_state = circuit_state
        self.failure_count = failure_count
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
    
    def get_category(self) -> str:
        return "circuit_breaker"
    
    def is_retryable(self) -> bool:
        """Circuit breaker errors are retryable after timeout."""
        return self.circuit_state == "half_open"


# ============ INTEGRATION PERFORMANCE EXCEPTIONS ============

class IntegrationTimeoutError(IntegrationError):
    """Exception for integration operation timeouts."""
    
    def __init__(
        self,
        service_name: str,
        timeout_duration: float,
        operation: Optional[str] = None,
        partial_response: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        message = f"Integration timeout with {service_name} after {timeout_duration}s"
        if operation:
            message += f" during {operation}"
        
        super().__init__(
            message,
            service_name=service_name,
            integration_type=IntegrationType.TIMEOUT,
            **kwargs
        )
        self.timeout_duration = timeout_duration
        self.operation = operation
        self.partial_response = partial_response or {}
    
    def get_category(self) -> str:
        return "integration_timeout"
    
    def is_retryable(self) -> bool:
        """Timeout errors are generally retryable."""
        return True


class IntegrationResourceError(IntegrationError):
    """Exception for integration resource limitations."""
    
    def __init__(
        self,
        service_name: str,
        resource_type: str,
        resource_limit: Union[int, float],
        current_usage: Union[int, float],
        **kwargs
    ):
        message = f"Integration resource limit exceeded for {service_name}: {resource_type} {current_usage}/{resource_limit}"
        
        super().__init__(
            message,
            service_name=service_name,
            integration_type=IntegrationType.RESOURCE_LIMIT,
            **kwargs
        )
        self.resource_type = resource_type
        self.resource_limit = resource_limit
        self.current_usage = current_usage
    
    def get_category(self) -> str:
        return "integration_resource"


class IntegrationQuotaError(IntegrationError):
    """Exception for integration quota exceeded."""
    
    def __init__(
        self,
        service_name: str,
        quota_type: str,
        quota_limit: int,
        current_usage: int,
        reset_time: Optional[datetime] = None,
        **kwargs
    ):
        message = f"Integration quota exceeded for {service_name}: {quota_type} {current_usage}/{quota_limit}"
        if reset_time:
            message += f" (resets: {reset_time.isoformat()})"
        
        super().__init__(
            message,
            service_name=service_name,
            integration_type=IntegrationType.QUOTA_EXCEEDED,
            **kwargs
        )
        self.quota_type = quota_type
        self.quota_limit = quota_limit
        self.current_usage = current_usage
        self.reset_time = reset_time
    
    def get_category(self) -> str:
        return "integration_quota"
    
    def is_retryable(self) -> bool:
        """Quota errors are retryable after reset."""
        return True


# ============ DATA TRANSFORMATION EXCEPTIONS ============

class DataTransformationError(IntegrationError):
    """Exception for data transformation failures during integration."""
    
    def __init__(
        self,
        transformation_issue: str,
        source_format: str,
        target_format: str,
        field_mapping_errors: Optional[List[str]] = None,
        transformation_context: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        message = f"Data transformation failed from {source_format} to {target_format}: {transformation_issue}"
        
        super().__init__(
            message,
            integration_type=IntegrationType.DATA_TRANSFORMATION,
            **kwargs
        )
        self.transformation_issue = transformation_issue
        self.source_format = source_format
        self.target_format = target_format
        self.field_mapping_errors = field_mapping_errors or []
        self.transformation_context = transformation_context or {}
    
    def get_category(self) -> str:
        return "data_transformation"


class FieldMappingError(DataTransformationError):
    """Exception for field mapping failures during data transformation."""
    
    def __init__(
        self,
        field_name: str,
        mapping_issue: str,
        source_value: Optional[Any] = None,
        expected_target_type: Optional[str] = None,
        **kwargs
    ):
        transformation_issue = f"Field mapping failed for '{field_name}': {mapping_issue}"
        if source_value is not None and expected_target_type:
            transformation_issue += f" (source: {source_value}, target type: {expected_target_type})"
        
        super().__init__(
            transformation_issue=transformation_issue,
            field_mapping_errors=[field_name],
            **kwargs
        )
        self.field_name = field_name
        self.mapping_issue = mapping_issue
        self.source_value = source_value
        self.expected_target_type = expected_target_type
    
    def get_category(self) -> str:
        return "field_mapping"


class DataTypeConversionError(DataTransformationError):
    """Exception for data type conversion failures."""
    
    def __init__(
        self,
        field_name: str,
        source_type: str,
        target_type: str,
        conversion_issue: str,
        source_value: Optional[Any] = None,
        **kwargs
    ):
        transformation_issue = f"Type conversion failed for '{field_name}' from {source_type} to {target_type}: {conversion_issue}"
        if source_value is not None:
            transformation_issue += f" (value: {source_value})"
        
        super().__init__(
            transformation_issue=transformation_issue,
            field_mapping_errors=[field_name],
            **kwargs
        )
        self.field_name = field_name
        self.source_type = source_type
        self.target_type = target_type
        self.conversion_issue = conversion_issue
        self.source_value = source_value
    
    def get_category(self) -> str:
        return "data_type_conversion"


# ============ UTILITY FUNCTIONS FOR INTEGRATION EXCEPTION HANDLING ============

def categorize_integration_error(error: Exception) -> str:
    """
    Categorize an integration error for handling and routing.
    
    Args:
        error: The exception to categorize
        
    Returns:
        Error category string
    """
    if isinstance(error, APIConnectionError):
        return "api_connection"
    elif isinstance(error, APIAuthenticationError):
        return "api_authentication"
    elif isinstance(error, APIRateLimitError):
        return "api_rate_limit"
    elif isinstance(error, DataSynchronizationError):
        return "data_synchronization"
    elif isinstance(error, WebhookError):
        return "webhook"
    elif isinstance(error, WebSocketError):
        return "websocket"
    elif isinstance(error, ThirdPartyServiceError):
        return "third_party_service"
    elif isinstance(error, IntegrationConfigError):
        return "integration_config"
    elif isinstance(error, CircuitBreakerError):
        return "circuit_breaker"
    elif isinstance(error, DataTransformationError):
        return "data_transformation"
    elif isinstance(error, IntegrationTimeoutError):
        return "integration_timeout"
    elif isinstance(error, IntegrationResourceError):
        return "integration_resource"
    elif isinstance(error, ExternalServiceError):
        return "external_service"
    elif isinstance(error, IntegrationError):
        return "general_integration"
    else:
        return "unknown"


def is_retryable_integration_error(error: IntegrationError) -> bool:
    """
    Determine if an integration error is retryable.
    
    Args:
        error: The integration error to check
        
    Returns:
        True if the error might succeed on retry
    """
    # Connection errors are generally retryable
    if isinstance(error, APIConnectionError):
        return True
    
    # Rate limit errors are retryable after waiting
    if isinstance(error, APIRateLimitError):
        return True
    
    # Authentication errors might be retryable if token expired
    if isinstance(error, APIAuthenticationError):
        return error.token_expired
    
    # Webhook errors depend on response status
    if isinstance(error, WebhookError):
        return error.is_retryable()
    
    # Circuit breaker errors are retryable when half-open
    if isinstance(error, CircuitBreakerError):
        return error.circuit_state == "half_open"
    
    # Timeout errors are retryable
    if isinstance(error, IntegrationTimeoutError):
        return True
    
    # Quota errors are retryable after reset
    if isinstance(error, IntegrationQuotaError):
        return True
    
    # Configuration errors are not retryable
    if isinstance(error, IntegrationConfigError):
        return False
    
    # Data transformation errors are not retryable without fixing data
    if isinstance(error, DataTransformationError):
        return False
    
    # Most other integration errors are retryable
    return error.is_retryable()


def get_integration_retry_delay(error: IntegrationError) -> Optional[int]:
    """
    Get recommended retry delay for integration errors.
    
    Args:
        error: The integration error
        
    Returns:
        Recommended delay in seconds, or None if not retryable
    """
    if not is_retryable_integration_error(error):
        return None
    
    if isinstance(error, APIRateLimitError):
        return error.retry_after_seconds or 60
    
    if isinstance(error, APIConnectionError):
        # Exponential backoff based on retry count
        return min(2 ** (error.retry_count or 0), 300)  # Max 5 minutes
    
    if isinstance(error, CircuitBreakerError):
        if error.reset_timeout:
            return int(error.reset_timeout.total_seconds())
        return 60
    
    if isinstance(error, IntegrationTimeoutError):
        # Increase timeout slightly on retry
        return int(error.timeout_duration * 0.5)
    
    if isinstance(error, IntegrationQuotaError):
        if error.reset_time:
            now = datetime.utcnow()
            if error.reset_time > now:
                return int((error.reset_time - now).total_seconds())
        return 3600  # Default 1 hour
    
    if isinstance(error, WebhookError):
        return 30  # Standard webhook retry delay
    
    if isinstance(error, WebSocketError):
        return 5  # Quick retry for WebSocket reconnection
    
    # Default retry delay
    return 30


def get_integration_recovery_suggestions(error: IntegrationError) -> List[str]:
    """
    Generate recovery suggestions for integration errors.
    
    Args:
        error: The integration error to analyze
        
    Returns:
        List of recovery suggestions
    """
    suggestions = list(error.recovery_suggestions)
    
    if isinstance(error, APIConnectionError):
        suggestions.extend([
            f"Check network connectivity to {error.host or error.api_name}",
            "Verify service is running and accessible",
            "Check firewall and proxy settings",
            "Validate DNS resolution"
        ])
        if error.timeout_duration:
            suggestions.append(f"Consider increasing timeout from {error.timeout_duration}s")
    
    elif isinstance(error, APIAuthenticationError):
        suggestions.extend([
            "Verify API credentials are correct",
            "Check if API key/token has expired",
            "Validate required authentication scopes"
        ])
        if error.token_expired:
            suggestions.append("Refresh authentication token")
        if error.auth_scope:
            suggestions.append(f"Required scopes: {', '.join(error.auth_scope)}")
    
    elif isinstance(error, APIRateLimitError):
        suggestions.extend([
            f"Wait {error.retry_after_seconds or 60} seconds before retrying",
            "Implement exponential backoff",
            "Consider upgrading API plan for higher limits",
            "Optimize request frequency"
        ])
        if error.reset_time:
            suggestions.append(f"Rate limit resets at {error.reset_time.isoformat()}")
    
    elif isinstance(error, DataConflictError):
        suggestions.extend([
            "Review conflicting data and choose resolution strategy",
            "Implement conflict resolution rules",
            "Consider manual intervention for critical conflicts"
        ])
        for field in error.conflicting_fields[:3]:
            suggestions.append(f"Resolve conflict in field: {field}")
    
    elif isinstance(error, WebhookError):
        suggestions.extend([
            f"Verify webhook endpoint {error.webhook_url} is accessible",
            "Check webhook payload format",
            "Validate webhook authentication",
            "Review webhook response handling"
        ])
    
    elif isinstance(error, CircuitBreakerError):
        suggestions.extend([
            f"Wait for circuit breaker reset (current state: {error.circuit_state})",
            "Address underlying service issues",
            "Review circuit breaker configuration",
            f"Service has {error.failure_count}/{error.failure_threshold} failures"
        ])
    
    elif isinstance(error, IntegrationConfigError):
        suggestions.extend([
            "Review integration configuration settings",
            "Validate required configuration keys",
            "Check environment-specific configurations"
        ])
        if error.required_configs:
            suggestions.extend([f"Configure: {config}" for config in error.required_configs[:3]])
    
    elif isinstance(error, DataTransformationError):
        suggestions.extend([
            f"Review data transformation from {error.source_format} to {error.target_format}",
            "Validate field mapping configuration",
            "Check data type compatibility"
        ])
        if error.field_mapping_errors:
            suggestions.extend([f"Fix mapping for field: {field}" for field in error.field_mapping_errors[:3]])
    
    elif isinstance(error, IntegrationTimeoutError):
        suggestions.extend([
            f"Increase timeout from {error.timeout_duration}s",
            "Check network latency and service performance",
            "Consider breaking operation into smaller chunks"
        ])
        if error.operation:
            suggestions.append(f"Optimize {error.operation} operation")
    
    elif isinstance(error, IntegrationQuotaError):
        suggestions.extend([
            f"Wait for quota reset: {error.reset_time.isoformat() if error.reset_time else 'unknown'}",
            "Reduce API call frequency",
            "Consider upgrading service plan"
        ])
    
    return suggestions


def create_integration_error_context(
    operation: str,
    service_name: Optional[str] = None,
    integration_type: Optional[IntegrationType] = None,
    request_id: Optional[str] = None,
    additional_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create standardized error context for integration operations.
    
    Args:
        operation: Name of the integration operation
        service_name: Name of the external service
        integration_type: Type of integration
        request_id: Unique request identifier
        additional_context: Additional context information
        
    Returns:
        Context dictionary for error reporting
    """
    context = {
        "operation": operation,
        "timestamp": datetime.utcnow().isoformat(),
        "request_id": request_id
    }
    
    if service_name:
        context["service_name"] = service_name
    
    if integration_type:
        context["integration_type"] = integration_type.value
    
    if additional_context:
        context.update(additional_context)
    
    return context


def get_service_health_status(error: IntegrationError) -> str:
    """
    Determine service health status based on integration error.
    
    Args:
        error: The integration error to analyze
        
    Returns:
        Service health status string
    """
    if isinstance(error, CircuitBreakerError):
        return f"degraded_{error.circuit_state}"
    elif isinstance(error, APIConnectionError):
        return "unavailable"
    elif isinstance(error, APIRateLimitError):
        return "throttled"
    elif isinstance(error, APIAuthenticationError):
        return "authentication_required"
    elif isinstance(error, IntegrationTimeoutError):
        return "slow_response"
    elif isinstance(error, IntegrationQuotaError):
        return "quota_exceeded"
    elif isinstance(error, IntegrationConfigError):
        return "misconfigured"
    else:
        return "unknown_issue"


# ============ MODULE METADATA ============

__version__ = '2.0.0'
__description__ = 'Integration and external service exceptions for D&D Creative Content Framework'
__author__ = 'D&D Character Creator Backend6'

# Clean Architecture compliance metadata
CLEAN_ARCHITECTURE_COMPLIANCE = {
    "layer": "core/exceptions",
    "dependencies": ["core/enums", "core/exceptions/base"],
    "dependents": ["domain/services", "application/use_cases", "infrastructure"],
    "infrastructure_independent": True,
    "focuses_on": "D&D integration and external service business rules"
}

# Exception statistics
EXCEPTION_STATISTICS = {
    "base_integration_exceptions": 2,
    "api_integration_exceptions": 5,
    "service_provider_exceptions": 4,
    "data_synchronization_exceptions": 3,
    "webhook_realtime_exceptions": 3,
    "third_party_service_exceptions": 3,
    "configuration_exceptions": 3,
    "performance_exceptions": 3,
    "data_transformation_exceptions": 3,
    "total_exception_types": 29,
    "utility_functions": 8
}