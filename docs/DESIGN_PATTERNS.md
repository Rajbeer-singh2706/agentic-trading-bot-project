# Design Patterns & SOLID Principles Applied

## Design Patterns Used

### 1. **Dependency Injection (DI)**
**Problem**: Components tightly coupled, hard to test, can't swap implementations.

**Solution**: Constructor-based dependency injection.

```python
# ❌ Before: Hard coupling
class QueryHandler:
    def __init__(self):
        self.vector_store = PineconeVectorStore()  # Hard-coded
        self.llm = GroqLLM()  # Hard-coded

# ✅ After: Loose coupling
class QueryUseCase:
    def __init__(
        self,
        document_repo: DocumentRepository,  # Interface, not implementation
        llm,  # Injected
    ):
        self.document_repo = document_repo
        self.llm = llm
```

**Location**: `src/infrastructure/container.py`

---

### 2. **Repository Pattern**
**Problem**: Business logic tightly coupled to storage implementation.

**Solution**: Abstract repository interfaces, concrete implementations.

```python
# ❌ Before: Direct database access in business logic
class QueryHandler:
    def __init__(self):
        self.pinecone = PineconeClient()  # Storage logic mixed in
    
    def search(self, query):
        return self.pinecone.query_index(query)

# ✅ After: Storage abstraction
class DocumentRepository(ABC):  # Abstract interface
    @abstractmethod
    async def search(self, query: str) -> List[SearchResult]: pass

class PineconeDocumentRepository(DocumentRepository):  # Concrete impl
    async def search(self, query: str) -> List[SearchResult]:
        # Pinecone-specific code

class QueryUseCase:  # Business logic
    def __init__(self, repo: DocumentRepository):  # Depends on interface
        self.repo = repo
```

**Benefits**:
- Easy to swap storage backends
- Can mock repositories in tests
- Business logic independent of storage

**Location**: `src/domain/repositories.py`

---

### 3. **Factory Pattern**
**Problem**: Complex object creation scattered throughout code.

**Solution**: Centralized factory for creating and managing objects.

```python
# ❌ Before: Tool creation repeated everywhere
def retriever_tool(query):
    pc = Pinecone(api_key=...)  # Every call creates
    vector_store = PineconeSparseVectorStore(...)
    return vector_store.as_retriever().invoke(query)

# ✅ After: Factory pattern
class ToolFactory:
    def __init__(self):
        self.tools = {}
    
    def register(self, name: str, tool: BaseTool):
        self.tools[name] = tool
    
    def get_tool(self, name: str) -> BaseTool:
        return self.tools.get(name)

factory = get_tool_factory()
factory.initialize(vector_store=vs, tavily_key=key)
retriever = factory.get_tool("retriever")
```

**Benefits**:
- Single initialization point
- Reusable instances
- Easy to add new tools
- Lifecycle management

**Location**: `src/infrastructure/tool_factory.py`

---

### 4. **Singleton Pattern**
**Problem**: Creating multiple instances of expensive resources.

**Solution**: Ensure only one instance exists, global access.

```python
# ❌ Before: Multiple instances created
config1 = load_config()  # Parses YAML
config2 = load_config()  # Parses YAML again
logger1 = get_logger(__name__)  # Different logger
logger2 = get_logger(__name__)  # Another logger

# ✅ After: Singleton pattern
@lru_cache(maxsize=1)
def get_config() -> AppConfig:
    return AppConfig.from_env()  # Created once, cached

@cache
def get_logger(name: str) -> StructuredLogger:
    return StructuredLogger(name)  # One instance per module
```

**Benefits**:
- Memory efficient
- Single source of truth
- Consistent state across app

**Location**: `src/infrastructure/config.py`, `src/infrastructure/logging.py`

---

### 5. **Builder Pattern**
**Problem**: Complex object construction with many optional parameters.

**Solution**: Step-by-step construction of complex objects.

```python
# ✅ Used in WorkflowBuilder
class WorkflowBuilder:
    def __init__(self, llm, tools):
        self.llm = llm
        self.tools = tools
        self.graph = None
    
    def build(self) -> "WorkflowBuilder":
        # Step 1: Create nodes
        # Step 2: Add edges
        # Step 3: Compile graph
        self.graph = graph_builder.compile()
        return self  # Method chaining
    
    def get_graph(self):
        if self.graph is None:
            raise ValueError("Must call build() first")
        return self.graph

# Usage
workflow = WorkflowBuilder(llm, tools).build()
graph = workflow.get_graph()
```

**Location**: `src/agents/workflow.py`

---

### 6. **Strategy Pattern**
**Problem**: Different implementations of same interface.

**Solution**: Define family of algorithms, encapsulate each one.

```python
# ✅ Tool implementations as strategies
class BaseTool(ABC):
    @abstractmethod
    async def execute(self, *args) -> Any: pass

class RetrieverTool(BaseTool):  # Strategy 1
    async def execute(self, query: str) -> List[Dict]:
        return await self.vector_store.search(query)

class WebSearchTool(BaseTool):  # Strategy 2
    async def execute(self, query: str) -> List[Dict]:
        return await self.tavily_client.search(query)

# Usage: interchangeable
tools = [RetrieverTool(), WebSearchTool(), FinancialDataTool()]
for tool in tools:
    results = await tool.execute(query)  # ✅ Polymorphic
```

**Location**: `src/infrastructure/tool_factory.py`

---

### 7. **Use Case Pattern (Interactors)**
**Problem**: Business logic scattered across layers.

**Solution**: Encapsulate each business use case in separate class.

```python
# ✅ Each use case is self-contained
class QueryUseCase:
    def __init__(self, document_repo, cache_repo, graph_executor):
        self.document_repo = document_repo
        self.cache_repo = cache_repo
        self.graph_executor = graph_executor
    
    async def execute(self, request: QueryRequest) -> QueryResponse:
        # 1. Validate
        # 2. Check cache
        # 3. Execute
        # 4. Cache result
        # 5. Return response
        pass

class DocumentIngestionUseCase:
    async def execute(self, files: List[UploadFile]) -> IngestionResult:
        # 1. Validate files
        # 2. Extract text
        # 3. Chunk content
        # 4. Store in vector DB
        # 5. Return result
        pass
```

**Benefits**:
- Business logic isolated
- Reusable across interfaces
- Easy to test
- Clear transaction boundaries

**Location**: `src/application/`

---

### 8. **Middleware Pattern**
**Problem**: Cross-cutting concerns (logging, error handling, authentication).

**Solution**: Middleware to process requests/responses.

```python
@app.middleware("http")
async def logging_middleware(request, call_next):
    start = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start
    logger.info(
        "Request processed",
        method=request.method,
        path=request.url.path,
        status=response.status_code,
        duration_ms=duration * 1000,
    )
    
    return response
```

**Location**: To be added in `src/presentation/middleware.py`

---

## SOLID Principles

### **S - Single Responsibility Principle**

Each class has one reason to change:

```python
# ✅ Good: Single responsibility
class WorkflowBuilder:
    """Only builds workflows"""
    pass

class StructuredLogger:
    """Only formats and outputs logs"""
    pass

class VectorDBConfig:
    """Only manages vector DB configuration"""
    pass

# ❌ Bad: Multiple responsibilities
class DataHandler:
    """Loads config, logs messages, handles queries, manages cache"""
    pass
```

**Benefits**:
- Easy to understand
- Easy to change
- Easy to test

---

### **O - Open/Closed Principle**

Open for extension, closed for modification:

```python
# ✅ Open for extension
class BaseTool(ABC):
    @abstractmethod
    async def execute(self): pass

class CustomTool(BaseTool):  # ✅ Can add new tools without changing existing
    async def execute(self):
        pass

# ✅ Existing code doesn't need modification
for tool in tools:
    await tool.execute()

# ❌ Closed for modification - can't add tools without changing code
if tool_type == "retriever":
    retriever_tool()
elif tool_type == "search":
    web_search_tool()
elif tool_type == "financial":
    financial_tool()
# Need to add elif for each new tool - violates principle
```

---

### **L - Liskov Substitution Principle**

Subtypes must substitute base types without breaking behavior:

```python
# ✅ All tools can substitute each other
class BaseTool(ABC):
    async def execute(self, *args) -> Any: pass

class RetrieverTool(BaseTool):
    async def execute(self, query: str) -> List[SearchResult]:
        return [...]

class WebSearchTool(BaseTool):
    async def execute(self, query: str) -> List[SearchResult]:
        return [...]

# ✅ Both work the same way
async def process_with_tool(tool: BaseTool, query: str):
    results = await tool.execute(query)  # Works with any BaseTool subclass
    return results

# ❌ Violation: subtype doesn't follow interface
class BrokenTool(BaseTool):
    async def execute(self, query: str) -> str:  # ❌ Returns string instead of list
        return "broken"

process_with_tool(BrokenTool(), "query")  # Breaks because of type mismatch
```

---

### **I - Interface Segregation Principle**

Clients should depend on specific interfaces, not general ones:

```python
# ❌ Bad: Fat interface
class GeneralRepository(ABC):
    @abstractmethod
    def create(self, item): pass
    
    @abstractmethod
    def read(self, id): pass
    
    @abstractmethod
    def update(self, item): pass
    
    @abstractmethod
    def delete(self, id): pass
    
    @abstractmethod
    def list_all(self): pass  # Client may not need
    
    @abstractmethod
    def search(self, query): pass  # Client may not need
    
    @abstractmethod
    def export(self, format): pass  # Client may not need

# Class must implement all methods even if not needed
class MinimalRepository(GeneralRepository):
    def export(self, format):
        raise NotImplementedError()  # ❌ Don't need this

# ✅ Good: Segregated interfaces
class DocumentRepository(ABC):
    @abstractmethod
    async def save(self, document: Document) -> str: pass
    
    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[Document]: pass
    
    @abstractmethod
    async def search(self, query: str) -> List[SearchResult]: pass

class ConversationRepository(ABC):
    @abstractmethod
    async def save(self, context: ConversationContext) -> str: pass
    
    @abstractmethod
    async def add_message(self, session_id: str, message: Message) -> None: pass

# ✅ Clients depend only on what they need
class QueryUseCase:
    def __init__(
        self,
        document_repo: DocumentRepository,  # ✅ Only what it needs
    ):
        pass

class ConversationUseCase:
    def __init__(
        self,
        conversation_repo: ConversationRepository,  # ✅ Only what it needs
    ):
        pass
```

---

### **D - Dependency Inversion Principle**

High-level modules should not depend on low-level modules. Both should depend on abstractions:

```python
# ❌ Bad: High-level depends on low-level (concrete classes)
class QueryUseCase:
    def __init__(self):
        # ❌ Depends on concrete implementations
        self.vector_store = PineconeVectorStore()
        self.cache = RedisCache()
        self.llm = GroqLLM()

# ✅ Good: Both depend on abstractions
class QueryUseCase:
    def __init__(
        self,
        document_repo: DocumentRepository,  # ✅ Abstract
        cache_repo: CacheRepository,  # ✅ Abstract
        llm,  # ✅ Abstract interface
    ):
        self.document_repo = document_repo  # Can be any implementation
        self.cache_repo = cache_repo  # Can be any implementation
        self.llm = llm  # Can be any LLM

# ✅ Low-level modules implement abstractions
class PineconeDocumentRepository(DocumentRepository):
    pass

class RedisCache(CacheRepository):
    pass

# ✅ Both high and low depend on abstractions
```

---

## Applied Principles Summary

| Principle | Application | Location |
|-----------|-------------|----------|
| **Single Responsibility** | Each class has one job | All modules |
| **Open/Closed** | Extend via inheritance, don't modify | BaseTool, BaseUseCase |
| **Liskov Substitution** | Subtypes interchangeable | Tool implementations |
| **Interface Segregation** | Specific interfaces per client | domain/repositories.py |
| **Dependency Inversion** | Depend on abstractions | All use cases |
| **DRY** | No repeated code | Centralized config, logging |
| **KISS** | Keep it simple | Clean code, clear naming |
| **YAGNI** | You aren't gonna need it | Minimal features, no bloat |

---

## Results

✅ **Low coupling**: Changes in one module don't break others
✅ **High cohesion**: Related code grouped together
✅ **Testability**: Easy to mock and test
✅ **Maintainability**: Clear structure, easy to navigate
✅ **Extensibility**: New features don't require changing existing code
✅ **Scalability**: Can handle growth in complexity
✅ **Reusability**: Components can be used in different contexts
