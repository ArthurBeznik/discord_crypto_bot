# alerts.py

# TODO configure alert check loop

import discord
from discord.ext import commands, tasks
from discord import User, app_commands
from psycopg2 import DatabaseError
import requests

from bot import CryptoBot
from utils.response_helpers import (
    send_error_response,
    send_misc_response,
    send_success_response,
)
from utils.alerts_helpers import format_alerts_table
from utils.autocomplete import crypto_autocomplete
from utils.config import LOOP_MINUTES
from utils.logger import logging

logger = logging.getLogger(__name__)


class Alert(commands.GroupCog, name="alert"):
    def __init__(self, bot: CryptoBot) -> None:
        self.bot = bot
        self.check_alerts.start()  # ! Start the task loop for checking alerts

    @tasks.loop(minutes=LOOP_MINUTES)
    async def check_alerts(self) -> None:
        """_summary_"""
        logger.info("Running check_alerts loop...")

        try:
            # Fetch all alerts from the database
            alerts = self.bot.db.alerts.get_alerts()
            logger.debug(f"alerts: {alerts}")  # ? debug

            if alerts is None:
                logger.warning("Empty alerts")

            # Iterate over each alert and process it
            for id, user_id, crypto, threshold in alerts:
                logger.debug(
                    f"id: {id} | user_id: {user_id} | crypto: {crypto} | threshold: {threshold}"
                )  # ? debug

                try:
                    # Fetch current price for the specified cryptocurrency
                    url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto}&vs_currencies=usd"
                    response = requests.get(url)
                    if response.status_code == 200:
                        data = response.json()
                        price = data.get(crypto, {}).get("usd", 0)

                        # Check if the current price is above the threshold
                        if price >= threshold:
                            logger.info("Price is bigger than threshold, sending alert")
                            logger.debug(
                                f"price: {price} | threshold: {threshold}"
                            )  # ? debug

                            user: User = await self.bot.fetch_user(user_id)
                            logger.debug(f"user: {user}")  # ? debug

                            if user:
                                try:
                                    # Send an alert message to the user
                                    await user.send(
                                        f"🚨 **Alert**: The price of [**{crypto.upper()}**] has reached [${price:.2f}], exceeding your threshold of [${threshold:.2f}]!"
                                    )
                                    logger.info(
                                        f"Sent alert to user [{user.id}] for [{crypto}] at [${price:.2f}]"
                                    )

                                    # Remove the alert from the database
                                    self.bot.db.alerts.remove_alert(user_id, id)
                                    logger.info(
                                        f"Successfully removed alert for [{crypto}] from DB for user [{user_id}]"
                                    )
                                except discord.Forbidden:
                                    logger.warning(
                                        f"Cannot DM user [{user_id}] (DMs are disabled)."
                                    )
                                except discord.HTTPException as e:
                                    logger.error(
                                        f"Failed to send DM to user [{user_id}]: {e}"
                                    )
                            else:
                                logger.error(
                                    f"Error fetching user [{user_id}], got [{user}]"
                                )
                        else:
                            logger.debug(
                                f"Price of {crypto} is below the threshold for user [{user_id}]"
                            )

                    else:
                        logger.error(
                            f"Failed to fetch price for [{crypto}]. Status code: {response.status_code}"
                        )

                except Exception as e:
                    logger.error(
                        f"Error processing alert for user [{user_id}] on [{crypto}]: {e}"
                    )
                    continue  # Continue to the next alert if there is an error

        except Exception as e:
            logger.error(f"Error in check_alerts loop: {e}")

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
        """
        Creates a new price alert for the specified cryptocurrency.

        Args:
            interaction (discord.Interaction): The Discord interaction instance.
            crypto (str): The symbol or name of the cryptocurrency to monitor.
            threshold (float): The price threshold at which the alert should trigger.

        Raises:
            DatabaseError: If there is an error creating the alert in the database.
            Exception: If there is an unknown error.
        """
        logger.info(
            f"Creating alert for user [{interaction.user.id}] on [{crypto}] at [{threshold}]"
        )

        try:
            # Resolve the cryptocurrency
            crypto_id = self.bot.crypto_map.get(crypto.lower())
            logger.debug(f"Resolved crypto: {crypto_id}")  # ? debug

            await interaction.response.defer(thinking=True)
            self.bot.db.alerts.create_alert(interaction.user.id, crypto_id, threshold)

            await send_success_response(
                interaction,
                "Alert created",
                f"Alert for **[{crypto_id}]** at **[${threshold:.2f}]** has been created.",
            )
            logger.info(f"Successfully created alert for user [{interaction.user.id}]")

        except DatabaseError as e:
            await send_error_response(
                interaction, "Error creating alert", "A database error occured."
            )
            logger.error(f"Error creating alert: {e}")
            raise
        except Exception as e:
            await send_error_response(
                interaction, "Error creating alert", "An unexpected error occured."
            )
            logger.error(f"Error creating alert: {e}")
            raise

    @app_commands.command(
        name="cancel", description="Cancel a previously set price alert."
    )
    @app_commands.describe(alert_id="The ID of the alert to cancel.")
    async def cancel_alert(
        self, interaction: discord.Interaction, alert_id: int
    ) -> None:
        """
        Cancels an active alert based on its unique ID.

        Args:
            interaction (discord.Interaction): The Discord interaction instance.
            alert_id (int): The unique identifier of the alert to be canceled.

        Raises:
            DatabaseError: If there is an error cancelling the user's alerts.
            Exception: If there is an unknown error.
        """
        logger.info(f"Cancelling alert [{alert_id}] for user [{interaction.user.id}]")

        try:
            await interaction.response.defer(thinking=True)
            result = self.bot.db.alerts.remove_alert(interaction.user.id, alert_id)

            if result:
                await send_success_response(
                    interaction,
                    "Alert cancelled",
                    f"Alert **[{alert_id}]** has been cancelled.",
                )
                logger.info(
                    f"Successfully cancelled alert [{alert_id}] for user [{interaction.user.id}]"
                )
            else:
                await send_error_response(
                    interaction,
                    "Error cancelling alert",
                    f"Alert **[{alert_id}]** was not found.",
                )

        except DatabaseError as e:
            await send_error_response(
                interaction, "Error cancelling alert", "A database error occured."
            )
            logger.error(f"Error creating alert: {e}")
            raise
        except Exception as e:
            await send_error_response(
                interaction,
                "Error canceling alert",
                "An unexpected error occured.",
            )
            logger.error(
                f"Error canceling alert [{alert_id}] for user [{interaction.user.id}]: {e}"
            )
            raise

    @app_commands.command(
        name="list", description="List all active alerts for the user."
    )
    async def list_alerts(self, interaction: discord.Interaction) -> None:
        """
        Lists all active alerts set by the user.

        Args:
            interaction (discord.Interaction): The Discord interaction instance.

        Raises:
            DatabaseError: If there is an error retrieving the user's alerts.
            ValueError: If there is an error formatting the user's alerts into a table.
            Exception: If there is an unknown error.
        """
        logger.info(f"Listing alerts of user [{interaction.user.id}]")

        try:
            alerts = self.bot.db.alerts.get_alerts(interaction.user.id)
            logger.debug(f"alerts: {alerts}")  # ? debug

            if alerts:
                alert_table = format_alerts_table(alerts)
                logger.debug(f"alert_table: {alert_table}")  # ? debug

                await interaction.response.send_message(alert_table)
                logger.info(
                    f"Successfully displayed alerts for [{interaction.user.id}]"
                )
            else:
                await send_misc_response(
                    interaction,
                    "No Alerts",
                    "You don't have any alerts. Use **/alert create** to set a new alert.",
                )
                logger.warning(f"Did not find alerts for user [{interaction.user.id}]")

        except DatabaseError as e:
            await send_error_response(
                interaction, "Error listing alerts", "A database error occured."
            )
            logger.error(f"Error listing alerts: {e}")
            raise
        except ValueError as e:
            await send_error_response(
                interaction, "Error listing alerts", "A formatting error occured."
            )
            logger.error(f"Error listing alerts: {e}")
            raise
        except Exception as e:
            await send_error_response(
                interaction, "Error listing alerts", "An unknown error occured."
            )
            logger.error(f"Error listing alerts: {e}")
            raise


async def setup(bot: CryptoBot) -> None:
    await bot.add_cog(Alert(bot))
