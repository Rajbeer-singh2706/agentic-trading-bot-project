import sys, os
from pathlib import Path
from dotenv import load_dotenv
from typing import List
from uuid import uuid4

# Ensure the `src` directory is on sys.path when this module is run directly.
# This lets `from utils...` succeed from the repo root.
# ROOT_DIR = Path(__file__).resolve().parents[1]
# if str(ROOT_DIR) not in sys.path:
#     sys.path.insert(0, str(ROOT_DIR))

## FROM LANGCHAIN 
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore

## FROM PINECONE 
from pinecone import ServerlessSpec, Pinecone

### MY 
from utils.mylogger import setup_logger
from utils.config_loader import load_config
from utils.model_loader import ModelLoader
from utils.exceptions import TradingBotException

logger = setup_logger(__name__)

class VectorDBManager:
    def __init__(self):
        try:
            logger.info("Initializing data ingestion pipeline")
            load_dotenv()
            self._load_env_variables()
            self.model_loader = ModelLoader()
            self.config = load_config()
        except Exception as exc:
            logger.exception("Failed to initialize data ingestion pipeline")
            raise TradingBotException(exc,sys )

    def _load_env_variables(self):
        try:
            required_vars = [
                "GOOGLE_API_KEY", "GROQ_API_KEY","PINECONE_API_KEY"]

            missing_vars = [var for var in required_vars if os.getenv(var) is None]
            if missing_vars:
                raise EnvironmentError(f"Missing environment variables: {missing_vars}")

            self.google_api_key = os.getenv("GOOGLE_API_KEY")
            self.groq_api_key = os.getenv("GROQ_API_KEY")
            self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        except Exception as e:
            raise TradingBotException(e, sys)
        
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into smaller chunks.
        """
        try:
            logger.info("chunk_documents() start ")
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len
            )
            docs = text_splitter.split_documents(documents)
            logger.info(f"chunk_documents() END : {len(docs)} ")
            return docs
        except Exception as e:
            logger.error(f"chunk_documents() Error : {e} ")
            raise TradingBotException(e, sys)

    def create_vector_store(self):
        """
        Create Pinecone index and return vector store object.
        """
        try:
            logger.info("create_vector_store() start ")
            pinecone_client = Pinecone(api_key=self.pinecone_api_key)
            index_name = self.config["vector_db"]["index_name"]

            existing_indexes = [i.name for i in pinecone_client.list_indexes()]

            ## Create index if not exists 
            if index_name not in existing_indexes:
                pinecone_client.create_index(
                    name=index_name,
                    dimension=384,  # Update based on embedding model
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    ),
                )
            
            ## Load the INdex 
            index = pinecone_client.Index(index_name)

            ## Load Vector Store
            vector_store = PineconeVectorStore(
                index=index,
                embedding=self.model_loader.load_embeddings()
            )
            logger.info(f"create_vector_store() END : {vector_store} ")
            return vector_store
        
        except Exception as e:
            logger.error(f"create_vector_store() Error : {e} ")
            raise TradingBotException(e, sys) 
    
    def store_documents(self, vector_store: PineconeVectorStore, documents: List[Document]):
        """
        Store chunked documents into vector DB.
        """
        try:
            logger.info("store_documents() start ")
            uuids = [str(uuid4()) for _ in range(len(documents))]
            vector_store.add_documents(documents=documents, ids = uuids) 
            logger.info("store_documents() eND ")
            return "Files Sucessfully processed and stored."
        except Exception as e:
            logger.error(f"store_documents() Error : {e} ")
            raise TradingBotException(e, sys)
        
    def store_in_vector_db(self,documents: List[Document]):
        """
        Complete pipeline:
        1. Chunk documents
        2. Create vector store 
        3. store documents
        """
        logger.info("store_in_vector_db() start ")
        try:
            chunked_documents = self.chunk_documents(documents=documents)
            vector_store = self.create_vector_store()

            status = self.store_documents(
                vector_store=vector_store,
                documents=chunked_documents
            )
            logger.info(f"store_in_vector_db() end : status : {status}")
            return status
        except Exception as e:
            logger.error(f"store_in_vector_db() end : Exception : {e}")
            raise TradingBotException(e, sys)


# if __name__ == '__main__':
#     obj = VectorDBManager()
#     docs = [
#         Document(page_content="this is document1", metadata={}),
#         Document(page_content="this is document2", metadata={}),
#         Document(page_content="this is document3", metadata={}),
#     ]
#     status = obj.store_in_vector_db(docs)
#     print(status)


# python src/ingestion/vector_db_manager.py