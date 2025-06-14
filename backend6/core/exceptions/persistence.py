"""
Data Persistence and Repository Exceptions for the D&D Creative Content Framework.

This module defines exceptions related to data persistence failures, repository
operation errors, database connectivity issues, and data integrity violations.
These exceptions represent business rule violations and failure states in the
data persistence and repository domain.

Following Clean Architecture principles, these exceptions are:
- Infrastructure-independent (don't depend on specific database implementations)
- Focused on D&D data persistence and repository business rules
- Designed for proper error handling and recovery strategies
- Aligned with the domain entity persistence and data integrity workflow
"""

from typing import Dict, List, Optional, Any, Union, Type
from datetime import datetime
from ..enums.persistence_types import PersistenceOperation, RepositoryType, DataIntegrityLevel, TransactionState
from ..enums.content_types import ContentType
from ..enums.validation_types import ValidationSeverity
from .base import DnDFrameworkError, ValidationError, DataIntegrityError


# ============ BASE PERSISTENCE EXCEPTIONS ============

class PersistenceError(DnDFrameworkError):
    """Base exception for all data persistence and repository errors."""
    
    def __init__(
        self,
        message: str,
        operation: Optional[PersistenceOperation] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        repository_type: Optional[RepositoryType] = None,
        persistence_context: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.operation = operation
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.repository_type = repository_type
        self.persistence_context = persistence_context or {}
    
    def _generate_error_code(self) -> str:
        """Generate persistence-specific error code."""
        base_code = "PER"
        operation_code = self.operation.value[:3].upper() if self.operation else "GEN"
        timestamp_code = str(int(self.timestamp.timestamp()))[-6:]
        return f"{base_code}_{operation_code}_{timestamp_code}"
    
    def get_category(self) -> str:
        """Persistence error category."""
        return "persistence"
    
    def is_retryable(self) -> bool:
        """Most persistence errors are retryable."""
        return True
    
    def should_fail_fast(self) -> bool:
        """Persistence errors don't fail fast by default."""
        return False
    
    def __str__(self) -> str:
        parts = [super().__str__()]
        
        if self.operation:
            parts.append(f"Operation: {self.operation.value}")
        
        if self.entity_type:
            parts.append(f"Entity: {self.entity_type}")
            if self.entity_id:
                parts.append(f"ID: {self.entity_id}")
        
        if self.repository_type:
            parts.append(f"Repository: {self.repository_type.value}")
        
        return " | ".join(parts)


class RepositoryError(PersistenceError):
    """Base exception for repository operation failures."""
    
    def __init__(
        self,
        message: str,
        repository_name: Optional[str] = None,
        repository_method: Optional[str] = None,
        method_parameters: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.repository_name = repository_name
        self.repository_method = repository_method
        self.method_parameters = method_parameters or {}
    
    def get_category(self) -> str:
        return "repository"
    
    def __str__(self) -> str:
        parts = [super().__str__()]
        
        if self.repository_name:
            parts.append(f"Repository: {self.repository_name}")
        
        if self.repository_method:
            parts.append(f"Method: {self.repository_method}")
        
        return " | ".join(parts)


# ============ DATABASE CONNECTION EXCEPTIONS ============

class DatabaseConnectionError(PersistenceError):
    """Exception for database connection failures."""
    
    def __init__(
        self,
        connection_issue: str,
        database_type: Optional[str] = None,
        connection_string: Optional[str] = None,
        connection_timeout: Optional[float] = None,
        retry_count: Optional[int] = None,
        **kwargs
    ):
        message = f"Database connection failed: {connection_issue}"
        if database_type:
            message += f" (type: {database_type})"
        
        super().__init__(
            message,
            operation=PersistenceOperation.CONNECT,
            **kwargs
        )
        self.connection_issue = connection_issue
        self.database_type = database_type
        self.connection_string = connection_string
        self.connection_timeout = connection_timeout
        self.retry_count = retry_count or 0
    
    def get_category(self) -> str:
        return "database_connection"
    
    def is_retryable(self) -> bool:
        """Connection errors are generally retryable."""
        return True


class DatabaseUnavailableError(DatabaseConnectionError):
    """Exception for database service unavailability."""
    
    def __init__(
        self,
        database_name: str,
        unavailability_reason: str,
        estimated_recovery_time: Optional[datetime] = None,
        alternative_sources: Optional[List[str]] = None,
        **kwargs
    ):
        connection_issue = f"Database '{database_name}' unavailable: {unavailability_reason}"
        super().__init__(
            connection_issue=connection_issue,
            **kwargs
        )
        self.database_name = database_name
        self.unavailability_reason = unavailability_reason
        self.estimated_recovery_time = estimated_recovery_time
        self.alternative_sources = alternative_sources or []
    
    def get_category(self) -> str:
        return "database_unavailable"


class ConnectionPoolExhaustedError(DatabaseConnectionError):
    """Exception for database connection pool exhaustion."""
    
    def __init__(
        self,
        pool_size: int,
        active_connections: int,
        queue_size: Optional[int] = None,
        wait_timeout: Optional[float] = None,
        **kwargs
    ):
        connection_issue = f"Connection pool exhausted: {active_connections}/{pool_size} connections in use"
        if queue_size:
            connection_issue += f", {queue_size} waiting"
        
        super().__init__(
            connection_issue=connection_issue,
            **kwargs
        )
        self.pool_size = pool_size
        self.active_connections = active_connections
        self.queue_size = queue_size
        self.wait_timeout = wait_timeout
    
    def get_category(self) -> str:
        return "connection_pool_exhausted"


# ============ ENTITY NOT FOUND EXCEPTIONS ============

class EntityNotFoundError(RepositoryError):
    """Exception for entity not found errors."""
    
    def __init__(
        self,
        entity_type: str,
        entity_identifier: Union[str, int, Dict[str, Any]],
        search_criteria: Optional[Dict[str, Any]] = None,
        suggested_alternatives: Optional[List[str]] = None,
        **kwargs
    ):
        if isinstance(entity_identifier, dict):
            identifier_str = ", ".join([f"{k}={v}" for k, v in entity_identifier.items()])
        else:
            identifier_str = str(entity_identifier)
        
        message = f"{entity_type} not found: {identifier_str}"
        
        super().__init__(
            message,
            operation=PersistenceOperation.READ,
            entity_type=entity_type,
            entity_id=str(entity_identifier),
            **kwargs
        )
        self.entity_identifier = entity_identifier
        self.search_criteria = search_criteria or {}
        self.suggested_alternatives = suggested_alternatives or []
    
    def get_category(self) -> str:
        return "entity_not_found"
    
    def is_retryable(self) -> bool:
        """Entity not found errors are generally not retryable."""
        return False


class CharacterNotFoundError(EntityNotFoundError):
    """Exception for character not found errors."""
    
    def __init__(
        self,
        character_identifier: Union[str, int],
        owner_id: Optional[str] = None,
        campaign_id: Optional[str] = None,
        **kwargs
    ):
        search_criteria = {}
        if owner_id:
            search_criteria["owner_id"] = owner_id
        if campaign_id:
            search_criteria["campaign_id"] = campaign_id
        
        super().__init__(
            entity_type="Character",
            entity_identifier=character_identifier,
            search_criteria=search_criteria,
            **kwargs
        )
        self.character_identifier = character_identifier
        self.owner_id = owner_id
        self.campaign_id = campaign_id
    
    def get_category(self) -> str:
        return "character_not_found"


class CampaignNotFoundError(EntityNotFoundError):
    """Exception for campaign not found errors."""
    
    def __init__(
        self,
        campaign_identifier: Union[str, int],
        owner_id: Optional[str] = None,
        **kwargs
    ):
        search_criteria = {}
        if owner_id:
            search_criteria["owner_id"] = owner_id
        
        super().__init__(
            entity_type="Campaign",
            entity_identifier=campaign_identifier,
            search_criteria=search_criteria,
            **kwargs
        )
        self.campaign_identifier = campaign_identifier
        self.owner_id = owner_id
    
    def get_category(self) -> str:
        return "campaign_not_found"


class UserNotFoundError(EntityNotFoundError):
    """Exception for user not found errors."""
    
    def __init__(
        self,
        user_identifier: Union[str, int],
        identifier_type: str = "id",
        **kwargs
    ):
        super().__init__(
            entity_type="User",
            entity_identifier=user_identifier,
            search_criteria={"identifier_type": identifier_type},
            **kwargs
        )
        self.user_identifier = user_identifier
        self.identifier_type = identifier_type
    
    def get_category(self) -> str:
        return "user_not_found"


class ContentNotFoundError(EntityNotFoundError):
    """Exception for custom content not found errors."""
    
    def __init__(
        self,
        content_identifier: Union[str, int],
        content_type: Optional[ContentType] = None,
        author_id: Optional[str] = None,
        **kwargs
    ):
        search_criteria = {}
        if content_type:
            search_criteria["content_type"] = content_type.value
        if author_id:
            search_criteria["author_id"] = author_id
        
        super().__init__(
            entity_type="Content",
            entity_identifier=content_identifier,
            search_criteria=search_criteria,
            **kwargs
        )
        self.content_identifier = content_identifier
        self.content_type = content_type
        self.author_id = author_id
    
    def get_category(self) -> str:
        return "content_not_found"


# ============ DATA INTEGRITY VIOLATION EXCEPTIONS ============

class PersistenceDataIntegrityError(DataIntegrityError):
    """Exception for data integrity violations during persistence operations."""
    
    def __init__(
        self,
        integrity_violation: str,
        entity_type: Optional[str] = None,
        entity_data: Optional[Dict[str, Any]] = None,
        integrity_level: DataIntegrityLevel = DataIntegrityLevel.STRICT,
        violated_constraints: Optional[List[str]] = None,
        **kwargs
    ):
        super().__init__(
            integrity_type="persistence_integrity",
            integrity_description=integrity_violation,
            data_state=entity_data,
            **kwargs
        )
        self.entity_type = entity_type
        self.entity_data = entity_data or {}
        self.integrity_level = integrity_level
        self.violated_constraints = violated_constraints or []
    
    def get_category(self) -> str:
        return "persistence_data_integrity"
    
    def should_fail_fast(self) -> bool:
        """High integrity levels should fail fast."""
        return self.integrity_level in [DataIntegrityLevel.STRICT, DataIntegrityLevel.CRITICAL]


class ForeignKeyViolationError(PersistenceDataIntegrityError):
    """Exception for foreign key constraint violations."""
    
    def __init__(
        self,
        foreign_key_field: str,
        foreign_key_value: Any,
        referenced_table: str,
        referenced_field: str,
        **kwargs
    ):
        integrity_violation = f"Foreign key violation: {foreign_key_field}={foreign_key_value} not found in {referenced_table}.{referenced_field}"
        super().__init__(
            integrity_violation=integrity_violation,
            violated_constraints=[f"FK_{foreign_key_field}"],
            **kwargs
        )
        self.foreign_key_field = foreign_key_field
        self.foreign_key_value = foreign_key_value
        self.referenced_table = referenced_table
        self.referenced_field = referenced_field
    
    def get_category(self) -> str:
        return "foreign_key_violation"


class UniqueConstraintViolationError(PersistenceDataIntegrityError):
    """Exception for unique constraint violations."""
    
    def __init__(
        self,
        constraint_name: str,
        conflicting_fields: List[str],
        conflicting_values: Dict[str, Any],
        existing_entity_id: Optional[str] = None,
        **kwargs
    ):
        field_values = ", ".join([f"{field}={conflicting_values.get(field)}" for field in conflicting_fields])
        integrity_violation = f"Unique constraint violation on {constraint_name}: {field_values}"
        if existing_entity_id:
            integrity_violation += f" (conflicts with entity {existing_entity_id})"
        
        super().__init__(
            integrity_violation=integrity_violation,
            violated_constraints=[constraint_name],
            **kwargs
        )
        self.constraint_name = constraint_name
        self.conflicting_fields = conflicting_fields
        self.conflicting_values = conflicting_values
        self.existing_entity_id = existing_entity_id
    
    def get_category(self) -> str:
        return "unique_constraint_violation"


class CheckConstraintViolationError(PersistenceDataIntegrityError):
    """Exception for check constraint violations."""
    
    def __init__(
        self,
        constraint_name: str,
        constraint_condition: str,
        violating_data: Dict[str, Any],
        **kwargs
    ):
        integrity_violation = f"Check constraint violation on {constraint_name}: {constraint_condition}"
        super().__init__(
            integrity_violation=integrity_violation,
            violated_constraints=[constraint_name],
            entity_data=violating_data,
            **kwargs
        )
        self.constraint_name = constraint_name
        self.constraint_condition = constraint_condition
        self.violating_data = violating_data
    
    def get_category(self) -> str:
        return "check_constraint_violation"


class OptimisticLockingError(PersistenceDataIntegrityError):
    """Exception for optimistic locking conflicts."""
    
    def __init__(
        self,
        entity_type: str,
        entity_id: str,
        expected_version: Union[int, str],
        actual_version: Union[int, str],
        conflicting_user: Optional[str] = None,
        last_modified: Optional[datetime] = None,
        **kwargs
    ):
        integrity_violation = f"Optimistic locking conflict for {entity_type} {entity_id}: expected version {expected_version}, found {actual_version}"
        if conflicting_user:
            integrity_violation += f" (modified by {conflicting_user})"
        
        super().__init__(
            integrity_violation=integrity_violation,
            entity_type=entity_type,
            **kwargs
        )
        self.entity_id = entity_id
        self.expected_version = expected_version
        self.actual_version = actual_version
        self.conflicting_user = conflicting_user
        self.last_modified = last_modified
    
    def get_category(self) -> str:
        return "optimistic_locking"
    
    def is_retryable(self) -> bool:
        """Optimistic locking errors are retryable after refreshing data."""
        return True


# ============ REPOSITORY OPERATION EXCEPTIONS ============

class RepositoryOperationError(RepositoryError):
    """Exception for specific repository operation failures."""
    
    def __init__(
        self,
        operation: PersistenceOperation,
        operation_issue: str,
        affected_entities: Optional[List[str]] = None,
        operation_parameters: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        message = f"Repository {operation.value} operation failed: {operation_issue}"
        if affected_entities:
            message += f" (affects: {', '.join(affected_entities)})"
        
        super().__init__(
            message,
            operation=operation,
            method_parameters=operation_parameters,
            **kwargs
        )
        self.operation_issue = operation_issue
        self.affected_entities = affected_entities or []
        self.operation_parameters = operation_parameters or {}
    
    def get_category(self) -> str:
        return "repository_operation"


class CreateOperationError(RepositoryOperationError):
    """Exception for entity creation failures."""
    
    def __init__(
        self,
        entity_type: str,
        creation_issue: str,
        entity_data: Optional[Dict[str, Any]] = None,
        validation_errors: Optional[List[str]] = None,
        **kwargs
    ):
        super().__init__(
            operation=PersistenceOperation.CREATE,
            operation_issue=f"Failed to create {entity_type}: {creation_issue}",
            entity_type=entity_type,
            operation_parameters=entity_data,
            **kwargs
        )
        self.creation_issue = creation_issue
        self.entity_data = entity_data or {}
        self.validation_errors = validation_errors or []
    
    def get_category(self) -> str:
        return "create_operation"


class UpdateOperationError(RepositoryOperationError):
    """Exception for entity update failures."""
    
    def __init__(
        self,
        entity_type: str,
        entity_id: str,
        update_issue: str,
        update_data: Optional[Dict[str, Any]] = None,
        changed_fields: Optional[List[str]] = None,
        **kwargs
    ):
        super().__init__(
            operation=PersistenceOperation.UPDATE,
            operation_issue=f"Failed to update {entity_type} {entity_id}: {update_issue}",
            entity_type=entity_type,
            entity_id=entity_id,
            operation_parameters=update_data,
            **kwargs
        )
        self.update_issue = update_issue
        self.update_data = update_data or {}
        self.changed_fields = changed_fields or []
    
    def get_category(self) -> str:
        return "update_operation"


class DeleteOperationError(RepositoryOperationError):
    """Exception for entity deletion failures."""
    
    def __init__(
        self,
        entity_type: str,
        entity_id: str,
        deletion_issue: str,
        cascade_entities: Optional[List[str]] = None,
        blocking_references: Optional[List[str]] = None,
        **kwargs
    ):
        super().__init__(
            operation=PersistenceOperation.DELETE,
            operation_issue=f"Failed to delete {entity_type} {entity_id}: {deletion_issue}",
            entity_type=entity_type,
            entity_id=entity_id,
            **kwargs
        )
        self.deletion_issue = deletion_issue
        self.cascade_entities = cascade_entities or []
        self.blocking_references = blocking_references or []
    
    def get_category(self) -> str:
        return "delete_operation"


class QueryOperationError(RepositoryOperationError):
    """Exception for query operation failures."""
    
    def __init__(
        self,
        query_type: str,
        query_issue: str,
        query_parameters: Optional[Dict[str, Any]] = None,
        query_filters: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(
            operation=PersistenceOperation.QUERY,
            operation_issue=f"Query {query_type} failed: {query_issue}",
            operation_parameters=query_parameters,
            **kwargs
        )
        self.query_type = query_type
        self.query_issue = query_issue
        self.query_parameters = query_parameters or {}
        self.query_filters = query_filters or {}
    
    def get_category(self) -> str:
        return "query_operation"


class BulkOperationError(RepositoryOperationError):
    """Exception for bulk operation failures."""
    
    def __init__(
        self,
        bulk_operation: str,
        total_items: int,
        failed_items: int,
        partial_success: bool = False,
        failed_item_details: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ):
        operation_issue = f"Bulk {bulk_operation} failed: {failed_items}/{total_items} items failed"
        if partial_success:
            operation_issue += " (partial success)"
        
        super().__init__(
            operation=PersistenceOperation.BULK,
            operation_issue=operation_issue,
            **kwargs
        )
        self.bulk_operation = bulk_operation
        self.total_items = total_items
        self.failed_items = failed_items
        self.partial_success = partial_success
        self.failed_item_details = failed_item_details or []
    
    def get_category(self) -> str:
        return "bulk_operation"
    
    def is_retryable(self) -> bool:
        """Bulk operations might be retryable for failed items only."""
        return self.partial_success and self.failed_items < self.total_items


# ============ TRANSACTION MANAGEMENT EXCEPTIONS ============

class TransactionError(PersistenceError):
    """Exception for transaction management failures."""
    
    def __init__(
        self,
        transaction_issue: str,
        transaction_state: Optional[TransactionState] = None,
        transaction_id: Optional[str] = None,
        involved_operations: Optional[List[str]] = None,
        **kwargs
    ):
        message = f"Transaction failed: {transaction_issue}"
        if transaction_id:
            message += f" (ID: {transaction_id})"
        
        super().__init__(
            message,
            operation=PersistenceOperation.TRANSACTION,
            **kwargs
        )
        self.transaction_issue = transaction_issue
        self.transaction_state = transaction_state
        self.transaction_id = transaction_id
        self.involved_operations = involved_operations or []
    
    def get_category(self) -> str:
        return "transaction"


class TransactionRollbackError(TransactionError):
    """Exception for transaction rollback failures."""
    
    def __init__(
        self,
        rollback_reason: str,
        completed_operations: Optional[List[str]] = None,
        rollback_operations: Optional[List[str]] = None,
        **kwargs
    ):
        transaction_issue = f"Transaction rolled back: {rollback_reason}"
        super().__init__(
            transaction_issue=transaction_issue,
            transaction_state=TransactionState.ROLLED_BACK,
            **kwargs
        )
        self.rollback_reason = rollback_reason
        self.completed_operations = completed_operations or []
        self.rollback_operations = rollback_operations or []
    
    def get_category(self) -> str:
        return "transaction_rollback"


class TransactionTimeoutError(TransactionError):
    """Exception for transaction timeout failures."""
    
    def __init__(
        self,
        timeout_duration: float,
        pending_operations: Optional[List[str]] = None,
        **kwargs
    ):
        transaction_issue = f"Transaction timed out after {timeout_duration} seconds"
        super().__init__(
            transaction_issue=transaction_issue,
            transaction_state=TransactionState.TIMED_OUT,
            **kwargs
        )
        self.timeout_duration = timeout_duration
        self.pending_operations = pending_operations or []
    
    def get_category(self) -> str:
        return "transaction_timeout"
    
    def is_retryable(self) -> bool:
        """Transaction timeouts are generally retryable."""
        return True


class DeadlockError(TransactionError):
    """Exception for database deadlock situations."""
    
    def __init__(
        self,
        deadlock_details: str,
        involved_tables: Optional[List[str]] = None,
        involved_transactions: Optional[List[str]] = None,
        **kwargs
    ):
        transaction_issue = f"Deadlock detected: {deadlock_details}"
        super().__init__(
            transaction_issue=transaction_issue,
            transaction_state=TransactionState.DEADLOCKED,
            **kwargs
        )
        self.deadlock_details = deadlock_details
        self.involved_tables = involved_tables or []
        self.involved_transactions = involved_transactions or []
    
    def get_category(self) -> str:
        return "deadlock"
    
    def is_retryable(self) -> bool:
        """Deadlocks are retryable after a delay."""
        return True


# ============ REPOSITORY CONFIGURATION EXCEPTIONS ============

class RepositoryConfigurationError(RepositoryError):
    """Exception for repository configuration issues."""
    
    def __init__(
        self,
        config_issue: str,
        repository_name: Optional[str] = None,
        config_key: Optional[str] = None,
        config_value: Optional[Any] = None,
        **kwargs
    ):
        message = f"Repository configuration error: {config_issue}"
        if repository_name:
            message += f" (repository: {repository_name})"
        
        super().__init__(
            message,
            repository_name=repository_name,
            **kwargs
        )
        self.config_issue = config_issue
        self.config_key = config_key
        self.config_value = config_value
    
    def get_category(self) -> str:
        return "repository_configuration"
    
    def should_fail_fast(self) -> bool:
        """Configuration errors should fail fast."""
        return True


class RepositoryInitializationError(RepositoryError):
    """Exception for repository initialization failures."""
    
    def __init__(
        self,
        initialization_issue: str,
        repository_type: Optional[RepositoryType] = None,
        dependencies: Optional[List[str]] = None,
        **kwargs
    ):
        message = f"Repository initialization failed: {initialization_issue}"
        if repository_type:
            message += f" (type: {repository_type.value})"
        
        super().__init__(
            message,
            repository_type=repository_type,
            **kwargs
        )
        self.initialization_issue = initialization_issue
        self.dependencies = dependencies or []
    
    def get_category(self) -> str:
        return "repository_initialization"
    
    def should_fail_fast(self) -> bool:
        """Initialization errors should fail fast."""
        return True


# ============ DATA MIGRATION EXCEPTIONS ============

class DataMigrationError(PersistenceError):
    """Exception for data migration failures."""
    
    def __init__(
        self,
        migration_name: str,
        migration_issue: str,
        source_version: Optional[str] = None,
        target_version: Optional[str] = None,
        affected_tables: Optional[List[str]] = None,
        **kwargs
    ):
        message = f"Data migration '{migration_name}' failed: {migration_issue}"
        if source_version and target_version:
            message += f" (from {source_version} to {target_version})"
        
        super().__init__(
            message,
            operation=PersistenceOperation.MIGRATE,
            **kwargs
        )
        self.migration_name = migration_name
        self.migration_issue = migration_issue
        self.source_version = source_version
        self.target_version = target_version
        self.affected_tables = affected_tables or []
    
    def get_category(self) -> str:
        return "data_migration"


class MigrationRollbackError(DataMigrationError):
    """Exception for migration rollback failures."""
    
    def __init__(
        self,
        migration_name: str,
        rollback_reason: str,
        completed_steps: Optional[List[str]] = None,
        failed_rollback_steps: Optional[List[str]] = None,
        **kwargs
    ):
        migration_issue = f"Migration rollback failed: {rollback_reason}"
        super().__init__(
            migration_name=migration_name,
            migration_issue=migration_issue,
            **kwargs
        )
        self.rollback_reason = rollback_reason
        self.completed_steps = completed_steps or []
        self.failed_rollback_steps = failed_rollback_steps or []
    
    def get_category(self) -> str:
        return "migration_rollback"
    
    def should_fail_fast(self) -> bool:
        """Migration rollback failures should fail fast."""
        return True


# ============ UTILITY FUNCTIONS FOR PERSISTENCE EXCEPTION HANDLING ============

def categorize_persistence_error(error: Exception) -> str:
    """
    Categorize a persistence error for handling and routing.
    
    Args:
        error: The exception to categorize
        
    Returns:
        Error category string
    """
    if isinstance(error, DatabaseConnectionError):
        return "database_connection"
    elif isinstance(error, EntityNotFoundError):
        return "entity_not_found"
    elif isinstance(error, PersistenceDataIntegrityError):
        return "data_integrity"
    elif isinstance(error, TransactionError):
        return "transaction"
    elif isinstance(error, RepositoryOperationError):
        return "repository_operation"
    elif isinstance(error, RepositoryConfigurationError):
        return "repository_configuration"
    elif isinstance(error, DataMigrationError):
        return "data_migration"
    elif isinstance(error, RepositoryError):
        return "repository"
    elif isinstance(error, PersistenceError):
        return "general_persistence"
    else:
        return "unknown"


def is_retryable_persistence_error(error: PersistenceError) -> bool:
    """
    Determine if a persistence error is retryable.
    
    Args:
        error: The persistence error to check
        
    Returns:
        True if the error might succeed on retry
    """
    # Connection errors are generally retryable
    if isinstance(error, DatabaseConnectionError):
        return True
    
    # Transaction timeouts and deadlocks are retryable
    if isinstance(error, (TransactionTimeoutError, DeadlockError)):
        return True
    
    # Optimistic locking errors are retryable
    if isinstance(error, OptimisticLockingError):
        return True
    
    # Bulk operations with partial success are retryable
    if isinstance(error, BulkOperationError):
        return error.partial_success
    
    # Entity not found errors are not retryable
    if isinstance(error, EntityNotFoundError):
        return False
    
    # Constraint violations are not retryable
    if isinstance(error, (ForeignKeyViolationError, UniqueConstraintViolationError, CheckConstraintViolationError)):
        return False
    
    # Configuration errors are not retryable
    if isinstance(error, RepositoryConfigurationError):
        return False
    
    # Migration rollback errors are not retryable
    if isinstance(error, MigrationRollbackError):
        return False
    
    # Most other persistence errors are retryable
    return error.is_retryable()


def get_persistence_retry_delay(error: PersistenceError) -> Optional[int]:
    """
    Get recommended retry delay for persistence errors.
    
    Args:
        error: The persistence error
        
    Returns:
        Recommended delay in seconds, or None if not retryable
    """
    if not is_retryable_persistence_error(error):
        return None
    
    if isinstance(error, DatabaseConnectionError):
        # Exponential backoff based on retry count
        return min(2 ** (error.retry_count or 0), 60)  # Max 1 minute
    
    if isinstance(error, DeadlockError):
        # Random delay to avoid thundering herd
        import random
        return random.randint(1, 5)
    
    if isinstance(error, TransactionTimeoutError):
        # Slightly longer delay for transaction timeouts
        return 10
    
    if isinstance(error, OptimisticLockingError):
        # Short delay for optimistic locking
        return 1
    
    if isinstance(error, ConnectionPoolExhaustedError):
        # Wait for connections to become available
        return error.wait_timeout or 30
    
    # Default retry delay
    return 5


def get_persistence_recovery_suggestions(error: PersistenceError) -> List[str]:
    """
    Generate recovery suggestions for persistence errors.
    
    Args:
        error: The persistence error to analyze
        
    Returns:
        List of recovery suggestions
    """
    suggestions = list(error.recovery_suggestions)
    
    if isinstance(error, DatabaseConnectionError):
        suggestions.extend([
            "Check database service status",
            "Verify connection string and credentials",
            "Check network connectivity",
            "Review connection pool configuration"
        ])
        if error.connection_timeout:
            suggestions.append(f"Consider increasing connection timeout from {error.connection_timeout}s")
    
    elif isinstance(error, ConnectionPoolExhaustedError):
        suggestions.extend([
            f"Increase pool size from {error.pool_size}",
            "Review connection usage patterns",
            "Implement connection cleanup",
            "Monitor for connection leaks"
        ])
    
    elif isinstance(error, EntityNotFoundError):
        suggestions.extend([
            f"Verify {error.entity_type} exists with identifier: {error.entity_identifier}",
            "Check entity permissions and access rights",
            "Refresh data from authoritative source"
        ])
        if error.suggested_alternatives:
            suggestions.extend([f"Try alternative: {alt}" for alt in error.suggested_alternatives[:3]])
    
    elif isinstance(error, ForeignKeyViolationError):
        suggestions.extend([
            f"Ensure referenced entity exists in {error.referenced_table}",
            f"Create {error.referenced_table} record first",
            f"Use valid {error.foreign_key_field} value"
        ])
    
    elif isinstance(error, UniqueConstraintViolationError):
        suggestions.extend([
            f"Use unique values for {', '.join(error.conflicting_fields)}",
            "Check for duplicate data",
            "Implement conflict resolution strategy"
        ])
        if error.existing_entity_id:
            suggestions.append(f"Consider updating existing entity: {error.existing_entity_id}")
    
    elif isinstance(error, OptimisticLockingError):
        suggestions.extend([
            "Refresh entity data and retry",
            "Implement merge conflict resolution",
            "Consider pessimistic locking for critical updates"
        ])
    
    elif isinstance(error, DeadlockError):
        suggestions.extend([
            "Retry operation with random delay",
            "Review transaction ordering",
            "Minimize transaction duration",
            "Consider lock ordering strategy"
        ])
    
    elif isinstance(error, TransactionTimeoutError):
        suggestions.extend([
            f"Break operation into smaller transactions",
            f"Optimize slow operations",
            f"Increase transaction timeout from {error.timeout_duration}s"
        ])
    
    elif isinstance(error, BulkOperationError):
        suggestions.extend([
            f"Retry failed {error.failed_items} items individually",
            "Reduce batch size",
            "Implement partial retry logic"
        ])
        if error.partial_success:
            suggestions.append(f"Process {error.total_items - error.failed_items} successful items")
    
    elif isinstance(error, RepositoryConfigurationError):
        suggestions.extend([
            "Review repository configuration",
            "Check required configuration keys",
            "Validate configuration values"
        ])
        if error.config_key:
            suggestions.append(f"Configure: {error.config_key}")
    
    elif isinstance(error, DataMigrationError):
        suggestions.extend([
            "Review migration script for errors",
            "Backup data before retry",
            "Test migration on copy of data"
        ])
        if error.affected_tables:
            suggestions.extend([f"Check table: {table}" for table in error.affected_tables[:3]])
    
    return suggestions


def create_persistence_error_context(
    operation: str,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    repository_name: Optional[str] = None,
    additional_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create standardized error context for persistence operations.
    
    Args:
        operation: Name of the persistence operation
        entity_type: Type of entity being operated on
        entity_id: ID of the entity
        repository_name: Name of the repository
        additional_context: Additional context information
        
    Returns:
        Context dictionary for error reporting
    """
    context = {
        "operation": operation,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if entity_type:
        context["entity_type"] = entity_type
    
    if entity_id:
        context["entity_id"] = entity_id
    
    if repository_name:
        context["repository_name"] = repository_name
    
    if additional_context:
        context.update(additional_context)
    
    return context


def validate_entity_constraints(
    entity_type: str,
    entity_data: Dict[str, Any],
    constraints: Dict[str, Any]
) -> List[str]:
    """
    Validate entity data against constraints.
    
    Args:
        entity_type: Type of entity being validated
        entity_data: Entity data to validate
        constraints: Constraint definitions
        
    Returns:
        List of constraint violations (empty if valid)
    """
    violations = []
    
    # Check required fields
    required_fields = constraints.get("required_fields", [])
    for field in required_fields:
        if field not in entity_data or entity_data[field] is None:
            violations.append(f"Required field missing: {field}")
    
    # Check unique constraints
    unique_constraints = constraints.get("unique_constraints", [])
    for constraint in unique_constraints:
        # This would typically involve database queries to check uniqueness
        # For now, we'll just validate the constraint is defined
        constraint_fields = constraint.get("fields", [])
        for field in constraint_fields:
            if field not in entity_data:
                violations.append(f"Unique constraint field missing: {field}")
    
    # Check data types
    field_types = constraints.get("field_types", {})
    for field, expected_type in field_types.items():
        if field in entity_data and entity_data[field] is not None:
            if not isinstance(entity_data[field], expected_type):
                violations.append(f"Field {field} has wrong type: expected {expected_type.__name__}, got {type(entity_data[field]).__name__}")
    
    # Check field lengths
    field_lengths = constraints.get("field_lengths", {})
    for field, max_length in field_lengths.items():
        if field in entity_data and entity_data[field] is not None:
            if isinstance(entity_data[field], str) and len(entity_data[field]) > max_length:
                violations.append(f"Field {field} exceeds maximum length: {len(entity_data[field])} > {max_length}")
    
    return violations


def analyze_constraint_violation(error: Exception) -> Dict[str, Any]:
    """
    Analyze constraint violation errors and provide detailed information.
    
    Args:
        error: The constraint violation error
        
    Returns:
        Analysis dictionary with violation details
    """
    analysis = {
        "violation_type": "unknown",
        "severity": "medium",
        "is_recoverable": False,
        "suggested_actions": []
    }
    
    if isinstance(error, ForeignKeyViolationError):
        analysis.update({
            "violation_type": "foreign_key",
            "severity": "high",
            "is_recoverable": True,
            "suggested_actions": [
                f"Create referenced entity in {error.referenced_table}",
                f"Validate {error.foreign_key_field} value",
                "Check entity creation order"
            ],
            "violating_field": error.foreign_key_field,
            "violating_value": error.foreign_key_value,
            "referenced_table": error.referenced_table
        })
    
    elif isinstance(error, UniqueConstraintViolationError):
        analysis.update({
            "violation_type": "unique_constraint",
            "severity": "medium",
            "is_recoverable": True,
            "suggested_actions": [
                "Modify conflicting field values",
                "Check for duplicate data",
                "Implement upsert logic"
            ],
            "constraint_name": error.constraint_name,
            "conflicting_fields": error.conflicting_fields,
            "conflicting_values": error.conflicting_values
        })
    
    elif isinstance(error, CheckConstraintViolationError):
        analysis.update({
            "violation_type": "check_constraint",
            "severity": "high",
            "is_recoverable": True,
            "suggested_actions": [
                "Validate data against business rules",
                "Modify data to meet constraints",
                "Review constraint definition"
            ],
            "constraint_name": error.constraint_name,
            "constraint_condition": error.constraint_condition,
            "violating_data": error.violating_data
        })
    
    elif isinstance(error, OptimisticLockingError):
        analysis.update({
            "violation_type": "optimistic_locking",
            "severity": "medium",
            "is_recoverable": True,
            "suggested_actions": [
                "Refresh entity data",
                "Implement merge strategy",
                "Retry with latest version"
            ],
            "expected_version": error.expected_version,
            "actual_version": error.actual_version,
            "entity_type": error.entity_type,
            "entity_id": error.entity_id
        })
    
    return analysis


# ============ MODULE METADATA ============

__version__ = '2.0.0'
__description__ = 'Data persistence and repository exceptions for D&D Creative Content Framework'
__author__ = 'D&D Character Creator Backend6'

# Clean Architecture compliance metadata
CLEAN_ARCHITECTURE_COMPLIANCE = {
    "layer": "core/exceptions",
    "dependencies": ["core/enums", "core/exceptions/base"],
    "dependents": ["domain/services", "application/use_cases", "infrastructure"],
    "infrastructure_independent": True,
    "focuses_on": "D&D data persistence and repository business rules"
}

# Exception statistics
EXCEPTION_STATISTICS = {
    "base_persistence_exceptions": 2,
    "database_connection_exceptions": 3,
    "entity_not_found_exceptions": 5,
    "data_integrity_exceptions": 4,
    "repository_operation_exceptions": 6,
    "transaction_exceptions": 4,
    "configuration_exceptions": 2,
    "migration_exceptions": 2,
    "total_exception_types": 28,
    "utility_functions": 8
}