"""Main API module."""

from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(
    title="Agentic Trading Bot API",
    description="API for the agentic trading bot",
    version="0.1.0",
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return JSONResponse(
        {"status": "healthy", "service": "agentic-trading-bot"},
        status_code=200,
    )


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Agentic Trading Bot API",
        "version": "0.1.0",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
