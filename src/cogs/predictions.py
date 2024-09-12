import discord
from discord.ext import commands
from discord import app_commands
import logging
from datetime import datetime

from utils.autocomplete import crypto_autocomplete

logger = logging.getLogger(__name__)

class Prediction(commands.Cog, name="prediction"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="prediction", description="Record a price prediction for a cryptocurrency at a future date.")
    @app_commands.describe(crypto="Name or symbol of the cryptocurrency")
    @app_commands.describe(date="Date for the prediction in YYYY-MM-DD format")
    @app_commands.describe(prediction="Predicted price for the cryptocurrency")
    @app_commands.autocomplete(crypto=crypto_autocomplete)
    async def prediction(self, interaction: discord.Interaction, crypto: str, date: str, prediction: float) -> None:
        """
        Command to record a cryptocurrency price prediction for a future date.

        Args:
            interaction (discord.Interaction): The interaction object for the command.
            symbol (str): The cryptocurrency symbol.
            date (str): The future date for the prediction.
            prediction (float): The predicted price.
        """
        try:
            # Resolve the cryptocurrency
            crypto_id = self.bot.crypto_map.get(crypto.lower())
            # logger.info(f"Resolved crypto: {crypto_id}") # ? debug

            # Validate the date format
            prediction_date = datetime.strptime(date, '%Y-%m-%d').date()

            # Record the prediction in the database
            self.bot.db.add_prediction(interaction.user.id, crypto_id.upper(), prediction_date, prediction)

            # Send a confirmation message
            embed = discord.Embed(
                title="Prediction Recorded",
                description=f"Your prediction for **{crypto_id.upper()}** on **{date}** is **${prediction}**.",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed)

        except ValueError:
            await interaction.response.send_message(
                "Invalid date format. Please use YYYY-MM-DD.",
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Error in /prediction command: {e}")
            await interaction.response.send_message(
                "An error occurred while recording your prediction. Please try again later.",
                ephemeral=True
            )

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Prediction(bot))
