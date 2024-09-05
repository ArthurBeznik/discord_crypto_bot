# alerts.py

# TODO task loop => every x minutes?
# TODO for an alert, does it notify when the treshold is <, > or = ?

from discord.ext import commands, tasks
from utils.errors import show_help
from dotenv import load_dotenv
import requests

load_dotenv()

# Price alerts
# ==============================================
class Alerts(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.alerts = {}  # Dictionary to store alerts, format: {user_id: {crypto: threshold}}
        self.check_alerts.start()  # Start the background task

    @commands.command(description="Set a price alert for a cryptocurrency.")
    async def alert(self, ctx, crypto: str = None, threshold: float = None):
        """
        !alert <crypto> <threshold>
        """
        if not crypto or not threshold:
            return await show_help(ctx)
        print(f"Setting alert for user: {ctx.author.id} | crypto: {crypto} | treshold: {threshold}") # ? debug
        user_id = ctx.author.id
        if user_id not in self.alerts:
            self.alerts[user_id] = {}
        self.alerts[user_id][crypto] = threshold
        await ctx.send(f"Price alert set for {crypto} at ${threshold:.2f}.")

    @commands.command(description="Cancel a previously set price alert.")
    async def cancel_alert(self, ctx, crypto: str = None):
        """
        !cancel_alert <crypto>
        """
        if not crypto:
            return await show_help(ctx)
        print(f"Cancelling alert for user: {ctx.author.id} | crypto: {crypto}") # ? debug
        user_id = ctx.author.id
        if user_id in self.alerts and crypto in self.alerts[user_id]:
            del self.alerts[user_id][crypto]
            await ctx.send(f"Price alert for {crypto} has been canceled.")
        else:
            await ctx.send(f"No alert found for {crypto}.")

    # ! Set the number of minutes
    @tasks.loop(minutes=1)  # Check every 5 minutes 
    async def check_alerts(self):
        # print(f"Current alerts: {self.alerts.items()}") # ? debug
        for user_id, alerts in self.alerts.items():
            for crypto, threshold in alerts.items():
                url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto}&vs_currencies=usd"
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    price = data.get(crypto, {}).get("usd", 0)
                    if price >= threshold:
                        user = self.bot.get_user(user_id)
                        if user:
                            print(f"Sending alert to user: {user_id}") # ? debug
                            await user.send(f"Alert: The price of {crypto} has reached ${price:.2f}.")
                        # Remove the alert after notifying
                        del self.alerts[user_id][crypto]
                else:
                    print("Error fetching price for alert check.")

async def setup(bot):
    await bot.add_cog(Alerts(bot))