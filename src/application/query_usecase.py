"""Query use case - handles user queries."""
import time
from typing import List
from datetime import datetime

from domain.entities import QueryRequest, QueryResponse, Message, MessageRole, SearchResult
from domain.repositories import DocumentRepository, ConversationRepository, CacheRepository
from domain.exceptions import QueryExecutionError, ValidationError
from infrastructure.logging import get_logger


class QueryUseCase:
    """Use case for handling user queries."""

    def __init__(
        self,
        document_repo: DocumentRepository,
        conversation_repo: ConversationRepository,
        cache_repo: CacheRepository,
        graph_executor,  # LangGraph executor
    ):
        """Initialize query use case."""
        self.document_repo = document_repo
        self.conversation_repo = conversation_repo
        self.cache_repo = cache_repo
        self.graph_executor = graph_executor
        self.logger = get_logger(__name__)

    async def execute(self, request: QueryRequest) -> QueryResponse:
        """Execute a query.
        
        Args:
            request: Query request with question and session context
            
        Returns:
            Query response with answer and sources
            
        Raises:
            ValidationError: If request is invalid
            QueryExecutionError: If execution fails
        """
        try:
            # Validate request
            request.validate()

            start_time = time.time()
            self.logger.info(
                f"Processing query: {request.question[:50]}...",
                session_id=request.session_id,
            )

            # Check cache
            cache_key = self._get_cache_key(request.question)
            if cached_response := await self.cache_repo.get(cache_key):
                self.logger.info("Cache hit for query", session_id=request.session_id)
                return cached_response

            # Load conversation context
            conversation = await self.conversation_repo.get_by_session_id(
                request.session_id
            )
            if not conversation:
                raise ValidationError(f"Session {request.session_id} not found")

            # Execute graph with agent workflow
            graph_input = {
                "messages": [
                    {
                        "role": MessageRole.USER.value,
                        "content": request.question,
                    }
                ],
                "context": request.context,
            }

            result = await self.graph_executor.invoke(graph_input)

            # Extract answer and sources
            answer = self._extract_answer(result)
            sources = self._extract_sources(result)

            # Add user message to conversation
            user_message = Message(
                content=request.question,
                role=MessageRole.USER,
                timestamp=datetime.utcnow(),
            )
            await self.conversation_repo.add_message(request.session_id, user_message)

            # Add assistant message to conversation
            assistant_message = Message(
                content=answer,
                role=MessageRole.ASSISTANT,
                timestamp=datetime.utcnow(),
                metadata={"sources": len(sources)},
            )
            await self.conversation_repo.add_message(
                request.session_id, assistant_message
            )

            execution_time = time.time() - start_time

            response = QueryResponse(
                answer=answer,
                sources=sources,
                confidence=self._calculate_confidence(sources),
                execution_time=execution_time,
                metadata={"sources_count": len(sources)},
            )

            # Cache response
            await self.cache_repo.set(cache_key, response, ttl=3600)

            self.logger.info(
                f"Query completed in {execution_time:.2f}s",
                session_id=request.session_id,
            )

            return response

        except ValidationError:
            raise
        except Exception as e:
            self.logger.error(
                f"Query execution failed: {e}",
                session_id=request.session_id,
            )
            raise QueryExecutionError(f"Failed to execute query: {str(e)}") from e

    def _get_cache_key(self, question: str) -> str:
        """Generate cache key for question."""
        import hashlib
        question_hash = hashlib.md5(question.encode()).hexdigest()
        return f"query:{question_hash}"

    def _extract_answer(self, result: dict) -> str:
        """Extract answer from graph result."""
        if isinstance(result, dict) and "messages" in result:
            messages = result["messages"]
            if messages and len(messages) > 0:
                last_msg = messages[-1]
                if hasattr(last_msg, "content"):
                    return last_msg.content
                elif isinstance(last_msg, dict) and "content" in last_msg:
                    return last_msg["content"]
        return "Unable to generate answer"

    def _extract_sources(self, result: dict) -> List[SearchResult]:
        """Extract sources from graph result."""
        sources = []
        if isinstance(result, dict) and "sources" in result:
            for source in result["sources"]:
                if isinstance(source, dict):
                    sr = SearchResult(
                        document_id=source.get("id", "unknown"),
                        content=source.get("content", ""),
                        score=source.get("score", 0.0),
                        metadata=source.get("metadata"),
                    )
                    sources.append(sr)
        return sources

    def _calculate_confidence(self, sources: List[SearchResult]) -> float:
        """Calculate confidence score based on sources."""
        if not sources:
            return 0.0
        avg_score = sum(s.score for s in sources) / len(sources)
        return min(avg_score, 1.0)  # Ensure between 0 and 1
