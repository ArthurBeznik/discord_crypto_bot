# graphs.py

# TODO rename this file and commands?

import discord
from discord import app_commands
from discord.ext import commands
import matplotlib.pyplot as plt
from io import BytesIO

from utils.crypto_data import fetch_crypto_data
from utils.autocomplete import crypto_autocomplete
from utils.embeds import error_embed, success_embed
from utils.config import (
    logging,
    PERIOD_MAP,
    TIME_PERIOD,
)

logger = logging.getLogger(__name__)

class Graphs(commands.GroupCog, name="graph"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="graphic", description="Generate a graph with historical data for a cryptocurrency.")
    @app_commands.rename(crypto="crypto", period="period")
    @app_commands.describe(crypto="Name or symbol of the cryptocurrency", period=TIME_PERIOD)
    @app_commands.autocomplete(crypto=crypto_autocomplete)
    async def graphic(self, interaction: discord.Interaction, crypto: str, period: str) -> None:
        """_summary_

        Args:
            interaction (discord.Interaction): _description_
            crypto (str): _description_
            period (str): _description_
        """
        # Resolve the cryptocurrency input
        crypto_id = self.bot.crypto_map.get(crypto.lower())
        logger.info(f"Resolved crypto: {crypto_id}")

        days = PERIOD_MAP.get(period, 30)

        # Fetch historical data
        df = fetch_crypto_data(crypto_id, days)

        if df is None:
            embed = error_embed("Error Fetching Data", f"Could not fetch data for {crypto}. Please try again.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            logger.error(f"Failed to fetch data for {crypto}")
            return

        # Plot the graph
        plt.figure(figsize=(10, 6))
        plt.plot(df.index, df['price'], label=f"{crypto.upper()} Price (USD)")
        plt.title(f"{crypto.upper()} Price Over Last {period}")
        plt.xlabel("Date")
        plt.ylabel("Price (USD)")
        plt.legend()
        plt.grid()

        # Save the plot to a buffer and send it as an image
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()

        file = discord.File(buf, filename=f"{crypto}_price_graph.png")
        embed = success_embed(f"{crypto.upper()} Price Graph", f"Here's the price graph for {crypto.upper()} over the last {period}.")
        embed.set_image(url=f"attachment://{crypto}_price_graph.png")

        await interaction.response.send_message(embed=embed, file=file)
        logger.info(f"Generated price graph for {crypto} over the last {period}.")

    @app_commands.command(name="history", description="Provide detailed historical data in tabular form.")
    @app_commands.rename(crypto="crypto", period="period")
    @app_commands.describe(crypto="Name or symbol of the cryptocurrency", period=TIME_PERIOD)
    @app_commands.autocomplete(crypto=crypto_autocomplete)
    async def history(self, interaction: discord.Interaction, crypto: str, period: str) -> None:
        """_summary_

        Args:
            interaction (discord.Interaction): _description_
            crypto (str): _description_
            period (str): _description_
        """
        # Resolve the cryptocurrency input
        crypto_id = self.bot.crypto_map.get(crypto.lower())
        logger.info(f"Resolved crypto: {crypto_id}")

        days = PERIOD_MAP.get(period, 30)
        # logger.info(days) # ? debug

        # Fetch historical data
        df = fetch_crypto_data(crypto_id, days)

        if df is None:
            embed = error_embed("Error Fetching Data", f"Could not fetch data for {crypto}. Please try again.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            logger.error(f"Failed to fetch data for {crypto}")
            return

        # If the period is 1 year, resample the data to one data point per month
        if period == "1y":
            df = df.resample('ME').last() # Use the last available price for each month

        # Format the data as a table
        df['price'] = df['price'].apply(lambda x: f"${x:.2f}")
        df.index = df.index.strftime("%Y-%m-%d") # Show the month in YYYY-MM-DD format
        table = df.tail(12 if period == "1y" else 10).to_string() # Show 12 months if 1y, else 10 latest entries

        # Send the data as an embed
        embed = success_embed(f"Historical Data for {crypto.upper()}", f"Here is the historical data for {crypto.upper()} over the last {period}.\n\n```{table}```")
        await interaction.response.send_message(embed=embed)
        logger.info(f"Provided historical data for {crypto} over the last {period}.")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Graphs(bot))
