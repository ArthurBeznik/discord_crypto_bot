# db_init.py

import psycopg2
from utils.config import DATABASE_URL
from utils.logger import logging

logger = logging.getLogger(__name__)

class DBInitializer:
    def __init__(self):
        try:
            self.conn = psycopg2.connect(DATABASE_URL)
            self.conn.autocommit = False
            logger.info("Database connection established for initialization.")
        except Exception as e:
            logger.error(f"Error connecting to the database for initialization: {e}")
            raise e

    def initialize(self) -> None:
        """
        Initialize the database by creating tables defined in schema.sql.
        """
        try:
            with open('src/database/schema.sql', 'r') as schema_file:
                schema = schema_file.read()
            statements = [stmt.strip() for stmt in schema.split(';') if stmt.strip()]

            with self.conn.cursor() as cursor:
                for statement in statements:
                    try:
                        cursor.execute(statement)
                        logger.info("Executed statement successfully")
                    except psycopg2.errors.DuplicateTable as e:
                        logger.warning(f"Table already exists: {e}")
                        self.conn.rollback()
                    except Exception as e:
                        logger.error(f"Error executing statement: {e}")
                        self.conn.rollback()
                        raise e
            self.conn.commit()
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            self.conn.rollback()

    def close(self):
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed for initialization.")
