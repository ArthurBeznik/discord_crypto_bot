# price.py

import discord
from discord import app_commands
from discord.ext import commands
from utils.errors import show_help
import requests

# Real-time price commands
# ==============================================
class Price(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(description="Display the current price of any cryptocurrency")
    async def price(self, ctx, crypto: str = None):
        """
        !price <crypto>
        """
        if crypto is None:
            return await show_help(ctx)
        
        print(f'Sending price for {crypto}') # ? debug
        
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto}&vs_currencies=usd"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            price = data.get(crypto, {}).get("usd", "N/A")
            await ctx.send(f"The current price of {crypto} is ${price}")
        else:
            await ctx.send("Error fetching the price. Please try again.")

    @commands.command(description="Display the current price of several cryptocurrencies at once.")
    async def mult_price(self, ctx, *cryptos: str):
        """
        !mult_price <crypto1> <crypto2> ...
        """
        if not cryptos:
            return await show_help(ctx)
        
        print(f'Sending mult prices {cryptos}') # ? debug
        
        crypto_list = ','.join(cryptos)
        # print(crypto_list) # ? debug
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_list}&vs_currencies=usd"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            prices = {crypto: data.get(crypto, {}).get("usd", "N/A") for crypto in cryptos}
            response_message = "\n".join([f"The current price of {crypto} is ${prices[crypto]}" for crypto in cryptos])
            await ctx.send(response_message)
        else:
            await ctx.send("Error fetching the prices. Please try again.")

async def setup(bot):
    await bot.add_cog(Price(bot))