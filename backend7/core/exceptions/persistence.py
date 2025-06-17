"""
Essential D&D Persistence Exception Types

Streamlined persistence-related exception handling following backend7 architecture.
Based on crude_functional.py patterns and essential-only philosophy.
"""

from typing import Optional, Dict, Any, List
from .base import DnDCharacterCreatorError

# ============ DATA PERSISTENCE EXCEPTIONS ============

class SaveError(DnDCharacterCreatorError):
    """Character data save operation failures."""
    
    def __init__(self, data_type: str, identifier: str, save_error: str, **kwargs):
        message = f"Save failed for {data_type} '{identifier}': {save_error}"
        details = {
            "data_type": data_type,
            "identifier": identifier,
            "save_error": save_error,
            **kwargs
        }
        super().__init__(message, details)
        self.data_type = data_type
        self.identifier = identifier
        self.save_error = save_error

class LoadError(DnDCharacterCreatorError):
    """Character data load operation failures."""
    
    def __init__(self, data_type: str, identifier: str, load_error: str, **kwargs):
        message = f"Load failed for {data_type} '{identifier}': {load_error}"
        details = {
            "data_type": data_type,
            "identifier": identifier,
            "load_error": load_error,
            **kwargs
        }
        super().__init__(message, details)
        self.data_type = data_type
        self.identifier = identifier
        self.load_error = load_error

class DeleteError(DnDCharacterCreatorError):
    """Character data deletion failures."""
    
    def __init__(self, data_type: str, identifier: str, delete_error: str, **kwargs):
        message = f"Delete failed for {data_type} '{identifier}': {delete_error}"
        details = {
            "data_type": data_type,
            "identifier": identifier,
            "delete_error": delete_error,
            **kwargs
        }
        super().__init__(message, details)
        self.data_type = data_type
        self.identifier = identifier

# ============ STORAGE SYSTEM EXCEPTIONS ============

class StorageConnectionError(DnDCharacterCreatorError):
    """Storage system connection failures."""
    
    def __init__(self, storage_type: str, connection_error: str, **kwargs):
        message = f"Storage connection failed: {storage_type} - {connection_error}"
        details = {
            "storage_type": storage_type,
            "connection_error": connection_error,
            **kwargs
        }
        super().__init__(message, details)
        self.storage_type = storage_type
        self.connection_error = connection_error

class StorageCapacityError(DnDCharacterCreatorError):
    """Storage capacity or quota exceeded."""
    
    def __init__(self, storage_type: str, used_capacity: int, max_capacity: int, **kwargs):
        message = f"Storage capacity exceeded: {storage_type} {used_capacity}/{max_capacity}"
        details = {
            "storage_type": storage_type,
            "used_capacity": used_capacity,
            "max_capacity": max_capacity,
            **kwargs
        }
        super().__init__(message, details)
        self.storage_type = storage_type
        self.used_capacity = used_capacity
        self.max_capacity = max_capacity

class StoragePermissionError(DnDCharacterCreatorError):
    """Storage permission or access rights failures."""
    
    def __init__(self, operation: str, resource: str, permission_error: str, **kwargs):
        message = f"Storage permission denied: {operation} on {resource} - {permission_error}"
        details = {
            "operation": operation,
            "resource": resource,
            "permission_error": permission_error,
            **kwargs
        }
        super().__init__(message, details)
        self.operation = operation
        self.resource = resource

# ============ DATA INTEGRITY EXCEPTIONS ============

class DataCorruptionError(DnDCharacterCreatorError):
    """Data corruption detected during persistence operations."""
    
    def __init__(self, data_source: str, corruption_type: str, **kwargs):
        message = f"Data corruption detected in {data_source}: {corruption_type}"
        details = {
            "data_source": data_source,
            "corruption_type": corruption_type,
            **kwargs
        }
        super().__init__(message, details)
        self.data_source = data_source
        self.corruption_type = corruption_type

class VersionConflictError(DnDCharacterCreatorError):
    """Version conflict during concurrent data modifications."""
    
    def __init__(self, resource: str, current_version: str, attempted_version: str, **kwargs):
        message = f"Version conflict for {resource}: current v{current_version}, attempted v{attempted_version}"
        details = {
            "resource": resource,
            "current_version": current_version,
            "attempted_version": attempted_version,
            **kwargs
        }
        super().__init__(message, details)
        self.resource = resource
        self.current_version = current_version
        self.attempted_version = attempted_version

class TransactionError(DnDCharacterCreatorError):
    """Database transaction failures."""
    
    def __init__(self, transaction_type: str, transaction_error: str, **kwargs):
        message = f"Transaction failed: {transaction_type} - {transaction_error}"
        details = {
            "transaction_type": transaction_type,
            "transaction_error": transaction_error,
            **kwargs
        }
        super().__init__(message, details)
        self.transaction_type = transaction_type
        self.transaction_error = transaction_error

# ============ CACHE EXCEPTIONS ============

class CacheError(DnDCharacterCreatorError):
    """Cache system operation failures."""
    
    def __init__(self, cache_operation: str, cache_key: str, cache_error: str, **kwargs):
        message = f"Cache {cache_operation} failed for key '{cache_key}': {cache_error}"
        details = {
            "cache_operation": cache_operation,
            "cache_key": cache_key,
            "cache_error": cache_error,
            **kwargs
        }
        super().__init__(message, details)
        self.cache_operation = cache_operation
        self.cache_key = cache_key

# ============ UTILITY FUNCTIONS ============

def create_save_error(data_type: str, identifier: str, error: str) -> SaveError:
    """Factory function for save errors."""
    return SaveError(data_type, identifier, error)

def create_load_error(data_type: str, identifier: str, error: str) -> LoadError:
    """Factory function for load errors."""
    return LoadError(data_type, identifier, error)

def create_storage_connection_error(storage_type: str, error: str) -> StorageConnectionError:
    """Factory function for storage connection errors."""
    return StorageConnectionError(storage_type, error)

def is_retryable_persistence_error(error: DnDCharacterCreatorError) -> bool:
    """Check if persistence error can be retried."""
    retryable_types = [
        SaveError,
        LoadError,
        StorageConnectionError,
        TransactionError,
        CacheError
    ]
    return any(isinstance(error, error_type) for error_type in retryable_types)

def is_data_integrity_issue(error: DnDCharacterCreatorError) -> bool:
    """Check if error indicates data integrity problems."""
    integrity_types = [
        DataCorruptionError,
        VersionConflictError,
        TransactionError
    ]
    return any(isinstance(error, error_type) for error_type in integrity_types)

def requires_admin_intervention(error: DnDCharacterCreatorError) -> bool:
    """Check if persistence error requires administrator intervention."""
    admin_types = [
        StorageCapacityError,
        StoragePermissionError,
        DataCorruptionError
    ]
    return any(isinstance(error, error_type) for error_type in admin_types)

def get_persistence_error_severity(error: DnDCharacterCreatorError) -> str:
    """Get persistence error severity level."""
    severity_map = {
        SaveError: "error",
        LoadError: "error",
        DeleteError: "error",
        StorageConnectionError: "critical",
        StorageCapacityError: "critical",
        StoragePermissionError: "error",
        DataCorruptionError: "critical",
        VersionConflictError: "warning",
        TransactionError: "error",
        CacheError: "warning"
    }
    return severity_map.get(type(error), "error")

# ============ ESSENTIAL EXPORTS ============

__all__ = [
    # Data persistence exceptions
    'SaveError',
    'LoadError',
    'DeleteError',
    
    # Storage system exceptions
    'StorageConnectionError',
    'StorageCapacityError',
    'StoragePermissionError',
    
    # Data integrity exceptions
    'DataCorruptionError',
    'VersionConflictError',
    'TransactionError',
    
    # Cache exceptions
    'CacheError',
    
    # Utility functions
    'create_save_error',
    'create_load_error',
    'create_storage_connection_error',
    'is_retryable_persistence_error',
    'is_data_integrity_issue',
    'requires_admin_intervention',
    'get_persistence_error_severity',
]

# ============ MODULE METADATA ============

__version__ = '1.0.0'
__description__ = 'Essential D&D persistence exception handling'
__author__ = 'D&D Character Creator Backend7'

# Backend7 architecture compliance
BACKEND7_COMPLIANCE = {
    "layer": "core/exceptions",
    "focus": "persistence_error_handling_only",
    "line_target": 150,
    "dependencies": ["base"],
    "philosophy": "crude_functional_inspired_simple_persistence_exceptions"
}