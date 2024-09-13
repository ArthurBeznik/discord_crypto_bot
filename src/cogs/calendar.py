# calendar.py

# TODO set return value
# TODO find an API

import discord
from discord.ext import commands
from discord import app_commands
import requests

from utils.config import (
    logging,
    CALENDAR_API_KEY,
)

logger = logging.getLogger(__name__)

# logger.info(f"CALENDAR_API_KEY: {CALENDAR_API_KEY}") # ? debug

class CryptoCalendar(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    # TODO set return value
    def fetch_crypto_news(self):
        """
        Fetches the latest cryptocurrency news from CoinMarketCap API.
        """
        url = ""
        headers = {
            'Accepts': 'application/json',
            'API_KEY': CALENDAR_API_KEY
        }
        params = {
            'limit': '5', # Limit number of news articles
        }
        # logger.info(f"headers: {headers}") # ? debug

        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            news = response.json()
            return news
        else:
            logger.error(f"Error fetching news: {response.status_code}")
            return None

    # TODO find an API
    @app_commands.command(name="calendar", description="Displays major economic events that could affect the crypto market.")
    async def calendar(self, interaction: discord.Interaction) -> None:
        """"""
        await interaction.response.send_message("Feed me an API!")
    
        crypto_news = self.fetch_crypto_news()
        
        if crypto_news:
            embed = discord.Embed(title="Crypto Market News", color=discord.Color.blue())
            for article in crypto_news.get('data', []):
                title = article.get('title')
                url = article.get('url')
                if title and url:
                    embed.add_field(name=title, value=f"[Read more]({url})", inline=False)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("Could not fetch crypto news at this time.")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(CryptoCalendar(bot))
