import psycopg2
import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

load_dotenv()

logger.info(f"DB_URL: {os.getenv('DATABASE_URL')}")

class DatabaseManager:
    def __init__(self):
        self.conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        self.cursor = self.conn.cursor()

    def create_alert_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS alerts (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            crypto VARCHAR(100) NOT NULL,
            threshold FLOAT NOT NULL
        );
        """
        self.cursor.execute(query)
        self.conn.commit()

    def add_alert(self, user_id, crypto, threshold):
        query = "INSERT INTO alerts (user_id, crypto, threshold) VALUES (%s, %s, %s)"
        self.cursor.execute(query, (user_id, crypto, threshold))
        self.conn.commit()

    def remove_alert(self, user_id, crypto):
        query = "DELETE FROM alerts WHERE user_id = %s AND crypto = %s"
        self.cursor.execute(query, (user_id, crypto))
        self.conn.commit()

    def get_alerts(self):
        query = "SELECT * FROM alerts"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def close(self):
        self.cursor.close()
        self.conn.close()
