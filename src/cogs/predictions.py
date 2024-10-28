# predictions.py

# TODO formatting of table?

from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Literal, Tuple
import discord
from discord.ext import commands
from discord import Embed, User, app_commands
import requests
from requests import Response

from bot import CryptoBot
from utils.autocomplete import crypto_autocomplete
from utils.logger import logging

logger = logging.getLogger(__name__)


class Prediction(commands.GroupCog, name="prediction"):
    def __init__(self, bot: CryptoBot) -> None:
        self.bot = bot

    @app_commands.command(
        name="create",
        description="Record a price prediction for a cryptocurrency at a future date.",
    )
    @app_commands.describe(crypto="Name or symbol of the cryptocurrency")
    @app_commands.describe(date="Date for the prediction in DD-MM-YYYY format")
    @app_commands.describe(prediction="Predicted price for the cryptocurrency")
    @app_commands.autocomplete(crypto=crypto_autocomplete)
    async def create_prediction(
        self,
        interaction: discord.Interaction,
        crypto: str,
        date: str,
        prediction: float,
    ) -> None:
        try:
            # Resolve the cryptocurrency
            crypto_id: str = self.bot.crypto_map.get(crypto.lower())

            # Validate the date format
            prediction_date: datetime = datetime.strptime(date, "%d-%m-%Y").date()

            # Record the prediction in the database
            self.db.add_prediction(
                interaction.user.id, crypto_id, prediction_date, prediction
            )

            # Send a confirmation message
            embed: Embed = discord.Embed(
                title="Prediction Recorded",
                description=f"Your prediction for **{crypto_id}** on **{date}** is **${prediction}**.",
                color=discord.Color.green(),
            )
            await interaction.response.send_message(embed=embed)

        except ValueError:
            await interaction.response.send_message(
                "Invalid date format. Please use DD-MM-YYYY.", ephemeral=True
            )
        except Exception as e:
            logger.error(f"Error in /prediction command: {e}")
            await interaction.response.send_message(
                "An error occurred while recording your prediction. Please try again later.",
                ephemeral=True,
            )

    async def fetch_actual_price(self, crypto: str, prediction_date: datetime) -> float:
        """
        Fetches the actual price for a given cryptocurrency on a given date from CoinGecko API.
        """
        try:
            logger.info(f"Fetching actual price for {crypto} at {prediction_date}")

            # Resolve the cryptocurrency
            crypto_id = self.bot.crypto_map.get(crypto.lower())

            formatted_date = prediction_date.strftime("%d-%m-%Y")

            url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}/history?date={formatted_date}"
            response: Response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                price = (
                    data.get("market_data", {})
                    .get("current_price", {})
                    .get("usd", None)
                )
                return price
            else:
                logger.error(
                    f"Failed to fetch actual price for {crypto} on {prediction_date}. Status code: {response.status_code}"
                )
                return None
        except Exception as e:
            logger.error(f"Error fetching price for {crypto} on {prediction_date}: {e}")
            return None

    @app_commands.command(
        name="leaderboard",
        description="Display a leaderboard of users ranked by their most accurate predictions.",
    )
    async def leaderboard(self, interaction: discord.Interaction) -> None:
        try:
            await interaction.response.defer(thinking=True)

            # Fetch all predictions from the database
            predictions: List[Tuple[int, int, str, datetime, float]] = (
                self.bot.db.get_predictions()
            )

            if not predictions:
                await interaction.followup.send("No predictions found.")
                return

            # Calculate accuracy for each user's predictions
            user_scores: Dict[
                int, List[Tuple[str, Decimal, float, float, datetime]]
            ] = {}
            current_date: datetime = datetime.now().date()

            for id, user_id, crypto, prediction_date, predicted_price in predictions:
                if prediction_date > current_date:
                    # Skip predictions where the date is in the future
                    continue

                # Fetch the actual price dynamically for the prediction date
                actual_price: float = await self.fetch_actual_price(
                    crypto, prediction_date
                )

                if actual_price is not None:
                    accuracy = (
                        1 - abs(float(predicted_price) - actual_price) / actual_price
                    )
                    if user_id not in user_scores:
                        user_scores[user_id] = []
                    user_scores[user_id].append(
                        (
                            crypto,
                            predicted_price,
                            actual_price,
                            accuracy,
                            prediction_date,
                        )
                    )

            logger.debug(f"user_scores: {user_scores}")

            # Average accuracy for each user
            user_avg_accuracy: Dict[int, float] = {
                user_id: sum(acc[3] for acc in accs) / len(accs)
                for user_id, accs in user_scores.items()
            }

            # logger.debug(f"user_avg_accuracy: {user_avg_accuracy}")

            # Sort users by their average accuracy
            leaderboard: List[Tuple[int, float]] = sorted(
                user_avg_accuracy.items(), key=lambda x: x[1], reverse=True
            )

            logger.debug(f"leaderboard: {leaderboard}")

            # Prepare the leaderboard message in plain text format
            leaderboard_message = "```\n"
            leaderboard_message += f"{'Rank':<5} {'User':<15} {'Crypto':<25} {'Accuracy':<20} {'Predicted':<20} {'Actual':<20} {'Date':<20}\n"
            leaderboard_message += "-" * 120 + "\n"

            rank = 1
            for user_id, _ in leaderboard:
                logger.debug(f"user_id: {user_id}")

                user: User = await interaction.client.fetch_user(user_id)

                logger.debug(f"user: {user}")

                username: str = user.name if user else f"User {user_id}"
                user_predictions: List[Tuple[str, Decimal, float, float, datetime]] = (
                    user_scores[user_id]
                )

                logger.debug(f"user_predictions: {user_predictions}")

                for (
                    crypto,
                    predicted_price,
                    actual_price,
                    accuracy,
                    prediction_date,
                ) in user_predictions:
                    formatted_date = prediction_date.strftime("%d-%m-%Y")
                    leaderboard_message += (
                        f"{rank:<5} {username:<15} {crypto:<25} "
                        f"{accuracy:<20.2%} ${predicted_price:<20.2f} "
                        f"${actual_price:<20.2f} {formatted_date:<20}\n"
                    )
                    rank += 1
                    if rank > 25:  # Limit to 25 entries
                        break

            leaderboard_message += "```"
            await interaction.followup.send(leaderboard_message)

        except Exception as e:
            logger.error(f"Error fetching leaderboard: {e}")
            await interaction.followup.send(f"Failed to display leaderboard: {e}")

    @app_commands.command(name="list", description="List all your predictions.")
    async def list_predictions(self, interaction: discord.Interaction) -> None:
        try:
            user_id: int = interaction.user.id

            predictions: List[Tuple[int, int, str, datetime, float]] = (
                self.db.get_predictions(user_id)
            )

            if not predictions:
                await interaction.response.send_message(
                    "You have no predictions recorded."
                )
                return

            # Prepare the predictions message
            predictions_message = "Your Predictions:\n"
            for id, user_id, crypto, prediction_date, predicted_price in predictions:
                formatted_date = prediction_date.strftime("%d-%m-%Y")
                predictions_message += f"[**{id}**] **{crypto}** on **{formatted_date}**: **${predicted_price}**\n"

            await interaction.response.send_message(predictions_message)

        except Exception as e:
            logger.error(f"Error listing predictions: {e}")
            await interaction.response.send_message(
                "An error occurred while fetching your predictions."
            )

    @app_commands.command(name="clear", description="Remove your predictions")
    @app_commands.describe(
        type="Removes all your predictions or a specific one",
        prediction_id="ID of the prediction to remove (optional)",
    )
    async def clear_predictions(
        self,
        interaction: discord.Interaction,
        type: Literal["all", "ID"],
        prediction_id: int = None,
    ) -> None:
        try:
            user_id: int = interaction.user.id

            if type == "all":
                self.db.clear_predictions(user_id)
                await interaction.response.send_message(
                    "All your predictions have been removed."
                )
                return

            elif type == "ID" and prediction_id:
                # Remove a specific prediction
                # result = self.bot.db.remove_prediction(user_id, prediction_id)
                result = self.db.remove_prediction(user_id, prediction_id)
                if result:
                    await interaction.response.send_message(
                        f"Prediction ID **{prediction_id}** has been removed."
                    )
                else:
                    await interaction.response.send_message(
                        f"No prediction found for ID **{prediction_id}**."
                    )
            else:
                await interaction.response.send_message(
                    "You need to specify a prediction ID to remove a specific prediction."
                )

        except Exception as e:
            logger.error(f"Error clearing predictions: {e}")
            await interaction.response.send_message(
                "An error occurred while clearing your predictions."
            )


async def setup(bot: CryptoBot) -> None:
    await bot.add_cog(Prediction(bot))
