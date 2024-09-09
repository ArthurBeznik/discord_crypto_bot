# alerts.py

# TODO task loop => every x minutes?
# TODO for an alert, does it notify when the threshold is <, > or = ?
# TODO fix dict_items size error => DB

from discord.ext import commands, tasks
from utils.errors import show_help
import requests
import logging

logger = logging.getLogger(__name__)

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
        logger.debug(f"Called alert, crypto {crypto} |  treshold: {threshold} | author: {ctx.author.id}")

        if not crypto or not threshold:
            return await show_help(ctx)
        
        user_id = ctx.author.id
        if user_id not in self.alerts:
            self.alerts[user_id] = {}

        self.alerts[user_id][crypto] = threshold
        logger.info(f"Setting alert for user: {user_id} | crypto: {crypto} | threshold: {threshold}")
        await ctx.send(f"Price alert set for {crypto} at ${threshold:.2f}.")

    @commands.command(description="Cancel a previously set price alert.")
    async def cancel_alert(self, ctx, crypto: str = None):
        """
        !cancel_alert <crypto>
        """
        logger.debug(f"Called cancel_alert, crypto: {crypto} | author: {ctx.author.id}")

        if not crypto:
            return await show_help(ctx)

        user_id = ctx.author.id
        if user_id in self.alerts and crypto in self.alerts[user_id]:
            del self.alerts[user_id][crypto]
            logger.info(f"Cancelling alert for user: {user_id} | crypto: {crypto}")
            await ctx.send(f"Price alert for {crypto} has been canceled.")
        else:
            await ctx.send(f"No alert found for {crypto}.")

    # TODO fix dict_items size error
    # ! Set the number of minutes for the task loop
    @tasks.loop(minutes=1)  # Check every 1 minute
    async def check_alerts(self):
        logger.debug(f"Current alerts: {self.alerts.items()}")
        
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
                            logger.info(f"Sending alert to user: {user_id}")
                            await user.send(f"Alert: The price of {crypto} has reached ${price:.2f}.")
                        # Remove the alert after notifying
                        del self.alerts[user_id][crypto]
                else:
                    logger.error("Error fetching price for alert check.")

async def setup(bot):
    await bot.add_cog(Alerts(bot))
