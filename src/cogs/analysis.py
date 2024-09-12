# analysis.py

from typing import Literal
import discord
from discord import app_commands
from discord.ext import commands
import pandas as pd
import ta
import logging

from utils.autocomplete import crypto_autocomplete
from utils.embeds import error_embed, success_embed
from utils.crypto_data import fetch_crypto_data

logger = logging.getLogger(__name__)

class Analysis(commands.Cog, name="analyse"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    # Helper function to calculate indicators
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df['rsi'] = ta.momentum.RSIIndicator(df['price']).rsi()
        df['macd'] = ta.trend.MACD(df['price']).macd()
        df['ema'] = ta.trend.EMAIndicator(df['price']).ema_indicator()
        return df

    # Helper function to generate response message based on analysis type
    def generate_analysis_message(self, crypto: str, df: pd.DataFrame, analysis_type: str) -> str:
        message = ""

        # Basic analysis message
        if analysis_type == "technical":
            message += (
                f"RSI (14): {df['rsi'].iloc[-1]:.2f}\n"
                f"MACD: {df['macd'].iloc[-1]:.2f}\n"
                f"EMA (14): {df['ema'].iloc[-1]:.2f}"
            )

        # Advanced analysis message
        elif analysis_type == "advanced":
            support = df['price'].min()
            resistance = df['price'].max()
            recommendation = "Buy" if df['rsi'].iloc[-1] < 30 else "Sell" if df['rsi'].iloc[-1] > 70 else "Hold"
            message += (
                f"RSI (14): {df['rsi'].iloc[-1]:.2f}\n"
                f"MACD: {df['macd'].iloc[-1]:.2f}\n"
                f"EMA (14): {df['ema'].iloc[-1]:.2f}\n"
                f"Support: ${support:.2f}\n"
                f"Resistance: ${resistance:.2f}\n"
                f"Recommendation: {recommendation}"
            )

        # Full analysis message
        elif analysis_type == "full":
            ma50 = df['price'].rolling(window=50).mean().iloc[-1]
            ma200 = df['price'].rolling(window=200).mean().iloc[-1]
            current_price = df['price'].iloc[-1]

            bollinger = ta.volatility.BollingerBands(df['price'])
            upper_band = bollinger.bollinger_hband().iloc[-1]
            lower_band = bollinger.bollinger_lband().iloc[-1]
            price_band_position = (current_price - lower_band) / (upper_band - lower_band) * 100

            logger.info('here')
            message += (
                f"**Analyse Technique Complète pour {crypto.upper()} (Intervalle : 1D)**\n"
                f"- **RSI** : {df['rsi'].iloc[-1]:.2f} (Neutre)\n"
                f"- **MACD** : {df['macd'].iloc[-1]:.2f} (Haussière)\n"
                f"- **Bandes de Bollinger** : Le prix est à {price_band_position:.2f}% de la bande supérieure "
                f"(volatilité moyenne)\n"
                f"- **Volume** : {df['volume'].iloc[-1]:,.0f} BTC échangés dans les dernières 24h\n"
                f"- **MA 50** : ${ma50:.2f} | **MA 200** : ${ma200:.2f} "
                f"(Le prix actuel est au-dessus des moyennes mobiles, tendance haussière)"
            )

        return message

    # Main analysis handler
    async def perform_analysis(self, interaction: discord.Interaction, crypto: str, analysis_type: str) -> None:
        logger.info(f"Input crypto: {crypto}")

        # Resolve crypto ID
        crypto_id = self.bot.crypto_map.get(crypto.lower())
        logger.info(f"Resolved crypto: {crypto_id}")

        # Fetch crypto data
        df = fetch_crypto_data(crypto_id)
        if df is None:
            embed = error_embed("Error Fetching Data", "Error fetching data. Please try again.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Calculate indicators
        df = self.calculate_indicators(df)

        # Generate the appropriate analysis message
        response_message = self.generate_analysis_message(crypto, df, analysis_type)
        embed = success_embed(f"{analysis_type.capitalize()} Analysis for {crypto}", response_message)
        await interaction.response.send_message(embed=embed)
        logger.info(f"Performed {analysis_type} analysis for {crypto}.")

    @app_commands.command(name="analyse", description="Provide basic technical analysis.")
    @app_commands.rename(crypto="crypto")
    @app_commands.describe(type="The type of analysis to run", crypto="Name or symbol of the cryptocurrency")
    @app_commands.autocomplete(crypto=crypto_autocomplete)
    async def analyse(self, interaction: discord.Interaction, type: Literal['technical', 'advanced', 'full'], crypto: str) -> None:
        await self.perform_analysis(interaction, crypto, type)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Analysis(bot))
