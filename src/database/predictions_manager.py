# predictions_manager.py

from datetime import datetime
from typing import List, Tuple
from utils.logger import logging

logger = logging.getLogger(__name__)

class PredictionsDatabaseManager:
    def __init__(self, conn):
        self.conn = conn

    def add_prediction(self, user_id: int, crypto: str, prediction_date: str, predicted_price: float) -> None:
        query = """
        INSERT INTO predictions (user_id, crypto, prediction_date, predicted_price)
        VALUES (%s, %s, %s, %s)
        """
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, (user_id, crypto, prediction_date, predicted_price))
            self.conn.commit()
            logger.info(f"Prediction added: {crypto} on {prediction_date} at {predicted_price} by user {user_id}.")
        except Exception as e:
            logger.error(f"Error adding prediction: {e}")
            self.conn.rollback()

    def get_predictions(self, user_id: int = None) -> List[Tuple[int, int, str, datetime, float]]:
        if user_id:
            query = "SELECT id, user_id, crypto, prediction_date, predicted_price FROM predictions WHERE user_id = %s"
            params = (user_id,)
        else:
            query = "SELECT id, user_id, crypto, prediction_date, predicted_price FROM predictions"
            params = ()

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error fetching predictions: {e}")
            return []

    def clear_predictions(self, user_id: int) -> None:
        query = "DELETE FROM predictions WHERE user_id = %s"
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, (user_id,))
            self.conn.commit()
            logger.info(f"All predictions removed for user [{user_id}]")
        except Exception as e:
            logger.error(f"Error clearing predictions: {e}")
            self.conn.rollback()

    def remove_prediction(self, user_id: int, prediction_id: int) -> bool:
        query = "DELETE FROM predictions WHERE user_id = %s AND id = %s"
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, (user_id, prediction_id))
            self.conn.commit()
            logger.info(f"Prediction [{prediction_id}] removed for user [{user_id}]")
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error removing prediction: {e}")
            self.conn.rollback()
            return False
