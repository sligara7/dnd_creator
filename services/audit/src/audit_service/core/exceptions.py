from datetime import datetime
from typing import Any, Dict, List, Optional


class AuditServiceError(Exception):
    """Base exception for Audit Service errors"""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.status_code = status_code
        self.details = details or {}
        self.timestamp = datetime.utcnow()


class EventProcessingError(AuditServiceError):
    """Event processing error"""

    def __init__(
        self,
        message: str,
        event_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        details = details or {}
        if event_id:
            details["event_id"] = event_id
        super().__init__(
            message=f"Event processing error: {message}",
            error_code="EVENT_PROCESSING_ERROR",
            status_code=500,
            details=details,
        )


class EventValidationError(AuditServiceError):
    """Event validation error"""

    def __init__(
        self,
        message: str,
        event_id: Optional[str] = None,
        validation_errors: Optional[List[str]] = None,
    ):
        details = {
            "validation_errors": validation_errors or [],
        }
        if event_id:
            details["event_id"] = event_id
        super().__init__(
            message=f"Event validation error: {message}",
            error_code="EVENT_VALIDATION_ERROR",
            status_code=400,
            details=details,
        )


class StorageError(AuditServiceError):
    """Storage backend error"""

    def __init__(
        self,
        backend: str,
        message: str,
        operation: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        details = details or {}
        if operation:
            details["operation"] = operation
        super().__init__(
            message=f"{backend} storage error: {message}",
            error_code="STORAGE_ERROR",
            status_code=500,
            details=details,
        )


class RetentionError(AuditServiceError):
    """Data retention error"""

    def __init__(
        self,
        message: str,
        policy: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        details = details or {}
        details["policy"] = policy
        super().__init__(
            message=f"Retention policy error: {message}",
            error_code="RETENTION_ERROR",
            status_code=500,
            details=details,
        )


class ComplianceError(AuditServiceError):
    """Compliance-related error"""

    def __init__(
        self,
        message: str,
        regulation: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        details = details or {}
        details["regulation"] = regulation
        super().__init__(
            message=f"Compliance error ({regulation}): {message}",
            error_code="COMPLIANCE_ERROR",
            status_code=400,
            details=details,
        )


class AnalysisError(AuditServiceError):
    """Analysis error"""

    def __init__(
        self,
        message: str,
        analysis_type: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        details = details or {}
        details["analysis_type"] = analysis_type
        super().__init__(
            message=f"Analysis error ({analysis_type}): {message}",
            error_code="ANALYSIS_ERROR",
            status_code=500,
            details=details,
        )


class ArchivalError(AuditServiceError):
    """Archival error"""

    def __init__(
        self,
        message: str,
        operation: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        details = details or {}
        details["operation"] = operation
        super().__init__(
            message=f"Archival error: {message}",
            error_code="ARCHIVAL_ERROR",
            status_code=500,
            details=details,
        )


class EventRoutingError(AuditServiceError):
    """Event routing error"""

    def __init__(
        self,
        message: str,
        source: str,
        event_type: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        details = details or {}
        details["source"] = source
        details["event_type"] = event_type
        super().__init__(
            message=f"Event routing error: {message}",
            error_code="ROUTING_ERROR",
            status_code=500,
            details=details,
        )


class QueryError(AuditServiceError):
    """Query error"""

    def __init__(
        self,
        message: str,
        query: Optional[Dict[str, Any]] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        details = details or {}
        if query:
            details["query"] = query
        super().__init__(
            message=f"Query error: {message}",
            error_code="QUERY_ERROR",
            status_code=400,
            details=details,
        )


class AuthorizationError(AuditServiceError):
    """Authorization error"""

    def __init__(
        self,
        message: str,
        required_permissions: Optional[List[str]] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        details = details or {}
        if required_permissions:
            details["required_permissions"] = required_permissions
        super().__init__(
            message=f"Authorization error: {message}",
            error_code="AUTHORIZATION_ERROR",
            status_code=403,
            details=details,
        )
