# list_crypto.py

import discord
import os
from discord.ext import commands
from discord import app_commands
import logging
import requests
from dotenv import load_dotenv

from views.paginator import CryptoPaginator

load_dotenv()
GUILD_ID = os.getenv('DISCORD_GUILD_ID')
BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
MY_GUILD = discord.Object(id=GUILD_ID)

logger = logging.getLogger(__name__)

class ListCrypto(commands.Cog, name="listCrypto"):
    def __init__(self, bot) -> None:
        self.bot = bot

    @app_commands.command(name="list_crypto", description="Command to list available cryptocurrencies from the CoinGecko API.")
    async def list_crypto(self, interaction: discord.Interaction) -> None:
        """_summary_

        Args:
            interaction (discord.Interaction): _description_
        """
        logger.info(f"Listing available cryptos, author: {interaction.user.id}")
        
        url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250&page=1"
        response = requests.get(url)

        if response.status_code == 200:
            cryptos = response.json()
            # logger.info(cryptos) # ? debug

            if not cryptos:
                await interaction.response.send_message("No cryptocurrencies found.")
                return

            # Create an instance of the paginator with the list of cryptos
            view = CryptoPaginator(self.bot.crypto_list)
            # view = CryptoPaginator(cryptos)
            
            # Send the initial message with the first page of the cryptos and add the paginator buttons
            await interaction.response.send_message(embed=view.create_embed(), view=view)
        else:
            logger.error(f"Error fetching cryptocurrencies. Status code: {response.status_code}")
            await interaction.response.send_message("Error fetching the list of cryptocurrencies. Please try again later.")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ListCrypto(bot))
