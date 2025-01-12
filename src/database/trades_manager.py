# trades_manager.py

# from datetime import datetime
# from decimal import Decimal
# from typing import List, Tuple

from typing import List
from psycopg2 import DatabaseError

from custom_types.trade_types import (
    # AllTradesType,
    TradeType,
)
from utils.exceptions import DatabaseOperationException
from utils.logger import logging

logger = logging.getLogger(__name__)


class TradesDatabaseManager:
    def __init__(self, conn):
        self.conn = conn

    # ########################################################################################
    # CREATE
    # ########################################################################################
    def create_trade(self, user_id: int, position_size: int, leverage: int) -> None:
        logger.info(f"Creating new trade for user [{user_id}] in DB")

        query = """
            INSERT INTO trades (user_id, position_size, leverage)
            VALUES (%s, %s, %s)
        """
        params = (
            user_id,
            position_size,
            leverage,
        )
        logger.debug(f"Executing query: {query} with parameters: {params}")  # ? debug

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, params)
            self.conn.commit()
            logger.info(
                f"Successfully added trade: [{position_size}] at [{leverage}] by user [{user_id}]"
            )
        except Exception as e:
            logger.error(f"Error adding trade: {e}")
            self.conn.rollback()
            raise DatabaseOperationException("create_trade", str(e))
            raise DatabaseError(f"{e}")

    # ########################################################################################
    # READ
    # ########################################################################################
    def get_trade(self, trade_id: int):
        logger.info(f"Fetching trade [{trade_id}] from DB")
        query = """
            SELECT *
            FROM trades
            WHERE trade_id = %s
        """
        params = (trade_id,)

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, params)
                trade = cursor.fetchone()
            return trade
        except Exception as e:
            logger.error(f"Error fetching trade: {e}")
            raise DatabaseOperationException("get_trade", str(e))

    def get_all_trades(self, user_id: int = None) -> List[TradeType]:
        logger.info("Fetching all trades from DB")
        query = """
            SELECT user_id, position_size, leverage
            FROM trades
        """
        params = ()
        if user_id is not None:
            query += " WHERE user_id = %s"
            params = (user_id,)

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, params)
                trades = cursor.fetchall()
            return trades
        except Exception as e:
            logger.error(f"Error fetching all trades: {e}")
            raise DatabaseOperationException("get_all_trades", str(e))

    # ########################################################################################
    # UPDATE
    # ########################################################################################
    def update_trade(self, trade_id: int, position_size: int, leverage: int) -> None:
        logger.info(f"Updating trade [{trade_id}] in DB")
        query = """
            UPDATE trades
            SET position_size = %s, leverage = %s
            WHERE trade_id = %s
        """
        params = (position_size, leverage, trade_id)
        logger.debug(f"Executing query: {query} with parameters: {params}")

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, params)
            self.conn.commit()
            logger.info(f"Successfully updated trade [{trade_id}]")
        except Exception as e:
            logger.error(f"Error updating trade: {e}")
            self.conn.rollback()
            raise DatabaseOperationException("update_trade", str(e))

    # ########################################################################################
    # DELETE
    # ########################################################################################
    def delete_trade(self, trade_id: int) -> None:
        logger.info(f"Deleting trade [{trade_id}] from DB")
        query = "DELETE FROM trades WHERE trade_id = %s"
        params = (trade_id,)
        logger.debug(f"Executing query: {query} with parameters: {params}")

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, params)
            self.conn.commit()
            logger.info(f"Successfully deleted trade [{trade_id}]")
        except Exception as e:
            logger.error(f"Error deleting trade: {e}")
            self.conn.rollback()
            raise DatabaseOperationException("delete_trade", str(e))
