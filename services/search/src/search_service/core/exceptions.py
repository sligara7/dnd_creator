from datetime import datetime
from typing import Any, Dict, List, Optional


class SearchServiceError(Exception):
    """Base exception for Search Service errors"""

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


class ValidationError(SearchServiceError):
    """Validation error"""

    def __init__(
        self,
        message: str,
        field: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        details = details or {}
        details["field"] = field
        super().__init__(
            message=f"Validation error: {message}",
            error_code="VALIDATION_ERROR",
            status_code=400,
            details=details,
        )


class IndexingError(SearchServiceError):
    """Indexing operation error"""

    def __init__(
        self,
        message: str,
        document_id: str,
        index: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        details = details or {}
        details.update({
            "document_id": document_id,
            "index": index,
        })
        super().__init__(
            message=f"Indexing error: {message}",
            error_code="INDEXING_ERROR",
            status_code=500,
            details=details,
        )


class SearchError(SearchServiceError):
    """Search operation error"""

    def __init__(
        self,
        message: str,
        query: str,
        index: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        details = details or {}
        details.update({
            "query": query,
            "index": index,
        })
        super().__init__(
            message=f"Search error: {message}",
            error_code="SEARCH_ERROR",
            status_code=500,
            details=details,
        )


class IndexNotFoundError(SearchServiceError):
    """Index not found error"""

    def __init__(self, index: str):
        super().__init__(
            message=f"Index not found: {index}",
            error_code="INDEX_NOT_FOUND",
            status_code=404,
            details={"index": index},
        )


class DocumentNotFoundError(SearchServiceError):
    """Document not found error"""

    def __init__(self, document_id: str, index: str):
        super().__init__(
            message=f"Document {document_id} not found in index {index}",
            error_code="DOCUMENT_NOT_FOUND",
            status_code=404,
            details={
                "document_id": document_id,
                "index": index,
            },
        )


class ElasticsearchError(SearchServiceError):
    """Elasticsearch client error"""

    def __init__(
        self,
        message: str,
        operation: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        details = details or {}
        details["operation"] = operation
        super().__init__(
            message=f"Elasticsearch error during {operation}: {message}",
            error_code="ELASTICSEARCH_ERROR",
            status_code=500,
            details=details,
        )


class CacheError(SearchServiceError):
    """Cache operation error"""

    def __init__(
        self,
        message: str,
        operation: str,
        key: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        details = details or {}
        details.update({
            "operation": operation,
            "key": key,
        })
        super().__init__(
            message=f"Cache error during {operation}: {message}",
            error_code="CACHE_ERROR",
            status_code=500,
            details=details,
        )


class InvalidQueryError(SearchServiceError):
    """Invalid query error"""

    def __init__(
        self,
        message: str,
        query: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        details = details or {}
        details["query"] = query
        super().__init__(
            message=f"Invalid query: {message}",
            error_code="INVALID_QUERY",
            status_code=400,
            details=details,
        )


class ResourceError(SearchServiceError):
    """Resource error"""

    def __init__(
        self,
        message: str,
        resource: str,
        limit: int,
        current: int,
        details: Optional[Dict[str, Any]] = None,
    ):
        details = details or {}
        details.update({
            "resource": resource,
            "limit": limit,
            "current": current,
        })
        super().__init__(
            message=f"Resource error: {message}",
            error_code="RESOURCE_ERROR",
            status_code=429,
            details=details,
        )


class ConfigurationError(SearchServiceError):
    """Configuration error"""

    def __init__(
        self,
        message: str,
        setting: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        details = details or {}
        details["setting"] = setting
        super().__init__(
            message=f"Configuration error: {message}",
            error_code="CONFIGURATION_ERROR",
            status_code=500,
            details=details,
        )
