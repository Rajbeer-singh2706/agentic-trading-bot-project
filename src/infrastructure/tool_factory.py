"""Tool factory and management - centralized tool initialization."""
from typing import List, Optional, Dict, Any
from abc import ABC, abstractmethod
import asyncio

from infrastructure.logging import get_logger
from domain.exceptions import ToolExecutionError


class BaseTool(ABC):
    """Base class for all tools."""

    def __init__(self, name: str, description: str):
        """Initialize tool."""
        self.name = name
        self.description = description
        self.logger = get_logger(self.__class__.__name__)

    @abstractmethod
    async def execute(self, *args, **kwargs) -> Any:
        """Execute tool. Must be implemented by subclasses."""
        pass

    @abstractmethod
    def to_langchain_tool(self):
        """Convert to LangChain tool format."""
        pass


class RetrieverTool(BaseTool):
    """Tool for retrieving documents from vector store."""

    def __init__(self, vector_store):
        """Initialize retriever tool."""
        super().__init__(
            name="retriever",
            description="Retrieve relevant documents from the knowledge base",
        )
        self.vector_store = vector_store

    async def execute(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve documents."""
        try:
            self.logger.info(f"Retrieving documents for: {query[:50]}...")
            results = await self.vector_store.search(query, top_k=top_k)
            self.logger.info(f"Retrieved {len(results)} documents")
            return results
        except Exception as e:
            self.logger.error(f"Retrieval failed: {e}")
            raise ToolExecutionError(f"Document retrieval failed: {str(e)}") from e

    def to_langchain_tool(self):
        """Convert to LangChain tool."""
        from langchain.tools import Tool

        async def retriever_wrapper(query: str) -> str:
            results = await self.execute(query)
            return "\n".join(
                [f"- {r.get('content', '')}" for r in results[:3]]
            )

        return Tool(
            name=self.name,
            description=self.description,
            func=lambda q: asyncio.run(retriever_wrapper(q)),
        )


class WebSearchTool(BaseTool):
    """Tool for web search."""

    def __init__(self, api_key: str, max_results: int = 5):
        """Initialize web search tool."""
        super().__init__(
            name="web_search",
            description="Search the web for current information",
        )
        self.api_key = api_key
        self.max_results = max_results

    async def execute(self, query: str) -> List[Dict[str, Any]]:
        """Execute web search."""
        try:
            self.logger.info(f"Searching web for: {query}")
            # Integration with Tavily or similar would go here
            # For now, returning empty results
            return []
        except Exception as e:
            self.logger.error(f"Web search failed: {e}")
            raise ToolExecutionError(f"Web search failed: {str(e)}") from e

    def to_langchain_tool(self):
        """Convert to LangChain tool."""
        from langchain.tools import Tool

        async def search_wrapper(query: str) -> str:
            results = await self.execute(query)
            return "\n".join([f"- {r.get('title', '')}" for r in results[:3]])

        return Tool(
            name=self.name,
            description=self.description,
            func=lambda q: asyncio.run(search_wrapper(q)),
        )


class FinancialDataTool(BaseTool):
    """Tool for retrieving financial data."""

    def __init__(self, api_key: str):
        """Initialize financial data tool."""
        super().__init__(
            name="financial_data",
            description="Get financial data for stocks and assets",
        )
        self.api_key = api_key

    async def execute(self, symbol: str, data_type: str = "quote") -> Dict[str, Any]:
        """Get financial data."""
        try:
            self.logger.info(f"Fetching {data_type} for {symbol}")
            # Integration with Polygon API would go here
            # For now, returning empty dict
            return {}
        except Exception as e:
            self.logger.error(f"Financial data fetch failed: {e}")
            raise ToolExecutionError(f"Financial data fetch failed: {str(e)}") from e

    def to_langchain_tool(self):
        """Convert to LangChain tool."""
        from langchain.tools import Tool

        async def financial_wrapper(symbol: str) -> str:
            data = await self.execute(symbol)
            return str(data)

        return Tool(
            name=self.name,
            description=self.description,
            func=lambda s: asyncio.run(financial_wrapper(s)),
        )


class ToolFactory:
    """Factory for creating and managing tools."""

    def __init__(self):
        """Initialize tool factory."""
        self.tools: Dict[str, BaseTool] = {}
        self.logger = get_logger(__name__)
        self._initialized = False

    def register(self, name: str, tool: BaseTool) -> None:
        """Register a tool."""
        self.tools[name] = tool
        self.logger.info(f"Registered tool: {name}")

    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name."""
        return self.tools.get(name)

    def get_all_tools(self) -> List[BaseTool]:
        """Get all registered tools."""
        return list(self.tools.values())

    def get_langchain_tools(self) -> List:
        """Get all tools in LangChain format."""
        return [tool.to_langchain_tool() for tool in self.tools.values()]

    async def initialize(
        self,
        vector_store=None,
        tavily_api_key: Optional[str] = None,
        polygon_api_key: Optional[str] = None,
    ) -> None:
        """Initialize and register tools.
        
        Args:
            vector_store: Vector store for retriever
            tavily_api_key: Tavily API key for web search
            polygon_api_key: Polygon API key for financial data
        """
        try:
            if vector_store:
                self.register("retriever", RetrieverTool(vector_store))

            if tavily_api_key:
                self.register("web_search", WebSearchTool(tavily_api_key))

            if polygon_api_key:
                self.register("financial_data", FinancialDataTool(polygon_api_key))

            self._initialized = True
            self.logger.info(f"Tool factory initialized with {len(self.tools)} tools")

        except Exception as e:
            self.logger.error(f"Failed to initialize tools: {e}")
            raise ToolExecutionError(f"Tool initialization failed: {str(e)}") from e

    def is_initialized(self) -> bool:
        """Check if factory is initialized."""
        return self._initialized


# Global tool factory instance (singleton)
_tool_factory: Optional[ToolFactory] = None


def get_tool_factory() -> ToolFactory:
    """Get global tool factory instance."""
    global _tool_factory
    if _tool_factory is None:
        _tool_factory = ToolFactory()
    return _tool_factory


def reset_tool_factory() -> None:
    """Reset tool factory (for testing)."""
    global _tool_factory
    _tool_factory = None
