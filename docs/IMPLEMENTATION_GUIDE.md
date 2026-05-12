# Implementation & Testing Guide

## Phase 1: Infrastructure Setup (Completed)

### Configuration Layer
✅ `src/infrastructure/config.py`
- Hierarchical configuration management
- Environment variable validation
- Sensible defaults

### Logging Layer
✅ `src/infrastructure/logging.py`
- Structured JSON logging
- Rotating file handlers
- Configurable log levels

### Dependency Injection
✅ `src/infrastructure/container.py`
- Service container for DI
- Application context lifecycle
- Singleton management

### Error Handling
✅ `src/infrastructure/error_handling.py`
- Structured exception hierarchy
- HTTP status code mapping
- Error response formatting

---

## Phase 2: Domain Layer (Completed)

### Entities
✅ `src/domain/entities.py`
- QueryRequest, QueryResponse
- Document, SearchResult
- Message, ConversationContext
- IngestionResult

### Exceptions
✅ `src/domain/exceptions.py`
- DomainException hierarchy
- ValidationError, ConfigurationError, etc.

### Repository Interfaces
✅ `src/domain/repositories.py`
- DocumentRepository
- ConversationRepository
- CacheRepository

---

## Phase 3: Application Layer (Completed)

### Use Cases
✅ `src/application/query_usecase.py`
- Query execution with caching
- Source extraction
- Confidence calculation

✅ `src/application/document_ingestion_usecase.py`
- File validation
- Text extraction (PDF, DOCX, TXT)
- Document storage

---

## Phase 4: Presentation Layer (Completed)

### DTOs
✅ `src/presentation/dtos.py`
- Request validation
- Response formatting
- OpenAPI documentation

### API Routers
✅ `src/presentation/routers.py`
- `/api/v1/query` - Process queries
- `/api/v1/upload` - Upload documents
- `/api/v1/session` - Create sessions
- `/api/v1/health` - Health check

---

## Phase 5: Agent Orchestration (Completed)

### Workflow
✅ `src/agents/workflow.py`
- Fixed END edge routing
- Proper state management
- Streaming support

### Tool Factory
✅ `src/infrastructure/tool_factory.py`
- BaseTool abstract class
- RetrieverTool, WebSearchTool, FinancialDataTool
- Centralized initialization

---

## Phase 6: Infrastructure Implementations (To Do)

### Vector DB Repository
**File**: `src/infrastructure/repositories/pinecone_repository.py`

```python
class PineconeDocumentRepository(DocumentRepository):
    def __init__(self, api_key: str, index_name: str):
        self.pc = Pinecone(api_key=api_key)
        self.index = self.pc.Index(index_name)
    
    async def save(self, document: Document) -> str:
        # 1. Split document into chunks
        # 2. Generate embeddings
        # 3. Upsert to Pinecone
        # 4. Return document ID
        pass
    
    async def search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        # 1. Generate query embedding
        # 2. Query vector index
        # 3. Return SearchResult objects
        pass
```

### Cache Repository
**File**: `src/infrastructure/repositories/redis_cache.py`

```python
class RedisCacheRepository(CacheRepository):
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
    
    async def get(self, key: str) -> Optional[Any]:
        value = self.redis.get(key)
        return json.loads(value) if value else None
    
    async def set(self, key: str, value: Any, ttl: int = 3600):
        self.redis.setex(key, ttl, json.dumps(value))
```

### Conversation Repository
**File**: `src/infrastructure/repositories/postgres_conversation.py`

```python
class PostgresConversationRepository(ConversationRepository):
    def __init__(self, connection_string: str):
        self.engine = create_async_engine(connection_string)
    
    async def save(self, context: ConversationContext) -> str:
        # Save to database
        pass
    
    async def add_message(self, session_id: str, message: Message):
        # Append message to conversation
        pass
```

---

## Phase 7: Testing (To Do)

### Unit Tests
**File**: `tests/unit/test_domain_entities.py`

```python
def test_query_request_validation():
    # Valid request
    req = QueryRequest(question="What is AI?", session_id="sess_1")
    assert req.question == "What is AI?"
    
    # Invalid request
    with pytest.raises(ValidationError):
        QueryRequest(question="", session_id="sess_1")

def test_document_entity():
    doc = Document(
        id="doc_1",
        filename="test.pdf",
        content="Test content",
        source="uploaded:test.pdf",
        created_at=datetime.utcnow(),
    )
    assert doc.to_dict()["filename"] == "test.pdf"
```

**File**: `tests/unit/test_query_usecase.py`

```python
@pytest.mark.asyncio
async def test_query_execution():
    # Mock repositories
    mock_doc_repo = AsyncMock(spec=DocumentRepository)
    mock_cache_repo = AsyncMock(spec=CacheRepository)
    mock_executor = AsyncMock()
    
    # Setup
    mock_doc_repo.search.return_value = [SearchResult(...)]
    mock_cache_repo.get.return_value = None
    mock_executor.invoke.return_value = {"messages": [...]}
    
    usecase = QueryUseCase(mock_doc_repo, mock_cache_repo, mock_executor)
    
    # Execute
    request = QueryRequest(question="Test?", session_id="sess_1")
    response = await usecase.execute(request)
    
    # Verify
    assert response.answer is not None
    assert len(response.sources) > 0
```

### Integration Tests
**File**: `tests/integration/test_api_endpoints.py`

```python
@pytest.mark.asyncio
async def test_query_endpoint():
    client = AsyncClient(app=app, base_url="http://test")
    
    # Create session first
    session_resp = await client.post("/api/v1/session")
    session_id = session_resp.json()["session_id"]
    
    # Execute query
    response = await client.post(
        "/api/v1/query",
        json={
            "question": "What is the meaning of life?",
            "session_id": session_id,
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data
    assert "confidence" in data
```

### E2E Tests
**File**: `tests/e2e/test_full_workflow.py`

```python
@pytest.mark.asyncio
async def test_full_chat_workflow():
    client = AsyncClient(app=app)
    
    # 1. Create session
    session = await client.post("/api/v1/session")
    session_id = session.json()["session_id"]
    
    # 2. Upload document
    with open("sample.pdf", "rb") as f:
        upload = await client.post(
            "/api/v1/upload",
            files={"files": f},
            params={"session_id": session_id}
        )
    assert upload.status_code == 200
    
    # 3. Query about uploaded document
    query = await client.post(
        "/api/v1/query",
        json={
            "question": "What is in the document?",
            "session_id": session_id,
        }
    )
    assert query.status_code == 200
    assert query.json()["answer"]
```

---

## Phase 8: CI/CD Pipeline (To Do)

### GitHub Actions Workflow
**File**: `.github/workflows/test.yml`

```yaml
name: Test & Deploy

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: "3.11"
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov
      
      - name: Run tests
        run: |
          pytest tests/ --cov=src --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

---

## Phase 9: Docker & Deployment (To Do)

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY config ./config

ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - VECTOR_DB_PROVIDER=pinecone
      - CACHE_PROVIDER=redis
    depends_on:
      - redis
      - postgres
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
```

---

## Quick Start

### 1. Setup Environment
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configuration
```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Run Locally
```bash
python -m uvicorn src.main:app --reload
```

### 4. Test
```bash
pytest tests/ -v --cov=src
```

### 5. API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Deployment Checklist

- [ ] All tests passing (>80% coverage)
- [ ] Environment variables configured
- [ ] Security review completed
- [ ] Logging configured
- [ ] Error handling tested
- [ ] Performance benchmarks met
- [ ] Documentation updated
- [ ] Docker image built and tested
- [ ] Load testing completed
- [ ] Monitoring/alerting configured
- [ ] Database migrations applied
- [ ] Backup strategy in place
- [ ] SSL/TLS configured
- [ ] Rate limiting enabled
- [ ] Authentication configured

---

## Next Steps

1. **Implement repository adapters** (Pinecone, Redis, Postgres)
2. **Add comprehensive tests** (aim for 80%+ coverage)
3. **Setup CI/CD pipeline**
4. **Add authentication** (JWT tokens)
5. **Implement rate limiting**
6. **Setup monitoring** (Prometheus, Grafana)
7. **Add load testing**
8. **Deploy to production** (Kubernetes or Cloud)

The application is now architected for production and ready for these implementation phases.
