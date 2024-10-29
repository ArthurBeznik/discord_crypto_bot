from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Tuple
import discord
from discord import User
import requests
import logging

from bot import CryptoBot

logger = logging.getLogger(__name__)


async def fetch_actual_price(
    bot: CryptoBot, crypto: str, prediction_date: datetime
) -> float:
    """
    Fetches the actual price for a given cryptocurrency on a given date from CoinGecko API.
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
                f"Failed to fetch actual price. Status code: {response.status_code}"
            )
            return None
    except Exception as e:
        logger.error(f"Error fetching price for {crypto} on {prediction_date}: {e}")
        return None


def format_user_scores(
    user_id: int,
    username: str,
    user_predictions: List[Tuple[str, float, float, float, datetime]],
) -> str:
    user_score_message = ""
    for (
        crypto,
        predicted_price,
        actual_price,
        accuracy,
        prediction_date,
    ) in user_predictions:
        formatted_date = prediction_date.strftime("%d-%m-%Y")
        user_score_message += (
            f"{crypto:<25} {accuracy:<20.2%} ${predicted_price:<20.2f} "
            f"${actual_price:<20.2f} {formatted_date:<20}\n"
        )
    return user_score_message


async def calculate_user_scores(
    bot: CryptoBot,
    predictions: List[Tuple[int, int, str, datetime, float]],
    current_date: datetime,
) -> Tuple[
    Dict[int, List[Tuple[str, float, float, float, datetime]]], Dict[int, float]
]:
    logger.info("Calculating user scores")

    user_scores = {}
    for id, user_id, crypto, prediction_date, predicted_price in predictions:
        if prediction_date > current_date:
            continue

        actual_price: float = await fetch_actual_price(bot, crypto, prediction_date)

        logger.debug(f"actual_price: {actual_price}")  # ? debug
        logger.debug(type(predicted_price))

        if actual_price is not None:
            accuracy = 1 - abs(predicted_price - Decimal(actual_price)) / Decimal(actual_price)
            logger.debug(f"accuracy: {accuracy}")  # ? debug
            user_scores.setdefault(user_id, []).append(
                (crypto, predicted_price, actual_price, accuracy, prediction_date)
            )


    user_avg_accuracy: dict[int, float] = {
        user_id: sum(acc[3] for acc in accs) / len(accs)
        for user_id, accs in user_scores.items()
    }

    return user_scores, user_avg_accuracy


async def format_leaderboard_table(
    leaderboard: List[Tuple[int, float]],
    user_scores: Dict[int, List[Tuple[str, float, float, float, datetime]]],
    interaction: discord.Interaction,
) -> str:
    leaderboard_message = "```\n"
    leaderboard_message += f"{'Rank':<5} {'User':<15} {'Crypto':<25} {'Accuracy':<20} {'Predicted':<20} {'Actual':<20} {'Date':<20}\n"
    leaderboard_message += "-" * 120 + "\n"

    rank = 1
    for user_id, _ in leaderboard:
        user: User = await interaction.client.fetch_user(user_id)
        username = user.name if user else f"User {user_id}"
        user_predictions = user_scores[user_id]
        user_score_message = format_user_scores(user_id, username, user_predictions)
        leaderboard_message += f"{rank:<5} {username:<15} {user_score_message}"

        rank += 1
        if rank > 25:
            break

    leaderboard_message += "```"
    return leaderboard_message


def format_predictions_table(
    predictions: List[Tuple[int, int, str, datetime, float]],
) -> str:
    table_message = "```\n"
    table_message += f"{'ID':<5} {'Crypto':<15} {'Date':<15} {'Predicted Price':<15}\n"
    table_message += "-" * 50 + "\n"
    for id, user_id, crypto, prediction_date, predicted_price in predictions:
        formatted_date = prediction_date.strftime("%d-%m-%Y")
        table_message += (
            f"{id:<5} {crypto:<15} {formatted_date:<15} ${predicted_price:<15.2f}\n"
        )
    table_message += "```"
    return table_message
