# manager.py

import psycopg2
import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

load_dotenv()

class DatabaseManager:
    def __init__(self) -> None:
        """
        Initializes the connection to the database using credentials from .env file.
        """
        try:
            self.conn = psycopg2.connect(os.getenv('DATABASE_URL'))
            self.cursor = self.conn.cursor()
            logger.info("Database connection established successfully.")
        except Exception as e:
            logger.error(f"Error connecting to the database: {e}")
            raise e

    def initialize(self) -> None:
        """
        Initialize the database by creating tables defined in schema.sql.
        """
        # with open('src/database/schema.sql', 'r') as schema_file:
        #     schema = schema_file.read()
        #     self.cursor.execute(schema)
        #     self.conn.commit()
        # logger.info("Database initialized and tables created.")

        try:
            with open('src/database/schema.sql', 'r') as schema_file:
                schema = schema_file.read()
                self.cursor.execute(schema)
                self.conn.commit()
            logger.info("Database initialized and tables created.")
        except Exception as e:
            logger.error(f"Error initializing the database: {e}")
            self.conn.rollback()

    # Alerts
    def add_alert(self, user_id: int, crypto: str, threshold: float) -> None:
        """
        Adds a new price alert for the user.

        Args:
            user_id (int): The ID of the user.
            crypto (str): The cryptocurrency symbol (e.g., 'BTC').
            threshold (float): The price threshold for the alert.
        """
        try:
            query = "INSERT INTO alerts (user_id, crypto, threshold) VALUES (%s, %s, %s)"
            self.cursor.execute(query, (user_id, crypto, threshold))
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
        try:
            query = "DELETE FROM alerts WHERE user_id = %s AND crypto = %s"
            self.cursor.execute(query, (user_id, crypto))
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
        try:
            query = "SELECT user_id, crypto, threshold FROM alerts"
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            logger.error(f"Error fetching alerts: {e}")
            return []

    # Predictions
    def add_prediction(self, user_id: int, symbol: str, prediction_date: str, predicted_price: float) -> None:
        """
        Records a price prediction for a cryptocurrency by a user.

        Args:
            user_id (int): The ID of the user making the prediction.
            symbol (str): The cryptocurrency symbol (e.g., 'BTC').
            prediction_date (str): The future date for the prediction (YYYY-MM-DD).
            predicted_price (float): The predicted price for the cryptocurrency.
        """
        try:
            query = """
            INSERT INTO predictions (user_id, symbol, prediction_date, predicted_price)
            VALUES (%s, %s, %s, %s)
            """
            self.cursor.execute(query, (user_id, symbol, prediction_date, predicted_price))
            self.conn.commit()
            logger.info(f"Prediction added: {symbol} on {prediction_date} at {predicted_price} by user {user_id}.")
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
        try:
            if user_id:
                query = "SELECT symbol, prediction_date, predicted_price FROM predictions WHERE user_id = %s"
                self.cursor.execute(query, (user_id,))
            else:
                query = "SELECT user_id, symbol, prediction_date, predicted_price FROM predictions"
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            logger.error(f"Error fetching predictions: {e}")
            return []

    def close(self) -> None:
        """
        Closes the database connection.
        """
        self.cursor.close()
        self.conn.close()
        logger.info("Database connection closed.")
