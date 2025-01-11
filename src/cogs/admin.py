# admin.py

import discord
from discord.ext import commands
from discord import app_commands
from bot import CryptoBot
from utils.response_helpers import send_error_response, send_success_response
from utils.predictions_helpers import format_predictions_table
from utils.config import (
    DISCORD_GUILD_OBJ,
)
from utils.logger import logging

logger = logging.getLogger(__name__)


class Admin(commands.Cog, name="admin"):
    def __init__(self, bot: CryptoBot) -> None:
        self.bot = bot

    @app_commands.command(
        name="adminonly", description="A command only accessible by admins."
    )
    @app_commands.default_permissions(administrator=True)
    async def admin_only_command(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(
            "You are an admin and have access to this command!"
        )

    @app_commands.command(name="load", description="Load a new cog")
    @app_commands.rename(cog_name="cog")
    @app_commands.describe(cog_name="Name of the cog to load")
    @app_commands.default_permissions(administrator=True)
    async def load(self, interaction: discord.Interaction, cog_name: str) -> None:
        try:
            await self.bot.load_extension(f"cogs.{cog_name}")
            await interaction.response.send_message(
                f"Loaded extension **{cog_name}.py**"
            )
            logger.info(f"Loaded cog: {cog_name}")
        except Exception as e:
            await interaction.response.send_message(f"Error loading cog: {e}")
            logger.error(f"Failed to load cog: {cog_name}")

    @app_commands.command(
        name="sync", description="Sync commands to the Discord server"
    )
    @app_commands.default_permissions(administrator=True)
    async def sync(self, interaction: discord.Interaction) -> None:
        try:
            await self.bot.tree.sync(guild=DISCORD_GUILD_OBJ)
            logger.info(self.bot.tree.get_commands(guild=DISCORD_GUILD_OBJ))
            await interaction.response.send_message(
                f"Commands synced to guild {DISCORD_GUILD_OBJ.id}"
            )
            logger.info(f"Synced commands to guild: {DISCORD_GUILD_OBJ.id}")
        except Exception as e:
            await interaction.response.send_message(f"Error syncing commands: {e}")
            logger.error(f"Failed to sync commands: {e}")

    @app_commands.command(
        name="remove", description="Remove a specific command from the Discord server"
    )
    @app_commands.rename(command_name="command")
    @app_commands.describe(command_name="Name of the command to remove")
    @app_commands.default_permissions(administrator=True)
    async def remove(self, interaction: discord.Interaction, command_name: str) -> None:
        try:
            logger.info(self.bot.tree.get_commands(guild=DISCORD_GUILD_OBJ))
            self.bot.tree.remove_command(command_name)
            await self.bot.tree.sync(guild=DISCORD_GUILD_OBJ)
            logger.info(self.bot.tree.get_commands(guild=DISCORD_GUILD_OBJ))
            await interaction.response.send_message(
                f"Removed command {command_name} from guild {DISCORD_GUILD_OBJ.id}"
            )
            logger.info(
                f"Removed command {command_name} from guild: {DISCORD_GUILD_OBJ}"
            )
        except Exception as e:
            await interaction.response.send_message(f"Error syncing commands: {e}")
            logger.error(f"Failed to remove command {command_name}: {e}")

    @app_commands.command(
        name="clear", description="Clear all commands from the server"
    )
    @app_commands.default_permissions(administrator=True)
    async def clear(self, interaction: discord.Interaction) -> None:
        try:
            logger.info(self.bot.tree.get_commands(guild=DISCORD_GUILD_OBJ))
            self.bot.tree.clear_commands(guild=DISCORD_GUILD_OBJ)
            await self.bot.tree.sync(guild=DISCORD_GUILD_OBJ)
            logger.info(self.bot.tree.get_commands(guild=DISCORD_GUILD_OBJ))
            await interaction.response.send_message(
                f"Cleared all commands from guild {DISCORD_GUILD_OBJ.id}"
            )
            logger.info(f"Cleared all commands from guild: {DISCORD_GUILD_OBJ}")
        except Exception as e:
            await interaction.response.send_message(f"Error syncing commands: {e}")
            logger.error(f"Failed to clear commands: {e}")

    @app_commands.command(
        name="clear_all_predictions", description="Clear all predictions for all users"
    )
    @app_commands.default_permissions(administrator=True)
    async def clear_all_predictions(self, interaction: discord.Interaction) -> None:
        """
        Clears all predictions made by all users.

        Args:
            interaction (discord.Interaction): The interaction that triggered this command.

        Returns:
            None
        """
        try:
            logger.info("Admin is clearing all predictions for all users")
            self.bot.db.predictions.clear_predictions()
            await interaction.response.send_message(
                "All predictions for all users have been removed successfully."
            )
            logger.info("Successfully cleared all predictions for all users.")
        except Exception as e:
            await interaction.response.send_message(f"Error clearing predictions: {e}")
            logger.error(f"Failed to clear all predictions: {e}")

    @app_commands.command(
        name="get_all_predictions", description="Get all predictions for all users"
    )
    @app_commands.default_permissions(administrator=True)
    async def get_all_predictions(self, interaction: discord.Interaction) -> None:
        """
        Clears all predictions made by all users.

        Args:
            interaction (discord.Interaction): The interaction that triggered this command.

        Returns:
            None
        """
        try:
            logger.info("Admin is getting all predictions for all users")
            predictions = self.bot.db.predictions.get_predictions()
            logger.debug(f"predictions: {predictions}")  # ? debug

            if not predictions:  # Check if the predictions list is empty
                logger.warning("No predictions found in the database.")
                await interaction.response.send_message(
                    "No predictions found for any users."
                )
                return

            predictions_message = await format_predictions_table(
                predictions, interaction
            )
            await interaction.response.send_message(predictions_message)
            logger.info("Successfully fetched all predictions for all users.")
        except Exception as e:
            await interaction.response.send_message(f"Error fetching predictions: {e}")
            logger.error(f"Failed to fetch all predictions: {e}")

    @app_commands.command(
        name="list_users",
        description="List all users with their entry date, roles, and number of roles",
    )
    async def list_users(self, interaction: discord.Interaction) -> None:
        logger.info("Listing all users and their information")

        try:
            guild = interaction.guild
            logger.debug(f"guild: {guild}")  # ? debug

            if guild is None:
                await send_error_response(
                    interaction, "Error", "This command must be used in a guild."
                )
                return

            # Ensure the bot fetches all members if they are not cached
            guild.fetch_members()
            logger.debug(f"guild members: {guild.members}")  # ? debug

            users_data = []
            # async for member in guild.fetch_members(): # ? is this better?
            for member in guild.members:
                logger.debug(f"member: {member}")  # ? debug

                join_date = member.joined_at.strftime("%Y-%m-%d %H:%M:%S")
                roles = [role.name for role in member.roles if role.name != "@everyone"]
                roles_display = ", ".join(roles) if roles else "No Roles"
                users_data.append(
                    f"**{member.name} | {member.global_name or ''}**\n"
                    f"Joined: {join_date}\n"
                    f"Roles ({len(roles)}): {roles_display}\n"
                )

            await send_success_response(
                interaction, "Server Members", "\n\n".join(users_data)
            )

        except Exception as e:
            await send_error_response(interaction, "Error listing users", f"{e}")
            logger.error(f"Error listing users: {e}")


async def setup(bot: CryptoBot) -> None:
    await bot.add_cog(Admin(bot))
