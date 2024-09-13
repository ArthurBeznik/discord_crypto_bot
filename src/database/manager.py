# manager.py

import psycopg2

from utils.config import (
    logging,
    DATABASE_URL,
)

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self) -> None:
        """
        Initializes the connection to the database using credentials from .env file.
        """
        try:
            self.conn = psycopg2.connect(DATABASE_URL)
            self.conn.autocommit = False # Enable manual transaction control
            logger.info("Database connection established successfully.")
        except Exception as e:
            logger.error(f"Error connecting to the database: {e}")
            raise e

    def initialize(self) -> None:
        """
        Initialize the database by creating tables defined in schema.sql.
        """
        try:
            with open('src/database/schema.sql', 'r') as schema_file:
                schema = schema_file.read()

            # Split schema into individual statements based on ';'
            statements = [stmt.strip() for stmt in schema.split(';') if stmt.strip()]

            # Use context manager to ensure cursor is closed
            with self.conn.cursor() as cursor:
                for statement in statements:
                    try:
                        cursor.execute(statement)
                        logger.info("Executed statement successfully.")
                    except psycopg2.errors.DuplicateTable as e:
                        logger.warning(f"Table already exists: {e}")
                        self.conn.rollback()
                    except Exception as e:
                        logger.error(f"Error executing statement: {e}")
                        self.conn.rollback()
                        raise e # Stop initialization if a serious error occurs

            self.conn.commit() # Commit all if no errors occurred
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            self.conn.rollback()

    def add_alert(self, user_id: int, crypto: str, threshold: float) -> None:
        """
        Adds a new price alert for the user.

        Args:
            user_id (int): The ID of the user.
            crypto (str): The cryptocurrency symbol (e.g., 'BTC').
            threshold (float): The price threshold for the alert.
        """
        query = "INSERT INTO alerts (user_id, crypto, threshold) VALUES (%s, %s, %s)"
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, (user_id, crypto, threshold))
            self.conn.commit()
            logger.info(f"Alert added for user {user_id} on {crypto} at {threshold}.")
        except Exception as e:
            logger.error(f"Error adding alert: {e}")
            self.conn.rollback()

    def remove_alert(self, user_id: int, crypto: str) -> None:
        """
        Removes an existing alert for a user and a cryptocurrency.

        Args:
            user_id (int): The ID of the user.
            crypto (str): The cryptocurrency symbol.
        """
        query = "DELETE FROM alerts WHERE user_id = %s AND crypto = %s"
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, (user_id, crypto))
            self.conn.commit()
            logger.info(f"Alert removed for user {user_id} on {crypto}.")
        except Exception as e:
            logger.error(f"Error removing alert: {e}")
            self.conn.rollback()

    def get_alerts(self):
        """
        Fetches all the active alerts.

        Returns:
            list: A list of tuples containing user_id, crypto, and threshold.
        """
        logger.info("Getting alerts")

        query = "SELECT user_id, crypto, threshold FROM alerts"
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query)
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error fetching alerts: {e}")
            return []

    def add_prediction(self, user_id: int, crypto: str, prediction_date: str, predicted_price: float) -> None:
        """
        Records a price prediction for a cryptocurrency by a user.

        Args:
            user_id (int): The ID of the user making the prediction.
            crypto (str): The cryptocurrency (e.g., 'BTC').
            prediction_date (str): The future date for the prediction (YYYY-MM-DD).
            predicted_price (float): The predicted price for the cryptocurrency.
        """
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

    def get_predictions(self, user_id: int = None):
        """
        Fetches predictions from the database. Can fetch for all users or a specific user.

        Args:
            user_id (int, optional): The user ID to filter predictions. Defaults to None.

        Returns:
            list: A list of predictions.
        """
        logger.info("Getting predictions")

        if user_id:
            query = "SELECT crypto, prediction_date, predicted_price FROM predictions WHERE user_id = %s"
            params = (user_id,)
        else:
            query = "SELECT user_id, crypto, prediction_date, predicted_price FROM predictions"
            params = ()

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error fetching predictions: {e}")
            return []

    def close(self) -> None:
        """
        Closes the database connection.
        """
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed.")
