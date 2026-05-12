"""API routers for the application."""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from typing import List
import uuid

from presentation.dtos import (
    QueryRequestDTO,
    QueryResponseDTO,
    IngestionResultDTO,
    ErrorDTO,
)
from domain.entities import QueryRequest, Message, MessageRole, ConversationContext
from domain.exceptions import DomainException
from infrastructure.logging import get_logger
from infrastructure.container import get_app_context


logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1", tags=["trading-bot"])


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
    }


@router.post("/query", response_model=QueryResponseDTO)
async def query_chatbot(request: QueryRequestDTO):
    """Process a user query.
    
    Args:
        request: Query request with question and session context
        
    Returns:
        Query response with answer and sources
        
    Raises:
        HTTPException: If query processing fails
    """
    try:
        logger.info(
            f"Query received: {request.question[:50]}...",
            session_id=request.session_id,
        )

        # Get application context and services
        app_context = get_app_context()
        query_usecase = app_context.container.get("query_usecase")

        # Convert DTO to domain entity
        domain_request = QueryRequest(
            question=request.question,
            session_id=request.session_id,
            context=request.context,
            top_k=request.top_k,
        )

        # Execute query
        response = await query_usecase.execute(domain_request)

        # Convert response to DTO
        return QueryResponseDTO(
            answer=response.answer,
            sources=[
                {
                    "document_id": s.document_id,
                    "content": s.content,
                    "score": s.score,
                    "metadata": s.metadata,
                }
                for s in response.sources
            ],
            confidence=response.confidence,
            execution_time=response.execution_time,
            metadata=response.metadata,
        )

    except DomainException as e:
        logger.error(f"Domain error: {e}", session_id=request.session_id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": e.__class__.__name__,
                    "message": str(e),
                }
            },
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}", session_id=request.session_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                }
            },
        )


@router.post("/upload", response_model=IngestionResultDTO)
async def upload_documents(
    files: List[UploadFile] = File(...),
    session_id: str = None,
):
    """Upload and ingest documents.
    
    Args:
        files: List of files to upload
        session_id: Session ID for context
        
    Returns:
        Ingestion result with statistics
        
    Raises:
        HTTPException: If upload fails
    """
    try:
        if not files:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": {"code": "NO_FILES", "message": "No files provided"}},
            )

        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())

        logger.info(f"Upload started: {len(files)} files", session_id=session_id)

        # Get application context and services
        app_context = get_app_context()
        ingestion_usecase = app_context.container.get("ingestion_usecase")

        # Execute ingestion
        result = await ingestion_usecase.execute(files)

        logger.info(
            f"Upload completed: {result.documents_processed} docs",
            session_id=session_id,
        )

        return IngestionResultDTO(
            success=result.success,
            documents_processed=result.documents_processed,
            chunks_created=result.chunks_created,
            errors=result.errors,
            execution_time=result.execution_time,
            metadata={**result.metadata, "session_id": session_id},
        )

    except DomainException as e:
        logger.error(f"Domain error during upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": e.__class__.__name__, "message": str(e)}},
        )
    except Exception as e:
        logger.error(f"Unexpected error during upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                }
            },
        )


@router.post("/session")
async def create_session():
    """Create a new chat session.
    
    Returns:
        Session ID
    """
    try:
        session_id = str(uuid.uuid4())
        
        # Get application context and initialize conversation
        app_context = get_app_context()
        conversation_repo = app_context.container.get("conversation_repository")
        
        context = ConversationContext(
            messages=[],
            session_id=session_id,
        )
        
        await conversation_repo.save(context)
        
        logger.info(f"Session created: {session_id}")
        
        return {"session_id": session_id}
        
    except Exception as e:
        logger.error(f"Failed to create session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "SESSION_ERROR", "message": str(e)}},
        )
