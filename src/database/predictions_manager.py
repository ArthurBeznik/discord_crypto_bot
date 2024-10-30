# predictions_manager.py

from datetime import datetime
from decimal import Decimal
from typing import List, Tuple

from custom_types.predictions_types import PredictionType
from utils.logger import logging

logger = logging.getLogger(__name__)


class PredictionsDatabaseManager:
    def __init__(self, conn):
        self.conn = conn

    def add_prediction(
        self,
        user_id: int,
        crypto: str,
        prediction_date: str,
        predicted_price: float,
        actual_price: float,
    ) -> None:
        logger.info(f"Adding prediction to DB for user [{user_id}]")

        query = """
        INSERT INTO predictions (user_id, crypto, prediction_date, predicted_price, actual_price)
        VALUES (%s, %s, %s, %s, %s)
        """
        logger.debug(f"query: {query}")  # ? debug

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    query,
                    (user_id, crypto, prediction_date, predicted_price, actual_price),
                )
            self.conn.commit()
            logger.info(
                f"Prediction added: [{crypto}] on [{prediction_date}] at [{predicted_price}] by user [{user_id}]"
            )
        except Exception as e:
            logger.error(f"Error adding prediction: {e}")
            self.conn.rollback()

    def get_predictions(self, user_id: int = None) -> List[PredictionType]:
        if user_id:
            logger.info(f"Getting predictions from DB for user [{user_id}]")
            query = "SELECT id, user_id, crypto, prediction_date, predicted_price, actual_price, accuracy FROM predictions WHERE user_id = %s"
            params = (user_id,)
        else:
            logger.info("Getting all predictions from DB")
            query = "SELECT id, user_id, crypto, prediction_date, predicted_price, actual_price, accuracy FROM predictions"
            params = ()
        logger.debug(f"query: {query}")  # ? debug

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error fetching predictions: {e}")
            return []

    def get_pending_predictions(self, date: datetime) -> List[Tuple[int, str, datetime, Decimal, Decimal]]:
        logger.info(f"Getting pending predictions before date [{date}]")

        query = """
            SELECT id, crypto, prediction_date, predicted_price, actual_price
            FROM predictions
            WHERE actual_price IS NULL AND prediction_date < %s
        """
        logger.debug(f"query: {query}")  # ? debug

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, (date,))
                results = cursor.fetchall()
                logger.info(f"Found {len(results)} pending predictions")
                return results
        except Exception as e:
            logger.error(f"Error fetching pending predictions: {e}")
            return []

    def get_completed_predictions(self) -> List[Tuple[int, str, datetime, Decimal, Decimal, Decimal]]:
        logger.info("Getting all completed predictions")

        query = """
            SELECT user_id, crypto, prediction_date, predicted_price, actual_price, accuracy
            FROM predictions
            WHERE actual_price IS NOT NULL AND accuracy IS NOT NULL
        """
        logger.debug(f"query: {query}")  # ? debug

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
                logger.info(f"Found {len(results)} completed predictions")
                return results
        except Exception as e:
            logger.error(f"Error fetching completed predictions: {e}")
            return []

    def clear_predictions(self, user_id: int) -> None:
        logger.info(f"Clearing predictions from DB for user [{user_id}]")

        query = "DELETE FROM predictions WHERE user_id = %s"
        logger.debug(f"query: {query}")  # ? debug

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, (user_id,))
            self.conn.commit()
            logger.info(f"All predictions removed for user [{user_id}]")
        except Exception as e:
            logger.error(f"Error clearing predictions: {e}")
            self.conn.rollback()

    def remove_prediction(self, user_id: int, prediction_id: int) -> bool:
        logger.info(
            f"Removing prediction [{prediction_id}] from DB for user [{user_id}]"
        )

        query = "DELETE FROM predictions WHERE user_id = %s AND id = %s"
        logger.debug(f"query: {query}")  # ? debug

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, (user_id, prediction_id))
            self.conn.commit()
            logger.info(
                f"Prediction [{prediction_id}] removed successfully for user [{user_id}]"
            )
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error removing prediction [{prediction_id}]: {e}")
            self.conn.rollback()
            return False

    def update_pending_prediction(
        self, prediction_id: int, actual_price: float, accuracy: Decimal
    ) -> bool:
        logger.info(
            f"Updating actual_price to [{actual_price}] and accuracy to [{accuracy}] for prediction [{prediction_id}] in the DB"
        )

        query = """
            UPDATE predictions
            SET actual_price = %s, accuracy = %s
            WHERE id = %s AND actual_price IS NULL
        """
        logger.debug(f"query: {query}")  # ? debug

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, (actual_price, accuracy, prediction_id))
            self.conn.commit()

            if cursor.rowcount > 0:
                logger.info(
                    f"Prediction [{prediction_id}] updated successfully, actual price: [{actual_price}] | accuracy: [{accuracy}]"
                )
                return True
            else:
                logger.info(
                    f"No update made for prediction [{prediction_id}], it may already have an actual price and/or accuracy"
                )
                return False
        except Exception as e:
            logger.error(
                f"Error updating actual price for prediction [{prediction_id}]: {e}"
            )
            self.conn.rollback()
            return False
