import os
from dotenv import load_dotenv

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from custmor_support_system.utils.config_loader import load_config
from langchain_groq import ChatGroq

from .logger import setup_logger

logger = setup_logger(__name__)


class ModelLoader:
    """
    A Utility class to load embedding models and LLM models.
    """
    def __init__(self):
        load_dotenv()
        # print(os.environ.keys())
        self._validate_env()
        self.config = load_config()
    
    def _validate_env(self):
        """
        Validate necessary envrioment Variables
        """
        required_vars = ["GOOGLE_API_KEY", "GROQ_API_KEY"]
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        logger.warning(f"Missing : {missing_vars}")
        if missing_vars:
            raise EnvironmentError(f"Missing enviorment variables: {missing_vars}")


    def load_embeddings(self):
        """
        Load and return the embedding model.
        """
        logger.info("Loading Embedding model")
        default_embedding = self.config['embedding_models']['default']
        model_name = self.config['embedding_models']['models'][default_embedding]
           
        #embeddings = GoogleGenerativeAIEmbeddings(model=model_name)
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-V2")
        return embeddings

    def load_llm(self):
        """
        Load and return the LLM model.
        """ 
        logger.info("LLM loading...")
        default_llm = self.config['llms']['default']
        llm_model = self.config['llms']['models'][default_llm]
        model_name = llm_model['model_name']
        #llm = ChatGroq(model=model_name)
        llm = ChatGroq(model=model_name, api_key = self.groq_api_key)
        return llm 


# if __name__ == '__main__':
#     #print(load_config())
#     loader = ModelLoader()
#     #print(loader.load_embeddings())
#     print(loader.load_llm())
#     print(loader)
#     print("HERE ")


### python utils/model_loader.py