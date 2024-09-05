# portfolio.py

# TODO to store everything we need a DB or json

from discord import app_commands
from discord.ext import commands
import requests

class Portfolio(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.portfolios = {}  # A dictionary to store user portfolios

    @commands.command(description="Add cryptocurrency to your virtual portfolio.")
    @app_commands.autocomplete()
    async def add_to_portfolio(self, ctx, crypto: str, quantity: float):
        """
        !add_to_portfolio <crypto> <quantity>
        """
        user_id = str(ctx.author.id)
        if user_id not in self.portfolios:
            self.portfolios[user_id] = {}

        if crypto not in self.portfolios[user_id]:
            self.portfolios[user_id][crypto] = 0

        self.portfolios[user_id][crypto] += quantity
        await ctx.send(f"Added {quantity} of {crypto} to your portfolio.")

    @commands.command(description="Display a summary of your portfolio.")
    async def portfolio(self, ctx):
        """
        !portfolio
        """
        user_id = str(ctx.author.id)
        if user_id not in self.portfolios or not self.portfolios[user_id]:
            await ctx.send("Your portfolio is empty.")
            return

        summary = f"**Portfolio Summary for {ctx.author.mention}:**\n"
        total_value = 0

        for crypto, quantity in self.portfolios[user_id].items():
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto}&vs_currencies=usd"
            response = requests.get(url)
            data = response.json()

            if crypto in data:
                price = data[crypto]['usd']
                value = price * quantity
                total_value += value
                summary += f"{crypto.capitalize()}: {quantity} @ ${price:.2f} each (Total: ${value:.2f})\n"
            else:
                summary += f"{crypto.capitalize()}: {quantity} (Price data not available)\n"

        summary += f"\n**Total Portfolio Value:** ${total_value:.2f}"
        await ctx.send(summary)

    @commands.command(description="Analyze the performance of your portfolio over a given period.")
    async def portefeuille_rendement(self, ctx, period: str):
        """
        !portefeuille_rendement <period>
        """
        user_id = str(ctx.author.id)
        if user_id not in self.portfolios or not self.portfolios[user_id]:
            await ctx.send("Your portfolio is empty.")
            return

        # For simplicity, we'll only calculate the performance based on current prices.
        # More complex analysis would require historical data and user entry timestamps.
        summary = f"**Portfolio Performance Analysis for {ctx.author.mention} over {period}:**\n"
        total_initial_value = 0
        total_current_value = 0

        for crypto, quantity in self.portfolios[user_id].items():
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto}&vs_currencies=usd"
            response = requests.get(url)
            data = response.json()

            if crypto in data:
                price = data[crypto]['usd']
                value = price * quantity
                total_current_value += value
                summary += f"{crypto.capitalize()}: {quantity} @ ${price:.2f} each (Total: ${value:.2f})\n"
            else:
                summary += f"{crypto.capitalize()}: {quantity} (Price data not available)\n"

        # For a more realistic implementation, you'd store and use initial values.
        # Here we only show the current total value.
        summary += f"\n**Total Current Portfolio Value:** ${total_current_value:.2f}"
        await ctx.send(summary)

async def setup(bot):
    await bot.add_cog(Portfolio(bot))
