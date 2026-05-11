import os 
from dotenv import load_dotenv
from langchain.tools import tool 
from langchain_community.utilities.polygon import PolygonAPIWrapper
from langchain_pinecone import PineconeSparseVectorStore

### TAVILY 
from langchain_community.tools import TavilySearchResults

###Polygon financials
from langchain_community.tools.polygon.financials import PolygonFinancials

#from langchain_community.tools.bing_search import BingSearchResults 


### Import PineCone Library
from pinecone import Pinecone

## Import our Libraries 
from utils.model_loader import ModelLoader
from utils.config_loader import load_config
from data_models.models import RagToolSchema

## Load envrioment variables
load_dotenv()

model_loader=ModelLoader()
config = load_config()


@tool(args_schema=RagToolSchema)
def retriever_tool(question):
    """this is retriever tool"""
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    pc = Pinecone(api_key=pinecone_api_key)

    ## Load VEctor Store 
    vector_store = PineconeSparseVectorStore(
        index = pc.Index(config['vector_db']['index_name']),
        embedding=model_loader.load_embeddings()
    )

    ## Retriever
    retriever = vector_store.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs = {
                "k": config['retriever']['top_k'],
                "score_threshold": config['retriever']['score_threshold']
        }
    )
    ## INVOKE Retriever
    retriever_result = retriever.invoke(question)
    return retriever_result


###### tool2 : Tavily Search ##########
tavilytool = TavilySearchResults(
    max_results = config['tools']['tavily']['max_results'],
    search_depth="advanced",
    include_answer=True,
    include_raw_content=True
)


###### tool3 : PolygonFinancials ##########
api_wrapper = PolygonAPIWrapper()
financials_tool = PolygonFinancials(api_wrapper=api_wrapper)
