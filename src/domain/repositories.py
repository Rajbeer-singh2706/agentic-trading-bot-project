"""Domain repositories - Abstract interfaces for data access."""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
from domain.entities import Document, SearchResult, Message, ConversationContext


class DocumentRepository(ABC):
    """Abstract repository for document storage."""

    @abstractmethod
    async def save(self, document: Document) -> str:
        """Save document. Returns document ID."""
        pass

    @abstractmethod
    async def get_by_id(self, doc_id: str) -> Optional[Document]:
        """Retrieve document by ID."""
        pass

    @abstractmethod
    async def list_all(self) -> List[Document]:
        """List all documents."""
        pass

    @abstractmethod
    async def delete(self, doc_id: str) -> bool:
        """Delete document."""
        pass

    @abstractmethod
    async def search(self, query: str, top_k: int = 10) -> List[SearchResult]:
        """Search documents."""
        pass


class ConversationRepository(ABC):
    """Abstract repository for conversation storage."""

    @abstractmethod
    async def save(self, context: ConversationContext) -> str:
        """Save conversation context. Returns session ID."""
        pass

    @abstractmethod
    async def get_by_session_id(self, session_id: str) -> Optional[ConversationContext]:
        """Retrieve conversation by session ID."""
        pass

    @abstractmethod
    async def add_message(self, session_id: str, message: Message) -> None:
        """Add message to conversation."""
        pass

    @abstractmethod
    async def list_by_user(self, user_id: str) -> List[ConversationContext]:
        """List conversations by user."""
        pass

    @abstractmethod
    async def delete(self, session_id: str) -> bool:
        """Delete conversation."""
        pass


class CacheRepository(ABC):
    """Abstract repository for caching."""

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get cached value."""
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """Set cached value with TTL (seconds)."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete cached value."""
        pass

    @abstractmethod
    async def clear(self) -> None:
        """Clear all cache."""
        pass
