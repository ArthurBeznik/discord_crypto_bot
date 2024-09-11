import discord
from discord.ext import commands, tasks
from discord import app_commands
import logging
import requests
from utils.autocomplete import get_crypto_autocomplete_choices

logger = logging.getLogger(__name__)

class Alert(commands.GroupCog, name="alert"):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db  # Access the DatabaseManager instance from the bot
        if not self.db:
            logger.error("DatabaseManager is not initialized")
            raise RuntimeError("DatabaseManager is not initialized")
        self.check_alerts.start()  # Start the task loop for checking alerts

    @commands.Cog.listener()
    async def on_ready(self):
        # Ensure the database is initialized when the bot is ready
        if not self.db:
            logger.error("DatabaseManager is not initialized")
            raise RuntimeError("DatabaseManager is not initialized")
        self.db.initialize()

    @tasks.loop(minutes=10)  # Check every 10 minute
    async def check_alerts(self):
        logger.info("Checking alerts...")

        try:
            alerts = self.db.get_alerts()
            user_alerts = {}
            for user_id, crypto, threshold in alerts:
                if user_id not in user_alerts:
                    user_alerts[user_id] = {}
                user_alerts[user_id][crypto] = threshold

            for user_id, alerts in user_alerts.items():
                for crypto, threshold in alerts.items():
                    url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto}&vs_currencies=usd"
                    response = requests.get(url)
                    if response.status_code == 200:
                        data = response.json()
                        price = data.get(crypto, {}).get("usd", 0)
                        if price >= threshold:
                            user = self.bot.get_user(user_id)
                            if user:
                                await user.send(f"Alert: The price of {crypto} has reached ${price:.2f}.")
                                logger.info(f"Sent alert to user: {user} for {crypto} at ${price:.2f}")
                                
                                self.db.remove_alert(user_id, crypto)
                                logger.info('Removed alert from DB')
                    else:
                        logger.error(f"Error fetching price for {crypto}. Status code: {response.status_code}")

        except Exception as e:
            logger.error(f"Error in check_alerts task: {e}")

    @app_commands.command(name='create', description='Set a price alert for a cryptocurrency.')
    @app_commands.describe(crypto='The cryptocurrency to set an alert for.', threshold='The price threshold for the alert.')
    @app_commands.autocomplete(crypto=get_crypto_autocomplete_choices)
    async def create_alert(self, interaction: discord.Interaction, crypto: str, threshold: float):
        try:
            # Resolve the cryptocurrency
            crypto_id = self.bot.crypto_map.get(crypto.lower())
            logger.info(f"Resolved crypto: {crypto_id}")

            await interaction.response.defer(thinking=True)
            self.db.add_alert(interaction.user.id, crypto_id, threshold)
            await interaction.followup.send(f'Alert set for {crypto_id} at ${threshold:.2f}')
        except Exception as e:
            logger.error(f'Error creating alert: {e}')
            await interaction.followup.send(f'Failed to set alert: {e}')

    @app_commands.command(name='cancel', description='Cancel a previously set price alert.')
    @app_commands.describe(crypto='The cryptocurrency of the alert to cancel.')
    async def cancel_alert(self, interaction: discord.Interaction, crypto: str):
        try:
            # Resolve the cryptocurrency
            crypto_id = self.bot.crypto_map.get(crypto.lower())
            logger.info(f"Resolved crypto: {crypto_id}")

            await interaction.response.defer(thinking=True)
            self.db.remove_alert(interaction.user.id, crypto_id)
            await interaction.followup.send(f'Alert for {crypto_id} has been canceled.')
        except Exception as e:
            logger.error(f'Error canceling alert: {e}')
            await interaction.followup.send(f'Failed to cancel alert: {e}')

    @app_commands.command(name='show', description='Show all active alerts for the user.')
    async def show_alerts(self, interaction: discord.Interaction):
        logger.info(f"Displaying alerts for {interaction.user.name}")
        try:
            alerts = self.db.get_alerts()
            user_alerts = [(crypto, threshold) for user_id, crypto, threshold in alerts if user_id == interaction.user.id]

            if user_alerts:
                alert_list = '\n'.join([f'{crypto}: ${threshold:.2f}' for crypto, threshold in user_alerts])
                await interaction.response.send_message(f'Your alerts:\n{alert_list}')
            else:
                await interaction.response.send_message('You have no active alerts.')
        except Exception as e:
            logger.error(f'Error showing alerts: {e}')
            await interaction.response.send_message(f'Failed to fetch alerts: {e}')

async def setup(bot):
    await bot.add_cog(Alert(bot))
