"""Main application factory and startup."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from infrastructure.config import get_config
from infrastructure.logging import setup_logging, get_logger
from infrastructure.container import get_app_context, get_container
from presentation.routers import router
from domain.exceptions import DomainException


logger = get_logger(__name__)


def create_app() -> FastAPI:
    """Create and configure FastAPI application.
    
    Returns:
        Configured FastAPI application
    """
    # Initialize configuration
    config = get_config()
    
    # Setup logging
    setup_logging()
    
    logger.info(f"Creating application in {config.api.environment} mode")

    # Create FastAPI app
    app = FastAPI(
        title="Agentic Trading Bot",
        description="Production-grade trading bot with RAG and agent orchestration",
        version="2.0.0",
        debug=config.api.debug,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.security.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register startup and shutdown events
    @app.on_event("startup")
    async def startup_event():
        """Application startup."""
        logger.info("Application startup...")
        try:
            app_context = get_app_context()
            await app_context.startup()
            logger.info("Application started successfully")
        except Exception as e:
            logger.error(f"Startup failed: {e}")
            raise

    @app.on_event("shutdown")
    async def shutdown_event():
        """Application shutdown."""
        logger.info("Application shutdown...")
        try:
            app_context = get_app_context()
            await app_context.shutdown()
            logger.info("Application shut down successfully")
        except Exception as e:
            logger.error(f"Shutdown error: {e}")

    # Include routers
    app.include_router(router)

    # Exception handlers
    @app.exception_handler(DomainException)
    async def domain_exception_handler(request, exc):
        """Handle domain exceptions."""
        return {
            "error": {
                "code": exc.__class__.__name__,
                "message": str(exc),
            }
        }

    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc):
        """Handle general exceptions."""
        logger.error(f"Unhandled exception: {exc}")
        return {
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
            }
        }

    logger.info("Application created successfully")
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    config = get_config()
    uvicorn.run(
        app,
        host=config.api.host,
        port=config.api.port,
        workers=config.api.workers,
        log_level=config.logging.level.lower(),
    )
