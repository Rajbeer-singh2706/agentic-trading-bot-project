"""HTTP error handling and responses."""
from fastapi import HTTPException, status
from typing import Any, Dict, Optional
from domain.exceptions import (
    DomainException,
    ValidationError,
    ConfigurationError,
    DocumentProcessingError,
    VectorStoreError,
    ModelLoadError,
    QueryExecutionError,
    ToolExecutionError,
    RateLimitError,
    AuthenticationError,
    AuthorizationError,
)


class ErrorResponse:
    """Structured error response."""

    def __init__(
        self,
        error_code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ):
        """Initialize error response."""
        self.error_code = error_code
        self.message = message
        self.details = details or {}
        self.status_code = status_code

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "error": {
                "code": self.error_code,
                "message": self.message,
                "details": self.details,
            }
        }


def handle_domain_exception(exc: DomainException) -> HTTPException:
    """Convert domain exception to HTTP exception."""
    
    if isinstance(exc, ValidationError):
        response = ErrorResponse(
            error_code="VALIDATION_ERROR",
            message=str(exc),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    elif isinstance(exc, ConfigurationError):
        response = ErrorResponse(
            error_code="CONFIG_ERROR",
            message="Configuration error",
            details={"message": str(exc)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    elif isinstance(exc, DocumentProcessingError):
        response = ErrorResponse(
            error_code="DOCUMENT_ERROR",
            message="Failed to process document",
            details={"message": str(exc)},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    elif isinstance(exc, VectorStoreError):
        response = ErrorResponse(
            error_code="VECTOR_STORE_ERROR",
            message="Vector store operation failed",
            details={"message": str(exc)},
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    elif isinstance(exc, ModelLoadError):
        response = ErrorResponse(
            error_code="MODEL_ERROR",
            message="Model loading failed",
            details={"message": str(exc)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    elif isinstance(exc, QueryExecutionError):
        response = ErrorResponse(
            error_code="QUERY_ERROR",
            message="Query execution failed",
            details={"message": str(exc)},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    elif isinstance(exc, ToolExecutionError):
        response = ErrorResponse(
            error_code="TOOL_ERROR",
            message="Tool execution failed",
            details={"message": str(exc)},
            status_code=status.HTTP_502_BAD_GATEWAY,
        )
    elif isinstance(exc, RateLimitError):
        response = ErrorResponse(
            error_code="RATE_LIMIT",
            message="Rate limit exceeded",
            details={"message": str(exc)},
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )
    elif isinstance(exc, AuthenticationError):
        response = ErrorResponse(
            error_code="AUTHENTICATION_ERROR",
            message="Authentication failed",
            details={"message": str(exc)},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    elif isinstance(exc, AuthorizationError):
        response = ErrorResponse(
            error_code="AUTHORIZATION_ERROR",
            message="Not authorized",
            details={"message": str(exc)},
            status_code=status.HTTP_403_FORBIDDEN,
        )
    else:
        response = ErrorResponse(
            error_code="INTERNAL_ERROR",
            message="An unexpected error occurred",
            details={"message": str(exc)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    raise HTTPException(
        status_code=response.status_code,
        detail=response.to_dict(),
    )


class HTTPExceptionMiddleware:
    """Middleware for handling HTTP exceptions."""

    async def __call__(self, request, call_next):
        """Handle exception during request processing."""
        try:
            return await call_next(request)
        except HTTPException:
            raise
        except DomainException as e:
            handle_domain_exception(e)
        except Exception as e:
            response = ErrorResponse(
                error_code="INTERNAL_ERROR",
                message="An unexpected error occurred",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
            raise HTTPException(
                status_code=response.status_code,
                detail=response.to_dict(),
            )
