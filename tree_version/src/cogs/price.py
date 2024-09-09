import discord
import os
from discord.ext import commands
from discord import app_commands
import logging
import requests
from dotenv import load_dotenv

load_dotenv()
GUILD_ID = os.getenv('DISCORD_GUILD_ID')
BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
MY_GUILD = discord.Object(id=GUILD_ID)

logger = logging.getLogger(__name__)

class Price(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # @app_commands.command(name="price", description="Display the current price of one or multiple cyrptocurrencies")
    # @app_commands.describe()

    @app_commands.command(description="Display the current price of several cryptocurrencies at once.")
    @app_commands.rename(cryptos="crypto")
    @app_commands.describe(cryptos='Name of the crypto')
    async def price(self, interaction: discord.Interaction, cryptos: str):
        """
        !mult_price <crypto1> <crypto2> ...
        """
        
        logger.info(f'Sending mult prices {cryptos}') # ? debug
        
        crypto_list = ','.join(cryptos)
        logger.info(crypto_list)
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_list}&vs_currencies=usd"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            prices = {crypto: data.get(crypto, {}).get("usd", "N/A") for crypto in cryptos}
            response_message = "\n".join([f"The current price of {crypto} is ${prices[crypto]}" for crypto in cryptos])
            await interaction.response.send_message(response_message)
        else:
            await interaction.response.send_message("Error fetching the prices. Please try again.")

async def setup(bot):
    await bot.add_cog(Price(bot))
