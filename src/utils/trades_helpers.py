# trades_helpers.py

from typing import List, Tuple

from custom_types.trade_types import (
    TradeType,
)
from utils.logger import logging

logger = logging.getLogger(__name__)


async def format_trades_table(
    trades: List[TradeType],
) -> str:
    """Formats a list of trades into a readable table format.

    Args:
        trades (List[Tuple[int, int, int]]):
            List of tuples containing trades details (user_id, position_size, leverage).

    Returns:
        str: A formatted string table for the user's trades as a code block.
    """
    logger.info("Formatting trades table")

    table_message = "```\n"
    table_message += f"{'User ID':<10} {'Position Size':<15} {'Leverage':<10}\n"
    table_message += "-" * 40 + "\n"

    for user_id, position_size, leverage in trades:
        table_message += f"{user_id:<10} {position_size:<15} {leverage:<10}\n"

    table_message += "```"
    return table_message


async def format_trades_table_with_username(
    trades: List[Tuple[str, int, int]],
) -> str:
    """_summary_

    Args:
        trades (List[Tuple[str, int, int]]): _description_

    Returns:
        str: _description_
    """

    logger.info("Formatting trades table")

    table_message = "```\n"
    table_message += f"{'User Name':<20} {'Position Size':<15} {'Leverage':<10}\n"
    table_message += "-" * 45 + "\n"

    for user_name, position_size, leverage in trades:
        table_message += f"{user_name:<20} {position_size:<15} {leverage:<10}\n"

    table_message += "```"
    return table_message
