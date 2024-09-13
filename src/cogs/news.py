# news.py

# TODO set return value

import discord
import requests
from typing import Literal
from discord import app_commands
from discord.ext import commands

from utils.autocomplete import crypto_autocomplete
from utils.config import (
    logging,
    NEWS_API_KEY,
    NEWS_API_URL,
)

logger = logging.getLogger(__name__)

class News(commands.Cog, name="news"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    # TODO set return value
    async def fetch_news(self, query: str):
        """
        Fetches cryptocurrency news from the NewsAPI.
        If a crypto symbol is provided, fetch news specific to that cryptocurrency.
        Otherwise, fetch global cryptocurrency news.

        Args:
            query (str): Search query for news (either a cryptocurrency name or 'cryptocurrency' for global news).

        Returns:
            list: A list of news articles, each containing 'title' and 'url'.
        """
        try:
            # Set up parameters for the API request
            params = {
                'q': query,
                'apiKey': NEWS_API_KEY,
                'language': 'en',
                'sortBy': 'publishedAt',  # Sort by latest news
                'pageSize': 5  # Limit to top 5 articles
            }

            # Make the API request to get the latest news
            url = NEWS_API_URL
            response = requests.get(url, params=params)

            # Check if the response is successful
            if response.status_code == 200:
                news_data = response.json()
                news_list = news_data.get('articles', [])
                return news_list
            else:
                logger.error(f"Error fetching news: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error while fetching news: {e}")
            return None
        
    @app_commands.command(name="news", description="Display the latest global or specific cryptocurrency news.")
    @app_commands.describe(type="Displays global news on cryptocurrency or for one specific crypto", crypto="Name or symbol of the cryptocurrency. Required if action is 'crypto'.")
    @app_commands.autocomplete(crypto=crypto_autocomplete)
    async def news(self, interaction: discord.Interaction, type: Literal['global', 'crypto'], crypto: str = None) -> None:
        """
        Fetch and display the latest cryptocurrency news.
        - If 'global' is selected, fetch global cryptocurrency news.
        - If 'crypto' is selected, fetch news specific to the provided cryptocurrency symbol.
        
        Args:
            interaction (discord.Interaction): The interaction object.
            action (Literal['global', 'crypto']): Action to fetch global or specific crypto news.
            crypto (str, optional): Cryptocurrency name or symbol. Required if action is 'crypto'.
        """
        if crypto is not None:
            # Resolve the cryptocurrency
            crypto = self.bot.crypto_map.get(crypto.lower())
            logger.info(f"Resolved crypto: {crypto}")

        if type == 'global':
            news_list = await self.fetch_news("cryptocurrency")
        elif type == 'crypto':
            if crypto:
                news_list = await self.fetch_news(crypto)
            else:
                await interaction.response.send_message("Please provide a cryptocurrency name or symbol for the 'crypto' action.", ephemeral=True)
                return

        if news_list:
            if type == 'crypto' and crypto:
                news_message = [f"**Latest news for {crypto.upper()}:**\n"]
            else:
                news_message = ["**Latest Global Cryptocurrency News:**\n"]

            for article in news_list:
                title = article['title']
                url = article['url']
                news_message.append(f"**{title}**\n{url}\n")

            await interaction.response.send_message('\n'.join(news_message))
        else:
            if type == 'crypto' and crypto:
                await interaction.response.send_message(f"No news found for {crypto.upper()}. Please try again with a different cryptocurrency.")
            else:
                await interaction.response.send_message("No global news found at the moment. Please try again later.")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(News(bot))
