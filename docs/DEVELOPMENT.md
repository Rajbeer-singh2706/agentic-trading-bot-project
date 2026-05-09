# Development Guide

## Setup

1. **Clone the repository**
   ```bash
   git clone <repository>
   cd agentic-trading-bot-project
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   make install
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```

## Running Tests

```bash
# Run all tests
make test

# Run only unit tests
make test-unit

# Run only integration tests
make test-integration
```

## Code Quality

```bash
# Check code quality
make lint

# Format code
make format
```

## Running the Application

### Local Development
```bash
make run
```

### Docker
```bash
# Build and start services
make docker-up

# Stop services
make docker-down

# View logs
make docker-logs
```

## Common Tasks

| Task | Command |
|------|---------|
| Install deps | `make install` |
| Run tests | `make test` |
| Format code | `make format` |
| Lint code | `make lint` |
| Run app | `make run` |
| Docker build | `make docker-build` |
| Docker up | `make docker-up` |
| Docker down | `make docker-down` |

## Adding New Dependencies

1. Add to `requirements.txt` (for production) or `requirements-dev.txt` (for development)
2. Run `pip install -r requirements.txt` or `make install`
3. Update Docker image if needed

## Project Guidelines

- Follow PEP 8 style guide
- Write docstrings for all functions and classes
- Include type hints
- Write tests for new features
- Keep commits atomic and meaningful
