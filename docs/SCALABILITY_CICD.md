# Scalability & CI/CD Best Practices

## Scalability Architecture

### 1. Horizontal Scaling

#### Stateless Design
```python
# ✅ Stateless: Can run on any instance
@app.post("/api/v1/query")
async def query_chatbot(request: QueryRequestDTO):
    # All state external (session DB, cache)
    # No in-memory state
    return response

# ❌ Avoid: In-memory state (prevents scaling)
class QueryHandler:
    cache = {}  # ❌ Not shared across instances
```

#### Session Management
```python
# Store sessions externally
class ConversationRepository(ABC):
    async def save(self, context: ConversationContext) -> str:
        # Persists to Postgres
        # Accessible from any instance
        pass

# Usage
repository = get_container().get("conversation_repository")
conversation = await repository.get_by_session_id(session_id)
```

#### Load Balancer Compatible
```yaml
# Docker Compose with load balancer
version: '3.8'
services:
  api-1:
    image: trading-bot:latest
    ports:
      - "8001:8000"
    
  api-2:
    image: trading-bot:latest
    ports:
      - "8002:8000"
  
  api-3:
    image: trading-bot:latest
    ports:
      - "8003:8000"
  
  nginx:
    image: nginx:latest
    ports:
      - "8000:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - api-1
      - api-2
      - api-3
```

### 2. Vertical Scaling

#### Async/Await for Concurrency
```python
# ✅ Handle many requests concurrently
@app.post("/api/v1/query")
async def query_chatbot(request: QueryRequestDTO):
    # FastAPI runs in thread pool
    # Can handle thousands of concurrent requests
    result = await query_usecase.execute(request)
    return result

# ✅ Async database operations
async def get_by_id(self, id: str) -> Optional[Document]:
    # Non-blocking I/O
    return await db.query(...)
```

#### Multi-Worker Setup
```bash
# Production: Multiple workers
uvicorn src.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 8 \  # Number of CPU cores
    --worker-class uvicorn.workers.UvicornWorker
```

#### Worker Sizing
```python
import multiprocessing

# Recommended: 2-4 workers per CPU core
cpus = multiprocessing.cpu_count()
workers = cpus * 2  # or cpus * 4 for I/O heavy

config = get_config()
config.api.workers = workers
```

### 3. Database Scaling

#### Read Replicas
```python
# Primary (write)
class PrimaryRepository(DocumentRepository):
    def __init__(self, primary_url: str):
        self.primary = create_engine(primary_url)
    
    async def save(self, document):
        # Write to primary
        await self.primary.execute(...)

# Read replicas (read-only)
class ReplicaRepository(DocumentRepository):
    def __init__(self, replica_urls: List[str]):
        self.replicas = [create_engine(url) for url in replica_urls]
        self.current = 0
    
    async def search(self, query):
        # Round-robin through replicas
        engine = self.replicas[self.current % len(self.replicas)]
        self.current += 1
        return await engine.execute(...)
```

#### Connection Pooling
```python
# Configure connection pool
config = PostgresConfig(
    connection_string="postgresql://...",
    pool_size=20,  # Max connections in pool
    max_overflow=10,  # Additional connections allowed
    pool_timeout=30,  # Timeout for getting connection
    pool_recycle=3600,  # Recycle connections hourly
)
```

### 4. Cache Scaling

#### Distributed Caching
```python
# Redis cluster for distributed cache
class RedisCacheRepository(CacheRepository):
    def __init__(self, redis_cluster_nodes: List[str]):
        # Redis Cluster automatically shards data
        self.redis = RedisCluster(startup_nodes=redis_cluster_nodes)
    
    async def set(self, key: str, value: Any, ttl: int = 3600):
        # Data automatically distributed across cluster
        self.redis.setex(key, ttl, json.dumps(value))
```

#### Cache Warming
```python
async def warm_cache():
    """Pre-populate cache with frequently accessed data."""
    cache = get_cache_repo()
    
    # Warm with popular queries
    popular_queries = await get_popular_queries()
    for query in popular_queries:
        result = await execute_query(query)
        await cache.set(f"query:{query}", result)
```

### 5. Vector Store Scaling

#### Partitioning by User
```python
# Namespace per user
class PineconeDocumentRepository(DocumentRepository):
    def __init__(self, pinecone_key: str, user_id: str):
        self.index = Pinecone(api_key=pinecone_key)
        self.namespace = f"user_{user_id}"  # Isolated per user
    
    async def search(self, query: str):
        results = self.index.query(
            vector=embed(query),
            namespace=self.namespace,  # Query only user's data
            top_k=5,
        )
        return results
```

#### Sharding by Document Type
```python
# Different index per document type
class ShardedDocumentRepository(DocumentRepository):
    def __init__(self, pinecone_key: str):
        self.index_pdf = Pinecone(...).Index("documents-pdf")
        self.index_web = Pinecone(...).Index("documents-web")
        self.index_financial = Pinecone(...).Index("documents-financial")
    
    async def search(self, query: str, doc_type: str):
        if doc_type == "pdf":
            index = self.index_pdf
        elif doc_type == "web":
            index = self.index_web
        else:
            index = self.index_financial
        
        return await index.query(...)
```

### 6. API Rate Limiting

#### Per-User Rate Limiting
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/query")
@limiter.limit("100/minute")
async def query_chatbot(request: Request, req: QueryRequestDTO):
    # Max 100 requests per minute per IP
    return await process_query(req)
```

#### Redis-Based Rate Limiting
```python
class RedisRateLimiter:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
    
    async def is_allowed(self, user_id: str, limit: int, window: int) -> bool:
        key = f"rate_limit:{user_id}"
        count = self.redis.incr(key)
        
        if count == 1:
            self.redis.expire(key, window)  # Set expiry on first request
        
        return count <= limit

# Usage
@app.post("/api/v1/query")
async def query_chatbot(request: QueryRequestDTO):
    limiter = RedisRateLimiter(config.external_apis.redis_url)
    
    if not await limiter.is_allowed(request.session_id, limit=100, window=60):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    return await process_query(request)
```

---

## CI/CD Pipeline

### 1. GitHub Actions Workflow

```yaml
# .github/workflows/main.yml
name: Test & Deploy

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}/trading-bot

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov pytest-mock
      
      - name: Lint with flake8
        run: |
          pip install flake8
          flake8 src/ --count --select=E9,F63,F7,F82 --show-source --statistics
      
      - name: Type check with mypy
        run: |
          pip install mypy
          mypy src/ --ignore-missing-imports
      
      - name: Run unit tests
        env:
          PYTEST_ADDOPTS: --cov=src --cov-report=xml
        run: |
          pytest tests/unit/ -v
      
      - name: Run integration tests
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/testdb
          REDIS_URL: redis://localhost:6379/0
        run: |
          pytest tests/integration/ -v
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml

  build:
    needs: test
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Log in to Container Registry
        uses: docker/login-action@v2
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
      
      - name: Build and push Docker image
        uses: docker/build-push-action@v4
        with:
          context: .
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}

  deploy-staging:
    needs: build
    if: github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Staging
        run: |
          # Deploy to staging environment
          kubectl set image deployment/trading-bot-staging \
            trading-bot=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }} \
            --record
      
      - name: Run smoke tests
        run: |
          pytest tests/e2e/smoke_tests.py -v \
            --base-url https://staging-api.example.com

  deploy-production:
    needs: build
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Production
        run: |
          # Deploy with canary strategy
          kubectl set image deployment/trading-bot \
            trading-bot=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }} \
            --record
      
      - name: Monitor deployment
        run: |
          # Wait for deployment to be ready
          kubectl rollout status deployment/trading-bot --timeout=5m
      
      - name: Run health checks
        run: |
          pytest tests/e2e/health_checks.py -v \
            --base-url https://api.example.com
```

### 2. Pre-Commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/PyCQA/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=100]

  - repo: https://github.com/PyCQA/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: [--profile=black]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.0.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

### 3. Testing Strategy

#### Unit Tests
```python
# tests/unit/test_query_usecase.py
@pytest.mark.asyncio
async def test_query_with_cache():
    # Mock repositories
    mock_doc_repo = AsyncMock(spec=DocumentRepository)
    mock_cache_repo = AsyncMock(spec=CacheRepository)
    
    # Cache hit
    mock_cache_repo.get.return_value = QueryResponse(...)
    
    usecase = QueryUseCase(mock_doc_repo, mock_cache_repo, mock_executor)
    response = await usecase.execute(QueryRequest(...))
    
    # Verify cache was checked
    mock_cache_repo.get.assert_called_once()
    # Verify document repo wasn't called (cache hit)
    mock_doc_repo.search.assert_not_called()
```

#### Integration Tests
```python
# tests/integration/test_api.py
@pytest.mark.asyncio
async def test_query_flow():
    # Real FastAPI app
    client = AsyncClient(app=app)
    
    # Create session
    session = await client.post("/api/v1/session")
    session_id = session.json()["session_id"]
    
    # Upload document (if needed)
    # Execute query
    # Verify response
    
    response = await client.post(
        "/api/v1/query",
        json={"question": "test", "session_id": session_id}
    )
    
    assert response.status_code == 200
```

#### Performance Tests
```python
# tests/performance/test_performance.py
@pytest.mark.asyncio
async def test_query_performance():
    # Should respond in <500ms
    start = time.time()
    response = await query_usecase.execute(QueryRequest(...))
    duration = time.time() - start
    
    assert duration < 0.5, f"Query took {duration}s"

@pytest.mark.asyncio
async def test_concurrent_queries():
    # Should handle 100 concurrent queries
    tasks = [
        query_usecase.execute(QueryRequest(...))
        for _ in range(100)
    ]
    
    results = await asyncio.gather(*tasks)
    assert len(results) == 100
```

### 4. Monitoring & Observability

#### Prometheus Metrics
```python
# src/infrastructure/metrics.py
from prometheus_client import Counter, Histogram, Gauge

query_counter = Counter(
    'query_requests_total',
    'Total queries processed',
    ['status']
)

query_duration = Histogram(
    'query_duration_seconds',
    'Query execution time',
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0)
)

active_queries = Gauge(
    'queries_active',
    'Number of active queries'
)

# Use in application
@app.post("/api/v1/query")
async def query_chatbot(request: QueryRequestDTO):
    active_queries.inc()
    with query_duration.time():
        try:
            result = await process_query(request)
            query_counter.labels(status="success").inc()
            return result
        except Exception as e:
            query_counter.labels(status="error").inc()
            raise
        finally:
            active_queries.dec()
```

#### OpenTelemetry Tracing
```python
# src/infrastructure/tracing.py
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Setup tracer
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

tracer = trace.get_tracer(__name__)

# Use in application
@app.post("/api/v1/query")
async def query_chatbot(request: QueryRequestDTO):
    with tracer.start_as_current_span("query") as span:
        span.set_attribute("question", request.question[:50])
        
        with tracer.start_as_current_span("retrieve_documents"):
            documents = await search_documents(request.question)
        
        with tracer.start_as_current_span("generate_response"):
            response = await generate_response(documents)
        
        return response
```

---

## Summary

### Scalability
✅ Horizontal scaling with stateless design
✅ Vertical scaling with async/await
✅ Database scaling with read replicas
✅ Distributed caching with Redis
✅ Vector store partitioning
✅ Rate limiting

### CI/CD
✅ GitHub Actions workflow
✅ Unit, integration, E2E tests
✅ Code coverage reporting
✅ Docker image building
✅ Staging/production deployment
✅ Monitoring and observability

**Result**: Production-grade, scalable system ready for enterprise deployment.
