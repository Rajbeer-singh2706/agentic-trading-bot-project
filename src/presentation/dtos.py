"""Request/Response DTOs for API."""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime


class QueryRequestDTO(BaseModel):
    """Data transfer object for query requests."""
    question: str = Field(..., min_length=1, max_length=2000)
    session_id: str = Field(...)
    context: Optional[str] = Field(default=None, max_length=5000)
    top_k: int = Field(default=3, ge=1, le=20)

    @validator("question")
    def question_not_empty(cls, v):
        """Validate question is not empty."""
        if not v or not v.strip():
            raise ValueError("Question cannot be empty")
        return v.strip()

    class Config:
        """Pydantic config."""
        schema_extra = {
            "example": {
                "question": "What is the current price of AAPL?",
                "session_id": "session_12345",
                "context": "Looking for stock market insights",
                "top_k": 5,
            }
        }

class SearchResultDTO(BaseModel):
    """Data transfer object for search results."""
    document_id: str
    content: str
    score: float = Field(ge=0.0, le=1.0)
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        """Pydantic config."""
        schema_extra = {
            "example": {
                "document_id": "doc_123",
                "content": "Apple Inc. is a technology company...",
                "score": 0.95,
                "metadata": {"source": "wikipedia"},
            }
        }

class QueryResponseDTO(BaseModel):
    """Data transfer object for query responses."""
    answer: str
    sources: List[SearchResultDTO]
    confidence: float = Field(ge=0.0, le=1.0)
    execution_time: float
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        """Pydantic config."""
        schema_extra = {
            "example": {
                "answer": "Apple's stock price is $150.25 as of today...",
                "sources": [],
                "confidence": 0.92,
                "execution_time": 0.45,
                "metadata": {"model": "mixtral-8x7b-32768"},
            }
        }

class UploadRequestDTO(BaseModel):
    """Data transfer object for upload requests."""
    session_id: str = Field(...)

    class Config:
        """Pydantic config."""
        schema_extra = {"example": {"session_id": "session_12345"}}

class IngestionResultDTO(BaseModel):
    """Data transfer object for ingestion results."""
    success: bool
    documents_processed: int
    chunks_created: int
    errors: List[str]
    execution_time: float
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        """Pydantic config."""
        schema_extra = {
            "example": {
                "success": True,
                "documents_processed": 5,
                "chunks_created": 125,
                "errors": [],
                "execution_time": 3.45,
            }
        }

class ErrorDTO(BaseModel):
    """Data transfer object for errors."""
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic config."""
        schema_extra = {
            "example": {
                "error_code": "VALIDATION_ERROR",
                "message": "Question must be provided",
                "details": {"field": "question"},
                "timestamp": "2024-01-01T12:00:00",
            }
        }

class HealthCheckDTO(BaseModel):
    """Data transfer object for health checks."""
    status: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    checks: Dict[str, str] = Field(default_factory=dict)

    class Config:
        """Pydantic config."""
        schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "timestamp": "2024-01-01T12:00:00",
                "checks": {
                    "vector_db": "healthy",
                    "llm": "healthy",
                    "cache": "healthy",
                },
            }
        }
