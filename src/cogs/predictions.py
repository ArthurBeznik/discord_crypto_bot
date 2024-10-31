# predictions.py

from datetime import datetime
from typing import Literal
import discord
from discord.ext import commands, tasks
from discord import Embed, app_commands

from bot import CryptoBot
from utils.predictions_helpers import (
    calculate_prediction_accuracy,
    fetch_actual_price,
    format_leaderboard_table,
    format_predictions_table,
)
from utils.autocomplete import crypto_autocomplete
from utils.logger import logging

logger = logging.getLogger(__name__)


class Prediction(commands.GroupCog, name="prediction"):
    def __init__(self, bot: CryptoBot) -> None:
        self.bot = bot
        self.check_pending_predictions.start()  # Start the task to fetch prices for future predictions

    @tasks.loop(hours=24)
    async def check_pending_predictions(self):
        """
        This background task runs every 24 hours to check for predictions with future dates
        and updates the actual prices and accuracy once those dates pass.
        """
        logger.info("Checking for pending predictions")

        try:
            # Get all predictions that need an actual price and have a past date
            pending_predictions = self.bot.db.predictions.get_pending_predictions(
                datetime.now().date()
            )
            logger.debug(f"pending_predictions: {pending_predictions}")  # ? debug

            for prediction in pending_predictions:
                (
                    prediction_id,
                    crypto_id,
                    prediction_date,
                    predicted_price,
                    actual_price,
                ) = prediction

                try:
                    actual_price = await fetch_actual_price(
                        self.bot, crypto_id, prediction_date
                    )
                    logger.debug(f"actual_price: {actual_price}")  # ? debug

                    # Update the actual price in the database if fetched successfully
                    if actual_price is not None:
                        accuracy = calculate_prediction_accuracy(
                            predicted_price, actual_price
                        )
                        logger.debug(f"accuracy: {accuracy}")  # ? debug

                        updated = self.bot.db.predictions.update_pending_prediction(
                            prediction_id, actual_price, accuracy
                        )
                        if updated:
                            logger.info(
                                f"Updated prediction [{prediction_id}] with actual price [${actual_price}] and accuracy [{accuracy:.2f}%]"
                            )
                        else:
                            logger.warning(
                                f"Prediction [{prediction_id}] already updated or does not exist"
                            )

                except Exception as e:
                    logger.error(
                        f"Error processing prediction [{prediction_id}] for [{crypto_id}]: {e}"
                    )

        except Exception as e:
            logger.error(f"Error in scheduled check_pending_predictions task: {e}")

    @check_pending_predictions.before_loop
    async def before_check_pending_predictions(self):
        await (
            self.bot.wait_until_ready()
        )  # Ensures the bot is ready before starting the loop

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
        """
        Records a new cryptocurrency price prediction made by the user for a specified future date.

        Args:
            interaction (discord.Interaction): The interaction that triggered this command.
            crypto (str): The cryptocurrency symbol for which the prediction is made.
            date (str): Date for the prediction in DD-MM-YYYY format.
            prediction (float): Predicted price of the cryptocurrency.

        Returns:
            None
        """
        logger.info(
            f"Creating prediction for user [{interaction.user.id}] for [{crypto}] on [{date}], predicted price: [{prediction}]"
        )

        try:
            # Resolve the cryptocurrency
            crypto_id: str = self.bot.crypto_map.get(crypto.lower())

            # Validate the date format
            prediction_date: datetime = datetime.strptime(date, "%d-%m-%Y").date()

            # If the date is today or earlier, fetch the actual price immediately
            actual_price = None
            accuracy = None
            if prediction_date <= datetime.now().date():
                actual_price = await fetch_actual_price(
                    self.bot, crypto, prediction_date
                )
                accuracy = calculate_prediction_accuracy(prediction, actual_price)

            # Record the prediction in the database with the actual price if available
            self.bot.db.predictions.create_prediction(
                interaction.user.id,
                crypto_id,
                prediction_date,
                prediction,
                actual_price,
                accuracy,
            )

            # Send a confirmation message
            embed: Embed = discord.Embed(
                title="Prediction Recorded",
                description=f"Your prediction for **{crypto_id}** on **{date}** is **${prediction}**.",
                color=discord.Color.green(),
            )
            await interaction.response.send_message(embed=embed)
            logger.info(
                f"Successfully created and displayed prediction to user [{interaction.user.id}]"
            )

        except ValueError as e:
            await interaction.response.send_message(
                f"An error occured: {e}", ephemeral=True
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
        """
        Displays a leaderboard showing users ranked by prediction accuracy.

        Args:
            interaction (discord.Interaction): The interaction that triggered this command.

        Returns:
            None
        """
        logger.info(f"Displaying leaderboard for user [{interaction.user.id}]")

        try:
            await interaction.response.defer(thinking=True)

            # Fetch all completed predictions from the database
            predictions = self.bot.db.predictions.get_completed_predictions()
            logger.debug(f"predictions: {predictions}")  # ? debug

            if not predictions:
                await interaction.followup.send("No predictions found")
                return

            # Sort the predictions by most accurate
            sorted_predictions = sorted(predictions, key=lambda x: x[5], reverse=True)
            logger.debug(f"Sorted predictions: {sorted_predictions}")  # ? debug

            # Format the leaderboard message
            leaderboard_message = await format_leaderboard_table(
                sorted_predictions, interaction
            )
            logger.debug(f"leaderboard_message: {leaderboard_message}")  # ? debug

            await interaction.followup.send(leaderboard_message)
            logger.info(
                f"Successfully displayed leaderboard to user [{interaction.user.id}]"
            )

        except Exception as e:
            logger.error(f"Error fetching leaderboard: {e}")
            await interaction.followup.send(f"Failed to display leaderboard: {e}")

    @app_commands.command(name="list", description="List all your predictions.")
    async def list_predictions(self, interaction: discord.Interaction) -> None:
        """
        Lists all predictions made by the user.

        Args:
            interaction (discord.Interaction): The interaction that triggered this command.

        Returns:
            None
        """
        logger.info(f"Listing predictions of user [{interaction.user.id}]")

        try:
            user_id: int = interaction.user.id

            predictions = self.bot.db.predictions.get_predictions(user_id)
            logger.debug(f"predictions: {predictions}")  # ? debug

            if not predictions:
                await interaction.response.send_message(
                    "You have no predictions recorded"
                )
                return

            # Use the helper function to format the predictions as a table
            predictions_message = format_predictions_table(predictions)
            logger.debug(f"predictions_message: {predictions_message}")  # ? debug

            await interaction.response.send_message(predictions_message)
            logger.info(f"Successfully listed predictions of user [{user_id}]")

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
        type: Literal["all", "Prediction ID"],
        prediction_id: int = None,
    ) -> None:
        """
        Clears one or all predictions made by the user based on the provided type.

        Args:
            interaction (discord.Interaction): The interaction that triggered this command.
            type (Literal["all", "Prediction ID"]): Indicates whether to delete all predictions or a specific one.
            prediction_id (int, optional): The ID of the specific prediction to delete.

        Returns:
            None
        """
        try:
            user_id: int = interaction.user.id

            if type == "all":
                logger.info(f"Clearing all predictions of user [{user_id}]")

                self.bot.db.predictions.clear_predictions(user_id)
                await interaction.response.send_message(
                    "All your predictions have been removed successfully"
                )
                return

            elif type == "Prediction ID" and prediction_id:
                logger.info(
                    f"Clearing prediction [{prediction_id}] of user [{user_id}]"
                )

                # Remove a specific prediction
                result = self.bot.db.predictions.remove_prediction(
                    user_id, prediction_id
                )
                if result:
                    await interaction.response.send_message(
                        f"Prediction ID **{prediction_id}** has been removed"
                    )
                else:
                    await interaction.response.send_message(
                        f"No prediction found for ID **{prediction_id}**"
                    )
            else:
                await interaction.response.send_message(
                    "You need to specify a prediction ID to remove a specific prediction"
                )

        except Exception as e:
            logger.error(f"Error clearing predictions: {e}")
            await interaction.response.send_message(
                "An error occurred while clearing your predictions"
            )


async def setup(bot: CryptoBot) -> None:
    await bot.add_cog(Prediction(bot))
