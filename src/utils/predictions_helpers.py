from datetime import datetime
from decimal import Decimal
from typing import List, Tuple
import discord
from discord import User
import requests
import logging

from bot import CryptoBot


logger = logging.getLogger(__name__)


async def fetch_actual_price(
    bot: CryptoBot, crypto: str, prediction_date: datetime
) -> float:
    """Fetches the actual price of a cryptocurrency for a given date.

    Args:
        bot (CryptoBot): The bot instance with necessary configurations and data.
        crypto (str): The cryptocurrency symbol or name.
        prediction_date (datetime): The date for which to fetch the price.

    Returns:
        float: The actual price of the cryptocurrency in USD, or None if not found.
    """
    try:
        logger.info(f"Fetching actual price for {crypto} at {prediction_date}")

        # Resolve the cryptocurrency
        crypto_id = bot.crypto_map.get(crypto.lower())

        formatted_date = prediction_date.strftime("%d-%m-%Y")
        url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}/history?date={formatted_date}"

        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data.get("market_data", {}).get("current_price", {}).get("usd", None)
        else:
            logger.error(
                f"Error fetching actual price. Status code: [{response.status_code}]"
            )
            return None
    except Exception as e:
        logger.error(f"Error fetching price for [{crypto}] on [{prediction_date}]: {e}")
        return None


async def format_leaderboard_table(
    leaderboard_data: List[Tuple[int, str, datetime, Decimal, Decimal, Decimal]],
    interaction: discord.Interaction,
) -> str:
    """Formats the leaderboard data into a table string for display.

    Args:
        leaderboard_data (List[Tuple[int, str, datetime, Decimal, Decimal, Decimal]]):
            List of tuples containing user data for the leaderboard.
        interaction (discord.Interaction): Discord interaction for fetching user information.

    Returns:
        str: Formatted leaderboard message as a code block.
    """
    logger.info("Formatting leaderboard table")
    logger.debug(f"leaderboard_data: {leaderboard_data}")

    leaderboard_message = "```\n"
    leaderboard_message += f"{'Rank':<5} {'User':<15} {'Crypto':<10} {'Accuracy':<10} {'Predicted':<15} {'Actual':<15} {'Date':<10}\n"
    leaderboard_message += "-" * 80 + "\n"

    rank = 1
    for (
        user_id,
        crypto,
        prediction_date,
        predicted_price,
        actual_price,
        accuracy,
    ) in leaderboard_data:
        user: User = await interaction.client.fetch_user(user_id)
        username = user.name if user else f"User {user_id}"

        # Format the prediction details
        formatted_date = prediction_date.strftime("%d-%m-%Y")

        # Append the user's prediction to the leaderboard message
        leaderboard_message += (
            f"{rank:<5} {username:<15} {crypto:<10} {accuracy:<10.2%} "
            f"${predicted_price:<15,.2f} ${actual_price:<15,.2f} {formatted_date:<10}\n"
        )

        rank += 1

        # Limit the display to the top 25 entries
        if rank > 25:
            break

    leaderboard_message += "```"
    return leaderboard_message


async def format_predictions_table(
    predictions: List[Tuple[int, int, str, datetime, Decimal, Decimal, Decimal]],
    interaction: discord.Interaction = None,
) -> str:
    """Formats a list of predictions into a readable table format.

    Args:
        predictions (List[Tuple[int, int, str, datetime, Decimal, Decimal, Decimal]]):
            List of tuples containing prediction details
                (id, user_id, crypto, date, predicted_price, actual_price and accuracy).

    Returns:
        str: A formatted string table for the user's predictions as a code block.
    """
    logger.info("Formatting predictions table")

    table_message = "```\n"
    if interaction is not None:
        table_message += f"{'ID':<5} {'User':<15} {'Crypto':<15} {'Date':<15} {'Predicted Price':<15} {'Actual Price':<15} {'Accuracy':<10}\n"
        table_message += "-" * 100 + "\n"
    else:
        table_message += f"{'ID':<5} {'Crypto':<15} {'Date':<15} {'Predicted Price':<15} {'Actual Price':<15} {'Accuracy':<10}\n"
        table_message += "-" * 80 + "\n"

    for (
        id,
        user_id,
        crypto,
        prediction_date,
        predicted_price,
        actual_price,
        accuracy,
    ) in predictions:
        formatted_date = prediction_date.strftime("%d-%m-%Y")

        # Set values to "N/A" if they are None
        actual_price_str = (
            f"${actual_price:<.2f}" if actual_price is not None else "N/A"
        )
        accuracy_str = f"{accuracy:<.2%}" if accuracy is not None else "N/A"

        if interaction is not None:
            user: User = await interaction.client.fetch_user(user_id)
            username = user.name if user else f"User {user_id}"
            table_message += (
                f"{id:<5} {username:<15} {crypto:<15} {formatted_date:<15} ${predicted_price:<15.2f} "
                f"{actual_price_str:<15} {accuracy_str:<10}\n"
            )
        else:
            table_message += (
                f"{id:<5} {crypto:<15} {formatted_date:<15} ${predicted_price:<15.2f} "
                f"{actual_price_str:<15} {accuracy_str:<10}\n"
            )
        logger.debug(f"table_message: {table_message}")  # ? debug

    table_message += "```"
    return table_message


def calculate_prediction_accuracy(
    predicted_price: Decimal | float, actual_price: Decimal | float
) -> Decimal:
    """Calculates the accuracy of a given prediction based on the actual price.

    Args:
        predicted_price (Decimal | float): The predicted price of the cryptocurrency.
        actual_price (Decimal | float): The actual price of the cryptocurrency on the prediction date.

    Raises:
        ValueError: If either predicted_price or actual_price is not provided.

    Returns:
        Decimal: Accuracy value between 0 and 1 representing the accuracy of the prediction.
    """
    logger.info(
        f"Calculating prediction accuracy: predicted price [{predicted_price}] | actual price [{actual_price}]"
    )

    if predicted_price is None or actual_price is None:
        raise ValueError("Both predicted_price and actual_price must be provided")

    accuracy = Decimal(1) - abs(
        Decimal(predicted_price) - Decimal(actual_price)
    ) / Decimal(actual_price)

    # Clamp the accuracy to a range of [0, 1] to handle any edge cases
    return max(Decimal(0), min(accuracy, Decimal(1)))
