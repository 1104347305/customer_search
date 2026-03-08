from typing import Any, Optional


class CustomerSearchException(Exception):
    """Base exception for customer search system"""

    def __init__(self, message: str, code: str = "INTERNAL_ERROR", details: Optional[Any] = None):
        self.message = message
        self.code = code
        self.details = details
        super().__init__(self.message)


class ElasticsearchConnectionError(CustomerSearchException):
    """Elasticsearch connection error"""

    def __init__(self, message: str = "Failed to connect to Elasticsearch", details: Optional[Any] = None):
        super().__init__(message, code="ES_CONNECTION_ERROR", details=details)


class InvalidQueryError(CustomerSearchException):
    """Invalid query parameters"""

    def __init__(self, message: str = "Invalid query parameters", details: Optional[Any] = None):
        super().__init__(message, code="INVALID_QUERY", details=details)


class DataNotFoundError(CustomerSearchException):
    """Data not found"""

    def __init__(self, message: str = "Data not found", details: Optional[Any] = None):
        super().__init__(message, code="DATA_NOT_FOUND", details=details)
