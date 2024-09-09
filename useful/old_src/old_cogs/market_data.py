# market_data.py

from discord.ext import commands
import requests
from utils.errors import show_help
import logging

logger = logging.getLogger(__name__)

class MarketData(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Display the market capitalization of a cryptocurrency.")
    async def market_cap(self, ctx, crypto: str = None):
        """
        !market_cap <crypto>
        """
        logger.debug(f"Called market_cap, crypto: {crypto} | author: {ctx.author.id}")

        if crypto is None:
            return await show_help(ctx)
        
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto}&vs_currencies=usd&include_market_cap=true"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching market cap for {crypto}: {e}")
            return await ctx.send(f"Error fetching market cap for {crypto}. Please try again later.")

        if crypto in data:
            market_cap = data[crypto].get('usd_market_cap', 'N/A')
            message = f"The market capitalization of {crypto} is ${market_cap}"
            logger.info(f"Sending market cap message to {ctx.author}: {message}")
            return await ctx.send(message)
        else:
            message = f"Error fetching market cap for {crypto}. Please check the cryptocurrency name."
            logger.info(f"Sending error message to {ctx.author}: {message}")
            return await ctx.send(message)

    @commands.command(description="Display the current trading volume of a cryptocurrency.")
    async def volume(self, ctx, crypto: str = None):
        """
        !volume <crypto>
        """
        logger.debug(f"Called volume, crypto: {crypto} | author: {ctx.author.id}")

        if crypto is None:
            return await show_help(ctx)
        
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto}&vs_currencies=usd&include_24hr_vol=true"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching volume for {crypto}: {e}")
            return await ctx.send(f"Error fetching volume for {crypto}. Please try again later.")

        if crypto in data:
            volume = data[crypto].get('usd_24h_vol', 'N/A')
            message = f"The 24-hour trading volume of {crypto} is ${volume}"
            logger.info(f"Sending volume message to {ctx.author}: {message}")
            return await ctx.send(message)
        else:
            message = f"Error fetching volume for {crypto}. Please check the cryptocurrency name."
            logger.info(f"Sending error message to {ctx.author}: {message}")
            return await ctx.send(message)

async def setup(bot):
    await bot.add_cog(MarketData(bot))
