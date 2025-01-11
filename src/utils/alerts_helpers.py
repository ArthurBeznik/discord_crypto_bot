# alerts_helpers.py

from typing import List, Tuple
import logging


logger = logging.getLogger(__name__)


def format_alerts_table(alerts: List[Tuple[int, int, str, float]]) -> str:
    """
    Formats a list of alerts into a readable table format for display.

    Args:
        alerts (List[Tuple[int, int, str, float]]): List of tuples containing
            alert details (alert_id, user_id, crypto, and threshold).

    Raises:
        ValueError: If there is an error while formatting the table.

    Returns:
        str: A formatted string table of the user's alerts as a code block.
    """
    logger.info("Formatting alerts table")
    logger.debug(f"alerts: {alerts}")  # ? debug

    try:
        table_message = "```\n"
        table_message += f"{'ID':<5} {'Crypto':<20} {'Threshold':<20}\n"
        table_message += "-" * 45 + "\n"

        for alert_id, _, crypto, threshold in alerts:
            table_message += f"{alert_id:<5} {crypto:<20} ${threshold:<.2f}\n"
            logger.debug(f"table_message: {table_message}")  # ? debug
        logger.debug(f"final table_message: {table_message}")  # ? debug

        table_message += "```"
        return table_message

    except Exception as e:
        logger.debug(f"exception type: {type(e)}")  # ? debug
        raise ValueError(f"{e}")
