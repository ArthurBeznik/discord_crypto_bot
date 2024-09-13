# trend.py

import discord
from typing import Literal
from discord import app_commands
from discord.ext import commands
import pandas as pd
import ta

from utils.autocomplete import crypto_autocomplete
from utils.crypto_data import fetch_crypto_data
from utils.embeds import error_embed, success_embed
from utils.config import (
    logging,
)

logger = logging.getLogger(__name__)

class TrendDetection(commands.Cog, name="trend"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    def detect_trend(self, df: pd.DataFrame)-> Literal['Bullish 🟢', 'Bearish 🔴', 'Neutral ⚪']:
        """
        Detects the market trend based on RSI and Moving Averages.

        Args:
            df (pd.DataFrame): DataFrame containing the price data with columns ['price'].

        Returns:
            str: A message indicating the current trend (Bullish, Bearish, or Neutral).
        """
        # Calculate RSI, EMA50, and EMA200
        df['rsi'] = ta.momentum.RSIIndicator(df['price']).rsi()
        df['ema50'] = ta.trend.EMAIndicator(df['price'], window=50).ema_indicator()
        df['ema200'] = ta.trend.EMAIndicator(df['price'], window=200).ema_indicator()

        current_price = df['price'].iloc[-1]
        rsi = df['rsi'].iloc[-1]
        ema50 = df['ema50'].iloc[-1]
        ema200 = df['ema200'].iloc[-1]

        # Determine the trend
        if current_price > ema50 > ema200 and rsi > 50:
            return "Bullish 🟢"
        elif current_price < ema50 < ema200 and rsi < 50:
            return "Bearish 🔴"
        else:
            return "Neutral ⚪"

    async def perform_trend_detection(self, interaction: discord.Interaction, crypto: str) -> None:
        """
        Main function to fetch the data, analyze the trend, and respond to the user.

        Args:
            interaction (discord.Interaction): The interaction object for the command.
            crypto (str): The cryptocurrency symbol.
        """
        logger.info(f"Input crypto: {crypto}")

        # Resolve crypto ID
        crypto_id = self.bot.crypto_map.get(crypto.lower())
        logger.info(f"Resolved crypto: {crypto_id}")

        # Fetch crypto data
        df = fetch_crypto_data(crypto_id)
        if df is None:
            embed = error_embed("Error Fetching Data", "Unable to fetch data for the specified symbol. Please try again.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Detect trend
        trend = self.detect_trend(df)
        # logger.info(f"Detected trend for {crypto}: {trend}")

        # Send trend result
        message = f"The current trend for {crypto.upper()} is: **{trend}**"
        embed = success_embed(f"Trend Detection for {crypto.upper()}", message)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="trend", description="Detect the current trend (bullish, bearish, or neutral) for a cryptocurrency.")
    @app_commands.rename(crypto="symbol")
    @app_commands.describe(crypto="The symbol of the cryptocurrency (e.g., BTC, ETH).")
    @app_commands.autocomplete(crypto=crypto_autocomplete)
    async def trend(self, interaction: discord.Interaction, crypto: str) -> None:
        """
        Command to detect the trend for the specified cryptocurrency.

        Args:
            interaction (discord.Interaction): The interaction object.
            crypto (str): The symbol of the cryptocurrency (e.g., BTC).
        """
        await self.perform_trend_detection(interaction, crypto)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(TrendDetection(bot))
