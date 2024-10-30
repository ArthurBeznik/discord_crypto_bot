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
    """_summary_

    Args:
        bot (CryptoBot): _description_
        crypto (str): _description_
        prediction_date (datetime): _description_

    Returns:
        float: _description_
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


# TODO still in use?
# def format_user_scores(
#     user_id: int,
#     username: str,
#     user_predictions: List[Tuple[str, float, float, float, datetime]],
# ) -> str:
#     """_summary_

#     Args:
#         user_id (int): _description_
#         username (str): _description_
#         user_predictions (List[Tuple[str, float, float, float, datetime]]): _description_

#     Returns:
#         str: _description_
#     """
#     logger.info(f"Formatting user [{user_id}] scores")
#     logger.debug(f"user_predictions: {user_predictions}")  # ? debug

#     user_score_message = ""
#     for (
#         crypto,
#         predicted_price,
#         actual_price,
#         accuracy,
#         prediction_date,
#     ) in user_predictions:
#         formatted_date = prediction_date.strftime("%d-%m-%Y")
#         user_score_message += (
#             f"{crypto:<25} {accuracy:<20.2%} ${predicted_price:<20.2f} "
#             f"${actual_price:<20.2f} {formatted_date:<20}\n"
#         )
#     return user_score_message


# TODO still used?
# def calculate_average_accuracy(
#     users_scores: AllUsersScoresType,
# ) -> AllUsersAverageAccuracyType:
#     """_summary_

#     Args:
#         users_scores (AllUsersScoresType): _description_

#     Returns:
#         AllUsersAverageAccuracyType: _description_
#     """
#     logger.info("Calculating average accuracy")
#     logger.debug(f"users_scores: {users_scores}")  # ? debug

#     user_avg_accuracy: AllUsersAverageAccuracyType = {}

#     for user_id, accs in users_scores.items():
#         # Sum the accuracy values (acc[3] in each score tuple)
#         total_accuracy = sum(acc[3] for acc in accs)

#         # Calculate the average accuracy
#         avg_accuracy = total_accuracy / len(accs)

#         # Store the result in the dictionary
#         user_avg_accuracy[user_id] = avg_accuracy

#     return user_avg_accuracy


# TODO still used?
# async def calculate_users_scores(
#     bot: CryptoBot,
#     predictions: List[PredictionType],
#     current_date: datetime,
# ) -> AllUsersScoresType:
#     """_summary_

#     Args:
#         bot (CryptoBot): _description_
#         predictions (List[PredictionType]): _description_
#         current_date (datetime): _description_

#     Returns:
#         AllUsersScoresType: _description_
#     """
#     logger.info("Calculating user scores")

#     users_scores = {}
#     for (
#         id,
#         user_id,
#         crypto,
#         prediction_date,
#         predicted_price,
#         actual_price,
#     ) in predictions:
#         if prediction_date > current_date:
#             continue

#         if actual_price is None:
#             actual_price: float = await fetch_actual_price(bot, crypto, prediction_date)
#             bot.db.predictions.update_actual_price(id, actual_price)

#         logger.debug(f"actual_price: {actual_price}")  # ? debug

#         if actual_price is not None:
#             accuracy: Decimal = 1 - abs(
#                 predicted_price - Decimal(actual_price)
#             ) / Decimal(actual_price)
#             logger.debug(f"accuracy: {accuracy}")  # ? debug

#             users_scores.setdefault(user_id, []).append(
#                 (crypto, predicted_price, actual_price, accuracy, prediction_date)
#             )

#     logger.debug(f"Final user_scores: {users_scores}")  # ? debug

#     return users_scores


async def format_leaderboard_table(
    leaderboard_data: List[Tuple[int, str, datetime, Decimal, Decimal, Decimal]],
    interaction: discord.Interaction,
) -> str:
    """_summary_

    Args:
        leaderboard_data (List[Tuple[int, str, datetime, Decimal, Decimal, Decimal]]): _description_
        interaction (discord.Interaction): _description_

    Returns:
        str: _description_
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


def format_predictions_table(
    predictions: List[Tuple[int, int, str, datetime, Decimal, Decimal, Decimal]],
) -> str:
    """_summary_

    Args:
        predictions (List[Tuple[int, int, str, datetime, Decimal, Decimal, Decimal]]): _description_

    Returns:
        str: _description_
    """
    logger.info("Formatting predictions table")

    table_message = "```\n"
    table_message += f"{'ID':<5} {'Crypto':<15} {'Date':<15} {'Predicted Price':<15} {'Actual Price':<15} {'Accuracy':<10}\n"
    table_message += "-" * 80 + "\n"

    for (
        id,
        _,
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
    """Calculates the accuracy of a prediction.

    Args:
        predicted_price (Decimal): _description_
        actual_price (Decimal): _description_

    Raises:
        ValueError: _description_

    Returns:
        Decimal: _description_
    """
    logger.info(
        f"Calculating prediction accuracy: predicted price [{predicted_price}] | actual price [{actual_price}]"
    )

    if predicted_price is None or actual_price is None:
        raise ValueError("Both predicted_price and actual_price must be provided.")

    # Calculate the accuracy as a decimal value
    accuracy = Decimal(1) - abs(
        Decimal(predicted_price) - Decimal(actual_price)
    ) / Decimal(actual_price)

    # Clamp the accuracy to a range of [0, 1] to handle any edge cases
    return max(Decimal(0), min(accuracy, Decimal(1)))
