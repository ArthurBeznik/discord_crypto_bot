# auto_updates.py

# TODO subscriptions should be stored in a DB

import discord
from discord.ext import commands, tasks
import requests
from utils.errors import show_help
import logging

logger = logging.getLogger(__name__)

class AutoUpdates(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.subscriptions = {}  # {user_id: [crypto1, crypto2, ...]}
        # self.check_updates.start()

    @commands.command(description="Subscribe to automatic updates for a specific cryptocurrency.")
    async def suivi_actu(self, ctx, crypto: str = None):
        """
        !suivi_actu <crypto>
        """
        logger.debug(f"Called suivi_actu, crypto: {crypto} | author: {ctx.author.id}")

        if crypto is None:
            return await show_help(ctx)
        
        user_id = ctx.author.id
        if user_id not in self.subscriptions:
            self.subscriptions[user_id] = []
        
        if crypto not in self.subscriptions[user_id]:
            self.subscriptions[user_id].append(crypto)
            logger.info(f"User {user_id} subscribed to updates for {crypto}.")
            await ctx.send(f"You will receive regular updates on {crypto}.")
        else:
            logger.info(f"User {user_id} already subscribed to updates for {crypto}.")
            await ctx.send(f"You are already subscribed to updates for {crypto}.")

    @commands.command(description="Unsubscribe from automatic updates for a specific cryptocurrency.")
    async def stop_suivi_actu(self, ctx, crypto: str = None):
        """
        !stop_suivi_actu <crypto>
        """
        logger.debug(f"Called stop_suivi_actu: {crypto} | {ctx.author.id}")

        if crypto is None:
            return await show_help(ctx)
        
        user_id = ctx.author.id
        if user_id in self.subscriptions and crypto in self.subscriptions[user_id]:
            self.subscriptions[user_id].remove(crypto)
            if not self.subscriptions[user_id]:
                del self.subscriptions[user_id]
            logger.info(f"User {user_id} unsubscribed from updates for {crypto}.")
            await ctx.send(f"You have been unsubscribed from updates on {crypto}.")
        else:
            logger.info(f"User {user_id} was not subscribed to updates for {crypto}.")
            await ctx.send(f"You are not subscribed to updates for {crypto}.")

    @tasks.loop(minutes=60) # ! set up number of minutes
    async def check_updates(self):
        """
        Fetch latest cryptocurrency data and send updates to users.
        """
        logger.debug("Loop check_updates")

        for user_id, cryptos in self.subscriptions.items():
            user = self.bot.get_user(user_id)
            if user:
                for crypto in cryptos:
                    url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto}&vs_currencies=usd"
                    response = requests.get(url)
                    data = response.json()
                    
                    if crypto in data:
                        price = data[crypto]['usd']
                        update_message = f"**Update for {crypto}:**\nCurrent Price: ${price:.2f}"
                        try:
                            logger.info(f"Sent update for {crypto} to user {user_id}.")
                            await user.send(update_message)
                        except discord.Forbidden:
                            logger.error(f"Failed to send message to {user_id}. User might have DMs disabled.")
    
    @check_updates.before_loop
    async def before_check_updates(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(AutoUpdates(bot))
