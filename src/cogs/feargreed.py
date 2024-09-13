# feargreed.py

# TODO set return value

import discord
from discord import app_commands
from discord.ext import commands
import requests

from utils.config import (
    logging,
    ALT_API_URL
)

logger = logging.getLogger(__name__)

class FearGreed(commands.Cog, name="feargreed"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def fetch_fear_greed_index(self):
        """
        Fetches the current Fear and Greed Index from an external API.
        
        Returns:
            dict: A dictionary containing the index value, classification, and other relevant data.
        """
        try:
            url = ALT_API_URL
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if data and data.get('data'):
                    return data['data'][0] # Get the most recent index data
            else:
                logger.error(f"Error fetching Fear and Greed Index: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error while fetching Fear and Greed Index: {e}")
            return None

    @app_commands.command(name="feargreed", description="Display the current Fear and Greed Index for the market.")
    async def feargreed(self, interaction: discord.Interaction) -> None:
        """
        Command to display the current Fear and Greed Index for the market.

        Args:
            interaction (discord.Interaction): The interaction object for the command.
        """
        logger.info("Fetching Fear and Greed Index")
        fear_greed_data = await self.fetch_fear_greed_index()

        if fear_greed_data:
            index_value = fear_greed_data['value']
            classification = fear_greed_data['value_classification']
            timestamp = fear_greed_data['timestamp']
            message = (
                f"**Fear and Greed Index**\n"
                f"**Current Value**: {index_value} ({classification})\n"
                f"*Updated on*: <t:{timestamp}:R>"
            )

            embed = discord.Embed(
                title="📈 Fear and Greed Index",
                description=message,
                color=discord.Color.green() if int(index_value) > 50 else discord.Color.red()
            )

            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(
                title="Error",
                description="Unable to fetch the Fear and Greed Index. Please try again later.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(FearGreed(bot))
