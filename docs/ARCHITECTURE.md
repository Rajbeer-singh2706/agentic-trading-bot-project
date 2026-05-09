# Architecture Overview

## Project Structure

```
agentic-trading-bot-project/
├── src/                          # Source code
│   ├── agents/                   # Agent implementations
│   ├── core/                     # Core classes and abstractions
│   ├── utils/                    # Utility functions
│   ├── api/                      # API endpoints
│   └── __init__.py
├── tests/                        # Test suite
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   └── fixtures/                 # Test fixtures and mocks
├── data/                         # Data directory
│   ├── raw/                      # Raw data
│   ├── processed/                # Processed data
│   └── models/                   # Trained models
├── scripts/                      # Utility scripts
├── docs/                         # Documentation
├── logs/                         # Application logs
├── notebooks/                    # Jupyter notebooks
├── config/                       # Configuration files
├── Dockerfile                    # Docker configuration
├── docker-compose.yml            # Multi-container setup
├── Makefile                      # Build automation
├── requirements.txt              # Dependencies
└── pyproject.toml                # Project metadata
```

## Core Components

### Agents (`src/agents/`)
Contains all agent implementations for trading decisions and analysis.

### Core (`src/core/`)
Base classes, interfaces, and abstract implementations.

### Utils (`src/utils/`)
Helper functions for common operations, logging, configuration management, etc.

### API (`src/api/`)
FastAPI or Flask endpoints for external communication.

## Development Workflow

1. **Development**: Write code in `src/`, tests in `tests/`
2. **Testing**: Run `make test` for comprehensive testing
3. **Linting**: Use `make lint` and `make format` for code quality
4. **Deployment**: Build with `make docker-build` and deploy with Docker Compose

## Environment Management

- Copy `.env.example` to `.env` and configure accordingly
- Never commit `.env` or sensitive credentials
- Use `.env.local` for local overrides

## Database Schema

Database schema and migrations should be stored in appropriate directories as the project evolves.

## Logging

- All logs are written to `logs/` directory
- Log level is configurable via environment variables
- Check `LOG_LEVEL` in `.env` to adjust verbosity
