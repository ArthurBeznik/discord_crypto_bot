# db_manager.py

import psycopg2
from utils.config import DATABASE_URL
from utils.logger import logging
from .db_init import DBInitializer
from .alerts_manager import AlertsDatabaseManager
from .predictions_manager import PredictionsDatabaseManager

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.conn = psycopg2.connect(DATABASE_URL)
        self.alerts = AlertsDatabaseManager(self.conn)
        self.predictions = PredictionsDatabaseManager(self.conn)
        self.initializer = DBInitializer()

    def close(self):
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed.")
