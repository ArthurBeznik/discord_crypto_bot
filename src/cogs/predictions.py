# predictions.py

# TODO formatting of table?

from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Literal, Tuple
import discord
from discord.ext import commands
from discord import Embed, app_commands

from bot import CryptoBot
from utils.prediction_helpers import (
    calculate_user_scores,
    format_leaderboard_table,
    format_predictions_table,
)

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
            self.bot.db.predictions.add_prediction(
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

    @app_commands.command(
        name="leaderboard",
        description="Display a leaderboard of users ranked by their most accurate predictions.",
    )
    async def leaderboard(self, interaction: discord.Interaction) -> None:
        try:
            await interaction.response.defer(thinking=True)

            # Fetch all predictions from the database
            predictions: List[Tuple[int, int, str, datetime, float]] = (
                self.bot.db.predictions.get_predictions()
            )

            logger.debug(f"predictions: {predictions}")  # ? debug

            if not predictions:
                await interaction.followup.send("No predictions found.")
                return

            # Calculate accuracy for each user's predictions
            user_scores: Dict[int, List[Tuple[str, float, float, float, datetime]]] = {}
            current_date: datetime = datetime.now().date()

            user_scores, user_avg_accuracy = await calculate_user_scores(
                self.bot, predictions, current_date
            )

            logger.debug(f"user_scores: {user_scores}")
            logger.debug(f"user_avg_accuracy: {user_avg_accuracy}")

            # Sort users by their average accuracy
            leaderboard: List[Tuple[int, float]] = sorted(
                user_avg_accuracy.items(), key=lambda x: x[1], reverse=True
            )

            logger.debug(f"leaderboard: {leaderboard}")  # ? debug

            # Use the helper function to format the leaderboard as a table
            leaderboard_message = await format_leaderboard_table(
                leaderboard, user_scores, interaction
            )

            logger.debug(f"leaderboard_message: {leaderboard_message}")  # ? debug

            await interaction.followup.send(leaderboard_message)

        except Exception as e:
            logger.error(f"Error fetching leaderboard: {e}")
            await interaction.followup.send(f"Failed to display leaderboard: {e}")

    @app_commands.command(name="list", description="List all your predictions.")
    async def list_predictions(self, interaction: discord.Interaction) -> None:
        try:
            user_id: int = interaction.user.id

            predictions: List[Tuple[int, int, str, datetime, Decimal]] = (
                self.bot.db.predictions.get_predictions(user_id)
            )

            if not predictions:
                await interaction.response.send_message(
                    "You have no predictions recorded."
                )
                return

            # Use the helper function to format the predictions as a table
            predictions_message = format_predictions_table(predictions)

            embed: Embed = Embed(
                title="Your Predictions",
                description=predictions_message,
                color=discord.Color.green(),
            )
            await interaction.response.send_message(embed=embed)

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
                self.bot.db.predictions.clear_predictions(user_id)
                await interaction.response.send_message(
                    "All your predictions have been removed."
                )
                return

            elif type == "ID" and prediction_id:
                # Remove a specific prediction
                result = self.bot.db.predictions.remove_prediction(
                    user_id, prediction_id
                )
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
