"""Repository implementations for data persistence."""
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from domain.entities import Document, SearchResult, Message, ConversationContext
from domain.repositories import DocumentRepository, ConversationRepository, CacheRepository
from infrastructure.config import get_config
from infrastructure.logging import get_logger


class InMemoryConversationRepository(ConversationRepository):
    """In-memory implementation of ConversationRepository."""

    def __init__(self):
        """Initialize repository."""
        self._conversations: Dict[str, ConversationContext] = {}
        self.logger = get_logger(__name__)

    async def save(self, context: ConversationContext) -> str:
        """Save conversation context."""
        session_id = context.session_id or str(uuid.uuid4())
        context.session_id = session_id
        self._conversations[session_id] = context
        self.logger.debug(f"Saved conversation: {session_id}")
        return session_id

    async def get_by_session_id(self, session_id: str) -> Optional[ConversationContext]:
        """Retrieve conversation by session ID."""
        return self._conversations.get(session_id)

    async def add_message(self, session_id: str, message: Message) -> None:
        """Add a message to an existing conversation."""
        conversation = self._conversations.get(session_id)
        if conversation is None:
            raise ValueError(f"Conversation not found: {session_id}")
        conversation.add_message(message)
        self._conversations[session_id] = conversation
        self.logger.debug(f"Added message to conversation: {session_id}")

    async def list_by_user(self, user_id: str) -> List[ConversationContext]:
        """List conversations belonging to a user."""
        return [
            conversation
            for conversation in self._conversations.values()
            if conversation.user_id == user_id
        ]

    async def update(self, context: ConversationContext) -> None:
        """Update conversation context."""
        if context.session_id:
            self._conversations[context.session_id] = context
            self.logger.debug(f"Updated conversation: {context.session_id}")

    async def delete(self, session_id: str) -> bool:
        """Delete conversation."""
        if session_id in self._conversations:
            del self._conversations[session_id]
            self.logger.debug(f"Deleted conversation: {session_id}")
            return True
        return False


class InMemoryCacheRepository(CacheRepository):
    """In-memory implementation of CacheRepository."""

    def __init__(self):
        """Initialize repository."""
        self._cache: Dict[str, Any] = {}
        self.logger = get_logger(__name__)

    async def get(self, key: str) -> Optional[Any]:
        """Get cached value."""
        return self._cache.get(key)

    async def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """Set cached value."""
        self._cache[key] = value
        self.logger.debug(f"Cached value for key: {key}")

    async def delete(self, key: str) -> bool:
        """Delete cached value."""
        if key in self._cache:
            del self._cache[key]
            self.logger.debug(f"Deleted cache key: {key}")
            return True
        return False

    async def clear(self) -> None:
        """Clear all cached values."""
        self._cache.clear()
        self.logger.debug("Cache cleared")


class PineconeDocumentRepository(DocumentRepository):
    """Pinecone-based implementation of DocumentRepository."""

    def __init__(self, config=None):
        """Initialize repository."""
        self.config = config or get_config()
        self.logger = get_logger(__name__)
        self._index = None
        self._initialized = False

    async def _ensure_initialized(self):
        """Ensure Pinecone index is initialized."""
        if self._initialized:
            return

        try:
            from pinecone import Pinecone

            pc = Pinecone(api_key=self.config.vector_db.api_key)
            self._index = pc.Index(self.config.vector_db.index_name)
            self._initialized = True
            self.logger.info("Pinecone repository initialized")
        except ImportError:
            self.logger.error("Pinecone not installed. Install with: pip install pinecone-client")
            raise
        except Exception as e:
            self.logger.error(f"Failed to initialize Pinecone: {e}")
            raise

    async def save(self, document: Document) -> str:
        """Save document to vector store."""
        await self._ensure_initialized()

        doc_id = document.id or str(uuid.uuid4())
        document.id = doc_id

        # Prepare vector data
        vector_data = {
            "id": doc_id,
            "values": document.embedding,
            "metadata": {
                "content": document.content,
                "filename": document.filename,
                "content_type": document.content_type,
                "created_at": document.created_at.isoformat() if document.created_at else None,
                "metadata": document.metadata or {}
            }
        }

        # Upsert to Pinecone
        self._index.upsert(vectors=[vector_data])
        self.logger.info(f"Saved document: {doc_id}")
        return doc_id

    async def get_by_id(self, doc_id: str) -> Optional[Document]:
        """Retrieve document by ID."""
        await self._ensure_initialized()

        try:
            result = self._index.fetch(ids=[doc_id])
            if not result.vectors:
                return None

            vector_data = result.vectors[doc_id]
            metadata = vector_data.metadata

            return Document(
                id=doc_id,
                content=metadata["content"],
                embedding=vector_data.values,
                filename=metadata["filename"],
                content_type=metadata["content_type"],
                created_at=datetime.fromisoformat(metadata["created_at"]) if metadata["created_at"] else None,
                metadata=metadata.get("metadata", {})
            )
        except Exception as e:
            self.logger.error(f"Failed to retrieve document {doc_id}: {e}")
            return None

    async def list_all(self) -> List[Document]:
        """List all documents."""
        await self._ensure_initialized()

        try:
            # This is a simplified implementation - in production you'd want pagination
            result = self._index.query(
                vector=[0] * self.config.vector_db.dimension,  # Dummy vector for listing
                top_k=10000,  # Large number to get all
                include_metadata=True,
                include_values=True
            )

            documents = []
            for match in result.matches:
                metadata = match.metadata
                documents.append(Document(
                    id=match.id,
                    content=metadata["content"],
                    embedding=match.values,
                    filename=metadata["filename"],
                    content_type=metadata["content_type"],
                    created_at=datetime.fromisoformat(metadata["created_at"]) if metadata["created_at"] else None,
                    metadata=metadata.get("metadata", {})
                ))

            return documents
        except Exception as e:
            self.logger.error(f"Failed to list documents: {e}")
            return []

    async def delete(self, doc_id: str) -> bool:
        """Delete document."""
        await self._ensure_initialized()

        try:
            self._index.delete(ids=[doc_id])
            self.logger.info(f"Deleted document: {doc_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete document {doc_id}: {e}")
            return False

    async def search(self, query: str, top_k: int = 10) -> List[SearchResult]:
        """Search documents."""
        await self._ensure_initialized()

        # For now, return empty results as the embedding function is not implemented
        # In a real implementation, you would:
        # 1. Embed the query using the same embedding model
        # 2. Query Pinecone with the embedded query
        # 3. Convert results to SearchResult objects
        self.logger.warning("Search not fully implemented - needs embedding function and query embedding")
        return []