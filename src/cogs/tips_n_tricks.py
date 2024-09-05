# tips_n_tricks.py

# TODO add tips n tricks

from discord.ext import commands
import random
from datetime import datetime, timedelta

class TipsAndTricks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tutorials = {
            "wallet": "To use a wallet, download a trusted wallet app, create a new wallet, and secure your recovery phrase.",
            "buy_cryptos": "To buy cryptocurrencies, create an account on a crypto exchange, complete the KYC process, and make your purchase using your preferred payment method.",
            "samulel": "To bam, you must zam in the lam with your kam",
            "secret": "Zam gives you 5 BTC, waoh."
            # TODO add tutorials/tricks
        }
        self.tips = [
            "Diversify your investments to minimize risk.",
            "Always do your own research before investing.",
            "Consider setting stop-loss orders to protect your investments."
            # TODO add tips
        ]
        self.last_advice_date = datetime.now() - timedelta(days=1)  # Initialize to ensure the first call will work

    @commands.command(description="Provide guides or tutorials on specific topics.")
    async def tuto(self, ctx, subject: str = None):
        """
        !tuto <subject>
        """
        if subject is None:
            subjects_list = ", ".join(self.tutorials.keys())
            await ctx.send(f"Available tutorial subjects: {subjects_list}")
        else:
            tutorial = self.tutorials.get(subject.lower())
            if tutorial:
                await ctx.send(f"**Tutorial on {subject}:**\n{tutorial}")
            else:
                await ctx.send(f"No tutorial found for '{subject}'. Please try another subject.")


    @commands.command(description="Offer a daily tip or trick on trading or investing in cryptocurrencies.")
    async def advice(self, ctx):
        """
        !advice
        """
        today = datetime.now().date()
        if self.last_advice_date.date() < today:
            self.last_advice_date = datetime.now()
            advice = random.choice(self.tips)
            await ctx.send(f"**Advice of the Day:**\n{advice}")
        else:
            await ctx.send("You have already received today's advice. Please come back tomorrow!")

async def setup(bot):
    await bot.add_cog(TipsAndTricks(bot))
