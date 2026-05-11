
from langgraph.graph.message import add_messages
from typing_extensions import Annotated, TypedDict

class State(TypedDict):
    messages: Annotated[list, add_messages]

class GraphBuilder:
    def __init__(self):
        self.model = None 
        self.llm = None 
        self.tools = None 
        self.llm_with_tools = None 
        self.graph = None  

    def _chatbot_node(self,state:State):
        return {"messages": []}
    
    def build(self):
        pass 

    def get_graph(self):
        if self.graph is None:
            raise ValueError("Graph not built. Call build() first.") 
        return self.graph

