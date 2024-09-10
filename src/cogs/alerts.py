import discord
from discord.ext import commands, tasks
from discord import app_commands
import logging
from database import DatabaseManager  # Import the DatabaseManager
from utils.list import get_crypto_autocomplete_choices
import requests

logger = logging.getLogger(__name__)

class Alert(commands.GroupCog, name="alert"):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db  # Access the DatabaseManager instance from the bot
        # self.check_alerts.start()  # Start the task loop for checking alerts

    @commands.Cog.listener()
    async def on_ready(self):
        # Ensure the database is initialized when the bot is ready
        await self.db.initialize()

    @tasks.loop(minutes=1)  # Check every 1 minute
    async def check_alerts(self):
        logger.info("Checking alerts...")
        
        try:
            # Fetch all alerts from the database
            alerts = await self.db.fetchall('SELECT user_id, crypto, threshold FROM alerts')
            
            # Organize alerts by user_id
            user_alerts = {}
            for user_id, crypto, threshold in alerts:
                if user_id not in user_alerts:
                    user_alerts[user_id] = {}
                user_alerts[user_id][crypto] = threshold

            # Process each user's alerts
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
                                logger.info(f"Sent alert to user: {user_id} for {crypto} at ${price:.2f}")
                                
                                # Remove the alert after notifying
                                await self.db.execute(
                                    'DELETE FROM alerts WHERE user_id = ? AND crypto = ?',
                                    (user_id, crypto)
                                )
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
            await self.db.execute(
                'INSERT INTO alerts (user_id, crypto, threshold) VALUES (?, ?, ?)',
                (interaction.user.id, crypto, threshold)
            )
            await interaction.response.send_message(f'Alert set for {crypto} at {threshold}')
        except Exception as e:
            await interaction.response.send_message(f'Failed to set alert: {e}')
            logger.error(f'Error creating alert: {e}')

    @app_commands.command(name='cancel', description='Cancel a previously set price alert.')
    @app_commands.describe(crypto='The cryptocurrency of the alert to cancel.')
    async def cancel_alert(self, interaction: discord.Interaction, crypto: str):
        try:
            await self.db.execute(
                'DELETE FROM alerts WHERE user_id = ? AND crypto = ?',
                (interaction.user.id, crypto)
            )
            await interaction.response.send_message(f'Alert for {crypto} has been canceled.')
        except Exception as e:
            logger.error(f'Error canceling alert: {e}')
            await interaction.response.send_message(f'Failed to cancel alert: {e}')

    @app_commands.command(name='show', description='Show all active alerts for the user.')
    async def show_alerts(self, interaction: discord.Interaction):
        logger.info(f"Dislaying alerts for {interaction.user.name}")
        try:
            alerts = await self.db.fetchall(
                'SELECT crypto, threshold FROM alerts WHERE user_id = ?',
                (interaction.user.id,)
            )
            if alerts:
                alert_list = '\n'.join([f'{crypto}: {threshold}' for crypto, threshold in alerts])
                await interaction.response.send_message(f'Your alerts:\n{alert_list}')
            else:
                await interaction.response.send_message('You have no active alerts.')
        except Exception as e:
            await interaction.response.send_message(f'Failed to fetch alerts: {e}')
            logger.error(f'Error showing alerts: {e}')

async def setup(bot):
    # Ensure the DatabaseManager instance is available in the bot before loading the cog
    bot.db = DatabaseManager()  # Initialize DatabaseManager here if not already initialized
    await bot.db.initialize()  # Initialize database tables
    await bot.add_cog(Alert(bot))
