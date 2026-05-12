"""Refactored agent workflow with proper design patterns."""
from typing import List, Dict, Any
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt.tool_node import ToolNode, tools_condition
from typing_extensions import Annotated, TypedDict

from infrastructure.logging import get_logger
from domain.exceptions import QueryExecutionError


class AgentState(TypedDict):
    """State schema for agent workflow."""
    messages: Annotated[list, add_messages]
    context: Dict[str, Any]
    tool_results: Dict[str, Any]


class WorkflowBuilder:
    """Builds LangGraph workflow for agent orchestration."""

    def __init__(self, llm, tools: List):
        """Initialize workflow builder.
        
        Args:
            llm: Language model instance with tool binding
            tools: List of tools available to agent
        """
        if not llm:
            raise ValueError("LLM is required")
        if not tools:
            raise ValueError("At least one tool is required")

        self.llm = llm
        self.tools = tools
        self.llm_with_tools = llm.bind_tools(tools)
        self.graph = None
        self.logger = get_logger(__name__)

    def _chatbot_node(self, state: AgentState) -> Dict[str, Any]:
        """Chatbot node that processes messages and calls tools if needed."""
        try:
            # Invoke LLM with current messages
            response = self.llm_with_tools.invoke(state["messages"])
            return {"messages": [response]}
        except Exception as e:
            self.logger.error(f"Chatbot node failed: {e}")
            raise QueryExecutionError(f"Chatbot processing failed: {str(e)}") from e

    def build(self) -> "WorkflowBuilder":
        """Build the workflow graph.
        
        Returns:
            Self for method chaining
            
        Raises:
            ValueError: If build fails
        """
        try:
            # Create tool node
            tool_node = ToolNode(tools=self.tools)

            # Create state graph
            graph_builder = StateGraph(AgentState)

            # Add nodes
            graph_builder.add_node("chatbot", self._chatbot_node)
            graph_builder.add_node("tools", tool_node)

            # Add edges
            graph_builder.add_edge(START, "chatbot")

            # Conditional routing: after chatbot, either use tools or end
            graph_builder.add_conditional_edges(
                "chatbot",
                tools_condition,
                {
                    "tools": "tools",
                    END: END,  # Route to END if no tool use
                },
            )

            # After tools, return to chatbot for next response
            graph_builder.add_edge("tools", "chatbot")

            # Compile graph
            self.graph = graph_builder.compile()
            self.logger.info("Workflow built successfully")

            return self

        except Exception as e:
            self.logger.error(f"Failed to build workflow: {e}")
            raise ValueError(f"Workflow build failed: {str(e)}") from e

    def get_graph(self):
        """Get compiled graph.
        
        Returns:
            Compiled graph
            
        Raises:
            ValueError: If graph not built
        """
        if self.graph is None:
            raise ValueError("Graph not built. Call build() first.")
        return self.graph

    def invoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Invoke the graph with input data.
        
        Args:
            input_data: Input dictionary with 'messages' key
            
        Returns:
            Graph output
            
        Raises:
            QueryExecutionError: If invocation fails
        """
        try:
            if self.graph is None:
                raise ValueError("Graph not built. Call build() first.")

            # Initialize context if not present
            if "context" not in input_data:
                input_data["context"] = {}
            if "tool_results" not in input_data:
                input_data["tool_results"] = {}

            result = self.graph.invoke(input_data)
            return result

        except Exception as e:
            self.logger.error(f"Graph invocation failed: {e}")
            raise QueryExecutionError(f"Failed to invoke workflow: {str(e)}") from e

    async def ainvoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Async invoke the graph with input data.
        
        Args:
            input_data: Input dictionary with 'messages' key
            
        Returns:
            Graph output
            
        Raises:
            QueryExecutionError: If invocation fails
        """
        try:
            if self.graph is None:
                raise ValueError("Graph not built. Call build() first.")

            # Initialize context if not present
            if "context" not in input_data:
                input_data["context"] = {}
            if "tool_results" not in input_data:
                input_data["tool_results"] = {}

            result = await self.graph.ainvoke(input_data)
            return result

        except Exception as e:
            self.logger.error(f"Async graph invocation failed: {e}")
            raise QueryExecutionError(f"Failed to invoke workflow: {str(e)}") from e

    def stream(self, input_data: Dict[str, Any]):
        """Stream the graph output.
        
        Args:
            input_data: Input dictionary with 'messages' key
            
        Yields:
            Intermediate graph outputs
        """
        if self.graph is None:
            raise ValueError("Graph not built. Call build() first.")

        # Initialize context if not present
        if "context" not in input_data:
            input_data["context"] = {}
        if "tool_results" not in input_data:
            input_data["tool_results"] = {}

        try:
            for event in self.graph.stream(input_data):
                yield event
        except Exception as e:
            self.logger.error(f"Graph streaming failed: {e}")
            raise QueryExecutionError(f"Failed to stream workflow: {str(e)}") from e

