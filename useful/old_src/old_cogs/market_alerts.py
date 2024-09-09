# market_alerts.py

import os
from discord.ext import commands, tasks
import requests
import json
import pandas as pd
from dotenv import load_dotenv
from utils.errors import show_help
import logging

logger = logging.getLogger(__name__)

load_dotenv()
ALERT_CHANNEL = os.getenv('ALERT_CHANNEL_ID')

class MarketAlerts(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_global_cap = None
        self.alert_threshold = 5  # Percentage change to trigger an alert
        self.global_alert_channel_id = ALERT_CHANNEL  # ! Set up in .env
        self.check_market_alerts.start()
        self.check_user_volatility_alerts.start()

    @tasks.loop(minutes=10)  # ! Set the number of minutes
    async def check_market_alerts(self):
        """
        Check global market metrics and send alerts if needed.
        """
        logger.debug("Checking market alerts")

        url = "https://api.coingecko.com/api/v3/global"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching market data: {e}")
            return

        current_global_cap = data['data']['total_market_cap']['usd']

        if self.last_global_cap:
            change_percentage = ((current_global_cap - self.last_global_cap) / self.last_global_cap) * 100
            if abs(change_percentage) >= self.alert_threshold:
                alert_message = f"**Global Market Alert:** The global market cap has changed by {change_percentage:.2f}% to ${current_global_cap:.2f}."
                if self.global_alert_channel_id:
                    try:
                        channel = await self.bot.fetch_channel(self.global_alert_channel_id)
                        if channel:
                            logger.info("Sending global market alert message")
                            await channel.send(alert_message)
                    except Exception as e:
                        logger.error(f"Exception occurred while sending market alert message: {e}")

        self.last_global_cap = current_global_cap

    @commands.command(description="Receive alerts for significant volatility in a cryptocurrency.")
    async def volatility_alert(self, ctx, crypto: str = None, threshold: float = None):
        """
        !volatility_alert <crypto> <threshold>
        """
        logger.debug(f"Called volatility_alert, crypto: {crypto} | threshold: {threshold} | author: {ctx.author.id}")

        if crypto is None or threshold is None:
            return await show_help(ctx)

        # Store user-specific alerts
        user_id = str(ctx.author.id)
        alert_data = {
            'crypto': crypto,
            'threshold': threshold
        }

        # Load user alerts
        if os.path.exists('user_alerts.json'):
            with open('user_alerts.json', 'r') as f:
                user_alerts = json.load(f)
        else:
            user_alerts = {}

        if user_id not in user_alerts:
            user_alerts[user_id] = []

        user_alerts[user_id].append(alert_data)

        with open('user_alerts.json', 'w') as f:
            json.dump(user_alerts, f)

        return await ctx.send(f"Volatility alert for {crypto} with a threshold of {threshold}% has been set.")

    async def check_volatility_alerts(self):
        """
        Check user-defined volatility alerts.
        """
        logger.debug("Check volatily alerts")

        if not os.path.exists('user_alerts.json'):
            return

        with open('user_alerts.json', 'r') as f:
            user_alerts = json.load(f)

        for user_id, alerts in user_alerts.items():
            for alert in alerts:
                crypto = alert['crypto']
                threshold = alert['threshold']

                logger.debug(f"Called volatility_alert, user: {user_id} | crypto: {crypto} | threshold: {threshold}")

                url = f"https://api.coingecko.com/api/v3/coins/{crypto}/market_chart?vs_currency=usd&days=1"
                try:
                    response = requests.get(url)
                    response.raise_for_status()
                    data = response.json()
                except requests.RequestException as e:
                    logger.error(f"Error fetching data for {crypto}: {e}")
                    continue

                if 'prices' in data:
                    df = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    df.set_index('timestamp', inplace=True)

                    # Calculate volatility
                    df['price_change'] = df['price'].pct_change() * 100
                    max_volatility = df['price_change'].abs().max()

                    if max_volatility >= threshold:
                        user = self.bot.get_user(int(user_id))
                        if user:
                            try:
                                logger.info(f"Sending volatility alert to user {user_id} for {crypto}")
                                await user.send(f"**Volatility Alert:** {crypto} has experienced {max_volatility:.2f}% volatility in the last 24 hours.")
                            except Exception as e:
                                logger.error(f"Failed to send volatility alert to user {user_id}: {e}")

    @tasks.loop(hours=1) # ! Set number of hours
    async def check_user_volatility_alerts(self):
        await self.check_volatility_alerts()

async def setup(bot):
    await bot.add_cog(MarketAlerts(bot))
