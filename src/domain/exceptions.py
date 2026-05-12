"""Domain exceptions - Business logic errors."""


class DomainException(Exception):
    """Base exception for domain layer."""
    pass


class ValidationError(DomainException):
    """Raised when domain validation fails."""
    pass


class ConfigurationError(DomainException):
    """Raised when configuration is invalid."""
    pass


class DocumentProcessingError(DomainException):
    """Raised when document processing fails."""
    pass


class VectorStoreError(DomainException):
    """Raised when vector store operations fail."""
    pass


class ModelLoadError(DomainException):
    """Raised when model loading fails."""
    pass


class QueryExecutionError(DomainException):
    """Raised when query execution fails."""
    pass


class ToolExecutionError(DomainException):
    """Raised when tool execution fails."""
    pass


class RateLimitError(DomainException):
    """Raised when rate limit is exceeded."""
    pass


class AuthenticationError(DomainException):
    """Raised when authentication fails."""
    pass


class AuthorizationError(DomainException):
    """Raised when authorization fails."""
    pass
