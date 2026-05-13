import sys , os 
import tempfile
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader

### from utils loads 
from utils.mylogger import setup_logger
from utils.exceptions import TradingBotException
from ingestion.vector_db_manager import VectorDBManager


logger = setup_logger(__name__)

class DataIngestion:
    """
    Class to handle document loading, transformation and ingestion into Vector Store.
    """
    def __init__(self):
        try:
            logger.info("Initializing data ingestion pipeline")
            self.vector_db_manager = VectorDBManager()
        except Exception as exc:
            logger.exception("Failed to initialize data ingestion pipeline")
            raise TradingBotException(exc,sys )
        
    def load_documents(self,uploaded_files):
        try:
            documents = []
            for uploaded_file in uploaded_files:
                file_ext = os.path.splitext(uploaded_file.filename)[1].lower()
                suffix = file_ext if file_ext in ['.pdf', '.docx'] else '.tmp'

                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                    temp_file.write(uploaded_file.file.read())
                    temp_path = temp_file.name
                
                if file_ext == '.pdf':
                    loader = PyPDFLoader(temp_path)
                    documents.extend(loader.load())
                elif file_ext == '.docx':
                    loader = Docx2txtLoader(temp_path)
                    documents.extend(loader.load())
                else:
                    print(f"Unsupoorted file type: {uploaded_file.filename}")
            return documents
        except Exception as e:
            raise TradingBotException(e, sys)

    def run_pipeline(self, uploaded_files):
        logger.info("run_pipeline() start ")
        try:
            documents = self.load_documents(uploaded_files)
            if not documents:
                print("No valid Document found.")
                return 
            status = self.vector_db_manager.store_in_vector_db(documents)
            logger.info(f"run_pipeline() status: {status} ")
            return status 
        except Exception as e:
            logger.error(f"run_pipeline() Exception: {e} ")
            raise TradingBotException(e,sys)
            

