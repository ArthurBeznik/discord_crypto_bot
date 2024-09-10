import discord
from discord import app_commands
from discord.ext import commands
import requests
from utils.list import get_crypto_autocomplete_choices, load_crypto_list
from utils.embeds import error_embed, success_embed
import logging

# Create a logger instance
logger = logging.getLogger(__name__)

class Info(commands.GroupCog, name="info"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # self.crypto_map = load_crypto_list()  # Load the crypto map using the utility function

    def fetch_crypto_info(self, crypto_id: str):
        """
        Fetches market data for a cryptocurrency from CoinGecko API.
        :param crypto: Name or symbol of the cryptocurrency
        :return: Dictionary with market data
        """
        url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}"
        # url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_id}&vs_currencies=usd"
        response = requests.get(url)
        
        if response.status_code != 200:
            return None
        
        data = response.json()
        return data

    @app_commands.command(name="market_cap", description="Display the market capitalization of a cryptocurrency.")
    @app_commands.rename(crypto="crypto")
    @app_commands.describe(crypto="Name or symbol of the cryptocurrency")
    @app_commands.autocomplete(crypto=get_crypto_autocomplete_choices)
    async def market_cap(self, interaction: discord.Interaction, crypto: str):
        """
        /market_cap <crypto>: Display the market capitalization of a cryptocurrency.
        """
        crypto_id = self.bot.crypto_map.get(crypto.lower())

        # Fetch cryptocurrency data
        data = self.fetch_crypto_info(crypto_id)

        if data is None:
            embed = error_embed("Error Fetching Data", f"Could not fetch data for {crypto}. Please try again.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Extract market cap information
        market_cap = data.get('market_data', {}).get('market_cap', {}).get('usd', 'N/A')

        if market_cap == 'N/A':
            embed = error_embed("Market Cap Data Unavailable", f"Could not fetch market cap data for {crypto}.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Create an embed to display the market cap
        embed = success_embed(
            f"Market Capitalization for {crypto.upper()}",
            f"The current market capitalization of {crypto.upper()} is **${market_cap:,.2f}** USD."
        )

        await interaction.response.send_message(embed=embed)
        logger.info(f"Displayed market cap for {crypto}.")

    @app_commands.command(name="volume", description="Display the current trading volume of a cryptocurrency.")
    @app_commands.rename(crypto="crypto")
    @app_commands.describe(crypto="Name or symbol of the cryptocurrency")
    @app_commands.autocomplete(crypto=get_crypto_autocomplete_choices)
    async def volume(self, interaction: discord.Interaction, crypto: str):
        """
        /volume <crypto>: Display the current trading volume of a cryptocurrency.
        """
        crypto_id = self.bot.crypto_map.get(crypto.lower())

        # Fetch cryptocurrency data
        data = self.fetch_crypto_info(crypto_id)

        if data is None:
            embed = error_embed("Error Fetching Data", f"Could not fetch data for {crypto}. Please try again.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Extract trading volume information
        volume = data.get('market_data', {}).get('total_volume', {}).get('usd', 'N/A')

        if volume == 'N/A':
            embed = error_embed("Volume Data Unavailable", f"Could not fetch volume data for {crypto}.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Create an embed to display the trading volume
        embed = success_embed(
            f"Trading Volume for {crypto.upper()}",
            f"The current trading volume of {crypto.upper()} is **${volume:,.2f}** USD."
        )

        await interaction.response.send_message(embed=embed)
        logger.info(f"Displayed trading volume for {crypto}.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Info(bot))
