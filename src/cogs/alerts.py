# alerts.py

# TODO configure alert check loop

from typing import Dict
import discord
from discord.ext import commands, tasks
from discord import Embed, app_commands
import requests

from bot import CryptoBot
from utils.autocomplete import crypto_autocomplete
from utils.config import LOOP_MINUTES
from utils.logger import logging
from utils.embeds import success_embed

logger = logging.getLogger(__name__)

UserAlertsType = Dict[int, Dict[str, float]]


class Alert(commands.GroupCog, name="alert"):
    def __init__(self, bot: CryptoBot) -> None:
        self.bot = bot
        # self.check_alerts.start()  # ! Start the task loop for checking alerts

    @tasks.loop(minutes=LOOP_MINUTES)
    async def check_alerts(self) -> None:
        logger.info("Checking alerts...")

        try:
            alerts = self.bot.db.alerts.get_alerts()
            logger.debug(f"alerts: {alerts}")  # ? debug

            # TODO bug: this is overwritting if there are multiple alerts for the same crypto
            user_alerts: UserAlertsType = {}
            for user_id, crypto, threshold in alerts:
                if user_id not in user_alerts:
                    user_alerts[user_id] = {}
                user_alerts[user_id][crypto] = threshold
            logger.debug(f"user_alerts: {user_alerts}")  # ? debug

            for user_id, alerts in user_alerts.items():
                logger.debug(f"user_id: {user_id} | alerts: {alerts}")  # ? debug

                for crypto, threshold in alerts.items():
                    logger.debug(f"crypto: {crypto} | treshold: {threshold}")  # ? debug

                    url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto}&vs_currencies=usd"
                    response = requests.get(url)
                    if response.status_code == 200:
                        data = response.json()
                        price = data.get(crypto, {}).get("usd", 0)
                        if price >= threshold:
                            user = self.bot.get_user(user_id)
                            if user:
                                await user.send(
                                    f"Alert: The price of {crypto} has reached ${price:.2f}."
                                )
                                logger.info(
                                    f"Sent alert to user [{user.id}] for {crypto} at ${price:.2f}"
                                )

                                self.bot.db.alerts.remove_alert(user_id, crypto)
                                logger.info("Successfully removed alert from DB")
                    else:
                        logger.error(
                            f"Error fetching price for [{crypto}]. Status code: {response.status_code}"
                        )

        except Exception as e:
            logger.error(f"Error in check_alerts task: {e}")

    @check_alerts.before_loop
    async def before_check_alerts(self):
        await (
            self.bot.wait_until_ready()
        )  # Ensures the bot is ready before starting the loop

    @app_commands.command(
        name="create", description="Set a price alert for a cryptocurrency."
    )
    @app_commands.describe(
        crypto="Name or symbol of the cryptocurrency",
        threshold="The price threshold for the alert.",
    )
    @app_commands.autocomplete(crypto=crypto_autocomplete)
    async def create_alert(
        self, interaction: discord.Interaction, crypto: str, threshold: float
    ) -> None:
        logger.info(
            f"Creating alert for user [{interaction.user.id}] on [{crypto}] at [{threshold}]"
        )

        try:
            # Resolve the cryptocurrency
            crypto_id = self.bot.crypto_map.get(crypto.lower())
            logger.debug(f"Resolved crypto: {crypto_id}")  # ? debug

            await interaction.response.defer(thinking=True)
            self.bot.db.alerts.add_alert(interaction.user.id, crypto_id, threshold)
            embed = success_embed(f"Alert set for {crypto_id} at ${threshold:.2f}")
            await interaction.followup.send(embed=embed)
            logger.info(f"Successfully set alert for user [{interaction.user.id}]")
        except Exception as e:
            await interaction.followup.send(f"Failed to set alert: {e}")
            logger.error(f"Error creating alert: {e}")

    @app_commands.command(
        name="cancel", description="Cancel a previously set price alert."
    )
    @app_commands.describe(crypto="The cryptocurrency of the alert to cancel.")
    async def cancel_alert(self, interaction: discord.Interaction, crypto: str) -> None:
        logger.info(f"Cancelling alert for user [{interaction.user.id}] for [{crypto}]")

        try:
            # Resolve the cryptocurrency
            crypto_id = self.bot.crypto_map.get(crypto.lower())
            logger.debug(f"Resolved crypto: {crypto_id}")  # ? debug

            await interaction.response.defer(thinking=True)
            self.bot.db.alerts.remove_alert(interaction.user.id, crypto_id)
            await interaction.followup.send(f"Alert for {crypto_id} has been canceled")
            logger.info(
                f"Successfully canceled alert for user [{interaction.user.id}]"
            )
        except Exception as e:
            await interaction.followup.send(f"Failed to cancel alert: {e}")
            logger.error(f"Error canceling alert: {e}")

    @app_commands.command(
        name="show", description="Show all active alerts for the user."
    )
    async def show_alerts(self, interaction: discord.Interaction) -> None:
        logger.info(f"Showing alerts of user [{interaction.user.id}]")

        try:
            alerts = self.bot.db.alerts.get_alerts()
            user_alerts = [
                (crypto, threshold)
                for user_id, crypto, threshold in alerts
                if user_id == interaction.user.id
            ]

            if user_alerts:
                alert_list = "\n".join(
                    [f"{crypto}: ${threshold:.2f}" for crypto, threshold in user_alerts]
                )

                embed: Embed = Embed(
                    title="Your Alerts",
                    description=alert_list,
                    color=discord.Color.green(),
                )
                await interaction.response.send_message(embed=embed)

                logger.info(
                    f"Successfully displayed alerts for [{interaction.user.id}]"
                )
            else:
                await interaction.response.send_message("You have no active alerts")
                logger.info(f"No alerts for {interaction.user.id}")
        except Exception as e:
            await interaction.response.send_message(f"Failed to fetch alerts: {e}")
            logger.error(f"Error showing alerts: {e}")


async def setup(bot: CryptoBot) -> None:
    await bot.add_cog(Alert(bot))
