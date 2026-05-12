"""Domain entities and models for the trading bot."""
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum


class ToolType(str, Enum):
    """Supported tool types."""
    RETRIEVER = "retriever"
    SEARCH = "search"
    FINANCIALS = "financials"


class MessageRole(str, Enum):
    """Message roles in conversation."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class Message:
    """Represents a conversation message."""
    content: str
    role: MessageRole
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "content": self.content,
            "role": self.role.value,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata or {},
        }


@dataclass
class ConversationContext:
    """Manages conversation context and history."""
    messages: List[Message]
    session_id: str
    user_id: Optional[str] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()

    def add_message(self, message: Message) -> None:
        """Add message to context."""
        self.messages.append(message)

    def get_recent_messages(self, count: int = 10) -> List[Message]:
        """Get recent messages."""
        return self.messages[-count:]

    def get_context_size(self) -> int:
        """Get total message count."""
        return len(self.messages)


@dataclass
class Document:
    """Represents an uploaded/ingested document."""
    id: str
    filename: str
    content: str
    source: str
    created_at: datetime
    metadata: Optional[Dict[str, Any]] = None
    chunk_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert document to dictionary."""
        return {
            "id": self.id,
            "filename": self.filename,
            "source": self.source,
            "created_at": self.created_at.isoformat(),
            "chunk_count": self.chunk_count,
            "metadata": self.metadata or {},
        }


@dataclass
class SearchResult:
    """Represents a search result from vector store."""
    document_id: str
    content: str
    score: float
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "document_id": self.document_id,
            "content": self.content,
            "score": self.score,
            "metadata": self.metadata or {},
        }


@dataclass
class QueryRequest:
    """Represents a user query request."""
    question: str
    session_id: str
    user_id: Optional[str] = None
    context: Optional[str] = None
    top_k: int = 3

    def validate(self) -> None:
        """Validate query request."""
        if not self.question or not isinstance(self.question, str):
            raise ValueError("Question must be a non-empty string")
        if not self.session_id:
            raise ValueError("Session ID is required")
        if self.top_k <= 0:
            raise ValueError("top_k must be positive")


@dataclass
class QueryResponse:
    """Represents a query response."""
    answer: str
    sources: List[SearchResult]
    confidence: float
    execution_time: float
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "answer": self.answer,
            "sources": [s.to_dict() for s in self.sources],
            "confidence": self.confidence,
            "execution_time": self.execution_time,
            "metadata": self.metadata or {},
        }


@dataclass
class IngestionResult:
    """Represents document ingestion result."""
    success: bool
    documents_processed: int
    chunks_created: int
    errors: List[str]
    execution_time: float
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "documents_processed": self.documents_processed,
            "chunks_created": self.chunks_created,
            "errors": self.errors,
            "execution_time": self.execution_time,
            "metadata": self.metadata or {},
        }
