import sys 

from utils.logger import setup_logger
from utils.model_loader import ModelLoader
from utils.exceptions import TradingBotException

logger = setup_logger(__name__)


class DataIngestion:
    """
    Class to handle document loading, transformation and ingestion into Vector Store.
    """

    def __init__(self):
        try:
            logger.info("Initializing data ingestion pipeline")
            self.model_loader = ModelLoader()
        except Exception as exc:
            logger.exception("Failed to initialize data ingestion pipeline")
            raise TradingBotException(exc,sys )
            


