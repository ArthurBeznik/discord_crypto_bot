# alerts_manager.py

from typing import List, Tuple
from utils.logger import logging

logger = logging.getLogger(__name__)


class AlertsDatabaseManager:
    def __init__(self, conn):
        self.conn = conn

    # ########################################################################################
    # CREATE
    # ########################################################################################
    def create_alert(self, user_id: int, crypto: str, threshold: float) -> None:
        """
        Creates a new alert for a specific user and cryptocurrency.

        Args:
            user_id (int): The ID of the user for whom the alert is created.
            crypto (str): The cryptocurrency symbol the alert is associated with.
            threshold (float): The price threshold that triggers the alert.

        Raises:
            Exception: Logs an error and rolls back the transaction if an error occurs.
        """
        logger.info(f"Adding alert for user [{user_id}] on [{crypto}] at [{threshold}]")

        query = """
            INSERT INTO alerts (user_id, crypto, threshold) VALUES (%s, %s, %s)
        """
        params = (
            user_id,
            crypto,
            threshold,
        )
        logger.debug(f"Executing query: {query} with parameters: {params}")  # ? debug

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, params)
            self.conn.commit()
            logger.info(
                f"Successfully added alert for user [{user_id}] on [{crypto}] at [{threshold}]"
            )
        except Exception as e:
            logger.error(f"Error adding alert: {e}")
            self.conn.rollback()

    # ########################################################################################
    # READ
    # ########################################################################################
    def get_alerts(self, user_id: int = None) -> List[Tuple[int, int, str, float]]:
        """
        Retrieves all active alerts from the database, optionally for a specific user.

        Args:
            user_id (int, optional): The ID of the user whose alerts to retrieve.

        Returns:
            List[Tuple[int, int, str, float]]: A list of tuples, each containing alert_id,
            user_id, cryptocurrency symbol, and the threshold price for an alert.

        Raises:
            Exception: Logs an error if retrieval fails and returns an empty list.
        """
        if user_id:
            logger.info(f"Getting all alerts for user [{user_id}] from DB")
            query = """
                SELECT id, user_id, crypto, threshold 
                FROM alerts
                WHERE user_id = %s
            """
            params = (user_id,)
        else:
            logger.info("Getting all alerts from DB")
            query = """
                SELECT id, user_id, crypto, threshold 
                FROM alerts
            """
            params = ()
        logger.debug(f"Executing query: {query} with parameters: {params}")  # ? debug

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error fetching alerts: {e}")
            return []

    # ########################################################################################
    # DELETE
    # ########################################################################################
    def remove_alert(
        self,
        user_id: int,
        alert_id: int,
    ) -> None:
        """
        Removes an existing alert based on its unique alert ID.

        Args:
            alert_id (int): The ID of the alert to be removed.
            user_id (int): The ID of the user attempting to remove the alert.

        Raises:
            Exception: Logs an error and rolls back the transaction if deletion fails.
        """
        logger.info(f"Removing alert with ID [{alert_id}] for user [{user_id}]")

        query = """
            DELETE FROM alerts 
            WHERE id = %s AND user_id = %s
        """
        params = (
            alert_id,
            user_id,
        )
        logger.debug(f"Executing query: {query} with parameters: {params}")  # ? debug

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, params)
            self.conn.commit()

            if cursor.rowcount > 0:
                logger.info(
                    f"Successfully removed alert [{alert_id}] for user [{user_id}]"
                )
            else:
                error_message = f"Error finding alert [{alert_id}] for user [{user_id}]"
                logger.warning(error_message)
                raise ValueError(error_message)
        except Exception as e:
            logger.error(f"Error removing alert [{alert_id}]: {e}")
            self.conn.rollback()
            raise
