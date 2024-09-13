# list_crypto.py

import discord
from discord.ext import commands
from discord import app_commands
import requests

from views.paginator import CryptoPaginator
from utils.config import (
    logging,
    CG_API_URL,
)

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
        logger.info(f"Listing available cryptos, user: {interaction.user} (ID: {interaction.user.id})")
        
        url = CG_API_URL
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
