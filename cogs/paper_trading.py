# paper_trading.py

# TODO paper trading?

from discord.ext import commands
import requests
import datetime
from utils.errors import show_help

class PaperTrading(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.trades = []  # In-memory list to store trade history

    @commands.command(description="Simulate a trade without risking real money.")
    async def paper_trade(self, ctx, crypto: str = None, amount: float = None):
        """
        !paper_trade <crypto> <amount>
        """
        if crypto is None or amount is None:
            return await show_help(ctx)
        
        # Fetch current price of the cryptocurrency
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto}&vs_currencies=usd"
        response = requests.get(url)
        data = response.json()

        if crypto in data:
            price = data[crypto]['usd']
            trade_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            trade = {
                "user": ctx.author.name,
                "crypto": crypto,
                "amount": amount,
                "price": price,
                "time": trade_time
            }
            self.trades.append(trade)
            await ctx.send(f"Simulated trade added: {amount} {crypto} at ${price:.2f} each.")
        else:
            await ctx.send("Error fetching data for the specified cryptocurrency. Please check the name and try again.")

    @commands.command(description="Display the history of simulated trades.")
    async def history_paper_trade(self, ctx):
        """
        !history_paper_trade
        """
        if self.trades:
            history_message = "**Trade History:**\n"
            for trade in self.trades:
                history_message += (f"**User:** {trade['user']}\n"
                                    f"**Crypto:** {trade['crypto']}\n"
                                    f"**Amount:** {trade['amount']}\n"
                                    f"**Price:** ${trade['price']:.2f}\n"
                                    f"**Time:** {trade['time']}\n\n")
            await ctx.send(history_message)
        else:
            await ctx.send("No simulated trades found.")

async def setup(bot):
    await bot.add_cog(PaperTrading(bot))
