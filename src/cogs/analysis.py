import discord
from discord import app_commands
from discord.ext import commands
import requests
import pandas as pd
import ta
from utils.list import get_crypto_autocomplete_choices
from utils.embeds import error_embed, success_embed
import logging

# Create a logger instance
logger = logging.getLogger(__name__)

class TechnicalAnalysis(commands.GroupCog, name="analyse"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="technical", description="Provide basic technical analysis.")
    @app_commands.rename(crypto="crypto")
    @app_commands.describe(crypto="Name or symbol of the cryptocurrency")
    @app_commands.autocomplete(crypto=get_crypto_autocomplete_choices)
    async def technical_analysis(self, interaction: discord.Interaction, crypto: str):
        """
        /technical_analysis <crypto>
        """
        # Ensure the crypto parameter is provided
        if not crypto:
            embed = error_embed("Missing Argument", "Please specify a cryptocurrency.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Fetch historical data from a public API
        url = f"https://api.coingecko.com/api/v3/coins/{crypto}/market_chart?vs_currency=usd&days=30"
        response = requests.get(url)
        data = response.json()

        if "prices" not in data:
            embed = error_embed("Error Fetching Data", "Error fetching data. Please try again.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Convert data to DataFrame
        df = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)

        # Calculate indicators
        df['rsi'] = ta.momentum.RSIIndicator(df['price']).rsi()
        df['macd'] = ta.trend.MACD(df['price']).macd()
        df['ema'] = ta.trend.EMAIndicator(df['price']).ema_indicator()

        # Create response message
        response_message = (
            # f"Technical Analysis for {crypto}\n"
            f"RSI (14): {df['rsi'].iloc[-1]:.2f}\n"
            f"MACD: {df['macd'].iloc[-1]:.2f}\n"
            f"EMA (14): {df['ema'].iloc[-1]:.2f}"
        )

        embed = success_embed(f"Technical Analysis for {crypto}", response_message)
        await interaction.response.send_message(embed=embed)
        # await interaction.response.send_message(response_message)
        logger.info(f"Performed technical analysis for {crypto}.")

    @app_commands.command(name="advanced", description="Provide advanced analysis.")
    @app_commands.rename(crypto="crypto")
    @app_commands.describe(crypto="Name or symbol of the cryptocurrency")
    @app_commands.autocomplete(crypto=get_crypto_autocomplete_choices)
    async def advanced_analysis(self, interaction: discord.Interaction, crypto: str):
        """
        /advanced_analysis <crypto>
        """
        # Ensure the crypto parameter is provided
        if not crypto:
            embed = error_embed("Missing Argument", "Please specify a cryptocurrency.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Fetch historical data from a public API
        url = f"https://api.coingecko.com/api/v3/coins/{crypto}/market_chart?vs_currency=usd&days=30"
        response = requests.get(url)
        data = response.json()

        if "prices" not in data:
            embed = error_embed("Error Fetching Data", "Error fetching data. Please try again.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Convert data to DataFrame
        df = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)

        # Calculate indicators
        df['rsi'] = ta.momentum.RSIIndicator(df['price']).rsi()
        df['macd'] = ta.trend.MACD(df['price']).macd()
        df['ema'] = ta.trend.EMAIndicator(df['price']).ema_indicator()
        df['volume'] = pd.Series(data['total_volumes'], index=df.index)  # Volume data
        
        # Dummy support/resistance and recommendations (implement as needed)
        support = df['price'].min()
        resistance = df['price'].max()
        recommendation = "Buy" if df['rsi'].iloc[-1] < 30 else "Sell" if df['rsi'].iloc[-1] > 70 else "Hold"

        # Create response message
        response_message = (
            # f"**Advanced Analysis for {crypto}**\n"
            f"RSI (14): {df['rsi'].iloc[-1]:.2f}\n"
            f"MACD: {df['macd'].iloc[-1]:.2f}\n"
            f"EMA (14): {df['ema'].iloc[-1]:.2f}\n"
            f"Support: ${support:.2f}\n"
            f"Resistance: ${resistance:.2f}\n"
            f"Recommendation: {recommendation}"
        )

        embed = success_embed(f"**Advanced Analysis for {crypto}**", response_message)
        await interaction.response.send_message(embed=embed)
        # await interaction.response.send_message(response_message)
        logger.info(f"Performed advanced analysis for {crypto}.")

async def setup(bot: commands.Bot):
    await bot.add_cog(TechnicalAnalysis(bot))
