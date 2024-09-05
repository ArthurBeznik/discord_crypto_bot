# market_data.py

from discord.ext import commands
import requests
from utils.errors import show_help

class MarketData(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Display the market capitalization of a cryptocurrency.")
    async def market_cap(self, ctx, crypto: str = None):
        """
        !market_cap <crypto>
        """
        if crypto is None:
            return await show_help(ctx)
    
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto}&vs_currencies=usd&include_market_cap=true"
        response = requests.get(url)
        data = response.json()

        if crypto in data:
            market_cap = data[crypto].get('usd_market_cap', 'N/A')
            await ctx.send(f"The market capitalization of {crypto} is ${market_cap}")
        else:
            await ctx.send(f"Error fetching market cap for {crypto}. Please check the cryptocurrency name.")

    @commands.command(description="Display the current trading volume of a cryptocurrency.")
    async def volume(self, ctx, crypto: str = None):
        """
        !volume <crypto>
        """
        if crypto is None:
            return await show_help(ctx)
    
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto}&vs_currencies=usd&include_24hr_vol=true"
        response = requests.get(url)
        data = response.json()

        if crypto in data:
            volume = data[crypto].get('usd_24h_vol', 'N/A')
            await ctx.send(f"The 24-hour trading volume of {crypto} is ${volume}")
        else:
            await ctx.send(f"Error fetching volume for {crypto}. Please check the cryptocurrency name.")

async def setup(bot):
    await bot.add_cog(MarketData(bot))
