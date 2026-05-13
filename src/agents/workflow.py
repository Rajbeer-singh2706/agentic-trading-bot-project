
## langgraph 
from langgraph.graph import StateGraph, START, END 
from langgraph.graph.message import add_messages
from typing_extensions import Annotated, TypedDict
from langgraph.prebuilt.tool_node import ToolNode, tools_condition

## 
from utils.model_loader import ModelLoader
from toolkit.tools import retriever_tool, financials_tool, tavilytool


class State(TypedDict):
    messages: Annotated[list, add_messages]

class GraphBuilder:
    def __init__(self):
        self.model = ModelLoader() 
        self.llm = self.model.load_llm()
        self.tools = [retriever_tool, financials_tool, tavilytool]
        self.llm_with_tools = self.llm.bind_tools(self.tools) 
        self.graph = None  

    def _chatbot_node(self,state:State):
        return {"messages": [self.llm_with_tools.invoke(state['messages'])]}
    
    def build(self):
        tool_node = ToolNode(tools=self.tools)

        graph_builder = StateGraph(State) 
        
        ### ADD NODE 
        graph_builder.add_node("chatbot", self._chatbot_node)
        graph_builder.add_node("tools", tool_node)

        ## ADD EDGE
        graph_builder.add_conditional_edges("chatbot", tools_condition)

        graph_builder.add_edge(START, "chatbot")
        graph_builder.add_edge("tools", "chatbot")

        ## where is end?
        self.graph = graph_builder.compile()

    def get_graph(self):
        if self.graph is None:
            raise ValueError("Graph not built. Call build() first.") 
        return self.graph

