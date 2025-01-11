# predictions_manager.py

from datetime import datetime
from decimal import Decimal
from typing import List, Tuple

from psycopg2 import DatabaseError

from custom_types.predictions_types import PredictionType
from utils.exceptions import DatabaseOperationException
from utils.logger import logging

logger = logging.getLogger(__name__)


class PredictionsDatabaseManager:
    def __init__(self, conn):
        self.conn = conn

    # ########################################################################################
    # CREATE
    # ########################################################################################
    def create_prediction(
        self,
        user_id: int,
        crypto: str,
        prediction_date: str,
        predicted_price: float,
        actual_price: float,
        accuracy: Decimal,
    ) -> None:
        """Inserts a new prediction record for a user into the database.

        Args:
            user_id (int): The ID of the user making the prediction.
            crypto (str): The cryptocurrency symbol.
            prediction_date (str): The date of the prediction.
            predicted_price (float): The predicted price.
            actual_price (float): The actual price.
            accuracy (Decimal): The accuracy of the prediction.
        """
        logger.info(f"Creating new prediction for user [{user_id}] into DB")

        query = """
            INSERT INTO predictions (user_id, crypto, prediction_date, predicted_price, actual_price, accuracy)
            VALUES (%s, %s, %s, %s, %s, %s)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (
            user_id,
            crypto,
            prediction_date,
            predicted_price,
            actual_price,
            accuracy,
        )
        logger.debug(f"Executing query: {query} with parameters: {params}")  # ? debug

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, params)
            self.conn.commit()
            logger.info(
                f"Successfully added prediction: [{crypto}] on [{prediction_date}] at [{predicted_price}] by user [{user_id}]"
            )
        except Exception as e:
            logger.error(f"Error adding prediction: {e}")
            self.conn.rollback()
            raise DatabaseOperationException("create_prediction", str(e))
            raise DatabaseError(f"{e}")

    # ########################################################################################
    # READ
    # ########################################################################################
    def get_predictions(self, user_id: int = None) -> List[PredictionType]:
        """Retrieves predictions from the database, optionally for a specific user.

        Args:
            user_id (int, optional): The ID of the user whose predictions to retrieve.

        Returns:
            List[PredictionType]: A list of prediction records from the database.
        """
        if user_id is not None:
            logger.info(f"Getting predictions from DB for user [{user_id}]")
            query = """
                SELECT id, user_id, crypto, prediction_date, predicted_price, actual_price, accuracy 
                FROM predictions 
                WHERE user_id = %s
            """
            params = (user_id,)
        else:
            logger.info("Getting all predictions from DB")
            query = """
                SELECT id, user_id, crypto, prediction_date, predicted_price, actual_price, accuracy 
                FROM predictions
            """
            params = ()
        logger.debug(f"Executing query: {query} with parameters: {params}")  # ? debug

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error fetching predictions: {e}")
            return []

    def get_pending_predictions(
        self, date: datetime
    ) -> List[Tuple[int, str, datetime, Decimal, Decimal]]:
        """Fetches pending predictions with prediction dates before a specified date.

        Args:
            date (datetime): The cutoff date for pending predictions.

        Returns:
            List[Tuple[int, str, datetime, Decimal, Decimal]]: A list of pending predictions.
        """
        logger.info(f"Getting pending predictions before date [{date}]")

        query = """
            SELECT id, crypto, prediction_date, predicted_price, actual_price
            FROM predictions
            WHERE actual_price IS NULL AND prediction_date < %s
        """
        params = (date,)
        logger.debug(f"Executing query: {query} with parameters: {params}")  # ? debug

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, params)
                results = cursor.fetchall()
                logger.info(f"Successfully found [{len(results)}] pending predictions")
                return results
        except Exception as e:
            logger.error(f"Error fetching pending predictions: {e}")
            return []

    def get_completed_predictions(
        self,
    ) -> List[Tuple[int, str, datetime, Decimal, Decimal, Decimal]]:
        """Retrieves all completed predictions with an actual price and calculated accuracy.

        Returns:
            List[Tuple[int, str, datetime, Decimal, Decimal, Decimal]]: A list of completed predictions.
        """
        logger.info("Getting all completed predictions")

        query = """
            SELECT user_id, crypto, prediction_date, predicted_price, actual_price, accuracy
            FROM predictions
            WHERE actual_price IS NOT NULL AND accuracy IS NOT NULL
        """
        logger.debug(f"Executing query: {query}")  # ? debug

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
                logger.info(
                    f"Successfully found [{len(results)}] completed predictions"
                )
                return results
        except Exception as e:
            logger.error(f"Error fetching completed predictions: {e}")
            return []

    # ########################################################################################
    # UPDATE
    # ########################################################################################
    def update_pending_prediction(
        self, prediction_id: int, actual_price: float, accuracy: Decimal
    ) -> bool:
        """Updates a pending prediction's actual price and accuracy.

        Args:
            prediction_id (int): The ID of the prediction to update.
            actual_price (float): The actual price to set.
            accuracy (Decimal): The accuracy to set.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        logger.info(
            f"Updating actual_price to [{actual_price}] and accuracy to [{accuracy}] for prediction [{prediction_id}] in the DB"
        )

        query = """
            UPDATE predictions
            SET actual_price = %s, accuracy = %s
            WHERE id = %s AND actual_price IS NULL
        """
        params = (
            actual_price,
            accuracy,
            prediction_id,
        )
        logger.debug(f"Executing query: {query} with parameters: {params}")  # ? debug

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, params)
            self.conn.commit()

            if cursor.rowcount > 0:
                logger.info(
                    f"Successfully updated prediction [{prediction_id}], actual price: [{actual_price}] | accuracy: [{accuracy}]"
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

    # ########################################################################################
    # DELETE
    # ########################################################################################
    def clear_predictions(self, user_id: int = None) -> None:
        """Clears all predictions from the database for a specific user or all users if no user_id is provided.

        Args:
            user_id (int, optional): The ID of the user whose predictions to clear. If None, clears predictions for all users.
        """
        if user_id is not None:
            logger.info(f"Clearing predictions from DB for user [{user_id}]")
            query = """
                DELETE FROM predictions WHERE user_id = %s
            """
            params = (user_id,)
        else:
            logger.info("Clearing all predictions from DB for all users")
            query = """
                DELETE FROM predictions
            """
            params = ()

        logger.debug(f"Executing query: {query} with parameters: {params}")  # ? debug

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, params)
            self.conn.commit()

            if user_id is not None:
                logger.info(f"Successfully removed all predictions for user [{user_id}]")
            else:
                logger.info("Successfully removed all predictions for all users")
        except Exception as e:
            logger.error(f"Error clearing predictions: {e}")
            self.conn.rollback()


    def remove_prediction(self, user_id: int, prediction_id: int) -> bool:
        """Removes a specific prediction for a user from the database.

        Args:
            user_id (int): The ID of the user.
            prediction_id (int): The ID of the prediction to remove.

        Returns:
            bool: True if the prediction was removed, False otherwise.
        """
        logger.info(
            f"Removing prediction [{prediction_id}] from DB for user [{user_id}]"
        )

        query = """
            DELETE FROM predictions WHERE user_id = %s AND id = %s
        """
        params = (
            user_id,
            prediction_id,
        )
        logger.debug(f"Executing query: {query} with parameters: {params}")  # ? debug

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, params)
            self.conn.commit()
            logger.info(
                f"Successfully removed prediction [{prediction_id}] for user [{user_id}]"
            )
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error removing prediction [{prediction_id}]: {e}")
            self.conn.rollback()
            return False
