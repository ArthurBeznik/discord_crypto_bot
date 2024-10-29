# alerts_manager.py

from typing import List, Tuple
from utils.logger import logging

logger = logging.getLogger(__name__)

class AlertsDatabaseManager:
    def __init__(self, conn):
        self.conn = conn

    def add_alert(self, user_id: int, crypto: str, threshold: float) -> None:
        query = "INSERT INTO alerts (user_id, crypto, threshold) VALUES (%s, %s, %s)"
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, (user_id, crypto, threshold))
            self.conn.commit()
            logger.info(f"Alert added for user {user_id} on {crypto} at {threshold}")
        except Exception as e:
            logger.error(f"Error adding alert: {e}")
            self.conn.rollback()

    def remove_alert(self, user_id: int, crypto: str) -> None:
        query = "DELETE FROM alerts WHERE user_id = %s AND crypto = %s"
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, (user_id, crypto))
            self.conn.commit()
            logger.info(f"Alert removed for user {user_id} on {crypto}")
        except Exception as e:
            logger.error(f"Error removing alert: {e}")
            self.conn.rollback()

    def get_alerts(self) -> List[Tuple[int, str, float]]:
        query = "SELECT user_id, crypto, threshold FROM alerts"
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query)
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error fetching alerts: {e}")
            return []
