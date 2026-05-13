# 🤖 Agentic Trading Bot

**Production-Grade AI-Powered Trading Assistant with RAG and Agent Orchestration**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/LangChain-0.1+-orange.svg)](https://www.langchain.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

---

## 📋 Overview

The Agentic Trading Bot is a sophisticated AI-powered trading assistant that combines Retrieval-Augmented Generation (RAG) with intelligent agent orchestration. Built with clean architecture principles and production-grade patterns, it provides comprehensive market analysis, trading insights, and automated decision support.

### ✨ Key Features

- **🤖 Intelligent Agent Orchestration** - Multi-agent system for complex trading analysis
- **📚 RAG-Powered Responses** - Context-aware answers using document retrieval
- **🏗️ Clean Architecture** - Layered design with SOLID principles and design patterns
- **🔒 Enterprise Security** - Input validation, error handling, and secure configurations
- **📊 Real-time Analysis** - Market trend analysis and trading signal generation
- **🚀 Production Ready** - Docker deployment, monitoring, and scalability features
- **🧪 Comprehensive Testing** - Full test suite with API validation and edge cases

---

## 🏗️ Architecture

### Clean Layered Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Presentation Layer (FastAPI, DTOs)                        │
│  - REST API endpoints                                      │
│  - Request/response validation                             │
│  - Error handling and status codes                         │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │
┌─────────────────────────────────────────────────────────────┐
│  Application Layer (Use Cases, Business Logic)             │
│  - Query execution and document ingestion                  │
│  - Agent orchestration and workflow management             │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │
┌─────────────────────────────────────────────────────────────┐
│  Domain Layer (Business Rules, Entities)                   │
│  - Core business entities and value objects                │
│  - Repository interfaces and domain services               │
│  - Business rules and validation                           │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │
┌─────────────────────────────────────────────────────────────┐
│  Infrastructure Layer (External Dependencies)              │
│  - Database implementations and connections                │
│  - External API integrations (market data, etc.)           │
│  - File system operations and caching                      │
└─────────────────────────────────────────────────────────────┘
```

### Design Patterns Implemented

- **Factory Pattern** - Object creation and dependency injection
- **Repository Pattern** - Data access abstraction
- **Strategy Pattern** - Algorithm selection and agent behaviors
- **Singleton Pattern** - Configuration and connection management
- **Observer Pattern** - Event handling and notifications
- **Builder Pattern** - Complex object construction
- **Adapter Pattern** - External service integrations
- **Command Pattern** - Action encapsulation and undo operations

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (optional)
- Git

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd agentic-trading-bot-project
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run the application**
   ```bash
   # Start the FastAPI server
   uvicorn src.main:create_app --reload --host 0.0.0.0 --port 8000

   # Or use Docker
   docker-compose up -d
   ```

6. **Access the application**
   - **API Documentation**: http://localhost:8000/docs
   - **Health Check**: http://localhost:8000/api/v1/health
   - **Streamlit UI**: streamlit run streamlit_ui.py

### Testing

Run the comprehensive test suite:

```bash
# Start the server first
uvicorn src.main:create_app --reload --host 0.0.0.0 --port 8000

# Run tests in Jupyter notebook
jupyter notebook notebooks/test_suite.ipynb
```

---

## 📡 API Usage

### Core Endpoints

#### Health Check
```bash
GET /api/v1/health
```

#### Create Session
```bash
POST /api/v1/session
```

#### Upload Documents
```bash
POST /api/v1/upload
Content-Type: multipart/form-data

files: <document_files>
session_id: <optional_session_id>
```

#### Query Chatbot
```bash
POST /api/v1/query
Content-Type: application/json

{
  "question": "What are the current market trends?",
  "session_id": "session-uuid",
  "context": "",
  "top_k": 3
}
```

### Example Usage

```python
import requests

# Health check
response = requests.get("http://localhost:8000/api/v1/health")
print(response.json())

# Create session
response = requests.post("http://localhost:8000/api/v1/session")
session_data = response.json()
session_id = session_data["session_id"]

# Upload documents
with open("trading_report.pdf", "rb") as f:
    files = {"files": ("trading_report.pdf", f)}
    data = {"session_id": session_id}
    response = requests.post("http://localhost:8000/api/v1/upload",
                           files=files, data=data)

# Query the system
query_data = {
    "question": "What are the key market insights?",
    "session_id": session_id,
    "top_k": 3
}
response = requests.post("http://localhost:8000/api/v1/query", json=query_data)
result = response.json()
print(f"Answer: {result['answer']}")
print(f"Confidence: {result['confidence']}")
```

---

## 🧪 Testing & Validation

The project includes a comprehensive test suite (`notebooks/test_suite.ipynb`) that validates:

- ✅ API endpoint functionality
- ✅ Session management
- ✅ Document ingestion pipeline
- ✅ Query processing and RAG
- ✅ Error handling and edge cases
- ✅ Performance metrics
- ✅ Concurrent operations

### Running Tests

1. Start the FastAPI server
2. Open `notebooks/test_suite.ipynb` in Jupyter
3. Run all cells or execute individually

---

## 📁 Project Structure

```
agentic-trading-bot-project/
├── src/                          # Source code
│   ├── domain/                   # Business entities & rules
│   │   ├── entities.py           # Core domain models
│   │   ├── exceptions.py         # Domain exceptions
│   │   └── repositories.py       # Repository interfaces
│   ├── application/              # Use cases & business logic
│   │   ├── query_usecase.py      # Query processing
│   │   └── document_ingestion_usecase.py
│   ├── infrastructure/           # External dependencies
│   │   ├── config.py             # Configuration management
│   │   ├── container.py          # Dependency injection
│   │   ├── logging.py            # Structured logging
│   │   └── tool_factory.py       # External tool setup
│   ├── presentation/             # API layer
│   │   ├── routers.py            # FastAPI endpoints
│   │   └── dtos.py               # Data transfer objects
│   ├── agents/                   # Agent workflows
│   │   └── workflow.py           # LangGraph orchestrations
│   └── main.py                   # FastAPI application factory
├── tests/                        # Test suite
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   └── conftest.py               # Test configuration
├── notebooks/                    # Jupyter notebooks
│   ├── test_suite.ipynb          # Comprehensive testing
│   ├── experiments.ipynb         # Development experiments
│   └── notes.ipynb               # Development notes
├── docs/                         # Documentation
│   ├── ARCHITECTURE.md           # Architecture details
│   ├── DESIGN_PATTERNS.md        # Design patterns guide
│   ├── DEVELOPMENT.md            # Development guide
│   ├── IMPLEMENTATION_GUIDE.md   # Implementation phases
│   ├── ISSUES_FIXED.md           # Bug fixes & improvements
│   ├── PRODUCTION_REFACTORING.md # Production setup
│   ├── REFACTORING_SUMMARY.md    # Refactoring summary
│   └── SCALABILITY_CICD.md       # Scaling & DevOps
├── data/                         # Data directory
│   ├── fallback/                 # Fallback data
│   └── processed/                # Processed documents
├── logs/                         # Application logs
├── streamlit_ui.py               # Streamlit web interface
├── pyproject.toml                # Project configuration
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Docker configuration
├── docker-compose.yml            # Multi-container setup
├── Makefile                      # Build automation
└── pytest.ini                    # Test configuration
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_ENVIRONMENT=development
API_DEBUG=true

# Security
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8501"]

# Database
DATABASE_URL=sqlite:///./trading_bot.db

# External Services
OPENAI_API_KEY=your-openai-key
LANGCHAIN_API_KEY=your-langchain-key

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Advanced Configuration

See `docs/PRODUCTION_REFACTORING.md` for detailed configuration options including:
- Database connection pooling
- Caching strategies
- Rate limiting
- Monitoring and observability

---

## 🐳 Docker Deployment

### Development

```bash
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f
```

### Production

```bash
# Build production image
docker build -t agentic-trading-bot:latest .

# Run with environment file
docker run -p 8000:8000 --env-file .env agentic-trading-bot:latest
```

---

## 📊 Monitoring & Observability

### Logging

The application uses structured JSON logging with:
- Request correlation IDs
- Performance metrics
- Error tracking
- Security events

### Health Checks

- `/api/v1/health` - Application health status
- Container health checks
- Database connectivity monitoring

### Metrics

- Response times
- Error rates
- Resource usage
- Query performance

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow the established architecture patterns
- Write comprehensive tests
- Update documentation
- Use type hints and docstrings
- Follow PEP 8 style guidelines

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/) for high-performance APIs
- Powered by [LangChain](https://www.langchain.com/) for LLM orchestration
- Containerized with [Docker](https://www.docker.com/)
- Tested with comprehensive validation suite

---

## 📞 Support

For questions, issues, or contributions:

- 📧 **Email**: [your-email@example.com]
- 🐛 **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- 📖 **Documentation**: See `docs/` folder for detailed guides
- 🧪 **Testing**: Run `notebooks/test_suite.ipynb` for validation

---

*Built with ❤️ for intelligent trading analysis and decision support*