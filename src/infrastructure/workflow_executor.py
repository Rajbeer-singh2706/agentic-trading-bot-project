"""Workflow executor for agent orchestration."""
from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, AIMessage

from agents.workflow import WorkflowBuilder
from domain.entities import QueryRequest, Message, MessageRole
from infrastructure.logging import get_logger


class WorkflowExecutor:
    """Executes agent workflows using LangGraph."""

    def __init__(self, llm, tools: List):
        """Initialize workflow executor.

        Args:
            llm: Language model instance
            tools: List of tools for the agent
        """
        self.workflow_builder = WorkflowBuilder(llm, tools)
        self.workflow = self.workflow_builder.build().compile()
        self.logger = get_logger(__name__)

    async def execute(self, request: QueryRequest) -> Dict[str, Any]:
        """Execute workflow for a query request.

        Args:
            request: Query request with question and context

        Returns:
            Workflow execution result
        """
        try:
            self.logger.info(f"Executing workflow for query: {request.question[:50]}...")

            # Convert domain messages to LangChain format
            messages = []
            for msg in request.messages:
                if msg.role == MessageRole.USER:
                    messages.append(HumanMessage(content=msg.content))
                elif msg.role == MessageRole.ASSISTANT:
                    messages.append(AIMessage(content=msg.content))

            # Add current question if not already in messages
            if not messages or not isinstance(messages[-1], HumanMessage):
                messages.append(HumanMessage(content=request.question))

            # Prepare initial state
            initial_state = {
                "messages": messages,
                "context": {
                    "session_id": request.session_id,
                    "metadata": request.metadata or {}
                },
                "tool_results": {}
            }

            # Execute workflow
            result = await self.workflow.ainvoke(initial_state)

            # Extract final response
            final_message = result["messages"][-1] if result["messages"] else None
            response_content = final_message.content if final_message else "No response generated"

            self.logger.info("Workflow execution completed")

            return {
                "answer": response_content,
                "context": result.get("context", {}),
                "tool_results": result.get("tool_results", {}),
                "messages": result.get("messages", [])
            }

        except Exception as e:
            self.logger.error(f"Workflow execution failed: {e}")
            raise